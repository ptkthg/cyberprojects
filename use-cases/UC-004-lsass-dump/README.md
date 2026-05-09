# 🔍 Use Case 004 — Spearphishing via Attachment

**Técnica MITRE ATT&CK:** [T1566.001 - Phishing: Spearphishing Attachment](https://attack.mitre.org/techniques/T1566/001/)  
**Tática:** Initial Access  
**Severidade:** 🔴 Alta  
**Plataforma:** Windows / E-mail  
**Autor:** Patrick Thiago Rezende dos Santos  
**Data:** 2026-05

---

## 📖 Descrição da Técnica

O Spearphishing via anexo é a técnica de acesso inicial mais utilizada em ataques direcionados. O adversário envia um e-mail personalizado para um alvo específico, contendo um anexo malicioso — geralmente um documento Office com macro, um PDF com exploit, ou um arquivo compactado com executável.

Diferente do phishing genérico, o **spearphishing** usa informações sobre o alvo (nome, cargo, empresa, contexto atual) para aumentar a credibilidade da mensagem e a taxa de abertura.

**Formatos de anexo mais usados:**
- Documentos Office com macros VBA (`.doc`, `.xls`, `.xlsm`)
- Arquivos ISO ou IMG (bypassa Mark-of-the-Web)
- Arquivos compactados com senha (`.zip`, `.rar`) — evade scanning de e-mail
- PDFs com links para download de payload
- Arquivos LNK (atalhos maliciosos)

Grupos que utilizam extensivamente: **APT28**, **APT29**, **Lazarus**, **FIN7**, praticamente todos os operadores de ransomware modernos.

**Por que é o ponto de partida da kill chain:**
Este Use Case representa o **acesso inicial** — o momento em que o atacante entra na rede pela primeira vez. Os UC-001, UC-002 e UC-003 acontecem depois desse ponto.

---

## 🧪 Simulação com Atomic Red Team

### Pré-requisitos
- VM Windows 10/11 com Wazuh Agent e Sysmon
- Microsoft Office instalado (para simulação com macro)
- Atomic Red Team instalado

### Executando o teste

```powershell
# Simular abertura de documento com macro maliciosa
Invoke-AtomicTest T1566.001 -TestNumbers 1

# Simular download de payload via documento Office
Invoke-AtomicTest T1566.001 -TestNumbers 2
```

### Simulação manual (para laboratório)

```powershell
# Criar documento Word com macro que executa PowerShell
# (simulação de payload — não malicioso)
$word = New-Object -ComObject Word.Application
$doc = $word.Documents.Add()
$macro = $doc.VBProject.VBComponents.Add(1)
$macro.CodeModule.AddFromString(@"
Sub AutoOpen()
    Shell "powershell.exe -WindowStyle Hidden -Command Write-EventLog -LogName Application -Source 'AtomicTest' -EventId 9999 -Message 'Macro executada'"
End Sub
"@)
$doc.SaveAs("C:\Users\Public\invoice_2026.doc", 0)
$word.Quit()

# Abrir o documento para disparar o AutoOpen
Start-Process "C:\Users\Public\invoice_2026.doc"
```

### O que acontece durante a simulação
1. Usuário abre o anexo do e-mail
2. O Office exibe aviso de macro — usuário clica em "Habilitar Conteúdo"
3. A macro `AutoOpen()` executa automaticamente
4. Um processo filho é criado a partir do `WINWORD.EXE` ou `EXCEL.EXE`
5. O payload faz download ou executa diretamente na memória

---

## 🔎 Evidências Geradas (O que você vai observar no SIEM)

### Windows Event Logs relevantes

| Event ID | Fonte | Descrição |
|----------|-------|-----------|
| **1** | Sysmon | Processo filho suspeito originado de Office (WINWORD, EXCEL) |
| **3** | Sysmon | Conexão de rede a partir de processo Office |
| **11** | Sysmon | Criação de arquivo suspeito em diretório temporário |
| **7** | Sysmon | Carregamento de DLL suspeita por processo Office |
| **4688** | Security | Criação de processo — cmd.exe ou powershell.exe filho de Office |

### Indicadores de Comprometimento (IOCs)

```
Processos pai suspeitos: WINWORD.EXE, EXCEL.EXE, POWERPNT.EXE, MSPUB.EXE
Processos filho suspeitos: cmd.exe, powershell.exe, wscript.exe, mshta.exe, rundll32.exe
Conexões de rede: processo Office iniciando conexão HTTP/HTTPS externa
Arquivos criados: executáveis ou scripts em %TEMP%, %APPDATA%, C:\Users\Public\
Extensões de anexo de risco: .doc, .xls, .xlsm, .iso, .lnk, .hta
```

### Padrão de detecção principal

```
WINWORD.EXE
    └── powershell.exe ← ALTAMENTE SUSPEITO
            └── cmd.exe
                    └── [payload]
```

Qualquer processo Office gerando filho de linha de comando é um sinal forte de execução de macro maliciosa.

---

## 🛡️ Regra de Detecção

### Regra Sigma

```yaml
title: Suspicious Child Process Spawned by Office Application
id: d0e6f5g4-3h7c-5i1d-e9f5-g6h8i0d4e7f9
status: experimental
description: >
  Detecta processos de linha de comando (cmd, powershell, wscript, mshta)
  originados de aplicações Office — indicativo de execução de macro maliciosa
references:
  - https://attack.mitre.org/techniques/T1566/001/
  - https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1566.001/T1566.001.md
author: Patrick Thiago Rezende dos Santos
date: 2026/05
tags:
  - attack.initial_access
  - attack.execution
  - attack.t1566.001
  - attack.t1059.001
logsource:
  category: process_creation
  product: windows
  service: sysmon
detection:
  selection_parent:
    ParentImage|endswith:
      - '\WINWORD.EXE'
      - '\EXCEL.EXE'
      - '\POWERPNT.EXE'
      - '\MSPUB.EXE'
      - '\MSACCESS.EXE'
  selection_child:
    Image|endswith:
      - '\cmd.exe'
      - '\powershell.exe'
      - '\wscript.exe'
      - '\cscript.exe'
      - '\mshta.exe'
      - '\rundll32.exe'
      - '\regsvr32.exe'
  condition: selection_parent and selection_child
falsepositives:
  - Macros legítimas corporativas (deve ser validado com o time de TI)
  - Plugins Office que utilizam scripts para automação
level: high
```

### Regra Wazuh (XML)

```xml
<!-- Detecção de processo filho suspeito de aplicação Office -->
<rule id="100007" level="14">
  <if_group>sysmon_event1</if_group>
  <field name="sysmon.parentImage" type="pcre2">(?i)(WINWORD|EXCEL|POWERPNT|MSPUB|MSACCESS)\.exe$</field>
  <field name="sysmon.image" type="pcre2">(?i)(cmd|powershell|wscript|cscript|mshta|rundll32|regsvr32)\.exe$</field>
  <description>CRÍTICO: Processo de linha de comando originado de aplicação Office — possível macro maliciosa</description>
  <mitre>
    <id>T1566.001</id>
  </mitre>
  <group>initial_access,macro_execution,high_severity</group>
</rule>

<!-- Detecção de conexão de rede originada de Office -->
<rule id="100008" level="12">
  <if_group>sysmon_event3</if_group>
  <field name="sysmon.image" type="pcre2">(?i)(WINWORD|EXCEL|POWERPNT)\.exe$</field>
  <field name="sysmon.initiated">true</field>
  <description>Aplicação Office iniciando conexão de rede — possível download de payload</description>
  <mitre>
    <id>T1566.001</id>
  </mitre>
  <group>initial_access,office_network,medium_severity</group>
</rule>
```

---

## 🔬 Investigação do Alerta

### Passo 1 — Identificar o processo filho e o documento de origem

```kql
# KQL — Microsoft Sentinel
DeviceProcessEvents
| where InitiatingProcessFileName in~ ("WINWORD.EXE", "EXCEL.EXE", "POWERPNT.EXE")
| where FileName in~ ("powershell.exe", "cmd.exe", "wscript.exe", "mshta.exe", "rundll32.exe")
| project Timestamp, DeviceName, AccountName, FileName, ProcessCommandLine,
          InitiatingProcessFileName, InitiatingProcessCommandLine
| order by Timestamp desc
```

**Perguntas a responder:**
- Qual documento disparou o processo filho?
- Qual usuário abriu o documento?
- O comando executado faz download, executa código em memória ou cria arquivos?

### Passo 2 — Verificar conexões de rede originadas do Office

```kql
DeviceNetworkEvents
| where InitiatingProcessFileName in~ ("WINWORD.EXE", "EXCEL.EXE", "POWERPNT.EXE")
| where RemoteIPType != "Private"
| project Timestamp, DeviceName, InitiatingProcessFileName, RemoteIP, RemoteUrl, RemotePort
| order by Timestamp desc
```

### Passo 3 — Analisar o e-mail de origem (se disponível)

```kql
# Microsoft Defender for Office 365
EmailEvents
| where RecipientEmailAddress == "usuario@empresa.com"
| where AttachmentCount > 0
| where TimeGenerated > ago(24h)
| project TimeGenerated, SenderFromAddress, Subject, AttachmentExtension, DeliveryAction
| order by TimeGenerated desc
```

### Passo 4 — Checar arquivos criados pelo processo suspeito

```kql
DeviceFileEvents
| where InitiatingProcessFileName in~ ("powershell.exe", "cmd.exe", "wscript.exe")
| where FolderPath contains "Temp" or FolderPath contains "Public" or FolderPath contains "AppData"
| where ActionType == "FileCreated"
| where TimeGenerated > ago(2h)
| project Timestamp, DeviceName, FileName, FolderPath, InitiatingProcessFileName, InitiatingProcessCommandLine
```

### Passo 5 — Verificar se houve execução de payload e início da kill chain

```kql
// Correlacionar com os próximos estágios da kill chain
DeviceProcessEvents
| where DeviceName == "NOME-DA-MAQUINA"
| where TimeGenerated > ago(4h)
| where FileName in~ ("mimikatz.exe", "procdump.exe", "schtasks.exe", "net.exe", "nltest.exe")
| project Timestamp, FileName, ProcessCommandLine, AccountName
```

---

## 🩹 Resposta ao Incidente

### Contenção imediata
- [ ] Isolar a máquina do usuário afetado da rede
- [ ] Bloquear o remetente e domínio do e-mail malicioso no gateway
- [ ] Quarentena do arquivo anexo em todos os endpoints (via EDR)
- [ ] Suspender temporariamente a conta do usuário comprometido

### Erradicação
- [ ] Analisar completamente o payload executado (sandbox ou FLARE VM)
- [ ] Verificar persistência criada pelo payload (UC-003)
- [ ] Checar outros usuários que receberam o mesmo e-mail
- [ ] Verificar se houve movimentação lateral a partir da máquina (UC-002)

### Hardening pós-incidente
- [ ] Desabilitar macros por padrão via GPO (`Disable all macros without notification`)
- [ ] Habilitar **Attack Surface Reduction (ASR) Rules** no Defender:
  - Bloquear processos filhos de aplicações Office
  - Bloquear criação de conteúdo executável por Office
  - Bloquear injeção de código por macros Office
- [ ] Implementar sandboxing de e-mail (Defender for Office, Harmony Email)
- [ ] Treinar usuários para identificar spearphishing (simulações periódicas)
- [ ] Bloquear extensões de anexo de alto risco no gateway de e-mail

---

## 🔗 Relação com outros Use Cases

```
UC-004 (T1566.001)  ──→  UC-003 (T1053.005)  ──→  UC-001 (T1003.001)  ──→  UC-002 (T1550.002)
Spearphishing            Scheduled Task             LSASS Dump               Pass-the-Hash
(acesso inicial)         (persiste no host)         (captura credenciais)    (move lateralmente)
```

Este Use Case representa o **início da kill chain**. Em um ataque real de ransomware ou APT, o spearphishing é o vetor de entrada que desencadeia todos os estágios seguintes.

---

## 📚 Referências

- [MITRE ATT&CK T1566.001](https://attack.mitre.org/techniques/T1566/001/)
- [Atomic Red Team - T1566.001](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1566.001/T1566.001.md)
- [Microsoft ASR Rules](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/attack-surface-reduction-rules-reference)
- [SANS - Phishing Detection](https://www.sans.org/white-papers/39981/)

---

*Use Case desenvolvido como parte do portfólio de Segurança da Informação — Blue Team / Detection Engineering*
