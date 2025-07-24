from django.contrib import admin
from .models import Categoria, Produto, Pedido, PedidoItem, Marca, ImagemProduto


# 🔁 Inline para múltiplas imagens
class ImagemProdutoInline(admin.TabularInline):
    model = ImagemProduto
    extra = 1


# 🔁 Admin do Produto completo
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'em_oferta', 'destaque', 'ativo']
    list_filter = ['em_oferta', 'destaque', 'ativo', 'categoria', 'marca']
    search_fields = ['nome', 'codigo_barras']

    inlines = [ImagemProdutoInline]

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'categoria', 'marca', 'codigo_barras')
        }),
        ('Estoque e Preço', {
            'fields': ('preco', 'estoque', 'em_oferta', 'preco_antigo', 'preco_novo')
        }),
        ('Imagem Principal', {
            'fields': ('imagem',)
        }),
        ('Destaques e Status', {
            'fields': ('destaque', 'ativo')
        }),
    )


# ✅ Registro dos outros modelos
admin.site.register(Categoria)
admin.site.register(Pedido)
admin.site.register(PedidoItem)
admin.site.register(Marca)
