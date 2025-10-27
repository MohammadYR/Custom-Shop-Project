from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="productreview",
            index=models.Index(
                fields=["deleted_at", "updated_at"],
                name="reviews_pro_del_upd_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="storereview",
            index=models.Index(
                fields=["deleted_at", "updated_at"],
                name="reviews_sto_del_upd_idx",
            ),
        ),
    ]

