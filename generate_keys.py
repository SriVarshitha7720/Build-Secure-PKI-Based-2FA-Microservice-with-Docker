import os
import sys
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def generate_rsa_keypair(key_size: int = 4096) -> tuple:
    """
    Generates the 4096-bit RSA key pair with the required public exponent (65537).
    """
    try:
        # 1. Generate 4096-bit RSA key with public exponent 65537
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
    except Exception as e:
        print(f"Error during key generation: {e}")
        sys.exit(1)
        
    # 2. Extract public key
    public_key = private_key.public_key()
    # 3. Return key objects
    return (private_key, public_key)

def serialize_and_save_private_key(key: rsa.RSAPrivateNumbers, filename: str):
    """Serializes the private key object to PEM format and saves it."""
    # Serialize to PEM format without encryption (as it is committed publicly)
    pem_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    # Write the key bytes to the specified file
    with open(filename, "wb") as f:
        f.write(pem_bytes)

def serialize_and_save_public_key(key: rsa.RSAPublicNumbers, filename: str):
    """Serializes the public key object to PEM format and saves it."""
    # Serialize to PEM format
    pem_bytes = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # Write the key bytes to the specified file
    with open(filename, "wb") as f:
        f.write(pem_bytes)

def main():
    private_file = "student_private.pem"
    public_file = "student_public.pem"

    print("--- Starting RSA Key Pair Generation (4096 bits) ---")
    
    # 1. Generate the key objects
    private_key_obj, public_key_obj = generate_rsa_keypair(key_size=4096)
    print("Key pair objects generated successfully.")
    
    try:
        # 2. Save the files to the required names
        serialize_and_save_private_key(private_key_obj, private_file)
        print(f"Private Key saved to: {private_file}")
        
        serialize_and_save_public_key(public_key_obj, public_file)
        print(f"Public Key saved to: {public_file}")
        
    except Exception as e:
        print(f"Error saving key files: {e}")
        sys.exit(1)
    
    print("\n--- Key Generation Complete. Proceed to Git Commit. ---")

if __name__ == "__main__":
    main()
