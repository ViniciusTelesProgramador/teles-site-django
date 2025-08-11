from .models import Produto
from .models import Categoria


def carrinho_total(request):
    carrinho = request.session.get('carrinho', {})
    valor_total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    quantidade_total = sum(item['quantidade'] for item in carrinho.values())

    return {
        'valor_total_carrinho': valor_total,
        'quantidade_total_carrinho': quantidade_total
    }

def categorias_context(request):
    return {
        'categorias': Categoria.objects.all()
    }

from .models import Favorito

def favoritos_ids(request):
    """
    Disponibiliza a lista de IDs de produtos favoritados do usuário logado
    em todos os templates como 'produtos_favoritados'.
    """
    if request.user.is_authenticated:
        ids = list(
            Favorito.objects.filter(user=request.user)
            .values_list('produto_id', flat=True)
        )
    else:
        ids = []
    return {'produtos_favoritados': ids}
