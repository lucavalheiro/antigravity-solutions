# BobQ: Laboratório Quântico no Windows com IBM Bob

Ambiente local para desenvolvimento e simulação de circuitos quânticos combinando **IBM Bob**, **Qiskit 2.x** e **Qiskit Aer**.

## 🚀 Como Executar no Windows (PowerShell)

1. Ative o ambiente virtual:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. Execute os testes:
   ```powershell
   # Teste 1: Emaranhamento Quântico (Estado de Bell)
   python test_bell.py

   # Teste 2: Otimização Logística (QAOA)
   python test_qaoa_logistics.py

   # Teste 3: Seleção de Portfólio (com gráfico PNG)
   python poc_portfolio_optimization.py
   ```

3. Usar o IBM Bob localmente:
   ```powershell
   bob chat
   ```

## 🌐 Acesso ao Frontend Web no Ubuntu
O dashboard gráfico web continua ativo no servidor da rede:
👉 **http://192.168.173.22:8080**
