#!/usr/bin/env python3
import time
import requests
import csv

# --- Hardcoded values ---
LOGIN_URL = "http://127.0.0.1:8000/api/blockchain/login"
LOGIN_PRIVATE_KEY = "0xdf57089febbacf7ba0bc227dafbffa9fc08a93fdc68e1e42411a14efcf23656e"

GEN_URL = "http://localhost:9000/generate_keys"
ENCRYPT_URL = "http://localhost:9000/encrypt_data"
DECRYPT_URL = "http://localhost:9000/decrypt_data"
ENCRYPTED_FILE = "/app/data_encrypted.bin"

ITERATIONS = 10
ENCRYPT_DATA_PAYLOAD = [

		{
            "OBJECTID": 1,
            "Nature_Of_": "ForTestingLatrest",
            "Premise_Ty": "SHOPTEST",
            "Organizati": "ABHYUDAY BANK",
            "Building_N": 1,
            "Street_Typ": "ROAD",
            "Street_Nam": "RANNA PARK ROAD",
            "Landmark": "NR RANNA PARK BUS STAND",
            "Locality": "GOKHALE NAGAR",
            "City": "AHMEDABAD",
            "Post_Offic": "GHATLODIA POST OFFICE",
            "District": "AHMEDABAD",
            "Sub_Distri": "AHMEDABAD",
            "State": "GUJARAT",
            "Postman_Be": 1000,
            "Pincode": 380061,
            "SymbolID": 1,
            "lat": 23.0682816437,
            "long": 72.5479675457
        },
		{
            "OBJECTID": 1,
            "Nature_Of_": "ForTestingLatrest",
            "Premise_Ty": "SHOPTEST",
            "Organizati": "ABHYUDAY BANK",
            "Building_N": 1,
            "Street_Typ": "ROAD",
            "Street_Nam": "RANNA PARK ROAD",
            "Landmark": "NR RANNA PARK BUS STAND",
            "Locality": "GOKHALE NAGAR",
            "City": "AHMEDABAD",
            "Post_Offic": "GHATLODIA POST OFFICE",
            "District": "AHMEDABAD",
            "Sub_Distri": "AHMEDABAD",
            "State": "GUJARAT",
            "Postman_Be": 1000,
            "Pincode": 380061,
            "SymbolID": 1,
            "lat": 23.0682816437,
            "long": 72.5479675457
        }
    ]   # hardcoded "data": []

# -------------------------

def ms(sec: float) -> float:
    return round(sec * 1000.0, 3)

def post_timed(session, url, payload, headers=None):
    start = time.perf_counter()
    resp = session.post(url, json=payload, headers=headers)
    elapsed = time.perf_counter() - start
    return resp, elapsed

def get_timed(session, url, headers=None):
    start = time.perf_counter()
    resp = session.get(url, headers=headers)
    elapsed = time.perf_counter() - start
    return resp, elapsed

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {"_raw": resp.text, "_status": resp.status_code}

def extract_session_token(session, resp):
    """
    Try to extract session_token from session cookies first,
    else parse Set-Cookie header.
    """
    token = None
    for c in session.cookies:
        if c.name == "session_token":
            token = c.value
            break
    if token:
        return token

    set_cookie = resp.headers.get("Set-Cookie", "")
    # very simple parse (good enough for 'session_token=XYZ; ...')
    for part in set_cookie.split(";"):
        kv = part.strip().split("=", 1)
        if len(kv) == 2 and kv[0] == "session_token":
            return kv[1]
    return None

def main():
    session = requests.Session()

    # Step 1: LOGIN (POST)
    print("== Step 1: Login ==")
    resp, t_login = post_timed(session, LOGIN_URL, {"private_key": LOGIN_PRIVATE_KEY})
    login_json = safe_json(resp)
    if not resp.ok:
        raise RuntimeError(f"Login failed: {resp.status_code} {login_json}")
    token = extract_session_token(session, resp)
    print(f"Login OK in {ms(t_login)} ms")
    print(f"Stored session_token: {token or '(not found!)'}")

    # Build cookie header to use explicitly for every endpoint after login
    cookie_header = {}
    if token:
        cookie_header = {"Cookie": f"session_token={token}"}

    # Step 2: GENERATE KEYS (GET)
    print("\n== Step 2: Generate keys (GET) ==")
    resp, t_gen = get_timed(session, GEN_URL, headers=cookie_header)
    gen_json = safe_json(resp)
    if not resp.ok:
        raise RuntimeError(f"generate_keys failed: {resp.status_code} {gen_json}")
    priv = gen_json.get("private_key")
    pub = gen_json.get("public_key")
    if not priv or not pub:
        raise RuntimeError(f"Keys missing in response: {gen_json}")
    print(f"generate_keys OK in {ms(t_gen)} ms")

    # Step 3: ENCRYPT + DECRYPT cycles
    print("\n== Step 3: Encrypt + Decrypt cycles ==")
    enc_times, dec_times = [], []
    with open("api_timing_log.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["iteration", "encrypt_ms", "decrypt_ms"])

        for i in range(1, ITERATIONS + 1):
            # ENCRYPT (POST)
            enc_payload = {"public_key": pub, "data": ENCRYPT_DATA_PAYLOAD}
            resp, t_enc = post_timed(session, ENCRYPT_URL, enc_payload, headers=cookie_header)
            enc_json = safe_json(resp)
            if not resp.ok:
                print(f"[ERROR] Encrypt failed at iter {i}: {enc_json}")
                writer.writerow([i, "ERROR", ""])
                continue

            # DECRYPT (POST)
            dec_payload = {
                "private_key": priv,
                "kem_ciphertext": enc_json.get("kem_ciphertext"),
                "aes_iv": enc_json.get("aes_iv"),
                "aes_tag": enc_json.get("aes_tag"),
                "encrypted_file": ENCRYPTED_FILE,
            }
            resp, t_dec = post_timed(session, DECRYPT_URL, dec_payload, headers=cookie_header)
            dec_json = safe_json(resp)
            if not resp.ok:
                print(f"[ERROR] Decrypt failed at iter {i}: {dec_json}")
                writer.writerow([i, ms(t_enc), "ERROR"])
                continue

            enc_ms, dec_ms = ms(t_enc), ms(t_dec)
            enc_times.append(enc_ms)
            dec_times.append(dec_ms)
            writer.writerow([i, enc_ms, dec_ms])
            print(f"Iteration {i:02d}: encrypt={enc_ms} ms, decrypt={dec_ms} ms")

    # Summary
    def stats(values):
        if not values:
            return {"avg": None, "min": None, "max": None}
        return {
            "avg": round(sum(values) / len(values), 3),
            "min": round(min(values), 3),
            "max": round(max(values), 3),
        }

    print("\n== Summary ==")
    enc_s, dec_s = stats(enc_times), stats(dec_times)
    print(f"Encrypt: count={len(enc_times)} avg={enc_s['avg']} ms min={enc_s['min']} ms max={enc_s['max']} ms")
    print(f"Decrypt: count={len(dec_times)} avg={dec_s['avg']} ms min={dec_s['min']} ms max={dec_s['max']} ms")
    print("Raw timings written to api_timing_log.csv")

if __name__ == "__main__":
    main()