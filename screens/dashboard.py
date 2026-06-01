import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import database as db
import config
from components.widgets import AppBar


class DashboardFuncionario(ctk.CTkFrame):
    def __init__(self, master, usuario, on_navigate, on_logout, on_theme_change=None, **kwargs):
        super().__init__(master, fg_color=config.COLORS["ink_25"], corner_radius=0, **kwargs)

        self.usuario = usuario
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.on_theme_change = on_theme_change

        # 1. Barra de navegação no topo (AppBar)
        app_bar = AppBar(
            self,
            self.usuario,
            self.on_logout,
            nav_atual="admin",
            on_nav=self.on_navigate,
            subtitle="Estatísticas e Relatórios"
        )
        app_bar.pack(fill="x", side="top")

        # 2. Corpo rolável
        body = ctk.CTkScrollableFrame(self, fg_color=config.COLORS["ink_25"], corner_radius=0)
        body.pack(fill="both", expand=True)

        wrapper = ctk.CTkFrame(body, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=40, pady=24)

        # 3. Cabeçalho com Título e Botão de Voltar
        header = ctk.CTkFrame(wrapper, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header, text="Visão Geral", font=("Segoe UI", 22, "bold"), text_color=config.COLORS["ink_900"]
        ).pack(side="left")

        ctk.CTkButton(
            header, text="⬅ Voltar ao Mural", font=("Segoe UI", 12, "bold"),
            fg_color=config.COLORS["ink_100"], text_color=config.COLORS["ink_700"],
            hover_color=config.COLORS["ink_200"],
            command=lambda: self.on_navigate("admin")
        ).pack(side="right")

        # 4. Grelha para os gráficos (2 colunas, 2 linhas)
        grid_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        grid_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")
        grid_frame.grid_rowconfigure((0, 1), weight=1, uniform="row")

        # Cores para os gráficos
        self.bg_color = config.COLORS["ink_25"]
        self.text_color = config.COLORS["ink_700"]
        self.magenta = config.COLORS["magenta"]
        self.magenta_light = config.COLORS["magenta_light"]

        # Renderizar os gráficos
        self.criar_grafico_categorias(grid_frame, row=0, col=0)
        self.criar_grafico_locais(grid_frame, row=0, col=1)
        self.criar_grafico_status(grid_frame, row=1, col=0)
        self.criar_kpi_tempo(grid_frame, row=1, col=1)

    def preparar_figura(self):
        """Prepara a figura usando a API de Objetos isolada do Matplotlib"""
        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)

        fig.patch.set_facecolor(self.bg_color)
        ax.set_facecolor(self.bg_color)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.tick_params(colors=self.text_color)
        ax.xaxis.label.set_color(self.text_color)
        ax.yaxis.label.set_color(self.text_color)
        ax.title.set_color(self.text_color)

        return fig, ax

    def renderizar_canvas(self, fig, parent, row, col):
        """Desenha o gráfico na interface de forma totalmente limpa"""
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def criar_grafico_categorias(self, parent, row, col):
        dados = db.get_itens_por_categoria()
        categorias = [d["categoria"] for d in dados]
        totais = [d["total"] for d in dados]

        fig, ax = self.preparar_figura()
        ax.bar(categorias, totais, color=self.magenta)
        ax.set_title("Itens por Categoria", fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(axis='x', rotation=45)

        self.renderizar_canvas(fig, parent, row, col)

    def criar_grafico_locais(self, parent, row, col):
        dados = db.get_locais_frequentes()
        locais = [d["local"] for d in reversed(dados)]
        totais = [d["total"] for d in reversed(dados)]

        fig, ax = self.preparar_figura()
        ax.barh(locais, totais, color=self.magenta_light)
        ax.set_title("Top 5 Locais de Ocorrência", fontsize=12, fontweight='bold', pad=15)

        self.renderizar_canvas(fig, parent, row, col)

    def criar_grafico_status(self, parent, row, col):
        dados = db.get_taxa_devolucao()
        labels = [config.STATUS.get(d["status"], d["status"]) for d in dados]
        totais = [d["total"] for d in dados]

        # CORES CORRIGIDAS: Cada status agora tem uma cor linda baseada na paleta do app!
        status_cores = {
            "aberto": "#71717A",  # Cinza discreto
            "analise": "#F59E0B",  # Amarelo Alerta
            "encontrado": "#10B981",  # Verde Sucesso
            "devolvido": "#E6007E",  # Magenta Oficial Afya
            "naoachado": "#EF4444"  # Vermelho Perigo
        }
        cores = [status_cores.get(d["status"], "#A1A1AA") for d in dados]

        fig, ax = self.preparar_figura()
        wedges, texts, autotexts = ax.pie(
            totais, labels=labels, autopct='%1.1f%%', startangle=90, colors=cores,
            textprops=dict(color=self.text_color)
        )

        # Transforma em gráfico de rosca de forma limpa
        centro_circulo = patches.Circle((0, 0), 0.70, fc=self.bg_color)
        ax.add_patch(centro_circulo)

        ax.set_title("Distribuição por Status", fontsize=12, fontweight='bold')
        self.renderizar_canvas(fig, parent, row, col)

    def criar_kpi_tempo(self, parent, row, col):
        media_dias = db.get_tempo_medio_resolucao()

        frame_kpi = ctk.CTkFrame(parent, fg_color=config.COLORS["ink_50"], corner_radius=10)
        frame_kpi.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        frame_kpi.grid_rowconfigure((0, 1, 2), weight=1)
        frame_kpi.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(frame_kpi, text="Tempo Médio de Resolução", font=config.FONTS["title_sm"],
                              text_color=self.text_color)
        titulo.grid(row=0, column=0, pady=(30, 0))

        dias_inteiros = int(media_dias)
        horas = int((media_dias - dias_inteiros) * 24)
        texto_tempo = f"{dias_inteiros}d {horas}h" if media_dias > 0 else "N/A"

        valor = ctk.CTkLabel(frame_kpi, text=texto_tempo, font=("Segoe UI", 48, "bold"), text_color=self.magenta)
        valor.grid(row=1, column=0)

        sub = ctk.CTkLabel(frame_kpi, text="Desde a criação até a devolução", font=config.FONTS["body_sm"],
                           text_color=config.COLORS["ink_400"])
        sub.grid(row=2, column=0, pady=(0, 30))