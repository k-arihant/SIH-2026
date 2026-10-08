"""
Minimal Gemini Connection Test for gemini-3.6-flash.
Tests connectivity to the Gemini Developer API using the official google-genai SDK.

Usage:
    python backend/test_connection.py [API_KEY]
"""

from pathlib import Path
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

from google import genai


def main():
    global api_key
    if len(sys.argv) > 1:
        api_key = sys.argv[1]

    clean_key = api_key.strip().strip('"').strip("'") if api_key else ""

    if clean_key:
        print("API key detected: YES")
    else:
        print("API key detected: NO")
        print("[!] ERROR: No API key provided.")
        print("Usage: python backend/test_connection.py YOUR_GEMINI_API_KEY")
        print("Or set GEMINI_API_KEY in backend/.env")
        sys.exit(1)

    print("[*] Initializing genai.Client for Gemini Developer API...")

    # Developer API initialization (no Vertex AI, no OAuth)
    client = genai.Client(api_key=clean_key)

    model_name = "gemini-3.6-flash"
    prompt = "Reply with exactly: GEMINI_OK"

    print(f"[*] Sending test request to '{model_name}'...")

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        print(f"\n[+] Output from {model_name}:")
        print(response.text.strip())
        print("\n[OK] GEMINI CONNECTION SUCCESSFUL: GEMINI_OK\n")
        return

    except Exception as e:
        err_msg = str(e)
        print(f"[-] models.generate_content failed: {err_msg}")

        # Check if Interactions API is recommended
        if "Interactions API" in err_msg or hasattr(client, "interactions"):
            print(f"[*] Attempting client.interactions.create with '{model_name}'...")
            try:
                interaction = client.interactions.create(
                    model=model_name,
                    input=prompt
                )
                output = getattr(interaction, "output_text", None) or str(interaction)
                print(f"\n[+] Output from {model_name} (Interactions API):")
                print(output.strip())
                print("\n[OK] GEMINI CONNECTION SUCCESSFUL: GEMINI_OK\n")
                return
            except Exception as e2:
                print(f"[!] Interactions API also failed: {e2}")

        print(f"\n[!] Final Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
