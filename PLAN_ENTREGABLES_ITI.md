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
**Estado:** ❌ TODO PENDIENTE

---

### CE0321 — Identificación de Activos Críticos ❌
**Archivo:** `CE0321_Activos_Criticos.html`

Actividades a realizar:
- Inventario completo de activos de Franco's SAC (hardware, software, datos, servicios, personas)
- Clasificación por tipo: primarios (información, procesos) y secundarios (infraestructura, RRHH)
- Valoración de activos según criterios: Confidencialidad / Integridad / Disponibilidad (CIA)
- Identificación de activos críticos priorizados (person-db, core-busines-db, API Gateway, AD, pfSense)
- Propietario de cada activo definido
- Tabla de activos conforme ISO 27005 Anexo B

**Activos críticos esperados:**
- person-db (PostgreSQL) — auth + personas
- core-busines-db (PostgreSQL) — ventas + inventario + estrategia
- VM-API-GATEWAY (NestJS, DMZ)
- VM-AD-DS (Active Directory)
- VM-PFSENSE-BORDE + VM-PFSENSE-INTERNO
- Túneles VPN IPSec (L1-L4, L3-L4, AWS-L4)
- Imágenes Docker en ECR

---

### CE0322 — Análisis de Riesgos (ISO 27005 / NIST) ❌
**Archivo:** `CE0322_Analisis_Riesgos.html`

Actividades a realizar:
- Identificación de amenazas por activo crítico (acceso no autorizado, fallo de hardware, ransomware, etc.)
- Identificación de vulnerabilidades actuales del entorno
- Cálculo de Probabilidad × Impacto para cada riesgo (escala 1-5)
- Construcción de Matriz de Riesgos (Heat Map): Muy Alto / Alto / Medio / Bajo
- Mapeo a controles NIST CSF (Identify → Protect → Detect → Respond → Recover)
- Plan de tratamiento de riesgos: aceptar / mitigar / transferir / evitar
- Al menos 15 riesgos identificados y evaluados

---

### CE0323 — Políticas de Seguridad ❌
**Archivo:** `CE0323_Politicas_Seguridad.html`

Actividades a realizar:
- Política de Control de Acceso (IAM, principio de mínimo privilegio, AD grupos)
- Política de Gestión de Contraseñas (complejidad, rotación, MFA)
- Política de Backups y Recuperación (pg_dump diario S3, snapshots ESXi, RTO/RPO)
- Política de Gestión de Parches y Actualizaciones (cronograma, ventanas de mantenimiento)
- Política de Uso Aceptable de Recursos TI
- Política de Respuesta a Incidentes (clasificación, escalamiento, comunicación)
- Cada política con: objetivo, alcance, responsable, procedimiento, indicador de cumplimiento
- Alineación explícita a ISO 27001 Anexo A y NIST CSF

---

### CE0324 — Roles y Responsabilidades (RACI) ❌
**Archivo:** `CE0324_Roles_Responsabilidades.html`

Actividades a realizar:
- Definición de roles del SGSI: CISO, Administrador de Red, DBA, Administrador de Sistemas, Usuario Final
- Matriz RACI para cada proceso de seguridad (gestión de accesos, backups, monitoreo, respuesta a incidentes, parches)
- Organigrama de seguridad TI de Franco's SAC
- Responsabilidades operativas diarias / semanales / mensuales por rol
- Vinculación de cada rol con los controles ISO 27001 Anexo A aplicables

---

### CE0325 — Calidad Documental y Ética ACM ❌
**Archivo:** `CE0325_Calidad_Documental_Etica.html`

Actividades a realizar:
- Revisión de coherencia entre CE0321-CE0324
- Declaración ética ACM aplicada a la gestión de seguridad (confidencialidad de datos de clientes, empleados)
- Análisis de impacto social y legal: Ley 29733 (Protección de Datos Personales — Perú)
- Declaración de cumplimiento normativo
- Estructura formal del entregable E2 completo

---

## E3 — Diseño de Centro de Datos (CE033)
**Rol:** Arquitecto de Centro de Datos  
**Estándares:** Uptime Institute · TIA-942 · ASHRAE TC9.9  
**Estado:** ❌ TODO PENDIENTE

---

### CE0331 — Arquitectura Tier I–IV ❌
**Archivo:** `CE0331_Arquitectura_Tier.html`

Actividades a realizar:
- Análisis de necesidades de Franco's SAC para seleccionar el Tier apropiado
- Justificación técnica del Tier seleccionado (esperado: Tier II o Tier III simulado en ESXi)
- Comparativa Tier I / II / III / IV: disponibilidad, redundancia, costo
- Mapeo de la infraestructura ESXi de la UPeU al Tier correspondiente
- Descripción de componentes críticos del data center: energía, refrigeración, conectividad, seguridad física
- Referencia explícita a Uptime Institute Tier Standard

**Justificación esperada:**  
Simulación de Tier II en ambiente ESXi UPeU: redundancia parcial (H3+H4 para BD, DHCP dual), sin generador físico pero con Dual-WAN y UPS a nivel lógico.

---

### CE0332 — Diseño de Layout Físico ❌
**Archivo:** `CE0332_Layout_Fisico.html`

Actividades a realizar:
- Diagrama de distribución de racks (posición de cada servidor/hipervisor en el rack)
- Diseño de flujos de aire: pasillo frío / pasillo caliente (simulado)
- Diagrama de cableado estructurado del data center: patch panels, cable trays
- Distribución de energía: PDUs, circuitos
- Seguridad física: acceso restringido, CCTV (propuesta)
- Plano de planta del área de servidores (simplificado para labs UPeU)
- Referencia a TIA-942 (white space, gray space) y ASHRAE TC9.9 (temperatura 18-27°C)

---

### CE0333 — Dimensionamiento de Capacidad ❌
**Archivo:** `CE0333_Dimensionamiento_Capacidad.html`

Actividades a realizar:
- Cálculo de CPU total disponible vs. requerido por VMs
- Cálculo de RAM total disponible vs. requerido por VMs
- Cálculo de almacenamiento: VMFS6 actual (348 GB H1) + proyección a 3 años
- Estimación de crecimiento de datos: ventas, personas, logs, backups
- Plan de escalamiento: cuándo y cómo agregar capacidad
- Tabla de dimensionamiento por hipervisor (H1, H2, H3, H4, H5/L1, L3-A, H6/L3)
- Proyección de consumo energético estimado (kWh)

**Datos base disponibles:**
- ESXi H1: Dell Precision 7920, 6C Xeon Bronze 3204, 31.65 GB RAM, 348 GB VMFS6
- ESXi H2-H4: Labs UPeU (specs a confirmar)

---

### CE0334 — Virtualización y Cloud Híbrido ❌
**Archivo:** `CE0334_Virtualizacion_Cloud.html`

Actividades a realizar:
- Descripción de la arquitectura de virtualización: VMware ESXi + vSwitches
- Inventario de VMs por hipervisor con su VLAN, IP y propósito
- Descripción de la arquitectura cloud híbrida AWS adoptada:
  - Route 53: DNS + health checks para `francos.com`
  - CloudFront + S3: Angular 20 SPA — frontend global CDN
  - AWS VPN Gateway ↔ pfSense-BORDE: túnel IPSec IKEv2 AES-256-GCM (172.16.30.0/30)
  - S3 Buckets: backups pg_dump diario 22:00 + OVF exports semanales
  - ECR Registry: imágenes Docker de microservicios
- Flujos de datos on-prem ↔ AWS documentados
- Justificación de qué permanece on-prem y qué va a la nube
- Beneficios, riesgos y herramientas justificadas (VMware ESXi + AWS)
- Referencia al diagrama `CE0312_Arquitectura_Hibrida_Global.drawio`

---

### CE0335 — Cumplimiento de Estándares DC ❌
**Archivo:** `CE0335_Cumplimiento_Estandares_DC.html`

Actividades a realizar:
- Mapeo de cada componente del DC al estándar aplicable
- Uptime Institute Tier Standard: nivel de disponibilidad, redundancia N+1
- TIA-942: categorías del data center, white space, subsistemas (arquitectónico, eléctrico, mecánico, telecomunicaciones)
- ASHRAE TC9.9: rangos de temperatura y humedad para equipos IT
- Tabla de cumplimiento: estándar → requerimiento → evidencia de aplicación en el proyecto
- Identificación de gaps respecto al estándar y justificación académica

---

### CE0336 — Calidad Documental y Ética ACM (DC) ❌
**Archivo:** `CE0336_Calidad_Documental_Etica_DC.html`

Actividades a realizar:
- Revisión de coherencia entre CE0331-CE0335
- Declaración ética ACM aplicada al diseño del data center (responsabilidad sobre disponibilidad, impacto de caídas en el negocio de Franco's SAC)
- Revisión final de estructura formal del entregable E3 completo

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

## Semestre 1 — Estado actual (al 31-May-2026)

| Entregable | Docs completados | Docs pendientes | % avance |
|---|---|---|---|
| E1 — Diseño de Red | **6 / 6** ✅ | — | **100%** 🟢 |
| E2 — Planificación de Seguridad | 0 / 5 | CE0321-CE0325 | 0% |
| E3 — Diseño de Centro de Datos | 0 / 6 | CE0331-CE0336 | 0% |
| **TOTAL S1** | **6 / 17** | **11 documentos** | **35%** |

> **E1 COMPLETO al 31/05/2026.** Pendiente: aprobación del coordinador (Gate S1) para que cuente como aprobado y poder avanzar a E2 y E3.

## Semestre 2 — Pendiente completo

| Entregable | Criterios | Estado |
|---|---|---|
| E4 — Implementación Red | 7 | ❌ Depende de Gate S1 |
| E5 — Implementación Seguridad | 8 | ❌ Depende de Gate S1 |
| E6 — Implementación DC | 7 | ❌ Depende de Gate S1 |
| E7 — Sustentación | 4 | ❌ Al finalizar S2 |

---

*Documento generado el 31/05/2026 | Proyecto ITI Franco's SAC | UPeU | Rubén Mark*
