from django import forms
from .models import Pedido

OPCAO_ENTREGA_CHOICES = (("entrega", "Entrega gratuita"), ("retirada", "Retirada em loja"))
LOJAS_OPCOES = (
    ("Loja Centro", "Loja Centro"),
    ("Loja Cohama", "Loja Cohama"),
    ("Loja São Cristóvão", "Loja São Cristóvão"),
)

class CheckoutForm(forms.ModelForm):
    nome = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'readonly': 'readonly'}))
    cep = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    opcao_entrega = forms.ChoiceField(
        choices=OPCAO_ENTREGA_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Forma de recebimento:"
    )

    # retirada
    loja_retirada = forms.ChoiceField(
        choices=LOJAS_OPCOES,
        widget=forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'}),
        required=False,
        label='Loja para retirada (obrigatório):'
    )

    # ENTREGA – campos detalhados
    rua = forms.CharField(required=False, label="Rua")
    numero = forms.CharField(required=False, label="Número")
    bairro = forms.CharField(required=False, label="Bairro")
    ponto_referencia = forms.CharField(required=False, label="Ponto de referência")
    telefone_contato = forms.CharField(required=False, label="Telefone para contato")

    class Meta:
        model = Pedido
        fields = [
            'nome', 'email', 'cep',
            'opcao_entrega', 'loja_retirada',
            'rua', 'numero', 'bairro', 'ponto_referencia', 'telefone_contato',
        ]

    def __init__(self, *args, **kwargs):
        self.mostrar_lojas = kwargs.pop("mostrar_lojas", False)
        self.mostrar_endereco = kwargs.pop("mostrar_endereco", False)
        self.permitir_opcao_entrega = kwargs.pop("permitir_opcao_entrega", False)
        super().__init__(*args, **kwargs)

        if not self.permitir_opcao_entrega:
            # força retirada quando não há entrega grátis
            self.fields['opcao_entrega'].widget = forms.HiddenInput()
            self.fields['opcao_entrega'].initial = 'retirada'

        for f in ['rua', 'numero', 'bairro', 'ponto_referencia', 'telefone_contato']:
            self.fields[f].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})

    def clean(self):
        cleaned = super().clean()
        modo = cleaned.get("opcao_entrega")

        if self.permitir_opcao_entrega and not modo:
            self.add_error("opcao_entrega", "Escolha uma forma de recebimento.")

        if modo == "retirada" and not cleaned.get("loja_retirada"):
            self.add_error("loja_retirada", "Escolha a loja para retirada.")

        if modo == "entrega":
            obrig = ["rua", "numero", "bairro", "telefone_contato"]
            for f in obrig:
                if not cleaned.get(f):
                    self.add_error(f, "Este campo é obrigatório para entregas.")
        return cleaned


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
