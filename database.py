"""
database.py — Gerenciamento do banco SQLite

Cria as tabelas, popula dados iniciais e fornece funções
para todas as queries usadas pelo sistema.
"""

import sqlite3
import os
from datetime import datetime

from api.email_service import (
    notificar_mudanca_status,
    notificar_nova_mensagem,
    notificar_nova_perda,
)

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

    # Tabela de notificações do aluno (sininho)
    c.execute("""
        CREATE TABLE IF NOT EXISTS notificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('mensagem', 'status')),
            lida INTEGER NOT NULL DEFAULT 0,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (item_id) REFERENCES itens(id)
        )
    """)

    # Tabela de avaliações de atendimento
    c.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL UNIQUE,
            nota INTEGER NOT NULL CHECK(nota BETWEEN 1 AND 5),
            comentario TEXT,
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

    # =========================================================================
    # DADO DE TESTE ADICIONAL PARA ITENS EXPIRADOS (MAIS DE 30 DIAS):
    # Cadastrando um item simulando o ano passado para testar a expiração
    # =========================================================================
    c.execute("""
        INSERT INTO itens (tipo, usuario_id, nome, categoria, local, descricao, status, criado_em)
        VALUES ('achado', 3, 'Garrafa de Alumínio Antiga', 'Garrafas/Recipientes', 'Auditório', 
                'Garrafa esquecida há muito tempo', 'aberto', '2025-11-15 10:00:00')
    """)

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

    # Updates extras de histórico
    c.execute("INSERT INTO historico_status (item_id, status) VALUES (1, 'analise')")
    c.execute(
        "INSERT INTO historico_status (item_id, status) VALUES (1, 'encontrado')")
    c.execute("INSERT INTO historico_status (item_id, status) VALUES (2, 'analise')")

    conn.commit()


# ============================================
# FUNÇÕES DE USUÁRIOS
# ============================================
def listar_usuarios():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM usuarios ORDER BY tipo, nome").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def buscar_usuario(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM usuarios WHERE id = ?",
                       (user_id,)).fetchone()
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
    """Lista itens achados disponíveis com menos de 30 dias (galeria pública)."""
    conn = get_conn()

    # MODIFICAÇÃO PR 1: Filtra apenas itens com 30 dias ou menos usando julianday
    query = """
        SELECT * FROM itens
        WHERE tipo = 'achado' 
          AND status IN ('aberto', 'analise')
          AND (julianday('now') - julianday(criado_em)) <= 30
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


def listar_itens_expirados(busca=None, categoria=None):
    """Lista itens achados que passaram do prazo de 30 dias (Para descarte/doação)."""
    conn = get_conn()

    # ADIÇÃO PR 1: Query criada especificamente para alimentar a futura tela do funcionário
    query = """
        SELECT *, CAST(julianday('now') - julianday(criado_em) AS INTEGER) as dias_passados
        FROM itens
        WHERE tipo = 'achado' 
          AND status NOT IN ('devolvido', 'expirado')
          AND (julianday('now') - julianday(criado_em)) > 30
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


def buscar_avaliacao(item_id):
    """Retorna a avaliação do atendimento para um item, se existir."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM avaliacoes WHERE item_id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def salvar_avaliacao(item_id, nota, comentario):
    """Salva ou atualiza a avaliação de um item."""
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO avaliacoes (item_id, nota, comentario)
        VALUES (?, ?, ?)
        ON CONFLICT(item_id) DO UPDATE SET
            nota = excluded.nota,
            comentario = excluded.comentario,
            criado_em = CURRENT_TIMESTAMP
        """,
        (item_id, nota, comentario)
    )
    conn.commit()
    conn.close()


def cadastrar_item(tipo, usuario_id, nome, categoria, local, descricao, foto_url, data_ocorrido=None):
    """Cadastra um novo item (perda ou achado)."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO itens (tipo, usuario_id, nome, categoria, local, descricao, foto_url, data_ocorrido, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'aberto')
    """, (tipo, usuario_id, nome, categoria, local, descricao, foto_url, data_ocorrido))
    item_id = c.lastrowid
    c.execute(
        "INSERT INTO historico_status (item_id, status) VALUES (?, 'aberto')", (item_id,))
    conn.commit()
    conn.close()

    # Notifica funcionários por email (somente quando uma PERDA é cadastrada)
    if tipo == "perda":
        try:
            conn2 = get_conn()
            funcionarios = conn2.execute(
                "SELECT * FROM usuarios WHERE tipo = 'funcionario'"
            ).fetchall()
            aluno = conn2.execute(
                "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
            ).fetchone()
            conn2.close()

            item_dict = {
                "nome": nome,
                "local": local,
                "data_ocorrido": data_ocorrido,
                "categoria": categoria,
            }

            for funcionario in funcionarios:
                notificar_nova_perda(
                    funcionario_email=funcionario["email"],
                    funcionario_nome=funcionario["nome"],
                    aluno_nome=aluno["nome"],
                    item=item_dict,
                )
        except Exception as e:
            print(f"[EMAIL] Falha ao notificar funcionários: {e}")

    return item_id


def atualizar_status(item_id, novo_status):
    """Atualiza o status de um item, registra no histórico e notifica o aluno dono."""
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
    # Notifica o aluno dono do item sobre a mudança de status
    item = conn.execute(
        "SELECT usuario_id FROM itens WHERE id = ?", (item_id,)).fetchone()
    if item:
        c.execute("""
            INSERT INTO notificacoes (usuario_id, item_id, tipo)
            VALUES (?, ?, 'status')
        """, (item["usuario_id"], item_id))
    conn.commit()
    conn.close()

    # Notifica o aluno por email sobre a mudança de status
    try:
        item = buscar_item(item_id)
        if item and item.get("aluno_email"):
            notificar_mudanca_status(
                aluno_email=item["aluno_email"],
                aluno_nome=item["aluno_nome"],
                item=item,
                novo_status=novo_status,
            )
    except Exception as e:
        print(f"[EMAIL] Falha ao notificar mudança de status: {e}")


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

    contadores = {"aberto": 0, "analise": 0,
                  "encontrado": 0, "devolvido": 0, "naoachado": 0}
    for r in rows:
        contadores[r["status"]] = r["total"]

    # Total de achados disponíveis (Atualizado para respeitar a nova regra de 30 dias)
    achados = c.execute("""
        SELECT COUNT(*) as total FROM itens
        WHERE tipo = 'achado' 
          AND status IN ('aberto', 'analise')
          AND (julianday('now') - julianday(criado_em)) <= 30
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
    """Envia uma nova mensagem no chat e cria notificação para o aluno dono do item."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO mensagens (item_id, remetente_id, texto, foto_url)
        VALUES (?, ?, ?, ?)
    """, (item_id, remetente_id, texto, foto_url))

    # Cria notificação para o aluno dono do item (só se quem enviou for funcionário)
    item = conn.execute(
        "SELECT usuario_id FROM itens WHERE id = ?", (item_id,)).fetchone()
    remetente = conn.execute(
        "SELECT tipo FROM usuarios WHERE id = ?", (remetente_id,)).fetchone()
    if item and remetente and remetente["tipo"] == "funcionario":
        c.execute("""
            INSERT INTO notificacoes (usuario_id, item_id, tipo)
            VALUES (?, ?, 'mensagem')
        """, (item["usuario_id"], item_id))

    conn.commit()
    conn.close()

    # Notifica o outro lado da conversa por email
    try:
        conn3 = get_conn()
        item = conn3.execute(
            """SELECT i.*, u.nome as aluno_nome, u.email as aluno_email
               FROM itens i JOIN usuarios u ON i.usuario_id = u.id
               WHERE i.id = ?""",
            (item_id,)
        ).fetchone()
        remetente = conn3.execute(
            "SELECT * FROM usuarios WHERE id = ?", (remetente_id,)
        ).fetchone()
        conn3.close()

        if item and remetente:
            item_dict = dict(item)

            # Se quem enviou foi o aluno → notifica os funcionários
            # Se quem enviou foi o funcionário → notifica o aluno
            if remetente["tipo"] == "aluno":
                conn4 = get_conn()
                funcionarios = conn4.execute(
                    "SELECT * FROM usuarios WHERE tipo = 'funcionario'"
                ).fetchall()
                conn4.close()
                for func in funcionarios:
                    notificar_nova_mensagem(
                        destinatario_email=func["email"],
                        destinatario_nome=func["nome"],
                        remetente_nome=remetente["nome"],
                        item=item_dict,
                        texto_mensagem=texto or "(imagem)",
                    )
            else:
                notificar_nova_mensagem(
                    destinatario_email=item["aluno_email"],
                    destinatario_nome=item["aluno_nome"],
                    remetente_nome=remetente["nome"],
                    item=item_dict,
                    texto_mensagem=texto or "(imagem)",
                )
    except Exception as e:
        print(f"[EMAIL] Falha ao notificar nova mensagem: {e}")


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


# ============================================
# UTILITÁRIOS
# ============================================
def reset_db():
    """Apaga e recria o banco. Útil para testes."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_db()


# ============================================
# FUNÇÕES DE ESTATÍSTICAS (NOVO DASHBOARD)
# ============================================
def get_itens_por_categoria():
    """Conta a quantidade total de itens (perdas e achados) agrupados por categoria."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT categoria, COUNT(*) as total 
        FROM itens 
        GROUP BY categoria 
        ORDER BY total DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_locais_frequentes():
    """Retorna o Top 5 locais com o maior número de ocorrências."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT local, COUNT(*) as total 
        FROM itens 
        GROUP BY local 
        ORDER BY total DESC 
        LIMIT 5
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_taxa_devolucao():
    """Conta a quantidade de itens agrupados pelo seu status atual."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT status, COUNT(*) as total 
        FROM itens 
        GROUP BY status
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tempo_medio_resolucao():
    """
    Calcula a média de dias que um item demora desde a sua criação
    até mudar para o status de 'devolvido'.
    """
    conn = get_conn()
    row = conn.execute("""
        SELECT AVG(julianday(h.criado_em) - julianday(i.criado_em)) as media_dias
        FROM itens i
        JOIN historico_status h ON i.id = h.item_id
        WHERE h.status = 'devolvido'
    """).fetchone()
    conn.close()

    return row["media_dias"] if row and row["media_dias"] is not None else 0


# ============================================
# FUNÇÕES DE NOTIFICAÇÕES
# ============================================
def contar_notificacoes(usuario_id):
    """Conta quantas notificações não lidas o aluno tem."""
    conn = get_conn()
    row = conn.execute("""
        SELECT COUNT(*) as total FROM notificacoes
        WHERE usuario_id = ? AND lida = 0
    """, (usuario_id,)).fetchone()
    conn.close()
    return row["total"] if row else 0


def marcar_notificacoes_lidas(usuario_id, item_id):
    """Marca como lidas todas as notificações do aluno para um item específico."""
    conn = get_conn()
    conn.execute("""
        UPDATE notificacoes SET lida = 1
        WHERE usuario_id = ? AND item_id = ? AND lida = 0
    """, (usuario_id, item_id))
    conn.commit()
    conn.close()


def listar_notificacoes(usuario_id):
    """Retorna notificações não lidas do aluno com o nome do item."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT n.id, n.item_id, n.tipo, n.criado_em, i.nome as item_nome
        FROM notificacoes n
        JOIN itens i ON n.item_id = i.id
        WHERE n.usuario_id = ? AND n.lida = 0
        ORDER BY n.criado_em DESC
    """, (usuario_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
