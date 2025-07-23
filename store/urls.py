from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('produto/<int:produto_id>/', views.produto_detail, name='produto_detail'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('adicionar/<int:produto_id>/', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('remover/<int:produto_id>/', views.remover_carrinho, name='remover_carrinho'),
    path('checkout/', views.checkout, name='checkout'),
    path('atualizar_carrinho/', views.atualizar_carrinho, name='atualizar_carrinho'),
    path('api/carrinho-total/', views.carrinho_total_ajax, name='carrinho_total_ajax'),
    path('categoria/<int:categoria_id>/', views.produtos_por_categoria, name='produtos_por_categoria'),
    path('nossaslojas/', views.nossas_lojas, name='nossas_lojas'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('buscar/', views.buscar_produtos, name='buscar_produtos'),
    path('contato/', views.contato, name='contato'),
    path('faq/', views.faq, name='faq'),
    path('politica-de-privacidade/', views.politica_privacidade, name='politica_privacidade'),
    path('termos-de-uso/', views.termos_uso, name='termos_uso'),
    path('ofertas/', views.ofertas, name='ofertas'),

]
