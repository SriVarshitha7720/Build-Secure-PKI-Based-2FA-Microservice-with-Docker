import os
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

def decrypt_seed(encrypted_seed_b64, private_key):
    ciphertext = base64.b64decode(encrypted_seed_b64)
    plaintext_bytes = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext_bytes.decode("utf-8").strip()

def load_private_key(path="student_private.pem"):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def main():
    private_key = load_private_key()
    with open("encrypted_seed.txt", "r") as f:
        encrypted_seed_b64 = f.read().strip()
    seed_hex = decrypt_seed(encrypted_seed_b64, private_key)
    safe_folder = os.path.join(os.getcwd(), "local_data")
    os.makedirs(safe_folder, exist_ok=True)
    output_path = os.path.join(safe_folder, "seed.txt")
    with open(output_path, "w") as f:
        f.write(seed_hex)
    print(f"Decrypted seed saved to {output_path}")

if __name__ == "__main__":
    main()
