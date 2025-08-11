from django.urls import path
from . import views
from .views import activate_view
from .views import toggle_favorito_view

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
    path('minha-conta/', views.painel_usuario, name='painel_usuario'),
    path('minha-conta/editar/', views.editar_perfil_view, name='editar_perfil'),
    path("checkout/pagar/", views.checkout_mercado_pago, name="checkout_mercado_pago"),
    path("pedido/concluido/", views.pagamento_sucesso, name="pagamento_sucesso"),
    path("pedido/erro/", views.pagamento_erro, name="pagamento_erro"),
    path("pedido/pendente/", views.pagamento_pendente, name="pagamento_pendente"),
    path('ativar/<uidb64>/<token>/', activate_view, name='activate'),
    path('favorito/<int:produto_id>/', toggle_favorito_view, name='toggle_favorito'),
    path('favoritos/', views.favoritos_view, name='favoritos'),
    path('produtos/', views.catalogo, name='catalogo'),

]

from django.contrib.auth import views as auth_views

path('minha-conta/alterar-senha/', auth_views.PasswordChangeView.as_view(
    template_name='store/alterar_senha.html',
    success_url='/minha-conta/'
), name='alterar_senha'),

# Recuperar senha
path('recuperar-senha/', auth_views.PasswordResetView.as_view(
    template_name='store/password_reset.html',
    email_template_name='store/password_reset_email.html',
    subject_template_name='store/password_reset_subject.txt',
    success_url='/recuperar-senha/enviado/'
), name='password_reset'),

path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
    template_name='store/password_reset_done.html'
), name='password_reset_done'),

path('recuperar-senha/confirmar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
    template_name='store/password_reset_confirm.html',
    success_url='/recuperar-senha/completo/'
), name='password_reset_confirm'),

path('recuperar-senha/completo/', auth_views.PasswordResetCompleteView.as_view(
    template_name='store/password_reset_complete.html'
), name='password_reset_complete'),

