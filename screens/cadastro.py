"""
screens/cadastro.py — Cadastro de item perdido

Formulário com:
- Nome do item
- Categorias em chips clicáveis
- Local (dropdown)
- Data
- Descrição
- Upload de foto (via API ImgBB)
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
from config import COLORS, CATEGORIAS, LOCAIS
from components.widgets import AppBar
import database as db
from api.imgbb import upload_imagem


class CadastroPerda(ctk.CTkFrame):
    def __init__(self, parent, usuario, on_navigate, on_logout):
        super().__init__(parent, fg_color=COLORS["ink_25"], corner_radius=0)
        self.usuario = usuario
        self.on_navigate = on_navigate
        self.on_logout = on_logout

        self.categoria_selecionada = None
        self.foto_caminho = None
        self.cat_buttons = {}

        self._build()

    def _build(self):
        # App bar
        app_bar = AppBar(
            self,
            self.usuario,
            self.on_logout,
            nav_atual="cadastrar",
            on_nav=self.on_navigate
        )
        app_bar.pack(fill="x", side="top")

        # Body scrollável
        body = ctk.CTkScrollableFrame(self, fg_color=COLORS["ink_25"], corner_radius=0)
        body.pack(fill="both", expand=True)

        wrapper = ctk.CTkFrame(body, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=40, pady=24)

        # Título
        ctk.CTkLabel(
            wrapper,
            text="Cadastrar item perdido",
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["ink_900"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            wrapper,
            text="Quanto mais detalhes, mais rápido encontramos seu item.",
            font=("Segoe UI", 12),
            text_color=COLORS["ink_500"]
        ).pack(anchor="w", pady=(2, 24))

        # Card do formulário
        form_card = ctk.CTkFrame(
            wrapper,
            fg_color=COLORS["white"],
            border_color=COLORS["ink_100"],
            border_width=1,
            corner_radius=16
        )
        form_card.pack(fill="x")

        form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
        form_inner.pack(fill="x", padx=28, pady=28)

        # === Nome do item ===
        self._label(form_inner, "Nome do item *")
        self.entry_nome = self._entry(form_inner, "Ex: Fone bluetooth JBL preto Tune 510BT")

        # === Categoria ===
        self._label(form_inner, "Categoria *", pady_top=18)
        cat_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        cat_frame.pack(fill="x")

        for i, cat in enumerate(CATEGORIAS):
            btn = ctk.CTkButton(
                cat_frame,
                text=f"{cat['icone']}  {cat['nome']}",
                font=("Segoe UI", 12),
                fg_color=COLORS["white"],
                text_color=COLORS["ink_700"],
                border_color=COLORS["ink_100"],
                border_width=1,
                hover_color=COLORS["ink_50"],
                corner_radius=20,
                height=34,
                command=lambda c=cat: self._selecionar_categoria(c["nome"])
            )
            btn.grid(row=i // 4, column=i % 4, padx=4, pady=4, sticky="w")
            self.cat_buttons[cat["nome"]] = btn

        # === Linha: Local e Data ===
        linha_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        linha_frame.pack(fill="x", pady=(18, 0))
        linha_frame.grid_columnconfigure(0, weight=1)
        linha_frame.grid_columnconfigure(1, weight=1)

        # Local
        local_col = ctk.CTkFrame(linha_frame, fg_color="transparent")
        local_col.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._label(local_col, "Onde perdeu? *")
        self.combo_local = ctk.CTkComboBox(
            local_col,
            values=LOCAIS,
            font=("Segoe UI", 12),
            fg_color=COLORS["white"],
            text_color=COLORS["ink_900"],
            border_color=COLORS["ink_100"],
            button_color=COLORS["ink_100"],
            button_hover_color=COLORS["ink_200"],
            dropdown_fg_color=COLORS["white"],
            dropdown_text_color=COLORS["ink_700"],
            dropdown_hover_color=COLORS["ink_50"],
            height=40,
            corner_radius=10,
        )
        self.combo_local.pack(fill="x")
        self.combo_local.set(LOCAIS[0])

        # Data
        data_col = ctk.CTkFrame(linha_frame, fg_color="transparent")
        data_col.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self._label(data_col, "Quando aconteceu?")
        self.entry_data = self._entry(data_col, datetime.now().strftime("%Y-%m-%d"))
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # === Descrição ===
        self._label(form_inner, "Descrição detalhada", pady_top=18)
        self.text_desc = ctk.CTkTextbox(
            form_inner,
            font=("Segoe UI", 12),
            fg_color=COLORS["white"],
            text_color=COLORS["ink_900"],
            border_color=COLORS["ink_100"],
            border_width=1,
            corner_radius=10,
            height=80
        )
        self.text_desc.pack(fill="x")

        # === Upload de foto ===
        self._label(form_inner, "Foto do item (opcional, mas recomendado)", pady_top=18)

        self.upload_frame = ctk.CTkFrame(
            form_inner,
            fg_color=COLORS["ink_25"],
            border_color=COLORS["ink_200"],
            border_width=2,
            corner_radius=12,
            height=100,
            cursor="hand2"
        )
        self.upload_frame.pack(fill="x")
        self.upload_frame.pack_propagate(False)

        self.upload_label = ctk.CTkLabel(
            self.upload_frame,
            text="📷  Clique para enviar uma foto\nPNG ou JPG até 5MB · upload via API ImgBB",
            font=("Segoe UI", 12),
            text_color=COLORS["ink_500"],
            justify="center"
        )
        self.upload_label.pack(expand=True)

        self.upload_frame.bind("<Button-1>", lambda e: self._escolher_arquivo())
        self.upload_label.bind("<Button-1>", lambda e: self._escolher_arquivo())

        # === Botões ===
        botoes = ctk.CTkFrame(form_inner, fg_color="transparent")
        botoes.pack(fill="x", pady=(24, 0))

        ctk.CTkButton(
            botoes,
            text="Cancelar",
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["white"],
            text_color=COLORS["ink_700"],
            border_color=COLORS["ink_100"],
            border_width=1,
            hover_color=COLORS["ink_50"],
            corner_radius=10,
            height=42, width=110,
            command=lambda: self.on_navigate("inicio")
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            botoes,
            text="Cadastrar perda  →",
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["magenta"],
            text_color=COLORS["white"],
            hover_color=COLORS["magenta_dark"],
            corner_radius=10,
            height=42, width=180,
            command=self._salvar
        ).pack(side="right")

    def _label(self, parent, texto, pady_top=0):
        lbl = ctk.CTkLabel(
            parent,
            text=texto,
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["ink_700"]
        )
        lbl.pack(anchor="w", pady=(pady_top, 6))
        return lbl

    def _entry(self, parent, placeholder):
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            font=("Segoe UI", 12),
            fg_color=COLORS["white"],
            text_color=COLORS["ink_900"],
            border_color=COLORS["ink_100"],
            border_width=1,
            corner_radius=10,
            height=40
        )
        entry.pack(fill="x")
        return entry

    def _selecionar_categoria(self, nome):
        """Marca a categoria escolhida visualmente."""
        self.categoria_selecionada = nome
        for cat_nome, btn in self.cat_buttons.items():
            if cat_nome == nome:
                btn.configure(
                    fg_color=COLORS["ink_900"],
                    text_color=COLORS["white"],
                    border_color=COLORS["ink_900"]
                )
            else:
                btn.configure(
                    fg_color=COLORS["white"],
                    text_color=COLORS["ink_700"],
                    border_color=COLORS["ink_100"]
                )

    def _escolher_arquivo(self):
        """Abre dialog para escolher imagem."""
        path = filedialog.askopenfilename(
            title="Selecione uma foto",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if path:
            self.foto_caminho = path
            nome = path.split("/")[-1] if "/" in path else path.split("\\")[-1]
            self.upload_label.configure(
                text=f"✅  {nome}\nClique para trocar",
                text_color=COLORS["magenta"]
            )

    def _salvar(self):
        """Valida e salva o item no banco."""
        nome = self.entry_nome.get().strip()
        local = self.combo_local.get()
        data = self.entry_data.get().strip()
        descricao = self.text_desc.get("1.0", "end").strip()

        # Validações
        if not nome or len(nome) < 3:
            messagebox.showerror("Erro", "Por favor, informe o nome do item (mínimo 3 caracteres).")
            return

        if not self.categoria_selecionada:
            messagebox.showerror("Erro", "Por favor, selecione uma categoria.")
            return

        if not local or local == "Selecione...":
            messagebox.showerror("Erro", "Por favor, selecione onde perdeu.")
            return

        # Upload da imagem (se houver)
        foto_url = None
        if self.foto_caminho:
            self.upload_label.configure(text="⏳  Fazendo upload...", text_color=COLORS["ink_500"])
            self.update()
            foto_url = upload_imagem(self.foto_caminho)

        # Salva no banco
        item_id = db.cadastrar_item(
            tipo="perda",
            usuario_id=self.usuario["id"],
            nome=nome,
            categoria=self.categoria_selecionada,
            local=local,
            descricao=descricao,
            foto_url=foto_url,
            data_ocorrido=data if data else None
        )

        messagebox.showinfo(
            "Sucesso!",
            f"Item cadastrado com sucesso!\n\nID da solicitação: #{item_id}\n\nVocê pode acompanhar pelo chat."
        )
        self.on_navigate("inicio")
