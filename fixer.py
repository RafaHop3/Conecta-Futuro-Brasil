content = """from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os
from network.vpn_manager import check_vpn_status
from security.scanner import scan_system
from moneylayer.database import engine, Base, get_db
from moneylayer.models import SocialFund

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post('/api/moneylayer/donate')
async def donate(db: Session = Depends(get_db)):
    fund = db.query(SocialFund).first()
    if not fund:
        fund = SocialFund(project_name='MoneyLayer Global', global_value=0.0, social_impact_score=100)
        db.add(fund)
    fund.global_value += 10.0
    db.commit()
    return {'status': 'sucesso', 'novo_total': fund.global_value}

@app.get('/', response_class=HTMLResponse)
async def home(db: Session = Depends(get_db)):
    fund = db.query(SocialFund).first()
    total = fund.global_value if fund else 0.0
    risk_info = scan_system()
    return f'''
    <html>
    <head>
        <title>MoneyLayer 2.0 | Steel Blue Edition</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{
                --main-blue: #0a192f;
                --steel-blue: #112240;
                --electric-blue: #00d2ff;
                --silver: #e2e8f0;
                --text: #8892b0;
            }}
            body {{ background: var(--main-blue); color: var(--silver); font-family: 'Inter', sans-serif; margin: 0; }}
            .header {{ padding: 25px; background: var(--steel-blue); border-bottom: 2px solid var(--electric-blue); display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
            .tabs {{ display: flex; background: #020c1b; padding: 0 20px; gap: 5px; border-bottom: 1px solid #233554; }}
            .tab-btn {{ padding: 18px 25px; border: none; background: none; color: var(--text); cursor: pointer; font-weight: 600; font-size: 0.9rem; transition: 0.4s; }}
            .tab-btn.active {{ color: var(--electric-blue); border-bottom: 3px solid var(--electric-blue); background: rgba(0,210,255,0.05); }}
            .content {{ padding: 40px; display: none; animation: fadeIn 0.5s; }}
            .content.active {{ display: block; }}
            @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
            .card {{ background: var(--steel-blue); border: 1px solid #233554; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 10px 30px -15px rgba(2,12,27,0.7); }}
            .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .info-item {{ background: rgba(0,210,255,0.03); padding: 15px; border-left: 4px solid var(--electric-blue); border-radius: 4px; }}
            .info-item label {{ font-size: 0.75rem; color: var(--electric-blue); text-transform: uppercase; font-weight: bold; display: block; }}
            .info-item span {{ font-size: 1.1rem; color: #fff; }}
            button {{ background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%); color: white; border: none; padding: 15px 30px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: 0.3s; }}
            button:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,210,255,0.4); }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2 style="margin:0; letter-spacing: 2px;"><i class="fas fa-layer-group"></i> MONEYLAYER <span style="color:var(--electric-blue)">2.0</span></h2>
            <div style="font-size: 0.8rem; border: 1px solid var(--electric-blue); padding: 5px 12px; border-radius: 20px;">
                <i class="fas fa-shield-alt"></i> STATUS: <span style="color:var(--electric-blue)">SISTEMA BLINDADO</span>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="openTab(event, 'perfil')"><i class="fas fa-user-circle"></i> MEU PERFIL</button>
            <button class="tab-btn" onclick="openTab(event, 'financas')"><i class="fas fa-wallet"></i> FINANCEIRO</button>
            <button class="tab-btn" onclick="openTab(event, 'cursos')"><i class="fas fa-graduation-cap"></i> CURSOS</button>
            <button class="tab-btn" onclick="openTab(event, 'trabalho')"><i class="fas fa-briefcase"></i> TRABALHO</button>
            <button class="tab-btn" onclick="openTab(event, 'habitacao')"><i class="fas fa-home"></i> HABITAÇÃO</button>
        </div>

        <div id="perfil" class="content active">
            <h3><i class="fas fa-id-card"></i> Identificação do Protocolo Zero</h3>
            <div class="card">
                <div class="info-grid">
                    <div class="info-item"><label>Usuário</label><span>Rafael Machado Gomes Machado</span></div>
                    <div class="info-item"><label>Status de Rede</label><span>{risk_info['risk_level']}</span></div>
                    <div class="info-item"><label>Conexão VPN</label><span>{check_vpn_status()}</span></div>
                    <div class="info-item"><label>IP do Túnel</label><span>10.0.0.2</span></div>
                </div>
                <div class="info-item" style="border-left-color: #ff0055;"><label>Nota de Segurança</label><span>Ambiente Monitorado e Protegido por Curve25519</span></div>
            </div>
        </div>

        <div id="financas" class="content">
            <div class="card" style="text-align:center;">
                <h3 style="color:var(--electric-blue)">Fundo de Interesse Social</h3>
                <div style="font-size: 3.5rem; color:#fff; margin: 20px 0;" id="total">R$ {total:.2f}</div>
                <button onclick="donate()"><i class="fas fa-bolt"></i> EFETUAR APORTE SOCIAL</button>
            </div>
        </div>

        <div id="cursos" class="content">
            <h3>🎓 Oportunidades Acadêmicas</h3>
            <div class="card">
                <h4>Cyber Safety & Defesa Cibernética</h4>
                <p>Nível: Avançado | Vagas remanescentes: 08</p>
                <button>CANDIDATAR-SE</button>
            </div>
        </div>

        <div id="trabalho" class="content">
            <h3>💼 Balcão de Trabalho Social</h3>
            <div class="card">
                <h4>Analista de Dados de Interesse Social</h4>
                <p>Empresa: CFB Tecnologia | Remuneração: R$ 4.200,00</p>
                <button>VER DETALHES</button>
            </div>
        </div>

        <div id="habitacao" class="content">
            <h3>🏠 Portal Habitação</h3>
            <div class="card">
                <h4>Inscrição Programa Moradia Popular</h4>
                <p>Sorteio previsto para: Abril/2026</p>
                <button>SOLICITAR INSCRIÇÃO</button>
            </div>
        </div>

        <script>
            function openTab(evt, tabName) {{
                var i, content, tablinks;
                content = document.getElementsByClassName("content");
                for (i = 0; i < content.length; i++) {{ content[i].className = content[i].className.replace(" active", ""); }}
                tablinks = document.getElementsByClassName("tab-btn");
                for (i = 0; i < tablinks.length; i++) {{ tablinks[i].className = tablinks[i].className.replace(" active", ""); }}
                document.getElementById(tabName).className += " active";
                evt.currentTarget.className += " active";
            }}

            async function donate() {{
                const res = await fetch('/api/moneylayer/donate', {{method:'POST'}});
                const data = await res.json();
                if(data.status === 'sucesso') {{
                    document.getElementById('total').innerText = 'R$ ' + data.novo_total.toFixed(2);
                }}
            }}
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
"""
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
