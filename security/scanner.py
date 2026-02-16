from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sys
import os
from dotenv import load_dotenv

# --- FASE 1: AMBIENTE E AUTOSSUFICIÊNCIA ---
load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Gatilho de Instalação: Verifica drivers antes de iniciar a interface
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
    def get_defense_stats(): return {"bloqueios": 0, "limpezas": 0, "origens": []}
    def scan_system(): return {"risk_level": "Erro"}
    def check_vpn_status(): return "Aguardando"
    def create_vpn_config(): return {"status": "error"}
    def toggle_tunnel(action): return False

app = FastAPI(title="TheOrbeSystems - Zero Trust Edition")

# --- ROTAS DA API ---

@app.get("/api/security/stats")
async def api_stats():
    return get_defense_stats()

@app.post("/api/security/scan")
async def run_scan():
    return scan_system()

@app.get("/api/security/logs")
async def get_logs():
    log_path = "logs/security_events.log"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            return {"logs": f.readlines()[-15:][::-1]}
    return {"logs": ["Aguardando monitoramento..."]}

@app.post("/api/vpn/configure")
async def vpn_config():
    """FASE 2: Gera e ATIVA o túnel via CLI automaticamente"""
    result = create_vpn_config()
    if result.get("status") == "configured":
        if toggle_tunnel("activate"):
            result["message"] = "VPN Ativada! Túnel blindado com sucesso."
        else:
            result["message"] = "Erro: Execute como ADMINISTRADOR para ativar a VPN."
    return result

@app.get("/api/moneylayer/access")
async def check_access():
    """FASE 3: Valida o Cadeado de Interesse Social"""
    vpn_active = check_vpn_status() == "Configurado"
    security = scan_system()
    risk = security.get("risk_level", "Erro")
    
    if vpn_active and "CRÍTICO" not in risk:
        return {"access": "granted"}
    
    reasons = []
    if not vpn_active: reasons.append("VPN Desativada")
    if "CRÍTICO" in risk: reasons.append("Ameaça Detectada")
    return {"access": "denied", "reasons": reasons}

# --- INTERFACE DASHBOARD ---

@app.get("/", response_class=HTMLResponse)
async def home():
    vpn_status = check_vpn_status()
    vpn_color = "#2ecc71" if vpn_status == "Configurado" else "#f39c12"
    
    # O HTML completo está abaixo, integrado para facilitar a cópia
    return render_dashboard(vpn_status, vpn_color)

def render_dashboard(vpn_status, vpn_color):
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
            .btn {{ padding: 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: #fff; transition: 0.3s; text-transform: uppercase; display: flex; align-items: center; justify-content: center; }}
            .btn-report {{ background: #27ae60; width: 100%; margin-top: 15px; }}
            .btn-vpn {{ background: #2c3e50; }}
            .btn-scan {{ background: #c0392b; }}
            .btn-money {{ background: #555; cursor: not-allowed; }}
            .btn:hover {{ filter: brightness(1.2); transform: scale(1.02); }}
            #console {{ background: #000; color: #0f0; padding: 20px; border-radius: 10px; margin-top: 20px; font-family: monospace; height: 250px; overflow-y: auto; border-left: 5px solid #00d2ff; white-space: pre-wrap; }}
            .stats-box {{ background: #1a1a1a; padding: 15px; border-radius: 10px; margin-top: 15px; border: 1px solid #333; }}
        </style>
        
        <script>
            // COLOQUE O SCRIPT AQUI (VEJA ABAIXO)
            {script_content}
        </script>

    </head>
    <body>
        <div class="container">
            <h1>THEORBESYSTEMS</h1>
            <p style="text-align:center; color:#666;">Protocolo Conecta Futuro Brasil | Inteligência Ativa</p>
            
            <div class="grid">
                <button class="btn btn-scan" onclick="scan()">🛡️ Auditoria Zero</button>
                <button class="btn btn-vpn" onclick="configVPN()">🔑 Ativar Túnel VPN</button>
                <button id="btn-money" class="btn btn-money" onclick="accessMoneyLayer()">🔒 MoneyLayer Bloqueado</button>
            </div>
            
            <button class="btn btn-report" onclick="showReport()">📊 Gerar Relatório de Eficácia</button>
            <div id="console"> > Sistema em prontidão.</div>
            
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

# Injeção do Script para manter o main.py limpo
script_content = """
    async function updateLogs() {
        try {
            const res = await fetch('/api/security/logs');
            const data = await res.json();
            document.getElementById('console').innerHTML = "<strong>📜 MONITORAMENTO EM TEMPO REAL:</strong>\\n" + data.logs.join("");
        } catch (e) { console.error("Erro nos logs"); }
    }

    async function updateLockStatus() {
        const res = await fetch('/api/moneylayer/access');
        const data = await res.json();
        const btn = document.getElementById('btn-money');
        if (data.access === "granted") {
            btn.style.background = "#00d2ff";
            btn.style.cursor = "pointer";
            btn.innerHTML = "🔓 Acessar MoneyLayer";
        } else {
            btn.style.background = "#555";
            btn.style.cursor = "not-allowed";
            btn.innerHTML = "🔒 MoneyLayer Bloqueado";
        }
    }

    async function scan() {
        document.getElementById('console').innerHTML = " > [SYSTEM]: Executando Varredura...\\n";
        const res = await fetch('/api/security/scan', { method: 'POST' });
        const data = await res.json();
        if(data.risk_level.includes("CRÍTICO")) alert("🚨 DEFESA ATIVA!");
        updateLogs();
        updateLockStatus();
    }

    async function configVPN() {
        const res = await fetch('/api/vpn/configure', { method: 'POST' });
        const data = await res.json();
        alert(data.message);
        location.reload();
    }

    async function accessMoneyLayer() {
        const res = await fetch('/api/moneylayer/access');
        const data = await res.json();
        if (data.access === "granted") {
            alert("💰 Bem-vindo ao MoneyLayer 2.0! Projeto: Ativo | Interesse Social: Garantido.");
        } else {
            alert("🚨 BLOQUEIO: " + data.reasons.join(" e "));
        }
    }

    setInterval(updateLogs, 5000);
    setInterval(updateLockStatus, 5000);
    window.onload = () => { updateLogs(); updateLockStatus(); };
"""

# Corrige o retorno da string formatada
@app.get("/", response_class=HTMLResponse)
async def home_final():
    vpn_status = check_vpn_status()
    vpn_color = "#2ecc71" if vpn_status == "Configurado" else "#f39c12"
    return HTMLResponse(content=render_dashboard(vpn_status, vpn_color).replace("{script_content}", script_content))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)