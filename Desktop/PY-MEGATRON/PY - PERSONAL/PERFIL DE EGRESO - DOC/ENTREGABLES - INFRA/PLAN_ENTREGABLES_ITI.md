# Plan de Entregables — ITI | Franco's SAC | UPeU 2026
**Área:** Infraestructura Tecnológica (ITI)  
**Empresa:** Franco's SAC — Agroindustria alimentaria (snacks naturales)  
**Plataforma:** Hipervisores Cisco — Labs UPeU (ESXi + pfSense + Cisco Catalyst 1000)  
**Estándar de referencia:** master.pdf — Guía de Evaluación del Proyecto de Fin de Carrera

---

## GATE CRÍTICO
> El diseño de Semestre 1 (E1 + E2 + E3) **DEBE ser aprobado por el coordinador** antes de iniciar Semestre 2.  
> Sin esta aprobación el estudiante **no puede continuar**.

---

# SEMESTRE 1 — Conceive / Design
> Etapas CDIO: Conceive (E1) + Design (E2, E3)

---

## E1 — Diseño de Red (CE031)
**Rol:** Arquitecto de Redes / Diseñador de Infraestructura  
**Estándares:** TIA/EIA-568 · IEEE 802.x · ISO/IEC 11801  
**Carpeta de entregables:** `ENTREGABLES 2026 - FRANCOS/`

---

### CE0311 — Levantamiento de Requerimientos ✅
**Archivo:** `CE0311_Levantamiento_Requerimientos.html`

Actividades realizadas:
- Caracterización de la empresa Franco's SAC (sector, tamaño, locales, áreas)
- Diagnóstico de situación actual AS-IS (infraestructura sin servidores, WiFi básico, 2 PCs)
- Identificación del driver principal: implementación de ERP empresarial
- Definición de requerimientos técnicos y de negocio por área (Producción, Ventas, Admin, Inventario)
- Definición de requerimientos de red: segmentación, disponibilidad, rendimiento
- Documentación con evidencia justificada

---

### CE0312 — Topología Lógica y Física ✅
**Archivo:** `CE0312_Topologia_Logica_Fisica.html`  
**Diagramas:** 5 archivos `.drawio` en carpeta `DIAGRAMAS/`

Actividades realizadas:
- Diagrama de topología física Local 1 (planta de producción)
- Diagrama de topología física Local 2 (ventas/administración)
- Diagrama de topología lógica Local 1 y Local 2 (VLANs, subnetting)
- Diagrama de arquitectura de vSwitches del Hipervisor 1 (ESXi Host 1)
- Diagrama de arquitectura híbrida global (on-premises + AWS Cloud)
- Documentación y justificación técnica de cada decisión de diseño

**Topología definida:**
- Sede Central (Local 4): 4 hipervisores ESXi, Cisco Catalyst 1000, pfSense dual (Borde + Interno/WAF)
- Local 1: pfSense-L1, Hipervisor 5 (lab UPeU), VLANs 10/20/60/99
- Local 3: pfSense-L3, Hipervisor L3-A (backup microservicios), Hipervisor 6 (servicios básicos)
- AWS Cloud: Route 53, CloudFront + S3, AWS VPN Gateway, S3 Backups, ECR

---

### CE0313 — Segmentación de Red ✅
**Archivo:** `CE0313_Segmentacion_Red.html`

Actividades realizadas:
- Diseño de VLANs por local (Local 1, Sede Central/Local 4, Local 3)
- Definición de subnetting por VLAN con justificación de tamaño
- Diseño de DMZ (VLAN 30: 10.10.30.0/28) para API Gateway expuesto
- Inter-VLAN routing via pfSense-INTERNO
- Trunk 802.1Q desde pfSense-INTERNO → Cisco Catalyst 1000 → hipervisores
- Tabla de VLANs completa con IP, máscara, GW y propósito

**VLANs Sede Central:** 10 Admin / 20 Usuarios / 30 DMZ / 40 Servicios / 50 Datos / 60 Gestión / 99 MGMT  
**VLANs Local 1 y Local 3:** 10 / 20 / 60 / 99

---

### CE0314 — Redundancia y Alta Disponibilidad ✅
**Archivo:** `CE0314_Redundancia_Alta_Disponibilidad.html`

Actividades realizadas:
- Identificación de 8 SPOFs (Single Points of Failure) con nivel de riesgo y mitigación
- Diseño de failover Dual-WAN en pfSense (ISP1 activo + ISP2 standby via CARP/failover)
- pfSense-BORDE + pfSense-INTERNO (doble capa de firewall)
- Replicación de BD: PostgreSQL Streaming Replication H3 → H4 (RPO < 5 min)
- DHCP-DNS primario (10.10.10.10) + réplica (10.10.10.11)
- Hipervisor 4 como backup crítico de H3 (microservicios + BDs en standby frío)
- Túneles VPN IPSec IKEv2 mesh: L1↔L4, L3↔L4, AWS↔L4

---

### CE0315 — Cumplimiento de Estándares ✅
**Archivo:** `CE0315_Cumplimiento_Estandares.html`

Actividades realizadas:
- Mapeo explícito de cada componente de red a su estándar aplicable
- TIA/EIA-568: cableado estructurado, categorías de cable, patch panels
- IEEE 802.1Q: trunking VLANs en Cisco Catalyst 1000
- IEEE 802.11: puntos de acceso WiFi (SSID FrancosCorp, VLAN 20)
- IEEE 802.3: conectividad Ethernet entre dispositivos
- ISO/IEC 11801: cableado de edificio, subsistemas horizontal/vertical
- Tabla de cumplimiento por componente con evidencia de aplicación

---

### CE0316 — Calidad Documental y Ética ACM ✅ COMPLETO
**Archivo:** `CE0316_Calidad_Documental_Etica.html` · v1.0 · 31 Mayo 2026

Actividades realizadas:
- §3: Revisión de 10 puntos de coherencia entre CE0311-CE0315 (todos COHERENTES)
- §4: Evaluación de 7 criterios de calidad documental (todos EXCELENTE)
- §5: 8 principios ACM aplicados al proyecto con tarjetas visuales
- §6: Tabla de cumplimiento ético ACM ↔ Franco's SAC con evidencia técnica
- §7: Impacto social (empleados, datos personales, brecha digital) · Ley 29733 Perú · Código Penal Art. 207-A · trade-offs documentados
- §8: Declaración formal de cierre E1 con sellos (10/10 coherencia, 8/8 ACM, Ley 29733, E1 completo)
- §9: Rúbrica completa con nivel EXCELENTE en los 6 criterios + Estado Gate Semestre 1

**INDEX_E1.html** — Landing page de navegación del Entregable 1 completo ✅

---

## E2 — Planificación de Seguridad (CE032)
**Rol:** Analista de Seguridad / CISO Junior  
**Estándares:** ISO 27001 · ISO 27005 · NIST CSF  
**Estado:** ✅ COMPLETO — `E2_Planificacion_Seguridad.html` v1.1 · 01 Jun 2026

---

### CE0321 — Identificación de Activos Críticos ✅
**Contenido en:** `E2_Planificacion_Seguridad.html` §1

Realizado:
- 28 activos en 6 categorías ISO 27005 (hardware, software, datos, servicios, personas, instalaciones)
- Valoración CIA escala 1-5 con justificación por activo
- Top 10 activos críticos ranking documentado

---

### CE0322 — Análisis de Riesgos (ISO 27005 / NIST) ✅
**Contenido en:** `E2_Planificacion_Seguridad.html` §2

Realizado:
- 18 riesgos identificados (8 ALTO P×I:12-19, 10 MEDIO P×I:8-11)
- Heat Map 5×5 completo con escala de color
- Mapeo a NIST CSF v2.0 (Govern/Identify/Protect/Detect/Respond/Recover)
- Tratamiento: 16 mitigar + 2 aceptar

---

### CE0323 — Políticas de Seguridad ✅
**Contenido en:** `E2_Planificacion_Seguridad.html` §3

Realizado:
- 6 políticas formales: POL-01 IAM · POL-02 Contraseñas GPO · POL-03 Backup 5 niveles · POL-04 Parches CVSS · POL-05 Uso Aceptable · POL-06 Incidentes P1-P4
- Cada política con: objetivo, alcance, responsable, procedimiento, indicador, alineación ISO 27001 Anexo A

---

### CE0324 — Roles y Responsabilidades (RACI) ✅
**Contenido en:** `E2_Planificacion_Seguridad.html` §4

Realizado:
- 6 roles: Gerencia / CISO / Admin Red / Admin Sis / DBA / Usuario
- Organigrama ASCII + Matriz RACI 13 procesos
- Responsabilidades D/S/M/T por rol, mapeo ISO 27001 por rol

---

### CE0325 — Calidad Documental y Ética ACM ✅
**Contenido en:** `E2_Planificacion_Seguridad.html` §5

Realizado:
- 8 principios ACM aplicados, 8 puntos coherencia verificados
- Ley 29733 + D.S. 003-2013-JUS aplicados
- Referencias: 9 documentos normativos
- Declaración formal con sellos

---

## E3 — Diseño de Centro de Datos (CE033)
**Rol:** Arquitecto de Centro de Datos  
**Estándares:** Uptime Institute · TIA-942 · ASHRAE TC9.9  
**Estado:** ✅ COMPLETO — `E3_Diseno_Centro_Datos.html` v1.0 · 01 Jun 2026

---

### CE0331 — Arquitectura Tier I–IV ✅
**Contenido en:** `E3_Diseno_Centro_Datos.html` §1

Realizado:
- Comparativa Tier I-IV (disponibilidad, redundancia, costo, uptime)
- **Tier II seleccionado y justificado** — redundancia lógica: DC2 (H4), streaming replication (RPO<5min), Dual-WAN, H4 backup
- Tabla justificación con criterios Uptime Institute
- Gap físico documentado como TO-BE: UPS APC, generador, CRAC, supresión de incendios

---

### CE0332 — Diseño de Layout Físico ✅
**Contenido en:** `E3_Diseno_Centro_Datos.html` §2

Realizado:
- Figura 2.1: diagrama ASCII layout Sede Central — 4 racks (A-D: H1 Borde, H2 Servicios, H3 Backend, H4 Backup)
- Tabla distribución de equipos por rack con modelos, roles y conexiones detalladas
- Figura 2.3: layout simétrico LOCAL 1 y LOCAL 3 (H5, H6)
- Tabla ASHRAE TC9.9 completa (temperatura, humedad, pasillo frío/caliente, densidad de potencia)
- Cableado Cat6 UTP · IEEE 802.3ab · TIA/EIA-568 T568B

---

### CE0333 — Dimensionamiento de Capacidad ✅
**Contenido en:** `E3_Diseno_Centro_Datos.html` §3

Realizado:
- Tabla H1-H6 con vCPU / RAM / Storage usados y % utilización
- H3 RAM flaggeado como cuello de botella (150% → requiere ≥32 GB)
- Cálculo almacenamiento detallado por componente (8 items) con crecimiento anual
- Proyección 3 años 2026-2029 con acciones requeridas
- Stats globales: 57 vCPU, 160+ GB RAM, 2.5+ TB storage, 22+ VMs

---

### CE0334 — Virtualización y Cloud Híbrido ✅
**Contenido en:** `E3_Diseno_Centro_Datos.html` §4

Realizado:
- VMware ESXi 8.0 U3 — vSwitches, VMFS6, OVF, snapshots
- AWS servicios: Route 53, CloudFront+S3, VPN GW, S3 Backups, ECR — costos ~$45-50/mes
- Diagrama ASCII arquitectura híbrida completa Franco's SAC
- Tabla beneficios/riesgos/mitigaciones detallada

---

### CE0335 — Cumplimiento de Estándares DC ✅
**Contenido en:** `E3_Diseno_Centro_Datos.html` §5

Realizado:
- 7 normas aplicadas: Uptime Tier II · TIA-942 Cat 1 lab/Cat 2 TO-BE · ASHRAE Clase A1 · ISO 17203 OVF · VMware · AWS WA · IEEE 802.3ab
- Tabla gaps TO-BE: 4 gaps físicos documentados (UPS, dual power, CRAC, fire suppression)

---

### CE0336 — Calidad Documental y Ética ACM (DC) ✅
**Contenido en:** `E3_Diseno_Centro_Datos.html` §6

Realizado:
- 5 coherencias verificadas entre CE0331-CE0335
- 5 principios ACM aplicados al diseño DC (impacto en disponibilidad, responsabilidad social)
- Declaración formal con 4 sellos
- Referencias normativas: 9 documentos

---

# SEMESTRE 2 — Implement / Operate
> Condición: Gate de Semestre 1 aprobado por coordinador  
> Etapas CDIO: Implement (E4, E5) + Operate (E6) + Transversal (E7)

---

## E4 — Implementación y Testing de Red (CE031)
**Rol:** Ingeniero de Redes / Administrador de Infraestructura  
**Estándares:** TIA/EIA · IEEE 802.x · ISO/IEC 11801  
**Estado:** ❌ SEMESTRE 2

---

### Criterio 1 — Configuración de Dispositivos
Actividades:
- Configuración real de pfSense-BORDE: Dual-WAN (CARP/failover), NAT, IPSec IKEv2 hacia L1, L3 y AWS
- Configuración de pfSense-INTERNO: Inter-VLAN routing, Suricata IPS, reglas de firewall por VLAN
- Configuración de Cisco Catalyst 1000: VLANs trunk 802.1Q, ports de acceso por VLAN
- Configuración de pfSense-L1 y pfSense-L3: Dual-WAN, IPSec hacia Sede Central
- Documentación de comandos usados y capturas de pantalla de verificación

### Criterio 2 — Direccionamiento IP
Actividades:
- Implementación del esquema IP definido en E1 (coherencia S1 → S2 verificable por jurado)
- Verificación de asignación DHCP por VLAN
- Tabla de direccionamiento final (real vs. diseñado)

### Criterio 3 — Routing Estático/Dinámico
Actividades:
- Configuración de rutas estáticas en pfSense para VLANs y subnets VPN
- Verificación de routing inter-VLAN (VLAN 20 → VLAN 30 DMZ → VLAN 40 Servicios)
- Pruebas de routing: ping, traceroute, tabla de rutas documentada

### Criterio 4 — Controles de Acceso (ACL)
Actividades:
- Reglas de firewall pfSense por VLAN (deny all, permit específico)
- ACL VLAN 20 (Usuarios) → solo puede acceder a VLAN 40 por puertos específicos
- ACL VLAN 10 (Admin) → acceso completo controlado
- ACL VLAN 30 (DMZ) → solo HTTPS 443 entrante desde internet
- Pruebas de bloqueo y permiso documentadas con capturas

### Criterio 5 — Cumplimiento de Estándares
Actividades:
- Evidencias físicas de cableado TIA/EIA-568 (fotos, etiquetado)
- Capturas de configuración IEEE 802.1Q trunk
- Documentación de cumplimiento implementado (vs. diseñado en E1)

### Criterio 6 — Pruebas de Conectividad y Rendimiento
Actividades:
- Pruebas de ping entre todas las VLANs (matriz de conectividad)
- Medición de latencia entre locales via VPN (ping L1 ↔ L4, L3 ↔ L4)
- Medición de throughput (iperf3 entre hipervisores)
- Prueba de failover Dual-WAN (desconectar ISP1, verificar switchover a ISP2)
- Documentación de resultados en tabla: origen → destino → latencia → resultado

### Criterio 7 — Monitoreo y Documentación
Actividades:
- Configuración de Zabbix 6.x + Grafana en VM-MONITOR (10.10.60.10)
- SNMP polling: pfSense-BORDE, Cisco Catalyst 1000, hipervisores
- Agente Zabbix en L1 (10.20.60.10) reportando a Sede Central
- Dashboard de disponibilidad de VLANs y túneles VPN
- Alertas configuradas: caída de interfaz, uso de CPU > 80%
- Documentación de incidencias encontradas y acciones correctivas

---

## E5 — Implementación, Monitoreo y Ética de Seguridad (CE032)
**Rol:** Especialista en Seguridad / Auditor TI  
**Estándares:** ISO 27001 · ISO 27002 · NIST SP 800-53  
**Estado:** ❌ SEMESTRE 2

---

### Criterio 1 — Controles Técnicos (IAM, Cifrado, Firewall)
Actividades:
- Configuración de Active Directory (VM-AD-DS): OUs, grupos de seguridad, GPOs
- IAM: roles mínimos por área (Producción, Ventas, Admin, TI)
- Cifrado: HTTPS en API Gateway (certificado TLS), VPN IPSec AES-256-GCM activa
- Firewall: reglas pfSense validadas y documentadas con evidencia de bloqueo
- Pruebas de control: intento de acceso no autorizado → verificación de bloqueo

### Criterio 2 — Principio de Mínimo Privilegio
Actividades:
- Usuarios AD con solo los permisos de su área
- Microservicios con cuentas de BD de solo lectura/escritura (no superuser)
- pfSense: acceso admin restringido a VLAN 10 y VLAN 99 MGMT
- Evidencias de configuración por cada capa

### Criterio 3 — Gestión de Parches y Actualizaciones
Actividades:
- Cronograma mensual de actualizaciones (OS, Docker images, pfSense, Zabbix)
- Procedimiento de parcheo documentado (ventana de mantenimiento, rollback)
- Registro de versiones instaladas y fecha de última actualización

### Criterio 4 — Planes de Continuidad
Actividades:
- Plan de Continuidad del Negocio (BCP) simplificado para Franco's SAC
- RTO y RPO definidos por servicio crítico
- Simulación de fallo de H3 → activación de H4 (standby frío)
- Prueba de restauración desde backup S3 (pg_dump → restore PostgreSQL)
- Evidencias de prueba documentadas

### Criterio 5 — KPIs de Seguridad
Actividades:
- Disponibilidad de red (%): línea base 99%, meta 99.5%
- Tiempo promedio de respuesta a incidente (MTTR)
- Número de intentos de acceso fallidos detectados por semana
- Tiempo de backup completado vs. ventana definida
- Cobertura de parches aplicados (% de activos actualizados)

### Criterio 6 — Registro y Auditoría
Actividades:
- Logs de pfSense centralizados (Syslog hacia VM-MONITOR)
- Logs de AD (eventos de login/logout, cambios de GPO)
- Logs de PostgreSQL (conexiones, queries críticas)
- Análisis de logs: detección de patrones anómalos
- Suricata IPS en pfSense-INTERNO: alertas documentadas

### Criterio 7 — Evaluación de Vulnerabilidades
Actividades:
- Escaneo con herramienta (Nessus Essentials o OpenVAS) sobre VMs expuestas
- Reporte de hallazgos: CVEs encontrados, severidad, descripción
- Plan de remediación aplicado (o justificación de aceptación de riesgo)
- Evidencias antes/después del parcheo

### Criterio 8 — Integración Ética ACM
Actividades:
- Análisis de confidencialidad: datos de clientes y empleados de Franco's SAC
- Cumplimiento Ley 29733 — Protección de Datos Personales (Perú)
- Evaluación de impacto social: qué pasa si la infraestructura falla (empleados sin ERP, ventas detenidas)
- Evaluación de impacto legal: responsabilidad del ingeniero en la custodia de datos

---

## E6 — Implementación y Control de Centro de Datos (CE033)
**Rol:** Administrador de Sistemas / Ingeniero de Operaciones  
**Estándares:** ISO/IEC 20000 · ITIL 4 · TIA-942  
**Estado:** ❌ SEMESTRE 2

---

### Criterio 1 — Servidores Físicos/Virtuales
Actividades:
- Configuración final de todos los hipervisores (H1-H4, H5/L1, H6/L3)
- Inventario de VMs en producción con IP, VLAN, propósito, recursos asignados
- Evidencias de desempeño: CPU usage, RAM usage, IOPS
- Validación de arranque y disponibilidad de cada VM crítica

### Criterio 2 — Servicios (AD, DNS, Web, BD)
Actividades:
- VM-AD-DS: dominio francos.local configurado, usuarios, GPOs aplicadas
- VM-DHCP-DNS primario + réplica: DHCP por VLAN, DNS interno resolviendo francos.local
- VM-API-GATEWAY: NestJS corriendo, HTTPS habilitado, ruta a microservicios funcional
- person-db + core-busines-db: PostgreSQL corriendo, schemas creados, acceso desde microservicios verificado
- Pruebas de integración: login → AD → auth-ms → person-db → respuesta exitosa

### Criterio 3 — Almacenamiento (RAID, SAN, NAS)
Actividades:
- Configuración de almacenamiento VMFS6 en ESXi (RAID software si aplica en lab)
- VM-FILESERVER: Samba/NFS configurado, shares por área de Franco's SAC
- Política de tiering de datos: datos activos en VMFS6 local, backups en S3 AWS
- Documentación de capacidad por datastore

### Criterio 4 — Políticas de Respaldo y Recuperación
Actividades:
- Script pg_dump diario 22:00 → S3 bucket (person-db-backup/ + core-busines-db-backup/)
- Snapshot ESXi diario 23:00 en VMFS6 local
- OVF export semanal de VMs críticas → S3 (vm-exports/)
- Prueba de restauración documentada (restore desde S3 → PostgreSQL)
- RTO definido por servicio: API Gateway < 15 min, BD < 30 min, AD < 1 hora
- RPO: PostgreSQL Streaming Replication → RPO < 5 min para BDs críticas

### Criterio 5 — Definición de SLA
Actividades:
- SLA por servicio: disponibilidad, tiempo de respuesta, tiempo de restauración
- Tabla de SLAs: Servicio → Disponibilidad meta → Penalidad si incumple → Responsable
- Ejemplo: API Gateway: 99.5% disponibilidad, tiempo de respuesta < 200ms
- Mecanismo de medición: Zabbix + Grafana dashboards

### Criterio 6 — Monitoreo de Infraestructura
Actividades:
- Dashboard Grafana con métricas de todos los hipervisores
- Alertas configuradas: VM caída, espacio en disco > 80%, CPU > 90%
- Agentes Zabbix en L1 y L3 reportando a VM-MONITOR (10.10.60.10)
- SNMP polling: Cisco Catalyst 1000, pfSense, APs
- Evidencias de alertas recibidas y atendidas

### Criterio 7 — Procedimientos Operativos y Eficiencia
Actividades:
- Runbook operativo: procedimientos para arrancar/detener VMs, gestión de backups, respuesta a alertas
- Procedimiento de cambio (Change Management — ITIL 4)
- Estimación de eficiencia energética del entorno ESXi (PUE estimado del lab UPeU)
- Recomendaciones de mejora: consolidación de VMs, optimización de recursos

---

## E7 — Presentación Ejecutiva y Sustentación
**Rol:** Equipo completo  
**Etapa CDIO:** Transversal  
**Estado:** ❌ SEMESTRE 2 (al finalizar)

---

### Criterio 1 — Presentación Ejecutiva
Actividades:
- Deck de presentación (10-15 slides): problema → solución → arquitectura → resultados → métricas
- Narrativa ejecutiva: qué obtuvo Franco's SAC con este proyecto
- Video Pitch (si aplica según modalidad): máx. 5 minutos, técnico y persuasivo

### Criterio 2 — Dominio Técnico Integral
Actividades:
- Preparar respuestas a preguntas del jurado sobre los 6 entregables
- Dominar: VLANs, IPSec, pfSense, ESXi, PostgreSQL, NIST CSF, ISO 27001, Tier DC, AWS híbrido
- Simulacros de defensa técnica previos a la sustentación

### Criterio 3 — Argumentación y Defensa
Actividades:
- Justificar decisiones de diseño: por qué Tier II, por qué pfSense dual, por qué AWS VPN y no solo on-prem
- Justificar estándares aplicados y cómo se implementaron
- Preparar defensa de los gaps encontrados y cómo se trataron

### Criterio 4 — Trabajo en Equipo y Ética ACM
Actividades:
- Distribución equitativa de roles en la presentación
- Evidencia de trabajo colaborativo durante el proyecto
- Declaración ética final frente al jurado

---

# Resumen Ejecutivo de Pendientes

## Semestre 1 — Estado actual (al 01-Jun-2026)

| Entregable | Docs completados | Docs pendientes | % avance |
|---|---|---|---|
| E1 — Diseño de Red | **6 / 6** ✅ | — | **100%** 🟢 |
| E2 — Planificación de Seguridad | **5 / 5** ✅ | — | **100%** 🟢 |
| E3 — Diseño de Centro de Datos | **6 / 6** ✅ | — | **100%** 🟢 |
| **TOTAL S1** | **17 / 17** ✅ | — | **100%** 🟢 |

> **E1, E2 y E3 COMPLETOS al 01/06/2026.** Repositorio: https://github.com/marksato13/AREA-DE-INFRA  
> **GATE PENDIENTE:** aprobación del coordinador para iniciar Semestre 2 (E4-E7).

## Semestre 2 — Pendiente completo

| Entregable | Criterios | Estado |
|---|---|---|
| E4 — Implementación Red | 7 | ❌ Depende de Gate S1 |
| E5 — Implementación Seguridad | 8 | ❌ Depende de Gate S1 |
| E6 — Implementación DC | 7 | ❌ Depende de Gate S1 |
| E7 — Sustentación | 4 | ❌ Al finalizar S2 |

---

*Documento generado el 31/05/2026 | Proyecto ITI Franco's SAC | UPeU | Rubén Mark*
