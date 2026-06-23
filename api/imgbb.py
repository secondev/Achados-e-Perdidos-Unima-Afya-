"""
api/imgbb.py — Cliente da API ImgBB (consumo de API externa)

Faz upload de imagens para o ImgBB (gratuito, sem limite mensal)
e retorna a URL pública para armazenar no banco.

Atende ao requisito do professor de "consumo de API externa".

Documentação oficial: https://api.imgbb.com
"""

import base64
import requests
import os
from config import IMGBB_API_KEY


IMGBB_URL = "https://api.imgbb.com/1/upload"


def upload_imagem(caminho_arquivo):
    """
    Faz upload de uma imagem para o ImgBB.

    Args:
        caminho_arquivo: caminho local da imagem (ex: 'C:/fotos/item.jpg')

    Returns:
        URL pública da imagem hospedada, ou None se falhar.

    Se a API key não estiver configurada (modo offline), retorna apenas
    o nome do arquivo (suficiente para demo, mas a imagem não fica online).
    """
    if not os.path.exists(caminho_arquivo):
        return None

    # Se não tem API key configurada, modo offline: retorna só o nome
    if not IMGBB_API_KEY:
        return f"local://{os.path.basename(caminho_arquivo)}"

    try:
        # Lê o arquivo e converte para base64 (formato exigido pela API)
        with open(caminho_arquivo, "rb") as f:
            imagem_b64 = base64.b64encode(f.read()).decode("utf-8")

        # Faz a requisição POST para a API
        response = requests.post(
            IMGBB_URL,
            data={
                "key": IMGBB_API_KEY,
                "image": imagem_b64,
            },
            timeout=30,
        )

        # Verifica resposta
        if response.status_code == 200:
            dados = response.json()
            if dados.get("success"):
                return dados["data"]["url"]

        print(f"Erro no upload ImgBB: {response.status_code}")
        return None

    except Exception as e:
        print(f"Exceção no upload ImgBB: {e}")
        # Fallback: retorna o caminho local em caso de erro
        return f"local://{os.path.basename(caminho_arquivo)}"


def is_url_valida(url):
    """Verifica se uma URL de imagem está acessível."""
    if not url or url.startswith("local://"):
        return False
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False
