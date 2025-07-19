# 🛍️ Site da Teles - E-commerce em Django + Tailwind

Este projeto é um site de e-commerce para a loja **Teles Acabamentos**, desenvolvido com **Django** e **Tailwind CSS**.  
Foi criado com foco em desempenho, usabilidade e facilidade de manutenção.

---

## 🚀 Tecnologias utilizadas

- [Python 3.11+](https://www.python.org)
- [Django 4.x](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [SQLite3](https://www.sqlite.org/index.html) (banco de dados padrão do Django)
- HTML + Jinja (Templates)

---

## ✅ Requisitos para rodar o projeto

Antes de iniciar, você precisa ter instalado:

- Python 3.11 ou superior
- Git
- Pip (gerenciador de pacotes do Python)
- (Opcional) Node.js e NPM — apenas se for compilar o Tailwind localmente

---

## ⚙️ Como rodar o projeto localmente

### 1. Clone o repositório

```bash
git clone https://github.com/SEU-USUARIO/teles-site.git
cd teles-site
2. Crie o ambiente virtual
bash
Copiar
Editar
python -m venv venv
3. Ative o ambiente virtual
No Windows:

bash
Copiar
Editar
venv\Scripts\activate
No Linux / Mac:

bash
Copiar
Editar
source venv/bin/activate
4. Instale as dependências
bash
Copiar
Editar
pip install -r requirements.txt
Se o arquivo requirements.txt ainda não existir, você pode criar com:

bash
Copiar
Editar
pip freeze > requirements.txt
🛠️ Rodando o servidor
bash
Copiar
Editar
python manage.py migrate
python manage.py runserver
Acesse no navegador:
http://127.0.0.1:8000

📦 Compilando Tailwind CSS (opcional)
Se estiver usando Tailwind via Node.js:

bash
Copiar
Editar
npm install
npx tailwindcss -i ./static/src/input.css -o ./static/css/styles.css --watch
Se estiver usando Tailwind já compilado (via CDN), ignore essa etapa.

👤 Usuário Admin (opcional)
Crie um superusuário para acessar o painel administrativo:

bash
Copiar
Editar
python manage.py createsuperuser
Acesse: http://127.0.0.1:8000/admin

📂 Estrutura básica do projeto
csharp
Copiar
Editar
teles-site/
│
├── app/                  # App principal Django
├── static/               # Arquivos estáticos (CSS, imagens, JS)
├── templates/            # Templates HTML
├── manage.py
├── requirements.txt
└── README.md
📌 Observações
O banco padrão usado é o SQLite, simples e funcional para desenvolvimento.

Você pode modificar o settings.py para usar outro banco, como PostgreSQL.

📬 Contato
Desenvolvido por Seu Nome Aqui
Se quiser contribuir ou tiver dúvidas, fique à vontade para abrir uma issue ou fazer um fork.

javascript
Copiar
Editar
