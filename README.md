#  Achados Unima Afya

Sistema de gestão de itens perdidos para o Centro Universitário Afya Unima Maceió.

Desenvolvido em Python com CustomTkinter, SQLite e integração com a API ImgBB para upload de imagens.

## 📋 Pré-requisitos

- Python 3.10 ou superior
- Conexão com internet (para upload de imagens via ImgBB)

Recomendado: use um ambiente virtual para isolar dependências.

No Windows (PowerShell):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

No Windows (cmd):

```cmd
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```
## 🚀 Como rodar

### 1. Instalar dependências

Abra o terminal na pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

### 2. (Opcional) Configurar ImgBB

Para que o upload de imagens funcione de verdade:

1. Crie uma conta gratuita em https://imgbb.com
2. Acesse https://api.imgbb.com e clique em "Get API Key"
3. Abra o arquivo `config.py`
4. Substitua o valor de `IMGBB_API_KEY` pela sua chave

Se não configurar, o sistema funciona normalmente, mas as imagens ficam apenas com o nome do arquivo (sem upload real).

### 3. Executar

```bash
python main.py
```

No PowerShell (se estiver usando o venv criado acima):

```powershell
& .\\.venv\\Scripts\\Activate.ps1
python main.py
```

## 👤 Usuários de teste

O sistema já vem com 4 usuários cadastrados para você testar:

**Alunos:**
- Leonardo Silva (leonardo@afya.edu.br)
- Ana Maria (ana@afya.edu.br)

**Funcionários:**
- Maria Fernandes (maria@afya.edu.br)
- Carlos Souza (carlos@afya.edu.br)

Na tela de login, basta clicar no usuário desejado.

## 📂 Estrutura do projeto

```
achados_unima/
├── main.py              # Ponto de entrada do app
├── config.py            # Cores, fontes e configurações
├── database.py          # Banco SQLite e queries
├── api/
│   └── imgbb.py         # Upload de imagens via API ImgBB
├── screens/
│   ├── login.py         # Tela de login
│   ├── home_aluno.py    # Dashboard do aluno
│   ├── cadastro.py      # Cadastrar item perdido
│   ├── disponiveis.py   # Galeria de itens achados
│   ├── admin.py         # Painel do funcionário
│   └── detalhe.py       # Detalhe + chat
├── components/
│   └── widgets.py       # Componentes reutilizáveis
├── assets/
│   └── (imagens)
├── requirements.txt
└── README.md
```

## 🎯 Funcionalidades implementadas

- ✅ Login com diferenciação aluno/funcionário
- ✅ Cadastro de item perdido com foto, categoria e localização
- ✅ Listagem de solicitações ativas do aluno com status
- ✅ Galeria de itens disponíveis com busca e filtro
- ✅ Painel administrativo com filtros e busca
- ✅ Chat aluno ↔ funcionário
- ✅ Mudança de status com linha do tempo
- ✅ Upload de imagens via API ImgBB

## 🧪 Testes

O sistema vem pré-populado com dados de exemplo (itens perdidos, mensagens de chat, itens achados) para facilitar a apresentação e os testes de usabilidade.
