"""Cree le fichier .env avec des cles aleatoires s'il n'existe pas deja."""
import secrets
from pathlib import Path

ENV = Path(__file__).parent / ".env"


def main():
    if ENV.exists():
        print(f"[OK] {ENV.name} existe deja, rien a faire.")
        return

    ENV.write_text(
        f"SECRET_KEY={secrets.token_hex(32)}\n"
        f"JWT_SECRET_KEY={secrets.token_hex(32)}\n",
        encoding="utf-8",
    )
    print(f"[OK] {ENV.name} cree avec de nouvelles cles.")


if __name__ == "__main__":
    main()
