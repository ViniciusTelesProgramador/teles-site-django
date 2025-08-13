# store/utils.py
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator


def build_activation_link(request, user):
    """
    Gera a URL absoluta para ativação de conta.
    """
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    path = reverse("ativar_conta", args=[uidb64, token])
    return request.build_absolute_uri(path)


def send_activation_email(request, user):
    """
    Envia o e-mail de ativação para o usuário recém-cadastrado.
    Usa o EMAIL_BACKEND configurado no settings (console por enquanto).
    """
    subject = "Ative sua conta - Teles"
    link = build_activation_link(request, user)
    message = (
        f"Olá, {user.get_full_name() or user.username}!\n\n"
        f"Obrigado pelo cadastro. Para ativar sua conta, clique no link abaixo:\n\n"
        f"{link}\n\n"
        f"Se você não fez este cadastro, ignore este e-mail."
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@teles.com.br")
    send_mail(subject, message, from_email, [user.email], fail_silently=False)
