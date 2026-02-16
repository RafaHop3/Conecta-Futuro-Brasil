import sys
import os

# Adiciona o diretório atual
sys.path.append(os.getcwd())

try:
    from network.vpn_manager import create_vpn_config, SERVER_PUB_KEY
except ImportError as e:
    print(f"ERRO: Não consegui importar o vpn_manager. {e}")
    sys.exit()

print("--- DIAGNÓSTICO VPN ---")
print(f"Chave configurada no código: {SERVER_PUB_KEY}")

# Força a recriação
print("\nGerando novo arquivo wg0.conf...")
result = create_vpn_config()
print(result['message'])

# Lê o arquivo gerado para provar o conteúdo
file_path = "network/vpn_configs/wg0.conf"
if os.path.exists(file_path):
    print(f"\n--- CONTEÚDO DO ARQUIVO ({file_path}) ---")
    with open(file_path, 'r') as f:
        content = f.read()
        print(content)
        
    if "<" in content or "COLE_A_CHAVE" in content:
        print("\n❌ ERRO FATAL: O arquivo ainda contém placeholders!")
    else:
        print("\n✅ SUCESSO: O arquivo parece correto e pronto para o WireGuard.")
else:
    print("❌ ERRO: O arquivo não foi criado.")