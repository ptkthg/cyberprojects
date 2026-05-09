# 🔍 Use Case 002 — Pass-the-Hash (Lateral Movement via NTLM Hash)

**Técnica MITRE ATT&CK:** [T1550.002 - Use Alternate Authentication Material: Pass the Hash](https://attack.mitre.org/techniques/T1550/002/)  
**Tática:** Lateral Movement / Defense Evasion  
**Severidade:** 🔴 Alta  
**Plataforma:** Windows  
**Pré-requisito do atacante:** Hash NTLM capturado (ex: via UC-001 — LSASS Dump)  
**Autor:** Patrick Thiago Rezende dos Santos  
**Data:** 2026-05

---

## 📖 Descrição da Técnica

Após capturar hashes NTLM via dump do LSASS (T1003.001), o adversário não precisa quebrar a senha — ele pode usá-la diretamente para autenticar em outros sistemas da rede. Essa técnica é chamada de **Pass-the-Hash (PtH)**.

O Windows autentica via protocolo NTLM usando o hash da senha, não a senha em texto claro. Isso significa que qualquer processo com o hash em memória pode se autenticar como aquele usuário em recursos de rede — sem nunca saber a senha real.

Ferramentas comuns usadas por adversários:
- **Mimikatz** (`sekurlsa::pth`)
- **Impacket** (`psexec.py`, `wmiexec.py`)
- **CrackMapExec**
- **Metasploit** (`exploit/windows/smb/psexec`)

Essa técnica é diretamente encadeada ao UC-001: **o dump do LSASS fornece o hash, o Pass-the-Hash usa esse hash para se mover lateralmente.**

---

## 🧪 Simulação com Atomic Red Team

### Pré-requisitos
- VM Windows 10/11 com Wazuh Agent
- Atomic Red Team instalado
- PowerShell como Administrador
- Hash NTLM de um usuário local (pode ser capturado via UC-001)

### Executando o teste

```powershell
# Simular Pass-the-Hash via Mimikatz (requer hash NTLM válido)
Invoke-AtomicTest T1550.002 -TestNumbers 1

# Simular autenticação lateral via NTLM com hash
Invoke-AtomicTest T1550.002 -TestNumbers 2
```

### Simulação manual com Mimikatz (para laboratório)

```powershell
# Passo 1: Capturar hash do usuário (requer SYSTEM)
mimikatz# sekurlsa::logonpasswords

# Passo 2: Usar o hash para criar processo autenticado
mimikatz# sekurlsa::pth /user:Administrator /domain:WORKGROUP /ntlm:HASH_AQUI /run:cmd.exe

# O cmd.exe aberto já está autenticado como Administrator usando o hash
# Agora é possível acessar recursos de rede remotos
```

### O que acontece durante a simulação
1. Um novo processo é criado com token de segurança do usuário alvo
2. Autenticação NTLM é realizada em hosts remotos **sem digitar senha**
3. Conexões de rede aparecem como originárias do usuário legítimo
4. Comandos remotos são executados via SMB, WMI ou WinRM

---

## 🔎 Evidências Geradas (O que você vai observar no SIEM)

### Windows Event Logs relevantes

| Event ID | Fonte | Descrição |
|----------|-------|-----------|
| **4624** | Security | Logon bem-sucedido — Tipo 3 (Network) com NTLM |
| **4625** | Security | Falha de logon (tentativas antes do sucesso) |
| **4648** | Security | Logon com credenciais explícitas |
| **4672** | Security | Privilégios especiais atribuídos ao logon |
| **3** | Sysmon | Conexão de rede originada de processo suspeito |
| **1** | Sysmon | Criação de processo com linha de comando suspeita |

### Assinatura do Pass-the-Hash no Event 4624

O indicador mais confiável é a combinação:
```
EventID: 4624
LogonType: 3 (Network)
AuthenticationPackage: NTLM
LogonProcessName: NtLmSsp
WorkstationName: [máquina de origem]
SubjectUserName: -  ← campo vazio é indicativo forte de PtH
```

### Indicadores de Comprometimento (IOCs)

```
Processos suspeitos: mimikatz.exe, psexec.exe, wmiexec.py
Conexões de rede: SMB (445), WMI (135), WinRM (5985) entre workstations
Padrão: múltiplos logons tipo 3 NTLM para hosts diferentes em curto intervalo
SubjectUserName vazio em Event 4624
Novo processo filho de lsass.exe com linha de comando incomum
```

---

## 🛡️ Regra de Detecção

### Regra Sigma

```yaml
title: Pass-the-Hash Attack - NTLM Lateral Movement Detection
id: b8c4d3e2-1f5a-4g9b-c7d3-e4f6g8b2c5d7
status: experimental
description: >
  Detecta possível Pass-the-Hash identificando logons de rede NTLM
  com campos de origem vazios, indicativo de uso de hash em vez de senha
references:
  - https://attack.mitre.org/techniques/T1550/002/
  - https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventID=4624
author: Patrick Thiago Rezende dos Santos
date: 2026/05
tags:
  - attack.lateral_movement
  - attack.defense_evasion
  - attack.t1550.002
logsource:
  product: windows
  service: security
detection:
  selection:
    EventID: 4624
    LogonType: 3
    AuthenticationPackageName: NTLM
    SubjectUserName: '-'
  filter_legitimate:
    IpAddress:
      - '127.0.0.1'
      - '::1'
    WorkstationName: ''
  condition: selection and not filter_legitimate
falsepositives:
  - Algumas aplicações legítimas usam NTLM com campos vazios
  - Serviços de monitoramento e backup corporativos
level: high
```

### Regra Wazuh (XML)

```xml
<rule id="100002" level="12">
  <if_sid>18104</if_sid>
  <field name="win.system.eventID">4624</field>
  <field name="win.eventdata.logonType">3</field>
  <field name="win.eventdata.authenticationPackageName">NTLM</field>
  <field name="win.eventdata.subjectUserName">-</field>
  <description>Possível Pass-the-Hash: logon NTLM tipo 3 com origem vazia</description>
  <mitre>
    <id>T1550.002</id>
  </mitre>
  <group>lateral_movement,pass_the_hash,high_severity</group>
</rule>

<!-- Regra complementar: múltiplos logons NTLM em curto intervalo -->
<rule id="100003" level="14" frequency="5" timeframe="60">
  <if_matched_sid>100002</if_matched_sid>
  <same_field>win.eventdata.subjectUserSid</same_field>
  <description>ALERTA CRÍTICO: Múltiplos logons NTLM suspeitos — possível movimento lateral via PtH</description>
  <mitre>
    <id>T1550.002</id>
  </mitre>
  <group>lateral_movement,pass_the_hash,critical</group>
</rule>
```

---

## 🔬 Investigação do Alerta

### Passo 1 — Confirmar o padrão de logon suspeito

```kql
# KQL — Microsoft Sentinel
SecurityEvent
| where EventID == 4624
| where LogonType == 3
| where AuthenticationPackageName == "NTLM"
| where SubjectUserName == "-" or SubjectUserName == ""
| where IpAddress !in ("127.0.0.1", "::1")
| project TimeGenerated, Computer, TargetUserName, IpAddress, WorkstationName, LogonProcessName
| order by TimeGenerated desc
```

**Perguntas a responder:**
- De qual máquina partiu a autenticação?
- Qual usuário foi usado?
- Esse usuário costuma acessar esse host remotamente?

### Passo 2 — Identificar padrão de movimento lateral

```kql
# Verificar se o mesmo usuário autenticou em múltiplos hosts
SecurityEvent
| where EventID == 4624
| where LogonType == 3
| where AuthenticationPackageName == "NTLM"
| where TimeGenerated > ago(2h)
| summarize HostsAcessados = dcount(Computer), ListaHosts = make_set(Computer) by TargetUserName, IpAddress
| where HostsAcessados > 3
| order by HostsAcessados desc
```

### Passo 3 — Correlacionar com dump de LSASS anterior (UC-001)

```kql
# Verificar se houve acesso ao LSASS na mesma máquina de origem antes do PtH
let MaquinaOrigem = "NOME-DA-MAQUINA";
let JanelaTemporal = ago(4h);
DeviceEvents
| where DeviceName == MaquinaOrigem
| where ActionType == "ProcessAccess"
| where AdditionalFields contains "lsass"
| where Timestamp > JanelaTemporal
| project Timestamp, ActionType, InitiatingProcessFileName, AdditionalFields
```

### Passo 4 — Verificar execução remota de comandos

```kql
# Checar processos criados remotamente via SMB/WMI após os logons suspeitos
SecurityEvent
| where EventID in (4688, 4697, 7045)
| where TimeGenerated > ago(2h)
| where Computer in (["HOST1", "HOST2"])  // hosts onde ocorreram logons suspeitos
| project TimeGenerated, Computer, SubjectUserName, NewProcessName, CommandLine
```

---

## 🩹 Resposta ao Incidente

### Contenção imediata
- [ ] Identificar todos os hosts acessados com o hash comprometido
- [ ] Desabilitar temporariamente a conta do usuário afetado
- [ ] Resetar a senha do usuário (invalida o hash NTLM atual)
- [ ] Isolar máquina de origem do movimento lateral

### Erradicação
- [ ] Verificar persistência nos hosts acessados (scheduled tasks, novos usuários, serviços)
- [ ] Checar se outros hashes foram capturados e usados
- [ ] Revogar todos os tickets Kerberos ativos do usuário

### Hardening pós-incidente
- [ ] Habilitar **Protected Users Security Group** (impede autenticação NTLM para membros)
- [ ] Desabilitar NTLM onde possível e forçar Kerberos
- [ ] Implementar **Credential Guard** para proteção de hashes em memória
- [ ] Habilitar **Local Administrator Password Solution (LAPS)** — evita reuso de senha local entre hosts
- [ ] Restringir movimentação lateral com **Windows Firewall** entre workstations (bloquear SMB 445 entre peers)

---

## 🔗 Relação com outros Use Cases

```
UC-001 (T1003.001) ──→ UC-002 (T1550.002)
LSASS Dump               Pass-the-Hash
(captura o hash)         (usa o hash para mover lateralmente)
```

Este Use Case é a continuação direta do UC-001. Em um ataque real, essas duas técnicas são executadas em sequência dentro de minutos.

---

## 📚 Referências

- [MITRE ATT&CK T1550.002](https://attack.mitre.org/techniques/T1550/002/)
- [Atomic Red Team - T1550.002](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1550.002/T1550.002.md)
- [Microsoft - Protected Users Security Group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group)
- [LAPS - Local Administrator Password Solution](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview)
- [Detecting Pass-the-Hash - SANS](https://www.sans.org/white-papers/33283/)

---

*Use Case desenvolvido como parte do portfólio de Segurança da Informação — Blue Team / Detection Engineering*
