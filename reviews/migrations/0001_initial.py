from django.db import migrations, models
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("catalog", "0001_initial"),
        ("marketplace", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductReview",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("rating", models.PositiveSmallIntegerField()),
                ("comment", models.TextField(blank=True)),
                (
                    "product",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="reviews", to="catalog.product"),
                ),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="product_reviews", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["product", "rating"], name="reviews_pro_product_6a6b15_idx"),
                    models.Index(fields=["user"], name="reviews_pro_user_3d3af0_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="StoreReview",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("rating", models.PositiveSmallIntegerField()),
                ("comment", models.TextField(blank=True)),
                (
                    "store",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="reviews", to="marketplace.store"),
                ),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="store_reviews", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["store", "rating"], name="reviews_sto_store_7b2a56_idx"),
                    models.Index(fields=["user"], name="reviews_sto_user_2c4b3a_idx"),
                ],
            },
        ),
        migrations.AlterUniqueTogether(
            name="productreview",
            unique_together={("user", "product")},
        ),
        migrations.AlterUniqueTogether(
            name="storereview",
            unique_together={("user", "store")},
        ),
    ]

