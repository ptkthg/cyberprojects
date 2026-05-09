# 🔍 Use Case 005 — Abuse of Valid Accounts

**Técnica MITRE ATT&CK:** [T1078 - Valid Accounts](https://attack.mitre.org/techniques/T1078/)  
**Tática:** Defense Evasion / Persistence / Privilege Escalation / Initial Access  
**Severidade:** 🔴 Alta  
**Plataforma:** Windows / Active Directory / Azure AD (Entra ID)  
**Autor:** Patrick Thiago Rezende dos Santos  
**Data:** 2026-05

---

## 📖 Descrição da Técnica

Após capturar credenciais válidas (via phishing, LSASS dump ou outras técnicas), o adversário passa a operar usando contas legítimas do ambiente. Isso é extremamente perigoso porque o comportamento parece normal para a maioria das soluções de segurança — afinal, é uma conta real, com senha real, fazendo login de forma válida.

Essa técnica cobre três categorias principais:

- **T1078.001 — Default Accounts:** uso de contas padrão (Administrator, Guest) não desabilitadas
- **T1078.002 — Domain Accounts:** uso de contas de domínio comprometidas para acesso a recursos corporativos
- **T1078.003 — Local Accounts:** uso de contas locais para persistência e movimentação lateral (relacionado ao UC-002)

**Por que é especialmente relevante para este portfólio:**
Este Use Case está diretamente ligado à experiência do autor com **governança de identidades e acessos (IAM)** — Active Directory, Entra ID e revisões de permissão são parte do seu dia a dia. Detectar abuso de contas válidas requer conhecimento profundo do comportamento esperado de cada conta.

---

## 🧪 Simulação com Atomic Red Team

### Pré-requisitos
- VM Windows com Wazuh Agent e Sysmon
- Conta de domínio com privilégios limitados (para simular comprometimento)
- Atomic Red Team instalado

### Executando o teste

```powershell
# Simular uso de conta local padrão
Invoke-AtomicTest T1078.001 -TestNumbers 1

# Simular acesso com conta de domínio em horário incomum
Invoke-AtomicTest T1078.002 -TestNumbers 1
```

### Simulação manual (para laboratório)

```powershell
# Simular logon com credenciais de outro usuário (requer as credenciais)
$cred = Get-Credential
Start-Process powershell.exe -Credential $cred -ArgumentList "-Command whoami; net user; net localgroup administrators"

# Simular acesso remoto com conta válida fora do horário esperado
# (executar entre 22h e 6h para acionar regras de horário anômalo)
Invoke-Command -ComputerName SERVIDOR -Credential $cred -ScriptBlock { whoami }
```

### O que acontece durante a simulação
1. Logon realizado com conta válida — sem alerta de credencial inválida
2. Acesso a recursos de rede usando permissões legítimas da conta
3. Ações executadas parecem normais para ferramentas sem contexto comportamental
4. Detecção depende de análise de anomalia: horário, localização, volume de acesso

---

## 🔎 Evidências Geradas (O que você vai observar no SIEM)

### Windows Event Logs relevantes

| Event ID | Fonte | Descrição |
|----------|-------|-----------|
| **4624** | Security | Logon bem-sucedido com conta válida |
| **4625** | Security | Falha de logon (tentativas de força bruta antes do sucesso) |
| **4648** | Security | Logon com credenciais explícitas (RunAs) |
| **4720** | Security | Nova conta de usuário criada |
| **4728** | Security | Usuário adicionado a grupo privilegiado |
| **4732** | Security | Usuário adicionado ao grupo Administrators local |
| **4756** | Security | Usuário adicionado a grupo universal |

### Indicadores de Comprometimento (IOCs)

```
Logon em horário incomum (fora do padrão histórico do usuário)
Logon de localização geográfica nova ou IP externo
Mesma conta autenticando em múltiplos hosts em curto intervalo
Conta de serviço fazendo logon interativo (Tipo 2 ou 10)
Conta inativa ou de ex-funcionário sendo usada
Escalada de privilégio: adição a grupo Administrators ou Domain Admins
Múltiplas falhas de logon seguidas de sucesso (força bruta)
```

---

## 🛡️ Regra de Detecção

### Regra Sigma

```yaml
title: Suspicious Valid Account Usage - Behavioral Anomalies
id: e1f7g6h5-4i8d-6j2e-f0g6-h7i9j1e5f8g0
status: experimental
description: >
  Detecta padrões anômalos de uso de contas válidas: logon interativo de conta
  de serviço, adição a grupos privilegiados e logon de conta inativa
references:
  - https://attack.mitre.org/techniques/T1078/
  - https://attack.mitre.org/techniques/T1078/002/
author: Patrick Thiago Rezende dos Santos
date: 2026/05
tags:
  - attack.defense_evasion
  - attack.persistence
  - attack.privilege_escalation
  - attack.initial_access
  - attack.t1078
logsource:
  product: windows
  service: security
detection:
  # Cenário 1: conta de serviço fazendo logon interativo
  selection_service_interactive:
    EventID: 4624
    LogonType:
      - 2
      - 10
    TargetUserName|contains:
      - 'svc_'
      - '_svc'
      - 'service'
      - 'srv_'
  # Cenário 2: adição a grupo privilegiado
  selection_priv_group:
    EventID:
      - 4728
      - 4732
      - 4756
    TargetUserName|contains:
      - 'Administrators'
      - 'Domain Admins'
      - 'Enterprise Admins'
  # Cenário 3: múltiplas falhas seguidas de sucesso (força bruta)
  condition: selection_service_interactive or selection_priv_group
falsepositives:
  - Manutenção legítima de TI com adição temporária a grupos
  - Contas de serviço que necessitam de logon interativo por design
  - Reset de senha seguido de logon (gera falhas antes do sucesso)
level: high
```

### Regra Wazuh (XML)

```xml
<!-- Conta de serviço com logon interativo -->
<rule id="100009" level="12">
  <if_group>windows</if_group>
  <field name="win.system.eventID">4624</field>
  <field name="win.eventdata.logonType">2</field>
  <field name="win.eventdata.targetUserName" type="pcre2">(?i)(svc_|_svc|service|srv_)</field>
  <description>Conta de serviço realizando logon interativo — comportamento anômalo</description>
  <mitre>
    <id>T1078</id>
  </mitre>
  <group>defense_evasion,valid_accounts,high_severity</group>
</rule>

<!-- Adição a grupo privilegiado -->
<rule id="100010" level="14">
  <if_group>windows</if_group>
  <field name="win.system.eventID" type="pcre2">4728|4732|4756</field>
  <field name="win.eventdata.targetUserName" type="pcre2">(?i)(administrators|domain admins|enterprise admins)</field>
  <description>CRÍTICO: Usuário adicionado a grupo privilegiado — possível escalada de privilégio</description>
  <mitre>
    <id>T1078</id>
  </mitre>
  <group>privilege_escalation,valid_accounts,critical</group>
</rule>

<!-- Múltiplas falhas seguidas de sucesso (força bruta bem-sucedida) -->
<rule id="100011" level="14" frequency="5" timeframe="120">
  <if_matched_sid>60122</if_matched_sid>
  <same_field>win.eventdata.targetUserName</same_field>
  <description>CRÍTICO: Múltiplas falhas de logon seguidas de sucesso — possível força bruta bem-sucedida</description>
  <mitre>
    <id>T1078</id>
  </mitre>
  <group>initial_access,brute_force,valid_accounts,critical</group>
</rule>
```

---

## 🔬 Investigação do Alerta

### Passo 1 — Mapear o comportamento histórico da conta

```kql
# KQL — Microsoft Sentinel
# Verificar padrão histórico de logon da conta suspeita
let ContaSuspeita = "nome_do_usuario";
SecurityEvent
| where EventID == 4624
| where TargetUserName == ContaSuspeita
| summarize LogonsPorHora = count() by bin(TimeGenerated, 1h), Computer, IpAddress
| order by TimeGenerated desc
```

**Perguntas a responder:**
- Essa conta costuma logar nesse horário?
- O IP ou host de origem é conhecido?
- Houve aumento repentino de volume de logons?

### Passo 2 — Verificar adições a grupos privilegiados

```kql
SecurityEvent
| where EventID in (4728, 4732, 4756)
| extend AlvoGrupo = tostring(EventData.TargetUserName)
| extend UsuarioAdicionado = tostring(EventData.MemberName)
| extend QuemAdicionou = tostring(EventData.SubjectUserName)
| where AlvoGrupo contains "Admin"
| project TimeGenerated, Computer, AlvoGrupo, UsuarioAdicionado, QuemAdicionou
| order by TimeGenerated desc
```

### Passo 3 — Detectar logon de conta inativa

```kql
# Cruzar logons recentes com lista de contas inativas do AD
# (requer exportação prévia da lista de contas inativas)
let ContasInativas = datatable(UserName:string)["user1","user2","ex_funcionario"];
SecurityEvent
| where EventID == 4624
| where TargetUserName in (ContasInativas)
| project TimeGenerated, Computer, TargetUserName, IpAddress, LogonType
```

### Passo 4 — Correlacionar com a kill chain completa

```kql
// Verificar se essa conta foi usada nos estágios anteriores
let ContaSuspeita = "nome_do_usuario";
let Maquina = "NOME-DA-MAQUINA";
SecurityEvent
| where TargetUserName == ContaSuspeita or SubjectUserName == ContaSuspeita
| where EventID in (4624, 4648, 4698, 4728, 4732)
| project TimeGenerated, EventID, Computer, TargetUserName, SubjectUserName
| order by TimeGenerated asc
```

---

## 🩹 Resposta ao Incidente

### Contenção imediata
- [ ] Desabilitar a conta comprometida imediatamente
- [ ] Revogar todas as sessões ativas (Azure AD: `Revoke-AzureADUserAllRefreshToken`)
- [ ] Remover a conta de grupos privilegiados se adicionada indevidamente
- [ ] Resetar a senha e forçar MFA no próximo logon

### Erradicação
- [ ] Investigar como a credencial foi comprometida (phishing? LSASS dump? força bruta?)
- [ ] Auditar todas as ações realizadas com a conta nas últimas 72h
- [ ] Verificar se foram criadas backdoors (novas contas, tarefas agendadas, regras de e-mail)
- [ ] Checar outras contas que possam ter sido comprometidas pelo mesmo vetor

### Hardening pós-incidente
- [ ] Habilitar **MFA** para todas as contas, especialmente privilegiadas
- [ ] Implementar **Conditional Access** (bloquear logon fora do horário ou de IPs não reconhecidos)
- [ ] Revisar contas inativas e desabilitar após 30 dias sem uso
- [ ] Aplicar **princípio do menor privilégio** — remover permissões excessivas
- [ ] Habilitar **Privileged Identity Management (PIM)** para contas admin (acesso just-in-time)
- [ ] Implementar revisões periódicas de acesso (Access Reviews no Entra ID)

---

## 🔗 Kill Chain Completa do Portfólio

```
UC-004 (T1566.001)    UC-001 (T1003.001)    UC-002 (T1550.002)
Spearphishing    ──→  LSASS Dump       ──→  Pass-the-Hash
(acesso inicial)      (captura hash)         (move lateralmente)
                                                    │
                                                    ▼
                      UC-005 (T1078)        UC-003 (T1053.005)
                      Valid Accounts   ←──  Scheduled Task
                      (opera como legítimo)  (persiste no host)
```

Com os 5 Use Cases, o portfólio cobre o ciclo completo de um ataque direcionado — do e-mail malicioso até a operação silenciosa com credenciais válidas.

---

## 📚 Referências

- [MITRE ATT&CK T1078](https://attack.mitre.org/techniques/T1078/)
- [Microsoft - Privileged Identity Management](https://learn.microsoft.com/en-us/azure/active-directory/privileged-identity-management/)
- [Microsoft - Access Reviews](https://learn.microsoft.com/en-us/azure/active-directory/governance/access-reviews-overview)
- [CIS Controls - Account Management](https://www.cisecurity.org/controls/account-management)

---

*Use Case desenvolvido como parte do portfólio de Segurança da Informação — Blue Team / Detection Engineering*

---
FIM DO CONTEÚDO
---

Depois, extraia apenas o bloco YAML da regra Sigma e salve em:
use-cases/UC-005-valid-accounts/detection-rule.yml

E extraia apenas a seção "Investigação do Alerta" e salve em:
use-cases/UC-005-valid-accounts/investigation.md

Faça um commit com a mensagem: "feat: add UC-005 Valid Accounts use case"

Em seguida, atualize o arquivo README.md da raiz do repositório e adicione uma nova linha na tabela de Use Cases:

| [UC-005](./use-cases/UC-005-valid-accounts/) | T1078 - Valid Accounts | Defense Evasion / Persistence / Initial Access | 🔴 Alta |
