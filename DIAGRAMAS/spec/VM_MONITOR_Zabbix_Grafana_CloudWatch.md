# VM-MONITOR — Zabbix + Grafana + CloudWatch Agent | Sede Central (LOCAL 2)
**Proyecto:** Franco's SAC — Infraestructura Tecnológica
**Área:** ITI — UPeU 2026
**Estándares:** ISO 27001 · ISO/IEC 20000 · ITIL 4 · NIST CSF
**Fecha:** 31/05/2026

---

## 1. Descripción general

VM-MONITOR es el **cerebro de observabilidad** de toda la infraestructura de Franco's SAC.
Centraliza el monitoreo de los 3 locales (L1, L2, L3) y la nube AWS en una sola VM
mediante tres herramientas desplegadas como contenedores Docker:

| Contenedor | Función | Puerto |
|---|---|---|
| **zabbix-server** | Recolección de métricas on-premises (agentes + SNMP + HTTP) | TCP 10051 |
| **grafana** | Visualización unificada (datasource Zabbix + CloudWatch) | TCP 3000 |
| **cloudwatch-agent** | Puente on-prem ↔ AWS CloudWatch | HTTPS 443 |

### Ubicación en la infraestructura
| Atributo | Valor |
|---|---|
| Hipervisor | H2 — Servicios Centrales (Sede Central) |
| IP | 10.10.60.10 |
| VLAN | VLAN 60 — Gestión |
| Acceso | Solo desde VLAN 10 (Admin) y VLAN 60 (Gestión) |

---

## 2. Arquitectura de monitoreo híbrido

La arquitectura divide el monitoreo en dos planos complementarios:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLANO ON-PREMISES                             │
│                    ZABBIX SERVER                                 │
│                                                                  │
│  Via Agente Zabbix:    Via SNMP:         Via HTTP Check:        │
│  ├── H1 (WAF, API GW) ├── pfSense-BORDE  ├── API /health       │
│  ├── H2 (AD, NTP, FS) ├── pfSense-L1     ├── Microservicios    │
│  ├── H3 (ms + BDs)    ├── pfSense-L3     └── Endpoints NATS    │
│  ├── H4 (backup)      ├── Cisco Switch                         │
│  ├── H5 L1 (fileserv) └── AP WiFi                              │
│  └── H6 L3 (fileserv)                                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │ cloudwatch-agent
                               │ reenvía KPIs seleccionados
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PLANO AWS CLOUD                               │
│                    CLOUDWATCH                                    │
│                                                                  │
│  Nativo AWS:                  On-prem (via cloudwatch-agent):   │
│  ├── CloudFront métricas      ├── API Gateway latencia + errors  │
│  ├── Route 53 health checks   ├── VPN tunnel status (pfSense)   │
│  ├── S3 operaciones backup    ├── BDs principales up/down        │
│  └── AWS VPN Gateway status   └── WAN1/WAN2 status              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GRAFANA                                       │
│  Datasource 1: Zabbix     → Dashboard Operativo (equipo TI)    │
│  Datasource 2: CloudWatch → Dashboard Ejecutivo (gerencia)     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Despliegue — Docker Compose

Toda la plataforma corre como contenedores en VM-MONITOR.
No se instala nada directamente en el sistema operativo.

### 3.1 docker-compose.yml

```yaml
version: '3.8'

services:

  # ── BASE DE DATOS DE ZABBIX ─────────────────────────────────────
  zabbix-db:
    image: postgres:15
    restart: always
    container_name: zabbix-db
    environment:
      POSTGRES_DB: zabbix
      POSTGRES_USER: zabbix
      POSTGRES_PASSWORD: ${ZBXDB_PASS}
    volumes:
      - zabbix_db_data:/var/lib/postgresql/data
    networks:
      - monitor-net

  # ── ZABBIX SERVER ───────────────────────────────────────────────
  zabbix-server:
    image: zabbix/zabbix-server-pgsql:latest
    restart: always
    container_name: zabbix-server
    environment:
      DB_SERVER_HOST: zabbix-db
      POSTGRES_USER: zabbix
      POSTGRES_PASSWORD: ${ZBXDB_PASS}
    ports:
      - "10051:10051"    # agentes activos conectan aquí
    depends_on:
      - zabbix-db
    networks:
      - monitor-net

  # ── ZABBIX WEB UI ───────────────────────────────────────────────
  zabbix-web:
    image: zabbix/zabbix-web-nginx-pgsql:latest
    restart: always
    container_name: zabbix-web
    ports:
      - "8080:8080"
    environment:
      DB_SERVER_HOST: zabbix-db
      POSTGRES_USER: zabbix
      POSTGRES_PASSWORD: ${ZBXDB_PASS}
      ZBX_SERVER_HOST: zabbix-server
      PHP_TZ: America/Lima
    depends_on:
      - zabbix-server
    networks:
      - monitor-net

  # ── GRAFANA ─────────────────────────────────────────────────────
  grafana:
    image: grafana/grafana:latest
    restart: always
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASS}
      GF_INSTALL_PLUGINS: alexanderzobnin-zabbix-app
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    networks:
      - monitor-net

  # ── CLOUDWATCH AGENT ────────────────────────────────────────────
  cloudwatch-agent:
    image: amazon/cloudwatch-agent:latest
    restart: always
    container_name: cloudwatch-agent
    volumes:
      - ./cloudwatch-config.json:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
      - ~/.aws:/root/.aws:ro
    environment:
      AWS_REGION: us-east-1
    networks:
      - monitor-net

volumes:
  zabbix_db_data:
  grafana_data:

networks:
  monitor-net:
    driver: bridge
```

### 3.2 Variables de entorno (.env)

```bash
# /opt/monitor/.env
ZBXDB_PASS=ZabbixDB$ecure2026
GRAFANA_PASS=Grafana$ecure2026
AWS_REGION=us-east-1
```

---

## 4. ZABBIX — Qué monitorea y cómo

### 4.1 Hosts monitoreados por Agente Zabbix

El agente Zabbix se instala en cada VM y envía métricas al servidor en modo **activo**
(agente inicia conexión TCP 10051 → Zabbix Server). Funciona a través de VPN.

#### SEDE CENTRAL (LOCAL 2)

| Host | IP | Métricas clave |
|---|---|---|
| VM-WAF | 10.10.30.5 | CPU, RAM, requests bloqueados ModSecurity, estado NGINX |
| VM-API-GATEWAY | 10.10.30.10 | CPU, RAM, requests/seg, latencia p50/p99, errores HTTP 5xx |
| VM-AD-DC (DC1) | 10.10.10.20 | CPU, RAM, proceso Samba activo, replicación AD, DNS respondiendo |
| VM-AD-DC-2 (DC2) | 10.10.10.21 | Estado réplica, lag replicación AD, DNS secundario |
| VM-NTP | 10.10.10.12 | Estado Chrony, offset con upstream (alerta si > 1 seg) |
| VM-FILESERVER | 10.10.40.10 | CPU, RAM, disco, conexiones SMB/NFS activas |
| VM-NATS-SERVER | 10.10.40.20 | CPU, RAM, mensajes/seg, colas JetStream, conexiones |
| auth-ms | 10.10.40.21 | CPU, RAM, Docker container status, health endpoint |
| person-ms | 10.10.40.22 | CPU, RAM, Docker container status, health endpoint |
| sales-invent-ms | 10.10.40.23 | CPU, RAM, Docker container status, health endpoint |
| strategic-ms | 10.10.40.24 | CPU, RAM, Docker container status, health endpoint |
| person-db | 10.10.50.10 | Conexiones, queries/seg, tamaño BD, **replication lag vs H4** |
| sales-invent-db | 10.10.50.11 | Ídem |
| strategic-db | 10.10.50.12 | Ídem |
| person-db réplica | 10.10.50.20 | Lag streaming replication (ALERTA si > 300 seg) |
| sales-invent-db réplica | 10.10.50.21 | Ídem |
| strategic-db réplica | 10.10.50.22 | Ídem |
| VM-BACKUP-API-GW | 10.10.30.20 | Ping disponibilidad (standby frío — solo verificar que VM enciende) |
| VM-AD-DC-2 (H4) | 10.10.10.21 | Estado RODC, replicación desde DC1 |

#### LOCAL 1

| Host | IP | Agente instalado en | Métricas |
|---|---|---|---|
| VM-FILESERVER-L1 | 10.20.40.10 | VM-FILESERVER-L1 | CPU, RAM, disco, Samba, estado Docker |
| pfSense-L1 | — | SNMP (ver §4.2) | Estado WAN, VPN, CPU |
| VM-AD-DC-L1 (RODC) | 10.20.10.20 | VM-AD-DC-L1 | CPU, RAM, Samba RODC activo |

#### LOCAL 3

| Host | IP | Agente instalado en | Métricas |
|---|---|---|---|
| VM-FILESERVER-L3 | 10.30.40.10 | VM-FILESERVER-L3 | CPU, RAM, disco, Samba |
| pfSense-L3 | — | SNMP | Estado WAN, VPN, CPU |
| VM-AD-DC-L3 (RODC) | 10.30.10.20 | VM-AD-DC-L3 | CPU, RAM, Samba RODC activo |

### 4.2 Hosts monitoreados por SNMP (sin agente)

| Dispositivo | IP MGMT | Community | Métricas |
|---|---|---|---|
| pfSense-BORDE | 10.10.99.1 | francos_snmp | WAN1/WAN2 status, **túneles VPN L1-L2/L2-L3/L2-AWS**, CPU, conexiones NAT |
| Cisco Catalyst 1000 | 10.10.99.2 | francos_snmp | Puertos up/down, tráfico por puerto, errores frame, CPU |
| AP WiFi | 10.10.20.50 | francos_snmp | Clientes conectados, RSSI, tráfico VLAN 20 |
| pfSense-L1 | 10.20.99.1 | francos_snmp | WAN status, túnel L1-L2, CPU |
| pfSense-L3 | 10.30.99.1 | francos_snmp | WAN status, túnel L2-L3, CPU |

### 4.3 Checks HTTP (sin agente, sin SNMP)

```
Zabbix HTTP Agent checks cada 30 segundos:

GET http://10.10.30.10/health   → espera HTTP 200  (VM-API-GATEWAY)
GET http://10.10.40.21/health   → espera HTTP 200  (auth-ms)
GET http://10.10.40.22/health   → espera HTTP 200  (person-ms)
GET http://10.10.40.23/health   → espera HTTP 200  (sales-invent-ms)
GET http://10.10.40.24/health   → espera HTTP 200  (strategic-ms)
TCP  10.10.40.20:4222           → espera conexión  (NATS server)
```

### 4.4 Configuración del agente (modo activo via VPN)

```ini
# /etc/zabbix/zabbix_agentd.conf
# Aplica a: VM-FILESERVER-L1, VM-FILESERVER-L3, VM-AD-DC-L1, VM-AD-DC-L3

ServerActive=10.10.60.10        # Zabbix Server Sede Central
Hostname=VM-FILESERVER-L1       # nombre único por host
RefreshActiveChecks=120         # re-registra checks cada 2 min
BufferSend=5                    # envía buffer si acumula 5 seg
Timeout=10
```

Regla firewall pfSense por sede:
```
# pfSense-L1 / pfSense-L3:
ALLOW VLAN-local → 10.10.60.10 TCP 10051   (agente activo → Zabbix server)
```

### 4.5 Alertas configuradas

| Alerta | Umbral | Severidad | Acción |
|---|---|---|---|
| VM caída (ping timeout) | 3 intentos fallidos | DISASTER | Email + notificación inmediata |
| Túnel VPN caído | Estado down SNMP | HIGH | Email equipo TI |
| CPU alto | > 85% por 5 min | WARNING | Log en dashboard |
| RAM alto | > 90% | HIGH | Email equipo TI |
| Disco lleno | > 80% usado | WARNING | Email preventivo |
| Replication lag BD | > 300 seg (5 min) | HIGH | Email — viola RPO |
| AD-DC sin respuesta LDAP | Timeout 3 intentos | DISASTER | Email — sin autenticación |
| NTP offset alto | > 2 segundos | WARNING | Riesgo Kerberos |
| Microservicio health fail | HTTP != 200 | HIGH | Email equipo TI |
| Docker container caído | Proceso ausente | HIGH | Email — reinicio automático vía Docker |

---

## 5. CLOUDWATCH AGENT — Qué monitorea y cómo

### 5.1 Principio de división

```
Zabbix  → monitoreo OPERATIVO completo on-prem (todo el detalle técnico)
CloudWatch → KPIs de NEGOCIO + correlación con servicios AWS
```

CloudWatch no duplica lo que hace Zabbix. Solo recibe métricas on-prem
que necesitan **correlacionarse con el lado AWS** o ser visibles desde la consola AWS.

### 5.2 Métricas AWS nativas (CloudWatch las recolecta solo)

| Servicio AWS | Métricas | Utilidad |
|---|---|---|
| **CloudFront** | Requests, ErrorRate 4xx/5xx, OriginLatency, CacheHitRate | Detectar si la lentitud está en CDN o en la API on-prem |
| **Route 53** | HealthCheckStatus (¿API on-prem responde?), DNSQueries | Alertar si el health check falla — Route 53 deja de enrutar |
| **S3 Buckets** | PutObject count (¿llegó el backup?), BucketSizeBytes | Verificar que pg_dump diario llegó al bucket |
| **AWS VPN Gateway** | TunnelState (Up/Down lado AWS), TunnelDataIn/Out | Correlacionar con estado pfSense lado on-prem |

### 5.3 Métricas on-prem enviadas a CloudWatch (via cloudwatch-agent)

Solo 4 métricas críticas — las que tienen correlación directa con AWS:

| Métrica on-prem | Fuente | Namespace CloudWatch | Por qué a CloudWatch |
|---|---|---|---|
| API Gateway latencia (p50, p99) | VM-API-GATEWAY | FrancosSAC/OnPrem | CloudFront llama a esta API — correlación directa |
| API Gateway error rate HTTP 5xx | VM-API-GATEWAY | FrancosSAC/OnPrem | Si CloudFront muestra errores, ¿viene de acá? |
| VPN Tunnel L2-AWS status | pfSense-BORDE SNMP | FrancosSAC/OnPrem | CloudWatch ve lado AWS, Zabbix ve lado on-prem — juntos = visibilidad completa |
| BDs principales up/down | person-db, sales-invent-db | FrancosSAC/OnPrem | S3 recibe sus backups — si BD cae, backup de mañana falla |

### 5.4 cloudwatch-config.json

```json
{
  "agent": {
    "metrics_collection_interval": 60,
    "region": "us-east-1",
    "logfile": "/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log"
  },
  "metrics": {
    "namespace": "FrancosSAC/OnPrem",
    "metrics_collected": {
      "statsd": {
        "service_address": ":8125",
        "metrics_collection_interval": 60,
        "metrics_aggregation_interval": 60
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_name": "FrancosSAC-APIGateway-Access",
            "log_stream_name": "api-gateway-{instance_id}"
          }
        ]
      }
    }
  }
}
```

Script de reenvío de métricas (cron cada 1 minuto):

```bash
#!/bin/bash
# /opt/monitor/scripts/send_metrics_to_cloudwatch.sh

# Obtener latencia API Gateway desde Zabbix API
API_LATENCY=$(curl -s http://10.10.30.10/metrics | grep response_time_p99 | awk '{print $2}')
API_ERRORS=$(curl -s http://10.10.30.10/metrics | grep http_errors_5xx | awk '{print $2}')

# Obtener estado BDs (1=up, 0=down)
DB_PERSON=$(pg_isready -h 10.10.50.10 -p 5432 > /dev/null 2>&1 && echo 1 || echo 0)
DB_SALES=$(pg_isready -h 10.10.50.11 -p 5432 > /dev/null 2>&1 && echo 1 || echo 0)

# Enviar a CloudWatch
aws cloudwatch put-metric-data --namespace "FrancosSAC/OnPrem" \
  --metric-data \
    MetricName=APIGatewayLatencyP99,Value=$API_LATENCY,Unit=Milliseconds \
    MetricName=APIGateway5xxErrors,Value=$API_ERRORS,Unit=Count \
    MetricName=PersonDBStatus,Value=$DB_PERSON,Unit=None \
    MetricName=SalesDBStatus,Value=$DB_SALES,Unit=None
```

---

## 6. GRAFANA — Dashboards

### 6.1 Datasources configurados

```yaml
# grafana/provisioning/datasources/datasources.yaml
apiVersion: 1
datasources:

  - name: Zabbix
    type: alexanderzobnin-zabbix-datasource
    url: http://zabbix-web:8080
    jsonData:
      username: grafana_reader
      trends: true
      trendsFrom: "7d"

  - name: CloudWatch
    type: cloudwatch
    jsonData:
      authType: keys
      defaultRegion: us-east-1
    secureJsonData:
      accessKey: ${AWS_ACCESS_KEY}
      secretKey: ${AWS_SECRET_KEY}
```

### 6.2 Dashboard Operativo (equipo TI)

**Audiencia:** Administrador de red, equipo TI  
**Datasource:** Zabbix  
**Frecuencia de refresco:** 30 segundos

| Panel | Métrica | Tipo |
|---|---|---|
| Estado general infraestructura | Todos los hosts up/down | Semáforo |
| CPU/RAM por hipervisor | H1/H2/H3/H4/H5/H6 | Time series |
| Estado túneles VPN | L1-L2, L2-L3, L2-AWS | Gauge verde/rojo |
| Replication lag BDs | person-db, sales-db, strategic-db | Time series + alerta |
| Microservicios health | auth/person/sales/strategic | Semáforo |
| NATS mensajes/seg | VM-NATS-SERVER | Time series |
| Tráfico Cisco Switch | Bytes in/out por puerto | Bar chart |
| Espacio en disco | Todos los filesservers | Gauge |
| Eventos de seguridad | pfSense firewall blocks | Table |

### 6.3 Dashboard Ejecutivo (gerencia / coordinador)

**Audiencia:** Gerente de Franco's SAC, Coordinador ITI UPeU  
**Datasource:** CloudWatch + Zabbix (KPIs seleccionados)  
**Frecuencia de refresco:** 5 minutos

| Panel | Métrica | Fuente |
|---|---|---|
| ERP disponible | API Gateway up/down | Zabbix HTTP check |
| Latencia ERP | API Gateway p99 vs CloudFront latency | Zabbix + CloudWatch |
| Usuarios activos | NATS conexiones activas | Zabbix |
| Backups OK hoy | S3 PutObject count del día | CloudWatch |
| VPN estado global | L1-L2, L2-L3, L2-AWS | Zabbix SNMP |
| CDN cache hit rate | CloudFront CacheHitRate | CloudWatch |
| Uptime del mes (%) | Disponibilidad API Gateway | Zabbix histórico |
| Sedes conectadas | L1 y L3 VPN status | Zabbix |

---

## 7. Correlación entre Zabbix y CloudWatch

El caso de uso más valioso: **detectar dónde está la lentitud del ERP**.

```
Escenario: usuario reporta "ERP lento"

Paso 1 — Dashboard ejecutivo:
  CloudFront OriginLatency: 800ms  ← alto
  API Gateway on-prem p99: 180ms   ← normal

Conclusión: el problema está entre CloudFront y la API (red AWS o CDN)
→ No es culpa de la infraestructura on-prem
→ Revisar configuración CloudFront o ruta de red AWS

─────────────────────────────────────────────────────

Escenario 2: "ERP no responde"

Paso 1 — Dashboard ejecutivo:
  Route 53 HealthCheck: FAIL ← API Gateway no responde
  API Gateway on-prem: DOWN  ← Zabbix confirma

Conclusión: problema en API Gateway on-prem
→ Revisar VM-API-GATEWAY (H1)
→ Activar VM-BACKUP-API-GW (H4) si necesario
```

---

## 8. CloudWatch Alarms — Notificaciones automáticas

```
Alarm 1: API Gateway caído
  Métrica: FrancosSAC/OnPrem/APIGatewayLatencyP99
  Condición: NoData por 2 minutos
  Acción: SNS → Email equipo TI + gerente

Alarm 2: Error rate alto
  Métrica: FrancosSAC/OnPrem/APIGateway5xxErrors
  Condición: > 10 errores en 5 minutos
  Acción: SNS → Email equipo TI

Alarm 3: Backup S3 no llegó
  Métrica: AWS/S3 PutObject count (bucket francos-db-backups)
  Condición: Count = 0 entre 22:00 y 23:00
  Acción: SNS → Email equipo TI

Alarm 4: VPN AWS caído
  Métrica: AWS/VPN TunnelState
  Condición: State = 0 (down) por 5 minutos
  Acción: SNS → Email equipo TI
```

---

## 9. Flujo completo de datos de monitoreo

```
INFRAESTRUCTURA                VM-MONITOR                    DESTINOS
─────────────────              ──────────────                ─────────────

Agentes VMs L1/L2/L3 ──TCP 10051──► zabbix-server ──────► zabbix-db (PostgreSQL)
                                          │                       │
SNMP (pfSense, Switch, AP) ──polling──────┘              grafana-datasource-1
                                                                  │
HTTP checks (health APIs) ──────────────────────────────► grafana-datasource-1
                                                                  │
                                                          ┌───────▼────────┐
cloudwatch-agent ──────HTTPS 443──► AWS CloudWatch        │    GRAFANA     │
  (KPIs on-prem)                         │                │  Dashboard     │
                                         │                │  Operativo     │
AWS services ──────────────────────►     │                │  Ejecutivo     │
  CloudFront, S3, Route53,               │                └───────┬────────┘
  VPN Gateway                            │                        │
                                  grafana-datasource-2            │
                                         │                        │
                                         └──────────────────────► │
                                                           Dashboard unificado
```

---

## 10. SLA del sistema de monitoreo

| Métrica | Valor objetivo |
|---|---|
| Disponibilidad VM-MONITOR | 99.5% (mantenimiento nocturno permitido) |
| Frecuencia de polling Zabbix | 30 seg (checks críticos), 5 min (métricas generales) |
| Retención de métricas Zabbix | 90 días en base de datos |
| Retención de métricas CloudWatch | 15 meses (tier estándar AWS) |
| Tiempo máximo de alerta (detección → notificación) | < 2 minutos |
| Dashboards disponibles sin Zabbix | No (Zabbix es el datasource principal) |

---

## 11. Relación con la rúbrica (master.pdf)

| Entregable | Criterio | Cómo lo cubre VM-MONITOR |
|---|---|---|
| **E1 — CE0315** | Cumplimiento estándares | Monitoreo SNMP IEEE 802.x + ITIL 4 gestión de eventos |
| **E3 — CE0334** | Virtualización y Cloud Híbrido | cloudwatch-agent como puente on-prem ↔ AWS |
| **E5 — CE0323** | KPIs de Seguridad | Alertas Zabbix: accesos fallidos AD, firewall blocks, lag replicación |
| **E5 — CE0323** | Registro y Auditoría | Logs centralizados en Zabbix + CloudWatch Logs |
| **E6 — Criterio 5** | Definición de SLA | Dashboard SLA: uptime mensual API Gateway vs meta 99.5% |
| **E6 — Criterio 6** | Monitoreo de Infraestructura | Cobertura completa: 3 sedes + AWS en un solo panel |
| **E6 — Criterio 7** | Procedimientos Operativos | Runbook: cómo interpretar alertas + acciones correctivas |

---

*Documento técnico de especificación — Franco's SAC ITI | UPeU 2026*
*Generado el 31/05/2026*
