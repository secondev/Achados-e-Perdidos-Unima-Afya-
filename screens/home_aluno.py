"""
screens/home_aluno.py — Tela inicial do aluno

Dashboard com:
- Saudação personalizada
- Cards de métricas (status das solicitações)
- CTA para cadastrar nova perda
- Lista de solicitações ativas
"""

import customtkinter as ctk
from config import COLORS
from components.widgets import AppBar, StatCard, ItemCard
import database as db


class HomeAluno(ctk.CTkFrame):
    def __init__(self, parent, usuario, on_navigate, on_logout):
        super().__init__(parent, fg_color=COLORS["ink_25"], corner_radius=0)
        self.usuario = usuario
        self.on_navigate = on_navigate
        self.on_logout = on_logout

        self._build()

    def _build(self):
        # App bar superior
        app_bar = AppBar(
            self,
            self.usuario,
            self.on_logout,
            nav_atual="inicio",
            on_nav=self.on_navigate
        )
        app_bar.pack(fill="x", side="top")

        # Container scrollável do corpo
        body = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["ink_25"],
            corner_radius=0
        )
        body.pack(fill="both", expand=True, padx=0, pady=0)

        # Wrapper para limitar largura
        wrapper = ctk.CTkFrame(body, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=40, pady=24)

        # Saudação
        primeiro_nome = self.usuario["nome"].split()[0]
        ctk.CTkLabel(
            wrapper,
            text=f"Olá, {primeiro_nome} 👋",
            font=("Segoe UI", 26, "bold"),
            text_color=COLORS["ink_900"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            wrapper,
            text="Aqui está o resumo das suas solicitações ativas.",
            font=("Segoe UI", 13),
            text_color=COLORS["ink_500"]
        ).pack(anchor="w", pady=(2, 24))

        # Cards de métricas
        self._criar_stats(wrapper)

        # CTA hero
        self._criar_cta(wrapper)

        # Lista de solicitações
        self._criar_lista_solicitacoes(wrapper)

    def _criar_stats(self, parent):
        """Cria os 4 cards de métricas."""
        contadores = db.contar_status(self.usuario["id"])

        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1, uniform="stat")

        cards_data = [
            ("📬", contadores["aberto"], "Em aberto"),
            ("⏳", contadores["analise"], "Em análise"),
            ("✅", contadores["devolvido"] + contadores["encontrado"], "Resolvidos"),
            ("📦", contadores["disponiveis"], "Disponíveis"),
        ]

        for i, (icone, num, lbl) in enumerate(cards_data):
            card = StatCard(stats_frame, icone, num, lbl)
            card.grid(row=0, column=i, padx=4, sticky="ew")

    def _criar_cta(self, parent):
        """Banner magenta de chamada para cadastrar perda."""
        cta = ctk.CTkFrame(
            parent,
            fg_color=COLORS["magenta"],
            corner_radius=16,
            height=100
        )
        cta.pack(fill="x", pady=(0, 24))
        cta.pack_propagate(False)

        inner = ctk.CTkFrame(cta, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        text_frame = ctk.CTkFrame(inner, fg_color="transparent")
        text_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            text_frame,
            text="Perdeu algo no campus?",
            font=("Segoe UI", 17, "bold"),
            text_color=COLORS["white"],
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame,
            text="Cadastre o item e acompanhe o status pelo chat.",
            font=("Segoe UI", 12),
            text_color=COLORS["white"],
            anchor="w"
        ).pack(anchor="w", pady=(2, 0))

        # Botão branco
        btn = ctk.CTkButton(
            inner,
            text="Cadastrar perda  →",
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["white"],
            text_color=COLORS["magenta"],
            hover_color=COLORS["magenta_50"],
            corner_radius=10,
            height=40, width=160,
            command=lambda: self.on_navigate("cadastrar")
        )
        btn.pack(side="right")

    def _criar_lista_solicitacoes(self, parent):
        """Lista as solicitações ativas do aluno."""
        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        itens = db.listar_itens_usuario(self.usuario["id"])
        ativas = [i for i in itens if i["status"] in ("aberto", "analise", "encontrado")]
        devolvidos = [i for i in itens if i["status"] == "devolvido"]

        ctk.CTkLabel(
            header,
            text=f"Minhas solicitações ativas",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS["ink_700"]
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=f"  {len(ativas)}  ",
            font=("Segoe UI", 11, "bold"),
            fg_color=COLORS["ink_100"],
            text_color=COLORS["ink_500"],
            corner_radius=12,
            height=22
        ).pack(side="left", padx=(8, 0))

        # Lista de itens
        if not ativas:
            empty = ctk.CTkFrame(
                parent,
                fg_color=COLORS["white"],
                border_color=COLORS["ink_100"],
                border_width=1,
                corner_radius=12,
                height=120
            )
            empty.pack(fill="x")
            empty.pack_propagate(False)

            ctk.CTkLabel(
                empty,
                text="📭\nNenhuma solicitação ativa.\nCadastre uma perda para começar.",
                font=("Segoe UI", 12),
                text_color=COLORS["ink_400"],
                justify="center"
            ).pack(expand=True)
        else:
            for item in ativas:
                card = ItemCard(
                    parent,
                    item,
                    on_click=lambda i: self.on_navigate("detalhe", i)
                )
                card.pack(fill="x", pady=4)

        if devolvidos:
            ctk.CTkLabel(
                parent,
                text="Itens devolvidos",
                font=("Segoe UI", 14, "bold"),
                text_color=COLORS["ink_700"],
            ).pack(anchor="w", pady=(24, 8))

            ctk.CTkLabel(
                parent,
                text="Clique em um caso devolvido para avaliar o atendimento.",
                font=("Segoe UI", 11),
                text_color=COLORS["ink_500"],
                wraplength=720,
                justify="left"
            ).pack(anchor="w", pady=(0, 12))

            for item in devolvidos:
                card = ItemCard(
                    parent,
                    item,
                    on_click=lambda i: self.on_navigate("detalhe", i)
                )
                card.pack(fill="x", pady=4)
