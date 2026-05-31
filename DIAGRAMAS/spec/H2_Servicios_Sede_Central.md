# HIPERVISOR 2 — Servicios Centrales | Sede Central (LOCAL 2)
**Proyecto:** Franco's SAC — Infraestructura Tecnológica  
**Área:** ITI — UPeU 2026  
**Estándares aplicados:** ISO 27001 · ISO/IEC 20000 · ITIL 4 · TIA-942  
**Fecha:** 31/05/2026

---

## 1. Resumen del Hipervisor

HIPERVISOR 2 aloja los **servicios de infraestructura centralizada** de la Sede Central.  
No corre microservicios ni bases de datos de negocio — esos están en H3.  
Su propósito es proveer los servicios que **toda la organización necesita** para funcionar:
autenticación, tiempo, almacenamiento y monitoreo.

### Especificaciones del host (ESXi Lab UPeU)
| Campo | Valor |
|---|---|
| Plataforma | VMware ESXi 8.x |
| Conectividad | Cisco Catalyst 1000 — Trunk 802.1Q |
| VLANs servidas | VLAN 10 (Admin), VLAN 40 (Servicios), VLAN 60 (Gestión) |
| VMs alojadas | 4 VMs |

---

## 2. Inventario de VMs

| VM | IP | VLAN | Rol principal |
|---|---|---|---|
| VM-AD-DC | 10.10.10.20 | VLAN 10 | Active Directory + DNS Server |
| VM-NTP | 10.10.10.12 | VLAN 10 | NTP Server (Chrony) |
| VM-FILESERVER | 10.10.40.10 | VLAN 40 | Samba + NFS centralizado |
| VM-MONITOR | 10.10.60.10 | VLAN 60 | Zabbix + Grafana + cloudwatch-agent |

> **Nota sobre DHCP:** pfSense-BORDE (H1) gestiona DHCP para todas las VLANs de forma nativa.  
> No se requiere VM dedicada para DHCP. pfSense entrega `DNS1=10.10.10.20` y `DNS2=10.10.10.21` a todos los clientes.

---

## 3. VM-AD-DC — Active Directory + DNS Server

### 3.1 Descripción
Servidor de dominio basado en **Samba AD-DC** (equivalente a Windows Server Active Directory).  
Es el componente de identidad central de toda la infraestructura Franco's SAC.  
Gestiona la autenticación de **todos** los usuarios: Sede Central, Local 1 y Local 3.

### 3.2 Servicios que provee

| Servicio | Protocolo / Puerto | Función |
|---|---|---|
| **Kerberos** | TCP/UDP 88 | Emisión de tickets de autenticación para login de usuarios al dominio `francos.local` |
| **LDAP** | TCP 389 | Consultas al directorio (usuarios, grupos, OUs, atributos) |
| **LDAPS** | TCP 636 | LDAP sobre TLS — consultas cifradas desde microservicios y apps |
| **DNS** | TCP/UDP 53 | Resolución interna autoritativa para `francos.local` |
| **Sysvol / GPO** | TCP 445 (SMB) | Distribución de Políticas de Grupo a todas las workstations del dominio |
| **Global Catalog** | TCP 3268 | Búsqueda de objetos en todo el directorio |
| **NetLogon** | TCP/UDP 135 | Validación de login de workstations contra el dominio |

### 3.3 Estructura del dominio

```
Dominio: francos.local
Domain Controller: DC1 (VM-AD-DC — 10.10.10.20)

Unidades Organizativas (OUs):
├── OU=Produccion
│   └── Usuarios operarios planta (L1, L3)
├── OU=Ventas
│   └── Usuarios área comercial
├── OU=Administracion
│   └── Usuarios administración y gerencia
├── OU=TI
│   └── Cuentas de servicio, admins de red
└── OU=Servidores
    └── Cuentas de máquina de todas las VMs
```

### 3.4 DNS — Resolución interna

VM-AD-DC es el **DNS autoritativo** para `francos.local`.  
Samba AD-DC integra DNS nativo — no requiere servidor DNS adicional.

```
Zona autoritativa:    francos.local
Registros automáticos (AD):
  _ldap._tcp.francos.local       → 10.10.10.20
  _kerberos._tcp.francos.local   → 10.10.10.20
  _gc._tcp.francos.local         → 10.10.10.20

Registros manuales:
  api.francos.local              → 10.10.30.10  (API Gateway)
  monitor.francos.local          → 10.10.60.10  (Zabbix)
  files.francos.local            → 10.10.40.10  (FileServer)
  ntp.francos.local              → 10.10.10.12  (NTP)

Forward zona externa (internet):
  *.* → pfSense Unbound (10.10.10.1) → 8.8.8.8
```

### 3.5 Integración con microservicios

Los microservicios en H3 usan LDAP/LDAPS para validar credenciales:

```
auth-ms (10.10.40.21)
  │
  └── LDAPS 636 ──→ VM-AD-DC (10.10.10.20)
                    Valida: usuario + contraseña + grupo
                    Devuelve: JWT con roles del usuario
```

### 3.6 GPOs aplicadas

| GPO | Aplica a | Efecto |
|---|---|---|
| Password Policy | Todos los usuarios | Mínimo 10 chars, complejidad, rotación 90 días |
| Screen Lock | Workstations | Bloqueo automático a los 5 minutos |
| Software Restriction | OU=Produccion | Solo apps autorizadas |
| Firewall Policy | Servidores | Windows Firewall habilitado en todas las VMs |
| Audit Policy | Todos | Log de login exitoso y fallido |

---

## 4. Redundancia de Active Directory

### 4.1 Arquitectura DC1 + DC2

La redundancia de AD se logra con un **segundo Domain Controller (DC2)** ubicado en **HIPERVISOR 4**.  
Ambos DCs replican automáticamente mediante **Samba DRS (Directory Replication Service)**.

```
┌─ HIPERVISOR 2 ─────────┐        ┌─ HIPERVISOR 4 ─────────┐
│  VM-AD-DC (DC1)         │        │  VM-AD-DC-2 (DC2)       │
│  IP: 10.10.10.20        │◄──────►│  IP: 10.10.10.21        │
│  FSMO roles             │ replic.│  Replica completa       │
│  DNS primario           │        │  DNS secundario         │
│  VLAN 10                │        │  VLAN 10                │
└─────────────────────────┘        └─────────────────────────┘
```

> DC2 en H4 es deliberado: H4 ya es el hipervisor de backup crítico.  
> Si H2 falla completamente, H4 mantiene tanto las BDs en réplica como la autenticación.

### 4.2 Replicación entre DCs

| Componente replicado | Mecanismo | Frecuencia |
|---|---|---|
| Base de datos AD (ntds.dit) | Samba DRS sobre LDAP | Tiempo real (cambios urgentes < 15 seg) |
| Sysvol (GPOs, scripts) | rsync o DFSR sobre Samba | Cada 5 minutos |
| Zona DNS `francos.local` | Replicación de zona integrada en AD | Tiempo real |
| Hashes de contraseñas | DRS cifrado | Tiempo real |

### 4.3 FSMO Roles

Los roles FSMO residen en DC1. Si DC1 falla, se hace **seize** manual en DC2:

| Rol FSMO | DC propietario | Impacto si cae |
|---|---|---|
| PDC Emulator | DC1 (10.10.10.20) | Sincronización de contraseñas más lenta |
| RID Master | DC1 | No se pueden crear nuevos objetos AD |
| Infrastructure Master | DC1 | Inconsistencias menores en referencias |
| Schema Master | DC1 | No se puede modificar el esquema AD |
| Domain Naming Master | DC1 | No se pueden agregar dominios nuevos |

> Para Franco's SAC: el seize de FSMO es un procedimiento operativo documentado — no ocurre automáticamente.

### 4.4 DNS con dos DCs

```
pfSense DHCP entrega a todos los clientes:
  DNS1: 10.10.10.20  (VM-AD-DC  — H2) ← primario
  DNS2: 10.10.10.21  (VM-AD-DC-2— H4) ← secundario
  DNS3: 10.10.10.1   (pfSense Unbound) ← caché/fallback

Resolución:
  1. Cliente pregunta a DNS1 (10.10.10.20)
  2. Si no responde → pregunta a DNS2 (10.10.10.21)
  3. Si no responde → pregunta a pfSense Unbound (caché)
```

### 4.5 Escenarios de fallo

| Escenario | Impacto | Recuperación |
|---|---|---|
| VM-AD-DC (DC1) cae | DC2 asume auth y DNS automáticamente | Ninguna — transparente para usuarios |
| H2 cae completo | DC2 en H4 sirve todo | Ninguna — transparente para usuarios |
| H4 cae completo | DC1 en H2 sirve solo | Ninguna — sin impacto inmediato |
| H2 + H4 caen | Sin autenticación de dominio | Reinicio de cualquiera de los dos |
| Red VPN cae (L1/L3) | L1/L3 sin login de dominio | Resuelve al restaurar VPN |

---

## 5. VM-NTP — NTP Server (Chrony)

### 5.1 Descripción

Servidor de tiempo para toda la infraestructura. Usa **Chrony** (más preciso y liviano que ntpd).

### 5.2 Por qué es crítico

Kerberos (protocolo de autenticación de AD) **rechaza tickets si el reloj difiere más de 5 minutos** entre cliente y servidor. Sin NTP sincronizado:
- Login de usuarios falla con error "clock skew too great"
- Logs de auditoría tienen timestamps inconsistentes
- Certificados TLS pueden marcar error de validez temporal

### 5.3 Jerarquía NTP en la infraestructura

```
Internet (pool.ntp.org — stratum 1/2)
        │
        ▼
VM-NTP (10.10.10.12) — stratum 3
Chrony sincroniza contra pool.ntp.org
        │
        ├──→ pfSense-BORDE        (10.x.x.x)
        ├──→ Cisco Catalyst 1000  (10.10.x.x)
        ├──→ Todas las VMs H1/H2/H3/H4
        ├──→ VM-AD-DC / VM-AD-DC-2
        ├──→ pfSense-L1  (via VPN → 10.20.x.x)
        ├──→ VMs Local 1
        ├──→ pfSense-L3  (via VPN → 10.30.x.x)
        └──→ VMs Local 3
```

### 5.4 Configuración Chrony (resumen)

```
# /etc/chrony.conf
pool pool.ntp.org iburst
allow 10.0.0.0/8          # permite consultas desde toda la infra
local stratum 10           # sirve como fallback si pierde internet
```

### 5.5 Redundancia NTP

pfSense-BORDE también puede configurarse como servidor NTP secundario.  
Si VM-NTP cae, pfSense sirve tiempo con precisión aceptable mientras se restaura VM-NTP.

---

## 6. VM-FILESERVER — Samba + NFS Centralizado

### 6.1 Descripción

Servidor de archivos compartidos para todas las áreas de Franco's SAC.  
Soporta clientes Windows (Samba/SMB) y Linux (NFS).

### 6.2 Shares por área

| Share | Protocolo | Acceso | Propósito |
|---|---|---|---|
| `\\files\produccion` | SMB/Samba | OU=Produccion | Partes de producción, fichas técnicas, recetas |
| `\\files\ventas` | SMB/Samba | OU=Ventas | Contratos, listas de precios, reportes de ventas |
| `\\files\administracion` | SMB/Samba | OU=Administracion | Documentos administrativos, RRHH |
| `\\files\ti` | SMB/Samba | OU=TI | Documentación técnica, scripts, backups locales |
| `/mnt/nfs/shared` | NFS | VMs Linux | Volúmenes compartidos entre microservicios (logs, exports) |

### 6.3 Integración con AD

Samba File Server se integra con VM-AD-DC para autenticación:
- Los usuarios se autentican con sus credenciales del dominio `francos.local`
- Permisos heredados de grupos AD (no se gestionan usuarios locales en el servidor)
- Auditoría de acceso: quién accedió, qué archivo, a qué hora

### 6.4 Acceso desde otras sedes

Via túneles IPSec VPN:
- L1 (operarios producción) → `\\files\produccion`
- L3 (operarios 2da planta) → `\\files\produccion`
- Cada sede también tiene su VM-FILESERVER local para archivos del día a día

### 6.5 Backup del File Server

```
Estrategia:
  - rsync diario 23:30 → S3 Bucket (files-backup/)
  - Retención: 30 días en S3
  - Snapshot ESXi semanal del volumen de datos
```

---

## 7. VM-MONITOR — Zabbix + Grafana + cloudwatch-agent

### 7.1 Descripción

Plataforma centralizada de monitoreo de **toda la infraestructura** de Franco's SAC:
Sede Central, Local 1, Local 3 y AWS Cloud.

### 7.2 Componentes

| Componente | Puerto | Función |
|---|---|---|
| **Zabbix Server 6.x** | TCP 10051 | Recolección de métricas vía agentes y SNMP |
| **Zabbix Agent 2** | TCP 10050 | Instalado en cada VM — reporta métricas al servidor |
| **Grafana** | TCP 3000 | Dashboards visuales de métricas y alertas |
| **cloudwatch-agent** | HTTPS 443 | Envía métricas de VMs seleccionadas a AWS CloudWatch |

### 7.3 Qué monitorea

#### Dispositivos físicos/red (SNMP)
| Dispositivo | IP | Métricas |
|---|---|---|
| Cisco Catalyst 1000 | 10.10.99.2 | CPU, puertos activos, tráfico por interfaz, errores |
| pfSense-BORDE | 10.10.99.1 | CPU, RAM, estado WAN1/WAN2, estado túneles VPN, conexiones activas |
| AP WiFi | 10.10.20.50 | Clientes conectados, señal, tráfico |

#### VMs Sede Central (Agente Zabbix)
| VM | IP | Métricas clave |
|---|---|---|
| VM-AD-DC | 10.10.10.20 | CPU, RAM, estado servicio Samba, replicación AD |
| VM-NTP | 10.10.10.12 | Estado Chrony, offset con upstream |
| VM-FILESERVER | 10.10.40.10 | CPU, RAM, espacio en disco, conexiones SMB/NFS activas |
| VM-API-GATEWAY | 10.10.30.10 | CPU, RAM, requests/seg, tiempo de respuesta, errores HTTP |
| VM-NATS-SERVER | 10.10.40.20 | Mensajes/seg, colas pendientes, memoria |
| person-db | 10.10.50.10 | Conexiones activas, queries/seg, tamaño de BD, replicación lag |
| sales-invent-db | 10.10.50.11 | Ídem |
| strategic-db | 10.10.50.12 | Ídem |
| H4 BDs réplica | 10.10.50.20-22 | Streaming replication lag (debe ser < 5 min = RPO) |

#### Sedes remotas (Agente Zabbix via VPN)
| Agente | IP | Métricas |
|---|---|---|
| Agente Zabbix-L1 | 10.20.60.10 | CPU/RAM VMs Local 1, estado pfSense-L1, conectividad VPN |
| Agente Zabbix-L3 | 10.30.60.10 | CPU/RAM VMs Local 3, estado pfSense-L3, conectividad VPN |

### 7.4 Alertas configuradas

| Alerta | Umbral | Acción |
|---|---|---|
| VM caída | Ping timeout 3 intentos | Email + Telegram al equipo TI |
| CPU alto | > 85% por 5 minutos | Warning en dashboard |
| RAM alto | > 90% | Warning + alerta crítica |
| Disco lleno | > 80% usado | Alerta preventiva |
| VPN túnel caído | Estado down | Alerta crítica inmediata |
| Replication lag BD | > 5 minutos | Alerta crítica (viola RPO) |
| AD-DC sin respuesta | LDAP timeout | Alerta crítica |
| NTP offset alto | > 2 segundos | Warning (riesgo Kerberos) |

### 7.5 Dashboards Grafana

| Dashboard | Contenido |
|---|---|
| **Infraestructura Global** | Estado general de todas las sedes (verde/amarillo/rojo) |
| **Sede Central** | Métricas en tiempo real H1/H2/H3/H4 |
| **Túneles VPN** | Estado y latencia L1↔L4, L3↔L4, AWS↔L4 |
| **Bases de Datos** | Queries/seg, connections, replication lag |
| **SLA Dashboard** | Disponibilidad histórica por servicio vs. meta |

### 7.6 cloudwatch-agent

El agente envía métricas seleccionadas a **AWS CloudWatch** via el túnel VPN:

```
VM-MONITOR → AWS VPN Gateway → CloudWatch
Métricas enviadas:
  - Disponibilidad de la API (% uptime)
  - Latencia promedio de respuesta
  - Errores HTTP 5xx por hora
```
Útil para correlacionar eventos on-prem con el comportamiento del CDN CloudFront.

---

## 8. Diagrama de interacción de servicios H2

```
                    ┌─────────────────────────────────────────┐
                    │        HIPERVISOR 2 — SERVICIOS         │
                    │                                         │
  Usuarios          │  ┌──────────────┐   ┌──────────────┐   │
  francos.local ───►│  │  VM-AD-DC    │   │   VM-NTP     │   │
  (LDAP/Kerberos)   │  │  DC1 + DNS   │◄──│   Chrony     │   │
                    │  │  10.10.10.20 │   │  10.10.10.12 │   │
  auth-ms ─────────►│  └──────┬───────┘   └──────────────┘   │
  (LDAPS 636)       │         │ replica                       │
                    │         ▼                               │
                    │  ┌──────────────┐   ┌──────────────┐   │
  Todas las VMs ───►│  │ VM-FILESERVER│   │  VM-MONITOR  │   │
  (SMB/NFS)         │  │  10.10.40.10 │   │  10.10.60.10 │   │
                    │  └──────────────┘   └──────┬───────┘   │
                    │                            │           │
                    └────────────────────────────┼───────────┘
                                                 │ SNMP + Agentes
                                    ┌────────────▼───────────────┐
                                    │  H1 + H3 + H4 + L1 + L3   │
                                    │  + pfSense + Cisco Switch  │
                                    └────────────────────────────┘
                                                 │
                                    ┌────────────▼───────────────┐
                                    │   AWS CloudWatch (via VPN) │
                                    └────────────────────────────┘
```

---

## 9. Flujo de servicios H2 hacia otras sedes

Los servicios de H2 llegan a **Local 1** y **Local 3** a través de los túneles IPSec VPN.

| Servicio | Desde H2 | Hacia L1 / L3 | Via |
|---|---|---|---|
| Autenticación AD | VM-AD-DC `10.10.10.20` | Login de operarios en dominio `francos.local` | VPN L1-L4 / L3-L4 |
| DNS `francos.local` | VM-AD-DC `10.10.10.20` | Resolución interna en L1/L3 | VPN |
| Sincronización NTP | VM-NTP `10.10.10.12` | pfSense-L1, pfSense-L3, VMs locales | VPN |
| Monitoreo | VM-MONITOR `10.10.60.10` | Recibe métricas de agentes Zabbix L1/L3 | VPN |
| Archivos centrales | VM-FILESERVER `10.10.40.10` | Documentos corporativos compartidos | VPN |

---

## 10. Resumen de redundancia H2

| Servicio | Redundancia | Mecanismo |
|---|---|---|
| Active Directory | ✅ DC2 en H4 (10.10.10.21) | Samba DRS replicación continua |
| DNS | ✅ DC2 + pfSense Unbound | DNS2=10.10.10.21, DNS3=10.10.10.1 |
| NTP | ✅ pfSense como fallback | pfSense NTP server habilitado |
| File Server | ⚠️ Backup a S3 (no réplica caliente) | rsync nocturno + snapshot ESXi |
| Monitoreo | ⚠️ Sin réplica (servicio de gestión) | Snapshot ESXi semanal |

---

## 11. Relación con la rúbrica (master.pdf)

| Entregable | Criterio | Cómo lo cubre H2 |
|---|---|---|
| **E1 — CE0314** | Redundancia y Alta Disponibilidad | DC1+DC2 replicación, DNS triple, NTP con fallback |
| **E3 — CE0331** | Arquitectura Tier II | H2 con servicios redundantes en hipervisor dedicado |
| **E3 — CE0332** | Layout físico | H2 separado de H3 (backend) y H1 (borde) |
| **E3 — CE0334** | Virtualización | VMs en ESXi, servicios desacoplados por VM |
| **E5 — CE0322** | Controles IAM | AD + LDAPS + GPOs + mínimo privilegio por OU |
| **E6 — Criterio 2** | Servicios AD, DNS, Web, BD | VM-AD-DC (AD+DNS), FILESERVER, MONITOR |
| **E6 — Criterio 6** | Monitoreo de infraestructura | VM-MONITOR: Zabbix + Grafana + alertas |

---

*Documento técnico de especificación — Franco's SAC ITI | UPeU 2026*  
*Generado el 31/05/2026*
