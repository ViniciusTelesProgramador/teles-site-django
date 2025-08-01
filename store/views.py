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
from .models import Marca
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib import messages
from .forms import CheckoutForm
import mercadopago
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.http import require_POST



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

    for produto_id in list(carrinho.keys()):
        item = carrinho[produto_id]
        item['subtotal'] = item['preco'] * item['quantidade']
        total += item['subtotal']

        try:
            produto = Produto.objects.get(id=produto_id)
            item['imagem_url'] = produto.imagem.url if produto.imagem else ''
        except Produto.DoesNotExist:
            item['imagem_url'] = ''

    return render(request, 'store/carrinho.html', {'carrinho': carrinho, 'total': total})


def remover_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})

    produto_id_str = str(produto_id)
    if produto_id_str in carrinho:
        del carrinho[produto_id_str]

    request.session['carrinho'] = carrinho
    return HttpResponseRedirect(reverse('carrinho'))



@login_required
def checkout(request):
    carrinho = request.session.get('carrinho', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    cep = request.user.profile.cep if hasattr(request.user, 'profile') else ''
    is_sao_luis = cep.startswith('650')
    entrega_gratis = is_sao_luis and total >= 400

    # ✅ Regras para exibição dos campos
    mostrar_lojas = not entrega_gratis  # se não ganhou entrega, obriga escolher loja
    mostrar_endereco = entrega_gratis  # mostra campo de endereço apenas se entrega grátis
    permitir_opcao_entrega = entrega_gratis  # mostra os radios somente para entrega grátis

    if request.method == 'POST':
        form = CheckoutForm(
            request.POST,
            mostrar_lojas=mostrar_lojas,
            mostrar_endereco=mostrar_endereco,
            permitir_opcao_entrega=permitir_opcao_entrega
        )
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.nome = f"{request.user.first_name} {request.user.last_name}"
            pedido.email = request.user.email
            pedido.cep = cep
            pedido.total = total
            pedido.usuario = request.user

            # salva o campo opcao_entrega, se disponível
            opcao_entrega = form.cleaned_data.get('opcao_entrega')
            if opcao_entrega:
                pedido.opcao_entrega = opcao_entrega  # precisa existir no model se quiser salvar

            pedido.save()

            for produto_id, item in carrinho.items():
                PedidoItem.objects.create(
                    pedido=pedido,
                    produto_nome=item['nome'],
                    preco=item['preco'],
                    quantidade=item['quantidade']
                )

            request.session['carrinho'] = {}
            return render(request, 'store/checkout_sucesso.html', {'pedido': pedido})

    else:
        form = CheckoutForm(
            mostrar_lojas=mostrar_lojas,
            mostrar_endereco=mostrar_endereco,
            permitir_opcao_entrega=permitir_opcao_entrega,
            initial={
                'nome': f"{request.user.first_name} {request.user.last_name}",
                'email': request.user.email,
                'cep': cep
            }
        )
    request.session['total'] = total

    return render(request, 'store/checkout.html', {
        'form': form,
        'carrinho': carrinho,
        'total': total,
        'entrega_gratis': entrega_gratis,
        'mostrar_lojas': mostrar_lojas,
        'mostrar_endereco': mostrar_endereco,
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
    categoria = Categoria.objects.get(id=categoria_id)
    marca_id = request.GET.get('marca')  # pega marca da URL

    produtos = Produto.objects.filter(categoria=categoria)

    if marca_id:
        produtos = produtos.filter(marca_id=marca_id)

    # filtrar marcas que têm produtos nessa categoria
    marcas = Marca.objects.filter(produto__categoria=categoria).distinct()

    context = {
        'categoria': categoria,
        'produtos': produtos,
        'marcas': marcas,
        'marca_selecionada': int(marca_id) if marca_id else None
    }

    return render(request, 'store/produtos_por_categoria.html', context)

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
        email = request.POST.get('email')
        senha = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=senha)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso.')
            return redirect('home')
        else:
            messages.error(request, 'E-mail ou senha inválidos.')

    return render(request, 'store/login.html')



def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('home')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')  # email será usado como username
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        cep = request.POST.get('cep')
        senha = request.POST.get('password')
        senha2 = request.POST.get('password2')

        # Validações
        if senha != senha2:
            messages.error(request, 'As senhas não coincidem.')
        elif len(senha) < 8 or not any(c.isupper() for c in senha) or not any(c.isdigit() for c in senha):
            messages.error(request, 'A senha deve ter pelo menos 8 caracteres, uma letra maiúscula e um número.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'E-mail já cadastrado.')
        else:
            # Cria o usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=first_name,
                last_name=last_name
            )

            # Cria ou garante que o perfil existe
            profile, created = Profile.objects.get_or_create(user=user)
            profile.cep = cep
            profile.save()

            messages.success(request, 'Cadastro realizado com sucesso. Faça login.')
            return redirect('login')

    return render(request, 'store/register.html')

from django.db.models import Q
from .models import Produto

def buscar_produtos(request):
    query = request.GET.get('q')
    resultados = Produto.objects.filter(
        Q(nome__icontains=query) | Q(descricao__icontains=query)
    ) if query else []

    context = {
        'query': query,
        'resultados': resultados,
        'categorias': Categoria.objects.all(),  # se usa em base.html
    }
    return render(request, 'store/busca.html', context)


from django.shortcuts import render

def contato(request):
    return render(request, 'store/contato.html')

def faq(request):
    return render(request, 'store/faq.html')


def politica_privacidade(request):
    return render(request, 'store/politica_privacidade.html')

def termos_uso(request):
    return render(request, 'store/termos_uso.html')

def ofertas(request):
    produtos = Produto.objects.filter(em_oferta=True)
    return render(request, 'store/ofertas.html', {'produtos': produtos})


@login_required
def painel_usuario(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-criado_em')
    profile = request.user.profile  # pega o CEP e outras infos
    return render(request, 'store/painel_usuario.html', {
        'pedidos': pedidos,
        'profile': profile
    })



@login_required
def editar_perfil_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        cep = request.POST.get('cep')

        # Validação básica
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'Este e-mail já está em uso.')
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = email  # se você usa o e-mail como username
            user.save()

            profile.cep = cep
            profile.save()

            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('painel_usuario')

    return render(request, 'store/editar_perfil.html', {
        'user': user,
        'profile': profile
    })


@login_required
@require_POST
def checkout_mercado_pago(request):
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    carrinho = request.session.get("carrinho", {})
    if not carrinho:
        messages.error(request, "Carrinho vazio.")
        return redirect("carrinho")

    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    # ✅ Fora do dicionário, ANTES do preference_data
    ngrok_base = "https://26bb4ffc23fe.ngrok-free.app"

    preference_data = {
        "items": [
            {
                "title": "Pedido Teles",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(total),
            }
        ],
        "back_urls": {
            "success": ngrok_base + reverse("pagamento_sucesso"),
            "failure": ngrok_base + reverse("pagamento_erro"),
            "pending": ngrok_base + reverse("pagamento_pendente"),
        },
        "auto_return": "approved",
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        print("🟢 Preferência Mercado Pago:", preference_response)

        if not preference_response or "response" not in preference_response:
            messages.error(request, "Erro ao criar preferência de pagamento.")
            return redirect("checkout")

        preference = preference_response["response"]

        if "init_point" not in preference:
            messages.error(request, "URL de pagamento não encontrada.")
            return redirect("checkout")

        return redirect(preference["init_point"])

    except Exception as e:
        messages.error(request, f"Erro ao conectar com Mercado Pago: {str(e)}")
        return redirect("checkout")
    
from django.shortcuts import render

def pagamento_sucesso(request):
    return render(request, "pagamento_sucesso.html")

def pagamento_erro(request):
    return render(request, "pagamento_erro.html")

def pagamento_pendente(request):
    return render(request, "pagamento_pendente.html")
