# 📝 Histórico de Versões

Todas as mudanças importantes deste projeto serão documentadas aqui.

O formato segue Keep a Changelog e este projeto adere ao Versionamento Semântico.

---

## [2.0.0] — Versão Web

### Adicionado
- Deploy em produção via Vercel
- Mockup interativo HTML com 7 telas (web + mobile)
- Documentação completa da API ImgBB no README
- Código de conduta para colaboradores
- Padrões de commit (Conventional Commits)

### Modificado
- README reformulado com instruções detalhadas
- Estrutura do projeto reorganizada para web

---

## [1.2.0] — Notificações por email

### Adicionado
- Integração com a API Resend para envio de emails
- Notificação automática quando o status do item muda
- Notificação automática quando há nova mensagem no chat
- Notificação automática quando aluno cadastra nova perda
- Templates HTML com identidade visual da Afya
- Modo demo para apresentações

### Modificado
- Atualização do database.py com triggers de notificação

---

## [1.1.0] — Tema claro/escuro e Dashboard

### Adicionado
- Botão de alternância entre tema claro e escuro
- Dashboard de estatísticas para funcionários
- Gráficos com matplotlib (categorias, locais, status)
- Tela de descarte e doações para itens expirados
- Validação de email acadêmico (@afya.edu.br)
- Auto-formatação de nomes no cadastro
- Logout com confirmação

### Corrigido
- Upload de imagens via ImgBB (correção do encoding base64)
- Instruções de criação de ambiente virtual no Windows

---

## [1.0.0] — Lançamento inicial

### Adicionado
- Sistema completo em Python com CustomTkinter
- Banco de dados SQLite com 4 tabelas relacionadas
- Login com diferenciação aluno/funcionário
- Cadastro de itens perdidos
- Galeria de itens achados
- Painel administrativo
- Chat entre aluno e funcionário
- Integração com a API ImgBB para hospedagem de imagens
- Identidade visual oficial da Afya