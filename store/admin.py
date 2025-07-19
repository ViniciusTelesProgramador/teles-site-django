from django.contrib import admin
from .models import Categoria, Produto
from .models import Pedido
from .models import PedidoItem

admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(Pedido)
admin.site.register(PedidoItem)

