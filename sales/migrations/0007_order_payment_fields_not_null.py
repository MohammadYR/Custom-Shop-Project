from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0006_order_payment_fields_fill_nulls"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="payment_authority",
            field=models.CharField(blank=True, db_index=True, default="", max_length=64),
        ),
        migrations.AlterField(
            model_name="order",
            name="payment_ref_id",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
    ]
