"""
api/email_service.py — Cliente da API Resend para envio de emails

Atende ao requisito de consumo de uma SEGUNDA API externa
(além da ImgBB que já é usada para upload de imagens).

Modo de funcionamento:
- Se RESEND_API_KEY estiver configurada: envia email de verdade
- Se não estiver: registra no terminal o email que seria enviado (modo simulação)
- Em modo demo, sempre envia para EMAIL_DESTINATARIO_DEMO (independente do destinatário real)

Documentação oficial: https://resend.com/docs
"""

import threading
import requests
from datetime import datetime
from config import (
    RESEND_API_KEY,
    RESEND_FROM_EMAIL,
    EMAIL_DESTINATARIO_DEMO,
    EMAIL_MODO_DEMO,
    EMAIL_ENABLED,
)

RESEND_URL = "https://api.resend.com/emails"


def _log(mensagem):
    """Log simples no terminal com timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[EMAIL {timestamp}] {mensagem}")


def _renderizar_template_html(titulo, mensagem, info_item=None, cta_texto=None):
    """
    Monta o HTML do email com identidade visual da Afya.

    Args:
        titulo: título principal (ex: "Boa notícia!")
        mensagem: corpo do texto
        info_item: dict opcional com info do item (nome, local, data)
        cta_texto: texto opcional do botão de ação

    Returns:
        string HTML formatado
    """
    info_html = ""
    if info_item:
        info_html = f"""
        <div style="background:#FDF2F8;border-left:4px solid #E6007E;padding:16px 20px;border-radius:8px;margin:20px 0;">
            <div style="font-size:16px;font-weight:bold;color:#0A0A0B;margin-bottom:8px;">
                {info_item.get('nome', '')}
            </div>
            <div style="font-size:14px;color:#52525B;line-height:1.6;">
                {f"📍 {info_item['local']}<br>" if info_item.get('local') else ''}
                {f"🗓 {info_item['data']}<br>" if info_item.get('data') else ''}
                {f"🏷 {info_item['categoria']}" if info_item.get('categoria') else ''}
            </div>
        </div>
        """

    cta_html = ""
    if cta_texto:
        cta_html = f"""
        <div style="text-align:center;margin:32px 0;">
            <a href="#" style="background:#E6007E;color:white;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:bold;display:inline-block;">
                {cta_texto}
            </a>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>{titulo}</title>
    </head>
    <body style="margin:0;padding:0;background:#F4F4F5;font-family:'Segoe UI',Arial,sans-serif;">
        <div style="max-width:600px;margin:40px auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.06);">

            <!-- Cabeçalho com logo Afya -->
            <div style="background:#E6007E;padding:24px;text-align:center;">
                <div style="display:inline-block;background:#0A0A0B;padding:12px 18px;border-radius:8px;">
                    <span style="color:#E6007E;font-size:24px;font-weight:bold;">Afya</span>
                    <span style="color:#E6007E;font-size:10px;margin-left:6px;">CENTRO UNIVERSITÁRIO UNIMA · AL</span>
                </div>
            </div>

            <!-- Corpo da mensagem -->
            <div style="padding:32px 28px;">
                <h1 style="font-size:22px;font-weight:bold;color:#0A0A0B;margin:0 0 12px 0;">
                    {titulo}
                </h1>
                <p style="font-size:15px;color:#52525B;line-height:1.6;margin:0;">
                    {mensagem}
                </p>
                {info_html}
                {cta_html}
            </div>

            <!-- Rodapé -->
            <div style="border-top:1px solid #E4E4E7;padding:20px 28px;text-align:center;background:#FAFAFA;">
                <p style="font-size:12px;color:#71717A;margin:0;line-height:1.5;">
                    Este é um email automático do sistema <strong>Achados Unima Afya</strong>.<br>
                    Não responda diretamente a este email.<br>
                    Em caso de dúvida: <a href="mailto:achados@unima.afya.edu.br" style="color:#E6007E;">achados@unima.afya.edu.br</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def _renderizar_template_texto(titulo, mensagem, info_item=None):
    """Versão em texto puro (fallback para clientes que não renderizam HTML)."""
    linhas = [
        "=" * 50,
        "ACHADOS UNIMA AFYA",
        "=" * 50,
        "",
        titulo,
        "-" * 50,
        mensagem,
        "",
    ]

    if info_item:
        linhas.append("Detalhes do item:")
        if info_item.get('nome'):
            linhas.append(f"  Nome: {info_item['nome']}")
        if info_item.get('local'):
            linhas.append(f"  Local: {info_item['local']}")
        if info_item.get('data'):
            linhas.append(f"  Data: {info_item['data']}")
        if info_item.get('categoria'):
            linhas.append(f"  Categoria: {info_item['categoria']}")
        linhas.append("")

    linhas.extend([
        "-" * 50,
        "Este é um email automático.",
        "Não responda diretamente.",
        "Suporte: achados@unima.afya.edu.br",
        "=" * 50,
    ])

    return "\n".join(linhas)


def _enviar_via_resend(destinatario, assunto, corpo_html, corpo_texto):
    """
    Faz a chamada HTTP real para a API Resend.
    Roda em thread separada para não travar a UI.
    """
    try:
        response = requests.post(
            RESEND_URL,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": RESEND_FROM_EMAIL,
                "to": [destinatario],
                "subject": assunto,
                "html": corpo_html,
                "text": corpo_texto,
            },
            timeout=10,
        )

        if response.status_code == 200:
            email_id = response.json().get("id", "?")
            _log(f"✓ Enviado para {destinatario} (id: {email_id})")
            return True
        else:
            _log(f"✗ Erro {response.status_code}: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        _log(f"✗ Timeout ao enviar para {destinatario}")
        return False
    except Exception as e:
        _log(f"✗ Exceção: {e}")
        return False


def enviar_email(destinatario, assunto, titulo, mensagem, info_item=None, cta_texto=None):
    """
    Função pública para enviar emails. Faz tudo de forma assíncrona
    (thread separada) para não travar a interface.

    Args:
        destinatario: email do destinatário real (ex: "leonardo@afya.edu.br")
        assunto: assunto do email
        titulo: título grande no corpo do email
        mensagem: texto principal
        info_item: dict opcional {nome, local, data, categoria}
        cta_texto: texto opcional do botão call-to-action
    """
    if not EMAIL_ENABLED:
        _log(f"[DESABILITADO] Email para {destinatario} não foi enviado")
        return

    # Em modo demo, sobrescreve o destinatário real
    destino_final = EMAIL_DESTINATARIO_DEMO if EMAIL_MODO_DEMO else destinatario

    # Renderiza HTML e texto
    corpo_html = _renderizar_template_html(titulo, mensagem, info_item, cta_texto)
    corpo_texto = _renderizar_template_texto(titulo, mensagem, info_item)

    # Modo simulação: sem API key, só registra no terminal
    if not RESEND_API_KEY:
        _log("=" * 60)
        _log("MODO SIMULAÇÃO (sem API key configurada)")
        _log(f"Para: {destino_final}  (destinatário original: {destinatario})")
        _log(f"Assunto: {assunto}")
        _log(f"Título: {titulo}")
        _log(f"Mensagem: {mensagem[:100]}{'...' if len(mensagem) > 100 else ''}")
        _log("=" * 60)
        return

    # Envio real em thread separada (não trava UI)
    thread = threading.Thread(
        target=_enviar_via_resend,
        args=(destino_final, assunto, corpo_html, corpo_texto),
        daemon=True,
    )
    thread.start()


# ============================================
# FUNÇÕES DE ALTO NÍVEL — eventos específicos do sistema
# ============================================

def notificar_mudanca_status(aluno_email, aluno_nome, item, novo_status):
    """Notifica o aluno que o status do seu item mudou."""
    nomes_status = {
        "analise": "Em análise pelo setor",
        "encontrado": "Item encontrado!",
        "devolvido": "Item devolvido",
        "naoachado": "Não encontrado",
    }

    titulos = {
        "analise": "Sua solicitação está em análise",
        "encontrado": "Boa notícia! Seu item foi encontrado",
        "devolvido": "Item devolvido com sucesso",
        "naoachado": "Atualização sobre sua solicitação",
    }

    mensagens = {
        "analise": f"Olá {aluno_nome.split()[0]}! O setor de achados está verificando sua solicitação. Vamos te avisar assim que tivermos novidades.",
        "encontrado": f"Olá {aluno_nome.split()[0]}! Localizamos um item que pode ser seu. Acesse o sistema para confirmar e combinar a retirada.",
        "devolvido": f"Olá {aluno_nome.split()[0]}! Confirmamos a devolução do seu item. Obrigado por usar nosso sistema!",
        "naoachado": f"Olá {aluno_nome.split()[0]}! Após buscas, infelizmente não conseguimos localizar seu item. Caso ele apareça, entraremos em contato.",
    }

    enviar_email(
        destinatario=aluno_email,
        assunto=f"[Achados Unima] {nomes_status.get(novo_status, novo_status)}",
        titulo=titulos.get(novo_status, "Atualização da sua solicitação"),
        mensagem=mensagens.get(novo_status, "Houve uma atualização na sua solicitação."),
        info_item={
            "nome": item.get("nome"),
            "local": item.get("local"),
            "data": item.get("data_ocorrido"),
            "categoria": item.get("categoria"),
        },
        cta_texto="Ver detalhes no sistema" if novo_status == "encontrado" else None,
    )


def notificar_nova_mensagem(destinatario_email, destinatario_nome, remetente_nome, item, texto_mensagem):
    """Notifica que houve nova mensagem no chat."""
    enviar_email(
        destinatario=destinatario_email,
        assunto=f"[Achados Unima] Nova mensagem de {remetente_nome}",
        titulo=f"Você recebeu uma nova mensagem",
        mensagem=(
            f"Olá {destinatario_nome.split()[0]}! {remetente_nome} enviou uma mensagem "
            f"sobre o caso \"{item.get('nome', 'sua solicitação')}\":\n\n"
            f"\"{texto_mensagem[:200]}{'...' if len(texto_mensagem) > 200 else ''}\""
        ),
        info_item={
            "nome": item.get("nome"),
            "local": item.get("local"),
            "categoria": item.get("categoria"),
        },
        cta_texto="Responder no sistema",
    )


def notificar_nova_perda(funcionario_email, funcionario_nome, aluno_nome, item):
    """Notifica o funcionário que um aluno cadastrou uma nova perda."""
    enviar_email(
        destinatario=funcionario_email,
        assunto=f"[Achados Unima] Nova perda reportada — {item.get('categoria', '')}",
        titulo="Nova solicitação no mural",
        mensagem=(
            f"Olá {funcionario_nome.split()[0]}! O aluno {aluno_nome} reportou uma "
            f"nova perda que aguarda triagem do setor."
        ),
        info_item={
            "nome": item.get("nome"),
            "local": item.get("local"),
            "data": item.get("data_ocorrido"),
            "categoria": item.get("categoria"),
        },
        cta_texto="Atender solicitação",
    )
