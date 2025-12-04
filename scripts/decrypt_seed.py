import os
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_private_key():
    with open("keys/student_private.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def decrypt_seed():
    # Read encrypted seed
    with open("encrypted/encrypted_seed.txt", "r") as f:
        encrypted_b64 = f.read().strip()

    if not encrypted_b64:
        print("Encrypted seed file is empty!")
        return

    encrypted_bytes = base64.b64decode(encrypted_b64)
    private_key = load_private_key()

    try:
        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        print("Decryption failed:", e)
        return

    # Create data folder if missing
    os.makedirs("data", exist_ok=True)
    with open("data/seed.txt", "w") as f:
        f.write(decrypted.hex())

    print("Decryption successful! Saved to data/seed.txt")
    print("Decrypted seed (first 50 chars):", decrypted.hex()[:50])

if __name__ == "__main__":
    decrypt_seed()
