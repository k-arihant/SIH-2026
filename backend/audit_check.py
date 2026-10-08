import requests
import time
import sys

base = 'http://localhost:8000'
endpoints = [
    ('GET', '/'),
    ('GET', '/health'),
    ('POST', '/api/v1/auth/login', {'email': 'inspector.verma@gov.in', 'password': 'pass'}),
    ('GET', '/api/v1/dashboard/stats'),
    ('GET', '/api/v1/dashboard/heatmap'),
    ('GET', '/api/v1/dashboard/analytics'),
    ('GET', '/api/v1/dashboard/recent-scans'),
    ('GET', '/api/v1/scan/f0ce5e06-601c-461a-bc66-b647a00bba02/certificate'),
]

print("=" * 65)
print("METROSCAN PRODUCTION BACKEND & PIPELINE AUDIT")
print("=" * 65)

all_pass = True
for ep in endpoints:
    method = ep[0]
    path = ep[1]
    url = base + path
    try:
        if method == 'GET':
            res = requests.get(url, timeout=5)
        else:
            res = requests.post(url, json=ep[2], timeout=5)
        ok = (res.status_code == 200)
        status_tag = "PASS [200 OK]" if ok else f"FAIL [{res.status_code}]"
        print(f" {status_tag:16} | {method:4} {path}")
        if not ok:
            all_pass = False
    except Exception as e:
        print(f" ERR [FAILED]    | {method:4} {path} -> {e}")
        all_pass = False

print("=" * 65)
if all_pass:
    print("ALL PRODUCTION ENDPOINTS OPERATIONAL AND WIRED UP SUCCESSFULLY!")
else:
    print("WARNING: ONE OR MORE ENDPOINTS RETURNED ERRORS.")
print("=" * 65)

sys.exit(0 if all_pass else 1)
