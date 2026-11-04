"""Configurações centralizadas da aplicação de Peritagem Técnica KGF."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Configuração base da aplicação Flask."""

    SECRET_KEY: str = os.getenv("SECRET_KEY", "kgf-peritagem-secret-key")
    UPLOAD_FOLDER: str = os.getenv(
        "UPLOAD_FOLDER", str(BASE_DIR / "uploads")
    )
    LAUDO_FOLDER: str = os.getenv(
        "LAUDO_FOLDER", str(BASE_DIR / "laudos")
    )
    FOTOS_SERVIDOR_DIR: str = os.getenv(
        "FOTOS_SERVIDOR_DIR", "/mnt/fotos-servidor"
    )

    # Limite máximo de upload: 32 MB
    MAX_CONTENT_LENGTH: int = int(
        os.getenv("MAX_CONTENT_LENGTH", str(32 * 1024 * 1024))
    )

    # Configurações de processamento de imagem
    IMAGE_TARGET_SIZE: int = int(os.getenv("IMAGE_TARGET_SIZE", "600"))
    IMAGE_JPEG_QUALITY: int = int(os.getenv("IMAGE_JPEG_QUALITY", "85"))
    ALLOWED_EXTENSIONS: set[str] = {
        "png",
        "jpg",
        "jpeg",
        "webp",
        "bmp",
        "gif",
        "heic",
        "heif",
    }

