from django import forms
from .models import Pedido

LOJAS_OPCOES = [
    ("kennedy", "Teles Acabamento Kennedy"),
    ("camboa", "Teles Acabamento Camboa"),
    ("africanos", "Teles Acabamento Africanos"),
]

class CheckoutForm(forms.ModelForm):
    nome = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'readonly': 'readonly'}))
    cep = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    endereco = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label="Endereço")
    
    loja_retirada = forms.ChoiceField(
        choices=LOJAS_OPCOES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label='Loja para retirada (obrigatório):'
    )

    class Meta:
        model = Pedido
        fields = ['nome', 'email', 'cep', 'endereco', 'loja_retirada']

    def __init__(self, *args, **kwargs):
        mostrar_lojas = kwargs.pop('mostrar_lojas', False)
        mostrar_endereco = kwargs.pop('mostrar_endereco', False)
        super().__init__(*args, **kwargs)

        if not mostrar_lojas:
            self.fields.pop('loja_retirada')
        else:
            self.fields['loja_retirada'].required = True

        if not mostrar_endereco:
            self.fields.pop('endereco')

