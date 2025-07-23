from django.contrib import admin
from .models import Categoria, Produto, Pedido, PedidoItem


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'em_oferta']
    fields = ['nome', 'descricao', 'preco', 'estoque', 'categoria', 'imagem', 'em_oferta', 'preco_antigo', 'preco_novo']


admin.site.register(Categoria)
admin.site.register(Pedido)
admin.site.register(PedidoItem)
