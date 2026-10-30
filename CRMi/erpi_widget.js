(function() {
  const path = window.location.pathname.toLowerCase();
  if (path.startsWith('/crm')) return;
  if (window.__erpi_widget_loaded) return;
  
  function initERPi() {
    const curPath = window.location.pathname.toLowerCase();
    if (curPath.startsWith('/crm')) return;
    if (window.__erpi_widget_loaded) return;
    if (!document.body) {
      setTimeout(initERPi, 50);
      return;
    }
    window.__erpi_widget_loaded = true;

    // Remover qualquer widget antigo se existir
    const oldFab = document.getElementById("luciano-ai-fab");
    if (oldFab) oldFab.remove();
    const oldWin = document.getElementById("luciano-ai-window");
    if (oldWin) oldWin.remove();
    const crmiFab = document.getElementById("crmi-ai-fab");
    if (crmiFab) crmiFab.remove();
    const crmiWin = document.getElementById("crmi-ai-window");
    if (crmiWin) crmiWin.remove();

    // Injetar estilos CSS exclusivos do ERPi
    const style = document.createElement("style");
    style.id = "erpi-ai-style";
    style.innerHTML = `
      #erpi-ai-fab {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 999999;
        display: flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(135deg, #0284c7, #2563eb);
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 50px;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(2, 132, 199, 0.45), 0 2px 6px rgba(0,0,0,0.25);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 14px;
        font-weight: 700;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        user-select: none;
        border: 1px solid rgba(255, 255, 255, 0.35);
      }
      #erpi-ai-fab:hover {
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 12px 28px rgba(2, 132, 199, 0.55), 0 4px 10px rgba(0,0,0,0.35);
      }
      #erpi-ai-fab .fab-icon {
        width: 22px;
        height: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      #erpi-ai-fab .fab-badge {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
      }

      /* Janela de Chat do ERPi */
      #erpi-ai-window {
        position: fixed;
        bottom: 84px;
        right: 24px;
        width: 460px;
        height: 640px;
        max-width: calc(100vw - 32px);
        max-height: calc(100vh - 100px);
        background: #101217;
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 18px;
        box-shadow: 0 24px 50px rgba(0, 0, 0, 0.75), 0 0 1px 1px rgba(255,255,255,0.06);
        z-index: 999999;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #e4e4e7;
        transform-origin: bottom right;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      }
      #erpi-ai-window.hidden {
        opacity: 0;
        transform: scale(0.92) translateY(15px);
        pointer-events: none;
      }

      /* Header */
      .erpi-header {
        padding: 14px 16px;
        background: #161820;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .erpi-header-info {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .erpi-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.4);
        background: #000;
        border: 1px solid rgba(255, 255, 255, 0.2);
      }
      .erpi-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
      }
      .erpi-header-text h4 {
        margin: 0;
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .erpi-header-text p {
        margin: 0;
        font-size: 11px;
        color: #38bdf8;
        display: flex;
        align-items: center;
        gap: 4px;
        font-weight: 500;
      }
      .erpi-header-actions button {
        background: transparent;
        border: none;
        color: #a1a1aa;
        cursor: pointer;
        font-size: 16px;
        padding: 4px 6px;
        border-radius: 6px;
        transition: background 0.15s;
      }
      .erpi-header-actions button:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
      }

      /* Sugestões Rápidas */
      .erpi-pills {
        padding: 8px 12px;
        display: flex;
        gap: 6px;
        overflow-x: auto;
        background: #13141a;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        scrollbar-width: none;
      }
      .erpi-pills::-webkit-scrollbar { display: none; }
      .erpi-pill {
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
      .erpi-pill:hover {
        background: #0284c7;
        color: #fff;
        border-color: #0284c7;
      }

      /* Mensagens */
      .erpi-body {
        flex: 1;
        padding: 14px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      .erpi-msg {
        max-width: 90%;
        padding: 10px 14px;
        border-radius: 14px;
        font-size: 13px;
        line-height: 1.5;
        word-break: break-word;
      }
      .erpi-msg.assistant {
        align-self: flex-start;
        background: #1a1c24;
        color: #f4f4f5;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-bottom-left-radius: 4px;
      }
      .erpi-msg.user {
        align-self: flex-end;
        background: linear-gradient(135deg, #0284c7, #2563eb);
        color: #ffffff;
        border-bottom-right-radius: 4px;
      }
      .erpi-msg p { margin: 0 0 6px 0; }
      .erpi-msg p:last-child { margin: 0; }
      .erpi-msg strong { color: #fff; }
      .erpi-msg code {
        background: rgba(0, 0, 0, 0.4);
        padding: 2px 5px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
        color: #38bdf8;
      }
      .erpi-msg pre {
        background: #101217;
        padding: 8px 10px;
        border-radius: 8px;
        overflow-x: auto;
        font-size: 12px;
        border: 1px solid rgba(255,255,255,0.08);
      }
      .erpi-msg table {
        width: 100%;
        border-collapse: collapse;
        margin: 6px 0;
        font-size: 12px;
      }
      .erpi-msg th, .erpi-msg td {
        border: 1px solid rgba(255,255,255,0.15);
        padding: 4px 8px;
        text-align: left;
      }
      .erpi-msg th {
        background: rgba(255,255,255,0.08);
      }

      /* Indicador de Digitação */
      .erpi-typing {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 8px 12px;
        background: #1a1c24;
        border-radius: 12px;
        width: fit-content;
        align-self: flex-start;
      }
      .erpi-dot {
        width: 6px;
        height: 6px;
        background: #38bdf8;
        border-radius: 50%;
        animation: erpiPulse 1.2s infinite ease-in-out;
      }
      .erpi-dot:nth-child(2) { animation-delay: 0.2s; }
      .erpi-dot:nth-child(3) { animation-delay: 0.4s; }
      @keyframes erpiPulse {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
      }

      /* Input Footer */
      .erpi-footer {
        padding: 12px;
        background: #161820;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        gap: 8px;
      }
      .erpi-footer input {
        flex: 1;
        background: #20232c;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px 14px;
        color: #fff;
        font-size: 13px;
        outline: none;
        transition: border-color 0.2s;
      }
      .erpi-footer input:focus {
        border-color: #0284c7;
      }
      .erpi-footer button {
        background: linear-gradient(135deg, #0284c7, #2563eb);
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
      .erpi-footer button:hover {
        opacity: 0.9;
      }
    `;
    document.head.appendChild(style);

    // Botão FAB do ERPi
    const fab = document.createElement("div");
    fab.id = "erpi-ai-fab";
    fab.innerHTML = `
      <div class="fab-icon">
        <img src="/assets/crm/images/watsonx_logo.jpg" alt="watsonx" style="width: 22px; height: 22px; border-radius: 50%; object-fit: cover; display: block;" />
      </div>
      <span>ERPi</span>
      <div class="fab-badge"></div>
    `;
    document.body.appendChild(fab);

    // Janela de Chat do ERPi
    const win = document.createElement("div");
    win.id = "erpi-ai-window";
    win.className = "hidden";
    win.innerHTML = `
      <div class="erpi-header">
        <div class="erpi-header-info">
          <div class="erpi-avatar"><img src="/assets/crm/images/watsonx_logo.jpg" alt="watsonx" /></div>
          <div class="erpi-header-text">
            <h4>ERPi Copilot <span>⚡</span></h4>
            <p><span style="display:inline-block;width:6px;height:6px;background:#10b981;border-radius:50%"></span> Online (Módulos ERPNext)</p>
          </div>
        </div>
        <div class="erpi-header-actions">
          <button id="erpi-btn-close" title="Fechar">✕</button>
        </div>
      </div>

      <div class="erpi-pills">
        <div class="erpi-pill" data-msg="Faça um resumo geral do ERPNext: total de faturas, pedidos de venda, compras e saldo financeiro.">📊 Finanças & Balanço</div>
        <div class="erpi-pill" data-msg="Como está o estoque geral e quantos itens da lista IBM estão cadastrados?">📦 Estoque & Itens IBM</div>
        <div class="erpi-pill" data-msg="Liste os 5 últimos pedidos de venda (Sales Orders) registrados no ERP.">🛒 Pedidos de Venda</div>
        <div class="erpi-pill" data-msg="Quais são as ordens de compra recentes e fornecedores cadastrados?">🛍️ Compras & Fornecedores</div>
        <div class="erpi-pill" data-msg="Verifique ordens de produção (Manufacturing) e lista de materiais (BOM) ativas.">🏭 Produção / BOM</div>
        <div class="erpi-pill" data-msg="Execute um teste de integridade no banco de dados e me reporte a saúde das tabelas.">⚡ Diagnóstico do ERP</div>
      </div>

      <div class="erpi-body" id="erpi-messages">
        <div class="erpi-msg assistant">
          Olá! Eu sou o <strong>ERPi</strong>, sua Inteligência Artificial executiva conectada a todos os módulos do <strong>ERPNext</strong> com privilégios totais de <strong>Owner / Administrador</strong>.<br><br>
          Tenho controle direto sobre:<br>
          • <strong>Accounting:</strong> Faturas, contas a pagar/receber, conciliação e plano de contas.<br>
          • <strong>Stock & Selling:</strong> Estoque, armazéns, cotações e catálogo IBM com 12.353 itens.<br>
          • <strong>Buying & Manufacturing:</strong> Compras, fornecedores, ordens de produção e BOM.<br>
          • <strong>Assets, Projects & Quality:</strong> Ativos, depreciação, tarefas e inspeções.<br><br>
          O que deseja que eu consulte, execute, altere ou avalie no ERP?
        </div>
      </div>

      <div class="erpi-footer">
        <input type="text" id="erpi-input" placeholder="Comande qualquer ação, relatório ou teste no ERPi..." autocomplete="off">
        <button id="erpi-btn-send" title="Enviar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    `;
    document.body.appendChild(win);

    fab.addEventListener("click", () => {
      win.classList.toggle("hidden");
      if (!win.classList.contains("hidden")) {
        document.getElementById("erpi-input").focus();
      }
    });

    document.getElementById("erpi-btn-close").addEventListener("click", () => {
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
      const container = document.getElementById("erpi-messages");
      const msgDiv = document.createElement("div");
      msgDiv.className = `erpi-msg ${role}`;
      msgDiv.innerHTML = formatMarkdown(text);
      container.appendChild(msgDiv);
      container.scrollTop = container.scrollHeight;
    }

    function showTyping() {
      const container = document.getElementById("erpi-messages");
      const typing = document.createElement("div");
      typing.id = "erpi-typing-indicator";
      typing.className = "erpi-typing";
      typing.innerHTML = `<div class="erpi-dot"></div><div class="erpi-dot"></div><div class="erpi-dot"></div>`;
      container.appendChild(typing);
      container.scrollTop = container.scrollHeight;
    }

    function hideTyping() {
      const typing = document.getElementById("erpi-typing-indicator");
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
            mode: "erpi"
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

    const inputEl = document.getElementById("erpi-input");
    const sendBtn = document.getElementById("erpi-btn-send");

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

    document.querySelectorAll(".erpi-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        const msg = pill.getAttribute("data-msg");
        sendMessage(msg);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initERPi);
  } else {
    initERPi();
  }
})();
