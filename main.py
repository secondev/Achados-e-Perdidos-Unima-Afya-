"""
main.py — Ponto de entrada do Achados Unima Afya

Inicializa a janela principal, gerencia navegação entre telas
e mantém o estado do usuário logado.
"""

import customtkinter as ctk
from config import COLORS, APP_TITLE, APP_WIDTH, APP_HEIGHT, APP_MIN_WIDTH, APP_MIN_HEIGHT
import database as db
from screens.login import LoginScreen
from screens.home_aluno import HomeAluno
from screens.cadastro import CadastroPerda
from screens.disponiveis import ItensDisponiveis
from screens.admin import AdminPanel
from screens.detalhe import DetalheItem


# ============================================
# CONFIGURAÇÃO INICIAL DO CUSTOMTKINTER
# ============================================
ctk.set_appearance_mode("light")  # Forçar modo claro
ctk.set_default_color_theme("blue")  # Será sobrescrito pelas nossas cores


class App(ctk.CTk):
    """Janela principal da aplicação."""

    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(APP_MIN_WIDTH, APP_MIN_HEIGHT)
        self.configure(fg_color=COLORS["ink_25"])

        # Centraliza na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (APP_WIDTH // 2)
        y = (self.winfo_screenheight() // 2) - (APP_HEIGHT // 2)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}+{x}+{y}")

        # Estado da aplicação
        self.usuario_atual = None
        self.tela_atual = None

        # Container principal (todas as telas vão aqui)
        self.container = ctk.CTkFrame(self, fg_color=COLORS["ink_25"], corner_radius=0)
        self.container.pack(fill="both", expand=True)

        # Inicia banco e mostra login
        db.init_db()
        self._mostrar_login()

    def _limpar_tela(self):
        """Remove a tela atual antes de mostrar uma nova."""
        if self.tela_atual:
            self.tela_atual.destroy()
            self.tela_atual = None

    def _mostrar_login(self):
        """Mostra a tela de login."""
        self._limpar_tela()
        self.usuario_atual = None
        self.tela_atual = LoginScreen(self.container, on_login=self._fazer_login)
        self.tela_atual.pack(fill="both", expand=True)

    def _fazer_login(self, usuario):
        """Callback quando usuário seleciona um perfil no login."""
        self.usuario_atual = usuario

        # Aluno → Home; Funcionário → Painel admin
        if usuario["tipo"] == "aluno":
            self._navegar("inicio")
        else:
            self._navegar("admin")

    def _logout(self):
        """Callback de logout."""
        self._mostrar_login()

    def _navegar(self, destino, dados=None):
        """
        Navega entre telas.

        Args:
            destino: nome da tela ('inicio', 'cadastrar', 'disponiveis', 'admin', 'detalhe')
            dados: dados adicionais (ex: item ao ir para 'detalhe')
        """
        self._limpar_tela()

        if destino == "inicio":
            self.tela_atual = HomeAluno(
                self.container,
                self.usuario_atual,
                on_navigate=self._navegar,
                on_logout=self._logout
            )
        elif destino == "cadastrar":
            self.tela_atual = CadastroPerda(
                self.container,
                self.usuario_atual,
                on_navigate=self._navegar,
                on_logout=self._logout
            )
        elif destino == "disponiveis":
            self.tela_atual = ItensDisponiveis(
                self.container,
                self.usuario_atual,
                on_navigate=self._navegar,
                on_logout=self._logout
            )
        elif destino == "admin":
            self.tela_atual = AdminPanel(
                self.container,
                self.usuario_atual,
                on_navigate=self._navegar,
                on_logout=self._logout
            )
        elif destino == "detalhe":
            # Recarrega o item do banco (caso tenha sido atualizado)
            item = db.buscar_item(dados["id"]) if dados else None
            if item:
                self.tela_atual = DetalheItem(
                    self.container,
                    self.usuario_atual,
                    item=item,
                    on_navigate=self._navegar,
                    on_logout=self._logout
                )
            else:
                # Se item não existe, volta pro início
                self._navegar("inicio")
                return

        if self.tela_atual:
            self.tela_atual.pack(fill="both", expand=True)


# ============================================
# EXECUÇÃO
# ============================================
if __name__ == "__main__":
    app = App()
    app.mainloop()
