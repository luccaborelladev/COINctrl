# COINctrl - Controle Financeiro Pessoal

Sistema de controle financeiro pessoal desenvolvido com Flask.

## Funcionalidades Implementadas

### ✅ Sistema de Autenticação
- **Cadastro de usuários** com validação completa
- **Login/Logout** seguro com gerenciamento de sessão
- **OAuth 2.0 com Google** para login social
- **Senhas criptografadas** com Werkzeug
- **Validações de segurança** e proteção contra ataques básicos

## Tecnologias Utilizadas

- **Backend:** Flask 2.3.3
- **Banco de Dados:** SQLite com SQLAlchemy
- **Autenticação:** Flask-Login + Google OAuth 2.0
- **Segurança:** Werkzeug (hashing), validações customizadas
- **Frontend:** HTML5, CSS3 (responsivo)

## Instalação e Execução
```bash
- 1. Clonar o repositório

git clone <url-do-repositorio>
cd COINctrl 

- 2. Configurar ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

- 3. Instalar dependências
pip install -r requirements.txt

- 4. Configurar OAuth Google
1 - cp .env.example .env
2 - Solicitar credenciais Google ao admin
3 - Editar .env com credenciais recebidas


5. Executar aplicação

python run.py