from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
import base64

def generate_key():
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return base64.b64encode(pub_bytes).decode('utf-8')

print("=== COPIE ESTA CHAVE PARA O SEU CÓDIGO ===")
print(generate_key())
print("==========================================")