# 🔍 Use Case 001 — Credential Dumping via LSASS Memory Access

**Técnica MITRE ATT&CK:** [T1003.001 - OS Credential Dumping: LSASS Memory](https://attack.mitre.org/techniques/T1003/001/)  
**Tática:** Credential Access  
**Severidade:** 🔴 Alta  
**Plataforma:** Windows  
**Autor:** Patrick Thiago Rezende dos Santos  
**Data:** 2026-05

---

## 📖 Descrição da Técnica

O processo `lsass.exe` (Local Security Authority Subsystem Service) armazena em memória credenciais de usuários autenticados no Windows, incluindo hashes NTLM, tickets Kerberos e senhas em texto claro (em versões mais antigas ou configurações inseguras).

Adversários utilizam ferramentas como **Mimikatz**, **ProcDump**, **Task Manager** e o próprio **comsvcs.dll** nativo do Windows para realizar dump da memória do LSASS e extrair essas credenciais — permitindo movimentação lateral e escalonamento de privilégios.

Essa técnica é amplamente utilizada em ataques reais e está presente em operações de grupos como **APT28**, **Lazarus Group** e na maioria dos ataques de ransomware modernos.

---

## 🧪 Simulação com Atomic Red Team

### Pré-requisitos
- VM Windows 10/11 com Wazuh Agent instalado
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) instalado
- PowerShell como Administrador

### Executando o teste

```powershell
# Instalar Atomic Red Team (se ainda não tiver)
IEX (IWR 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing)
Install-AtomicRedTeam -getAtomics

# Simular dump via comsvcs.dll (método nativo — sem ferramentas externas)
Invoke-AtomicTest T1003.001 -TestNumbers 1

# Simular dump via ProcDump
Invoke-AtomicTest T1003.001 -TestNumbers 2
```

### O que acontece durante a simulação
1. O processo `rundll32.exe` ou `procdump.exe` abre o handle do `lsass.exe` com permissão de leitura de memória (`PROCESS_VM_READ`)
2. Um arquivo `.dmp` é criado no disco
3. O arquivo pode ser exfiltrado e analisado offline com Mimikatz

---

## 🔎 Evidências Geradas (O que você vai observar no SIEM)

### Windows Event Logs relevantes

| Event ID | Fonte | Descrição |
|----------|-------|-----------|
| **4656** | Security | Handle de objeto solicitado (lsass.exe como alvo) |
| **4663** | Security | Acesso a objeto — leitura de memória do processo |
| **10** | Sysmon | ProcessAccess — processo acessando lsass.exe |
| **1** | Sysmon | Criação de processo suspeito (procdump, rundll32) |
| **11** | Sysmon | Criação de arquivo .dmp |

### Indicadores de Comprometimento (IOCs)

```
Processo alvo: lsass.exe
Processos suspeitos de origem: rundll32.exe, procdump.exe, taskmgr.exe, comsvcs.dll
Linha de comando suspeita: rundll32.exe C:\windows\System32\comsvcs.dll MiniDump
Arquivo gerado: *.dmp em diretórios temporários (C:\Windows\Temp, C:\Users\*\AppData)
```

---

## 🛡️ Regra de Detecção

### Regra Sigma

```yaml
title: LSASS Memory Access - Credential Dumping Attempt
id: a7f3b2c1-9e4d-4f8a-b6c2-d3e5f7a9b1c4
status: experimental
description: Detecta acesso à memória do processo LSASS, indicativo de tentativa de dump de credenciais
references:
  - https://attack.mitre.org/techniques/T1003/001/
  - https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1003.001/T1003.001.md
author: Patrick Thiago Rezende dos Santos
date: 2026/05
tags:
  - attack.credential_access
  - attack.t1003.001
logsource:
  category: process_access
  product: windows
  service: sysmon
detection:
  selection:
    EventID: 10
    TargetImage|endswith: '\lsass.exe'
    GrantedAccess|contains:
      - '0x1010'
      - '0x1038'
      - '0x143a'
      - '0x1fffff'
  filter_legitimate:
    SourceImage|contains:
      - 'MsMpEng.exe'
      - 'Microsoft Defender'
      - 'SentinelAgent'
      - 'CrowdStrike'
  condition: selection and not filter_legitimate
falsepositives:
  - Ferramentas de segurança legítimas (EDR, AV)
  - Processos de diagnóstico corporativos
level: high
```

### Regra Wazuh (XML)

```xml
<rule id="100001" level="12">
  <if_group>sysmon_event_10</if_group>
  <field name="sysmon.targetImage" type="pcre2">(?i)lsass\.exe$</field>
  <field name="sysmon.grantedAccess">0x1010|0x1038|0x143a|0x1fffff</field>
  <description>Possível dump de credenciais: acesso à memória do LSASS detectado</description>
  <mitre>
    <id>T1003.001</id>
  </mitre>
  <group>credential_access,lsass_dump,high_severity</group>
</rule>
```

---

## 🔬 Investigação do Alerta

Ao receber esse alerta em ambiente real, o fluxo de investigação é:

### Passo 1 — Identificar o processo de origem

```kql
# KQL (Microsoft Sentinel / Defender)
SecurityEvent
| where EventID == 10
| where TargetImage contains "lsass"
| project TimeGenerated, SourceImage, SourceProcessId, TargetImage, GrantedAccess, Computer
| order by TimeGenerated desc
```

**Perguntas a responder:**
- Qual processo acessou o LSASS?
- Esse processo é esperado nessa máquina?
- Qual usuário estava logado?

### Passo 2 — Verificar linha de comando e processo pai

```kql
DeviceProcessEvents
| where FileName in~ ("procdump.exe", "rundll32.exe", "taskmgr.exe")
| where ProcessCommandLine contains "lsass" or ProcessCommandLine contains "MiniDump"
| project Timestamp, DeviceName, AccountName, FileName, ProcessCommandLine, InitiatingProcessFileName
```

### Passo 3 — Checar criação de arquivo .dmp

```kql
DeviceFileEvents
| where FileName endswith ".dmp"
| where FolderPath contains "Temp" or FolderPath contains "AppData"
| project Timestamp, DeviceName, FileName, FolderPath, InitiatingProcessFileName, InitiatingProcessAccountName
```

### Passo 4 — Verificar movimentação lateral posterior

Se confirmado o dump, verificar autenticações anômalas nas próximas horas:

```kql
SecurityEvent
| where EventID in (4624, 4648)
| where LogonType in (3, 10)  // Network e RemoteInteractive
| where TimeGenerated > ago(4h)
| summarize count() by Account, WorkstationName, IpAddress
| where count_ > 5
```

---

## 🩹 Resposta ao Incidente

### Contenção imediata
- [ ] Isolar a máquina afetada da rede
- [ ] Revogar e resetar senhas de todos os usuários logados na máquina nas últimas 24h
- [ ] Invalidar tickets Kerberos (executar `klist purge` / `Invoke-Command`)
- [ ] Bloquear hash NTLM capturado (se identificado)

### Erradicação
- [ ] Identificar e remover ferramenta de dump utilizada
- [ ] Verificar persistência (scheduled tasks, registry run keys, serviços)
- [ ] Checar outros hosts com autenticações originadas da máquina comprometida

### Hardening pós-incidente
- [ ] Habilitar **LSA Protection** (`RunAsPPL = 1`)
- [ ] Habilitar **Credential Guard** (Windows 10+ com Hyper-V)
- [ ] Restringir acesso ao SeDebugPrivilege
- [ ] Garantir Sysmon Event ID 10 ativo com filtros adequados

---

## 📚 Referências

- [MITRE ATT&CK T1003.001](https://attack.mitre.org/techniques/T1003/001/)
- [Atomic Red Team - T1003.001](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1003.001/T1003.001.md)
- [Microsoft - LSA Protection](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection)
- [Sigma Rules Repository](https://github.com/SigmaHQ/sigma)
- [Wazuh Documentation](https://documentation.wazuh.com)

---

*Use Case desenvolvido como parte do portfólio de Segurança da Informação — Blue Team / Detection Engineering*
