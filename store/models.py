from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    icone = models.ImageField(upload_to='icones_categorias/', blank=True, null=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, default='')
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField()
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    marca = models.ForeignKey('Marca', on_delete=models.SET_NULL, null=True, blank=True)  # nova

    imagem = models.ImageField(upload_to='produtos/capa/', null=True, blank=True)  # imagem principal
    codigo_barras = models.CharField(max_length=50, blank=True, null=True)
    
    em_oferta = models.BooleanField(default=False)
    preco_antigo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preco_novo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    destaque = models.BooleanField(default=False)  # nova
    ativo = models.BooleanField(default=True)  # nova

    def get_preco_display(self):
        return self.preco_novo if self.em_oferta and self.preco_novo else self.preco

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    endereco = models.TextField()
    cep = models.CharField(max_length=10, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    loja_retirada = models.CharField(max_length=100, blank=True, null=True)
    opcao_entrega = models.CharField(max_length=10, choices=[("entrega", "Entrega"), ("retirada", "Retirada")], blank=True, null=True)  # NOVO

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

class Marca(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class ImagemProduto(models.Model):
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='produtos/imagens/')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cep = models.CharField(max_length=9, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
