# 🔍 Use Case 003 — Persistence via Scheduled Task

**Técnica MITRE ATT&CK:** [T1053.005 - Scheduled Task/Job: Scheduled Task](https://attack.mitre.org/techniques/T1053/005/)  
**Tática:** Persistence / Privilege Escalation  
**Severidade:** 🟠 Média-Alta  
**Plataforma:** Windows  
**Autor:** Patrick Thiago Rezende dos Santos  
**Data:** 2026-05

---

## 📖 Descrição da Técnica

Após ganhar acesso a um sistema (via phishing, exploração ou movimento lateral), o adversário precisa garantir que vai continuar presente mesmo após reinicializações ou logoffs. Uma das formas mais comuns de persistência no Windows é a criação de **Scheduled Tasks** (tarefas agendadas).

O atacante cria uma tarefa que executa um payload automaticamente em intervalos definidos, na inicialização do sistema ou no logon do usuário — usando ferramentas nativas como `schtasks.exe` ou APIs do sistema, o que dificulta a detecção por soluções que bloqueiam apenas ferramentas externas.

Grupos como **APT29 (Cozy Bear)**, **FIN7** e operadores de ransomware utilizam essa técnica extensivamente após o acesso inicial para garantir persistência antes de avançar na kill chain.

**Por que é perigosa:**
- Usa binários nativos do Windows (Living off the Land)
- Pode ser criada por qualquer usuário com privilégios suficientes
- Sobrevive a reinicializações
- Pode mascarar o nome da tarefa como processo legítimo do sistema

---

## 🧪 Simulação com Atomic Red Team

### Pré-requisitos
- VM Windows 10/11 com Wazuh Agent
- Atomic Red Team instalado
- PowerShell como Administrador

### Executando o teste

```powershell
# Simular criação de Scheduled Task para persistência
Invoke-AtomicTest T1053.005 -TestNumbers 1

# Simular tarefa criada via schtasks.exe com payload em Base64
Invoke-AtomicTest T1053.005 -TestNumbers 4
```

### Simulação manual (para laboratório)

```powershell
# Criar tarefa agendada suspeita manualmente
schtasks /create /tn "WindowsUpdateHelper" /tr "powershell.exe -WindowStyle Hidden -EncodedCommand <BASE64_PAYLOAD>" /sc onlogon /ru SYSTEM

# Variação: execução na inicialização
schtasks /create /tn "MicrosoftEdgeUpdate" /tr "C:\Users\Public\payload.exe" /sc onstart /ru SYSTEM

# Verificar tarefas criadas
schtasks /query /fo LIST /v | findstr /i "task name\|run as\|task to run"
```

### O que acontece durante a simulação
1. `schtasks.exe` é invocado com parâmetros de criação (`/create`)
2. Uma nova entrada é criada no registro ou em `C:\Windows\System32\Tasks\`
3. O payload é configurado para executar automaticamente
4. Em um ataque real, o payload mantém canal de C2 ou executa ações adicionais

---

## 🔎 Evidências Geradas (O que você vai observar no SIEM)

### Windows Event Logs relevantes

| Event ID | Fonte | Descrição |
|----------|-------|-----------|
| **4698** | Security | Scheduled Task criada |
| **4702** | Security | Scheduled Task atualizada |
| **4699** | Security | Scheduled Task deletada (cobertura de rastros) |
| **4700** | Security | Scheduled Task habilitada |
| **1** | Sysmon | Criação de processo — schtasks.exe com /create |
| **11** | Sysmon | Criação de arquivo em C:\Windows\System32\Tasks\ |
| **13** | Sysmon | Modificação de registro relacionada a tarefas |

### Indicadores de Comprometimento (IOCs)

```
Processo: schtasks.exe com argumento /create
Caminhos suspeitos no payload: C:\Users\Public\, C:\ProgramData\, %TEMP%
Nomes de tarefas que imitam processos legítimos: WindowsUpdate*, Microsoft*, Adobe*
Comandos codificados: powershell.exe -EncodedCommand ou -enc
Execução como SYSTEM por tarefa criada por usuário comum
Arquivo XML criado em C:\Windows\System32\Tasks\ por processo não esperado
```

---

## 🛡️ Regra de Detecção

### Regra Sigma

```yaml
title: Suspicious Scheduled Task Creation - Persistence Attempt
id: c9d5e4f3-2g6b-4h0c-d8e4-f5g7h9c3d6e8
status: experimental
description: >
  Detecta criação de Scheduled Tasks com características suspeitas:
  payload em diretórios incomuns, comandos codificados ou execução como SYSTEM
references:
  - https://attack.mitre.org/techniques/T1053/005/
  - https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1053.005/T1053.005.md
author: Patrick Thiago Rezende dos Santos
date: 2026/05
tags:
  - attack.persistence
  - attack.privilege_escalation
  - attack.t1053.005
logsource:
  product: windows
  service: security
detection:
  selection_event:
    EventID: 4698
  selection_suspicious_path:
    TaskContent|contains:
      - '\Users\Public\'
      - '\ProgramData\'
      - '\AppData\Local\Temp\'
      - '\Windows\Temp\'
  selection_encoded:
    TaskContent|contains:
      - '-EncodedCommand'
      - '-enc '
      - 'FromBase64String'
  selection_system:
    TaskContent|contains: 'SYSTEM'
  condition: selection_event and (selection_suspicious_path or selection_encoded or selection_system)
falsepositives:
  - Softwares legítimos que criam tarefas agendadas durante instalação
  - Scripts de administração corporativa
  - Ferramentas de backup e monitoramento
level: high
```

### Regra Wazuh (XML)

```xml
<!-- Detecção via Event 4698 - Scheduled Task criada -->
<rule id="100004" level="10">
  <if_group>windows</if_group>
  <field name="win.system.eventID">4698</field>
  <description>Scheduled Task criada: %(win.eventdata.taskName)</description>
  <mitre>
    <id>T1053.005</id>
  </mitre>
  <group>persistence,scheduled_task</group>
</rule>

<!-- Escalação: tarefa com payload suspeito -->
<rule id="100005" level="14">
  <if_sid>100004</if_sid>
  <field name="win.eventdata.taskContent" type="pcre2">(?i)(encodedcommand|programdata|users\\public|appdata.*temp|fromsbase64)</field>
  <description>CRÍTICO: Scheduled Task criada com payload suspeito — possível persistência</description>
  <mitre>
    <id>T1053.005</id>
  </mitre>
  <group>persistence,scheduled_task,high_severity</group>
</rule>

<!-- Detecção via Sysmon Event 1 - schtasks /create -->
<rule id="100006" level="12">
  <if_group>sysmon_event1</if_group>
  <field name="sysmon.image" type="pcre2">(?i)schtasks\.exe$</field>
  <field name="sysmon.commandLine" type="pcre2">(?i)/create</field>
  <description>Processo schtasks.exe invocado com argumento /create</description>
  <mitre>
    <id>T1053.005</id>
  </mitre>
  <group>persistence,scheduled_task</group>
</rule>
```

---

## 🔬 Investigação do Alerta

### Passo 1 — Identificar a tarefa criada

```kql
# KQL — Microsoft Sentinel
SecurityEvent
| where EventID == 4698
| extend TaskName = tostring(EventData.TaskName)
| extend TaskContent = tostring(EventData.TaskContent)
| extend SubjectUser = tostring(EventData.SubjectUserName)
| project TimeGenerated, Computer, SubjectUser, TaskName, TaskContent
| order by TimeGenerated desc
```

**Perguntas a responder:**
- Quem criou a tarefa? Era esperado?
- O nome da tarefa imita algum processo legítimo?
- Qual é o payload configurado para execução?

### Passo 2 — Analisar o conteúdo da tarefa

```kql
SecurityEvent
| where EventID == 4698
| extend TaskContent = tostring(EventData.TaskContent)
| where TaskContent contains "-EncodedCommand"
    or TaskContent contains "ProgramData"
    or TaskContent contains @"\Users\Public\"
    or TaskContent contains "FromBase64String"
| project TimeGenerated, Computer, EventData.TaskName, TaskContent
```

### Passo 3 — Verificar processo que criou a tarefa (Sysmon)

```kql
DeviceProcessEvents
| where FileName =~ "schtasks.exe"
| where ProcessCommandLine contains "/create"
| project Timestamp, DeviceName, AccountName, ProcessCommandLine, InitiatingProcessFileName, InitiatingProcessCommandLine
| order by Timestamp desc
```

**Red flag:** se o processo pai for `powershell.exe`, `wscript.exe`, `mshta.exe` ou qualquer processo não administrativo, é altamente suspeito.

### Passo 4 — Correlacionar com acesso lateral anterior (UC-002)

```kql
# Verificar se houve logon NTLM suspeito na mesma máquina antes da criação da tarefa
let Maquina = "NOME-DA-MAQUINA";
let HoraTarefa = datetime(2026-05-01T10:00:00Z); // substituir pelo horário do alerta
SecurityEvent
| where Computer == Maquina
| where EventID == 4624
| where LogonType == 3
| where AuthenticationPackageName == "NTLM"
| where TimeGenerated between ((HoraTarefa - 2h) .. HoraTarefa)
| project TimeGenerated, Computer, TargetUserName, IpAddress, LogonType
```

---

## 🩹 Resposta ao Incidente

### Contenção imediata
- [ ] Desabilitar a tarefa suspeita imediatamente: `schtasks /disable /tn "NomeDaTarefa"`
- [ ] Deletar a tarefa após coleta de evidências: `schtasks /delete /tn "NomeDaTarefa" /f`
- [ ] Isolar a máquina se payload malicioso confirmado
- [ ] Preservar o arquivo XML da tarefa em `C:\Windows\System32\Tasks\` como evidência

### Erradicação
- [ ] Analisar o payload completo (decodificar Base64 se necessário)
- [ ] Verificar outras tarefas criadas pelo mesmo usuário ou no mesmo período
- [ ] Checar outros mecanismos de persistência: registry run keys, serviços, startup folder
- [ ] Identificar vetor de acesso inicial que permitiu a criação da tarefa

### Hardening pós-incidente
- [ ] Restringir criação de Scheduled Tasks a administradores via GPO
- [ ] Habilitar auditoria de **Task Scheduler** nos logs de segurança (Event 4698/4699/4700/4702)
- [ ] Monitorar `C:\Windows\System32\Tasks\` com alertas de criação de arquivo
- [ ] Implementar **AppLocker** ou **WDAC** para bloquear payloads em diretórios não autorizados
- [ ] Bloquear execução de PowerShell encodado via política de execução

---

## 🔗 Relação com outros Use Cases

```
UC-001 (T1003.001)  ──→  UC-002 (T1550.002)  ──→  UC-003 (T1053.005)
LSASS Dump               Pass-the-Hash              Scheduled Task
(captura o hash)         (move lateralmente)        (garante persistência)
```

Após o movimento lateral via Pass-the-Hash, o adversário cria uma Scheduled Task no novo host para garantir que seu acesso persiste mesmo após reinicializações ou detecção parcial.

---

## 📚 Referências

- [MITRE ATT&CK T1053.005](https://attack.mitre.org/techniques/T1053/005/)
- [Atomic Red Team - T1053.005](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1053.005/T1053.005.md)
- [Microsoft - Scheduled Tasks Security](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4698)
- [SANS - Detecting Persistence Mechanisms](https://www.sans.org/white-papers/39870/)

---

*Use Case desenvolvido como parte do portfólio de Segurança da Informação — Blue Team / Detection Engineering*
