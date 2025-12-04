from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()

SEED_PATH = "/data/seed.txt"
PRIVATE_KEY_PATH = "student_private.pem"  # your key file


# ---------- REQUEST MODELS ----------
class DecryptSeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str


# ---------- ENDPOINT 1: DECRYPT SEED ----------
@app.post("/decrypt-seed")
def decrypt_seed_api(req: DecryptSeedRequest):
    try:
        encrypted_bytes = base64.b64decode(req.encrypted_seed)

        # Load RSA private key
        with open(PRIVATE_KEY_PATH, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )

        # Decrypt
        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        hex_seed = decrypted.decode()

        # Validate hex seed
        if len(hex_seed) != 64 or any(c not in "0123456789abcdef" for c in hex_seed):
            raise Exception("Invalid seed format")

        os.makedirs("/data", exist_ok=True)

        with open(SEED_PATH, "w") as f:
            f.write(hex_seed)

        return {"status": "ok"}

    except Exception as e:
        return {"error": "Decryption failed", "details": str(e)}


# ---------- ENDPOINT 2: GENERATE 2FA ----------
@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_PATH, "r") as f:
        hex_seed = f.read().strip()

    code = generate_totp_code(hex_seed)

    # calculate remaining validity (0–29 sec)
    import time
    remaining = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": remaining}


# ---------- ENDPOINT 3: VERIFY 2FA ----------
@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):

    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_PATH, "r") as f:
        hex_seed = f.read().strip()

    valid = verify_totp_code(hex_seed, req.code)

    return {"valid": valid}