"""
Serviço de armazenamento e integração com o servidor de fotos (/mnt/fotos-servidor).

IMPORTANTE:
O diretório /mnt/fotos-servidor é um compartilhamento crítico de produção.
Este módulo NUNCA deve remover, renomear ou mover arquivos/pastas existentes.
Sua única ação de escrita permitida é copiar o arquivo PDF do laudo gerado
para dentro da pasta correspondente à Ordem de Serviço (OS).
"""

import logging
import os
import re
import shutil
from typing import Optional

logger = logging.getLogger(__name__)


def sanitizar_identificador_os(os_num: str) -> str:
    """
    Limpa o identificador da OS para uso seguro em nomes de arquivos e buscas,
    removendo barras, pontos de navegação (..) e espaços nas extremidades.
    """
    if not os_num:
        return ""
    limpo = os_num.strip()
    # Substitui barras ou caracteres inválidos de caminho por hífen
    limpo = re.sub(r"[\\/:\*\?\"<>\|]+", "-", limpo)
    limpo = limpo.replace("..", "")
    return limpo.strip(" .-")


def encontrar_pasta_os(
    os_num: str, base_dir: str = "/mnt/fotos-servidor"
) -> Optional[str]:
    """
    Localiza o diretório correspondente à OS dentro de `base_dir`.

    A estrutura padrão do servidor organiza as pastas por ano no formato:
      /mnt/fotos-servidor/Fotos 2026/<OS>
      /mnt/fotos-servidor/Fotos 2025/<OS>
      /mnt/fotos-servidor/Fotos 2024/<OS>

    Para evitar varreduras lentas em rede (CIFS/SMB com milhares de pastas),
    realiza verificação direta O(1) (`os.path.isdir`) nas pastas anuais
    ordenadas do ano mais recente para o mais antigo.

    Args:
        os_num: Número da Ordem de Serviço informada no formulário.
        base_dir: Caminho base do servidor de fotos.

    Returns:
        Caminho absoluto da pasta da OS se encontrada, ou None.
    """
    os_limpa = sanitizar_identificador_os(os_num)
    if not os_limpa:
        return None

    if not os.path.isdir(base_dir):
        logger.warning(
            "Diretório base do servidor de fotos não acessível: %s", base_dir
        )
        return None

    # Candidatos de nomes de pasta para a OS (ex: valor limpo e apenas dígitos caso haja prefixo)
    candidatos_os = [os_limpa]
    apenas_digitos = re.sub(r"\D+", "", os_limpa)
    if apenas_digitos and apenas_digitos not in candidatos_os:
        candidatos_os.append(apenas_digitos)

    try:
        entradas_topo = os.listdir(base_dir)
    except OSError as exc:
        logger.error(
            "Erro ao ler nível superior de '%s': %s", base_dir, exc
        )
        return None

    # Filtra pastas anuais (ex: "Fotos 2026", "Fotos 2025") ordenadas da mais recente para a mais antiga
    pastas_fotos_ano = sorted(
        [
            nome
            for nome in entradas_topo
            if nome.lower().startswith("fotos")
            and os.path.isdir(os.path.join(base_dir, nome))
        ],
        reverse=True,
    )

    # 1. Busca direta O(1) dentro de cada pasta "Fotos YYYY/<OS>"
    for pasta_ano in pastas_fotos_ano:
        caminho_ano = os.path.join(base_dir, pasta_ano)
        for candidato in candidatos_os:
            caminho_os = os.path.join(caminho_ano, candidato)
            if os.path.isdir(caminho_os):
                return caminho_os

    # 2. Verifica também diretamente na raiz de base_dir/<OS>
    for candidato in candidatos_os:
        caminho_direto = os.path.join(base_dir, candidato)
        if os.path.isdir(caminho_direto):
            return caminho_direto

    logger.info(
        "Pasta da OS '%s' não encontrada em '%s'.", os_limpa, base_dir
    )
    return None


def salvar_pdf_no_servidor(
    caminho_pdf_local: str,
    os_num: str,
    base_dir: str = "/mnt/fotos-servidor",
) -> Optional[str]:
    """
    Copia o PDF gerado localmente para a pasta correspondente da OS em `base_dir`.

    Nenhuma pasta ou arquivo existente é removido ou renomeado.

    Args:
        caminho_pdf_local: Caminho do arquivo PDF já gerado localmente.
        os_num: Número da Ordem de Serviço.
        base_dir: Diretório raiz do servidor de fotos.

    Returns:
        Caminho completo do PDF salvo no servidor de fotos em caso de sucesso,
        ou None caso a pasta da OS não seja encontrada ou ocorra falha de I/O.
    """
    if not os.path.isfile(caminho_pdf_local):
        logger.error("PDF local não encontrado para cópia: %s", caminho_pdf_local)
        return None

    pasta_os = encontrar_pasta_os(os_num, base_dir=base_dir)
    if not pasta_os:
        return None

    nome_arquivo = os.path.basename(caminho_pdf_local)
    destino_pdf = os.path.join(pasta_os, nome_arquivo)

    try:
        shutil.copyfile(caminho_pdf_local, destino_pdf)
        logger.info(
            "PDF da OS '%s' salvo com sucesso no servidor: %s",
            os_num,
            destino_pdf,
        )
        return destino_pdf
    except OSError as exc:
        logger.error(
            "Falha ao copiar PDF para '%s': %s", destino_pdf, exc
        )
        return None

