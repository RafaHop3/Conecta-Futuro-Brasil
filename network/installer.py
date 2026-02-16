import subprocess
import os

def check_and_install_driver():
    """Verifica a presença do driver WireGuard NT e instala se necessário"""
    # Caminho padrão onde o executável deve estar após instalado
    target_path = "C:\\Program Files\\WireGuard\\wireguard.exe"
    
    if not os.path.exists(target_path):
        # Localiza o instalador que você colocará na pasta bin
        installer = os.path.abspath("network/bin/wireguard_installer.exe")
        
        if os.path.exists(installer):
            try:
                # O parâmetro /S executa a instalação silenciosa
                subprocess.run([installer, "/S"], check=True)
                return "Driver instalado com sucesso."
            except Exception as e:
                return f"Erro na instalação: {e}"
        return "Aviso: wireguard_installer.exe não encontrado em network/bin/"
    return "Infraestrutura de rede pronta."
