"""
database.py — Gerenciamento do banco SQLite

Cria as tabelas, popula dados iniciais e fornece funções
para todas as queries usadas pelo sistema.
"""

import sqlite3
import os
from datetime import datetime

DB_FILE = "achados_unima.db"


def get_conn():
    """Abre conexão com o banco. row_factory=Row permite acessar colunas por nome."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas e popula dados iniciais se o banco for novo."""
    novo_banco = not os.path.exists(DB_FILE)

    conn = get_conn()
    c = conn.cursor()

    # Tabela de usuários
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('aluno', 'funcionario')),
            foto_url TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de itens (perdas e achados)
    c.execute("""
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL CHECK(tipo IN ('perda', 'achado')),
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            local TEXT NOT NULL,
            descricao TEXT,
            foto_url TEXT,
            status TEXT NOT NULL DEFAULT 'aberto',
            data_ocorrido DATE,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # Tabela de mensagens (chat)
    c.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            remetente_id INTEGER NOT NULL,
            texto TEXT,
            foto_url TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES itens(id),
            FOREIGN KEY (remetente_id) REFERENCES usuarios(id)
        )
    """)

    # Tabela de histórico de status (linha do tempo)
    c.execute("""
        CREATE TABLE IF NOT EXISTS historico_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES itens(id)
        )
    """)

    conn.commit()

    if novo_banco:
        seed_data(conn)

    conn.close()


def seed_data(conn):
    """Popula o banco com dados iniciais para teste e apresentação."""
    c = conn.cursor()

    # Usuários
    usuarios = [
        ("Leonardo Silva", "leonardo@afya.edu.br", "aluno", "👨‍🎓"),
        ("Ana Maria", "ana@afya.edu.br", "aluno", "👩‍🎓"),
        ("Maria Fernandes", "maria@afya.edu.br", "funcionario", "👩‍💼"),
        ("Carlos Souza", "carlos@afya.edu.br", "funcionario", "👨‍💼"),
    ]
    c.executemany(
        "INSERT INTO usuarios (nome, email, tipo, foto_url) VALUES (?, ?, ?, ?)",
        usuarios
    )

    # Itens perdidos (do aluno Leonardo, id=1)
    itens_perda = [
        (1, "Fone de ouvido bluetooth preto", "Eletrônicos", "Bloco C — Salas 201 a 220",
         "JBL Tune 510BT, com pequeno arranhão na haste direita", "encontrado", "2026-04-22"),
        (1, "Caderno universitário verde", "Material escolar", "Cantina principal",
         "Tilibra 10 matérias, capa verde com adesivos", "analise", "2026-04-24"),
        (1, "Garrafa térmica rosa", "Garrafas/Recipientes", "Biblioteca",
         "Stanley rosa claro, 750ml", "aberto", "2026-04-25"),
        # Itens de outros alunos
        (2, "Carteira preta com documentos", "Documentos", "Bloco A — Salas 101 a 120",
         "Carteira de couro com RG e cartões", "aberto", "2026-04-22"),
        (2, "Estojo cinza com canetas", "Material escolar", "Bloco B — Laboratórios",
         "Estojo grande com várias canetas Stabilo", "aberto", "2026-04-23"),
    ]
    for item in itens_perda:
        c.execute("""
            INSERT INTO itens (tipo, usuario_id, nome, categoria, local, descricao, status, data_ocorrido)
            VALUES ('perda', ?, ?, ?, ?, ?, ?, ?)
        """, item)
        item_id = c.lastrowid
        # Insere histórico inicial
        c.execute(
            "INSERT INTO historico_status (item_id, status) VALUES (?, 'aberto')",
            (item_id,)
        )

    # Itens achados (cadastrados pelo funcionário Maria, id=3)
    itens_achado = [
        (3, "Caderno azul espiral", "Material escolar", "Biblioteca",
         "Caderno espiral 10 matérias, capa azul"),
        (3, "Carteira marrom", "Documentos", "Pátio central",
         "Carteira de couro marrom sem documentos"),
        (3, "Molho de chaves com 4 chaves", "Acessórios", "Estacionamento",
         "Chaveiro de borracha vermelha com 4 chaves"),
        (3, "Casaco preto P", "Roupas", "Cantina principal",
         "Casaco moletom preto tamanho P, marca Adidas"),
        (3, "Relógio prata", "Acessórios", "Bloco A — Salas 101 a 120",
         "Relógio analógico com pulseira de metal prata"),
        (3, "Estojo cinza", "Material escolar", "Bloco B — Laboratórios",
         "Estojo de tecido cinza com canetas"),
    ]
    for item in itens_achado:
        c.execute("""
            INSERT INTO itens (tipo, usuario_id, nome, categoria, local, descricao, status)
            VALUES ('achado', ?, ?, ?, ?, ?, 'aberto')
        """, item)

    # Mensagens de exemplo (para o item 1 do Leonardo - Fone)
    mensagens = [
        (1, 3, "Olá Leonardo! Recebemos sua solicitação sobre o fone. Pode descrever alguma marca distinta para confirmarmos?", None),
        (1, 1, "Oi! Tem um arranhão pequeno na haste direita, e a capinha de silicone do botão é roxa.", None),
        (1, 3, "Perfeito, isso bate com um que recebemos hoje. Pode confirmar se é este aqui?", None),
        (1, 1, "É esse mesmo! Muito obrigado 🙏", None),
        (1, 3, "Ótimo! Pode passar no setor de achados (Bloco A, sala 105) das 8h às 18h para retirar. Traga seu RA.", None),
    ]
    c.executemany(
        "INSERT INTO mensagens (item_id, remetente_id, texto, foto_url) VALUES (?, ?, ?, ?)",
        mensagens
    )

    # Atualiza status do item 1 para "encontrado" no histórico
    c.execute("INSERT INTO historico_status (item_id, status) VALUES (1, 'analise')")
    c.execute("INSERT INTO historico_status (item_id, status) VALUES (1, 'encontrado')")

    # Atualiza item 2 para "em análise"
    c.execute("INSERT INTO historico_status (item_id, status) VALUES (2, 'analise')")

    conn.commit()


# ============================================
# FUNÇÕES DE USUÁRIOS
# ============================================
def listar_usuarios():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM usuarios ORDER BY tipo, nome").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def buscar_usuario(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ============================================
# FUNÇÕES DE ITENS
# ============================================
def listar_itens_usuario(user_id, status_filtro=None):
    """Lista itens (perdas) cadastrados por um aluno específico."""
    conn = get_conn()
    if status_filtro:
        rows = conn.execute("""
            SELECT * FROM itens
            WHERE usuario_id = ? AND tipo = 'perda' AND status = ?
            ORDER BY criado_em DESC
        """, (user_id, status_filtro)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM itens
            WHERE usuario_id = ? AND tipo = 'perda'
            ORDER BY criado_em DESC
        """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def listar_todas_perdas(status_filtro=None, busca=None, categoria=None):
    """Lista todas as perdas reportadas (para o funcionário)."""
    conn = get_conn()
    query = """
        SELECT i.*, u.nome as aluno_nome
        FROM itens i
        JOIN usuarios u ON i.usuario_id = u.id
        WHERE i.tipo = 'perda'
    """
    params = []
    if status_filtro:
        query += " AND i.status = ?"
        params.append(status_filtro)
    if busca:
        query += " AND (i.nome LIKE ? OR i.descricao LIKE ? OR u.nome LIKE ?)"
        like = f"%{busca}%"
        params.extend([like, like, like])
    if categoria:
        query += " AND i.categoria = ?"
        params.append(categoria)
    query += " ORDER BY i.criado_em DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def listar_achados_disponiveis(busca=None, categoria=None):
    """Lista itens achados disponíveis (galeria pública)."""
    conn = get_conn()
    query = """
        SELECT * FROM itens
        WHERE tipo = 'achado' AND status IN ('aberto', 'analise')
    """
    params = []
    if busca:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        like = f"%{busca}%"
        params.extend([like, like])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    query += " ORDER BY criado_em DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def buscar_item(item_id):
    """Busca um item específico com dados do dono."""
    conn = get_conn()
    row = conn.execute("""
        SELECT i.*, u.nome as aluno_nome, u.email as aluno_email, u.foto_url as aluno_foto
        FROM itens i
        JOIN usuarios u ON i.usuario_id = u.id
        WHERE i.id = ?
    """, (item_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def cadastrar_item(tipo, usuario_id, nome, categoria, local, descricao, foto_url, data_ocorrido=None):
    """Cadastra um novo item (perda ou achado)."""
    nome = nome.strip().title()
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO itens (tipo, usuario_id, nome, categoria, local, descricao, foto_url, data_ocorrido, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'aberto')
    """, (tipo, usuario_id, nome, categoria, local, descricao, foto_url, data_ocorrido))
    item_id = c.lastrowid
    c.execute("INSERT INTO historico_status (item_id, status) VALUES (?, 'aberto')", (item_id,))
    conn.commit()
    conn.close()
    return item_id


def atualizar_status(item_id, novo_status):
    """Atualiza o status de um item e registra no histórico."""
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "UPDATE itens SET status = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
        (novo_status, item_id)
    )
    c.execute(
        "INSERT INTO historico_status (item_id, status) VALUES (?, ?)",
        (item_id, novo_status)
    )
    conn.commit()
    conn.close()


def contar_status(usuario_id):
    """Conta itens por status para um usuário (cards do dashboard)."""
    conn = get_conn()
    c = conn.cursor()

    rows = c.execute("""
        SELECT status, COUNT(*) as total
        FROM itens
        WHERE usuario_id = ? AND tipo = 'perda'
        GROUP BY status
    """, (usuario_id,)).fetchall()

    contadores = {"aberto": 0, "analise": 0, "encontrado": 0, "devolvido": 0, "naoachado": 0}
    for r in rows:
        contadores[r["status"]] = r["total"]

    # Total de achados disponíveis
    achados = c.execute("""
        SELECT COUNT(*) as total FROM itens
        WHERE tipo = 'achado' AND status IN ('aberto', 'analise')
    """).fetchone()
    contadores["disponiveis"] = achados["total"]

    conn.close()
    return contadores


# ============================================
# FUNÇÕES DE MENSAGENS
# ============================================
def listar_mensagens(item_id):
    """Lista mensagens de um item, do mais antigo para o mais novo."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT m.*, u.nome as remetente_nome, u.tipo as remetente_tipo
        FROM mensagens m
        JOIN usuarios u ON m.remetente_id = u.id
        WHERE m.item_id = ?
        ORDER BY m.criado_em ASC
    """, (item_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def enviar_mensagem(item_id, remetente_id, texto, foto_url=None):
    """Envia uma nova mensagem no chat."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO mensagens (item_id, remetente_id, texto, foto_url)
        VALUES (?, ?, ?, ?)
    """, (item_id, remetente_id, texto, foto_url))
    conn.commit()
    conn.close()


def listar_historico_status(item_id):
    """Lista a linha do tempo de mudanças de status de um item."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM historico_status
        WHERE item_id = ?
        ORDER BY criado_em ASC
    """, (item_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

import re

def validar_dados_item(nome, categoria, local):
    """Verifica se os campos obrigatórios estão preenchidos."""
    if not nome.strip() or not categoria or not local:
        return False, "Nome, Categoria e Local são obrigatórios."
    return True, ""

def validar_email(email):
    """Valida o formato do e-mail acadêmico."""
    padrao = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    if re.match(padrao, email.lower()):
        return True
    return False


# ============================================
# UTILITÁRIOS
# ============================================
def reset_db():
    """Apaga e recria o banco. Útil para testes."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_db()
