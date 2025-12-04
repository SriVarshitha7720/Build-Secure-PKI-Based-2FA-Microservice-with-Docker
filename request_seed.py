import sys
import requests
import os
from cryptography.hazmat.primitives import serialization

STUDENT_ID = "24P35A0535"
GITHUB_REPO_URL = "https://github.com/SriVarshitha7720/Build-Secure-PKI-Based-2FA-Microservice-with-Docker"
API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws/"

def request_seed(student_id: str, github_repo_url: str, api_url: str):
    PUBLIC_KEY_FILE = "student_public.pem"
    OUTPUT_FILE = "encrypted_seed.txt"

    try:
        with open(PUBLIC_KEY_FILE, "rb") as f:
            key_data = f.read()

        public_key = serialization.load_pem_public_key(key_data)

        public_key_clean = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("utf-8").strip()

    except FileNotFoundError:
        print(f"ERROR: Public key file not found: {PUBLIC_KEY_FILE}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load or parse public key: {e}")
        sys.exit(1)

    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_clean
    }

    headers = {"Content-Type": "application/json"}

    print(f"\nSending request to API: {api_url}")
    print(f"Using repo URL: {github_repo_url}")

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to reach API: {e}")
        sys.exit(1)

    try:
        data = response.json()
    except Exception:
        print("ERROR: Response was not valid JSON.")
        print("Raw response:", response.text)
        sys.exit(1)

    if data.get("status") != "success":
        print("API ERROR: Failed to retrieve encrypted seed.")
        print("Message:", data.get("error", '(no error message)'))
        sys.exit(1)

    encrypted_seed = data.get("encrypted_seed")
    if not encrypted_seed:
        print("API ERROR: Missing 'encrypted_seed' field in response.")
        sys.exit(1)

    print("\nSUCCESS: Encrypted seed received.")

    try:
        with open(OUTPUT_FILE, "w") as f:
            f.write(encrypted_seed)

        print(f"Encrypted seed saved to: {OUTPUT_FILE}")
        print("IMPORTANT: Do NOT commit encrypted_seed.txt to Git.")
    except IOError as e:
        print(f"ERROR: Could not write output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    request_seed(STUDENT_ID, GITHUB_REPO_URL, API_URL)
