#!/bin/bash
BRIDGE_URL="http://192.168.173.22:8095"
ISSUE_ID="instana-demo-$RANDOM"

echo "=========================================================="
echo " SIMULADOR DE ALERTA IBM INSTANA -> GLPI ITIL"
echo "=========================================================="

echo -e "\n[1] Disparando Alerta OPEN (Incidente Critico P1)..."
curl -s -X POST "$BRIDGE_URL/webhook/instana" \
  -H "Content-Type: application/json" \
  -d '{
    "issue": {
      "id": "'"$ISSUE_ID"'",
      "type": "issue",
      "state": "OPEN",
      "text": "Esgotamento Critico de Recursos na GPU (Memoria VRAM > 94%)",
      "description": "A utilizacao de memoria de video (VRAM) na GPU 0 excedeu o patamar seguro de 94% por 3 minutos consecutivos.",
      "severity": 10,
      "suggestion": "Descarregar modelos ociosos no LiteLLM ou aplicar quantizacao 4-bit.",
      "link": "https://10.1.0.65.nip.io/#/events;eventId='"$ISSUE_ID"'",
      "zone": "Luciano-GPU-Production",
      "fqdn": "192.168.173.22"
    }
  }' | jq .

echo -e "\nAguardando 6 segundos antes de simular a normalizacao (auto-resolucao)..."
sleep 6

echo -e "\n[2] Disparando Alerta CLOSED (Normalizacao / Solucao ITIL)..."
curl -s -X POST "$BRIDGE_URL/webhook/instana" \
  -H "Content-Type: application/json" \
  -d '{
    "issue": {
      "id": "'"$ISSUE_ID"'",
      "type": "issue",
      "state": "CLOSED",
      "text": "Esgotamento Critico de Recursos na GPU (Memoria VRAM > 94%)",
      "severity": 10
    }
  }' | jq .

echo -e "\nAcesse o GLPI em: http://192.168.173.22:8090 (Usuario: glpi | Senha: glpi)\n"
