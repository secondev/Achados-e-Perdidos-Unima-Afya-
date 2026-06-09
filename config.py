"""
config.py â€” ConfiguraÃ§Ãµes globais do Achados Unima Afya

Define cores da identidade visual da Afya (magenta), fontes,
tamanhos, paletas claro/escuro e a chave da API ImgBB.
"""

# ============================================
# IDENTIDADE VISUAL â€” CORES OFICIAIS DA AFYA
# ============================================
# Magenta Ã© fixo nas duas paletas (cor da marca)
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
    "magenta_50": "#2D0A1E",      # versÃ£o escura do magenta_50
    "magenta_100": "#4A1132",     # versÃ£o escura do magenta_100

    # Tons invertidos (fundo escuro)
    "ink_900": "#FAFAFA",         # texto principal vira branco
    "ink_700": "#E4E4E7",         # texto secundÃ¡rio claro
    "ink_500": "#A1A1AA",         # texto terciÃ¡rio cinza claro
    "ink_400": "#71717A",         # texto fraco
    "ink_300": "#52525B",         # bordas mais visÃ­veis
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
# Tema atual (comeÃ§a em light por padrÃ£o)
_tema_atual = "light"

# COLORS aponta dinamicamente pra paleta atual
# IMPORTANTE: as telas leem COLORS["chave"], entÃ£o quando alteramos
# o tema, todas as referÃªncias futuras pegam as novas cores
COLORS = dict(LIGHT_THEME)


def get_tema():
    """Retorna o tema atual ('light' ou 'dark')."""
    return _tema_atual


def alternar_tema():
    """
    Alterna entre tema claro e escuro.
    Atualiza o dicionÃ¡rio COLORS in-place pra que as referÃªncias
    existentes nas telas peguem as novas cores ao re-renderizar.
    """
    global _tema_atual

    if _tema_atual == "light":
        _tema_atual = "dark"
        nova_paleta = DARK_THEME
    else:
        _tema_atual = "light"
        nova_paleta = LIGHT_THEME

    # Atualiza COLORS in-place (mantÃ©m a referÃªncia)
    COLORS.clear()
    COLORS.update(nova_paleta)

    return _tema_atual


def aplicar_tema(tema):
    """
    Define o tema explicitamente ('light' ou 'dark').
    Ãštil pra carregar preferÃªncia salva.
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
    {"id": 1, "nome": "Material escolar", "icone": "ðŸ“š"},
    {"id": 2, "nome": "EletrÃ´nicos", "icone": "ðŸŽ§"},
    {"id": 3, "nome": "Roupas", "icone": "ðŸ‘•"},
    {"id": 4, "nome": "Documentos", "icone": "ðŸ’³"},
    {"id": 5, "nome": "AcessÃ³rios", "icone": "ðŸ”‘"},
    {"id": 6, "nome": "Garrafas/Recipientes", "icone": "ðŸ’§"},
    {"id": 7, "nome": "Outros", "icone": "ðŸ“¦"},
]

# ============================================
# LOCAIS DO CAMPUS
# ============================================
LOCAIS = [
    "Bloco A â€” Salas 101 a 120",
    "Bloco B â€” LaboratÃ³rios",
    "Bloco C â€” Salas 201 a 220",
    "Cantina principal",
    "Biblioteca",
    "AuditÃ³rio",
    "Estacionamento",
    "PÃ¡tio central",
    "NÃ£o tenho certeza",
]

# ============================================
# STATUS POSSÃVEIS
# ============================================
STATUS = {
    "aberto": "Aberto",
    "analise": "Em anÃ¡lise",
    "encontrado": "Encontrado",
    "devolvido": "Devolvido",
    "naoachado": "NÃ£o encontrado",
}

# ============================================
# API IMGBB
# ============================================
IMGBB_API_KEY = ""

# ============================================
# CONFIGURAÃ‡Ã•ES DA JANELA
# ============================================
APP_TITLE = "Achados Unima Afya"
APP_WIDTH = 1200
APP_HEIGHT = 760
APP_MIN_WIDTH = 1000
APP_MIN_HEIGHT = 650

# ============================================
# API RESEND (notificaÃ§Ãµes por email)
# ============================================
# Para envio real de emails, crie conta gratuita em https://resend.com
# Gere uma API key em: https://resend.com/api-keys
# Cole a key abaixo. Sem ela, o sistema funciona em modo SIMULAÃ‡ÃƒO
# (apenas registra no terminal o email que seria enviado)
RESEND_API_KEY = ""

# Email remetente (deve ser de domÃ­nio verificado na Resend)
# Por padrÃ£o, a Resend permite usar "onboarding@resend.dev" para testes
RESEND_FROM_EMAIL = "Achados Unima <onboarding@resend.dev>"

# MODO DEMO: se True, todos os emails (independente do destinatÃ¡rio real)
# sÃ£o enviados para EMAIL_DESTINATARIO_DEMO. Ãštil para apresentaÃ§Ã£o:
# o professor recebe todos os emails na prÃ³pria caixa dele para visualizar.
EMAIL_MODO_DEMO = True
EMAIL_DESTINATARIO_DEMO = "alanmaiacomercial@gmail.com"  # ALTERE PARA SEU EMAIL

# Master switch: desligar emails para apresentaÃ§Ãµes sem internet
EMAIL_ENABLED = True
