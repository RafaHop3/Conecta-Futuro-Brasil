$jsContent = @'
async function updateLogs() {
    try {
        const res = await fetch('/api/security/logs');
        const data = await res.json();
        document.getElementById('console').innerHTML = "<strong>📜 MONITORAMENTO EM TEMPO REAL:</strong>\n" + data.logs.join("");
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
    document.getElementById('console').innerHTML = " > [SYSTEM]: Executando Varredura...\n";
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
'@

$jsContent | Out-File -FilePath static/js/dashboard.js -Encoding utf8