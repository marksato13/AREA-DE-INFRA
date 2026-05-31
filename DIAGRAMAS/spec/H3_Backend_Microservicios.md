# HIPERVISOR 3 — Backend: Microservicios + Bases de Datos | Sede Central (LOCAL 2)
**Proyecto:** Franco's SAC — Infraestructura Tecnológica  
**Área:** ITI — UPeU 2026  
**Estándares aplicados:** ISO 27001 · ISO/IEC 20000 · ITIL 4 · TIA-942  
**Fecha:** 31/05/2026

---

## 1. Descripción general

HIPERVISOR 3 aloja el **núcleo del ERP** de Franco's SAC.  
Contiene todos los microservicios de negocio y sus bases de datos PostgreSQL.  
Toda la comunicación entre microservicios ocurre a través de **NATS 2.x + JetStream** — ningún microservicio llama directamente a la BD de otro.

### Principio de diseño: Database per Service
Cada microservicio es dueño de su propia base de datos. Ningún ms accede directamente a la BD de otro. La comunicación entre servicios es exclusivamente vía mensajes NATS.

```
auth-ms    → no tiene BD propia → consulta datos de persona via NATS → person-ms
person-ms  → person-db
sales-invent-ms → sales-invent-db
strategic-ms    → strategic-db
```

---

## 2. Inventario de VMs y servicios

| VM | IP | VLAN | Tecnología | Rol |
|---|---|---|---|---|
| VM-NATS-SERVER | 10.10.40.20 | VLAN 40 | NATS 2.x + JetStream | Message broker central |
| VM-AUTH-MS | 10.10.40.21 | VLAN 40 | NestJS + Docker | Autenticación JWT |
| VM-PERSON-MS | 10.10.40.22 | VLAN 40 | NestJS + Docker | Gestión de personas |
| VM-SALES-INVENT-MS | 10.10.40.23 | VLAN 40 | NestJS + Docker | Ventas e inventario |
| VM-STRATEGIC-MS | 10.10.40.24 | VLAN 40 | NestJS + Docker | BI y estrategia |
| person-db | 10.10.50.10 | VLAN 50 | PostgreSQL 15 | BD de person-ms |
| sales-invent-db | 10.10.50.11 | VLAN 50 | PostgreSQL 15 | BD de sales-invent-ms |
| strategic-db | 10.10.50.12 | VLAN 50 | PostgreSQL 15 | BD de strategic-ms |

> **VLAN 40** (Servicios): microservicios + NATS — TCP interno  
> **VLAN 50** (Datos): bases de datos PostgreSQL — aisladas de la capa de servicios

---

## 3. VM-NATS-SERVER — Message Broker

### 3.1 Descripción

NATS 2.x con JetStream habilitado es el **sistema nervioso** de la arquitectura de microservicios.  
Todo mensaje entre servicios pasa por aquí. Ningún ms llama directamente a otro ms via HTTP.

| Atributo | Valor |
|---|---|
| Software | NATS Server 2.x + JetStream |
| Puerto | TCP 4222 |
| IP | 10.10.40.20 |
| VLAN | VLAN 40 — Servicios |

### 3.2 Patrones de comunicación

#### Patrón Request-Reply (síncrono via NATS)
Usado cuando un ms necesita respuesta inmediata de otro:

```
auth-ms necesita validar usuario:
  auth-ms ──NATS request──→ "person.find.by.email"
  person-ms recibe mensaje, consulta person-db, responde
  auth-ms recibe respuesta con datos del usuario
  auth-ms genera JWT con los datos recibidos
```

#### Patrón Publish-Subscribe (asíncrono)
Usado para eventos de negocio:

```
sales-invent-ms registra venta:
  sales-invent-ms ──NATS publish──→ "sales.created"
  strategic-ms suscrito a "sales.*" → recibe el evento
  strategic-ms actualiza su BD de métricas BI
```

#### JetStream (persistencia de mensajes)
Para mensajes críticos que no pueden perderse si un ms está caído temporalmente:

```
JetStream stream: "BUSINESS_EVENTS"
Subjects: sales.*, inventory.*, person.*
Retención: 7 días
Réplicas: 1 (proyecto académico)
```

### 3.3 Topics principales

| Topic NATS | Publicador | Suscriptor | Propósito |
|---|---|---|---|
| `person.find.by.email` | auth-ms | person-ms | Buscar usuario para login |
| `person.find.by.id` | auth-ms, strategic-ms | person-ms | Obtener datos de persona |
| `person.created` | person-ms | strategic-ms | Evento nuevo registro |
| `sales.created` | sales-invent-ms | strategic-ms | Evento nueva venta |
| `sales.summary.request` | strategic-ms | sales-invent-ms | Solicitar resumen ventas |
| `inventory.updated` | sales-invent-ms | strategic-ms | Evento cambio inventario |
| `auth.token.validate` | API Gateway | auth-ms | Validar JWT entrante |

---

## 4. Microservicios — Descripción y flujos

### 4.1 auth-ms (VM 10.10.40.21)

**Rol:** Autenticación y autorización — emite y valida JWT  
**Sin base de datos propia** — obtiene datos de usuario via NATS desde person-ms

```
Flujo de login:
  POST /auth/login (desde API Gateway)
        │
        ▼
  auth-ms recibe {email, password}
        │
        ├──NATS request "person.find.by.email"──→ person-ms
        │                                          │
        │◄──NATS reply {userData, passwordHash}────┘
        │
        ├── valida bcrypt(password, hash)
        │
        └── genera JWT firmado (RS256)
            payload: {userId, roles, email, exp}
            responde al API Gateway con el token
```

```
Flujo de validación de token (cada request):
  API Gateway ──NATS "auth.token.validate"──→ auth-ms
  auth-ms verifica firma JWT + expiración
  auth-ms responde: {valid: true/false, userId, roles}
```

**Puertos:**
| Puerto | Protocolo | Función |
|---|---|---|
| TCP 3001 | HTTP interno | Health check endpoint |
| TCP 4222 | NATS | Comunicación con otros ms |

---

### 4.2 person-ms (VM 10.10.40.22)

**Rol:** Gestión de personas — empleados, clientes, proveedores  
**Base de datos:** person-db (10.10.50.10:5432)

```
Entidades en person-db:
  - persons (id, name, email, password_hash, role, status)
  - employees (id, person_id, area, hire_date)
  - clients (id, person_id, ruc, address)
  - suppliers (id, person_id, ruc, contact)
```

```
Flujo de creación de empleado:
  API Gateway → NATS "person.create"
  person-ms recibe datos
  person-ms INSERT → person-db
  person-ms publica NATS "person.created" (evento)
  strategic-ms suscrito recibe el evento para métricas
```

**Puertos:**
| Puerto | Protocolo | Función |
|---|---|---|
| TCP 3002 | HTTP interno | Health check |
| TCP 4222 | NATS | Broker |
| TCP 5432 | PostgreSQL | → person-db (10.10.50.10) |

---

### 4.3 sales-invent-ms (VM 10.10.40.23)

**Rol:** Ventas + Inventario — core del ERP para Franco's SAC  
**Base de datos:** sales-invent-db (10.10.50.11:5432)

```
Entidades en sales-invent-db:
  - products (id, name, category, unit, price)
  - inventory (id, product_id, quantity, warehouse, updated_at)
  - sales_orders (id, client_id, date, total, status)
  - sale_items (id, order_id, product_id, qty, unit_price)
  - purchase_orders (id, supplier_id, date, total)
```

```
Flujo de venta:
  API Gateway → NATS "sales.create"
  sales-invent-ms valida stock en inventario
  sales-invent-ms INSERT sale_order + UPDATE inventory
  sales-invent-ms publica "sales.created" + "inventory.updated"
  strategic-ms consume ambos eventos para BI
```

**Puertos:**
| Puerto | Protocolo | Función |
|---|---|---|
| TCP 3003 | HTTP interno | Health check |
| TCP 4222 | NATS | Broker |
| TCP 5432 | PostgreSQL | → sales-invent-db (10.10.50.11) |

---

### 4.4 strategic-ms (VM 10.10.40.24)

**Rol:** Business Intelligence y estrategia — KPIs, reportes, métricas  
**Base de datos:** strategic-db (10.10.50.12:5432)

```
Entidades en strategic-db:
  - kpi_sales (date, total_revenue, units_sold, top_product)
  - kpi_inventory (date, stock_value, low_stock_alerts)
  - kpi_clients (date, new_clients, active_clients)
  - reports (id, type, period, generated_at, data_json)
```

```
Flujo de actualización BI:
  NATS "sales.created" evento recibido
        │
        ▼
  strategic-ms procesa evento
  strategic-ms UPSERT kpi_sales en strategic-db
  strategic-ms genera alerta si KPI baja del umbral
  strategic-ms publica "kpi.updated" (para dashboard Grafana)
```

> **Decisión de diseño:** strategic-ms NO accede directamente a sales-invent-db.  
> Recibe datos via eventos NATS. Esto garantiza desacoplamiento — si sales-invent-ms cambia su BD, strategic-ms no se ve afectado.

**Puertos:**
| Puerto | Protocolo | Función |
|---|---|---|
| TCP 3004 | HTTP interno | Health check |
| TCP 4222 | NATS | Broker |
| TCP 5432 | PostgreSQL | → strategic-db (10.10.50.12) |

---

## 5. Bases de datos PostgreSQL — VLAN 50

### 5.1 Tabla de BDs

| BD | IP:Puerto | Owner ms | Schemas |
|---|---|---|---|
| person-db | 10.10.50.10:5432 | person-ms | persons, employees, clients, suppliers |
| sales-invent-db | 10.10.50.11:5432 | sales-invent-ms | products, inventory, sales_orders, sale_items |
| strategic-db | 10.10.50.12:5432 | strategic-ms | kpi_sales, kpi_inventory, reports |

### 5.2 Acceso mínimo privilegio

Cada ms tiene su propio usuario de BD con permisos mínimos:

```sql
-- Ejemplo para person-ms
CREATE USER person_ms_user WITH PASSWORD '...';
GRANT CONNECT ON DATABASE person_db TO person_ms_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES 
  IN SCHEMA public TO person_ms_user;
-- NO se otorga DROP, ALTER, CREATE
```

Ningún ms tiene acceso a la BD de otro:
```
person-ms-user → SOLO person-db    (acceso DENEGADO a sales-invent-db, strategic-db)
sales-ms-user  → SOLO sales-invent-db
strategic-user → SOLO strategic-db
```

### 5.3 Separación de red

```
VLAN 40 (Servicios 10.10.40.0/24):  microservicios + NATS
VLAN 50 (Datos    10.10.50.0/28):   solo PostgreSQL

Regla firewall pfSense-INTERNO:
  ALLOW  VLAN40 → VLAN50  TCP 5432   (ms acceden a sus BDs)
  DENY   VLAN20 → VLAN50             (usuarios NO acceden a BDs)
  DENY   VLAN30 → VLAN50             (DMZ NO accede a BDs)
```

---

## 6. Estrategia de Redundancia — 2 Niveles

### Nivel 1 — Dentro de H3: Docker Restart Policy

Cada VM corre su contenedor con política de reinicio automático.  
Si el proceso del microservicio crashea, Docker lo levanta en segundos.

```yaml
# docker-compose.yml — aplicado en cada VM de ms
version: '3.8'
services:
  auth-ms:
    image: <ECR_URI>/auth-ms:latest
    restart: always
    environment:
      NATS_URL: nats://10.10.40.20:4222
      JWT_SECRET: ${JWT_SECRET}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "5"
```

**Comportamiento con `restart: always`:**

| Evento | Tiempo de recuperación |
|---|---|
| Proceso del ms crashea | < 5 segundos (Docker reinicia automático) |
| Container sale con error | < 5 segundos |
| VM reiniciada | Container arranca automáticamente al levantar Docker |

**Health checks:** Zabbix monitorea el endpoint `/health` de cada ms.  
Si el health check falla 3 veces → alerta a VM-MONITOR.

---

### Nivel 2 — Cross-Hypervisor: H4 Cold Standby

HIPERVISOR 4 tiene réplicas en standby frío de los microservicios críticos.  
Si H3 falla completamente (fallo de hardware del hipervisor), se activan las VMs en H4.

```
ESTADO NORMAL:
  H3: auth-ms ✅  person-ms ✅  sales-ms ✅  strategic-ms ✅
  H4: auth-ms ⏸  person-ms ⏸  sales-ms ⏸  (apagadas / standby frío)

H3 FALLA:
  H3: ❌ (hipervisor inaccesible)
  │
  ▼
  Zabbix detecta caída (VM-MONITOR alerta al equipo TI)
  │
  ▼
  Equipo TI levanta VMs en H4 (procedimiento documentado)
  │
  ▼
  H4: auth-ms ✅  person-ms ✅  sales-ms ✅  (activas)
  H4: BDs réplica ✅ (ya sincronizadas via streaming replication)
  │
  ▼
  Servicios restaurados — usuarios acceden al ERP nuevamente
```

**RTO estimado con H4 standby frío:** 15-30 minutos (proceso manual documentado)  
**RPO de bases de datos:** < 5 minutos (PostgreSQL Streaming Replication H3 → H4)

#### Replicación de BDs H3 → H4

```
H3 (primario):                    H4 (standby):
  person-db (10.10.50.10)   ══════►  person-db réplica (10.10.50.20)
  sales-invent-db (10.10.50.11) ══► sales-invent-db réplica (10.10.50.21)
  strategic-db (10.10.50.12) ══════► strategic-db réplica (10.10.50.22)

Mecanismo: PostgreSQL Streaming Replication (WAL shipping)
Lag máximo tolerado: 5 minutos (RPO)
Monitoreo: Zabbix alerta si replication_lag > 5 min
```

---

### Nivel 3 — NATS Queue Groups (escalabilidad futura)

NATS 2.x soporta **Queue Groups**: múltiples instancias del mismo ms compiten por mensajes.  
Si en el futuro se levantan 2 instancias de un ms, NATS hace load balancing automático.

```
NATS topic: "sales.create"
Queue group: "sales-workers"

    ├──→ sales-invent-ms instancia 1 (H3, 10.10.40.23) ← procesa
    └──→ sales-invent-ms instancia 2 (H4, 10.10.40.31) ← en espera

Solo una instancia procesa cada mensaje (no duplicación).
Si instancia 1 cae, instancia 2 toma los mensajes automáticamente.
```

> Para el proyecto académico actual esto se documenta como **escalabilidad horizontal futura**.  
> La infraestructura de NATS ya soporta este patrón sin cambios.

---

## 7. Backup y pipeline de imágenes

### 7.1 pg_dump diario → S3

Script ejecutado a las 22:00 todos los días desde VM-NATS-SERVER (o cron en cada VM de BD):

```bash
#!/bin/bash
# backup_dbs.sh — ejecuta en cada VM de BD o centralmente
DATE=$(date +%Y%m%d)
BUCKET="s3://francos-db-backups"

pg_dump -U postgres person_db     | gzip | aws s3 cp - $BUCKET/person-db/backup_$DATE.sql.gz
pg_dump -U postgres sales_invent_db | gzip | aws s3 cp - $BUCKET/sales-invent-db/backup_$DATE.sql.gz
pg_dump -U postgres strategic_db  | gzip | aws s3 cp - $BUCKET/strategic-db/backup_$DATE.sql.gz

echo "Backup completado: $DATE" | logger -t pg_backup
```

**Estructura en S3:**
```
francos-db-backups/
  ├── person-db/
  │   ├── backup_20260601.sql.gz
  │   └── backup_20260602.sql.gz
  ├── sales-invent-db/
  │   └── backup_20260601.sql.gz
  └── strategic-db/
      └── backup_20260601.sql.gz
```

**Retención:** 30 días (S3 Lifecycle policy)  
**Transferencia:** via AWS VPN Gateway → pfSense-BORDE (túnel privado, no por internet público)

### 7.2 docker push → ECR (pipeline de imágenes)

Las imágenes Docker de todos los microservicios se almacenan en **AWS ECR** para:
- Respaldo de versiones de cada ms
- Fuente para restaurar VMs en H4 standby
- Historial de releases

```
Repositorios ECR:
  francos/gateway-ms     ← tags: latest, v1.0, v1.1...
  francos/auth-ms        ← tags: latest, v1.0...
  francos/person-ms      ← tags: latest, v1.0...
  francos/sales-invent-ms← tags: latest, v1.0...
  francos/strategic-ms   ← tags: latest, v1.0...

Push manual (o CI/CD futuro):
  docker build -t francos/auth-ms:v1.x .
  docker tag francos/auth-ms:v1.x <ECR_URI>/auth-ms:v1.x
  docker push <ECR_URI>/auth-ms:v1.x

Transferencia: via VPN Gateway → pfSense-BORDE (túnel privado)
```

---

## 8. Flujo completo de una petición al ERP

```
Usuario (navegador)
    │ HTTPS 443
    ▼
CloudFront (AWS) → Angular 20 SPA
    │ HTTPS api.francos.com
    ▼
VM-API-GATEWAY (10.10.30.10 — DMZ)
    │ valida JWT
    ├──NATS "auth.token.validate"──→ auth-ms ──→ responde {valid, userId, roles}
    │
    │ si válido, rutea a ms correspondiente
    ├──NATS "person.find.by.id"────→ person-ms ──→ person-db ──→ responde datos
    ├──NATS "sales.create"──────────→ sales-invent-ms ──→ sales-invent-db ──→ ok
    └──NATS "kpi.get"───────────────→ strategic-ms ──→ strategic-db ──→ métricas
```

---

## 9. Diagrama de capas H3

```
┌─ HIPERVISOR 3 ─────────────────────────────────────────────────────┐
│                                                                      │
│  ┌─── VLAN 40 — Servicios (10.10.40.0/24) ──────────────────────┐  │
│  │                                                                │  │
│  │           ┌─────────────────────────┐                         │  │
│  │           │    VM-NATS-SERVER       │                         │  │
│  │           │  NATS 2.x + JetStream   │                         │  │
│  │           │  10.10.40.20 :4222      │                         │  │
│  │           └────────────┬────────────┘                         │  │
│  │         TCP 4222       │ TCP 4222 (todos los ms)              │  │
│  │    ┌───────┬───────────┼────────────┬──────────┐              │  │
│  │    ▼       ▼           ▼            ▼          ▼              │  │
│  │ auth-ms person-ms sales-invent-ms strategic-ms                │  │
│  │ .40.21  .40.22    .40.23          .40.24                      │  │
│  │                                                                │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌─── VLAN 50 — Datos (10.10.50.0/28) ──────────────────────────┐  │
│  │                                                                │  │
│  │   person-db        sales-invent-db      strategic-db          │  │
│  │   10.10.50.10      10.10.50.11          10.10.50.12           │  │
│  │   PostgreSQL 15    PostgreSQL 15        PostgreSQL 15         │  │
│  │       │                │                    │                  │  │
│  │       │  ══════════════╪════════════════════╪══ Streaming ════►H4│
│  │       └────────────────┴────────────────────┘  Replication    │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  pg_dump 22:00 ──────────────────────────────────────────► S3 AWS   │
│  docker push ────────────────────────────────────────────► ECR AWS  │
└──────────────────────────────────────────────────────────────────────┘
                              │
                   Streaming Replication
                              ▼
┌─ HIPERVISOR 4 — BACKUP CRÍTICO ────────────────────────────────────┐
│  person-db réplica (10.10.50.20)                                    │
│  sales-invent-db réplica (10.10.50.21)   RPO < 5 min               │
│  strategic-db réplica (10.10.50.22)                                 │
│  + VMs standby frío: auth-ms, person-ms, sales-ms, strategic-ms    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 10. Relación con la rúbrica (master.pdf)

| Entregable | Criterio | Cómo lo cubre H3 |
|---|---|---|
| **E1 — CE0313** | Segmentación de Red | VLAN 40 ms separada de VLAN 50 BDs — reglas firewall documentadas |
| **E1 — CE0314** | Redundancia y Alta Disponibilidad | Docker restart (Nivel 1) + H4 standby (Nivel 2) + Streaming Replication RPO < 5 min |
| **E3 — CE0331** | Arquitectura Tier | H3 separado de H4 — no SPOF en BD |
| **E3 — CE0334** | Virtualización | VMs ESXi + contenedores Docker — arquitectura híbrida documentada |
| **E5 — CE0322** | Controles IAM | Usuarios PostgreSQL por ms con permisos mínimos — ningún ms accede a BD ajena |
| **E6 — Criterio 2** | Servicios Web + BD | API via NATS + 3 PostgreSQL + health checks |
| **E6 — Criterio 4** | Políticas de Respaldo | pg_dump diario → S3 con retención 30 días + Streaming Replication |
| **E6 — Criterio 5** | Definición de SLA | RPO < 5 min (replicación) + RTO < 30 min (H4 standby) |

---

*Documento técnico de especificación — Franco's SAC ITI | UPeU 2026*  
*Generado el 31/05/2026*
