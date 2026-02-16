from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import sys
import os
from dotenv import load_dotenv

# --- FASE 1: CONFIGURAÇÃO E AUTOSSUFICIÊNCIA ---
load_dotenv()

# Adiciona o diretório atual ao path para evitar erros de importação
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Gatilho de Instalação Silenciosa: Verifica drivers antes de abrir o dashboard
try:
    from network.installer import check_and_install_driver
    print(" > [SISTEMA]: Validando infraestrutura de rede...")
    setup_result = check_and_install_driver()
    print(f" > [SETUP]: {setup_result}")
except ImportError:
    print(" > [AVISO]: Módulo network.installer não encontrado.")

# --- IMPORTAÇÃO DOS MÓDULOS DE DEFESA ---
try:
    from security.scanner import scan_system, get_defense_stats
    from network.vpn_manager import create_vpn_config, check_vpn_status, toggle_tunnel
except ImportError:
    # Fallbacks de segurança
    def get_defense_stats(): return {"bloqueios": 0, "limpezas": 0, "origens": []}
    def scan_system(): return {"risk_level": "Erro"}
    def check_vpn_status(): return "Aguardando"
    def create_vpn_config(): return {"status": "error"}
    def toggle_tunnel(action): return False

app = FastAPI(title="TheOrbeSystems - Zero Trust Edition")

# --- CONFIGURAÇÃO DE ARQUIVOS ESTÁTICOS ---
# Permite que o FastAPI sirva o arquivo dashboard.js da pasta static/js
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- ROTAS DA API ---

@app.get("/api/security/stats")
async def api_stats():
    """Retorna estatísticas para o Relatório de Eficácia"""
    return get_defense_stats()

@app.post("/api/security/scan")
async def run_scan():
    """Executa varredura e o protocolo de auto-defesa"""
    return scan_system()

@app.get("/api/security/logs")
async def get_logs():
    """Recupera logs forenses para o console"""
    log_path = "logs/security_events.log"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            return {"logs": f.readlines()[-15:][::-1]}
    return {"logs": ["Aguardando monitoramento..."]}

@app.post("/api/vpn/configure")
async def vpn_config():
    """FASE 2: Gera a configuração e ATIVA o túnel via CLI"""
    result = create_vpn_config()
    if result.get("status") == "configured":
        if toggle_tunnel("activate"):
            result["message"] = "VPN Ativada! Seu túnel está blindado."
        else:
            result["message"] = "Aviso: Execute como ADMINISTRADOR para ativar o túnel."
    return result

@app.get("/api/moneylayer/access")
async def check_access():
    """FASE 3: Lógica do Cadeado de Interesse Social"""
    vpn_active = check_vpn_status() == "Configurado"
    security = scan_system()
    risk = security.get("risk_level", "Erro")
    
    # Validação para liberação do MoneyLayer 2.0 [cite: 2026-01-09]
    if vpn_active and "CRÍTICO" not in risk:
        return {"access": "granted"}
    
    reasons = []
    if not vpn_active: reasons.append("VPN Desativada")
    if "CRÍTICO" in risk: reasons.append("Ameaça na Rede")
    return {"access": "denied", "reasons": reasons}

# --- INTERFACE DASHBOARD ---

@app.get("/", response_class=HTMLResponse)
async def home():
    vpn_status = check_vpn_status()
    vpn_color = "#2ecc71" if vpn_status == "Configurado" else "#f39c12"
    
    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>TheOrbeSystems | Protocolo Zero</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #050505; color: #fff; margin: 0; padding: 20px; }}
            .container {{ max-width: 950px; margin: auto; background: #111; padding: 30px; border-radius: 15px; border: 1px solid #222; box-shadow: 0 0 40px rgba(0,210,255,0.1); }}
            h1 {{ color: #00d2ff; text-align: center; letter-spacing: 5px; text-transform: uppercase; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }}
            .btn {{ padding: 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: #fff; transition: 0.3s; text-transform: uppercase; }}
            .btn-report {{ background: #27ae60; width: 100%; margin-top: 15px; }}
            .btn-vpn {{ background: #2c3e50; }}
            .btn-scan {{ background: #c0392b; }}
            .btn-money {{ background: #555; cursor: not-allowed; }}
            .btn:hover {{ filter: brightness(1.2); transform: scale(1.02); }}
            #console {{ background: #000; color: #0f0; padding: 20px; border-radius: 10px; margin-top: 20px; font-family: monospace; height: 250px; overflow-y: auto; border-left: 5px solid #00d2ff; white-space: pre-wrap; }}
            .stats-box {{ background: #1a1a1a; padding: 15px; border-radius: 10px; margin-top: 15px; border: 1px solid #333; }}
        </style>
        
        <script src="/static/js/dashboard.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>THEORBESYSTEMS</h1>
            <p style="text-align:center; color:#666;">Protocolo Conecta Futuro Brasil | Interesse Social Ativo</p>
            
            <div class="grid">
                <button class="btn btn-scan" onclick="scan()">🛡️ Auditoria Zero</button>
                <button class="btn btn-vpn" onclick="configVPN()">🔑 Ativar Túnel VPN</button>
                <button id="btn-money" class="btn btn-money" onclick="accessMoneyLayer()">🔒 MoneyLayer Bloqueado</button>
            </div>
            
            <button class="btn btn-report" onclick="showReport()">📊 Gerar Relatório de Eficácia</button>
            <div id="console"> > Aguardando inicialização do monitoramento...</div>
            
            <div class="stats-box">
                <div style="display:flex; justify-content: space-around;">
                    <span>VPN: <b style="color:{vpn_color}">{vpn_status}</b></span>
                    <span>Monitoramento: <b style="color:#2ecc71">Ativo</b></span>
                    <span>Meta: <b style="color:#00d2ff">Taxa Zero</b></span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    # Executa o servidor local na porta 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)