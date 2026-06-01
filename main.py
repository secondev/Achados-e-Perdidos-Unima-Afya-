"""
main.py — Ponto de entrada do Achados Unima Afya

Inicializa a janela principal, gerencia navegação entre telas,
mantém o estado do usuário logado e gerencia o tema (claro/escuro).
"""

import customtkinter as ctk
from tkinter import messagebox
from config import (
    COLORS, APP_TITLE, APP_WIDTH, APP_HEIGHT,
    APP_MIN_WIDTH, APP_MIN_HEIGHT, get_tema
)
import database as db
from screens.login import LoginScreen
from screens.home_aluno import HomeAluno
from screens.cadastro import CadastroPerda
from screens.disponiveis import ItensDisponiveis
from screens.admin import AdminPanel
from screens.detalhe import DetalheItem
from screens.dashboard import DashboardFuncionario


# ============================================
# CONFIGURAÇÃO INICIAL DO CUSTOMTKINTER
# ============================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """Janela principal da aplicação."""

    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(APP_MIN_WIDTH, APP_MIN_HEIGHT)
        self.configure(fg_color=COLORS["ink_25"])

        # Centraliza
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (APP_WIDTH // 2)
        y = (self.winfo_screenheight() // 2) - (APP_HEIGHT // 2)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}+{x}+{y}")

        # Estado
        self.usuario_atual = None
        self.tela_atual = None
        self.tela_atual_nome = None      # Nome da tela atual (pra re-renderizar)
        self.tela_atual_dados = None     # Dados da tela atual (pra re-renderizar)

        self.container = ctk.CTkFrame(
            self, fg_color=COLORS["ink_25"], corner_radius=0
        )
        self.container.pack(fill="both", expand=True)

        db.init_db()
        self._mostrar_login()

    def _limpar_tela(self):
        if self.tela_atual:
            self.tela_atual.destroy()
            self.tela_atual = None

    def _mostrar_login(self):
        self._limpar_tela()
        self.usuario_atual = None
        self.tela_atual_nome = "login"
        self.tela_atual_dados = None
        # LoginScreen não tem theme toggle (tela pré-login)
        self.tela_atual = LoginScreen(self.container, on_login=self._fazer_login)
        self.tela_atual.pack(fill="both", expand=True)

    def _fazer_login(self, usuario):
        self.usuario_atual = usuario
        if usuario["tipo"] == "aluno":
            self._navegar("inicio")
        else:
            self._navegar("admin")

    def _logout(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair da sua conta?"):
            self._mostrar_login()

    def _on_theme_change(self, novo_tema):
        """
        Callback quando o usuário alterna o tema.
        Re-renderiza a tela atual com as novas cores e atualiza o fundo da janela.
        """
        # Atualiza o fundo da janela e do container
        self.configure(fg_color=COLORS["ink_25"])
        self.container.configure(fg_color=COLORS["ink_25"])

        # Atualiza o appearance_mode do CustomTkinter (afeta dialogs e scrollbars nativas)
        ctk.set_appearance_mode("dark" if novo_tema == "dark" else "light")

        # Re-renderiza a tela atual com as novas cores
        if self.tela_atual_nome:
            self._navegar(self.tela_atual_nome, self.tela_atual_dados)

    def _navegar(self, destino, dados=None):
        """Navega entre telas. Salva o destino atual pra permitir re-renderizar no toggle."""
        self._limpar_tela()
        self.tela_atual_nome = destino
        self.tela_atual_dados = dados

        # CORREÇÃO: Removemos o 'on_theme_change' daqui para não causar erros
        # (TypeError) em telas que não possuem esse parâmetro no __init__.
        kwargs_comum = {
            "on_navigate": self._navegar,
            "on_logout": self._logout,
        }

        if destino == "inicio":
            self.tela_atual = HomeAluno(
                self.container, self.usuario_atual, **kwargs_comum
            )
        elif destino == "cadastrar":
            self.tela_atual = CadastroPerda(
                self.container, self.usuario_atual, **kwargs_comum
            )
        elif destino == "disponiveis":
            self.tela_atual = ItensDisponiveis(
                self.container, self.usuario_atual, **kwargs_comum
            )
        elif destino == "admin":
            self.tela_atual = AdminPanel(
                self.container, self.usuario_atual, **kwargs_comum
            )
        elif destino == "dashboard":
            self.tela_atual = DashboardFuncionario(
                self.container, self.usuario_atual, **kwargs_comum
            )
        elif destino == "detalhe":
            item = db.buscar_item(dados["id"]) if dados else None
            if item:
                self.tela_atual = DetalheItem(
                    self.container, self.usuario_atual, item=item, **kwargs_comum
                )
                # Salva o item recarregado como dados atuais (pra re-renderizar mantendo o mesmo)
                self.tela_atual_dados = item
            else:
                self._navegar("inicio")
                return

        if self.tela_atual:
            self.tela_atual.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()