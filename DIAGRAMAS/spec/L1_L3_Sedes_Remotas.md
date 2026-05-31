# LOCAL 1 y LOCAL 3 — Sedes Remotas | Franco's SAC
**Proyecto:** Franco's SAC — Infraestructura Tecnológica
**Área:** ITI — UPeU 2026
**Estándares:** TIA/EIA-568 · IEEE 802.1Q · ISO 27001 · ITIL 4
**Fecha:** 31/05/2026

---

## 1. Descripción general

Franco's SAC opera con **3 locales**:

| Local | Nombre | Rol | Subredes |
|---|---|---|---|
| **LOCAL 1** | Planta de Producción 1 | Sede remota — operarios producción | 10.20.0.0/16 |
| **LOCAL 2** | Sede Central | Hub principal — todos los servicios críticos | 10.10.0.0/16 |
| **LOCAL 3** | Segunda Planta de Producción | Sede remota — operarios 2da planta | 10.30.0.0/16 |

LOCAL 1 y LOCAL 3 son **sedes remotas simétricas**: misma arquitectura, mismos servicios locales,
distinta dirección IP. Se conectan a LOCAL 2 (Sede Central) mediante túneles IPSec IKEv2.

### Principio de diseño: sede remota liviana
Los servicios críticos (ERP, BDs, AD primario) están centralizados en LOCAL 2.
LOCAL 1 y LOCAL 3 tienen **servicios mínimos locales** para operar de forma autónoma
ante una caída del VPN:

```
Servicios locales (sin necesidad de VPN):
  ✅ DHCP — pfSense local
  ✅ DNS — RODC local (caché francos.local)
  ✅ NTP — pfSense local
  ✅ Autenticación AD — RODC local (credenciales cacheadas)
  ✅ Archivos locales — VM-FILESERVER local

Servicios que requieren VPN activo:
  ⚠️ ERP (microservicios en Sede Central)
  ⚠️ Sincronización AD (cambios de contraseña, nuevos usuarios)
  ⚠️ Monitoreo remoto (Zabbix agente → Sede Central)
```

---

## 2. LOCAL 1 — Planta de Producción 1

### 2.1 Inventario de componentes

| Componente | IP / Subred | Función |
|---|---|---|
| VM-PFSENSE-L1 | WAN dinámica | Firewall + Dual-WAN + IPSec + DHCP + DNS + NTP |
| HIPERVISOR 5 (ESXi Lab UPeU — TBD) | — | Plataforma de virtualización |
| VM-AD-DC-L1 (DC3 — RODC) | 10.20.10.20 / VLAN 10 | Active Directory Read-Only + DNS local |
| VM-FILESERVER-L1 | 10.20.40.10 / VLAN 40 | Samba/NFS + **Agente Zabbix** |
| Workstations L1 | 10.20.20.x / VLAN 20 | Workstations operarios producción |
| APs físicos | VLAN 20 (futuro) | WiFi para operarios (planificado) |

### 2.2 VLANs LOCAL 1

| VLAN | Nombre | Subred | Gateway | Propósito |
|---|---|---|---|---|
| VLAN 10 | Admin | 10.20.10.0/24 | 10.20.10.1 | Administración y servidores |
| VLAN 20 | Usuarios | 10.20.20.0/24 | 10.20.20.1 | Workstations operarios |
| VLAN 60 | Gestión | 10.20.60.0/28 | 10.20.60.1 | Monitoreo y gestión |
| VLAN 99 | MGMT | 10.20.99.0/28 | 10.20.99.1 | Gestión ESXi hipervisor |

### 2.3 VM-PFSENSE-L1 — Servicios integrados

pfSense-L1 provee todos los servicios de red de LOCAL 1 de forma nativa.
No se requieren VMs adicionales para estos servicios.

#### Dual-WAN Failover
```
WAN1 (vmnic1): ISP1 — Cisco Router — GW: 172.17.25.121  ← ACTIVO primario
WAN2 (vmnic0): ISP2 — Fortigate    — GW: 100.17.25.121  ← STANDBY failover

Failover: si WAN1 falla (3 pings perdidos a 8.8.8.8) → activa WAN2 en < 10 seg
```

#### Túnel IPSec — L1 ↔ L2 (Sede Central)
```
Protocolo:     IPSec IKEv2
Cifrado:       AES-256-GCM / SHA-256 / DH Group 14
Subred túnel:  172.16.10.0/30
  IP local L1: 172.16.10.2
  IP remota L2: 172.16.10.1
Phase 2:
  Local:  10.20.0.0/16  (toda L1)
  Remote: 10.10.0.0/16  (toda L2 Sede Central)
DPD: habilitado — detecta caída del túnel en 30 seg
```

#### DHCP por VLAN (pfSense nativo)
```
VLAN 10: 10.20.10.50 – 10.20.10.200
  DNS entregado: 10.20.10.20 (RODC local) primario
                 10.10.10.20 (DC1 Sede Central via VPN) secundario

VLAN 20: 10.20.20.50 – 10.20.20.200
  DNS entregado: 10.20.10.20 (RODC local) primario
                 10.10.10.20 (DC1 Sede Central via VPN) secundario
```

#### DNS — Unbound en pfSense (fallback)
```
pfSense Unbound actúa como DNS terciario:
  francos.local → forward a RODC (10.20.10.20)
  internet      → forward a 8.8.8.8
  caché local   → sirve respuestas aunque VPN esté caído (TTL)
```

#### NTP Server — pfSense
```
pfSense-L1 como servidor NTP para LOCAL 1:
  Sincroniza desde: VM-NTP Sede Central (10.10.10.12) via VPN
  Sirve a: VM-AD-DC-L1, VM-FILESERVER-L1, workstations VLAN 10/20
  Si VPN cae: sirve desde reloj local (stratum 4 — aceptable)
```

#### Reglas de firewall L1

```
ALLOW VLAN20 → VPN → 10.10.30.10 TCP 443    (operarios → ERP via API Gateway)
ALLOW VLAN10 → VPN → 10.10.10.20 TCP 389    (admin → AD DC1 Sede Central)
ALLOW VLAN20 → VLAN10 TCP 389/88            (login dominio → RODC local)
ALLOW VLAN10/20 → VLAN40 TCP 445            (acceso fileserver local)
ALLOW VLAN60 → VPN → 10.10.60.10 TCP 10051  (Zabbix agente → Sede Central)
DENY  VLAN20 → VLAN99                        (usuarios no acceden a MGMT)
DENY  VLAN20 → WAN directo                   (sin salida directa a internet para usuarios)
```

### 2.4 VM-AD-DC-L1 — RODC (DC3)

| Atributo | Valor |
|---|---|
| IP | 10.20.10.20 |
| VLAN | VLAN 10 — Admin |
| Software | Samba AD-DC (modo RODC) |
| Rol en dominio | DC3 — Read-Only Domain Controller |
| Replica desde | DC1 (10.10.10.20) via VPN L1-L2 |

#### Qué hace el RODC

```
RODC = Read-Only Domain Controller

✅ Autentica usuarios con credenciales CACHEADAS localmente
✅ Resuelve DNS francos.local sin necesidad de VPN
✅ Sirve tickets Kerberos para usuarios que ya iniciaron sesión antes
✅ Aplica GPOs cacheadas a workstations

❌ No puede procesar cambios de contraseña (necesita DC1 via VPN)
❌ No puede crear usuarios nuevos
❌ Primer login de usuario nuevo requiere VPN activo
```

#### Replicación DC1 → DC3 (RODC)

```
DC1 (Sede Central, 10.10.10.20)
    │
    └── Samba DRS via VPN L1-L2 ──────► DC3-RODC (L1, 10.20.10.20)
        Replica: base de datos AD         Solo lectura — no escribe de vuelta
        Replica: zona DNS francos.local   Cada 5 min (Sysvol)
        Replica: GPOs                     Urgentes < 15 seg
```

#### Comportamiento ante caída del VPN

```
VPN L1-L2 cae
    │
    ├── DNS francos.local: ✅ RODC responde localmente
    ├── Kerberos tickets:  ✅ RODC emite para usuarios cacheados
    ├── Login workstation: ✅ si usuario ya inició sesión antes en L1
    ├── GPOs:              ✅ aplica desde caché local
    │
    ├── Login usuario nuevo: ❌ requiere VPN → DC1
    └── Cambio contraseña:  ❌ requiere VPN → DC1
```

#### FSMO Roles
El RODC **no tiene** roles FSMO. Todos los FSMO están en DC1 (Sede Central).
El RODC es solo un punto de autenticación local — no puede operar como DC primario.

### 2.5 VM-FILESERVER-L1 — Samba/NFS + Agente Zabbix

| Atributo | Valor |
|---|---|
| IP | 10.20.40.10 |
| VLAN | VLAN 40 — (Servicios locales) |
| Software | Samba 4.x + NFS + Zabbix Agent 2 |

#### Shares locales

```
\\10.20.40.10\produccion-l1   → Operarios L1 (partes diarios, reportes turno)
\\10.20.40.10\temp            → Archivos temporales de producción
/mnt/nfs/l1                   → Montaje NFS para VMs locales
```

#### Agente Zabbix — configuración

```ini
# /etc/zabbix/zabbix_agentd.conf
ServerActive=10.10.60.10     ← VM-MONITOR Sede Central (via VPN)
Hostname=VM-FILESERVER-L1
RefreshActiveChecks=120
Timeout=10
```

**Modo activo** — el agente inicia la conexión TCP 10051 hacia Sede Central.
Funciona correctamente a través del túnel VPN L1-L2.

**Qué monitorea el agente desde L1:**

| Qué | Cómo |
|---|---|
| VM-FILESERVER-L1 (CPU, RAM, disco) | Agente interno |
| Samba servicio activo | Agente — process check |
| VM-AD-DC-L1 disponibilidad | ICMP ping desde el agente |
| pfSense-L1 estado WAN/VPN | SNMP hacia pfSense |
| Estado túnel L1-L2 | SNMP OID pfSense IPSec |

---

## 3. LOCAL 3 — Segunda Planta de Producción

### 3.1 Inventario de componentes

| Componente | IP / Subred | Función |
|---|---|---|
| VM-PFSENSE-L3 | WAN dinámica | Firewall + Dual-WAN + IPSec + DHCP + DNS + NTP |
| HIPERVISOR 6 (ESXi Lab UPeU — TBD) | — | Plataforma de virtualización |
| VM-AD-DC-L3 (DC4 — RODC) | 10.30.10.20 / VLAN 10 | Active Directory Read-Only + DNS local |
| VM-FILESERVER-L3 | 10.30.40.10 / VLAN 40 | Samba/NFS + **Agente Zabbix** |
| Workstations L3 | 10.30.20.x / VLAN 20 | Workstations operarios 2da planta |
| APs físicos | VLAN 20 (futuro) | WiFi para operarios (planificado) |

### 3.2 VLANs LOCAL 3

| VLAN | Nombre | Subred | Gateway | Propósito |
|---|---|---|---|---|
| VLAN 10 | Admin | 10.30.10.0/24 | 10.30.10.1 | Administración y servidores |
| VLAN 20 | Usuarios | 10.30.20.0/24 | 10.30.20.1 | Workstations operarios |
| VLAN 60 | Gestión | 10.30.60.0/28 | 10.30.60.1 | Monitoreo y gestión |
| VLAN 99 | MGMT | 10.30.99.0/28 | 10.30.99.1 | Gestión ESXi hipervisor |

### 3.3 VM-PFSENSE-L3 — Servicios integrados

Arquitectura idéntica a pfSense-L1. Solo cambian las subredes y el túnel.

#### Dual-WAN Failover
```
WAN1: ISP1  ← ACTIVO primario
WAN2: ISP2  ← STANDBY failover
Comportamiento: idéntico a pfSense-L1
```

#### Túnel IPSec — L2 (Sede Central) ↔ L3
```
Protocolo:     IPSec IKEv2
Cifrado:       AES-256-GCM / SHA-256 / DH Group 14
Subred túnel:  172.16.20.0/30
  IP remota L2: 172.16.20.2
  IP local L3:  172.16.20.1
Phase 2:
  Local:  10.30.0.0/16  (toda L3)
  Remote: 10.10.0.0/16  (toda L2 Sede Central)
```

#### DHCP por VLAN (pfSense nativo)
```
VLAN 10: 10.30.10.50 – 10.30.10.200
  DNS: 10.30.10.20 (RODC local), 10.10.10.20 (DC1 via VPN)

VLAN 20: 10.30.20.50 – 10.30.20.200
  DNS: 10.30.10.20 (RODC local), 10.10.10.20 (DC1 via VPN)
```

#### NTP y DNS — idéntico a L1 con subredes 10.30.x

### 3.4 VM-AD-DC-L3 — RODC (DC4)

| Atributo | Valor |
|---|---|
| IP | 10.30.10.20 |
| VLAN | VLAN 10 — Admin |
| Software | Samba AD-DC (modo RODC) |
| Rol en dominio | DC4 — Read-Only Domain Controller |
| Replica desde | DC1 (10.10.10.20) via VPN L2-L3 |

Comportamiento idéntico al DC3 de LOCAL 1.
Cachea credenciales de operarios de L3 para autenticación sin VPN.

### 3.5 VM-FILESERVER-L3 — Samba/NFS + Agente Zabbix

| Atributo | Valor |
|---|---|
| IP | 10.30.40.10 |
| VLAN | VLAN 40 |
| Software | Samba 4.x + NFS + Zabbix Agent 2 |

#### Shares locales
```
\\10.30.40.10\produccion-l3   → Operarios L3 (partes diarios, reportes turno)
\\10.30.40.10\temp            → Archivos temporales
```

#### Agente Zabbix — configuración
```ini
ServerActive=10.10.60.10     ← VM-MONITOR Sede Central (via VPN L2-L3)
Hostname=VM-FILESERVER-L3
RefreshActiveChecks=120
```

---

## 4. Comparativa L1 vs L3

| Aspecto | LOCAL 1 | LOCAL 3 |
|---|---|---|
| Hipervisor | H5 (ESXi TBD) | H6 (ESXi TBD) |
| pfSense | VM-PFSENSE-L1 | VM-PFSENSE-L3 |
| RODC | DC3 — 10.20.10.20 | DC4 — 10.30.10.20 |
| Fileserver | VM-FILESERVER-L1 — 10.20.40.10 | VM-FILESERVER-L3 — 10.30.40.10 |
| Workstations | 10.20.20.x (VLAN 20) | 10.30.20.x (VLAN 20) |
| Túnel VPN | L1-L2: 172.16.10.0/30 | L2-L3: 172.16.20.0/30 |
| Subred total | 10.20.0.0/16 | 10.30.0.0/16 |
| Agente Zabbix | En VM-FILESERVER-L1 | En VM-FILESERVER-L3 |

---

## 5. Servicios que llegan desde Sede Central (via VPN)

| Servicio | Origen L2 | Destino L1/L3 | Protocolo |
|---|---|---|---|
| AD sync (replicación) | DC1 10.10.10.20 | DC3/DC4 RODC | Samba DRS TCP |
| ERP acceso | VM-API-GW 10.10.30.10 | Workstations L1/L3 | HTTPS TCP 443 |
| NTP sync | VM-NTP 10.10.10.12 | pfSense-L1/L3 | UDP 123 |
| Zabbix monitoreo | VM-MONITOR 10.10.60.10 | Agente L1/L3 | TCP 10051 activo |
| File server central | VM-FILESERVER 10.10.40.10 | Workstations L1/L3 | TCP 445 SMB |

---

## 6. Topología de red L1 y L3

```
INTERNET
    │
    ├── ISP1 WAN1 ──┐
    │               ├── VM-PFSENSE-L1/L3
    └── ISP2 WAN2 ──┘   (Dual-WAN Failover)
                         │
                         ├── IPSec VPN ──────────► SEDE CENTRAL (L2)
                         │   (172.16.10/20.0/30)
                         │
                         └── Trunk 802.1Q
                               │
                         HIPERVISOR 5/6
                               │
                    ┌──────────┴──────────┐
                    │                     │
             VM-AD-DC-L1/L3        VM-FILESERVER-L1/L3
             RODC 10.x0.10.20      Samba/NFS 10.x0.40.10
             VLAN 10                + Agente Zabbix
                                    VLAN 40
                    │
             Workstations L1/L3
             10.x0.20.x (VLAN 20)
             (x = 2 para L1, x = 3 para L3)
```

---

## 7. Escenarios de fallo y recuperación

### Escenario 1 — VPN cae (L1 o L3 sin conexión a Sede Central)

```
VPN caído
├── DHCP:     ✅ pfSense local sigue asignando IPs
├── DNS:      ✅ RODC responde francos.local desde caché
├── NTP:      ✅ pfSense local desde su reloj
├── Login AD: ✅ RODC autentica usuarios cacheados
├── Archivos: ✅ fileserver local accesible
└── ERP:      ❌ API Gateway en Sede Central inaccesible
               Operarios no pueden registrar ventas/producción
               Deben anotar manualmente hasta restaurar VPN
```

**RTO del VPN:** pfSense DPD detecta caída en 30 seg → reinicia túnel automáticamente.
Si WAN1 falla → Dual-WAN activa WAN2 → VPN se reconecta en WAN2. RTO total < 2 min.

### Escenario 2 — Hipervisor local cae (H5 o H6)

```
H5/H6 caído
├── pfSense-L1/L3: ✅ no depende del hipervisor (VM en ESXi aparte o físico)
├── RODC:          ❌ sin autenticación local → requiere VPN para AD
├── Fileserver:    ❌ sin acceso a archivos locales
└── Zabbix agente: ❌ sin monitoreo de la sede
```

**Mitigación:** pfSense mantiene DHCP/DNS/NTP aunque el hipervisor caiga.
Los usuarios pueden seguir trabajando si VPN está activo (autentican contra DC1 Sede Central).

### Escenario 3 — ISP1 y ISP2 ambos caen

```
Dual-WAN fallida
├── Red interna L1/L3: ✅ funciona (DHCP, RODC, fileserver)
├── VPN:               ❌ sin internet → sin túnel
└── ERP:               ❌ sin acceso a Sede Central
```

**Mitigación:** operación manual documentada. Al restaurar cualquier WAN → VPN reconecta automático.

---

## 8. Monitoreo de L1 y L3 desde Sede Central

VM-MONITOR (10.10.60.10) en Sede Central recibe métricas de ambas sedes via VPN:

| Métrica | Fuente | Alerta si |
|---|---|---|
| VM-FILESERVER-L1/L3 CPU | Agente Zabbix | > 85% por 5 min |
| VM-FILESERVER-L1/L3 disco | Agente Zabbix | > 80% usado |
| Samba servicio | Agente Zabbix | proceso ausente |
| VM-AD-DC-L1/L3 ping | ICMP desde agente | timeout 3 intentos |
| pfSense-L1/L3 WAN status | SNMP | WAN caída |
| Túnel VPN L1-L2 / L2-L3 | SNMP pfSense | estado down |
| Agente Zabbix L1/L3 | Zabbix server | no data > 5 min |

**Alerta crítica:** si el agente de L1 o L3 deja de reportar por más de 5 minutos
→ puede indicar caída del VPN, del hipervisor o de la VM-FILESERVER.
Zabbix Server envía alerta inmediata al equipo TI.

---

## 9. Relación con la rúbrica (master.pdf)

| Entregable | Criterio | Cómo lo cubren L1 y L3 |
|---|---|---|
| **E1 — CE0311** | Levantamiento de requerimientos | Sedes remotas con necesidades de producción — operarios necesitan ERP y autenticación local |
| **E1 — CE0313** | Segmentación VLAN/Subnetting | VLANs 10/20/60/99 por sede con subredes únicas 10.20.x y 10.30.x |
| **E1 — CE0314** | Redundancia y Alta Disponibilidad | Dual-WAN en cada sede + RODC local para AD sin VPN + pfSense DHCP/DNS/NTP autónomo |
| **E4 — Criterio 1** | Configuración de dispositivos | pfSense-L1/L3: Dual-WAN, IPSec, DHCP, DNS, NTP documentados |
| **E4 — Criterio 4** | Controles de acceso ACL | Reglas firewall pfSense por VLAN en L1 y L3 |
| **E5 — CE0322** | Controles IAM | RODC cachea credenciales — autenticación disponible sin VPN |
| **E6 — Criterio 6** | Monitoreo de infraestructura | Agente Zabbix en fileserver → VM-MONITOR Sede Central via VPN |

---

*Documento técnico de especificación — Franco's SAC ITI | UPeU 2026*
*Generado el 31/05/2026*
