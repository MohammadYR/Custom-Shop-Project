from django.db import migrations


def nulls_to_empty(apps, schema_editor):
    """Existing NULLs must become '' before 0007 makes the columns NOT NULL.

    Kept in its own migration: PostgreSQL refuses to ALTER a table in the same
    transaction that just updated it ("pending trigger events").
    """
    Order = apps.get_model("sales", "Order")
    Order.objects.filter(payment_authority__isnull=True).update(payment_authority="")
    Order.objects.filter(payment_ref_id__isnull=True).update(payment_ref_id="")


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0005_orderitem_status"),
    ]

    operations = [
        migrations.RunPython(nulls_to_empty, migrations.RunPython.noop),
    ]
