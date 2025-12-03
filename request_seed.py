import sys
import requests 
import os


STUDENT_ID = "24P35A0535" 

GITHUB_REPO_URL = "https://github.com/SriVarshitha7720/Build-Secure-PKI-Based-2FA-Microservice-with-Docker"


API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"


def request_seed(student_id: str, github_repo_url: str, api_url: str):
    """
    Requests the encrypted seed from the Instructor API.
    
    Implementation Steps:
    1. Read and format student public key.
    2. Prepare JSON payload.
    3. Send POST request.
    4. Parse JSON response.
    5. Save encrypted seed to encrypted_seed.txt.
    """
    PUBLIC_KEY_FILE = "student_public.pem"
    OUTPUT_FILE = "encrypted_seed.txt"
    
    try:
        with open(PUBLIC_KEY_FILE, 'r') as f:
            
            public_key_pem = f.read()
    except FileNotFoundError:
        print(f"ERROR: Public key file not found at '{PUBLIC_KEY_FILE}'. Did you run Step 2?")
        sys.exit(1)

    
    public_key_single_line = public_key_pem.replace('\n', '\\n')
    
    
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_single_line
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to API: {api_url}")
    print(f"Using repo URL: {github_repo_url}")
    
    
    try:
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status() 
    
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to connect to API or request timed out: {e}")
        sys.exit(1)
        
   
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"ERROR: Failed to decode JSON response. Received status code: {response.status_code}")
        print(f"Response content: {response.text[:200]}...")
        sys.exit(1)

    
    if data.get("status") != "success":
        print(f"API ERROR: Failed to get encrypted seed.")
        print(f"API Message: {data.get('error', 'No error message provided.')}")
        sys.exit(1)

   
    encrypted_seed = data.get("encrypted_seed")
    if not encrypted_seed:
        print("API ERROR: Response was successful but 'encrypted_seed' field is missing.")
        sys.exit(1)
    
    print("SUCCESS: Encrypted seed received.")
    
   
    try:
        with open(OUTPUT_FILE, 'w') as f:
            f.write(encrypted_seed)
        print(f"Saved encrypted seed to {OUTPUT_FILE}")
        print("REMINDER: DO NOT commit 'encrypted_seed.txt' to Git.")
        
    except IOError as e:
        print(f"ERROR: Could not write to output file {OUTPUT_FILE}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    request_seed(STUDENT_ID, GITHUB_REPO_URL, API_URL)