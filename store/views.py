from django.shortcuts import render, get_object_or_404
from .models import PedidoItem, Produto, Pedido
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from .models import Categoria
from django.shortcuts import render
from .models import Produto, Categoria
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import messages

def home(request):
    produtos = Produto.objects.all()
    return render(request, 'store/home.html', {'produtos': produtos})


def produto_detail(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    return render(request, 'store/produto_detail.html', {'produto': produto})


def adicionar_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    # Pega carrinho da sessão ou cria vazio
    carrinho = request.session.get('carrinho', {})

    # Obtém a quantidade enviada pelo formulário
    quantidade = int(request.POST.get('quantidade', 1))

    if str(produto_id) in carrinho:
        carrinho[str(produto_id)]['quantidade'] += quantidade
    else:
        carrinho[str(produto_id)] = {
            'nome': produto.nome,
            'preco': float(produto.preco),
            'quantidade': quantidade
        }

    request.session['carrinho'] = carrinho
    return HttpResponseRedirect(reverse('carrinho'))



def carrinho(request):
    carrinho = request.session.get('carrinho', {})
    total = 0

    # Vamos calcular o subtotal de cada item e atualizar no dicionário
    for item in carrinho.values():
        item['subtotal'] = item['preco'] * item['quantidade']
        total += item['subtotal']

    return render(request, 'store/carrinho.html', {'carrinho': carrinho, 'total': total})


def remover_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})

    produto_id_str = str(produto_id)
    if produto_id_str in carrinho:
        del carrinho[produto_id_str]

    request.session['carrinho'] = carrinho
    return HttpResponseRedirect(reverse('carrinho'))


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nome', 'email', 'endereco', 'cep']


def checkout(request):
    carrinho = request.session.get('carrinho', {})
    frete = 0.00

    if request.method == 'POST':
        cep = request.POST.get('cep', '')

        if cep.startswith('01'):
            frete = 10.00
        elif cep.startswith('20'):
            frete = 25.00
        else:
            frete = 40.00

        # Salva uma cópia segura do carrinho
        carrinho_original = carrinho.copy()

        total = sum(item['preco'] * item['quantidade'] for item in carrinho_original.values())
        total += frete

        form = CheckoutForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.total = total
            pedido.save()

            # Agora usamos a cópia garantida
            for produto_id, item in carrinho_original.items():
                PedidoItem.objects.create(
                    pedido=pedido,
                    produto_nome=item['nome'],
                    preco=item['preco'],
                    quantidade=item['quantidade']
                )

            # Limpa o carrinho apenas depois
            request.session['carrinho'] = {}

            return render(request, 'store/checkout_sucesso.html', {
                'pedido': pedido,
                'frete': frete
            })
    else:
        form = CheckoutForm()
        total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    return render(request, 'store/checkout.html', {
        'form': form,
        'carrinho': carrinho,
        'total': total,
        'frete': frete
    })


def atualizar_carrinho(request):
    if request.method == 'POST':
        carrinho = request.session.get('carrinho', {})

        for key in request.POST:
            if key.startswith('quantidade_'):
                produto_id = key.split('_')[1]
                nova_qtd = int(request.POST.get(key, 1))
                if produto_id in carrinho:
                    if nova_qtd > 0:
                        carrinho[produto_id]['quantidade'] = nova_qtd
                    else:
                        del carrinho[produto_id]

        request.session['carrinho'] = carrinho
        return HttpResponseRedirect(reverse('carrinho'))



def carrinho_total_ajax(request):
    carrinho = request.session.get('carrinho', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    return JsonResponse({'total': round(total, 2)})




def index(request):
    categorias = Categoria.objects.all()
    # Adicione categorias no contexto
    return render(request, 'sua_template.html', {'categorias': categorias})


def produtos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    produtos = Produto.objects.filter(categoria=categoria)
    return render(request, 'store/produtos_por_categoria.html', {
        'categoria': categoria,
        'produtos': produtos
    })


def nossas_lojas(request):
    lojas = [
        {
            'nome': 'Teles Acabamento Kennedy',
            'endereco': 'Av. Kennedy, 1506, Fátima - São Luís/MA - CEP 65015-560',
            'telefone': '(98) 3222-6048',
            'trocas': '(98) 9999-9999',
            'horarios': [
                'Segunda a Sexta: 08:00 às 18:00',
                'Sábado: 08:00 às 12:00',
                'Domingo: Fechado'
            ],
            'imagem': 'img/lojas/teles kennedy.png',
            'telefone_link': 'tel:9832489999',
            'maps_link': 'https://maps.google.com/?q=Teles+Acabamento+Kennedy',
            'whatsapp_link': 'https://wa.me/5598982281027'
        },
        {
            'nome': 'Teles Acabamento Camboa',
            'endereco': 'Av. Camboa, 30, Liberdade - São Luís/MA - CEP 65035-048',
            'telefone': '(98) 3221-1058',
            'trocas': '(98) 9999-9999',
            'horarios': [
                'Segunda a Sexta: 08:00 às 18:00',
                'Sábado: 08:00 às 12:00',
                'Domingo: Fechado'
            ],
            'imagem': 'img/lojas/teles camboa.png',
            'telefone_link': 'tel:XXXXXXXXXXX',
            'maps_link': 'https://maps.google.com/?q=SEGUNDA+LOJA',
            'whatsapp_link': 'https://wa.me/5598982281027'
        },
        {
            'nome': 'Teles Acabamento Africanos',
            'endereco': 'Av. dos Africanos, Q.49 Lote 19, Coroado - São Luís/MA - CEP 65042-245',
            'telefone': '(98) 3243-6319',
            'trocas': '(98) 9999-9999',
            'horarios': [
                'Segunda a Sexta: 08:00 às 18:00',
                'Sábado: 08:00 às 12:00',
                'Domingo: Fechado'
            ],
            'imagem': 'img/lojas/teles africanos.png',
            'telefone_link': 'tel:XXXXXXXXXXX',
            'maps_link': 'https://maps.google.com/?q=TERCEIRA+LOJA',
            'whatsapp_link': 'https://wa.me/5598982281027'
        }
    ]
    return render(request, 'store/nossas_lojas.html', {'lojas': lojas})



def home(request):
    produtos = Produto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'store/home.html', {
        'produtos': produtos,
        'categorias': categorias
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=username, password=senha)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso.')
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('home')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('password')
        senha2 = request.POST.get('password2')

        if senha != senha2:
            messages.error(request, 'As senhas não coincidem.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já está em uso.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'E-mail já cadastrado.')
        else:
            user = User.objects.create_user(username=username, email=email, password=senha)
            user.save()
            messages.success(request, 'Cadastro realizado com sucesso. Faça login.')
            return redirect('login')

    return render(request, 'store/register.html')