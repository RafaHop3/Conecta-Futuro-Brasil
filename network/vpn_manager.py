import os
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
import base64

VPN_CONFIG_PATH = "network/vpn_configs/wg0.conf"
SERVER_PUB_KEY = "Rtd2FpsRfuPq31mAzrIRhF6MK+B01Xmd4kGlSs76Jkc=" 

def generate_wireguard_keys():
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
    allowed_ips = "10.0.0.0/24, 192.168.100.0/24"
    if "COLE_A_CHAVE" in SERVER_PUB_KEY:
        return {"status": "error", "message": "Erro de Chave"}
    
    priv_key, pub_key = generate_wireguard_keys()
    config_content = f"""[Interface]
# TheOrbeSystems Secure Tunnel - SPLIT MODE
PrivateKey = {priv_key}
Address = {client_ip}/32

[Peer]
PublicKey = {SERVER_PUB_KEY}
AllowedIPs = {allowed_ips}
Endpoint = {server_ip}:51820
PersistentKeepalive = 25
"""
    os.makedirs(os.path.dirname(VPN_CONFIG_PATH), exist_ok=True)
    with open(VPN_CONFIG_PATH, "w") as f:
        f.write(config_content)
    return {"status": "configured", "message": "Split Tunneling aplicado."}

def check_vpn_status():
    return "Configurado" if os.path.exists(VPN_CONFIG_PATH) else "Aguardando"
