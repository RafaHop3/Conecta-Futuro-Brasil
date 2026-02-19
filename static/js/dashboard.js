function openTab(evt, tabName) {
    let i, content, tablinks;
    content = document.getElementsByClassName("content");
    for (i = 0; i < content.length; i++) { content[i].classList.remove("active"); }
    tablinks = document.getElementsByClassName("tab-btn");
    for (i = 0; i < tablinks.length; i++) { tablinks[i].classList.remove("active"); }
    document.getElementById(tabName).classList.add("active");
    evt.currentTarget.classList.add("active");
    if(tabName === 'auditoria') updateAudit();
}

async function updateAudit() {
    const res = await fetch('/api/moneylayer/audit');
    const data = await res.json();
    const enrollList = document.getElementById('audit-enroll');
    if(data.enrollments.length > 0) {
        enrollList.innerHTML = data.enrollments.map(e => `
            <li style="margin-bottom:10px; padding:15px; background:rgba(0,210,255,0.05); border-radius:8px; border-left:4px solid #00d2ff;">
                <b style="color:#fff;">${e.program_name}</b><br>
                <small style="color:#8892b0;"><i class="fas fa-link"></i> Hash: ${e.blockchain_hash.substring(0,20)}...</small>
            </li>`).join('');
    } else { enrollList.innerHTML = "<li>Nenhum registro encontrado no Protocolo CFB.</li>"; }
}

async function applyForSocialProgram(progName, realUrl, btnElement) {
    // Ideograma: Muda o botão para estado de processamento
    const originalText = btnElement.innerHTML;
    btnElement.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Auditando Hash...';
    btnElement.disabled = true;

    try {
        const res = await fetch('/api/moneylayer/apply', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({program: progName})
        });
        
        if(res.ok) {
            // Ideograma: Sucesso e redirecionamento
            btnElement.innerHTML = '<i class="fas fa-check-circle" style="color:#00ff00;"></i> Liberado! Redirecionando...';
            setTimeout(() => {
                btnElement.innerHTML = originalText;
                btnElement.disabled = false;
                window.open(realUrl, '_blank'); // Abre a oportunidade real em nova aba
                if(document.getElementById('auditoria').classList.contains('active')) updateAudit();
            }, 1500);
        }
    } catch (e) {
        btnElement.innerHTML = '<i class="fas fa-exclamation-triangle" style="color:#ff0055;"></i> Erro de Rede';
        setTimeout(() => { btnElement.innerHTML = originalText; btnElement.disabled = false; }, 2000);
    }
}
