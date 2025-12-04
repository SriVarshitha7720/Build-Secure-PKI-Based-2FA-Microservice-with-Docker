import requests

code = requests.get("http://localhost:8000/generate").json()["code"]
print("Generated code:", code)

resp = requests.post("http://localhost:8000/verify", json={"code": code}).json()
print("Is code valid?", resp["valid"])
