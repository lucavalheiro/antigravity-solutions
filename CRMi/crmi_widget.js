(function() {
  const path = window.location.pathname.toLowerCase();
  if (!path.startsWith('/crm')) return;
  if (window.__crmi_widget_loaded) return;
  
  function initCRMi() {
    const curPath = window.location.pathname.toLowerCase();
    if (!curPath.startsWith('/crm')) return;
    if (window.__crmi_widget_loaded) return;
    if (!document.body) {
      setTimeout(initCRMi, 50);
      return;
    }
    window.__crmi_widget_loaded = true;

    // Remover qualquer widget antigo se existir
    const oldFab = document.getElementById("luciano-ai-fab");
    if (oldFab) oldFab.remove();
    const oldWin = document.getElementById("luciano-ai-window");
    if (oldWin) oldWin.remove();
    const erpiFab = document.getElementById("erpi-ai-fab");
    if (erpiFab) erpiFab.remove();
    const erpiWin = document.getElementById("erpi-ai-window");
    if (erpiWin) erpiWin.remove();

    // Injetar estilos CSS exclusivos do CRMi
    const style = document.createElement("style");
    style.id = "crmi-ai-style";
    style.innerHTML = `
      #crmi-ai-fab {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 999999;
        display: flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 50px;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.45), 0 2px 6px rgba(0,0,0,0.25);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 14px;
        font-weight: 700;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        user-select: none;
        border: 1px solid rgba(255, 255, 255, 0.35);
      }
      #crmi-ai-fab:hover {
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 12px 28px rgba(124, 58, 237, 0.55), 0 4px 10px rgba(0,0,0,0.35);
      }
      #crmi-ai-fab .fab-icon {
        width: 22px;
        height: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      #crmi-ai-fab .fab-badge {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
      }

      /* Janela de Chat do CRMi */
      #crmi-ai-window {
        position: fixed;
        bottom: 84px;
        right: 24px;
        width: 440px;
        height: 600px;
        max-width: calc(100vw - 32px);
        max-height: calc(100vh - 100px);
        background: #121216;
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
      #crmi-ai-window.hidden {
        opacity: 0;
        transform: scale(0.92) translateY(15px);
        pointer-events: none;
      }

      /* Header */
      .crmi-header {
        padding: 14px 16px;
        background: #191822;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .crmi-header-info {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .crmi-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(124, 58, 237, 0.4);
        background: #000;
        border: 1px solid rgba(255, 255, 255, 0.2);
      }
      .crmi-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
      }
      .crmi-header-text h4 {
        margin: 0;
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .crmi-header-text p {
        margin: 0;
        font-size: 11px;
        color: #a78bfa;
        display: flex;
        align-items: center;
        gap: 4px;
        font-weight: 500;
      }
      .crmi-header-actions button {
        background: transparent;
        border: none;
        color: #a1a1aa;
        cursor: pointer;
        font-size: 16px;
        padding: 4px 6px;
        border-radius: 6px;
        transition: background 0.15s;
      }
      .crmi-header-actions button:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
      }

      /* Sugestões Rápidas */
      .crmi-pills {
        padding: 8px 12px;
        display: flex;
        gap: 6px;
        overflow-x: auto;
        background: #15141d;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        scrollbar-width: none;
      }
      .crmi-pills::-webkit-scrollbar { display: none; }
      .crmi-pill {
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
      .crmi-pill:hover {
        background: #7c3aed;
        color: #fff;
        border-color: #7c3aed;
      }

      /* Mensagens */
      .crmi-body {
        flex: 1;
        padding: 14px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      .crmi-msg {
        max-width: 90%;
        padding: 10px 14px;
        border-radius: 14px;
        font-size: 13px;
        line-height: 1.5;
        word-break: break-word;
      }
      .crmi-msg.assistant {
        align-self: flex-start;
        background: #1e1d28;
        color: #f4f4f5;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-bottom-left-radius: 4px;
      }
      .crmi-msg.user {
        align-self: flex-end;
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: #ffffff;
        border-bottom-right-radius: 4px;
      }
      .crmi-msg p { margin: 0 0 6px 0; }
      .crmi-msg p:last-child { margin: 0; }
      .crmi-msg strong { color: #fff; }
      .crmi-msg code {
        background: rgba(0, 0, 0, 0.4);
        padding: 2px 5px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
        color: #c084fc;
      }

      /* Indicador de Digitação */
      .crmi-typing {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 8px 12px;
        background: #1e1d28;
        border-radius: 12px;
        width: fit-content;
        align-self: flex-start;
      }
      .crmi-dot {
        width: 6px;
        height: 6px;
        background: #c084fc;
        border-radius: 50%;
        animation: crmiPulse 1.2s infinite ease-in-out;
      }
      .crmi-dot:nth-child(2) { animation-delay: 0.2s; }
      .crmi-dot:nth-child(3) { animation-delay: 0.4s; }
      @keyframes crmiPulse {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
      }

      /* Input Footer */
      .crmi-footer {
        padding: 12px;
        background: #191822;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        gap: 8px;
      }
      .crmi-footer input {
        flex: 1;
        background: #232230;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px 14px;
        color: #fff;
        font-size: 13px;
        outline: none;
        transition: border-color 0.2s;
      }
      .crmi-footer input:focus {
        border-color: #7c3aed;
      }
      .crmi-footer button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
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
      .crmi-footer button:hover {
        opacity: 0.9;
      }
    `;
    document.head.appendChild(style);

    // Botão FAB do CRMi
    const fab = document.createElement("div");
    fab.id = "crmi-ai-fab";
    fab.innerHTML = `
      <div class="fab-icon">
        <img src="/assets/crm/images/watsonx_logo.jpg" alt="watsonx" style="width: 22px; height: 22px; border-radius: 50%; object-fit: cover; display: block;" />
      </div>
      <span>CRMi</span>
      <div class="fab-badge"></div>
    `;
    document.body.appendChild(fab);

    // Janela de Chat do CRMi
    const win = document.createElement("div");
    win.id = "crmi-ai-window";
    win.className = "hidden";
    win.innerHTML = `
      <div class="crmi-header">
        <div class="crmi-header-info">
          <div class="crmi-avatar"><img src="/assets/crm/images/watsonx_logo.jpg" alt="watsonx" /></div>
          <div class="crmi-header-text">
            <h4>CRMi Copilot <span>✨</span></h4>
            <p><span style="display:inline-block;width:6px;height:6px;background:#10b981;border-radius:50%"></span> Online (Pipeline & Catálogo IBM)</p>
          </div>
        </div>
        <div class="crmi-header-actions">
          <button id="crmi-btn-close" title="Fechar">✕</button>
        </div>
      </div>

      <div class="crmi-pills">
        <div class="crmi-pill" data-msg="Faça um resumo executivo do CRM: quantos leads e oportunidades temos ativos e qual o valor do pipeline?">📊 Pipeline & Leads</div>
        <div class="crmi-pill" data-msg="Mostre os últimos 5 leads cadastrados e seus status.">🔍 Últimos Leads</div>
        <div class="crmi-pill" data-msg="Consulte o part number D003KZX na tabela IBM e informe faixas de desconto.">📦 Catálogo IBM</div>
        <div class="crmi-pill" data-msg="Crie um lead para Carlos Andrade, empresa TechSolutions, email carlos@techsolutions.com">➕ Criar Lead</div>
      </div>

      <div class="crmi-body" id="crmi-messages">
        <div class="crmi-msg assistant">
          Olá! Eu sou o <strong>CRMi</strong>, seu copiloto comercial especializado no <strong>Frappe CRM</strong>.<br><br>
          Posso gerenciar seus leads, oportunidades no pipeline, buscar part numbers e preços na tabela oficial IBM Outubro 2025 (12.353 itens) e automatizar propostas comerciais. Como posso ajudar?
        </div>
      </div>

      <div class="crmi-footer">
        <input type="text" id="crmi-input" placeholder="Pergunte algo ou peça para criar um lead no CRMi..." autocomplete="off">
        <button id="crmi-btn-send" title="Enviar">
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
        document.getElementById("crmi-input").focus();
      }
    });

    document.getElementById("crmi-btn-close").addEventListener("click", () => {
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
      const container = document.getElementById("crmi-messages");
      const msgDiv = document.createElement("div");
      msgDiv.className = `crmi-msg ${role}`;
      msgDiv.innerHTML = formatMarkdown(text);
      container.appendChild(msgDiv);
      container.scrollTop = container.scrollHeight;
    }

    function showTyping() {
      const container = document.getElementById("crmi-messages");
      const typing = document.createElement("div");
      typing.id = "crmi-typing-indicator";
      typing.className = "crmi-typing";
      typing.innerHTML = `<div class="crmi-dot"></div><div class="crmi-dot"></div><div class="crmi-dot"></div>`;
      container.appendChild(typing);
      container.scrollTop = container.scrollHeight;
    }

    function hideTyping() {
      const typing = document.getElementById("crmi-typing-indicator");
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
            mode: "crmi"
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

    const inputEl = document.getElementById("crmi-input");
    const sendBtn = document.getElementById("crmi-btn-send");

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

    document.querySelectorAll(".crmi-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        const msg = pill.getAttribute("data-msg");
        sendMessage(msg);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCRMi);
  } else {
    initCRMi();
  }
})();
