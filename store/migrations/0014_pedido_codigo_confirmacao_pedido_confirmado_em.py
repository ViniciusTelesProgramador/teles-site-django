from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_pedido_atualizado_em_pedido_external_reference_and_more'),
    ]


    operations = [
        migrations.AddField(
            model_name="pedido",
            name="codigo_confirmacao",
            field=models.CharField(
                max_length=12,
                null=True,     # <- permite nulo agora
                blank=True,    # <- permite em branco agora
                default=None,  # <- sem default gerador e SEM unique aqui
            ),
        ),
        migrations.AddField(
            model_name="pedido",
            name="confirmado_em",
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
