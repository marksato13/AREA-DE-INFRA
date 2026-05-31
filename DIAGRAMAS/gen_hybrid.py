import sys
sys.stdout.reconfigure(encoding='utf-8')

xml = '''<?xml version="1.0" encoding="UTF-8"?>
<mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="4681" pageHeight="3307" math="0" shadow="0">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />

    <!-- TITULO -->
    <mxCell id="title" value="Arquitectura Hibrida — Franco&apos;s SAC | ITI UPeU 2026 v1.0" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=18;fontStyle=1;fontColor=#1B2A4A;" vertex="1" parent="1">
      <mxGeometry x="1400" y="20" width="1200" height="60" as="geometry" />
    </mxCell>

    <!-- ═══════════ AWS CLOUD ═══════════ -->
    <mxCell id="aws_zone" value="AWS CLOUD" style="swimlane;fontStyle=1;align=center;startSize=30;fillColor=#FFF8F0;strokeColor=#FF9900;strokeWidth=3;fontColor=#FF6600;fontSize=14;rounded=1;" vertex="1" parent="1">
      <mxGeometry x="950" y="100" width="2800" height="330" as="geometry" />
    </mxCell>
    <mxCell id="route53" value="Route 53&#xa;DNS + Health Checks&#xa;francos.com" style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.route_53;fillColor=#FF9900;strokeColor=#D45B07;fontStyle=1;fontSize=9;" vertex="1" parent="aws_zone">
      <mxGeometry x="60" y="90" width="70" height="70" as="geometry" />
    </mxCell>
    <mxCell id="cloudfront" value="CloudFront + S3&#xa;Angular 20 SPA&#xa;CDN Global" style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudfront;fillColor=#FF9900;strokeColor=#D45B07;fontStyle=1;fontSize=9;" vertex="1" parent="aws_zone">
      <mxGeometry x="280" y="90" width="70" height="70" as="geometry" />
    </mxCell>
    <mxCell id="ecs" value="ECS Fargate (Failover)&#xa;gateway-ms&#xa;auth-ms | sales-ms" style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ecs;fillColor=#FF9900;strokeColor=#D45B07;fontStyle=1;fontSize=9;" vertex="1" parent="aws_zone">
      <mxGeometry x="620" y="90" width="70" height="70" as="geometry" />
    </mxCell>
    <mxCell id="rds" value="RDS PostgreSQL&#xa;person-db (standby)&#xa;core-busines-db (standby)" style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.rds;fillColor=#FF9900;strokeColor=#D45B07;fontStyle=1;fontSize=9;" vertex="1" parent="aws_zone">
      <mxGeometry x="960" y="90" width="70" height="70" as="geometry" />
    </mxCell>
    <mxCell id="ecr" value="ECR Registry&#xa;Images Docker&#xa;gateway|auth|sales" style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ecr;fillColor=#FF9900;strokeColor=#D45B07;fontStyle=1;fontSize=9;" vertex="1" parent="aws_zone">
      <mxGeometry x="1280" y="90" width="70" height="70" as="geometry" />
    </mxCell>
    <mxCell id="s3bk" value="S3 Backups&#xa;person-db-backup/&#xa;core-busines-db-bkp/&#xa;vm-exports/" style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3;fillColor=#FF9900;strokeColor=#D45B07;fontStyle=1;fontSize=9;" vertex="1" parent="aws_zone">
      <mxGeometry x="1600" y="90" width="70" height="70" as="geometry" />
    </mxCell>
    <mxCell id="aws_vpngw" value="AWS VPN Gateway&#xa;IPSec to Sede Central&#xa;172.16.30.0/30" style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.vpn_gateway;fillColor=#FF9900;strokeColor=#D45B07;fontStyle=1;fontSize=9;" vertex="1" parent="aws_zone">
      <mxGeometry x="2360" y="90" width="70" height="70" as="geometry" />
    </mxCell>
    <mxCell id="aws_vpc_lbl" value="AWS VPC: 10.40.0.0/16  |  ECS subnet: 10.40.10.0/24  |  RDS subnet: 10.40.20.0/24" style="text;html=1;strokeColor=#FF9900;fillColor=#FEF0DC;align=center;fontSize=9;fontColor=#FF6600;fontStyle=1;rounded=1;" vertex="1" parent="aws_zone">
      <mxGeometry x="1900" y="180" width="500" height="30" as="geometry" />
    </mxCell>

    <!-- ═══════════ LOCAL 1 ═══════════ -->
    <mxCell id="local1" value="LOCAL 1" style="swimlane;fontStyle=1;align=center;startSize=30;fillColor=#F0FFF4;strokeColor=#1A7A4A;strokeWidth=3;fontColor=#1A7A4A;fontSize=14;rounded=1;" vertex="1" parent="1">
      <mxGeometry x="50" y="570" width="720" height="1500" as="geometry" />
    </mxCell>
    <mxCell id="l1_isp1" value="ISP1 WAN1" style="shape=mxgraph.cisco.routers.router;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=9;" vertex="1" parent="local1">
      <mxGeometry x="80" y="60" width="60" height="60" as="geometry" />
    </mxCell>
    <mxCell id="l1_isp2" value="ISP2 WAN2" style="shape=mxgraph.cisco.routers.router;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=9;" vertex="1" parent="local1">
      <mxGeometry x="280" y="60" width="60" height="60" as="geometry" />
    </mxCell>
    <mxCell id="l1_pf" value="pfSense-L1&#xa;Multi-WAN Failover&#xa;IPSec to Sede Central&#xa;VPN endpoint: 172.16.10.2" style="shape=mxgraph.cisco.firewalls.firewall;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=9;" vertex="1" parent="local1">
      <mxGeometry x="160" y="200" width="80" height="80" as="geometry" />
    </mxCell>
    <mxCell id="l1_h5" value="HIPERVISOR 5  (ESXi Lab UPeU — TBD)" style="swimlane;fontStyle=1;align=left;startSize=25;fillColor=#E8F5E9;strokeColor=#1A7A4A;strokeWidth=2;fontColor=#1A7A4A;fontSize=10;rounded=1;dashed=1;" vertex="1" parent="local1">
      <mxGeometry x="40" y="380" width="630" height="900" as="geometry" />
    </mxCell>
    <mxCell id="l1_dhcp" value="VM-DHCP-DNS-L1&#xa;DHCP 10.20.10.0/24&#xa;DNS: 10.20.10.10" style="rounded=1;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=9;" vertex="1" parent="l1_h5">
      <mxGeometry x="30" y="50" width="260" height="70" as="geometry" />
    </mxCell>
    <mxCell id="l1_fs" value="VM-FILESERVER-L1&#xa;Samba/NFS&#xa;IP: 10.20.40.10" style="rounded=1;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=9;" vertex="1" parent="l1_h5">
      <mxGeometry x="340" y="50" width="250" height="70" as="geometry" />
    </mxCell>
    <mxCell id="l1_zabbix" value="Agente Zabbix-L1&#xa;IP: 10.20.60.10&#xa;Reporta a Zabbix Sede Central" style="rounded=1;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=9;" vertex="1" parent="l1_h5">
      <mxGeometry x="30" y="180" width="250" height="70" as="geometry" />
    </mxCell>
    <mxCell id="l1_workers" value="Workstations L1 (VLAN 20)&#xa;IP range: 10.20.20.x&#xa;APs fisicos (futuro)" style="rounded=1;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=9;" vertex="1" parent="l1_h5">
      <mxGeometry x="30" y="310" width="560" height="60" as="geometry" />
    </mxCell>
    <mxCell id="l1_vlans" value="VLAN 10 Admin: 10.20.10.0/24 | VLAN 20 Usuarios: 10.20.20.0/24 | VLAN 60 Gestion: 10.20.60.0/28 | VLAN 99 MGMT: 10.20.99.0/28" style="text;html=1;strokeColor=#1A7A4A;fillColor=#EBF7F1;align=center;fontSize=8;fontColor=#1A7A4A;fontStyle=1;rounded=1;" vertex="1" parent="l1_h5">
      <mxGeometry x="20" y="420" width="590" height="40" as="geometry" />
    </mxCell>

    <!-- ═══════════ SEDE CENTRAL (LOCAL 4) ═══════════ -->
    <mxCell id="sc" value="LOCAL 4 — SEDE CENTRAL" style="swimlane;fontStyle=1;align=center;startSize=35;fillColor=#EEF1F8;strokeColor=#1B2A4A;strokeWidth=4;fontColor=#1B2A4A;fontSize=16;rounded=1;" vertex="1" parent="1">
      <mxGeometry x="850" y="560" width="2900" height="1600" as="geometry" />
    </mxCell>

    <!-- ISPs Sede Central -->
    <mxCell id="sc_isp1" value="Cisco Router&#xa;ISP1/WAN1&#xa;GW:172.17.25.121" style="shape=mxgraph.cisco.routers.router;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=9;" vertex="1" parent="sc">
      <mxGeometry x="360" y="60" width="70" height="70" as="geometry" />
    </mxCell>
    <mxCell id="sc_forti" value="FortiGate 40F&#xa;ISP2/WAN2&#xa;LAN:192.168.100.1" style="shape=mxgraph.cisco.firewalls.firewall;fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1;fontSize=9;" vertex="1" parent="sc">
      <mxGeometry x="580" y="60" width="70" height="70" as="geometry" />
    </mxCell>

    <!-- H1 container -->
    <mxCell id="sc_h1" value="HIPERVISOR 1 — BORDE  (Dell Precision 7920 | 31.65 GB RAM | 348 GB VMFS6 | vmnic0/vmnic1/vmnic2)" style="swimlane;fontStyle=1;align=left;startSize=28;fillColor=#F3E8FF;strokeColor=#6B3FA0;strokeWidth=2;fontColor=#6B3FA0;fontSize=10;rounded=1;" vertex="1" parent="sc">
      <mxGeometry x="140" y="190" width="1540" height="360" as="geometry" />
    </mxCell>
    <mxCell id="vm_pf_borde" value="VM-PFSENSE-BORDE&#xa;pfSense 2.7 CE&#xa;WAN1: 172.17.25.7 (vmnic0)&#xa;WAN2: 192.168.100.2 (vmnic1)&#xa;Transit to Internal: 10.0.0.1/30&#xa;NAT | Dual-WAN Failover&#xa;IPSec VPN: L1 | L3 | AWS" style="rounded=1;whiteSpace=wrap;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=9;align=left;verticalAlign=top;" vertex="1" parent="sc_h1">
      <mxGeometry x="30" y="45" width="360" height="130" as="geometry" />
    </mxCell>
    <mxCell id="vm_pf_interno" value="VM-PFSENSE-INTERNO / WAF&#xa;pfSense 2.7 + Suricata IPS&#xa;Transit: 10.0.0.2/30&#xa;Inter-VLAN Routing&#xa;GW todas las VLANs: 10.10.x.1&#xa;Trunk 802.1Q out vmnic2&#xa;→ Cisco Catalyst 1000" style="rounded=1;whiteSpace=wrap;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=9;align=left;verticalAlign=top;" vertex="1" parent="sc_h1">
      <mxGeometry x="440" y="45" width="360" height="130" as="geometry" />
    </mxCell>
    <mxCell id="vm_apigw" value="VM-API-GATEWAY&#xa;NestJS 11 + Docker&#xa;VLAN 30 DMZ&#xa;IP: 10.10.30.10 | Port: 443&#xa;REST endpoint publico&#xa;Recibe: AWS CloudFront&#xa;Usuarios L1 | L3 via VPN" style="rounded=1;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=9;align=left;verticalAlign=top;" vertex="1" parent="sc_h1">
      <mxGeometry x="850" y="45" width="360" height="130" as="geometry" />
    </mxCell>
    <mxCell id="h1_nic" value="vmnic0 → ISP1 Cisco Router (WAN1)  |  vmnic1 → FortiGate 40F (WAN2)  |  vmnic2 → Trunk 802.1Q VLAN 4095 → Cisco Catalyst 1000" style="text;html=1;strokeColor=#6B3FA0;fillColor=#F3E8FF;align=center;fontSize=9;fontColor=#6B3FA0;fontStyle=1;rounded=1;" vertex="1" parent="sc_h1">
      <mxGeometry x="30" y="220" width="1480" height="28" as="geometry" />
    </mxCell>
    <mxCell id="h1_vlans" value="VLAN 10:10.10.10.0/24 | VLAN 20:10.10.20.0/24 | VLAN 30 DMZ:10.10.30.0/28 | VLAN 40:10.10.40.0/24 | VLAN 50:10.10.50.0/28 | VLAN 60:10.10.60.0/28 | VLAN 99 MGMT:10.10.99.0/28" style="text;html=1;strokeColor=none;fillColor=#EEE8FF;align=center;fontSize=8;fontColor=#6B3FA0;rounded=1;" vertex="1" parent="sc_h1">
      <mxGeometry x="30" y="265" width="1480" height="25" as="geometry" />
    </mxCell>
    <mxCell id="h1_transit" value="pfSense-BORDE LAN transit → 10.0.0.0/30 → pfSense-INTERNO (WAF+IPS+Inter-VLAN)" style="text;html=1;strokeColor=none;fillColor=#FFE8FF;align=center;fontSize=8;fontColor=#6B3FA0;fontStyle=2;rounded=1;" vertex="1" parent="sc_h1">
      <mxGeometry x="30" y="308" width="1480" height="25" as="geometry" />
    </mxCell>

    <!-- Cisco Catalyst 1000 -->
    <mxCell id="cisco_sw" value="Cisco Catalyst 1000&#xa;Switch Fisico 802.1Q&#xa;Puertos trunk → H1|H2|H3|H4&#xa;Puerto acceso VLAN20 → AP" style="shape=mxgraph.cisco.switches.workgroup_switch;fillColor=#dae8fc;strokeColor=#1B2A4A;fontStyle=1;fontSize=9;" vertex="1" parent="sc">
      <mxGeometry x="1200" y="460" width="130" height="110" as="geometry" />
    </mxCell>
    <mxCell id="sc_ap" value="AP WiFi&#xa;SSID:FrancosCorp&#xa;VLAN 20&#xa;10.10.20.50" style="shape=mxgraph.cisco.wireless.access_point;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=9;" vertex="1" parent="sc">
      <mxGeometry x="1480" y="475" width="70" height="70" as="geometry" />
    </mxCell>

    <!-- H2 -->
    <mxCell id="sc_h2" value="HIPERVISOR 2 — SERVICIOS REDUNDANTES" style="swimlane;fontStyle=1;align=left;startSize=25;fillColor=#E8F4FD;strokeColor=#2E5090;strokeWidth=2;fontColor=#2E5090;fontSize=11;rounded=1;" vertex="1" parent="sc">
      <mxGeometry x="140" y="650" width="720" height="780" as="geometry" />
    </mxCell>
    <mxCell id="vm_dhcp1" value="VM-DHCP-DNS (primario)&#xa;DHCP all VLANs | DNS primario&#xa;VLAN 10 | IP: 10.10.10.10" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h2">
      <mxGeometry x="30" y="50" width="300" height="75" as="geometry" />
    </mxCell>
    <mxCell id="vm_dhcp2" value="VM-DHCP-DNS (replica/failover)&#xa;DHCP secundario | DNS 2do&#xa;IP: 10.10.10.11" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h2">
      <mxGeometry x="370" y="50" width="300" height="75" as="geometry" />
    </mxCell>
    <mxCell id="vm_ad" value="VM-AD-DS&#xa;Active Directory&#xa;Windows Server 2022&#xa;VLAN 10 | IP: 10.10.10.20" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h2">
      <mxGeometry x="30" y="170" width="290" height="80" as="geometry" />
    </mxCell>
    <mxCell id="vm_ntp" value="VM-NTP&#xa;NTP Server&#xa;IP: 10.10.10.12" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h2">
      <mxGeometry x="380" y="170" width="290" height="80" as="geometry" />
    </mxCell>
    <mxCell id="vm_monitor" value="VM-MONITOR&#xa;Zabbix 6.x + Grafana&#xa;SNMP polling infra completa&#xa;VLAN 60 | IP: 10.10.60.10" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h2">
      <mxGeometry x="30" y="305" width="290" height="80" as="geometry" />
    </mxCell>
    <mxCell id="vm_fs" value="VM-FILESERVER&#xa;Samba/NFS centralizado&#xa;VLAN 40 | IP: 10.10.40.10" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h2">
      <mxGeometry x="380" y="305" width="290" height="80" as="geometry" />
    </mxCell>
    <mxCell id="h2_lbl" value="VLAN 10 Admin: 10.10.10.0/24  |  VLAN 60 Gestion: 10.10.60.0/28  |  VLAN 40 Servicios: 10.10.40.0/24" style="text;html=1;strokeColor=#2E5090;fillColor=#D6EAF8;align=center;fontSize=8;fontColor=#2E5090;fontStyle=1;rounded=1;" vertex="1" parent="sc_h2">
      <mxGeometry x="20" y="440" width="670" height="28" as="geometry" />
    </mxCell>

    <!-- H3 -->
    <mxCell id="sc_h3" value="HIPERVISOR 3 — BACKEND: MICROSERVICIOS + BASES DE DATOS" style="swimlane;fontStyle=1;align=left;startSize=25;fillColor=#F0FFF4;strokeColor=#1A7A4A;strokeWidth=2;fontColor=#1A7A4A;fontSize=11;rounded=1;" vertex="1" parent="sc">
      <mxGeometry x="920" y="650" width="1060" height="780" as="geometry" />
    </mxCell>
    <mxCell id="vm_nats" value="VM-NATS-SERVER&#xa;NATS 2.x + JetStream&#xa;VLAN 40 | IP: 10.10.40.20&#xa;Puerto TCP: 4222" style="rounded=1;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h3">
      <mxGeometry x="390" y="40" width="280" height="80" as="geometry" />
    </mxCell>
    <mxCell id="vm_auth" value="auth-ms&#xa;NestJS Docker&#xa;JWT Auth&#xa;10.10.40.21" style="rounded=1;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h3">
      <mxGeometry x="30" y="175" width="220" height="80" as="geometry" />
    </mxCell>
    <mxCell id="vm_person" value="person-ms&#xa;NestJS Docker&#xa;Personas&#xa;10.10.40.22" style="rounded=1;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h3">
      <mxGeometry x="280" y="175" width="220" height="80" as="geometry" />
    </mxCell>
    <mxCell id="vm_sales" value="sales-invent-ms&#xa;NestJS Docker&#xa;Ventas+Inv&#xa;10.10.40.23" style="rounded=1;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h3">
      <mxGeometry x="540" y="175" width="220" height="80" as="geometry" />
    </mxCell>
    <mxCell id="vm_strategic" value="strategic-ms&#xa;NestJS Docker&#xa;BI/Estrategia&#xa;10.10.40.24" style="rounded=1;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h3">
      <mxGeometry x="800" y="175" width="220" height="80" as="geometry" />
    </mxCell>
    <mxCell id="h3_vlan40" value="VLAN 40 — Servicios (10.10.40.0/24) — NATS TCP 4222 — microservices TCP" style="text;html=1;strokeColor=#1A7A4A;fillColor=#EBF7F1;align=center;fontSize=8;fontColor=#1A7A4A;fontStyle=1;rounded=1;" vertex="1" parent="sc_h3">
      <mxGeometry x="20" y="300" width="1010" height="25" as="geometry" />
    </mxCell>
    <mxCell id="vm_pdb" value="person-db&#xa;PostgreSQL 15&#xa;auth-ms + person-ms&#xa;VLAN 50 | 10.10.50.10:5432" style="shape=mxgraph.flowchart.database;whiteSpace=wrap;fillColor=#e1d5e7;strokeColor=#9673a6;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h3">
      <mxGeometry x="80" y="380" width="330" height="120" as="geometry" />
    </mxCell>
    <mxCell id="vm_cdb" value="core-busines-db&#xa;PostgreSQL 15&#xa;sales-invent-ms + strategic-ms&#xa;VLAN 50 | 10.10.50.11:5432" style="shape=mxgraph.flowchart.database;whiteSpace=wrap;fillColor=#e1d5e7;strokeColor=#9673a6;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h3">
      <mxGeometry x="620" y="380" width="330" height="120" as="geometry" />
    </mxCell>
    <mxCell id="h3_vlan50" value="VLAN 50 — Datos (10.10.50.0/28) — PostgreSQL TCP 5432" style="text;html=1;strokeColor=#9673a6;fillColor=#F3E8FF;align=center;fontSize=8;fontColor=#6B3FA0;fontStyle=1;rounded=1;" vertex="1" parent="sc_h3">
      <mxGeometry x="20" y="550" width="1010" height="25" as="geometry" />
    </mxCell>
    <mxCell id="h3_aws1" value="pg_dump diario 22:00 → S3 (person-db-backup | core-busines-db-backup)" style="text;html=1;strokeColor=#FF9900;fillColor=#FFF8F0;align=center;fontSize=8;fontColor=#FF6600;fontStyle=1;rounded=1;" vertex="1" parent="sc_h3">
      <mxGeometry x="20" y="610" width="1010" height="25" as="geometry" />
    </mxCell>
    <mxCell id="h3_aws2" value="docker push → ECR (gateway-ms | auth-ms | sales-invent-ms | strategic-ms)" style="text;html=1;strokeColor=#FF9900;fillColor=#FFF8F0;align=center;fontSize=8;fontColor=#FF6600;fontStyle=1;rounded=1;" vertex="1" parent="sc_h3">
      <mxGeometry x="20" y="645" width="1010" height="25" as="geometry" />
    </mxCell>

    <!-- H4 -->
    <mxCell id="sc_h4" value="HIPERVISOR 4 — BACKUP CRITICO (Replica H3)" style="swimlane;fontStyle=1;align=left;startSize=25;fillColor=#FFF8E1;strokeColor=#B7770D;strokeWidth=2;fontColor=#B7770D;fontSize=11;rounded=1;" vertex="1" parent="sc">
      <mxGeometry x="2060" y="650" width="680" height="780" as="geometry" />
    </mxCell>
    <mxCell id="vm_bk_gw" value="VM-BACKUP-API-GW&#xa;NestJS Gateway (replica)&#xa;VLAN 30 | 10.10.30.20&#xa;Standby frio" style="rounded=1;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h4">
      <mxGeometry x="30" y="50" width="300" height="80" as="geometry" />
    </mxCell>
    <mxCell id="vm_bk_auth" value="VM-BACKUP-AUTH-MS&#xa;auth-ms (replica)&#xa;10.10.40.30" style="rounded=1;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h4">
      <mxGeometry x="30" y="185" width="280" height="75" as="geometry" />
    </mxCell>
    <mxCell id="vm_bk_sales" value="VM-BACKUP-SALES-MS&#xa;sales-invent-ms (replica)&#xa;10.10.40.31" style="rounded=1;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h4">
      <mxGeometry x="360" y="185" width="280" height="75" as="geometry" />
    </mxCell>
    <mxCell id="vm_bk_db" value="person-db (replica streaming)&#xa;core-busines-db (replica streaming)&#xa;10.10.50.20 | 10.10.50.21&#xa;PostgreSQL Streaming Replication&#xa;RPO menor a 5 min" style="shape=mxgraph.flowchart.database;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=9;" vertex="1" parent="sc_h4">
      <mxGeometry x="30" y="330" width="620" height="130" as="geometry" />
    </mxCell>
    <mxCell id="h4_snaps" value="Snapshot diario 23:00 → VMFS6 local  |  OVF export semanal → S3" style="text;html=1;strokeColor=#B7770D;fillColor=#FFF8E1;align=center;fontSize=8;fontColor=#B7770D;fontStyle=1;rounded=1;" vertex="1" parent="sc_h4">
      <mxGeometry x="20" y="530" width="630" height="28" as="geometry" />
    </mxCell>

    <!-- ═══════════ LOCAL 3 ═══════════ -->
    <mxCell id="local3" value="LOCAL 3" style="swimlane;fontStyle=1;align=center;startSize=30;fillColor=#EFF6FF;strokeColor=#2E5090;strokeWidth=3;fontColor=#2E5090;fontSize=14;rounded=1;" vertex="1" parent="1">
      <mxGeometry x="3830" y="570" width="760" height="1500" as="geometry" />
    </mxCell>
    <mxCell id="l3_isp1" value="ISP1 WAN1" style="shape=mxgraph.cisco.routers.router;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=9;" vertex="1" parent="local3">
      <mxGeometry x="80" y="60" width="60" height="60" as="geometry" />
    </mxCell>
    <mxCell id="l3_isp2" value="ISP2 WAN2" style="shape=mxgraph.cisco.routers.router;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=9;" vertex="1" parent="local3">
      <mxGeometry x="280" y="60" width="60" height="60" as="geometry" />
    </mxCell>
    <mxCell id="l3_pf" value="pfSense-L3&#xa;Multi-WAN Failover&#xa;IPSec to Sede Central&#xa;VPN endpoint: 172.16.20.2" style="shape=mxgraph.cisco.firewalls.firewall;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=9;" vertex="1" parent="local3">
      <mxGeometry x="160" y="200" width="80" height="80" as="geometry" />
    </mxCell>
    <mxCell id="l3_hbk" value="HIPERVISOR L3-A — Microservices Backup" style="swimlane;fontStyle=1;align=left;startSize=25;fillColor=#E8EEF8;strokeColor=#2E5090;strokeWidth=2;fontColor=#2E5090;fontSize=10;rounded=1;dashed=1;" vertex="1" parent="local3">
      <mxGeometry x="30" y="390" width="690" height="400" as="geometry" />
    </mxCell>
    <mxCell id="l3_auth_r" value="auth-ms (replica remota)&#xa;10.30.40.10&#xa;Failover desde H3 Sede Central" style="rounded=1;whiteSpace=wrap;fillColor=#E8EEF8;strokeColor=#2E5090;fontStyle=1;fontSize=9;" vertex="1" parent="l3_hbk">
      <mxGeometry x="30" y="50" width="280" height="70" as="geometry" />
    </mxCell>
    <mxCell id="l3_sales_r" value="sales-invent-ms (replica)&#xa;10.30.40.11&#xa;Acceso ERP desde L3" style="rounded=1;whiteSpace=wrap;fillColor=#E8EEF8;strokeColor=#2E5090;fontStyle=1;fontSize=9;" vertex="1" parent="l3_hbk">
      <mxGeometry x="380" y="50" width="280" height="70" as="geometry" />
    </mxCell>
    <mxCell id="l3_apigw_r" value="API Gateway (replica)&#xa;10.30.30.10&#xa;Failover si H1 Sede Central cae" style="rounded=1;whiteSpace=wrap;fillColor=#E8EEF8;strokeColor=#2E5090;fontStyle=1;fontSize=9;" vertex="1" parent="l3_hbk">
      <mxGeometry x="180" y="180" width="300" height="70" as="geometry" />
    </mxCell>
    <mxCell id="l3_bk_note" value="Replica via VPN IPSec L3 to L4 (172.16.20.0/30)" style="text;html=1;strokeColor=none;fillColor=none;align=center;fontSize=9;fontColor=#2E5090;fontStyle=2;" vertex="1" parent="l3_hbk">
      <mxGeometry x="30" y="310" width="630" height="30" as="geometry" />
    </mxCell>
    <mxCell id="l3_h6" value="HIPERVISOR 6 — Servicios Basicos L3" style="swimlane;fontStyle=1;align=left;startSize=25;fillColor=#EFF6FF;strokeColor=#2E5090;strokeWidth=2;fontColor=#2E5090;fontSize=10;rounded=1;dashed=1;" vertex="1" parent="local3">
      <mxGeometry x="30" y="820" width="690" height="570" as="geometry" />
    </mxCell>
    <mxCell id="l3_dhcp" value="VM-DHCP-DNS-L3&#xa;IP: 10.30.10.10" style="rounded=1;whiteSpace=wrap;fillColor=#DBEAFE;strokeColor=#2E5090;fontStyle=1;fontSize=9;" vertex="1" parent="l3_h6">
      <mxGeometry x="30" y="50" width="270" height="65" as="geometry" />
    </mxCell>
    <mxCell id="l3_fsrv" value="VM-FILESERVER-L3&#xa;Samba/NFS&#xa;IP: 10.30.40.10" style="rounded=1;whiteSpace=wrap;fillColor=#DBEAFE;strokeColor=#2E5090;fontStyle=1;fontSize=9;" vertex="1" parent="l3_h6">
      <mxGeometry x="380" y="50" width="270" height="65" as="geometry" />
    </mxCell>
    <mxCell id="l3_workers" value="Workstations L3 (VLAN 20)&#xa;10.30.20.x | Operarios 2da Planta" style="rounded=1;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=9;" vertex="1" parent="l3_h6">
      <mxGeometry x="30" y="175" width="620" height="60" as="geometry" />
    </mxCell>
    <mxCell id="l3_vlans" value="VLAN 10: 10.30.10.0/24 | VLAN 20: 10.30.20.0/24 | VLAN 60: 10.30.60.0/28 | VLAN 99: 10.30.99.0/28" style="text;html=1;strokeColor=#2E5090;fillColor=#EFF6FF;align=center;fontSize=8;fontColor=#2E5090;fontStyle=1;rounded=1;" vertex="1" parent="l3_h6">
      <mxGeometry x="20" y="290" width="640" height="35" as="geometry" />
    </mxCell>

    <!-- ═══════════ CONNECTIONS ═══════════ -->

    <!-- AWS VPN → pfSense BORDE -->
    <mxCell id="e1" value="IPSec VPN&#xa;172.16.30.0/30&#xa;L4:172.16.30.2" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#FF9900;strokeWidth=2;fontStyle=1;fontSize=8;dashed=1;exitX=0.5;exitY=1;" edge="1" source="aws_vpngw" target="vm_pf_borde" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- CloudFront → API GW -->
    <mxCell id="e2" value="HTTPS 443&#xa;Frontend → API" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#FF9900;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="cloudfront" target="vm_apigw" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- ECS failover to API GW (dashed) -->
    <mxCell id="e3" value="Failover&#xa;Route53 HC" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#FF9900;strokeWidth=1;fontStyle=2;fontSize=8;dashed=1;" edge="1" source="ecs" target="vm_apigw" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- S3 backup from H3 DBs -->
    <mxCell id="e4" value="pg_dump → S3" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#FF9900;strokeWidth=1;fontStyle=2;fontSize=8;dashed=1;" edge="1" source="vm_cdb" target="s3bk" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- ECR push from H3 -->
    <mxCell id="e5" value="docker push" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#FF9900;strokeWidth=1;fontStyle=2;fontSize=8;dashed=1;" edge="1" source="vm_nats" target="ecr" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- ISP1 → pfSense BORDE -->
    <mxCell id="e6" value="vmnic0 WAN1" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#6c8ebf;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="sc_isp1" target="vm_pf_borde" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- FortiGate → pfSense BORDE -->
    <mxCell id="e7" value="vmnic1 WAN2" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#d79b00;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="sc_forti" target="vm_pf_borde" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- pfSense BORDE → pfSense INTERNO transit -->
    <mxCell id="e8" value="Transit&#xa;10.0.0.0/30" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#b85450;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="vm_pf_borde" target="vm_pf_interno" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- pfSense INTERNO → API GW (DMZ VLAN 30) -->
    <mxCell id="e9" value="VLAN 30 DMZ&#xa;10.10.30.0/28" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#82b366;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="vm_pf_interno" target="vm_apigw" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- pfSense INTERNO → Cisco Catalyst 1000 (trunk vmnic2) -->
    <mxCell id="e10" value="vmnic2&#xa;Trunk 802.1Q&#xa;VLAN 4095" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#1B2A4A;strokeWidth=3;fontStyle=1;fontSize=9;" edge="1" source="vm_pf_interno" target="cisco_sw" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- Cisco SW → H2 trunk -->
    <mxCell id="e11" value="Trunk 802.1Q" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#2E5090;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="cisco_sw" target="sc_h2" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- Cisco SW → H3 trunk -->
    <mxCell id="e12" value="Trunk 802.1Q" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#1A7A4A;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="cisco_sw" target="sc_h3" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- Cisco SW → H4 trunk -->
    <mxCell id="e13" value="Trunk 802.1Q" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#B7770D;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="cisco_sw" target="sc_h4" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- Cisco SW → AP access VLAN20 -->
    <mxCell id="e14" value="Access VLAN20" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#d6b656;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="cisco_sw" target="sc_ap" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- API GW → NATS -->
    <mxCell id="e15" value="TCP 4222&#xa;VLAN30→VLAN40" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#82b366;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="vm_apigw" target="vm_nats" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- NATS → microservices -->
    <mxCell id="e16" value="TCP" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#82b366;strokeWidth=1;fontSize=8;" edge="1" source="vm_nats" target="vm_auth" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="e17" value="TCP" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#82b366;strokeWidth=1;fontSize=8;" edge="1" source="vm_nats" target="vm_person" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="e18" value="TCP" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#82b366;strokeWidth=1;fontSize=8;" edge="1" source="vm_nats" target="vm_sales" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="e19" value="TCP" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#82b366;strokeWidth=1;fontSize=8;" edge="1" source="vm_nats" target="vm_strategic" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- auth/person → person-db -->
    <mxCell id="e20" value="5432" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#9673a6;strokeWidth=1;fontSize=8;" edge="1" source="vm_auth" target="vm_pdb" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="e21" value="5432" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#9673a6;strokeWidth=1;fontSize=8;" edge="1" source="vm_person" target="vm_pdb" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- sales/strategic → core-busines-db -->
    <mxCell id="e22" value="5432" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#9673a6;strokeWidth=1;fontSize=8;" edge="1" source="vm_sales" target="vm_cdb" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="e23" value="5432" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#9673a6;strokeWidth=1;fontSize=8;" edge="1" source="vm_strategic" target="vm_cdb" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- H3 → H4 replication -->
    <mxCell id="e24" value="Streaming&#xa;Replication&#xa;+ Snapshots" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#B7770D;strokeWidth=2;fontStyle=1;fontSize=8;dashed=1;" edge="1" source="sc_h3" target="sc_h4" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- VPN L1 ↔ Sede Central -->
    <mxCell id="e25" value="IPSec VPN L1-L4&#xa;172.16.10.0/30&#xa;L1:172.16.10.2 / L4:172.16.10.1" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#1A7A4A;strokeWidth=2;fontStyle=1;fontSize=8;dashed=1;" edge="1" source="l1_pf" target="vm_pf_borde" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- VPN L3 ↔ Sede Central -->
    <mxCell id="e26" value="IPSec VPN L3-L4&#xa;172.16.20.0/30&#xa;L3:172.16.20.2 / L4:172.16.20.1" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#2E5090;strokeWidth=2;fontStyle=1;fontSize=8;dashed=1;" edge="1" source="l3_pf" target="vm_pf_borde" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- L1 ISP → pfSense -->
    <mxCell id="e27" value="WAN1" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#6c8ebf;strokeWidth=1;fontSize=8;" edge="1" source="l1_isp1" target="l1_pf" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="e28" value="WAN2" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#6c8ebf;strokeWidth=1;fontSize=8;" edge="1" source="l1_isp2" target="l1_pf" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- L1 pfSense → H5 -->
    <mxCell id="e29" value="Trunk 802.1Q" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#1A7A4A;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="l1_pf" target="l1_h5" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- L3 ISP → pfSense -->
    <mxCell id="e30" value="WAN1" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#6c8ebf;strokeWidth=1;fontSize=8;" edge="1" source="l3_isp1" target="l3_pf" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="e31" value="WAN2" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#6c8ebf;strokeWidth=1;fontSize=8;" edge="1" source="l3_isp2" target="l3_pf" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- L3 pfSense → hypervisors -->
    <mxCell id="e32" value="Trunk 802.1Q" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#2E5090;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="l3_pf" target="l3_hbk" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="e33" value="Trunk 802.1Q" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#2E5090;strokeWidth=2;fontStyle=1;fontSize=8;" edge="1" source="l3_pf" target="l3_h6" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- Zabbix monitoring -->
    <mxCell id="e34" value="SNMP" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#6c8ebf;strokeWidth=1;fontSize=7;dashed=1;" edge="1" source="vm_monitor" target="sc_h3" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="e35" value="SNMP" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#6c8ebf;strokeWidth=1;fontSize=7;dashed=1;" edge="1" source="vm_monitor" target="sc_h4" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>

    <!-- Legend -->
    <mxCell id="legend" value="LEYENDA" style="swimlane;fontStyle=1;align=center;startSize=25;fillColor=#F4F6FA;strokeColor=#1B2A4A;strokeWidth=2;fontColor=#1B2A4A;fontSize=11;rounded=1;" vertex="1" parent="1">
      <mxGeometry x="50" y="2200" width="750" height="380" as="geometry" />
    </mxCell>
    <mxCell id="l1" value="━━ Trunk 802.1Q (LAN interna)" style="text;html=1;fillColor=none;strokeColor=none;align=left;fontSize=10;fontColor=#1B2A4A;fontStyle=1;" vertex="1" parent="legend">
      <mxGeometry x="20" y="50" width="340" height="25" as="geometry" />
    </mxCell>
    <mxCell id="l2" value="- - - IPSec VPN Tunnel" style="text;html=1;fillColor=none;strokeColor=none;align=left;fontSize=10;fontColor=#1B2A4A;fontStyle=2;" vertex="1" parent="legend">
      <mxGeometry x="20" y="85" width="340" height="25" as="geometry" />
    </mxCell>
    <mxCell id="l3l" value="━━ WAN (ISP1/ISP2/FortiGate)" style="text;html=1;fillColor=none;strokeColor=none;align=left;fontSize=10;fontColor=#6c8ebf;fontStyle=1;" vertex="1" parent="legend">
      <mxGeometry x="20" y="120" width="340" height="25" as="geometry" />
    </mxCell>
    <mxCell id="l4l" value="━━ NATS/microservices TCP" style="text;html=1;fillColor=none;strokeColor=none;align=left;fontSize=10;fontColor=#82b366;fontStyle=1;" vertex="1" parent="legend">
      <mxGeometry x="20" y="155" width="340" height="25" as="geometry" />
    </mxCell>
    <mxCell id="l5l" value="━━ PostgreSQL TCP 5432" style="text;html=1;fillColor=none;strokeColor=none;align=left;fontSize=10;fontColor=#9673a6;fontStyle=1;" vertex="1" parent="legend">
      <mxGeometry x="20" y="190" width="340" height="25" as="geometry" />
    </mxCell>
    <mxCell id="l6l" value="━━ AWS backup/failover" style="text;html=1;fillColor=none;strokeColor=none;align=left;fontSize=10;fontColor=#FF9900;fontStyle=1;" vertex="1" parent="legend">
      <mxGeometry x="20" y="225" width="340" height="25" as="geometry" />
    </mxCell>
    <mxCell id="l7l" value="━━ Streaming Replication DB (H3→H4)" style="text;html=1;fillColor=none;strokeColor=none;align=left;fontSize=10;fontColor=#B7770D;fontStyle=1;" vertex="1" parent="legend">
      <mxGeometry x="20" y="260" width="340" height="25" as="geometry" />
    </mxCell>
    <mxCell id="l8l" value="VPN Mesh: L1-L4: 172.16.10.0/30 | L3-L4: 172.16.20.0/30 | AWS-L4: 172.16.30.0/30&#xa;Sede Central SW: Cisco Catalyst 1000 | Firewalls: pfSense 2.7 CE" style="text;html=1;fillColor=#EEF1F8;strokeColor=#1B2A4A;align=left;fontSize=8;fontColor=#1B2A4A;rounded=1;" vertex="1" parent="legend">
      <mxGeometry x="20" y="305" width="700" height="50" as="geometry" />
    </mxCell>

  </root>
</mxGraphModel>'''

path = r'C:\Users\markp\Desktop\PY-MEGATRON\PY - PERSONAL\PERFIL DE EGRESO - DOC\ENTREGABLES - INFRA\ENTREGABLES 2026 - FRANCOS\DIAGRAMAS\CE0312_Arquitectura_Hibrida_Global.drawio'
with open(path, 'w', encoding='utf-8') as f:
    f.write(xml)
print('OK')
