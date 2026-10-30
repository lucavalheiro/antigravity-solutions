(function() {
  if (window.__luciano_widget_loaded) return;
  
  function initWidget() {
    if (window.__luciano_widget_loaded) return;
    if (!document.body) {
      setTimeout(initWidget, 50);
      return;
    }
    window.__luciano_widget_loaded = true;

    // Detectar contexto: Desk (ERPNext) vs CRM
    const path = window.location.pathname.toLowerCase();
    const isDesk = path.startsWith('/app') || path.startsWith('/desk') || path === '/' || !path.includes('/crm');
    const agentName = isDesk ? "ERPi" : "CRMi";
    const agentMode = isDesk ? "erpi" : "crmi";
    const agentTheme = isDesk ? "linear-gradient(135deg, #0284c7, #4f46e5)" : "linear-gradient(135deg, #7c3aed, #4f46e5)";
    const agentSubtitle = isDesk ? "Online (ERP Enterprise Owner)" : "Online (CRM Pipeline Owner)";
    const agentHoverShadow = isDesk ? "rgba(2, 132, 199, 0.45)" : "rgba(124, 58, 237, 0.45)";

    // Injetar estilos CSS
    const style = document.createElement("style");
    style.id = "luciano-ai-style";
    style.innerHTML = `
      #luciano-ai-fab {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 999999;
        display: flex;
        align-items: center;
        gap: 10px;
        background: ${agentTheme};
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 50px;
        cursor: pointer;
        box-shadow: 0 8px 24px ${agentHoverShadow}, 0 2px 6px rgba(0,0,0,0.25);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 14px;
        font-weight: 700;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        user-select: none;
        border: 1px solid rgba(255, 255, 255, 0.3);
      }
      #luciano-ai-fab:hover {
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 12px 28px ${agentHoverShadow}, 0 4px 10px rgba(0,0,0,0.35);
      }
      #luciano-ai-fab .fab-icon {
        width: 22px;
        height: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      #luciano-ai-fab .fab-badge {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
      }

      /* Janela de Chat */
      #luciano-ai-window {
        position: fixed;
        bottom: 84px;
        right: 24px;
        width: 450px;
        height: 630px;
        max-width: calc(100vw - 32px);
        max-height: calc(100vh - 100px);
        background: #111216;
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 18px;
        box-shadow: 0 24px 50px rgba(0, 0, 0, 0.7), 0 0 1px 1px rgba(255,255,255,0.06);
        z-index: 999999;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #e4e4e7;
        transform-origin: bottom right;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      }
      #luciano-ai-window.hidden {
        opacity: 0;
        transform: scale(0.92) translateY(15px);
        pointer-events: none;
      }

      /* Header */
      .lai-header {
        padding: 14px 16px;
        background: #18191f;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .lai-header-info {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .lai-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        background: #000;
        border: 1px solid rgba(255, 255, 255, 0.2);
      }
      .lai-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
      }
      .lai-header-text h4 {
        margin: 0;
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .lai-header-text p {
        margin: 0;
        font-size: 11px;
        color: #10b981;
        display: flex;
        align-items: center;
        gap: 4px;
        font-weight: 500;
      }
      .lai-header-actions button {
        background: transparent;
        border: none;
        color: #a1a1aa;
        cursor: pointer;
        font-size: 16px;
        padding: 4px 6px;
        border-radius: 6px;
        transition: background 0.15s;
      }
      .lai-header-actions button:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
      }

      /* Sugestões Rápidas */
      .lai-pills {
        padding: 8px 12px;
        display: flex;
        gap: 6px;
        overflow-x: auto;
        background: #14151b;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        scrollbar-width: none;
      }
      .lai-pills::-webkit-scrollbar { display: none; }
      .lai-pill {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #d4d4d8;
        font-size: 11px;
        padding: 5px 11px;
        border-radius: 12px;
        cursor: pointer;
        white-space: nowrap;
        transition: all 0.15s;
        font-weight: 500;
      }
      .lai-pill:hover {
        background: ${isDesk ? "#0284c7" : "#7c3aed"};
        color: #fff;
        border-color: ${isDesk ? "#0284c7" : "#7c3aed"};
      }

      /* Mensagens */
      .lai-body {
        flex: 1;
        padding: 14px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      .lai-msg {
        max-width: 90%;
        padding: 10px 14px;
        border-radius: 14px;
        font-size: 13px;
        line-height: 1.5;
        word-break: break-word;
      }
      .lai-msg.assistant {
        align-self: flex-start;
        background: #1d1e26;
        color: #f4f4f5;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-bottom-left-radius: 4px;
      }
      .lai-msg.user {
        align-self: flex-end;
        background: ${agentTheme};
        color: #ffffff;
        border-bottom-right-radius: 4px;
      }
      .lai-msg p { margin: 0 0 6px 0; }
      .lai-msg p:last-child { margin: 0; }
      .lai-msg strong { color: #fff; }
      .lai-msg code {
        background: rgba(0, 0, 0, 0.4);
        padding: 2px 5px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
        color: #38bdf8;
      }
      .lai-msg pre {
        background: #111216;
        padding: 8px 10px;
        border-radius: 8px;
        overflow-x: auto;
        font-size: 12px;
        border: 1px solid rgba(255,255,255,0.08);
      }
      .lai-msg table {
        width: 100%;
        border-collapse: collapse;
        margin: 6px 0;
        font-size: 12px;
      }
      .lai-msg th, .lai-msg td {
        border: 1px solid rgba(255,255,255,0.15);
        padding: 4px 8px;
        text-align: left;
      }
      .lai-msg th {
        background: rgba(255,255,255,0.08);
      }

      /* Indicador de Digitação */
      .lai-typing {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 8px 12px;
        background: #1d1e26;
        border-radius: 12px;
        width: fit-content;
        align-self: flex-start;
      }
      .lai-dot {
        width: 6px;
        height: 6px;
        background: #a1a1aa;
        border-radius: 50%;
        animation: laiPulse 1.2s infinite ease-in-out;
      }
      .lai-dot:nth-child(2) { animation-delay: 0.2s; }
      .lai-dot:nth-child(3) { animation-delay: 0.4s; }
      @keyframes laiPulse {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
      }

      /* Input Footer */
      .lai-footer {
        padding: 12px;
        background: #18191f;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        gap: 8px;
      }
      .lai-footer input {
        flex: 1;
        background: #23242c;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px 14px;
        color: #fff;
        font-size: 13px;
        outline: none;
        transition: border-color 0.2s;
      }
      .lai-footer input:focus {
        border-color: ${isDesk ? "#0284c7" : "#7c3aed"};
      }
      .lai-footer button {
        background: ${agentTheme};
        border: none;
        border-radius: 10px;
        color: #fff;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: opacity 0.15s;
      }
      .lai-footer button:hover {
        opacity: 0.9;
      }
    `;
    document.head.appendChild(style);

    // Criar Botão Flutuante (FAB)
    const fab = document.createElement("div");
    fab.id = "luciano-ai-fab";
    fab.innerHTML = `
      <div class="fab-icon">
        <img src="/assets/crm/images/watsonx_logo.jpg" alt="watsonx" style="width: 22px; height: 22px; border-radius: 50%; object-fit: cover; display: block;" />
      </div>
      <span>${agentName}</span>
      <div class="fab-badge"></div>
    `;
    document.body.appendChild(fab);

    // Configurar Pills e Mensagem Inicial baseadas no modo
    let pillsHtml = "";
    let initialGreeting = "";

    if (isDesk) {
      pillsHtml = `
        <div class="lai-pill" data-msg="Faça um resumo geral do ERPNext: total de faturas, pedidos de venda, compras e saldo financeiro.">📊 Finanças & Balanço</div>
        <div class="lai-pill" data-msg="Como está o estoque geral e quantos itens da lista IBM estão cadastrados?">📦 Estoque & Itens IBM</div>
        <div class="lai-pill" data-msg="Liste os 5 últimos pedidos de venda (Sales Orders) registrados no ERP.">🛒 Pedidos de Venda</div>
        <div class="lai-pill" data-msg="Quais são as ordens de compra recentes e fornecedores cadastrados?">🛍️ Compras & Fornecedores</div>
        <div class="lai-pill" data-msg="Verifique ordens de produção (Manufacturing) e lista de materiais (BOM) ativas.">🏭 Produção / BOM</div>
        <div class="lai-pill" data-msg="Execute um teste de integridade no banco de dados e me reporte a saúde das tabelas.">⚡ Diagnóstico do ERP</div>
      `;
      initialGreeting = `
        Olá! Eu sou o <strong>ERPi</strong>, sua Inteligência Artificial executiva conectada ao <strong>ERPNext</strong> com privilégios totais de <strong>Owner / Administrador</strong>.<br><br>
        Tenho controle e acesso direto a todos os módulos:<br>
        • <strong>Accounting:</strong> Faturas, contas a pagar/receber, conciliação e plano de contas.<br>
        • <strong>Stock & Selling:</strong> Estoque, armazéns, cotações e catálogo IBM com 12.353 itens.<br>
        • <strong>Buying & Manufacturing:</strong> Compras, fornecedores, ordens de produção e BOM.<br>
        • <strong>Assets, Projects & Quality:</strong> Ativos, depreciação, tarefas e inspeções.<br><br>
        O que deseja que eu consulte, execute, altere ou avalie agora?
      `;
    } else {
      pillsHtml = `
        <div class="lai-pill" data-msg="Faça um resumo executivo do CRM: quantos leads e oportunidades temos ativos e qual o valor do pipeline?">📊 Pipeline & Leads</div>
        <div class="lai-pill" data-msg="Mostre os últimos 5 leads cadastrados e seus status.">🔍 Últimos Leads</div>
        <div class="lai-pill" data-msg="Consulte o part number D003KZX na tabela IBM e informe faixas de desconto.">📦 Catálogo IBM</div>
        <div class="lai-pill" data-msg="Crie um lead para Carlos Andrade, empresa TechSolutions, email carlos@techsolutions.com">➕ Criar Lead</div>
      `;
      initialGreeting = `
        Olá! Eu sou o <strong>CRMi</strong>, seu copiloto comercial inteligente no <strong>Frappe CRM</strong>.<br><br>
        Posso gerenciar seus leads, oportunidades no pipeline, buscar part numbers e preços na tabela oficial IBM Outubro 2025 e automatizar propostas comerciais. Como posso ajudar?
      `;
    }

    // Criar Janela de Chat
    const win = document.createElement("div");
    win.id = "luciano-ai-window";
    win.className = "hidden";
    win.innerHTML = `
      <div class="lai-header">
        <div class="lai-header-info">
          <div class="lai-avatar"><img src="/assets/crm/images/watsonx_logo.jpg" alt="watsonx" /></div>
          <div class="lai-header-text">
            <h4>${agentName} Copilot <span>✨</span></h4>
            <p><span style="display:inline-block;width:6px;height:6px;background:#10b981;border-radius:50%"></span> ${agentSubtitle}</p>
          </div>
        </div>
        <div class="lai-header-actions">
          <button id="lai-btn-close" title="Fechar">✕</button>
        </div>
      </div>

      <div class="lai-pills">
        ${pillsHtml}
      </div>

      <div class="lai-body" id="lai-messages">
        <div class="lai-msg assistant">
          ${initialGreeting}
        </div>
      </div>

      <div class="lai-footer">
        <input type="text" id="lai-input" placeholder="Comande qualquer ação, relatório ou teste no ${agentName}..." autocomplete="off">
        <button id="lai-btn-send" title="Enviar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    `;
    document.body.appendChild(win);

    // Eventos de Abertura/Fechamento
    fab.addEventListener("click", () => {
      win.classList.toggle("hidden");
      if (!win.classList.contains("hidden")) {
        document.getElementById("lai-input").focus();
      }
    });

    document.getElementById("lai-btn-close").addEventListener("click", () => {
      win.classList.add("hidden");
    });

    const history = [];

    function formatMarkdown(text) {
      if (!text) return "";
      let html = text
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\n\n/g, "<br><br>")
        .replace(/\n/g, "<br>");
      return html;
    }

    function appendMessage(role, text) {
      const container = document.getElementById("lai-messages");
      const msgDiv = document.createElement("div");
      msgDiv.className = `lai-msg ${role}`;
      msgDiv.innerHTML = formatMarkdown(text);
      container.appendChild(msgDiv);
      container.scrollTop = container.scrollHeight;
    }

    function showTyping() {
      const container = document.getElementById("lai-messages");
      const typing = document.createElement("div");
      typing.id = "lai-typing-indicator";
      typing.className = "lai-typing";
      typing.innerHTML = `<div class="lai-dot"></div><div class="lai-dot"></div><div class="lai-dot"></div>`;
      container.appendChild(typing);
      container.scrollTop = container.scrollHeight;
    }

    function hideTyping() {
      const typing = document.getElementById("lai-typing-indicator");
      if (typing) typing.remove();
    }

    async function sendMessage(text) {
      if (!text || !text.trim()) return;
      const cleanText = text.trim();
      appendMessage("user", cleanText);
      history.push({ role: "user", content: cleanText });
      showTyping();

      try {
        const csrf = (window.frappe && window.frappe.csrf_token) || window.csrf_token || "";
        const res = await fetch("/api/method/crm.api.ai_assistant.chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Frappe-CSRF-Token": csrf
          },
          body: JSON.stringify({
            message: cleanText,
            history: history.slice(-6),
            mode: agentMode
          })
        });

        const data = await res.json();
        hideTyping();

        if (data && data.message && data.message.reply) {
          appendMessage("assistant", data.message.reply);
          history.push({ role: "assistant", content: data.message.reply });
        } else {
          appendMessage("assistant", "⚠️ Não foi possível obter resposta no momento.");
        }
      } catch (e) {
        hideTyping();
        appendMessage("assistant", `⚠️ Erro de comunicação: ${e.message}`);
      }
    }

    const inputEl = document.getElementById("lai-input");
    const sendBtn = document.getElementById("lai-btn-send");

    sendBtn.addEventListener("click", () => {
      const txt = inputEl.value;
      inputEl.value = "";
      sendMessage(txt);
    });

    inputEl.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        const txt = inputEl.value;
        inputEl.value = "";
        sendMessage(txt);
      }
    });

    document.querySelectorAll(".lai-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        const msg = pill.getAttribute("data-msg");
        sendMessage(msg);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initWidget);
  } else {
    initWidget();
  }
})();
