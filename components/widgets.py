"""
components/widgets.py — Componentes visuais reutilizáveis

Centraliza widgets que aparecem em várias telas:
- AppBar (barra superior com logo, navegação e usuário)
- StatusBadge (selo colorido de status)
- ItemCard (card de item perdido/achado)
- StatCard (card de métrica)
- IconLabel (ícone + texto)
"""

import customtkinter as ctk
from config import COLORS, FONTS, STATUS
import database as db


# ============================================
# APP BAR — barra superior
# ============================================
class AppBar(ctk.CTkFrame):
    """Barra superior com brand, navegação e usuário logado."""

    def __init__(self, parent, usuario, on_logout, nav_atual="inicio", on_nav=None, subtitle=None):
        super().__init__(parent, fg_color=COLORS["white"], height=64,
                         corner_radius=0, border_width=0)
        self.usuario = usuario
        self.on_logout = on_logout
        self.on_nav = on_nav
        self.nav_atual = nav_atual

        # Linha de borda inferior
        self.configure(border_width=0)

        # Container interno
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=12)

        # === Brand (esquerda) ===
        brand_frame = ctk.CTkFrame(inner, fg_color="transparent")
        brand_frame.pack(side="left")

        logo_label = ctk.CTkLabel(
            brand_frame,
            text="A",
            width=36, height=36,
            corner_radius=8,
            fg_color=COLORS["magenta"],
            text_color=COLORS["white"],
            font=("Segoe UI", 16, "bold")
        )
        logo_label.pack(side="left")

        text_frame = ctk.CTkFrame(brand_frame, fg_color="transparent")
        text_frame.pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            text_frame,
            text="Achados Unima",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS["ink_900"]
        ).pack(anchor="w")

        sub = subtitle if subtitle else ("Painel Administrativo" if usuario["tipo"] == "funcionario" else "Afya Maceió")
        ctk.CTkLabel(
            text_frame,
            text=sub,
            font=("Segoe UI", 10),
            text_color=COLORS["ink_400"]
        ).pack(anchor="w", pady=(0, 0))

        # === Navegação (centro) ===
        if usuario["tipo"] == "aluno":
            nav_items = [
                ("inicio", "Início"),
                ("cadastrar", "Cadastrar perda"),
                ("disponiveis", "Itens achados"),
            ]
        else:
            nav_items = [
                ("admin", "Mural"),
                ("disponiveis", "Itens recebidos"),
            ]

        nav_frame = ctk.CTkFrame(inner, fg_color="transparent")
        nav_frame.pack(side="left", padx=(40, 0))

        for key, label in nav_items:
            is_active = key == nav_atual
            btn = ctk.CTkButton(
                nav_frame,
                text=label,
                font=("Segoe UI", 12, "bold" if is_active else "normal"),
                fg_color=COLORS["magenta_50"] if is_active else "transparent",
                text_color=COLORS["magenta"] if is_active else COLORS["ink_500"],
                hover_color=COLORS["magenta_100"] if is_active else COLORS["magenta_50"],
                corner_radius=8,
                height=32,
                width=110 if "achados" in label.lower() or "recebidos" in label.lower() else 90,
                command=lambda k=key: on_nav(k) if on_nav else None
            )
            btn.pack(side="left", padx=2)

        # === Sininho de notificações (só para aluno) ===
        if usuario["tipo"] == "aluno" and on_nav:
            total_notif = db.contar_notificacoes(usuario["id"])

            sino_frame = ctk.CTkFrame(inner, fg_color="transparent")
            sino_frame.pack(side="right", padx=(0, 12))

            sino_btn = ctk.CTkButton(
                sino_frame,
                text="🔔",
                font=("Segoe UI", 16),
                fg_color=COLORS["ink_50"],
                text_color=COLORS["ink_700"],
                hover_color=COLORS["ink_100"],
                width=36, height=36,
                corner_radius=18,
                command=lambda: self._abrir_popup_notificacoes(sino_btn, usuario, on_nav)
            )
            sino_btn.pack()

            if total_notif > 0:
                badge = ctk.CTkLabel(
                    sino_frame,
                    text=str(total_notif) if total_notif <= 9 else "9+",
                    font=("Segoe UI", 9, "bold"),
                    fg_color=COLORS["magenta"],
                    text_color=COLORS["white"],
                    corner_radius=8,
                    width=16, height=16
                )
                badge.place(in_=sino_btn, relx=0.65, rely=0.0, anchor="n")

        # === Usuário (direita) ===
        user_frame = ctk.CTkFrame(
            inner,
            fg_color=COLORS["white"],
            border_color=COLORS["ink_100"],
            border_width=1,
            corner_radius=20,
            height=36
        )
        user_frame.pack(side="right")

        avatar = ctk.CTkLabel(
            user_frame,
            text=usuario.get("foto_url", "👤"),
            font=("Segoe UI", 14),
            width=28, height=28,
            corner_radius=14,
            fg_color=COLORS["magenta_50"]
        )
        avatar.pack(side="left", padx=(4, 8), pady=4)

        ctk.CTkLabel(
            user_frame,
            text=usuario["nome"].split()[0],
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["ink_700"]
        ).pack(side="left", padx=(0, 8))

        logout_btn = ctk.CTkButton(
            user_frame,
            text="Sair",
            font=("Segoe UI", 11),
            fg_color="transparent",
            text_color=COLORS["ink_500"],
            hover_color=COLORS["ink_100"],
            width=50, height=28,
            corner_radius=14,
            command=on_logout
        )
        logout_btn.pack(side="left", padx=(0, 4))

        # Linha divisória inferior
        divider = ctk.CTkFrame(self, fg_color=COLORS["ink_100"], height=1)
        divider.pack(side="bottom", fill="x")

    def _abrir_popup_notificacoes(self, ancora, usuario, on_nav):
        """Abre um popup dropdown com as notificações não lidas do aluno."""
        notificacoes = db.listar_notificacoes(usuario["id"])

        # Posição absoluta do sininho na tela
        ancora.update_idletasks()
        x = ancora.winfo_rootx()
        y = ancora.winfo_rooty() + ancora.winfo_height() + 4

        popup = ctk.CTkToplevel()
        popup.overrideredirect(True)          # sem barra de título
        popup.attributes("-topmost", True)
        popup.geometry(f"280x{min(60 + len(notificacoes) * 72, 360)}+{x - 220}+{y}")
        popup.configure(fg_color=COLORS["white"])

        # Fecha o popup ao clicar fora
        popup.bind("<FocusOut>", lambda e: popup.destroy())
        popup.focus_set()

        # Cabeçalho
        header = ctk.CTkFrame(popup, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(
            header,
            text="Notificações",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["ink_900"]
        ).pack(side="left")

        if notificacoes:
            ctk.CTkLabel(
                header,
                text=f"  {len(notificacoes)}  ",
                font=("Segoe UI", 10, "bold"),
                fg_color=COLORS["magenta"],
                text_color=COLORS["white"],
                corner_radius=10,
                height=20
            ).pack(side="left", padx=(6, 0))

        # Divisória
        ctk.CTkFrame(popup, fg_color=COLORS["ink_100"], height=1).pack(fill="x")

        if not notificacoes:
            ctk.CTkLabel(
                popup,
                text="🎉  Nenhuma notificação nova.",
                font=("Segoe UI", 11),
                text_color=COLORS["ink_400"]
            ).pack(pady=16)
            return

        # Lista de notificações
        lista = ctk.CTkScrollableFrame(popup, fg_color="transparent", height=260)
        lista.pack(fill="both", expand=True)

        for notif in notificacoes:
            icone = "💬" if notif["tipo"] == "mensagem" else "🔄"
            texto = (
                "Nova mensagem do setor"
                if notif["tipo"] == "mensagem"
                else "Status atualizado"
            )
            item_nome = notif["item_nome"][:28] + ("…" if len(notif["item_nome"]) > 28 else "")

            row = ctk.CTkFrame(
                lista,
                fg_color=COLORS["magenta_50"],
                corner_radius=10,
                cursor="hand2"
            )
            row.pack(fill="x", padx=10, pady=4)

            inner_row = ctk.CTkFrame(row, fg_color="transparent")
            inner_row.pack(fill="x", padx=12, pady=8)

            ctk.CTkLabel(
                inner_row,
                text=icone,
                font=("Segoe UI", 18),
                width=28
            ).pack(side="left")

            info = ctk.CTkFrame(inner_row, fg_color="transparent")
            info.pack(side="left", padx=(8, 0), fill="x", expand=True)

            ctk.CTkLabel(
                info,
                text=texto,
                font=("Segoe UI", 11, "bold"),
                text_color=COLORS["ink_900"],
                anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=item_nome,
                font=("Segoe UI", 10),
                text_color=COLORS["ink_400"],
                anchor="w"
            ).pack(anchor="w")

            def _abrir(item_id=notif["item_id"]):
                popup.destroy()
                db.marcar_notificacoes_lidas(usuario["id"], item_id)
                item = db.buscar_item(item_id)
                if item:
                    on_nav("detalhe", item)

            for w in [row, inner_row, info]:
                w.bind("<Button-1>", lambda e, fn=_abrir: fn())




# ============================================
# STATUS BADGE — selo colorido de status
# ============================================
class StatusBadge(ctk.CTkLabel):
    """Pequeno selo colorido indicando o status."""

    def __init__(self, parent, status):
        bg, fg = self._cores(status)
        texto = self._texto(status)
        super().__init__(
            parent,
            text=f"  •  {texto}  ",
            font=("Segoe UI", 11, "bold"),
            fg_color=bg,
            text_color=fg,
            corner_radius=12,
            height=24,
        )

    @staticmethod
    def _cores(status):
        mapa = {
            "aberto": (COLORS["status_aberto_bg"], COLORS["status_aberto_fg"]),
            "analise": (COLORS["status_analise_bg"], COLORS["status_analise_fg"]),
            "encontrado": (COLORS["status_encontrado_bg"], COLORS["status_encontrado_fg"]),
            "devolvido": (COLORS["status_devolvido_bg"], COLORS["status_devolvido_fg"]),
            "naoachado": (COLORS["status_naoachado_bg"], COLORS["status_naoachado_fg"]),
        }
        return mapa.get(status, mapa["aberto"])

    @staticmethod
    def _texto(status):
        return STATUS.get(status, status.title())


# ============================================
# STAT CARD — card de métrica
# ============================================
class StatCard(ctk.CTkFrame):
    """Card de métrica com ícone, número grande e label."""

    def __init__(self, parent, icone, numero, label, on_click=None):
        super().__init__(
            parent,
            fg_color=COLORS["white"],
            border_color=COLORS["ink_100"],
            border_width=1,
            corner_radius=14,
            height=100
        )
        self.on_click = on_click

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        # Ícone com fundo magenta-50
        ic_frame = ctk.CTkLabel(
            inner,
            text=icone,
            width=32, height=32,
            corner_radius=8,
            fg_color=COLORS["magenta_50"],
            text_color=COLORS["magenta"],
            font=("Segoe UI", 14)
        )
        ic_frame.pack(anchor="w")

        # Número grande
        ctk.CTkLabel(
            inner,
            text=str(numero),
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["ink_900"]
        ).pack(anchor="w", pady=(8, 0))

        # Label
        ctk.CTkLabel(
            inner,
            text=label,
            font=("Segoe UI", 11),
            text_color=COLORS["ink_400"]
        ).pack(anchor="w")

        if on_click:
            for widget in [self, inner]:
                widget.bind("<Button-1>", lambda e: on_click())
                widget.configure(cursor="hand2")


# ============================================
# ITEM CARD — card de item na listagem
# ============================================
class ItemCard(ctk.CTkFrame):
    """Card horizontal mostrando um item: thumb + info + status."""

    def __init__(self, parent, item, on_click=None, mostrar_aluno=False):
        super().__init__(
            parent,
            fg_color=COLORS["white"],
            border_color=COLORS["ink_100"],
            border_width=1,
            corner_radius=12,
            height=80,
        )
        self.item = item
        self.on_click = on_click

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=12)

        # Thumb com ícone da categoria
        icone_cat = self._icone_categoria(item.get("categoria", ""))
        thumb = ctk.CTkLabel(
            inner,
            text=icone_cat,
            width=48, height=48,
            corner_radius=10,
            fg_color=COLORS["magenta_50"],
            text_color=COLORS["magenta"],
            font=("Segoe UI", 20)
        )
        thumb.pack(side="left")

        # Info do item
        info = ctk.CTkFrame(inner, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=(14, 10))

        # Título
        ctk.CTkLabel(
            info,
            text=item.get("nome", ""),
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["ink_900"],
            anchor="w"
        ).pack(anchor="w", fill="x")

        # Meta
        meta_parts = []
        if mostrar_aluno and item.get("aluno_nome"):
            meta_parts.append(f"👤 {item['aluno_nome']}")
        meta_parts.append(f"📍 {item.get('local', '')}")
        if item.get("data_ocorrido"):
            meta_parts.append(f"🗓 {self._formatar_data(item['data_ocorrido'])}")
        meta_parts.append(f"🏷 {item.get('categoria', '')}")

        meta_text = "   ".join(meta_parts)
        ctk.CTkLabel(
            info,
            text=meta_text,
            font=("Segoe UI", 11),
            text_color=COLORS["ink_400"],
            anchor="w"
        ).pack(anchor="w", fill="x", pady=(2, 0))

        # Status badge
        if item.get("status"):
            badge = StatusBadge(inner, item["status"])
            badge.pack(side="right")

        # Bind clique em todos os elementos
        if on_click:
            for w in [self, inner, info, thumb]:
                w.bind("<Button-1>", lambda e: on_click(item))
                w.configure(cursor="hand2")

    @staticmethod
    def _icone_categoria(categoria):
        mapa = {
            "Material escolar": "📚",
            "Eletrônicos": "🎧",
            "Roupas": "👕",
            "Documentos": "💳",
            "Acessórios": "🔑",
            "Garrafas/Recipientes": "💧",
            "Outros": "📦",
        }
        return mapa.get(categoria, "📦")

    @staticmethod
    def _formatar_data(data_str):
        """Formata data ISO (2026-04-22) para 22/04."""
        try:
            partes = data_str.split("-")
            return f"{partes[2]}/{partes[1]}"
        except:
            return data_str


# ============================================
# GALLERY CARD — card vertical para galeria
# ============================================
class GalleryCard(ctk.CTkFrame):
    """Card vertical (foto em cima, info embaixo) para galeria de itens disponíveis."""

    def __init__(self, parent, item, on_click=None):
        super().__init__(
            parent,
            fg_color=COLORS["white"],
            border_color=COLORS["ink_100"],
            border_width=1,
            corner_radius=14,
            width=200, height=200
        )
        self.item = item
        self.pack_propagate(False)

        # Foto (placeholder com ícone)
        foto_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["magenta_50"],
            corner_radius=0,
            height=120
        )
        foto_frame.pack(fill="x")
        foto_frame.pack_propagate(False)

        icone = ItemCard._icone_categoria(item.get("categoria", ""))
        ctk.CTkLabel(
            foto_frame,
            text=icone,
            font=("Segoe UI", 36),
            text_color=COLORS["magenta"]
        ).pack(expand=True)

        # Info
        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(fill="both", expand=True, padx=12, pady=10)

        ctk.CTkLabel(
            info,
            text=item.get("nome", "")[:25],
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["ink_900"],
            anchor="w"
        ).pack(anchor="w", fill="x")

        ctk.CTkLabel(
            info,
            text=f"📍 {item.get('local', '').split('—')[0].strip()[:20]}",
            font=("Segoe UI", 10),
            text_color=COLORS["ink_400"],
            anchor="w"
        ).pack(anchor="w", fill="x", pady=(2, 0))

        if on_click:
            for w in [self, foto_frame, info]:
                w.bind("<Button-1>", lambda e: on_click(item))
                w.configure(cursor="hand2")


# ============================================
# SEARCH BAR — barra de busca
# ============================================
class SearchBar(ctk.CTkFrame):
    """Campo de busca com ícone."""

    def __init__(self, parent, placeholder="Buscar...", on_change=None):
        super().__init__(
            parent,
            fg_color=COLORS["white"],
            border_color=COLORS["ink_100"],
            border_width=1,
            corner_radius=10,
            height=40
        )
        self.on_change = on_change

        # Ícone
        ctk.CTkLabel(
            self,
            text="🔍",
            font=("Segoe UI", 13),
            text_color=COLORS["ink_400"]
        ).pack(side="left", padx=(12, 4))

        # Input
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            border_width=0,
            fg_color="transparent",
            font=("Segoe UI", 12),
            text_color=COLORS["ink_900"]
        )
        self.entry.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=4)

        if on_change:
            self.entry.bind("<KeyRelease>", lambda e: on_change(self.entry.get()))

    def get(self):
        return self.entry.get()
