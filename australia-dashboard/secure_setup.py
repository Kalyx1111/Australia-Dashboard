"""Run: python secure_setup.py - encrypts optional API keys AES-256-GCM."""
import sys
from getpass import getpass

sys.path.insert(0, ".")
from app.secure_store import update_secrets, KEY_PATH, SECRETS_PATH, CRYPTO_AVAILABLE  # noqa: E402

FIELDS = [
    ("GROK_API_KEY", "xAI Grok API key (x.ai)"),
    ("GROK_TRACKED_HANDLES", "Comma-separated X handles for Grok to track (no @)"),
    ("X_THIRDPARTY_API_KEY", "TwitterAPI.io key"),
    ("NEWSAPI_KEY", "NewsAPI.org key"),
    ("INSTAGRAM_IG_USER_ID", "Your Instagram Business/Creator account ID (Meta)"),
    ("INSTAGRAM_ACCESS_TOKEN", "Instagram/Meta access token (official Business Discovery)"),
]


def main():
    if not CRYPTO_AVAILABLE:
        print("Run: pip install cryptography, then re-run this script.")
        sys.exit(1)
    print("AUSTRALIA Dashboard - encrypted key setup")
    print(f"Key file: {KEY_PATH}\nEncrypted store: {SECRETS_PATH}\n")
    print("Leave blank to skip. Input is hidden.\n")
    updates = {}
    for env_name, label in FIELDS:
        value = getpass(f"{label}\n{env_name} = ").strip()
        if value:
            updates[env_name] = value
        print()
    if not updates:
        print("No keys entered - nothing written. Free sources still work fully.")
        return
    update_secrets(updates)
    print(f"Encrypted {len(updates)} key(s) to {SECRETS_PATH}")


if __name__ == "__main__":
    main()
