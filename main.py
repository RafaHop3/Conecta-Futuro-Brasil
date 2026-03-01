from fastapi import FastAPI, Body, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn, socket, hashlib, json, urllib.request, time
from datetime import datetime

# SOC: Honeypot & Defesa Ativa
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
BANNED = set()
TRAPS = list(("/.env", "/wp-admin", "/admin", "/docs", "/redoc", "/openapi.json"))

def get_ip(req):
    try:
        f = req.headers.get("x-forwarded-for")
        if f: return str(f).split(",").strip()
        return req.client.host if req.client else "127.0.0.1"
    except: return "127.0.0.1"

@app.middleware("http")
async def security_layer(req: Request, call_next):
    ip = get_ip(req)
    if ip in BANNED or any(t in req.url.path for t in TRAPS):
        BANNED.add(ip)
        print(f"\n[!!!] BLOQUEIO SOC: {ip} BANIDO")
        return JSONResponse(status_code=403, content={"SOC": "BLOCK_IP"})
    res = await call_next(req)
    res.headers["X-Project"] = "CFB-Elite-V13"
    return res

@app.post("/api/osint/scan")
async def run_osint(payload = Body(...)):
    raw = payload.get("target", "")
    t = raw.replace("https://", "").replace("http://", "").split("/").split(":")
    logs = [f"> [SCAN] Infiltrando em: {t}"]
    try:
        ip = socket.gethostbyname(t)
        logs.append(f"> [DNS] IP Identificado: {ip}")
        try:
            with urllib.request.urlopen(f"http://ip-api.com/json/{ip}", timeout=3) as r:
                d = json.loads(r.read().decode())
                if d.get("status") == "success":
                    logs.append(f"> [GEO] {d.get('city')}, {d.get('country')} | {d.get('isp')}")
        except: pass
        for p in list((22, 80, 443, 3389)):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(0.3)
            if s.connect_ex((ip, p)) == 0: logs.append(f"> [PORTA] {p} ATIVA")
            s.close()
    except: logs.append("> [ALERTA] Alvo Blindado ou Offline.")
    return {"status": "success", "logs": logs}

@app.post("/api/social/cep")
async def get_cep(payload = Body(...)):
    cep = payload.get("cep", "").replace("-", "")
    try:
        with urllib.request.urlopen(f"https://brasilapi.com.br/api/cep/v1/{cep}", timeout=3) as r:
            return json.loads(r.read().decode())
    except: return {"error": "CEP Inválido"}

@app.post("/api/finance/pix")
async def gen_pix(req: Request, payload = Body(...)):
    val = payload.get("amount", 0); ip = get_ip(req)
    h = hashlib.sha256(f"{val}{ip}{time.time()}".encode()).hexdigest()[:16]
    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=PIX_{h}"
    return {"status": "success", "hash": h, "qr": qr, "ip": ip}

html = """
<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CONECTA FUTURO BRASIL - PRO</title><link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<style>
:root { --neon: #00d2ff; --bg: #030712; --panel: rgba(16, 20, 28, 0.95); }
body { background: var(--bg); color: #fff; font-family: 'Courier New', monospace; margin: 0; overflow-x: hidden; }
canvas { position: fixed; top: 0; left: 0; z-index: -1; width: 100%; height: 100%; opacity: 0.4; }
.container { max-width: 900px; margin: 20px auto; padding: 20px; position: relative; z-index: 1; }
.hud { text-align: center; border: 1px solid var(--neon); padding: 10px; margin-bottom: 20px; box-shadow: 0 0 15px var(--neon); text-transform: uppercase; font-weight: bold; }
.tabs { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; justify-content: center; }
.tab-btn { flex: 1 1 18%; background: #111827; border: 1px solid #374151; color: #9ca3af; padding: 12px; cursor: pointer; border-radius: 4px; font-weight: bold; font-size: 0.7rem; transition: 0.3s; }
.tab-btn.active { color: var(--neon); border-color: var(--neon); background: rgba(0, 210, 255, 0.15); box-shadow: 0 0 10px var(--neon); }
.content { display: none; background: var(--panel); border: 1px solid var(--neon); padding: 20px; border-radius: 8px; animation: slideIn 0.3s ease-out; }
@keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
input { width: 100%; padding: 12px; background: #000; border: 1px solid #333; color: var(--neon); margin-bottom: 15px; box-sizing: border-box; font-size: 1rem; }
button.main-btn { background: var(--neon); color: #000; border: none; padding: 12px; width: 100%; font-weight: bold; cursor: pointer; text-transform: uppercase; border-radius: 4px; }
.card { border-left: 4px solid var(--neon); background: rgba(255,255,255,0.03); padding: 15px; margin-bottom: 15px; }
pre { background: #000; padding: 15px; color: #00ff00; font-size: 0.85rem; border: 1px solid #1f2937; overflow-x: auto; line-height: 1.5; }
</style></head>
<body><canvas id="bg"></canvas><div class="container">
<div class="hud">OPERADOR [SOC ATIVO] | CFB V13 CORE</div>
<div class="tabs">
    <button class="tab-btn active" onclick="nav('osint', this, '#00d2ff')">OSINT</button>
    <button class="tab-btn" onclick="nav('edu', this, '#a855f7')">CURSOS</button>
    <button class="tab-btn" onclick="nav('jobs', this, '#22c55e')">VAGAS</button>
    <button class="tab-btn" onclick="nav('hab', this, '#f59e0b')">MORADIA</button>
    <button class="tab-btn" onclick="nav('fundo', this, '#ef4444')">FUNDO</button>
</div>
<div id="osint" class="content" style="display:block;"><h3><i class="fas fa-radar"></i> RASTREAMENTO PROFUNDO</h3><input type="text" id="target" placeholder="Site ou IP"><button class="main-btn" onclick="scan()">EXECUTAR ESPURGAÇÃO</button><pre id="out">AGUARDANDO COMANDO...</pre></div>
<div id="edu" class="content"><h3><i class="fas fa-graduation-cap"></i> CAPACITAÇÃO</h3><div class="card"><h4>Cyber Security Essentials (Cisco)</h4><button class="main-btn" onclick="window.open('https://skillsforall.com','_blank')">ACESSAR ACADEMIA</button></div></div>
<div id="jobs" class="content"><h3><i class="fas fa-briefcase"></i> OPORTUNIDADES</h3><div class="card"><h4>Portal Gupy - Rastrear Vagas</h4><button class="main-btn" onclick="window.open('https://portal.gupy.io/','_blank')">RASTREAR</button></div></div>
<div id="hab" class="content"><h3><i class="fas fa-home"></i> HABITAÇÃO SOCIAL</h3><input type="text" id="cep_in" placeholder="Digite seu CEP para buscar serviços"><button class="main-btn" onclick="checkCEP()">BUSCAR LOCALIDADE</button><pre id="cep_out"></pre></div>
<div id="fundo" class="content"><h3><i class="fas fa-wallet"></i> FUNDO MONEYLAYER</h3><input type="number" id="pix_v" placeholder="Valor R$"><button class="main-btn" style="background:#22c55e" onclick="genPix()">GERAR APORTE SOCIAL</button><div id="qr_box" style="text-align:center; display:none; margin-top:15px;"><img id="qr_img" src="" width="160"><p id="pix_h" style="font-size:0.65rem; color:#9ca3af;"></p></div></div>
</div><script>
let activeColor = '#00d2ff';
function nav(id, btn, color) {
    document.querySelectorAll('.content').forEach(e => e.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(e => e.classList.remove('active'));
    document.getElementById(id).style.display = 'block'; btn.classList.add('active');
    activeColor = color; document.documentElement.style.setProperty('--neon', color);
}
const canvas = document.getElementById('bg'), ctx = canvas.getContext('2d');
canvas.width = window.innerWidth; canvas.height = window.innerHeight;
const particles = list(); for(let i=0; i<80; i++) particles.push({x:Math.random()*canvas.width, y:Math.random()*canvas.height, vx:(Math.random()-0.5)*2, vy:(Math.random()-0.5)*2});
function draw() {
    ctx.clearRect(0,0,canvas.width,canvas.height); ctx.fillStyle = activeColor;
    particles.forEach(p => {
        p.x += p.vx; p.y += p.vy; if(p.x<0 || p.x>canvas.width) p.vx*=-1; if(p.y<0 || p.y>canvas.height) p.vy*=-1;
        ctx.beginPath(); ctx.arc(p.x,p.y,2,0,Math.PI*2); ctx.fill();
    }); requestAnimationFrame(draw);
} draw();
async function scan() {
    const t = document.getElementById('target').value; if(!t) return;
    document.getElementById('out').innerText = '[*] Triangulando coordenadas do alvo...';
    const r = await fetch('/api/osint/scan', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({target:t})});
    const d = await r.json(); document.getElementById('out').innerText = d.logs.join('\\n');
}
async function checkCEP() {
    const c = document.getElementById('cep_in').value;
    const r = await fetch('/api/social/cep', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({cep:c})});
    const d = await r.json(); document.getElementById('cep_out').innerText = JSON.stringify(d, null, 2);
}
async function genPix() {
    const a = document.getElementById('pix_v').value; if(!a) return;
    const r = await fetch('/api/finance/pix', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({amount:a})});
    const d = await r.json();
    document.getElementById('qr_box').style.display='block'; document.getElementById('qr_img').src=d.qr;
    document.getElementById('pix_h').innerText=`TX: ${d.hash}\nIP: ${d.ip}`;
}
</script></body></html>
"""
@app.get("/")
async def home(): return HTMLResponse(content=html)
if __name__ == "__main__": uvicorn.run(app, host="127.0.0.1", port=8000)