import hashlib, os, socket, psutil, requests
from datetime import datetime
from fastapi import FastAPI, Depends, Body, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session
from moneylayer.database import engine, Base, get_db

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

Base.metadata.create_all(bind=engine)
app = FastAPI()
if os.path.exists("static"): app.mount("/static", StaticFiles(directory="static"), name="static")

def get_geoip(ip):
    try:
        if ip == "127.0.0.1" or ip.startswith("192.168"): ip = "8.8.8.8"
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        return res.get("city", "Desconhecido"), res.get("isp", "Desconhecido")
    except: return "Desconhecido", "Desconhecido"

SIGNATURES = ['wireshark.exe', 'ncat.exe', 'nc.exe', 'mimikatz.exe', 'notepad.exe']

def perform_raio_x():
    hostname = socket.gethostname(); ip_addr = socket.gethostbyname(hostname)
    found = [p.info['name'] for p in psutil.process_iter(['name']) if p.info['name'] and p.info['name'].lower() in SIGNATURES]
    return {"ip": ip_addr, "host": hostname, "status": "SISTEMA LIMPO E AUDITADO" if not found else f"INVASOR DETECTADO: {found[0]}"}

# --- ARMADILHA HONEYPOT RESTAURADA ---
@app.get("/wp-admin")
@app.get("/.env")
@app.get("/admin/login")
async def honeypot_trap(request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host
    city, isp = get_geoip(client_ip)
    threat = ThreatLog(ip_address=client_ip, city=city, isp=isp, endpoint_attacked=request.url.path)
    db.add(threat); db.commit()
    raise HTTPException(status_code=403, detail="ACESSO NEGADO. SOC REGISTROU O IP.")

# --- EDR (ESPURGAÇÃO) ---
@app.post("/api/soc/purge")
async def purge_malware(db: Session = Depends(get_db)):
    purged_processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process_name = proc.info['name'].lower()
            if process_name in SIGNATURES:
                proc.kill()
                purged_processes.append(process_name)
                threat = ThreatLog(
                    ip_address="127.0.0.1 (Local)", city="Varredura de RAM", isp="EDR Interno",
                    endpoint_attacked=f"Processo Neutralizado: {process_name}"
                )
                db.add(threat)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass 
    db.commit()
    if purged_processes:
        return {"status": "alerta", "message": f"AMEAÇAS ESPURGADAS: {', '.join(purged_processes)}"}
    return {"status": "limpo", "message": "MEMÓRIA RAM LIMPA. NENHUMA AMEAÇA ENCONTRADA."}

@app.get("/api/soc/threats")
async def get_threats(db: Session = Depends(get_db)):
    threats = db.query(ThreatLog).order_by(ThreatLog.id.desc()).limit(15).all()
    return {"threats": threats}

@app.post("/api/moneylayer/apply")
async def apply(payload: dict = Body(...), db: Session = Depends(get_db)):
    user = "Rafael Machado Gomes Machado"; prog = payload.get('program', 'Protocolo CFB')
    b_hash = hashlib.sha256(f"{user}{prog}{datetime.now()}".encode()).hexdigest()
    db.add(Enrollment(user_name=user, program_name=prog, blockchain_hash=b_hash)); db.commit()
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def home(db: Session = Depends(get_db)):
    rx = perform_raio_x(); status_color = "#00ff00" if "LIMPO" in rx["status"] else "#ff0055"
    xp_points = (db.query(Enrollment).count() if db else 0) * 150
    nivel = "Iniciante Social" if xp_points < 300 else "Pleno de Impacto" if xp_points < 1000 else "Sênior de Transformação"

    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="/static/css/style.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <script src="/static/js/dashboard.js"></script>
        <style>
            .cyber-terminal {{ background: #000; border: 1px solid #0f0; padding: 20px; font-family: 'Courier New', monospace; color: #0f0; height: 300px; overflow-y: auto; text-shadow: 0 0 5px #0f0; }}
            .cyber-alert {{ color: #ff003c; text-shadow: 0 0 5px #ff003c; font-weight: bold; }}
            .cyber-btn {{ background: transparent; border: 1px solid #0f0; color: #0f0; padding: 10px; cursor: pointer; text-transform: uppercase; font-weight: bold; transition: 0.3s; width: 100%; margin-bottom: 10px; }}
            .cyber-btn:hover {{ background: #0f0; color: #000; box-shadow: 0 0 15px #0f0; }}
            .cyber-btn-danger {{ border-color: #ff003c; color: #ff003c; }}
            .cyber-btn-danger:hover {{ background: #ff003c; color: #000; box-shadow: 0 0 15px #ff003c; }}
        </style>
        <script>
            async function loadThreats() {{
                const res = await fetch('/api/soc/threats');
                const data = await res.json();
                const term = document.getElementById('cyber-radar');
                if(data.threats.length === 0) {{
                    term.innerHTML = "> MONITORAÇÃO ATIVA... NENHUMA INTRUSÃO DETECTADA.<br><span class='cyber-alert'>> AGUARDANDO TENTATIVAS DE CONEXÃO...</span>";
                    return;
                }}
                term.innerHTML = data.threats.map(t => 
                    `> [<span class="${{t.isp === 'EDR Interno' ? 'cyber-alert' : 'cyber-alert'}}">${{t.isp === 'EDR Interno' ? 'PROCESSO DESTRUÍDO' : 'INTRUSÃO BLOQUEADA'}}</span>] Data: ${{t.timestamp.replace('T', ' ').substring(0,19)}}<br>` +
                    `> ALVO: ${{t.endpoint_attacked}} | ORIGEM: ${{t.ip_address}}<br>` +
                    `> STATUS: <span style="color:#0f0">NEUTRALIZADO COM SUCESSO</span><br>---<br>`
                ).join('');
            }}
            
            async function runEDR() {{
                const term = document.getElementById('cyber-radar');
                term.innerHTML = "> INICIANDO VARREDURA DE MEMÓRIA RAM...<br>> PROCURANDO ROOTKITS E MALWARES...<br><i class='fas fa-circle-notch fa-spin'></i>";
                
                const res = await fetch('/api/soc/purge', {{ method: 'POST' }});
                const data = await res.json();
                
                setTimeout(() => {{
                    if(data.status === 'alerta') {{
                        term.innerHTML = `<span class="cyber-alert">> ALERTA CRÍTICO: ${{data.message}}</span><br>> APLICANDO PROTOCOLO DE ESPURGAÇÃO... FEITO.`;
                        setTimeout(loadThreats, 2000);
                    }} else {{
                        term.innerHTML = `> ${{data.message}}<br>> SISTEMA SEGURO.`;
                        setTimeout(loadThreats, 2000);
                    }}
                }}, 1500);
            }}
            
            async function simulateAttack() {{
                const term = document.getElementById('cyber-radar');
                term.innerHTML = "> ALERTA: TENTATIVA DE INVASÃO EXTERNA DETECTADA!<br>> RASTREANDO IP E GEOLOCALIZAÇÃO...<br><i class='fas fa-circle-notch fa-spin'></i>";
                try {{ await fetch('/wp-admin'); }} catch(e) {{}}
                setTimeout(loadThreats, 1500);
            }}
        </script>
    </head>
    <body onload="loadThreats()">
        <div class="header">
            <h2><i class="fas fa-globe-americas"></i> CONECTA FUTURO <span style="color:#00d2ff">BRASIL</span></h2>
        </div>
        <div class="tabs" style="overflow-x: auto; white-space: nowrap;">
            <button class="tab-btn active" onclick="openTab(event, 'perfil')">PERFIL</button>
            <button class="tab-btn" onclick="openTab(event, 'social')">OPORTUNIDADES</button>
            <button class="tab-btn" onclick="openTab(event, 'soc')"><i class="fas fa-crosshairs"></i> SOC (DEFESA)</button>
        </div>
        
        <div id="perfil" class="content active">
            <div class="card">
                <h3><i class="fas fa-rocket"></i> Nível: {nivel} ({xp_points} XP)</h3>
                <hr>
                <p>IP Local: <b style="color:#fff">{rx['ip']}</b> | Status: <b style="color:{status_color}">{rx['status']}</b></p>
            </div>
        </div>
        
        <div id="social" class="content">
            <div class="info-grid">
                <div class="card">
                    <h3><i class="fas fa-laptop-code"></i> Formação Cyber Safety</h3>
                    <p style="font-size:0.85rem; color:#8892b0;">Acervo real de cursos da Cisco.</p>
                    <button class="btn-action" onclick="applyForSocialProgram('Cisco Cyber Safety', 'https://skillsforall.com/', this)"><i class="fas fa-external-link-alt"></i> ACESSAR ACADEMIA</button>
                </div>
                <div class="card">
                    <h3><i class="fas fa-briefcase"></i> Vagas de Tecnologia</h3>
                    <p style="font-size:0.85rem; color:#8892b0;">Busca em tempo real no LinkedIn.</p>
                    <button class="btn-action" onclick="applyForSocialProgram('Vagas Tech Brasil', 'https://www.linkedin.com/jobs/search/?keywords=tecnologia', this)"><i class="fas fa-external-link-alt"></i> BUSCAR NO LINKEDIN</button>
                </div>
                <div class="card">
                    <h3><i class="fas fa-house-user"></i> Programas de Moradia</h3>
                    <p style="font-size:0.85rem; color:#8892b0;">Acesso direto ao portal do Governo.</p>
                    <button class="btn-action" onclick="applyForSocialProgram('Habitação Gov.br', 'https://www.gov.br/mdr/pt-br/assuntos/habitacao', this)"><i class="fas fa-external-link-alt"></i> ACESSAR PORTAL GOV</button>
                </div>
            </div>
        </div>
        
        <div id="soc" class="content">
            <div class="card" style="background:#050505; border-color:#0f0;">
                <h3 style="color:#0f0; font-family:'Courier New';"><i class="fas fa-radar"></i> CENTRO DE OPERAÇÕES DE SEGURANÇA (SOC)</h3>
                
                <button class="cyber-btn cyber-btn-danger" onclick="runEDR()"><i class="fas fa-skull-crossbones"></i> INICIAR VARREDURA E ESPURGAÇÃO (EDR)</button>
                <button class="cyber-btn" onclick="simulateAttack()"><i class="fas fa-biohazard"></i> SIMULAR ATAQUE DE HONEYPOT</button>
                
                <div id="cyber-radar" class="cyber-terminal">
                    > CARREGANDO TERMINAL DE DEFESA...
                </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
