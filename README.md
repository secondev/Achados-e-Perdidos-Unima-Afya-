# 🌸 Achados Unima Afya

Sistema de gestão de itens perdidos para o **Centro Universitário Afya Unima Maceió**.

**🔗 Vitrine web do projeto:** (https://achados-e-perdidos-unima-afya-1c1yto2sy.vercel.app/)

---

## 📋 Sobre o projeto

O **Achados Unima Afya** é uma solução desenvolvida para digitalizar a gestão de itens perdidos e achados dentro do campus da Afya Unima Maceió. O projeto conecta alunos ao setor responsável por meio de uma interface intuitiva, com identidade visual oficial da instituição.

O projeto é entregue em **duas versões complementares**, cada uma com um propósito específico:

### 🌐 Versão Web (vitrine interativa)

A versão web está disponível online no link acima. É uma **vitrine demonstrativa interativa** do sistema, construída em HTML, CSS e JavaScript puro, que permite ao usuário:

- Navegar por todas as 7 telas do sistema
- Visualizar a aplicação em formatos web e mobile (lado a lado)
- Acessar o "modo interativo" que mostra a função de cada elemento da interface
- Compreender o fluxo completo do sistema sem precisar instalar nada

Essa versão serve como apresentação pública do projeto, ideal para demonstração a stakeholders, alunos e funcionários da Afya.

### 🖥️ Versão Desktop (sistema funcional completo)

A versão funcional completa foi desenvolvida em **Python com CustomTkinter** e está disponível no mesmo repositório. Ela contém:

- Banco de dados **SQLite** funcional com 4 tabelas relacionadas
- Integração real com **2 APIs externas** (ImgBB e Resend)
- Sistema de login com perfis diferentes (aluno e funcionário)
- Chat em tempo real entre usuários
- Notificações por email automáticas
- Dashboard com estatísticas e gráficos (matplotlib)
- Tema claro/escuro

Essa versão é a que rodaria em produção no setor de achados da Afya.

> 💡 **Por que duas versões?** Sistemas reais frequentemente têm múltiplas vertentes (web pública, app mobile, painel admin desktop). A versão web é a porta de entrada pública; a versão desktop é a ferramenta operacional do setor. Ambas compartilham a mesma identidade visual e fluxo de negócio.

---

## 🚀 Como executar localmente

### Versão Web (vitrine HTML)

A versão web é um arquivo HTML estático que roda em qualquer navegador moderno, sem dependências externas.

**Clone o repositório:**
\`\`\`bash
git clone https://github.com/secondev/Achados-e-Perdidos-Unima-Afya-.git
cd Achados-e-Perdidos-Unima-Afya-
\`\`\`

**Abra o arquivo `index.html`:**

- **Windows:** clique duas vezes no arquivo
- **macOS:** `open index.html`
- **Linux:** `xdg-open index.html`

**Alternativa: servir via servidor local** (recomendado):
\`\`\`bash
python -m http.server 8000
# Acesse http://localhost:8000 no navegador
\`\`\`

### Versão Desktop (Python)

**Pré-requisitos:** Python 3.10 ou superior.

\`\`\`bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
source .venv/bin/activate      # macOS/Linux

pip install -r requirements.txt
python main.py
\`\`\`

#### Usuários de teste cadastrados

**Alunos:**
- Leonardo Silva — leonardo@afya.edu.br
- Ana Maria — ana@afya.edu.br

**Funcionários:**
- Maria Fernandes — maria@afya.edu.br
- Carlos Souza — carlos@afya.edu.br

---

## 🌐 Documentação da API utilizada

### ImgBB — Hospedagem de imagens

O projeto consome a **API REST do ImgBB** para hospedar as fotos dos itens cadastrados, evitando armazenamento de binários no banco de dados.

#### Sobre a API

- **Site oficial:** https://imgbb.com
- **Documentação:** https://api.imgbb.com
- **Modelo:** REST sobre HTTPS
- **Formato de resposta:** JSON
- **Limite gratuito:** ilimitado para conta pessoal

#### Autenticação

A autenticação é feita via **API key** transmitida no corpo da requisição.

**Como obter a API key:**

1. Crie uma conta gratuita em https://imgbb.com
2. Acesse https://api.imgbb.com
3. Clique em **"Get API Key"**
4. Copie a chave gerada

**Configuração no projeto:**

\`\`\`python
# config.py
IMGBB_API_KEY = "sua_chave_aqui"
\`\`\`

> ⚠️ Nunca commite sua API key. Use o `.gitignore` ou variáveis de ambiente.

#### Endpoint utilizado

##### `POST https://api.imgbb.com/1/upload`

Realiza upload de uma imagem e retorna a URL pública hospedada.

**Parâmetros:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `key` | string | Sim | API key |
| `image` | string (base64) | Sim | Imagem codificada em base64 |
| `name` | string | Não | Nome do arquivo |
| `expiration` | integer | Não | Tempo de expiração em segundos |

**Exemplo de chamada (Python):**

\`\`\`python
import base64
import requests

with open("foto_item.jpg", "rb") as f:
    imagem_b64 = base64.b64encode(f.read())

response = requests.post(
    "https://api.imgbb.com/1/upload",
    data={
        "key": "SUA_API_KEY",
        "image": imagem_b64,
    },
    timeout=30,
)

resultado = response.json()
url_publica = resultado["data"]["url"]
\`\`\`

**Resposta de sucesso (`200`):**

\`\`\`json
{
  "data": {
    "id": "abc123",
    "title": "foto_item",
    "url": "https://i.ibb.co/abc123/foto-item.jpg",
    "size": 102400
  },
  "success": true,
  "status": 200
}
\`\`\`

#### Como contribuir com o consumo da API

1. Mantenha as chamadas isoladas em `api/imgbb.py`
2. Sempre trate exceções (`Timeout`, `ConnectionError`)
3. Use timeout explícito (recomendado: 30 segundos)
4. Faça fallback gracioso em caso de falha
5. Não bloqueie a thread principal — use `threading.Thread`

#### Tratamento de erros

| Código | Significado | Comportamento |
|---|---|---|
| 200 | Sucesso | Retorna URL pública |
| 400 | API key inválida | Loga erro e retorna `local://` |
| 403 | Limite excedido | Loga erro e retorna `local://` |
| 5xx | Erro do servidor | Loga erro e retorna `local://` |
| Timeout | Sem resposta em 30s | Loga e retorna `local://` |

---

### Resend — Envio de emails (API secundária)

O projeto também integra com a **API Resend** para envio de notificações por email aos alunos e funcionários quando ocorrem eventos no sistema.

- **Site oficial:** https://resend.com
- **Documentação:** https://resend.com/docs
- **Plano gratuito:** 100 emails/dia (3.000/mês)

Implementação completa em `api/email_service.py`.

---

## 👥 Equipe

| Membro | GitHub | Contribuições principais |
|---|---|---|
| Alan Maia | [@secondev](https://github.com/secondev) | Coordenação, deploy, integração ImgBB, feature de email |
| Leonardo R. | [@LeonardoRdo](https://github.com/LeonardoRdo) | Dashboard com gráficos, validações, tema claro/escuro |
| Pedro H. | [@PedroHML1](https://github.com/PedroHML1) | Estrutura inicial do main.py, código de conduta |
| Victor C. | [@VictorCRB](https://github.com/VictorCRB) | Auto-formatação de nomes, changelog |
| Felipe S. | [@FelpsSds](https://github.com/FelpsSds) | Fix do base64 ImgBB, instruções de venv, licença |
| Rafael V. | [@rafaelvalverdev](https://github.com/rafaelvalverdev) | Tela de descarte, queries de expirados, templates |

Histórico completo:
- [Pull Requests](https://github.com/secondev/Achados-e-Perdidos-Unima-Afya-/pulls)
- [Gráfico de contribuidores](https://github.com/secondev/Achados-e-Perdidos-Unima-Afya-/graphs/contributors)

---

## 📂 Estrutura do projeto

\`\`\`
Achados-e-Perdidos-Unima-Afya-/
├── index.html                  # Versão web (vitrine deployed)
├── main.py                     # Versão desktop Python
├── config.py                   # Cores, fontes e API keys
├── database.py                 # Banco SQLite local
├── api/
│   ├── imgbb.py               # Cliente da API ImgBB
│   └── email_service.py       # Cliente da API Resend
├── screens/                    # Telas da versão desktop
├── components/                 # Componentes reutilizáveis
├── .github/ISSUE_TEMPLATE/     # Templates de issues
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── LICENSE
├── requirements.txt
└── README.md
\`\`\`

---

## 🎯 Funcionalidades

### 👨‍🎓 Para alunos
- Cadastro de item perdido com foto, categoria e localização
- Validação de email acadêmico (@afya.edu.br)
- Dashboard pessoal com métricas
- Galeria de itens achados com busca e filtros
- Chat direto com o setor
- Notificações automáticas por email

### 👩‍💼 Para funcionários
- Painel administrativo com filtros por status
- Dashboard de estatísticas com gráficos (matplotlib)
- Triagem de solicitações com 1 clique
- Setor de descarte e doações
- Exportação de relatórios
- Notificações automáticas por email

### 🎨 Interface
- Identidade visual oficial da Afya (#E6007E)
- Tema claro/escuro
- Versão web e desktop compartilhando o mesmo design

---

## 🏗️ Arquitetura técnica

Arquitetura monolítica em camadas com padrão MVC simplificado:

- **Apresentação:** classes em `screens/` herdando de `CTkFrame`
- **Orquestração:** classe `App` em `main.py`
- **Dados:** `database.py` com queries SQL parametrizadas (proteção SQL injection)
- **Integração:** módulos em `api/` isolando chamadas HTTP

**Banco:** 4 tabelas relacionadas com chaves estrangeiras e CHECK constraints.

---

## 📄 Licença

Veja [LICENSE](./LICENSE). Projeto acadêmico do Centro Universitário Afya Unima Maceió.

---

## 🤝 Contribuição

Veja [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) e o [CHANGELOG.md](./CHANGELOG.md) para histórico de versões.
