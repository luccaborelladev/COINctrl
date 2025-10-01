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

- 4. Configurar OAuth Google (opcional)
Criar projeto no https://cloud.google.com/cloud-console?utm_source=bing&utm_medium=cpc&utm_campaign=latam-BR-all-pt-dr-BKWS-all-all-trial-e-dr-1710136-LUAC0016489&utm_content=text-ad-none-any-DEV_c-CRE_-ADGP_Hybrid+%7C+BKWS+-+MIX+%7C+Txt_+Management+Tools-Console-KWID_134065238444-kwd-78065736327892:loc-20&utm_term=KW_console+cloud+google-ST_console+cloud+google&&msclkid=315c8f2c53b31d598b21e7f11b7975e3&gclid=315c8f2c53b31d598b21e7f11b7975e3&gclsrc=3p.ds&gad_source=7&gad_campaignid=15217860715

Depois clicar em console
Criar um projeto 
Ir em APIS e Serviços > Biblioteca
Ir em Credenciais > Tela de consentimento OAuth
Ir em Credenciais > Criar credenciais > ID do cliente OAuth



console.cloud.google.com
Ativar Google+ API
Criar credenciais OAuth 2.0
Baixar JSON como google_credentials.json
Adicionar URLs autorizadas:
http://127.0.0.1:5000
http://127.0.0.1:5000/auth/google/callback

5. Executar aplicação

python run.py