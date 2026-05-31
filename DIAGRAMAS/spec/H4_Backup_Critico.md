# HIPERVISOR 4 — Backup Crítico (Réplica H3) | Sede Central (LOCAL 2)
**Proyecto:** Franco's SAC — Infraestructura Tecnológica  
**Área:** ITI — UPeU 2026  
**Estándares aplicados:** ISO 27001 · ISO/IEC 20000 · ITIL 4 · TIA-942  
**Fecha:** 31/05/2026

---

## 1. Propósito del hipervisor

HIPERVISOR 4 es el **hipervisor de continuidad operativa** de la Sede Central.  
No procesa carga productiva en condiciones normales. Su función es garantizar que, ante un fallo de H2 o H3, los servicios críticos de Franco's SAC puedan ser restaurados en el menor tiempo posible.

**Rol en la arquitectura:**

| Condición | Estado H4 |
|---|---|
| Operación normal | VMs de microservicios apagadas (standby frío). DC2 y BDs réplica activos. |
| H2 falla | VM-AD-DC-2 ya está activa — toma auth/DNS automáticamente |
| H3 falla | Equipo TI levanta VMs backup de microservicios — BDs ya sincronizadas |
| H3 + H2 fallan | H4 cubre ambos roles simultáneamente |

---

## 2. Inventario de VMs

| VM | IP | VLAN | Estado normal | Rol |
|---|---|---|---|---|
| VM-AD-DC-2 (DC2) | 10.10.10.21 | VLAN 10 | **Activa** | AD réplica + DNS secundario |
| VM-BACKUP-API-GW | 10.10.30.20 | VLAN 30 | Standby frío | API Gateway réplica |
| VM-BACKUP-AUTH-MS | 10.10.40.30 | VLAN 40 | Standby frío | auth-ms réplica |
| VM-BACKUP-PERSON-MS | 10.10.40.31 | VLAN 40 | Standby frío | person-ms réplica |
| VM-BACKUP-SALES-MS | 10.10.40.32 | VLAN 40 | Standby frío | sales-invent-ms réplica |
| VM-BACKUP-STRATEGIC-MS | 10.10.40.33 | VLAN 40 | Standby frío | strategic-ms réplica |
| person-db réplica | 10.10.50.20 | VLAN 50 | **Activa** | Réplica streaming de H3 |
| sales-invent-db réplica | 10.10.50.21 | VLAN 50 | **Activa** | Réplica streaming de H3 |
| strategic-db réplica | 10.10.50.22 | VLAN 50 | **Activa** | Réplica streaming de H3 |

> **Activas permanentemente:** VM-AD-DC-2 y las 3 BDs réplica.  
> **Standby frío:** VMs de microservicios — apagadas en operación normal, listas para encender.

---

## 3. VM-AD-DC-2 — Active Directory Réplica (DC2)

### 3.1 Descripción

Segundo Domain Controller del dominio `francos.local`.  
Corre **Samba AD-DC** en modo réplica del DC1 (VM-AD-DC en H2).  
Está **activo permanentemente** — no es standby frío.

| Atributo | Valor |
|---|---|
| IP | 10.10.10.21 |
| VLAN | VLAN 10 — Admin |
| Software | Samba AD-DC 4.x |
| Rol | Domain Controller secundario — DNS secundario |

### 3.2 Servicios que provee (idénticos a DC1)

| Servicio | Puerto | Estado |
|---|---|---|
| Kerberos | TCP/UDP 88 | Activo — sirve tickets si DC1 no responde |
| LDAP | TCP 389 | Activo |
| LDAPS | TCP 636 | Activo |
| DNS `francos.local` | TCP/UDP 53 | Activo — zona replicada desde DC1 |
| Sysvol/GPO | TCP 445 | Activo — replicado desde DC1 |
| Global Catalog | TCP 3268 | Activo |

### 3.3 Replicación DC1 → DC2

```
VM-AD-DC (DC1 — H2)           VM-AD-DC-2 (DC2 — H4)
10.10.10.20                    10.10.10.21
     │                               │
     └──── Samba DRS (LDAP) ────────►│  base de datos AD
     └──── rsync Sysvol ────────────►│  GPOs + scripts
     └──── DNS zona integrada ───────►│  registros francos.local

Frecuencia: cambios urgentes < 15 seg | Sysvol cada 5 min
Protocolo: Samba Directory Replication Service (DRS) sobre TCP
```

### 3.4 Rol en redundancia DNS

pfSense DHCP entrega a todos los clientes (Sede Central + L1 + L3):

```
DNS1: 10.10.10.20  (DC1 — H2)   ← primario
DNS2: 10.10.10.21  (DC2 — H4)   ← secundario  ← este VM
DNS3: 10.10.10.1   (pfSense)     ← fallback caché
```

Si DC1 cae → los clientes cambian automáticamente a DC2 sin intervención.

### 3.5 Escenarios cubiertos

| Fallo | Respuesta de DC2 |
|---|---|
| VM-AD-DC (DC1) crashea | DC2 sirve Kerberos + LDAP + DNS inmediatamente |
| H2 completo cae | DC2 es el único DC activo — usuarios siguen con login |
| Red entre H2-H4 cae | Cada DC sirve a los clientes que puede alcanzar |
| DC2 cae | DC1 sigue solo — sin impacto en usuarios |

---

## 4. VM-BACKUP-API-GW — API Gateway Réplica

| Atributo | Valor |
|---|---|
| IP | 10.10.30.20 |
| VLAN | VLAN 30 — DMZ |
| Software | NestJS 11 + Docker |
| Estado | Standby frío |

### 4.1 Función

Réplica del VM-API-GATEWAY principal (10.10.30.10 en H1).  
En operación normal está apagada. Se activa si H1 falla completamente.

### 4.2 Procedimiento de activación

```
1. Equipo TI detecta caída de VM-API-GATEWAY (H1) vía Zabbix alerta
2. Encender VM-BACKUP-API-GW en H4
3. Actualizar imagen Docker desde ECR:
   docker pull <ECR_URI>/gateway-ms:latest
   docker-compose up -d
4. Actualizar DNS: api.francos.local → 10.10.30.20 (en DC1 o DC2)
5. Verificar conectividad: curl https://10.10.30.20/health
```

**RTO estimado:** 10-15 minutos (proceso manual documentado)

---

## 5. VMs Backup de Microservicios (Standby Frío)

### 5.1 Inventario

| VM | IP | Ms que replica | Imagen Docker |
|---|---|---|---|
| VM-BACKUP-AUTH-MS | 10.10.40.30 | auth-ms (H3: 10.10.40.21) | ECR: francos/auth-ms:latest |
| VM-BACKUP-PERSON-MS | 10.10.40.31 | person-ms (H3: 10.10.40.22) | ECR: francos/person-ms:latest |
| VM-BACKUP-SALES-MS | 10.10.40.32 | sales-invent-ms (H3: 10.10.40.23) | ECR: francos/sales-invent-ms:latest |
| VM-BACKUP-STRATEGIC-MS | 10.10.40.33 | strategic-ms (H3: 10.10.40.24) | ECR: francos/strategic-ms:latest |

### 5.2 Estado en operación normal

Las 4 VMs están **apagadas** (standby frío).  
No consumen recursos de CPU/RAM del hipervisor.  
Los discos del sistema operativo están listos con Docker instalado.

### 5.3 Procedimiento de activación ante fallo de H3

```
TRIGGER: Zabbix alerta "H3 inaccesible" o "VM-NATS-SERVER caído"

PASO 1 — Verificar (2 min)
  Confirmar que H3 no responde (ping, SSH, consola ESXi)

PASO 2 — Activar BDs réplica en H4 (5 min)
  En cada VM de BD réplica (ya activas en modo réplica):
    pg_ctl promote -D /var/lib/postgresql/data
  Las BDs réplica pasan de modo read-only a read-write (primary)
  Datos disponibles: hasta el último WAL recibido (RPO < 5 min)

PASO 3 — Levantar microservicios en H4 (10 min)
  Encender: VM-BACKUP-AUTH-MS, VM-BACKUP-PERSON-MS,
            VM-BACKUP-SALES-MS, VM-BACKUP-STRATEGIC-MS
  En cada VM:
    docker pull <ECR_URI>/<ms-name>:latest
    docker-compose up -d
  Variables de entorno: NATS_URL, DB_HOST apuntan a IPs de H4

PASO 4 — Verificar NATS conectividad (3 min)
  VM-NATS-SERVER sigue en H3 (si solo H3 parcialmente falla)
  O: levantar NATS en H4 si H3 está completamente caído

PASO 5 — Confirmar servicio (5 min)
  curl http://10.10.40.30/health  → auth-ms OK
  curl http://10.10.40.31/health  → person-ms OK
  curl http://10.10.40.32/health  → sales-ms OK
  curl http://10.10.40.33/health  → strategic-ms OK

TOTAL RTO estimado: 25-30 minutos
```

### 5.4 Conexión de microservicios backup a BDs promovidas

Una vez promovidas las BDs réplica, los ms de H4 se conectan a sus IPs locales:

```
VM-BACKUP-PERSON-MS (10.10.40.31)  → person-db réplica (10.10.50.20) ← ahora primaria
VM-BACKUP-SALES-MS  (10.10.40.32)  → sales-invent-db réplica (10.10.50.21)
VM-BACKUP-STRATEGIC-MS (10.10.40.33) → strategic-db réplica (10.10.50.22)
```

---

## 6. Bases de Datos Réplica (PostgreSQL Streaming Replication)

### 6.1 Inventario

| BD réplica | IP | Puerto | BD origen (H3) |
|---|---|---|---|
| person-db réplica | 10.10.50.20 | 5432 | person-db (10.10.50.10) |
| sales-invent-db réplica | 10.10.50.21 | 5432 | sales-invent-db (10.10.50.11) |
| strategic-db réplica | 10.10.50.22 | 5432 | strategic-db (10.10.50.12) |

### 6.2 Mecanismo: PostgreSQL Streaming Replication (WAL)

```
H3 (Primary):                          H4 (Standby):
person-db (10.10.50.10)                person-db réplica (10.10.50.20)
  │                                          │
  │  WAL records (Write-Ahead Log)           │
  └──────── TCP 5432 streaming ─────────────►│
            (cambios en tiempo real)         │
                                        modo: hot standby
                                        (read-only mientras H3 vive)
```

### 6.3 Parámetros de replicación

```ini
# postgresql.conf en H3 (primary)
wal_level = replica
max_wal_senders = 3
wal_keep_size = 256MB

# recovery.conf en H4 (standby)
standby_mode = on
primary_conninfo = 'host=10.10.50.10 port=5432 user=replicator'
restore_command = 'cp /var/lib/postgresql/archive/%f %p'
```

### 6.4 Monitoreo de replication lag

VM-MONITOR (Zabbix) consulta cada minuto:

```sql
-- Ejecutado en H3 (primary)
SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds;
```

**Alerta configurada:** si `lag_seconds > 300` (5 min) → alerta crítica en Zabbix  
**RPO garantizado:** < 5 minutos en condiciones normales de red

### 6.5 Proceso de promoción (failover)

Cuando H3 falla y se decide activar H4:

```bash
# En cada VM de BD réplica en H4:
pg_ctl promote -D /var/lib/postgresql/15/main

# Verificar que es primaria:
psql -c "SELECT pg_is_in_recovery();"
# Resultado esperado: f (false = ya es primary)
```

Una vez promovida, acepta escrituras.  
Los datos disponibles corresponden al último WAL recibido antes del fallo (RPO < 5 min).

---

## 7. Estrategia de Snapshots y Backups locales

### 7.1 Snapshot ESXi diario

Todos los días a las 23:00, ESXi toma snapshots de las VMs críticas de H4:

```
Scope del snapshot:
  - VM-AD-DC-2          → snapshot diario (estado del DC2)
  - person-db réplica   → snapshot diario
  - sales-invent-db réplica → snapshot diario
  - strategic-db réplica → snapshot diario

Retención: 7 snapshots (7 días)
Almacenamiento: VMFS6 local del hipervisor
```

### 7.2 OVF Export semanal → S3

Cada domingo a las 02:00, se exporta una imagen OVF completa de las VMs críticas a S3:

```
Destino S3: s3://francos-vm-exports/
  francos-vm-exports/
    ├── vm-ad-dc2/      → ovf_20260601.tar.gz
    ├── person-db-h4/   → ovf_20260601.tar.gz
    └── sales-db-h4/    → ovf_20260601.tar.gz

Retención: 4 semanas
Transferencia: via AWS VPN Gateway (túnel privado)
```

### 7.3 Diferencia entre Snapshot y OVF Export

| Mecanismo | Propósito | Velocidad recuperación | Dónde |
|---|---|---|---|
| Streaming Replication | BD sincronizada en tiempo real | < 5 min (promote) | H4 mismo |
| Snapshot ESXi | Estado VM del día anterior | 15-20 min (restore snap) | H4 VMFS6 |
| OVF Export S3 | Disaster recovery total (pérdida H4) | 1-2 horas (download + deploy) | AWS S3 |

---

## 8. Diagrama de relaciones H3 → H4

```
┌─ HIPERVISOR 3 (activo) ──────────────┐
│  VM-AD-DC (DC1)       10.10.10.20    │
│  person-db            10.10.50.10    │
│  sales-invent-db      10.10.50.11    │──── Streaming Replication ────┐
│  strategic-db         10.10.50.12    │     (WAL continuo)            │
│  auth-ms, person-ms,  10.10.40.21-24 │                               │
│  sales-ms, strategic-ms              │──── Samba DRS ────────────────┤
└──────────────────────────────────────┘     (AD replication)          │
                                                                        │
                                                                        ▼
┌─ HIPERVISOR 4 (backup) ──────────────────────────────────────────────┐
│                                                                       │
│  VM-AD-DC-2 (DC2)        10.10.10.21  ← ACTIVA SIEMPRE               │
│                                                                       │
│  person-db réplica       10.10.50.20  ← ACTIVA (read-only)           │
│  sales-invent-db réplica 10.10.50.21  ← ACTIVA (read-only)           │
│  strategic-db réplica    10.10.50.22  ← ACTIVA (read-only)           │
│                                                                       │
│  VM-BACKUP-API-GW        10.10.30.20  ⏸ STANDBY FRÍO                │
│  VM-BACKUP-AUTH-MS       10.10.40.30  ⏸ STANDBY FRÍO                │
│  VM-BACKUP-PERSON-MS     10.10.40.31  ⏸ STANDBY FRÍO                │
│  VM-BACKUP-SALES-MS      10.10.40.32  ⏸ STANDBY FRÍO                │
│  VM-BACKUP-STRATEGIC-MS  10.10.40.33  ⏸ STANDBY FRÍO                │
│                                                                       │
│  Snapshot diario 23:00 → VMFS6 local                                 │
│  OVF export semanal → S3 AWS (via VPN)                               │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 9. SLA y métricas de H4

| Métrica | Valor objetivo | Monitoreo |
|---|---|---|
| Replication lag person-db | < 5 min | Zabbix query pg_last_xact_replay_timestamp |
| Replication lag sales-invent-db | < 5 min | Zabbix |
| Replication lag strategic-db | < 5 min | Zabbix |
| DC2 disponibilidad | 99.9% | Zabbix LDAP check |
| RTO microservicios (H3 falla) | < 30 min | Runbook documentado |
| RTO API Gateway (H1 falla) | < 15 min | Runbook documentado |
| RPO bases de datos | < 5 min | Garantizado por streaming replication |

---

## 10. Relación con la rúbrica (master.pdf)

| Entregable | Criterio | Cómo lo cubre H4 |
|---|---|---|
| **E1 — CE0314** | Redundancia y Alta Disponibilidad | DC2 activo permanente + BDs réplica RPO < 5 min + standby frío microservicios |
| **E3 — CE0331** | Arquitectura Tier II | H4 como tier de backup — redundancia N+1 para servicios críticos |
| **E3 — CE0334** | Virtualización | VMs ESXi en standby, activación bajo demanda, imágenes en ECR |
| **E5 — CE0322** | Planes de Continuidad | RTO/RPO documentados, procedimiento de activación H4 paso a paso |
| **E6 — Criterio 4** | Políticas de Respaldo | Streaming Replication + Snapshots diarios + OVF semanal → S3 |
| **E6 — Criterio 5** | Definición de SLA | RPO < 5 min, RTO < 30 min, disponibilidad DC2 99.9% |
| **E6 — Criterio 6** | Monitoreo de Infraestructura | Zabbix monitorea replication lag + alerta si lag > 5 min |

---

*Documento técnico de especificación — Franco's SAC ITI | UPeU 2026*  
*Generado el 31/05/2026*
