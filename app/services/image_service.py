"""Serviço de processamento e padronização de imagens para os laudos."""

import logging
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def tratar_imagem_quadrada(
    caminho_origem: str, tamanho: int = 600, qualidade: int = 85
) -> bool:
    """
    Corrige a orientação EXIF da imagem, corta em proporção 1:1 centralizada
    e redimensiona para `tamanho` x `tamanho` pixels em formato JPEG.

    Args:
        caminho_origem: Caminho completo do arquivo de imagem salvo.
        tamanho: Dimensão final (largura e altura) em pixels.
        qualidade: Qualidade da compressão JPEG (1 a 100).

    Returns:
        True se a imagem foi processada com sucesso, False caso contrário.
    """
    try:
        with Image.open(caminho_origem) as img_original:
            # Corrige rotação automática de fotos tiradas por celulares (EXIF)
            img = ImageOps.exif_transpose(img_original)

            # Converte para RGB caso seja RGBA, P (paleta) ou outro modo
            if img.mode != "RGB":
                img = img.convert("RGB")

            largura, altura = img.size
            novo_lado = min(largura, altura)

            esquerda = (largura - novo_lado) / 2
            topo = (altura - novo_lado) / 2
            direita = (largura + novo_lado) / 2
            base = (altura + novo_lado) / 2

            img = img.crop((esquerda, topo, direita, base))

            resample_filter = getattr(
                Image, "Resampling", Image
            ).LANCZOS
            img = img.resize((tamanho, tamanho), resample_filter)
            img.save(caminho_origem, "JPEG", quality=qualidade)

        return True
    except Exception as exc:
        logger.error(
            "Erro ao processar imagem '%s': %s", caminho_origem, exc
        )
        return False

