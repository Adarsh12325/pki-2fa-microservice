from fastapi import FastAPI, HTTPException
import time
import hmac
import hashlib
import struct
import os

# Create FastAPI instance (must be named 'app')
app = FastAPI(title="PKI 2FA Microservice")


# -------------------------------
# Load TOTP seed from file
# -------------------------------
def load_seed():
    seed_file = "data/seed.txt"
    if not os.path.exists(seed_file):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    with open(seed_file, "r") as f:
        hex_seed = f.read().strip()
    try:
        return bytes.fromhex(hex_seed)
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid seed format")


# -------------------------------
# Generate TOTP code (RFC 6238)
# -------------------------------
def generate_totp(offset: int = 0) -> str:
    seed = load_seed()
    timestep = int(time.time() // 30) + offset
    msg = struct.pack(">Q", timestep)
    h = hmac.new(seed, msg, hashlib.sha1).digest()
    o = h[-1] & 0x0F
    code = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    return f"{code:06d}"


# -------------------------------
# API Endpoint: Generate 2FA
# -------------------------------
@app.get("/generate-2fa")
def generate_2fa():
    code = generate_totp()
    remaining = 30 - (int(time.time()) % 30)
    return {"code": code, "valid_for": remaining}


# -------------------------------
# API Endpoint: Verify 2FA
# -------------------------------
@app.post("/verify-2fa/{otp}")
def verify_2fa(otp: str):
    # Allow 1 period tolerance (-1, 0, +1)
    codes = [generate_totp(-1), generate_totp(0), generate_totp(1)]
    if otp in codes:
        return {"valid": True}
    return {"valid": False}
