import os
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
import base64

VPN_CONFIG_PATH = "network/vpn_configs/wg0.conf"

# --- SUA CHAVE DO SERVIDOR ---
SERVER_PUB_KEY = "RAXhzSsZaeEXYNuvMRCj9nwmR8m4LCcDKm+B01Xmd4kGlSs76Jkc=" 
# -----------------------------

def generate_wireguard_keys():
    """Gera par de chaves Curve25519 (Cliente)"""
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()

    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    return base64.b64encode(priv_bytes).decode('utf-8'), base64.b64encode(pub_bytes).decode('utf-8')

def create_vpn_config(server_ip="192.168.100.1", client_ip="10.0.0.2"):
    """Cria o arquivo de configuração wg0.conf"""
    
    # Verificação de segurança para evitar erro de placeholder
    if "COLE_A_CHAVE" in SERVER_PUB_KEY or "<" in SERVER_PUB_KEY:
        return {"status": "error", "message": "ERRO: Chave inválida no vpn_manager.py"}

    # Remove a configuração antiga para forçar a criação de uma nova limpa
    if os.path.exists(VPN_CONFIG_PATH):
        try:
            os.remove(VPN_CONFIG_PATH)
        except PermissionError:
            pass # Ignora se estiver travado

    priv_key, pub_key = generate_wireguard_keys()

    # Conteúdo do arquivo wg0.conf
    config_content = f"""[Interface]
# TheOrbeSystems Secure Tunnel
PrivateKey = {priv_key}
Address = {client_ip}/32
DNS = 1.1.1.1

[Peer]
# Servidor Central
PublicKey = {SERVER_PUB_KEY}
AllowedIPs = 0.0.0.0/0
Endpoint = {server_ip}:51820
PersistentKeepalive = 25
"""
    
    # Garante que a pasta existe
    os.makedirs(os.path.dirname(VPN_CONFIG_PATH), exist_ok=True)
    
    # Salva o arquivo
    with open(VPN_CONFIG_PATH, "w") as f:
        f.write(config_content)
    
    return {
        "status": "configured",
        "message": "Configuração VPN gerada com sucesso! Chave aplicada.",
        "path": VPN_CONFIG_PATH
    }

def check_vpn_status():
    if os.path.exists(VPN_CONFIG_PATH):
        return "Configurado"
    return "Aguardando"