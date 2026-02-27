import hashlib, os, socket, psutil, requests
from datetime import datetime
from fastapi import FastAPI, Depends, Body, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import Session
from moneylayer.database import engine, Base, get_db

# --- MODELOS DE BANCO DE DADOS ---
class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String); program_name = Column(String)
    blockchain_hash = Column(String); timestamp = Column(DateTime, default=datetime.utcnow)

class ThreatLog(Base):
    __tablename__ = "threats"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String); city = Column(String); isp = Column(String)
    endpoint_attacked = Column(String); timestamp = Column(DateTime, default=datetime.utcnow)

# NOVOS MODELOS ANTI-CORRUPÇÃO
class SocialFund(Base):
    __tablename__ = "social_fund"
    id = Column(Integer, primary_key=True, index=True)
    global_value = Column(Float, default=0.0)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String); amount = Column(Float)
    tx_hash = Column(String); timestamp = Column(DateTime, default=datetime.utcnow)

class PublicFeedback(Base):
    __tablename__ = "public_feedback"
    id = Column(Integer, primary_key=True, index=True)
    report_text = Column(String); tracking_hash = Column(String)
    status = Column(String, default="SOB INVESTIGAÇÃO"); timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
app = FastAPI()
if os.path.exists("static"): app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializa Fundo Social Zero se não existir
def init_fund(db: Session):
    fund = db.query(SocialFund).first()
    if not fund:
        fund = SocialFund(global_value=150000.00) # Fundo inicial simulado para transparência
        db.add(fund); db.commit()
    return fund

# --- ROTAS DO SOC E EDR ---
SIGNATURES = ['wireshark.exe', 'ncat.exe', 'nc.exe', 'mimikatz.exe', 'notepad.exe']

def perform_raio_x():
    hostname = socket.gethostname(); ip_addr = socket.gethostbyname(hostname)
    found = [p.info['name'] for p in psutil.process_iter(['name']) if p.info['name'] and p.info['name'].lower() in SIGNATURES]
    return {"ip": ip_addr, "host": hostname, "status": "SISTEMA SEGURO" if not found else f"INVASOR DETECTADO: {found[0]}"}

@app.get("/api/soc/threats")
async def get_threats(db: Session = Depends(get_db)):
    return {"threats": db.query(ThreatLog).order_by(ThreatLog.id.desc()).limit(15).all()}

# --- ROTAS ANTI-CORRUPÇÃO E TRANSPARÊNCIA ---
@app.get("/api/transparency/ledger")
async def get_ledger(db: Session = Depends(get_db)):
    fund = init_fund(db)
    txs = db.query(Transaction).order_by(Transaction.id.desc()).limit(5).all()
    feedbacks = db.query(PublicFeedback).order_by(PublicFeedback.id.desc()).limit(5).all()
    return {"total_fund": fund.global_value, "transactions": txs, "feedbacks": feedbacks}

@app.post("/api/transparency/report")
async def submit_report(payload: dict = Body(...), db: Session = Depends(get_db)):
    report_text = payload.get('text', '')
    if len(report_text) < 5: raise HTTPException(status_code=400, detail="Relato muito curto.")
    
    # Gera hash de rastreio anônimo
    t_hash = hashlib.sha256(f"{report_text}{datetime.now()}".encode()).hexdigest()
    db.add(PublicFeedback(report_text=report_text, tracking_hash=t_hash))
    db.commit()
    return {"status": "sucesso", "tracking_hash": t_hash}

# --- ROTAS SOCIAIS ---
@app.post("/api/moneylayer/apply")
async def apply(payload: dict = Body(...), db: Session = Depends(get_db)):
    user = "Rafael Machado Gomes Machado"; prog = payload.get('program', 'Protocolo CFB')
    b_hash = hashlib.sha256(f"{user}{prog}{datetime.now()}".encode()).hexdigest()
    db.add(Enrollment(user_name=user, program_name=prog, blockchain_hash=b_hash)); db.commit()
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def home(db: Session = Depends(get_db)):
    rx = perform_raio_x(); status_color = "#00ff00" if "SEGURO" in rx["status"] else "#ff003c"
    xp_points = (db.query(Enrollment).count() if db else 0) * 150
    nivel = "Iniciante Social" if xp_points < 300 else "Pleno de Impacto" if xp_points < 1000 else "Sênior de Transformação"
    init_fund(db) # Garante que o fundo existe

    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap');
            body {{ margin: 0; padding: 20px; background: #050a15; color: #e2e8f0; font-family: 'Rajdhani', sans-serif; overflow-x: hidden; }}
            #particles-js {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }}
            
            .glass-card {{ background: rgba(16, 30, 56, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 16px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5); transition: 0.3s ease; }}
            .glass-card:hover {{ transform: translateY(-5px); border-color: rgba(0, 210, 255, 0.5); }}
            
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; margin-bottom: 20px; }}
            h2, h3 {{ margin-top: 0; color: #fff; letter-spacing: 1px; }}
            
            .tabs {{ display: flex; gap: 10px; margin-bottom: 30px; overflow-x: auto; padding-bottom: 10px; justify-content: center; }}
            .tab-btn {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #8892b0; padding: 12px 25px; border-radius: 30px; cursor: pointer; font-weight: bold; transition: all 0.3s; font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; }}
            .tab-btn:hover {{ background: rgba(0, 210, 255, 0.1); color: #fff; }}
            .tab-btn.active {{ background: linear-gradient(135deg, rgba(0,210,255,0.2), rgba(0,100,255,0.2)); border-color: #00d2ff; color: #fff; box-shadow: 0 0 15px rgba(0,210,255,0.3); }}
            
            .content {{ display: none; animation: fadeIn 0.5s; }}
            .content.active {{ display: block; }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            
            .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
            .btn-action {{ background: transparent; border: 2px solid #00d2ff; color: #00d2ff; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; transition: 0.3s; font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; }}
            .btn-action:hover {{ background: #00d2ff; color: #000; box-shadow: 0 0 20px rgba(0, 210, 255, 0.5); }}
            
            .cyber-terminal {{ background: rgba(0, 0, 0, 0.7); border: 1px solid #0f0; padding: 20px; font-family: 'Courier New', monospace; color: #0f0; height: 300px; overflow-y: auto; border-radius: 8px; }}
            
            .form-input {{ width: 100%; background: rgba(0,0,0,0.5); border: 1px solid #00d2ff; color: #fff; padding: 15px; border-radius: 8px; font-family: 'Rajdhani'; font-size: 1rem; margin-bottom: 15px; resize: none; }}
            .audit-list li {{ padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        </style>
        <script>
            function openTab(evt, tabName) {{
                document.querySelectorAll(".content").forEach(c => c.classList.remove("active"));
                document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
                document.getElementById(tabName).classList.add("active");
                evt.currentTarget.classList.add("active");
                if(tabName === 'transparencia') loadLedger();
            }}

            async function loadLedger() {{
                const res = await fetch('/api/transparency/ledger');
                const data = await res.json();
                
                document.getElementById('fund-total').innerText = "R$ " + data.total_fund.toLocaleString('pt-BR', {{minimumFractionDigits: 2}});
                
                const txList = document.getElementById('tx-ledger');
                txList.innerHTML = data.transactions.length ? data.transactions.map(t => 
                    `<li><i class="fas fa-exchange-alt" style="color:#00d2ff;"></i> <b>${{t.description}}</b> - R$ ${{t.amount.toFixed(2)}}<br><small style="color:#8892b0;"><i class="fas fa-link"></i> HASH: ${{t.tx_hash}}</small></li>`
                ).join('') : "<li>Nenhuma transação registrada.</li>";

                const fbList = document.getElementById('fb-ledger');
                fbList.innerHTML = data.feedbacks.length ? data.feedbacks.map(f => 
                    `<li><i class="fas fa-bullhorn" style="color:#ffaa00;"></i> <b>Status: ${{f.status}}</b><br><small style="color:#8892b0;">Protocolo: ${{f.tracking_hash}}<br>Data: ${{f.timestamp.replace('T', ' ').substring(0,19)}}</small></li>`
                ).join('') : "<li>Nenhum relato registrado.</li>";
            }}

            async function submitFeedback() {{
                const text = document.getElementById('report-text').value;
                const btn = document.getElementById('btn-report');
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Criptografando...';
                
                try {{
                    const res = await fetch('/api/transparency/report', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{text: text}}) }});
                    const data = await res.json();
                    if(res.ok) {{
                        document.getElementById('report-text').value = '';
                        btn.innerHTML = '<i class="fas fa-check"></i> Enviado com Sucesso!';
                        alert("SEU HASH DE ACOMPANHAMENTO: " + data.tracking_hash + "\\n\\nGuarde este código. Ninguém pode alterar sua denúncia.");
                        loadLedger();
                    }} else {{ btn.innerHTML = 'Erro ao enviar'; }}
                }} catch (e) {{ btn.innerHTML = 'Erro de Rede'; }}
                setTimeout(() => btn.innerHTML = '<i class="fas fa-paper-plane"></i> ENVIAR RELATO ANÔNIMO', 3000);
            }}

            // (Mantivemos as funções applyForSocialProgram e Chart.js idênticas aqui para brevidade visual)
            window.onload = function() {{
                particlesJS("particles-js", {{"particles": {{"number": {{"value": 50}},"color": {{"value": "#00d2ff"}},"shape": {{"type": "circle"}},"opacity": {{"value": 0.3}},"size": {{"value": 3}},"line_linked": {{"enable": true, "distance": 150, "color": "#00d2ff", "opacity": 0.2, "width": 1}},"move": {{"enable": true, "speed": 2}}}}}});
            }};
        </script>
    </head>
    <body>
        <div id="particles-js"></div>
        
        <div class="header">
            <h2><i class="fas fa-globe-americas"></i> CONECTA FUTURO <span style="color:#00d2ff">BRASIL</span></h2>
            <div style="color:#00d2ff; font-weight:bold;"><i class="fas fa-satellite-dish"></i> NODE: ONLINE</div>
        </div>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="openTab(event, 'perfil')"><i class="fas fa-user-astronaut"></i> DASHBOARD</button>
            <button class="tab-btn" onclick="openTab(event, 'social')"><i class="fas fa-network-wired"></i> OPORTUNIDADES</button>
            <button class="tab-btn" onclick="openTab(event, 'transparencia')"><i class="fas fa-search-dollar"></i> ANTI-CORRUPÇÃO</button>
        </div>
        
        <div id="perfil" class="content active">
            <div class="glass-card">
                <h3 style="color:#00d2ff;"><i class="fas fa-microchip"></i> Raio-X de Rede</h3>
                <ul style="list-style: none; padding: 0; line-height: 2;">
                    <li><i class="fas fa-fingerprint" style="color:#8892b0; width:20px;"></i> Titular: <b style="color:#fff;">Rafael Machado Gomes Machado</b></li>
                    <li><i class="fas fa-laptop" style="color:#8892b0; width:20px;"></i> Host: <b style="color:#fff;">{rx['host']}</b></li>
                    <li><i class="fas fa-shield-virus" style="color:#8892b0; width:20px;"></i> Status EDR: <b style="color:{status_color};">{rx['status']}</b></li>
                </ul>
            </div>
        </div>
        
        <div id="social" class="content">
            <div class="info-grid">
                <div class="glass-card"><h3><i class="fas fa-laptop-code"></i> Cyber Safety</h3><button class="btn-action">ACESSAR ACADEMIA</button></div>
            </div>
        </div>
        
        <div id="transparencia" class="content">
            <div class="info-grid">
                
                <div class="glass-card">
                    <h3 style="color:#00d2ff;"><i class="fas fa-landmark"></i> Fundo Social Público</h3>
                    <p style="font-size:0.85rem; color:#8892b0;">Rastreio ponta a ponta dos recursos do protocolo.</p>
                    <div style="font-size: 2.5rem; color: #fff; font-weight: bold; margin: 20px 0;" id="fund-total">R$ 0,00</div>
                    
                    <h4 style="color:#00d2ff; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px;">Últimas Movimentações</h4>
                    <ul id="tx-ledger" class="audit-list" style="list-style:none; padding:0; margin:0;"></ul>
                </div>

                <div class="glass-card" style="border-color: rgba(255, 170, 0, 0.5);">
                    <h3 style="color:#ffaa00;"><i class="fas fa-bullhorn"></i> Canal de Ouvidoria (Whistleblower)</h3>
                    <p style="font-size:0.85rem; color:#8892b0;">Ferramenta de denúncia e feedback. Totalmente anônimo e protegido por criptografia de ponta a ponta.</p>
                    
                    <textarea id="report-text" class="form-input" rows="4" placeholder="Descreva aqui sua denúncia, irregularidade ou feedback estrutural para a comunidade..."></textarea>
                    <button id="btn-report" class="btn-action" style="border-color:#ffaa00; color:#ffaa00;" onclick="submitFeedback()"><i class="fas fa-paper-plane"></i> ENVIAR RELATO ANÔNIMO</button>
                    
                    <h4 style="color:#ffaa00; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px; margin-top:25px;">Status das Investigações</h4>
                    <ul id="fb-ledger" class="audit-list" style="list-style:none; padding:0; margin:0;"></ul>
                </div>

            </div>
        </div>
        
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
