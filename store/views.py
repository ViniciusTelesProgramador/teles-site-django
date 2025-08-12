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
from .forms import CheckoutForm
import mercadopago
from django.conf import settings
from django.views.decorators.http import require_POST
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.db.models import Q
from .models import Produto
from django.db.models import Q
from .models import Produto, Categoria, Favorito
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from .models import Pedido, PedidoItem





def home(request):
    # lista completa usada no grid principal
    produtos = Produto.objects.all()

    # menu e carrossel de categorias
    categorias = Categoria.objects.all()

    # carrosséis
    ofertas = Produto.objects.filter(em_oferta=True)[:12]   # até 12 itens
    novidades = Produto.objects.order_by('-id')[:12]        # mais recentes

    # ids favoritados do usuário (pra pintar os corações ao carregar a página)
    fav_ids = set()
    if request.user.is_authenticated:
        fav_ids = set(
            Favorito.objects.filter(user=request.user)
                            .values_list('produto_id', flat=True)
        )

    return render(request, 'store/home.html', {
        'produtos': produtos,
        'categorias': categorias,
        'ofertas': ofertas,
        'novidades': novidades,
        'produtos_favoritados': fav_ids,
    })



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
    ordenar = request.GET.get('ordenar')  # novo: pega ordenação da URL

    produtos = Produto.objects.filter(categoria=categoria)

    if marca_id:
        produtos = produtos.filter(marca_id=marca_id)

    if ordenar == 'menor_preco':
        produtos = produtos.order_by('preco')
    elif ordenar == 'maior_preco':
        produtos = produtos.order_by('-preco')
    elif ordenar == 'lancamento':
        produtos = produtos.order_by('-data_criacao')  # ou 'data_lancamento' se tiver esse campo

    # marcas disponíveis apenas dentro da categoria
    marcas = Marca.objects.filter(produto__categoria=categoria).distinct()

    context = {
        'categoria': categoria,
        'produtos': produtos,
        'marcas': marcas,
        'marca_selecionada': int(marca_id) if marca_id else None,
        'ordenar': ordenar,  # necessário para manter valor no <select>
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
        # 1. Verificação do reCAPTCHA v2
        token = request.POST.get('g-recaptcha-response')
        recaptcha_response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': token
            }
        )
        result = recaptcha_response.json()
        if not result.get('success'):
            messages.error(request, 'Erro na verificação do reCAPTCHA.')
            return redirect('register')

        # 2. Dados do formulário
        username = request.POST.get('email')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        cep = request.POST.get('cep')
        senha = request.POST.get('password')
        senha2 = request.POST.get('password2')

        # 3. Validações
        if senha != senha2:
            messages.error(request, 'As senhas não coincidem.')
        elif len(senha) < 8 or not any(c.isupper() for c in senha) or not any(c.isdigit() for c in senha):
            messages.error(request, 'A senha deve ter pelo menos 8 caracteres, uma letra maiúscula e um número.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'E-mail já cadastrado.')
        else:
            # 4. Criação do usuário (inativo) e perfil
            user = User.objects.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=first_name,
                last_name=last_name
            )
            user.is_active = False  # desativa até a confirmação
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.cep = cep
            profile.save()

            # 5. Envia o e-mail de ativação
            send_activation_email(request, user)

            messages.success(request, 'Cadastro realizado! Verifique seu e-mail para ativar sua conta.')
            return redirect('login')

    # GET request
    return render(request, 'store/register.html', {
        'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY
    })




def buscar_produtos(request):
    query = request.GET.get('q')
    ordenar = request.GET.get('ordenar')

    resultados = Produto.objects.filter(
        Q(nome__icontains=query) | Q(descricao__icontains=query)
    ) if query else []

    if ordenar == 'menor_preco':
        resultados = resultados.order_by('preco')
    elif ordenar == 'maior_preco':
        resultados = resultados.order_by('-preco')
    elif ordenar == 'lancamento':
        resultados = resultados.order_by('-data_criacao')  # ajuste conforme seu modelo

    context = {
        'query': query,
        'ordenar': ordenar,
        'resultados': resultados,
        'categorias': Categoria.objects.all(),  # usado no base.html
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

# store/views.py


@login_required
@require_http_methods(["GET","POST"])
def checkout_mercado_pago(request):
    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    carrinho = request.session.get("carrinho", {})
    if not carrinho:
        messages.error(request, "Carrinho vazio.")
        return redirect("carrinho")

    total = sum(item["preco"] * item["quantidade"] for item in carrinho.values())

    # dados do formulário (ajuste os names conforme seu HTML)
    nome = request.POST.get("nome") or (request.user.get_full_name() or request.user.username)
    email = request.POST.get("email") or (request.user.email or "sem-email@local.test")
    endereco = request.POST.get("endereco") or ""
    cep = request.POST.get("cep") or ""
    opcao_entrega = request.POST.get("opcao_entrega")  # "entrega" ou "retirada"
    loja_retirada = request.POST.get("loja_retirada")  # se existir

    # 1) cria o pedido local
    pedido = Pedido.objects.create(
        usuario=request.user,
        nome=nome,
        email=email,
        endereco=endereco,
        cep=cep,
        total=total,
        opcao_entrega=opcao_entrega,
        loja_retirada=loja_retirada,
        status="aguardando",
    )

    # 2) cria os itens
    for item in carrinho.values():
        PedidoItem.objects.create(
            pedido=pedido,
            produto_nome=item["nome"],          # ajuste ao seu dicionário
            preco=item["preco"],
            quantidade=item["quantidade"],
        )

    # 3) define external_reference
    pedido.external_reference = f"pedido_{pedido.id}"
    pedido.save(update_fields=["external_reference"])

    public = settings.PUBLIC_URL.rstrip("/")

    preference_data = {
        "items": [{
            "title": f"Pedido #{pedido.id} - Teles",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": float(total),
        }],
        "back_urls": {
            "success": f"{public}{reverse('pagamento_sucesso')}?pedido={pedido.id}",
            "failure": f"{public}{reverse('pagamento_erro')}?pedido={pedido.id}",
            "pending": f"{public}{reverse('pagamento_pendente')}?pedido={pedido.id}",
        },
        "auto_return": "approved",
        "notification_url": f"{public}/webhooks/mercadopago/",
        "statement_descriptor": "TELES CONSTRUCOES",
        "payment_methods": {"installments": 1},
        "external_reference": pedido.external_reference,
    }

    pref = sdk.preference().create(preference_data)["response"]
    return redirect(pref["init_point"])

    
def pagamento_sucesso(request):
    pedido_id = request.GET.get("pedido")
    return render(request, "store/pagamento_sucesso.html", {"pedido_id": pedido_id})

def pagamento_erro(request):
    return render(request, "store/pagamento_erro.html")

def pagamento_pendente(request):
    return render(request, "store/pagamento_pendente.html")


import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# store/views.py (substitua o mp_webhook atual)

import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Pedido  # <-- importa o Pedido
import mercadopago
from django.conf import settings

@csrf_exempt
def mp_webhook(request):
    """
    Webhook do Mercado Pago: atualiza o Pedido com base no external_reference.
    Idempotente: não processa duas vezes o mesmo payment_id.
    """
    try:
        payload = json.loads(request.body.decode() or "{}")

        # 1) obtém o payment_id (novo/antigo formato)
        payment_id = payload.get("data", {}).get("id")
        if not payment_id and request.GET.get("topic") == "payment":
            payment_id = request.GET.get("id")

        if not payment_id:
            print("Webhook sem payment_id:", payload)
            return HttpResponse(status=200)

        # 2) consulta o pagamento no MP
        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
        info = sdk.payment().get(payment_id)["response"]

        status = info.get("status")                  # "approved" | "pending" | "rejected"
        external_ref = info.get("external_reference")

        if not external_ref:
            print("Pagamento sem external_reference:", info)
            return HttpResponse(status=200)

        # 3) localiza o pedido pelo external_reference
        try:
            pedido = Pedido.objects.get(external_reference=external_ref)
        except Pedido.DoesNotExist:
            print("Pedido não encontrado para external_reference:", external_ref)
            return HttpResponse(status=200)

        # 4) idempotência: se já processou esse payment_id, não faz de novo
        if pedido.mp_payment_id == str(payment_id):
            return HttpResponse(status=200)

        pedido.mp_payment_id = str(payment_id)

        # 5) atualiza status interno
        if status == "approved":
            pedido.status = "pago"
        elif status == "pending":
            pedido.status = "pendente"
        else:
            pedido.status = "recusado"

        pedido.save()
        print(f"[WEBHOOK] Pedido {pedido.id} → {pedido.status} (payment_id={payment_id})")

    except Exception as e:
        print("Webhook erro:", e)

    # o MP espera 200 sempre que você recebeu/entendeu
    return HttpResponse(status=200)


def send_activation_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = request.build_absolute_uri(reverse('activate', args=[uid, token]))
    
    subject = 'Ative sua conta'
    message = f'Olá {user.first_name},\n\nAtive sua conta acessando:\n{activation_link}'
    
    send_mail(subject, message, 'no-reply@seusite.com', [user.email])


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User

def activate_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Conta ativada com sucesso! Faça login.')
        return redirect('login')
    else:
        messages.error(request, 'Link de ativação inválido ou expirado.')
        return redirect('register')

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Produto, Favorito
from django.http import JsonResponse

@login_required
def toggle_favorito_view(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    favorito, created = Favorito.objects.get_or_create(user=request.user, produto=produto)

    if not created:
        favorito.delete()
        status = 'removed'
    else:
        status = 'added'

    return JsonResponse({'status': status})



@login_required
def favoritos_view(request):
    favoritos = Favorito.objects.filter(user=request.user).select_related('produto')
    return render(request, 'store/favoritos.html', {'favoritos': favoritos})

from decimal import Decimal, InvalidOperation
from django.db.models import Q, Case, When, F, DecimalField
from django.core.paginator import Paginator
from .models import Produto, Categoria, Marca, Favorito  # ajuste o import de Marca se o nome for diferente

def _parse_decimal(value):
    if not value:
        return None
    try:
        # aceita "9,90" ou "9.90"
        return Decimal(str(value).replace(',', '.'))
    except (InvalidOperation, ValueError):
        return None

def catalogo(request):
    ordenar = request.GET.get('ordenar', '-id')
    ordem = {'preco': 'preco_efetivo', '-preco': '-preco_efetivo', 'nome': 'nome', '-id': '-id'}.get(ordenar, '-id')

    categoria_id = request.GET.get('categoria')  # id único
    marcas_ids   = request.GET.getlist('marca')  # múltiplas
    preco_min    = _parse_decimal(request.GET.get('preco_min'))
    preco_max    = _parse_decimal(request.GET.get('preco_max'))
    so_ofertas   = request.GET.get('oferta') == '1'
    q            = request.GET.get('q', '').strip()

    qs = Produto.objects.filter(ativo=True)

    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)

    if marcas_ids:
        qs = qs.filter(marca_id__in=marcas_ids)

    if so_ofertas:
        qs = qs.filter(em_oferta=True)

    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(descricao__icontains=q))

    # preço efetivo: usa preco_novo quando em oferta, senão preco
    qs = qs.annotate(
        preco_efetivo=Case(
            When(em_oferta=True, then=F('preco_novo')),
            default=F('preco'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    if preco_min is not None:
        qs = qs.filter(preco_efetivo__gte=preco_min)
    if preco_max is not None:
        qs = qs.filter(preco_efetivo__lte=preco_max)

    qs = qs.order_by(ordem, '-id')

    paginator = Paginator(qs, 24)
    page_obj  = paginator.get_page(request.GET.get('page'))

    # opções do sidebar
    categorias = Categoria.objects.all().order_by('nome')
    if categoria_id:
        marcas = Marca.objects.filter(produto__ativo=True, produto__categoria_id=categoria_id).distinct().order_by('nome')
    else:
        marcas = Marca.objects.filter(produto__ativo=True).distinct().order_by('nome')

    # range de páginas “elíptico”
    page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=1, on_ends=1)

    # mantemos os params (sem 'page') para a paginação
    params = request.GET.copy()
    params.pop('page', None)
    query_without_page = params.urlencode()

    fav_ids = set()
    if request.user.is_authenticated:
        fav_ids = set(Favorito.objects.filter(user=request.user).values_list('produto_id', flat=True))

    return render(request, 'store/catalogo.html', {
        'page_obj': page_obj,
        'page_range': page_range,
        'ordenar': ordenar,
        'q': q,
        'categorias': categorias,
        'marcas': marcas,
        'categoria_id': str(categoria_id or ''),
        'marcas_ids': set(marcas_ids),
        'preco_min': request.GET.get('preco_min', ''),
        'preco_max': request.GET.get('preco_max', ''),
        'so_ofertas': so_ofertas,
        'query_without_page': query_without_page,
        'produtos_favoritados': fav_ids,
    })