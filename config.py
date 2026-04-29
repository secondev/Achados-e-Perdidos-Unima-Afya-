"""
config.py — Configurações globais do Achados Unima Afya

Define cores da identidade visual da Afya (magenta), fontes,
tamanhos, paletas claro/escuro e a chave da API ImgBB.
"""

# ============================================
# IDENTIDADE VISUAL — CORES OFICIAIS DA AFYA
# ============================================
# Magenta é fixo nas duas paletas (cor da marca)
MAGENTA = "#E6007E"
MAGENTA_DARK = "#B30062"
MAGENTA_LIGHT = "#FF4DA6"
MAGENTA_50 = "#FDF2F8"
MAGENTA_100 = "#FCE7F3"

# ============================================
# PALETA TEMA CLARO
# ============================================
LIGHT_THEME = {
    # Magenta (cor da marca)
    "magenta": MAGENTA,
    "magenta_dark": MAGENTA_DARK,
    "magenta_light": MAGENTA_LIGHT,
    "magenta_50": MAGENTA_50,
    "magenta_100": MAGENTA_100,

    # Tons de cinza (fundo claro)
    "ink_900": "#0A0A0B",
    "ink_700": "#27272A",
    "ink_500": "#52525B",
    "ink_400": "#71717A",
    "ink_300": "#A1A1AA",
    "ink_200": "#D4D4D8",
    "ink_100": "#E4E4E7",
    "ink_50": "#F4F4F5",
    "ink_25": "#FAFAFA",
    "white": "#FFFFFF",

    # Status (cores fixas pros badges)
    "status_aberto_bg": "#F4F4F5",
    "status_aberto_fg": "#52525B",
    "status_analise_bg": "#FEF3C7",
    "status_analise_fg": "#92400E",
    "status_encontrado_bg": "#DBEAFE",
    "status_encontrado_fg": "#1E40AF",
    "status_devolvido_bg": "#D1FAE5",
    "status_devolvido_fg": "#065F46",
    "status_naoachado_bg": "#FEE2E2",
    "status_naoachado_fg": "#991B1B",

    # Outros
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
}

# ============================================
# PALETA TEMA ESCURO
# ============================================
DARK_THEME = {
    # Magenta (cor da marca - mesma)
    "magenta": MAGENTA,
    "magenta_dark": MAGENTA_DARK,
    "magenta_light": MAGENTA_LIGHT,
    "magenta_50": "#2D0A1E",      # versão escura do magenta_50
    "magenta_100": "#4A1132",     # versão escura do magenta_100

    # Tons invertidos (fundo escuro)
    "ink_900": "#FAFAFA",         # texto principal vira branco
    "ink_700": "#E4E4E7",         # texto secundário claro
    "ink_500": "#A1A1AA",         # texto terciário cinza claro
    "ink_400": "#71717A",         # texto fraco
    "ink_300": "#52525B",         # bordas mais visíveis
    "ink_200": "#3F3F46",         # bordas
    "ink_100": "#27272A",         # bordas sutis e fundo de cards
    "ink_50": "#1F1F23",          # fundo de elementos
    "ink_25": "#18181B",          # fundo principal
    "white": "#27272A",           # "branco" no escuro = cinza escuro (cards)

    # Status (cores adaptadas pro dark)
    "status_aberto_bg": "#3F3F46",
    "status_aberto_fg": "#D4D4D8",
    "status_analise_bg": "#451A03",
    "status_analise_fg": "#FCD34D",
    "status_encontrado_bg": "#1E3A5F",
    "status_encontrado_fg": "#93C5FD",
    "status_devolvido_bg": "#064E3B",
    "status_devolvido_fg": "#6EE7B7",
    "status_naoachado_bg": "#7F1D1D",
    "status_naoachado_fg": "#FCA5A5",

    # Outros
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
}

# ============================================
# GERENCIADOR DE TEMA
# ============================================
# Tema atual (começa em light por padrão)
_tema_atual = "light"

# COLORS aponta dinamicamente pra paleta atual
# IMPORTANTE: as telas leem COLORS["chave"], então quando alteramos
# o tema, todas as referências futuras pegam as novas cores
COLORS = dict(LIGHT_THEME)


def get_tema():
    """Retorna o tema atual ('light' ou 'dark')."""
    return _tema_atual


def alternar_tema():
    """
    Alterna entre tema claro e escuro.
    Atualiza o dicionário COLORS in-place pra que as referências
    existentes nas telas peguem as novas cores ao re-renderizar.
    """
    global _tema_atual

    if _tema_atual == "light":
        _tema_atual = "dark"
        nova_paleta = DARK_THEME
    else:
        _tema_atual = "light"
        nova_paleta = LIGHT_THEME

    # Atualiza COLORS in-place (mantém a referência)
    COLORS.clear()
    COLORS.update(nova_paleta)

    return _tema_atual


def aplicar_tema(tema):
    """
    Define o tema explicitamente ('light' ou 'dark').
    Útil pra carregar preferência salva.
    """
    global _tema_atual

    if tema == "dark":
        _tema_atual = "dark"
        nova_paleta = DARK_THEME
    else:
        _tema_atual = "light"
        nova_paleta = LIGHT_THEME

    COLORS.clear()
    COLORS.update(nova_paleta)

    return _tema_atual


# ============================================
# FONTES
# ============================================
FONTS = {
    "title_xl": ("Segoe UI", 28, "bold"),
    "title_lg": ("Segoe UI", 22, "bold"),
    "title_md": ("Segoe UI", 18, "bold"),
    "title_sm": ("Segoe UI", 16, "bold"),
    "body_lg": ("Segoe UI", 14),
    "body_md": ("Segoe UI", 13),
    "body_sm": ("Segoe UI", 12),
    "body_xs": ("Segoe UI", 11),
    "label": ("Segoe UI", 12, "bold"),
}

# ============================================
# CATEGORIAS DE ITENS
# ============================================
CATEGORIAS = [
    {"id": 1, "nome": "Material escolar", "icone": "📚"},
    {"id": 2, "nome": "Eletrônicos", "icone": "🎧"},
    {"id": 3, "nome": "Roupas", "icone": "👕"},
    {"id": 4, "nome": "Documentos", "icone": "💳"},
    {"id": 5, "nome": "Acessórios", "icone": "🔑"},
    {"id": 6, "nome": "Garrafas/Recipientes", "icone": "💧"},
    {"id": 7, "nome": "Outros", "icone": "📦"},
]

# ============================================
# LOCAIS DO CAMPUS
# ============================================
LOCAIS = [
    "Bloco A — Salas 101 a 120",
    "Bloco B — Laboratórios",
    "Bloco C — Salas 201 a 220",
    "Cantina principal",
    "Biblioteca",
    "Auditório",
    "Estacionamento",
    "Pátio central",
    "Não tenho certeza",
]

# ============================================
# STATUS POSSÍVEIS
# ============================================
STATUS = {
    "aberto": "Aberto",
    "analise": "Em análise",
    "encontrado": "Encontrado",
    "devolvido": "Devolvido",
    "naoachado": "Não encontrado",
}

# ============================================
# API IMGBB
# ============================================
IMGBB_API_KEY = ""

# ============================================
# CONFIGURAÇÕES DA JANELA
# ============================================
APP_TITLE = "Achados Unima Afya"
APP_WIDTH = 1200
APP_HEIGHT = 760
APP_MIN_WIDTH = 1000
APP_MIN_HEIGHT = 650
