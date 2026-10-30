# Teste de Disparo de Alerta Instana -> GLPI ITIL Bridge
param(
    [string]$BridgeUrl = "http://192.168.173.22:8095",
    [string]$Action = "both" # open, close, both
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " SIMULADOR DE ALERTA IBM INSTANA -> GLPI ITIL" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$IssueId = "instana-demo-$(Get-Random -Minimum 1000 -Maximum 9999)"

if ($Action -in @("open", "both")) {
    Write-Host "`n[1] Disparando Alerta OPEN (Incidente Critico P1)..." -ForegroundColor Yellow
    $OpenPayload = @{
        issue = @{
            id = $IssueId
            type = "issue"
            state = "OPEN"
            text = "Esgotamento Critico de Recursos na GPU (Memoria VRAM > 94%)"
            description = "A utilizacao de memoria de video (VRAM) na GPU 0 excedeu o patamar seguro de 94% por 3 minutos consecutivos."
            severity = 10
            suggestion = "Descarregar modelos ociosos no LiteLLM ou aplicar quantizacao 4-bit."
            link = "https://10.1.0.65.nip.io/#/events;eventId=$IssueId"
            zone = "Luciano-GPU-Production"
            fqdn = "192.168.173.22"
        }
    } | ConvertTo-Json -Depth 5

    $resOpen = Invoke-RestMethod -Uri "$BridgeUrl/webhook/instana" -Method Post -Body $OpenPayload -ContentType "application/json"
    $resOpen | ConvertTo-Json
    Write-Host "-> Chamado aberto com sucesso no GLPI!" -ForegroundColor Green
}

if ($Action -eq "both") {
    Write-Host "`nAguardando 8 segundos antes de simular a normalizacao (auto-resolucao)..." -ForegroundColor Gray
    Start-Sleep -Seconds 8
}

if ($Action -in @("close", "both")) {
    Write-Host "`n[2] Disparando Alerta CLOSED (Normalizacao / Solucao ITIL)..." -ForegroundColor Yellow
    $ClosePayload = @{
        issue = @{
            id = $IssueId
            type = "issue"
            state = "CLOSED"
            text = "Esgotamento Critico de Recursos na GPU (Memoria VRAM > 94%)"
            severity = 10
        }
    } | ConvertTo-Json -Depth 5

    $resClose = Invoke-RestMethod -Uri "$BridgeUrl/webhook/instana" -Method Post -Body $ClosePayload -ContentType "application/json"
    $resClose | ConvertTo-Json
    Write-Host "-> Chamado solucionado automaticamente no GLPI com parecer ITIL!" -ForegroundColor Green
}

Write-Host "`nAcesse o GLPI em: http://192.168.173.22:8090 (Usuario: glpi | Senha: glpi)" -ForegroundColor Cyan
