from django import forms
from .models import Pedido

LOJAS_OPCOES = [
    ("kennedy", "Teles Acabamento Kennedy"),
    ("camboa", "Teles Acabamento Camboa"),
    ("africanos", "Teles Acabamento Africanos"),
]

OPCAO_ENTREGA_CHOICES = [
    ("entrega", "Entrega gratuita"),
    ("retirada", "Retirada em loja"),
]

class CheckoutForm(forms.ModelForm):
    nome = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'readonly': 'readonly'}))
    cep = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    endereco = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label="Endereço (opcional)")

    opcao_entrega = forms.ChoiceField(
        choices=OPCAO_ENTREGA_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Forma de recebimento:"
    )

    loja_retirada = forms.ChoiceField(
        choices=LOJAS_OPCOES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label='Loja para retirada (obrigatório):'
    )

    class Meta:
        model = Pedido
        fields = ['nome', 'email', 'cep', 'endereco', 'opcao_entrega', 'loja_retirada']

    def __init__(self, *args, **kwargs):
        mostrar_lojas = kwargs.pop('mostrar_lojas', False)
        mostrar_endereco = kwargs.pop('mostrar_endereco', False)
        permitir_opcao_entrega = kwargs.pop('permitir_opcao_entrega', False)
        super().__init__(*args, **kwargs)

        # Remove os campos que não devem aparecer
        if not permitir_opcao_entrega:
            self.fields.pop('opcao_entrega')

        if not mostrar_lojas:
            self.fields.pop('loja_retirada')
        else:
            self.fields['loja_retirada'].required = True

        if not mostrar_endereco:
            self.fields.pop('endereco')
