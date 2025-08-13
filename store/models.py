# store/models.py
import secrets
from django.db import models
from django.contrib.auth.models import User


# =========================
# Utils
# =========================
ALFABETO_CODIGO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sem 0/O/I/1

def gerar_codigo_unico() -> str:
    # Não consulta o banco! (evita erro na 1ª migração)
    return "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(8))


# =========================
# Catálogo
# =========================
class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    icone = models.ImageField(upload_to='icones_categorias/', blank=True, null=True)

    def __str__(self):
        return self.nome


class Marca(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, default='')
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField()
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    marca = models.ForeignKey('Marca', on_delete=models.SET_NULL, null=True, blank=True)

    imagem = models.ImageField(upload_to='produtos/capa/', null=True, blank=True)
    codigo_barras = models.CharField(max_length=50, blank=True, null=True)

    em_oferta = models.BooleanField(default=False)
    preco_antigo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preco_novo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    destaque = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

    def get_preco_display(self):
        return self.preco_novo if (self.em_oferta and self.preco_novo) else self.preco

    def __str__(self):
        return self.nome


class ImagemProduto(models.Model):
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='produtos/imagens/')


# =========================
# Pedido
# =========================
class Pedido(models.Model):
    STATUS = [
        ("aguardando", "Aguardando pagamento"),
        ("pago", "Pago"),
        ("pendente", "Pendente"),
        ("recusado", "Recusado"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    endereco = models.TextField()
    cep = models.CharField(max_length=10, blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    total = models.DecimalField(max_digits=10, decimal_places=2)

    loja_retirada = models.CharField(max_length=100, blank=True, null=True)
    opcao_entrega = models.CharField(
        max_length=10,
        choices=[("entrega", "Entrega"), ("retirada", "Retirada")],
        blank=True, null=True
    )

    # Integração MP
    status = models.CharField(max_length=20, choices=STATUS, default="aguardando")
    external_reference = models.CharField(max_length=64, unique=True, blank=True, null=True)
    mp_payment_id = models.CharField(max_length=64, blank=True, null=True)

    # Código de confirmação para retirada/entrega + timestamp de confirmação
    codigo_confirmacao = models.CharField(
        max_length=12,
        unique=True,
        default=gerar_codigo_unico,
    )
    confirmado_em = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.nome}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto_nome = models.CharField(max_length=200)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.preco * self.quantidade

    def __str__(self):
        return f"{self.produto_nome} (x{self.quantidade})"


# =========================
# Usuário / Favoritos
# =========================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cep = models.CharField(max_length=9, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Favorito(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'produto')

    def __str__(self):
        return f"{self.user.username} ♥ {self.produto.nome}"
