"""
screens/admin.py — Painel do funcionário

Mural com:
- Lista de perdas reportadas (com filtro por status, busca multi-campo)
- Filtros visuais
- Acesso ao detalhe + chat de cada caso
"""

import customtkinter as ctk
from config import COLORS
from components.widgets import AppBar, ItemCard, SearchBar
import database as db


class AdminPanel(ctk.CTkFrame):
    def __init__(self, parent, usuario, on_navigate, on_logout, **kwargs):
        super().__init__(parent, fg_color=COLORS["ink_25"], corner_radius=0)
        self.usuario = usuario
        self.on_navigate = on_navigate
        self.on_logout = on_logout

        self.busca_atual = ""
        self.status_atual = "aberto"
        self.status_buttons = {}

        self._build()

    def _build(self):
        # App bar
        app_bar = AppBar(
            self,
            self.usuario,
            self.on_logout,
            nav_atual="admin",
            on_nav=self.on_navigate,
            subtitle="Painel Administrativo"
        )
        app_bar.pack(fill="x", side="top")

        # Body
        body = ctk.CTkScrollableFrame(self, fg_color=COLORS["ink_25"], corner_radius=0)
        body.pack(fill="both", expand=True)

        wrapper = ctk.CTkFrame(body, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=40, pady=24)

        # Título
        ctk.CTkLabel(
            wrapper,
            text="Mural de gestão",
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["ink_900"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            wrapper,
            text="Triagem das solicitações dos alunos.",
            font=("Segoe UI", 12),
            text_color=COLORS["ink_500"]
        ).pack(anchor="w", pady=(2, 20))

        # Toolbar
        toolbar = ctk.CTkFrame(wrapper, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 20))

        # Busca
        self.search = SearchBar(
            toolbar,
            placeholder="Buscar por aluno, item ou palavra-chave...",
            on_change=self._on_busca
        )
        self.search.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # Filtros de status
        filter_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        filter_frame.pack(side="left")

        status_options = [
            ("aberto", "Aberto"),
            ("analise", "Em análise"),
            ("encontrado", "Encontrado"),
        ]

        for valor, texto in status_options:
            btn = self._criar_filter_btn(filter_frame, texto, valor, ativo=(valor == "aberto"))
            btn.pack(side="left", padx=2)
            self.status_buttons[valor] = btn

        # ============================================
        # BOTÃO PARA O NOVO DASHBOARD
        # ============================================
        btn_stats = ctk.CTkButton(
            toolbar,
            text="📊 Dashboard",
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["magenta"],
            text_color=COLORS["white"],
            hover_color=COLORS["magenta_dark"],
            height=36,
            command=lambda: self.on_navigate("dashboard")
        )
        btn_stats.pack(side="right", padx=(12, 0))

        # Container da lista
        self.list_container = ctk.CTkFrame(wrapper, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True)

        self._renderizar_lista()

    def _criar_filter_btn(self, parent, texto, valor, ativo=False):
        return ctk.CTkButton(
            parent,
            text=texto,
            font=("Segoe UI", 11, "bold" if ativo else "normal"),
            fg_color=COLORS["ink_900"] if ativo else COLORS["white"],
            text_color=COLORS["white"] if ativo else COLORS["ink_700"],
            border_color=COLORS["ink_100"],
            border_width=1,
            hover_color=COLORS["ink_200"] if not ativo else COLORS["ink_700"],
            corner_radius=10,
            height=36, width=100,
            command=lambda v=valor: self._on_filtro(v)
        )

    def _on_busca(self, texto):
        self.busca_atual = texto
        self._renderizar_lista()

    def _on_filtro(self, valor):
        self.status_atual = valor
        for v, btn in self.status_buttons.items():
            if v == valor:
                btn.configure(
                    fg_color=COLORS["ink_900"],
                    text_color=COLORS["white"],
                    font=("Segoe UI", 11, "bold")
                )
            else:
                btn.configure(
                    fg_color=COLORS["white"],
                    text_color=COLORS["ink_700"],
                    font=("Segoe UI", 11)
                )
        self._renderizar_lista()

    def _renderizar_lista(self):
        for w in self.list_container.winfo_children():
            w.destroy()

        itens = db.listar_todas_perdas(
            status_filtro=self.status_atual,
            busca=self.busca_atual or None
        )

        if not itens:
            empty = ctk.CTkFrame(
                self.list_container,
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
                text="📭\nNenhuma solicitação com esse filtro.",
                font=("Segoe UI", 12),
                text_color=COLORS["ink_400"],
                justify="center"
            ).pack(expand=True)
            return

        for item in itens:
            card = ItemCard(
                self.list_container,
                item,
                mostrar_aluno=True,
                on_click=lambda i: self.on_navigate("detalhe", i)
            )
            card.pack(fill="x", pady=4)