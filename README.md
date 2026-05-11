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
git clone https://github.com/ViniciusTelesProgramador/teles-site-django.git
cd teles-site-django
```

### 2. Crie o ambiente virtual

```bash
python -m venv venv
```

### 3. Ative o ambiente virtual
```bash
venv\Scripts\activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```
Se o arquivo requirements.txt ainda não existir:

```bash
pip freeze > requirements.txt
```

## 🛠️ Rodando o servidor

```bash
python manage.py migrate
python manage.py runserver
```
Acesse no navegador:
http://127.0.0.1:8000

## 📦 Compilando Tailwind CSS (opcional)
Se estiver usando Tailwind via Node.js:

```bash
npm install
npx tailwindcss -i ./static/src/input.css -o ./static/css/styles.css --watch
```
Se estiver usando Tailwind já compilado (via CDN), ignore essa etapa.

# #👤 Usuário Admin (opcional)

Crie um superusuário para acessar o painel administrativo:
```bash
python manage.py createsuperuser
```

Acesse: http://127.0.0.1:8000/admin


## 📂 Estrutura básica do projeto

```csharp
teles-site-django/
│
├── app/                  # App principal Django
├── static/               # Arquivos estáticos (CSS, imagens, JS)
├── templates/            # Templates HTML
├── manage.py
├── requirements.txt
└── README.md
```

## 📌 Observações
O banco padrão usado é o SQLite, simples e funcional para desenvolvimento.

Você pode modificar o settings.py para usar outro banco, como PostgreSQL.




## 🏗️ Sobre o Projeto

Este e-commerce foi desenvolvido para uso real na **Teles Construções**, loja de materiais de construção em São Luís, MA.

**Problemas que o sistema resolve:**
- Catálogo de produtos acessível online para clientes
- Gestão de estoque e produtos via painel administrativo
- Registro e acompanhamento de pedidos
- Redução de atendimentos manuais por telefone

**O que aprendi construindo isso:**
- Arquitetura de aplicações Django em produção
- Integração de Tailwind CSS com templates Django
- Gestão de arquivos de mídia e estáticos
- Deploy e configuração de ambiente real

---

## 👨‍💻 Autor

**Marcos Teles** — AI Automation Developer  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/marcos-vinicius-teles-b57a1b272/)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:developer.teles@gmail.com)


