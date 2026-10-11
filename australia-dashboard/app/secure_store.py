"""AES-256-GCM key storage - real `cryptography` package, not a homemade
cipher. Protects keys if secrets.enc leaks on its own; does not protect an
already-compromised machine (nothing local can honestly claim that)."""
from __future__ import annotations
import json
import os
import stat
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_AVAILABLE = True
except ImportError:
    AESGCM = None
    CRYPTO_AVAILABLE = False

KEY_DIR = Path.home() / ".australia_dashboard"
KEY_PATH = KEY_DIR / "secret.key"
_BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_PATH = _BASE_DIR / "data" / "secrets.enc"
KEY_BYTES = 32
NONCE_BYTES = 12
AAD = b"australia-dashboard-secrets-v1"


class CryptoUnavailable(Exception):
    pass


class DecryptError(Exception):
    """The store exists but couldn't be read: wrong/regenerated key, a
    corrupted file, or tampering - GCM's auth tag can't tell these apart,
    and from a security standpoint it shouldn't need to: all three mean
    'don't trust this ciphertext.'"""
    pass


def _get_or_create_key() -> bytes:
    if not CRYPTO_AVAILABLE:
        raise CryptoUnavailable("pip install cryptography  (only needed for encrypted API-key storage)")
    if KEY_PATH.exists():
        key = KEY_PATH.read_bytes()
        if len(key) != KEY_BYTES:
            raise ValueError(f"{KEY_PATH} is not a valid 256-bit key - delete it to regenerate")
        return key
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    key = os.urandom(KEY_BYTES)
    KEY_PATH.write_bytes(key)
    try:
        os.chmod(KEY_PATH, stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, NotImplementedError):
        pass
    return key


def decrypt_secrets() -> dict:
    """Raises on a genuinely unreadable store (wrong/regenerated key,
    corrupted file, or tampering - GCM's auth tag catches all three the same
    way) rather than silently returning {} - that failure is a real signal
    worth surfacing, not hiding. Callers that need to degrade gracefully
    (the HTTP routes in server.py) catch it there; see DecryptError."""
    if not CRYPTO_AVAILABLE or not SECRETS_PATH.exists():
        return {}
    key = _get_or_create_key()
    raw = SECRETS_PATH.read_bytes()
    nonce, ciphertext = raw[:NONCE_BYTES], raw[NONCE_BYTES:]
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=AAD)
    except Exception as e:
        raise DecryptError(
            f"could not decrypt {SECRETS_PATH.name} - wrong/regenerated key, corrupted file, "
            f"or tampering (the AES-GCM auth tag failed to verify)"
        ) from e
    return json.loads(plaintext.decode("utf-8"))


def _write_secrets(secrets: dict) -> None:
    key = _get_or_create_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_BYTES)
    plaintext = json.dumps(secrets).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=AAD)
    SECRETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SECRETS_PATH.write_bytes(nonce + ciphertext)


def update_secrets(updates: dict) -> dict:
    try:
        current = decrypt_secrets()
    except Exception:
        current = {}
    for k, v in updates.items():
        if v:
            current[k] = v
        else:
            current.pop(k, None)
    _write_secrets(current)
    return current


def load_into_environ() -> int:
    try:
        secrets = decrypt_secrets()
    except CryptoUnavailable:
        return 0
    for k, v in secrets.items():
        os.environ.setdefault(k, v)
    return len(secrets)
