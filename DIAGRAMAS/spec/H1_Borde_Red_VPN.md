# HIPERVISOR 1 — Borde, Red, VPN y Switching | Sede Central (LOCAL 2)
**Proyecto:** Franco's SAC — Infraestructura Tecnológica
**Área:** ITI — UPeU 2026
**Estándares:** TIA/EIA-568 · IEEE 802.1Q · ISO 27001 · NIST CSF
**Fecha:** 31/05/2026

---

## 1. Descripción general

HIPERVISOR 1 es el **punto de entrada y salida de toda la infraestructura** de Franco's SAC.
Controla el tráfico WAN, los túneles VPN hacia L1, L3 y AWS, la segmentación VLAN,
el WAF y el API Gateway público. Todo el tráfico externo pasa por aquí.

### NICs físicas del hipervisor (ESXi Host 1 — Dell Precision 7920)

| NIC | Mapeo físico | Función |
|---|---|---|
| vmnic0 | → Cisco Router ISP1 | WAN1 primaria — GW: 172.17.25.121 |
| vmnic1 | → FortiGate 40F ISP2 | WAN2 failover — GW: 100.17.25.121 |
| vmnic2 | → Cisco Catalyst 1000 | Trunk 802.1Q VLAN 4095 (todas las VLANs) |

### VMs en H1

| VM | IP | VLAN | Función |
|---|---|---|---|
| VM-PFSENSE-BORDE | WAN / múltiples | — | Firewall, NAT, Dual-WAN, IPSec, inter-VLAN routing |
| VM-WAF | 10.10.30.5 | VLAN 30 DMZ | NGINX + ModSecurity — WAF capa 7 |
| VM-API-GATEWAY | 10.10.30.10 | VLAN 30 DMZ | NestJS 11 + Docker — REST endpoint público |

---

## 2. VM-PFSENSE-BORDE — Firewall Principal

### 2.1 Interfaces configuradas en pfSense

| Interfaz pfSense | Tipo | IP | Función |
|---|---|---|---|
| WAN1 (vmnic0) | WAN física | DHCP/estática ISP1 | Internet primario |
| WAN2 (vmnic1) | WAN física | DHCP/estática ISP2 | Internet failover |
| VLAN10 (vmnic2.10) | LAN virtual | 10.10.10.1/24 | Admin — GW para admins |
| VLAN20 (vmnic2.20) | LAN virtual | 10.10.20.1/24 | Usuarios — GW para workstations |
| VLAN30 (vmnic2.30) | DMZ virtual | 10.10.30.1/28 | DMZ — GW para WAF y API GW |
| VLAN40 (vmnic2.40) | LAN virtual | 10.10.40.1/24 | Servicios — GW para microservicios |
| VLAN50 (vmnic2.50) | LAN virtual | 10.10.50.1/28 | Datos — GW para PostgreSQL |
| VLAN60 (vmnic2.60) | LAN virtual | 10.10.60.1/28 | Gestión — GW para Zabbix/Monitor |
| VLAN99 (vmnic2.99) | MGMT virtual | 10.10.99.1/28 | MGMT ESXi — acceso a consolas |

### 2.2 DHCP en pfSense (por VLAN)

pfSense gestiona DHCP nativo por interfaz VLAN. No se requiere VM dedicada.

| VLAN | Rango DHCP | DNS entregado | Reservas |
|---|---|---|---|
| VLAN 10 Admin | 10.10.10.50 – 10.10.10.200 | 10.10.10.20 (DC1), 10.10.10.21 (DC2) | Admins fijos |
| VLAN 20 Usuarios | 10.10.20.50 – 10.10.20.200 | 10.10.10.20, 10.10.10.21 | Workstations |
| VLAN 40 Servicios | estáticas (VMs) | 10.10.10.20 | Sin DHCP — IPs fijas |
| VLAN 50 Datos | estáticas (BDs) | — | Sin DHCP — IPs fijas |
| VLAN 60 Gestión | 10.10.60.10 – 10.10.60.20 | 10.10.10.20 | Sin DHCP — IPs fijas |
| VLAN 99 MGMT | 10.10.99.10 – 10.10.99.20 | — | Sin DHCP — IPs fijas |

> **DNS entregado:** Siempre apunta a VM-AD-DC (DC1: 10.10.10.20) como primario
> y VM-AD-DC-2 (DC2: 10.10.10.21) como secundario para todos los clientes.

### 2.3 Reglas de Firewall — Segmentación por VLAN

#### WAN → DMZ (tráfico entrante público)
```
ALLOW WAN → VLAN30 TCP 443    (HTTPS a VM-WAF → VM-API-GATEWAY)
DENY  WAN → cualquier otro    (bloqueo total por defecto)
```

#### DMZ (VLAN 30) → interna
```
ALLOW VLAN30 → VLAN40 TCP 4222   (API GW → NATS server)
DENY  VLAN30 → VLAN10            (DMZ no accede a Admin)
DENY  VLAN30 → VLAN50            (DMZ no accede a BDs directamente)
DENY  VLAN30 → VLAN60            (DMZ no accede a Gestión)
DENY  VLAN30 → VLAN99            (DMZ no accede a MGMT)
```

#### VLAN 20 Usuarios → servicios
```
ALLOW VLAN20 → VLAN30 TCP 443    (usuarios acceden al ERP via HTTPS)
ALLOW VLAN20 → VLAN10 TCP 389    (LDAP para login AD)
DENY  VLAN20 → VLAN50            (usuarios no acceden a BDs)
DENY  VLAN20 → VLAN60            (usuarios no acceden a monitoreo)
DENY  VLAN20 → VLAN99            (usuarios no acceden a MGMT)
ALLOW VLAN20 → WAN               (internet — controlado por proxy futuro)
```

#### VLAN 10 Admin → todo
```
ALLOW VLAN10 → ANY               (admins acceden a toda la infraestructura)
```

#### VLAN 40 Servicios → Datos
```
ALLOW VLAN40 → VLAN50 TCP 5432   (microservicios → PostgreSQL)
DENY  VLAN40 → VLAN20            (servicios no inician tráfico a usuarios)
DENY  VLAN40 → VLAN10            (servicios no acceden a Admin)
```

#### VLAN 50 Datos (BDs) — aislamiento máximo
```
DENY  VLAN50 → cualquier origen inbound   (BDs solo reciben — no inician)
ALLOW VLAN40 → VLAN50 TCP 5432            (única regla que aplica — desde servicios)
```

#### VLAN 60 Gestión → monitoreo
```
ALLOW VLAN60 → ANY ICMP          (ping para monitoreo)
ALLOW VLAN60 → ANY UDP 161       (SNMP polling)
ALLOW VLAN60 → ANY TCP 10050     (Zabbix agent)
DENY  VLAN60 → WAN               (monitoreo no sale a internet directo)
```

#### VPN → interna (L1, L3, AWS)
```
ALLOW VPN_L1-L2 (10.20.0.0/16) → VLAN30 TCP 443   (operarios L1 acceden al ERP)
ALLOW VPN_L1-L2 (10.20.0.0/16) → VLAN10 TCP 389   (login AD desde L1)
ALLOW VPN_L2-L3 (10.30.0.0/16) → VLAN30 TCP 443   (operarios L3 acceden al ERP)
ALLOW VPN_L2-L3 (10.30.0.0/16) → VLAN10 TCP 389   (login AD desde L3)
ALLOW VPN_L2-AWS → VLAN50 TCP 5432                 (backup pg_dump via VPN)
DENY  VPN_L1-L2 → VLAN50                           (L1 no accede a BDs directamente)
DENY  VPN_L2-L3 → VLAN50                           (L3 no accede a BDs directamente)
```

---

## 3. Multi-WAN Failover (Dual-WAN)

### 3.1 Configuración

```
WAN1 (vmnic0) → Cisco Router ISP1
  IP: asignada por ISP1
  GW: 172.17.25.121
  Estado: ACTIVO (primario)
  Monitor: ping a 8.8.8.8 cada 1 segundo

WAN2 (vmnic1) → FortiGate 40F ISP2
  IP: asignada por ISP2
  GW: 100.17.25.121
  Estado: STANDBY (failover)
  Monitor: ping a 8.8.8.8 cada 1 segundo
```

### 3.2 Comportamiento de failover

| Evento | Acción pfSense | Tiempo |
|---|---|---|
| WAN1 falla (3 pings perdidos) | Activa WAN2 automáticamente | < 10 segundos |
| WAN1 se restaura | Regresa a WAN1 (WAN1 siempre preferida) | < 30 segundos |
| Ambas WAN caen | Sin internet — VPN interna sigue funcionando via LAN | Inmediato |

### 3.3 Impacto en túneles VPN durante failover

Los túneles IPSec se reconectan automáticamente usando el IP del nuevo WAN activo.
pfSense renegocia IKEv2 con el extremo remoto.
Tiempo de reconexión del túnel: 15-30 segundos (IKEv2 fast rekeying).

### 3.4 pfSense Backup — CARP (futuro)

Para eliminar pfSense como SPOF, se puede agregar una segunda instancia con CARP:

```
VM-PFSENSE-BORDE   (primary)  — activo
VM-PFSENSE-BORDE-2 (backup)   — standby (mismas NICs, diferente VM)

Virtual IPs (CARP VIPs) compartidas:
  WAN1 VIP: IP flotante ISP1
  WAN2 VIP: IP flotante ISP2
  LAN VIP:  10.10.x.1 (GW de cada VLAN)

Failover: si primary cae → backup toma los VIPs en < 2 segundos
Sincronización: estado de conexiones (pfsync) entre ambas instancias
```

> **Para el proyecto académico:** documentado como mejora futura.
> La infraestructura actual mitiga el riesgo con Dual-WAN + H4 standby.

---

## 4. Túneles IPSec VPN

### 4.0 Nomenclatura de sedes

| Código | Sede | Rol |
|---|---|---|
| **L1** | Local 1 — Planta de Producción | Sede remota 1 |
| **L2** | Local 2 — Sede Central | Hub de todos los túneles |
| **L3** | Local 3 — Segunda Planta de Producción | Sede remota 2 |

> pfSense-BORDE en L2 (Sede Central) es el **hub VPN** — todos los túneles terminan aquí.
> L1 y L3 se comunican entre sí solo a través de L2 (no hay túnel directo L1↔L3).

### 4.1 Resumen de túneles

| Túnel | Extremo L2 (Sede Central) | Extremo remoto | Subred túnel | IP L2 | IP remota |
|---|---|---|---|---|---|
| **L1 ↔ L2** | pfSense-BORDE WAN1 | pfSense-L1 WAN | 172.16.10.0/30 | 172.16.10.1 | 172.16.10.2 (L1) |
| **L2 ↔ L3** | pfSense-BORDE WAN1 | pfSense-L3 WAN | 172.16.20.0/30 | 172.16.20.2 | 172.16.20.1 (L3) |
| **L2 ↔ AWS** | pfSense-BORDE WAN1 | AWS VPN Gateway | 172.16.30.0/30 | 172.16.30.2 | 172.16.30.1 (AWS) |

### 4.2 Parámetros IKEv2 — todos los túneles

| Parámetro | Valor |
|---|---|
| Protocolo | IPSec IKEv2 |
| Cifrado Phase 1 | AES-256-GCM |
| Hash Phase 1 | SHA-256 |
| DH Group | Group 14 (2048-bit MODP) |
| Lifetime Phase 1 | 28800 segundos (8 horas) |
| Cifrado Phase 2 | AES-256-GCM |
| Hash Phase 2 | SHA-256 |
| PFS Group | Group 14 |
| Lifetime Phase 2 | 3600 segundos (1 hora) |
| Autenticación | Pre-Shared Key (PSK) único por túnel |
| DPD (Dead Peer Detection) | Habilitado — 10 seg intervalo, 5 reintentos |

### 4.3 Túnel L1 ↔ L2 (Local 1 ↔ Sede Central)

```
pfSense-BORDE (L2 — Sede Central)      pfSense-L1 (Local 1)
  WAN1: 172.17.25.x (IP pública)         WAN1: IP pública ISP L1
  Tunnel IP: 172.16.10.1                 Tunnel IP: 172.16.10.2

Phase 2 (subredes enrutadas):
  Local L2:  10.10.0.0/8   (toda Sede Central)
  Remote L1: 10.20.0.0/16  (toda Local 1)

Tráfico permitido via VPN:
  L1 → L2 (Sede Central):
    10.20.x.x → 10.10.30.10  TCP 443    (ERP via API Gateway)
    10.20.x.x → 10.10.10.20  TCP 389    (login AD — DC1)
    10.20.x.x → 10.10.10.21  TCP 389    (login AD — DC2 fallback)
    10.20.x.x → 10.10.10.12  UDP 123    (NTP sincronización)
    10.20.x.x → 10.10.40.10  TCP 445    (File Server central)

  L2 (Sede Central) → L1:
    10.10.60.10 → 10.20.60.10  TCP 10050  (Zabbix polling agente L1)
    10.10.60.10 → 10.20.x.x    UDP 161    (SNMP pfSense-L1 y switch L1)
```

### 4.4 Túnel L2 ↔ L3 (Sede Central ↔ Local 3)

```
pfSense-BORDE (L2 — Sede Central)      pfSense-L3 (Local 3)
  WAN1: 172.17.25.x (IP pública)         WAN1: IP pública ISP L3
  Tunnel IP: 172.16.20.2                 Tunnel IP: 172.16.20.1

Phase 2 (subredes enrutadas):
  Local L2:  10.10.0.0/8   (toda Sede Central)
  Remote L3: 10.30.0.0/16  (toda Local 3)

Tráfico permitido: idéntico al túnel L1-L2 con subredes 10.30.x.x
  L3 → L2: ERP (TCP 443), AD (TCP 389), NTP (UDP 123), FileServer (TCP 445)
  L2 → L3: Zabbix polling (TCP 10050), SNMP (UDP 161)
```

### 4.5 Túnel L2 ↔ AWS (Sede Central ↔ AWS Cloud)

```
pfSense-BORDE (L2 — Sede Central)      AWS VPN Gateway
  WAN1: 172.17.25.x (IP pública)         IP pública AWS
  Tunnel IP L2: 172.16.30.2              Tunnel IP AWS: 172.16.30.1

Phase 2 (subredes enrutadas):
  Local L2:   10.10.0.0/8    (Sede Central completa)
  Remote AWS: 10.40.0.0/16   (VPC AWS)

Tráfico permitido via VPN AWS:
  L2 → AWS:
    10.10.50.x → S3 (pg_dump backup)           HTTPS 443
    10.10.40.x → ECR (docker push imágenes)     HTTPS 443
    10.10.60.10 → CloudWatch (métricas)         HTTPS 443

  AWS → L2:
    Sin tráfico iniciado desde AWS en operación normal.
    Solo respuestas a conexiones iniciadas desde on-prem.
```

### 4.6 Topología VPN — esquema hub-and-spoke

```
         ┌─────────────────────────────┐
         │   LOCAL 1 (Planta Prod. 1)  │
         │   pfSense-L1                │
         │   Tunnel: 172.16.10.2       │
         └───────────────┬─────────────┘
                         │ IPSec L1-L2
                         │ 172.16.10.0/30
                         ▼
┌────────────────────────────────────────────┐
│         LOCAL 2 — SEDE CENTRAL (HUB)       │
│         VM-PFSENSE-BORDE                   │
│         L1-L2: 172.16.10.1                 │
│         L2-L3: 172.16.20.2                 │
│         L2-AWS: 172.16.30.2                │
└──────────┬──────────────────┬──────────────┘
           │ IPSec L2-L3      │ IPSec L2-AWS
           │ 172.16.20.0/30   │ 172.16.30.0/30
           ▼                  ▼
┌──────────────────┐  ┌──────────────────────┐
│ LOCAL 3          │  │ AWS Cloud            │
│ pfSense-L3       │  │ AWS VPN Gateway      │
│ Tunnel: 172.16   │  │ Tunnel: 172.16.30.1  │
│ .20.1            │  └──────────────────────┘
└──────────────────┘

Comunicación L1 ↔ L3: pasa obligatoriamente por L2 (Sede Central)
```

### 4.7 Monitoreo de túneles

Zabbix monitorea el estado de cada túnel via SNMP en pfSense:

```
OID: .1.3.6.1.4.1.12325.1.200.1.2.1   (pfSense IPSec tunnel status)

Alertas configuradas:
  Túnel L1-L2 caído  → Alerta crítica (L1 sin acceso al ERP)
  Túnel L2-L3 caído  → Alerta crítica (L3 sin acceso al ERP)
  Túnel L2-AWS caído → Alerta warning (backups pausados, no impacta operación)
```

---

## 5. DMZ — Arquitectura y Segmentación

### 5.1 ¿VLAN o NIC dedicada?

**La DMZ es VLAN 30 — no NIC dedicada.**

En ESXi con vmnic2 en trunk, VLAN 30 es una subred lógica etiquetada.
pfSense crea una interfaz virtual `vmnic2.30` que actúa como GW de la DMZ (10.10.30.1).

```
vmnic2 (físico) → trunk 802.1Q con VLAN tag 30
pfSense interface VLAN30: 10.10.30.1/28 ← gateway de la DMZ
```

### 5.2 ¿La VLAN 30 va en el trunk hacia el switch?

**SÍ**, pero solo a los hipervisores que la necesitan:

```
Cisco Catalyst 1000 — distribución de VLANs por puerto trunk:

Puerto H1 (vmnic2): VLANs 10,20,30,40,50,60,99  (todas)
Puerto H2:          VLANs 10,40,60               (NO VLAN 30)
Puerto H3:          VLANs 40,50                  (NO VLAN 30)
Puerto H4:          VLANs 10,30,40,50            (SÍ VLAN 30 ← VM-BACKUP-API-GW)
Puerto AP WiFi:     Access VLAN 20               (access port, sin trunk)
```

**H4 necesita VLAN 30** porque `VM-BACKUP-API-GW` (10.10.30.20) es el standby del API Gateway.
**H2 y H3 NO reciben VLAN 30** — el switch filtra el tag 30 en esos puertos.

### 5.3 Subred DMZ

```
Subred: 10.10.30.0/28
Gateway (pfSense): 10.10.30.1
VM-WAF NGINX+ModSecurity: 10.10.30.5
VM-API-GATEWAY: 10.10.30.10
VM-BACKUP-API-GW (H4): 10.10.30.20
Broadcast: 10.10.30.15
Hosts disponibles: .2 → .14 (13 hosts)
```

### 5.4 Flujo de tráfico en la DMZ

```
Internet (usuario)
    │ HTTPS 443
    ▼
pfSense-BORDE WAN (NAT/PAT)
    │ ALLOW WAN → VLAN30 TCP 443
    ▼
VM-WAF NGINX + ModSecurity (10.10.30.5)
    │ Inspección HTTP/S capa 7
    │ Bloquea: SQLi, XSS, OWASP Top 10
    ▼
VM-API-GATEWAY (10.10.30.10) NestJS
    │ ALLOW VLAN30 → VLAN40 TCP 4222
    ▼
VM-NATS-SERVER (10.10.40.20) ← cruza inter-VLAN via pfSense
    │
    ├──► auth-ms, person-ms, sales-ms, strategic-ms
```

### 5.5 Acceso a la DMZ desde otras sedes (via VPN)

```
Operarios L1 (10.20.20.x) → VPN → pfSense-BORDE → VLAN30 → API GW
Operarios L3 (10.30.20.x) → VPN → pfSense-BORDE → VLAN30 → API GW
AWS CloudFront             → Internet → WAN pfSense → VLAN30 → API GW
```

---

## 6. VM-WAF — NGINX + ModSecurity

### 6.1 Función

Proxy reverso con WAF integrado. Todo el tráfico HTTPS pasa por aquí antes de llegar al API Gateway.

| Atributo | Valor |
|---|---|
| IP | 10.10.30.5 |
| VLAN | VLAN 30 DMZ |
| Software | NGINX + ModSecurity v3 |
| Puerto expuesto | TCP 443 (recibe desde pfSense) |
| Puerto backend | TCP 443 → VM-API-GATEWAY 10.10.30.10 |

### 6.2 Reglas ModSecurity activas

```
- OWASP Core Rule Set (CRS) 3.x
- SQLi detection y bloqueo
- XSS filtering
- Path traversal protection
- Rate limiting: max 100 req/seg por IP
- Bloqueo de User-Agents maliciosos
- Geo-blocking (opcional — IPs fuera de Perú)
```

### 6.3 Configuración NGINX (resumen)

```nginx
upstream api_backend {
    server 10.10.30.10:443;
}

server {
    listen 443 ssl;
    server_name api.francos.com;

    ssl_certificate     /etc/ssl/francos.crt;
    ssl_certificate_key /etc/ssl/francos.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsecurity/main.conf;

    location / {
        proxy_pass https://api_backend;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 7. VM-API-GATEWAY — NestJS + Docker

### 7.1 Función

Punto de entrada al ERP. Recibe requests HTTPS, valida JWT, enruta a microservicios via NATS.

| Atributo | Valor |
|---|---|
| IP | 10.10.30.10 |
| VLAN | VLAN 30 DMZ |
| Puerto | TCP 443 |
| Software | NestJS 11 + Docker |
| Recibe tráfico de | AWS CloudFront, Usuarios L1/L3 via VPN, Usuarios VLAN 20 |

### 7.2 Flujo de request

```
1. Request HTTPS → VM-WAF (10.10.30.5)
2. WAF inspecciona → pasa a VM-API-GW (10.10.30.10)
3. API GW extrae JWT del header Authorization
4. API GW → NATS "auth.token.validate" → auth-ms → responde {valid, userId, roles}
5. Si válido → API GW enruta a ms correspondiente via NATS
6. ms procesa → responde via NATS → API GW → responde al cliente
```

---

## 8. Cisco Catalyst 1000 — Switch Físico 802.1Q

### 8.1 Descripción

Switch físico Layer 2 que interconecta todos los hipervisores de la Sede Central.
Conectado a vmnic2 del Hipervisor 1 (trunk 802.1Q VLAN 4095 = todas las VLANs).

### 8.2 Configuración de puertos (IOS)

```ios
! Definición de VLANs
vlan 10
 name Admin
vlan 20
 name Usuarios
vlan 30
 name DMZ
vlan 40
 name Servicios
vlan 50
 name Datos
vlan 60
 name Gestion
vlan 99
 name MGMT

! Puerto uplink a H1 vmnic2 (trunk completo)
interface GigabitEthernet0/1
 description "Uplink H1 vmnic2 pfSense-BORDE"
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,50,60,99
 spanning-tree portfast trunk

! Puerto a H2 (Servicios Redundantes)
interface GigabitEthernet0/2
 description "Trunk H2 Servicios"
 switchport mode trunk
 switchport trunk allowed vlan 10,40,60

! Puerto a H3 (Backend Microservicios)
interface GigabitEthernet0/3
 description "Trunk H3 Backend"
 switchport mode trunk
 switchport trunk allowed vlan 40,50

! Puerto a H4 (Backup Critico)
interface GigabitEthernet0/4
 description "Trunk H4 Backup"
 switchport mode trunk
 switchport trunk allowed vlan 10,30,40,50

! Puerto AP WiFi (access VLAN 20)
interface GigabitEthernet0/5
 description "AP WiFi FrancosCorp"
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast

! Gestión del switch
interface Vlan99
 ip address 10.10.99.2 255.255.255.240
 description "Management VLAN"

ip default-gateway 10.10.99.1

! Seguridad básica
service password-encryption
no cdp run
spanning-tree mode rapid-pvst
```

### 8.3 VLANs por hipervisor — resumen visual

```
                  H1    H2    H3    H4    AP
VLAN 10 Admin   | ✅  | ✅  |     | ✅  |
VLAN 20 Usuarios| ✅  |     |     |     | ✅
VLAN 30 DMZ     | ✅  |     |     | ✅  |
VLAN 40 Servicios| ✅ | ✅  | ✅  | ✅  |
VLAN 50 Datos   | ✅  |     | ✅  | ✅  |
VLAN 60 Gestión | ✅  | ✅  |     |     |
VLAN 99 MGMT    | ✅  |     |     |     |
```

---

## 9. AP WiFi — FrancosCorp

| Atributo | Valor |
|---|---|
| IP | 10.10.20.50 |
| VLAN | VLAN 20 — Usuarios |
| SSID | FrancosCorp |
| Puerto del switch | GigabitEthernet0/5 (access VLAN 20) |
| Seguridad WiFi | WPA2-Enterprise (802.1X via AD) o WPA2-PSK |
| Usuarios | Workstations inalámbricas — áreas Admin y Ventas |

### 9.1 Flujo de conexión WiFi

```
Dispositivo WiFi → asocia con SSID FrancosCorp
    │ WPA2
    ▼
AP (access port VLAN 20) → Cisco Switch → trunk H1 → pfSense VLAN 20
    │ DHCP request
    ▼
pfSense DHCP VLAN 20 → asigna 10.10.20.x, DNS: 10.10.10.20
    │ Login Windows
    ▼
LDAP → VM-AD-DC (10.10.10.20) → autenticación dominio francos.local
```

---

## 10. Diagrama de flujo completo H1

```
INTERNET
    │
    ├── ISP1 ──── vmnic0 ──→ ┌─────────────────────────────┐
    │                        │    VM-PFSENSE-BORDE          │
    └── ISP2 ──── vmnic1 ──→ │    Dual-WAN Failover         │
                             │    IPSec: L1 | L3 | AWS       │
                             │    DHCP: todas las VLANs      │
                             │    Firewall: reglas VLAN      │
                             └──────────┬──────────────────-─┘
                                        │ vmnic2
                                        │ Trunk 802.1Q
                                        │ VLANs 10,20,30,40,50,60,99
                                        ▼
                               ┌─────────────────┐
                               │  Cisco Catalyst  │ ── Access VLAN20 ──► AP WiFi
                               │      1000        │
                               └──┬──┬──┬──┬──────┘
                          Trunk   │  │  │  │
                  VL10,40,60 ─────┘  │  │  └──── VL10,30,40,50 ──► H4
                  VL40,50 ──────────-┘  └──────── VL10,20,30... ──► H1 interno
                  (H2)      (H3)

Aparte (dentro de H1, vSwitch interno):
  pfSense VLAN30 ──► VM-WAF (10.10.30.5) ──► VM-API-GW (10.10.30.10) ──► NATS H3

VPN Tunnels (pfSense WAN):
  ──IPSec L1-L2──► pfSense-L1  (172.16.10.0/30 · L2:172.16.10.1 · L1:172.16.10.2)
  ──IPSec L2-L3──► pfSense-L3  (172.16.20.0/30 · L2:172.16.20.2 · L3:172.16.20.1)
  ──IPSec L2-AWS─► AWS VPN GW  (172.16.30.0/30 · L2:172.16.30.2 · AWS:172.16.30.1)
```

---

## 11. Relación con la rúbrica (master.pdf)

| Entregable | Criterio | Cómo lo cubre H1 |
|---|---|---|
| **E1 — CE0311** | Levantamiento de requerimientos | Multi-WAN, VPN mesh 3 sedes, DMZ para ERP público |
| **E1 — CE0313** | Segmentación VLAN/DMZ/Subnetting | 7 VLANs documentadas + DMZ aislada + reglas inter-VLAN |
| **E1 — CE0314** | Redundancia y Alta Disponibilidad | Dual-WAN failover < 10 seg + pfSense CARP (futuro) |
| **E1 — CE0315** | Cumplimiento de estándares | IEEE 802.1Q trunk + TIA/EIA cableado + IPSec IKEv2 NIST |
| **E4 — Criterio 3** | Routing estático/dinámico | Rutas estáticas por VLAN en pfSense + rutas VPN |
| **E4 — Criterio 4** | Controles de acceso ACL | Reglas firewall pfSense por VLAN documentadas y probadas |
| **E5 — CE0322** | Controles técnicos (Firewall, Cifrado) | pfSense reglas + IPSec AES-256-GCM + WAF ModSecurity |
| **E6 — Criterio 2** | Servicios Web | VM-API-GATEWAY HTTPS 443 + VM-WAF como proxy seguro |

---

*Documento técnico de especificación — Franco's SAC ITI | UPeU 2026*
*Generado el 31/05/2026*
