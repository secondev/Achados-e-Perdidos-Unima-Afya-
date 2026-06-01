"""
screens/detalhe.py — Detalhe do item + chat

Mostra:
- Card com foto, dados e linha do tempo (esquerda)
- Chat aluno ↔ funcionário (direita)
- Funcionário pode mudar o status do item
"""

import customtkinter as ctk
from tkinter import messagebox
from config import COLORS, STATUS
from components.widgets import AppBar, StatusBadge
import database as db


class DetalheItem(ctk.CTkFrame):
    def __init__(self, parent, usuario, item, on_navigate, on_logout):
        super().__init__(parent, fg_color=COLORS["ink_25"], corner_radius=0)
        self.usuario = usuario
        self.item = item
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.avaliacao = db.buscar_avaliacao(self.item["id"])

        # Determina nav_atual baseado em quem está logado
        nav = "admin" if usuario["tipo"] == "funcionario" else "inicio"

        self._build(nav)

    def _build(self, nav_atual):
        # App bar
        app_bar = AppBar(
            self,
            self.usuario,
            self.on_logout,
            nav_atual=nav_atual,
            on_nav=self.on_navigate,
            subtitle=f"Caso #{self.item['id']}"
        )
        app_bar.pack(fill="x", side="top")

        # Body
        body = ctk.CTkScrollableFrame(self, fg_color=COLORS["ink_25"], corner_radius=0)
        body.pack(fill="both", expand=True)

        wrapper = ctk.CTkFrame(body, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=40, pady=24)

        # Botão voltar
        ctk.CTkButton(
            wrapper,
            text="← Voltar",
            font=("Segoe UI", 11, "bold"),
            fg_color=COLORS["white"],
            text_color=COLORS["ink_700"],
            border_color=COLORS["ink_100"],
            border_width=1,
            hover_color=COLORS["ink_100"],
            corner_radius=10,
            height=34, width=90,
            command=lambda: self.on_navigate(
                "admin" if self.usuario["tipo"] == "funcionario" else "inicio"
            )
        ).pack(anchor="w", pady=(0, 16))

        # Grid principal: detalhe (esquerda) + chat (direita)
        grid = ctk.CTkFrame(wrapper, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure(0, weight=1, uniform="col")
        grid.grid_columnconfigure(1, weight=1, uniform="col")

        # Coluna esquerda: detalhe
        self._criar_card_detalhe(grid)

        # Coluna direita: chat
        self._criar_card_chat(grid)

    def _criar_card_detalhe(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["white"],
            border_color=COLORS["ink_100"],
            border_width=1,
            corner_radius=16
        )
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Foto/banner
        foto = ctk.CTkFrame(
            card,
            fg_color=COLORS["magenta_50"],
            corner_radius=0,
            height=180
        )
        foto.pack(fill="x")
        foto.pack_propagate(False)

        from components.widgets import ItemCard
        icone = ItemCard._icone_categoria(self.item.get("categoria", ""))
        ctk.CTkLabel(
            foto,
            text=icone,
            font=("Segoe UI", 64),
            text_color=COLORS["magenta"]
        ).pack(expand=True)

        # Body do detalhe
        det = ctk.CTkFrame(card, fg_color="transparent")
        det.pack(fill="x", padx=22, pady=22)

        # Nome
        ctk.CTkLabel(
            det,
            text=self.item.get("nome", ""),
            font=("Segoe UI", 17, "bold"),
            text_color=COLORS["ink_900"],
            anchor="w",
            wraplength=400
        ).pack(anchor="w", fill="x")

        # Badge de status
        badge = StatusBadge(det, self.item.get("status", "aberto"))
        badge.pack(anchor="w", pady=(8, 0))

        # Metadados
        meta_frame = ctk.CTkFrame(det, fg_color="transparent")
        meta_frame.pack(fill="x", pady=(16, 0))

        meta_data = [
            ("🏷", "Categoria", self.item.get("categoria", "—")),
            ("📍", "Local", self.item.get("local", "—")),
            ("🗓", "Data", self.item.get("data_ocorrido", "—") or "—"),
        ]

        if self.item.get("aluno_nome"):
            meta_data.insert(0, ("👤", "Aluno", self.item["aluno_nome"]))

        if self.item.get("descricao"):
            meta_data.append(("📝", "Detalhes", self.item["descricao"]))

        for icone, lbl, val in meta_data:
            row = ctk.CTkFrame(meta_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)

            ctk.CTkLabel(
                row,
                text=icone,
                font=("Segoe UI", 14),
                width=24
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=f"{lbl}:",
                font=("Segoe UI", 11),
                text_color=COLORS["ink_400"],
                width=80,
                anchor="w"
            ).pack(side="left", padx=(4, 8))

            ctk.CTkLabel(
                row,
                text=val,
                font=("Segoe UI", 12, "bold"),
                text_color=COLORS["ink_900"],
                anchor="w",
                wraplength=280,
                justify="left"
            ).pack(side="left", fill="x", expand=True)

        # Linha do tempo
        timeline_frame = ctk.CTkFrame(det, fg_color="transparent")
        timeline_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkLabel(
            timeline_frame,
            text="LINHA DO TEMPO",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["ink_400"]
        ).pack(anchor="w", pady=(0, 12))

        historico = db.listar_historico_status(self.item["id"])
        for h in historico:
            row = ctk.CTkFrame(timeline_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)

            ctk.CTkLabel(
                row,
                text="●",
                font=("Segoe UI", 14),
                text_color=COLORS["magenta"],
                width=20
            ).pack(side="left")

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=(8, 0))

            ctk.CTkLabel(
                info,
                text=STATUS.get(h["status"], h["status"]),
                font=("Segoe UI", 12, "bold"),
                text_color=COLORS["ink_900"],
                anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=self._formatar_data_hora(h["criado_em"]),
                font=("Segoe UI", 10),
                text_color=COLORS["ink_400"],
                anchor="w"
            ).pack(anchor="w")

        if self.item.get("status") == "devolvido":
            self._criar_secao_avaliacao(det)

        # Botões de ação (só para funcionário)
        if self.usuario["tipo"] == "funcionario":
            self._criar_acoes_funcionario(det)

    def _criar_acoes_funcionario(self, parent):
        """Botões para funcionário mudar o status."""
        sep = ctk.CTkFrame(parent, fg_color=COLORS["ink_100"], height=1)
        sep.pack(fill="x", pady=(20, 16))

        ctk.CTkLabel(
            parent,
            text="ALTERAR STATUS",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["ink_400"]
        ).pack(anchor="w", pady=(0, 12))

        botoes_frame = ctk.CTkFrame(parent, fg_color="transparent")
        botoes_frame.pack(fill="x")

        acoes = [
            ("analise", "Em análise", COLORS["status_analise_bg"], COLORS["status_analise_fg"]),
            ("encontrado", "Encontrado", COLORS["status_encontrado_bg"], COLORS["status_encontrado_fg"]),
            ("devolvido", "Devolvido", COLORS["status_devolvido_bg"], COLORS["status_devolvido_fg"]),
            ("naoachado", "Não encontrado", COLORS["status_naoachado_bg"], COLORS["status_naoachado_fg"]),
        ]

        for status, texto, bg, fg in acoes:
            btn = ctk.CTkButton(
                botoes_frame,
                text=texto,
                font=("Segoe UI", 11, "bold"),
                fg_color=bg,
                text_color=fg,
                hover_color=COLORS["ink_200"],
                corner_radius=8,
                height=34,
                command=lambda s=status: self._mudar_status(s)
            )
            btn.pack(fill="x", pady=2)

    def _mudar_status(self, novo_status):
        if messagebox.askyesno(
            "Confirmar",
            f"Mudar status para '{STATUS[novo_status]}'?"
        ):
            db.atualizar_status(self.item["id"], novo_status)
            messagebox.showinfo("Sucesso", "Status atualizado!")
            # Recarrega a tela
            self.item = db.buscar_item(self.item["id"])
            self.on_navigate("detalhe", self.item)

    def _criar_secao_avaliacao(self, parent):
        sep = ctk.CTkFrame(parent, fg_color=COLORS["ink_100"], height=1)
        sep.pack(fill="x", pady=(20, 16))

        ctk.CTkLabel(
            parent,
            text="AVALIAÇÃO DO ATENDIMENTO",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["ink_400"]
        ).pack(anchor="w", pady=(0, 12))

        if self.avaliacao:
            nota_frame = ctk.CTkFrame(parent, fg_color="transparent")
            nota_frame.pack(fill="x", pady=(0, 8))

            ctk.CTkLabel(
                nota_frame,
                text=f"Nota: {self.avaliacao['nota']} de 5",
                font=("Segoe UI", 12, "bold"),
                text_color=COLORS["ink_900"]
            ).pack(anchor="w")

            ctk.CTkLabel(
                parent,
                text=self.avaliacao.get("comentario", "Sem comentário."),
                font=("Segoe UI", 11),
                text_color=COLORS["ink_700"],
                wraplength=400,
                justify="left"
            ).pack(fill="x")
        elif self.usuario["tipo"] == "aluno":
            ctk.CTkLabel(
                parent,
                text="Seu item foi devolvido! Conte como foi o atendimento para ajudar o setor.",
                font=("Segoe UI", 11),
                text_color=COLORS["ink_600"],
                wraplength=400,
                justify="left"
            ).pack(fill="x", pady=(0, 12))

            ctk.CTkButton(
                parent,
                text="Avaliar atendimento",
                font=("Segoe UI", 11, "bold"),
                fg_color=COLORS["magenta"],
                text_color=COLORS["white"],
                corner_radius=10,
                height=36,
                width=180,
                command=self._abrir_modal_avaliacao
            ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                parent,
                text="Aguardando avaliação do aluno.",
                font=("Segoe UI", 11),
                text_color=COLORS["ink_600"],
                wraplength=400,
                justify="left"
            ).pack(fill="x")

    def _abrir_modal_avaliacao(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Avaliar atendimento")
        modal.geometry("440x380")
        modal.grab_set()
        modal.transient(self)

        ctk.CTkLabel(
            modal,
            text="Avaliação de 1 a 5 estrelas",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS["ink_900"]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        nota_var = ctk.IntVar(value=5)
        stars_frame = ctk.CTkFrame(modal, fg_color="transparent")
        stars_frame.pack(anchor="w", padx=20, pady=(0, 16))

        star_buttons = []

        def atualizar_estrelas():
            for index, btn in enumerate(star_buttons, start=1):
                btn.configure(text="★" if index <= nota_var.get() else "☆")

        def set_nota(valor):
            nota_var.set(valor)
            atualizar_estrelas()

        for i in range(1, 6):
            btn = ctk.CTkButton(
                stars_frame,
                text="★" if i <= nota_var.get() else "☆",
                font=("Segoe UI", 18),
                fg_color=COLORS["magenta"],
                text_color=COLORS["white"],
                width=38,
                height=38,
                corner_radius=12,
                command=lambda v=i: set_nota(v)
            )
            btn.pack(side="left", padx=4)
            star_buttons.append(btn)

        ctk.CTkLabel(
            modal,
            text="Comentário (opcional)",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS["ink_700"]
        ).pack(anchor="w", padx=20, pady=(0, 8))

        comentario_box = ctk.CTkTextbox(modal, width=400, height=140)
        comentario_box.pack(padx=20, pady=(0, 14))

        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            font=("Segoe UI", 11),
            fg_color=COLORS["white"],
            text_color=COLORS["ink_700"],
            border_width=1,
            border_color=COLORS["ink_200"],
            corner_radius=10,
            command=modal.destroy
        ).pack(side="left", expand=True, padx=(0, 8), pady=(0, 10))

        def enviar_avaliacao():
            comentario = comentario_box.get("1.0", "end").strip()
            nota = nota_var.get()
            if nota < 1 or nota > 5:
                messagebox.showerror("Erro", "Escolha uma nota entre 1 e 5.")
                return

            db.salvar_avaliacao(self.item["id"], nota, comentario)
            messagebox.showinfo("Obrigado", "Avaliação registrada com sucesso.")
            modal.destroy()
            self.item = db.buscar_item(self.item["id"])
            self.on_navigate("detalhe", self.item)

        ctk.CTkButton(
            btn_frame,
            text="Enviar avaliação",
            font=("Segoe UI", 11, "bold"),
            fg_color=COLORS["magenta"],
            text_color=COLORS["white"],
            corner_radius=10,
            command=enviar_avaliacao
        ).pack(side="right", expand=True, padx=(8, 0), pady=(0, 10))

    def _criar_card_chat(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["white"],
            border_color=COLORS["ink_100"],
            border_width=1,
            corner_radius=16
        )
        card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Header do chat
        header = ctk.CTkFrame(card, fg_color="transparent", height=70)
        header.pack(fill="x", padx=18, pady=(14, 0))
        header.pack_propagate(False)

        # Avatar do contato (se aluno → mostra foto do funcionário; se funcionário → mostra do aluno)
        if self.usuario["tipo"] == "aluno":
            contato_nome = "Setor de Achados"
            contato_avatar = "👩‍💼"
        else:
            contato_nome = self.item.get("aluno_nome", "Aluno")
            contato_avatar = "👨‍🎓"

        ctk.CTkLabel(
            header,
            text=contato_avatar,
            font=("Segoe UI", 22),
            width=42, height=42,
            corner_radius=21,
            fg_color=COLORS["magenta_50"]
        ).pack(side="left")

        info_frame = ctk.CTkFrame(header, fg_color="transparent")
        info_frame.pack(side="left", padx=(12, 0), pady=8)

        ctk.CTkLabel(
            info_frame,
            text=contato_nome,
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["ink_900"],
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text="● Online",
            font=("Segoe UI", 10),
            text_color=COLORS["success"],
            anchor="w"
        ).pack(anchor="w")

        # Divisória
        ctk.CTkFrame(card, fg_color=COLORS["ink_100"], height=1).pack(fill="x")

        # Body do chat (mensagens)
        self.chat_body = ctk.CTkScrollableFrame(
            card,
            fg_color=COLORS["ink_25"],
            corner_radius=0,
            height=380
        )
        self.chat_body.pack(fill="both", expand=True)

        self._renderizar_mensagens()

        # Input de mensagem
        input_frame = ctk.CTkFrame(card, fg_color="transparent", height=60)
        input_frame.pack(fill="x", padx=14, pady=14)
        input_frame.pack_propagate(False)

        self.entry_msg = ctk.CTkEntry(
            input_frame,
            placeholder_text="Digite uma mensagem...",
            font=("Segoe UI", 12),
            fg_color=COLORS["white"],
            text_color=COLORS["ink_900"],
            border_color=COLORS["ink_100"],
            border_width=1,
            corner_radius=20,
            height=38
        )
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_msg.bind("<Return>", lambda e: self._enviar())

        ctk.CTkButton(
            input_frame,
            text="Enviar",
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["magenta"],
            text_color=COLORS["white"],
            hover_color=COLORS["magenta_dark"],
            corner_radius=20,
            height=38, width=80,
            command=self._enviar
        ).pack(side="left")

    def _renderizar_mensagens(self):
        # Limpa
        for w in self.chat_body.winfo_children():
            w.destroy()

        mensagens = db.listar_mensagens(self.item["id"])

        if not mensagens:
            empty_label = ctk.CTkLabel(
                self.chat_body,
                text="💬\nNenhuma mensagem ainda.\nInicie a conversa.",
                font=("Segoe UI", 11),
                text_color=COLORS["ink_400"],
                justify="center"
            )
            empty_label.pack(expand=True, pady=40)
            return

        for msg in mensagens:
            self._criar_balao(msg)

    def _criar_balao(self, msg):
        """Cria um balão de mensagem."""
        is_minha = msg["remetente_id"] == self.usuario["id"]

        wrapper = ctk.CTkFrame(self.chat_body, fg_color="transparent")
        wrapper.pack(fill="x", pady=4, padx=8)

        # Bolha
        if is_minha:
            balao = ctk.CTkFrame(
                wrapper,
                fg_color=COLORS["magenta"],
                corner_radius=14,
            )
            balao.pack(side="right", anchor="e")

            label = ctk.CTkLabel(
                balao,
                text=msg["texto"],
                font=("Segoe UI", 12),
                text_color=COLORS["white"],
                wraplength=320,
                justify="left",
                anchor="w"
            )
            label.pack(padx=14, pady=10)
        else:
            balao = ctk.CTkFrame(
                wrapper,
                fg_color=COLORS["white"],
                border_color=COLORS["ink_100"],
                border_width=1,
                corner_radius=14,
            )
            balao.pack(side="left", anchor="w")

            label = ctk.CTkLabel(
                balao,
                text=msg["texto"],
                font=("Segoe UI", 12),
                text_color=COLORS["ink_900"],
                wraplength=320,
                justify="left",
                anchor="w"
            )
            label.pack(padx=14, pady=10)

    def _enviar(self):
        texto = self.entry_msg.get().strip()
        if not texto:
            return

        db.enviar_mensagem(
            item_id=self.item["id"],
            remetente_id=self.usuario["id"],
            texto=texto
        )

        self.entry_msg.delete(0, "end")
        self._renderizar_mensagens()

        # Auto-scroll para o final
        self.after(100, lambda: self.chat_body._parent_canvas.yview_moveto(1.0))

    @staticmethod
    def _formatar_data_hora(timestamp):
        """Formata timestamp do SQLite para exibição."""
        try:
            # Formato esperado: '2026-04-22 14:35:00'
            partes = timestamp.split(" ")
            data = partes[0]
            hora = partes[1][:5] if len(partes) > 1 else ""
            d = data.split("-")
            return f"{d[2]}/{d[1]} · {hora}" if hora else f"{d[2]}/{d[1]}"
        except:
            return timestamp
