---
description: Regra de ouro para o gatilho 'gpuubuntu' e integração com servidor local (192.168.173.22)
always_on: true
---

# Regra Crítica: Gatilho 'gpuubuntu'

Sempre que o usuário mencionar a palavra-chave **`gpuubuntu`** (ou variações como "GPU Ubuntu", "gpu ubuntu"):
1. **Destino Obrigatório:** Execute **TODAS** as tarefas, criação de projetos, programação de código, testes e execuções no servidor remoto **`192.168.173.22`** (usuário `luciano-erp`).
2. **Caminho Padrão dos Projetos:** `/home/luciano-erp/projetos/<nome-do-projeto>`.
3. **Mecanismo de Ação:**
   - Use o **Aider** no servidor (`run_aider_task`) para programar, gerar código e commitar no Git com o autor oficial `Luciano Cavalheiro <lucavalheiro@live.com>`.
   - Use a **GPU NVIDIA L4 local** (`ask_luciano_gpu`) para processar o raciocínio sem gastar tokens externos.
   - Use `exec_remote_bash` para rodar comandos no terminal Ubuntu, compilar, rodar testes ou subir contêineres Docker.
4. **Confirmação:** Confirme sempre que a execução e os tokens foram processados localmente na GPU NVIDIA L4 do servidor Ubuntu.
