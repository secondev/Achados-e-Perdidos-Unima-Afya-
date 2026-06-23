"""
screens/descarte.py — Galeria de itens expirados (Mais de 30 dias)

Mostra os itens que ultrapassaram o prazo de 30 dias na instituição,
permitindo ao funcionário gerenciar o destino (descarte/doação).
"""

import customtkinter as ctk
from config import COLORS, CATEGORIAS
from components.widgets import AppBar, GalleryCard, SearchBar
import database as db


class ItensExpirados(ctk.CTkFrame):
    def __init__(self, parent, usuario, on_navigate, on_logout):
        super().__init__(parent, fg_color=COLORS["ink_25"], corner_radius=0)
        self.usuario = usuario
        self.on_navigate = on_navigate
        self.on_logout = on_logout

        self.busca_atual = ""
        self.categoria_atual = None
        self.filter_buttons = {}

        self._build()

    def _build(self):
        # App bar
        app_bar = AppBar(
            self,
            self.usuario,
            self.on_logout,
            nav_atual="descarte",
            on_nav=self.on_navigate
        )
        app_bar.pack(fill="x", side="top")

        # Body
        body = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["ink_25"], corner_radius=0)
        body.pack(fill="both", expand=True)

        wrapper = ctk.CTkFrame(body, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=40, pady=24)

        # Título da Área de Descarte
        ctk.CTkLabel(
            wrapper,
            text="Setor de Descarte e Doações (>30 dias)",
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["ink_900"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            wrapper,
            text="Estes itens ultrapassaram o prazo regulamentar de 30 dias e estão prontos para triagem.",
            font=("Segoe UI", 12),
            text_color=COLORS["ink_500"]
        ).pack(anchor="w", pady=(2, 20))

        # Toolbar (busca + filtros)
        toolbar = ctk.CTkFrame(wrapper, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 20))

        # Busca
        self.search = SearchBar(
            toolbar,
            placeholder="Buscar nos itens expirados...",
            on_change=self._on_busca
        )
        self.search.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # Filtros de categoria
        filter_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        filter_frame.pack(side="left")

        # Botão "Todas"
        btn_todas = self._criar_filter_btn(
            filter_frame, "Todas", None, ativo=True)
        btn_todas.pack(side="left", padx=2)
        self.filter_buttons[None] = btn_todas

        for cat in CATEGORIAS[:4]:
            btn = self._criar_filter_btn(
                filter_frame, cat["nome"][:12], cat["nome"])
            btn.pack(side="left", padx=2)
            self.filter_buttons[cat["nome"]] = btn

        # Container da galeria
        self.gallery_container = ctk.CTkFrame(wrapper, fg_color="transparent")
        self.gallery_container.pack(fill="both", expand=True)

        self._renderizar_galeria()

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
        self._renderizar_galeria()

    def _on_filtro(self, valor):
        self.categoria_atual = valor
        for v, btn in self.filter_buttons.items():
            if v == valor:
                btn.configure(fg_color=COLORS["ink_900"], text_color=COLORS["white"], font=(
                    "Segoe UI", 11, "bold"))
            else:
                btn.configure(
                    fg_color=COLORS["white"], text_color=COLORS["ink_700"], font=("Segoe UI", 11))
        self._renderizar_galeria()

    def _renderizar_galeria(self):
        for w in self.gallery_container.winfo_children():
            w.destroy()

        # CHAMA A FUNÇÃO DA PR 1:
        itens = db.listar_itens_expirados(
            busca=self.busca_atual or None,
            categoria=self.categoria_atual
        )

        if not itens:
            empty = ctk.CTkFrame(
                self.gallery_container,
                fg_color=COLORS["white"],
                border_color=COLORS["ink_100"],
                border_width=1,
                corner_radius=12,
                height=160
            )
            empty.pack(fill="x")
            empty.pack_propagate(False)

            ctk.CTkLabel(
                empty,
                text="✅\nNenhum item expirado encontrado no momento.\nTudo limpo e dentro do prazo!",
                font=("Segoe UI", 12),
                text_color=COLORS["ink_400"],
                justify="center"
            ).pack(expand=True)
            return

        # Grid de cards (4 colunas)
        grid = ctk.CTkFrame(self.gallery_container, fg_color="transparent")
        grid.pack(fill="x")

        for i in range(4):
            grid.grid_columnconfigure(i, weight=1, uniform="col")

        for i, item in enumerate(itens):
            # Criamos uma cópia para injetar um aviso visual customizado no card sem alterar a estrutura padrão
            item_modificado = dict(item)
            item_modificado["local"] = f"⚠️ EXPIRADO ({item['dias_passados']} dias atrás)"

            card = GalleryCard(
                grid,
                item_modificado,
                on_click=lambda it: self.on_navigate(
                    "detalhe", {"id": it["id"]})
            )
            card.grid(row=i // 4, column=i % 4, padx=8, pady=8, sticky="nsew")
