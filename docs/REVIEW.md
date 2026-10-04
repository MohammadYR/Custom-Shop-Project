# Code review: problems found and fixes

## خلاصه فارسی

این سند فهرست مشکلات امنیتی و منطقی پیدا شده در شاخه `main` و نحوه رفع هر کدام است (PR شماره ۱، شاخه `fix/security-and-logic`).
مهم‌ترین موارد: خریدار می‌توانست سفارش خود را «پرداخت‌شده» کند یا قیمت آیتم سفارش را تغییر دهد، کاتالوگ برای کاربران ناشناس قابل ویرایش بود، کاربر می‌توانست خود را فروشنده کند، رمز ایمیل و SECRET_KEY در کد بود، OTP با `random` ساخته و در لاگ چاپ می‌شد، موجودی انبار با لغو مکرر سفارش افزایش می‌یافت و امکان فروش بیش از موجودی وجود داشت.
برای هر باگ یک تست رگرسیون نوشته شده است. اقدامات دستی لازم (باطل‌کردن رمز ایمیل، تغییر SECRET_KEY، خصوصی‌کردن ریپو) در انتهای سند آمده است.

---

Every item was reproduced on `main` before fixing. The regression test that covers it is listed in the last column.

## Security

| # | Problem | Fix | Test |
|---|---------|-----|------|
| 1 | `OrderViewSet` was a `ModelViewSet` with a writable `status`: `PATCH /api/sales/orders/{id}/ {"status":"PAID"}` returned 200 and the payment became `VERIFIED`. | `ReadOnlyModelViewSet` + `POST /orders/{id}/cancel/` (PENDING only, through the state machine). All order fields are read-only. | `tests/test_sales_api_regressions.py::test_buyer_cannot_mark_own_order_paid` |
| 2 | `OrderItemViewSet` let buyers edit `unit_price`, `quantity`, `order` (a 100 order became 0.50). | Read-only; items are created only by checkout. | `test_buyer_cannot_edit_order_items` |
| 3 | Catalog viewsets used `AllowAny` on `ModelViewSet`s: anonymous users could create/edit/delete categories and products. | `core.permissions.IsAdminOrReadOnly` (read: everyone, write: staff). | `tests/test_catalog_api.py::test_anonymous_cannot_write_catalog`, `test_regular_user_cannot_write_catalog` |
| 4 | `PATCH /api/accounts/me/ {"is_seller": true}` worked. | `id`, `username`, `is_seller` read-only in `UserMeSerializer`. | `tests/test_accounts_regressions.py::test_user_cannot_make_himself_seller_via_me` |
| 5 | Ownership fields were writable: `CartItem.cart`, `Store.owner`, `Seller.user`; a store item could be moved into another seller's store. | Read-only and set server-side; `StoreItemSerializer` only accepts the requester's store and refuses to move items. | `tests/test_marketplace_regressions.py`, `test_cart_item_cart_field_is_read_only` |
| 6 | OTP codes came from `random`, had no attempt limit, OTP verify had no throttle, SMS codes were `print()`ed, OTP login ignored `is_active`, `RegisterThrottle` was commented out and no throttle rates were configured. | `accounts/services.py`: `secrets.randbelow`, constant-time compare, `OTP.attempts` with `OTP_MAX_ATTEMPTS` (5), only the newest code is valid. `ScopedRateThrottle` on register/login/OTP request/OTP verify with `DEFAULT_THROTTLE_RATES`. Logging with masked targets and no codes. Inactive users get 403. | `test_otp_*`, `test_register_is_throttled`, `test_otp_verify_is_throttled`, `test_sms_task_does_not_print_or_log_the_code` |
| 7 | `config/settings/base.py` contained a hardcoded `SECRET_KEY`, a Gmail app password as the default of `EMAIL_HOST_PASSWORD` and (commented) an SMS API key; `CORS_ALLOW_ALL_ORIGINS=True` everywhere; `prod.py` only set `DEBUG=False`. | Every secret and deployment value is read from env (`python-dotenv`, `config/env.py`). `prod.py` refuses to start without `DJANGO_SECRET_KEY`/`DJANGO_ALLOWED_HOSTS`, uses explicit CORS origins, SSL redirect, HSTS, secure cookies and a Redis cache. **The leaked credentials are still in git history and must be revoked (see below).** | `manage.py check --deploy` |

Other settings problems fixed at the same time: `BASE_DIR` pointed to `config/` (sqlite DB, media and static roots lived inside `config/`); `JAZZMIN_SETTINGS`/`JAZZMIN_UI_TWEAKS` were defined twice (the second silently replaced the first); `STATICFILES_DIRS` pointed to the deleted `frontend/frontend/public`; `config/wsgi.py`/`asgi.py` defaulted to the empty `config.settings` package; `.env.example` listed many variables nothing reads (Stripe, PayPal, Twilio...).

## Logic bugs

| # | Problem | Fix | Test |
|---|---------|-----|------|
| 8 | `restock_on_order_cancel` (pre_save) restocked on every transition into CANCELLED: CANCELLED→PENDING→CANCELLED raised stock 10→14. Admin actions used `queryset.update()` and skipped every side effect. | State machine in `sales/services.py` (`PENDING→PAID`, `PENDING→CANCELLED` only). `cancel_order` restocks with `F()` inside `transaction.atomic` under a row lock; `mark_order_paid` sets `paid_at`, verifies the payment and queues emails on commit. Used by the API, payment verify and admin actions. Signal removed. | `tests/test_order_state_machine.py`, `tests/test_sales_admin.py` |
| 9 | `create_order_from_cart` had no locking (overselling) and accepted an empty cart. | Moved to `sales.services`; `select_for_update` on the store items (pk order), conditional `F()` decrement, `bulk_create`, empty cart rejected, everything rolls back on error. | `tests/test_checkout_regressions.py` |
| 10 | Soft delete vs. unique constraints: `cart.items.all().delete()` only soft-deleted, so re-adding the item after checkout raised `IntegrityError` (500). Same for Cart, default Address, `Category.name`, `Store.name`, `StoreItem.sku`, variants and reviews. | Unique constraints now have `condition=Q(deleted_at__isnull=True)`; cart lines are hard-deleted; `get_or_create_cart` restores a soft-deleted cart. Migrations added. | `test_same_item_can_be_added_again_after_checkout`, `test_*_after_soft_delete` |
| 11 | `GET /api/marketplace/items/` always 500 (`select_related("product")` on a model without `product`). | Correct `select_related`. | `test_store_items_list_no_longer_500` |
| 12 | `RegisterAsSellerView` used `ValidationError` without importing it (second call → `NameError` 500) and was not atomic. | Input serializer + `marketplace.services.register_as_seller` in one transaction. | `test_register_as_seller_twice_returns_400_not_500`, `test_register_as_seller_is_atomic` |
| 13 | Persian names produced an empty slug; the second Persian category/product/store crashed. | `core.utils.unique_slugify` (`allow_unicode=True` + `-2`, `-3` suffix + fallback). | `test_persian_names_get_unique_unicode_slugs`, `test_persian_store_names_get_unique_slugs` |
| 14 | OTP sent twice (view and `post_save` signal). | Signal removed; `request_otp` sends once on commit. | `test_otp_is_sent_exactly_once` |
| 15 | Payments hardcoded sandbox URLs and read settings that did not exist (`ZARINPAL_MERCHANT_ID`), while the defined `ZP_*` settings were unused; `to_rial` ignored `PRICE_UNIT`; verify was not idempotent. | `payments/gateway.py` (`ZarinpalClient`, settings-driven, errors → 502), `to_rial` honours `PRICE_UNIT`, verify short-circuits for paid orders and transitions under a lock. HTTP mocked in tests. | `tests/test_payments_gateway.py`, `tests/test_payments_api.py` |
| 16 | Username/email lower-cased in `post_save` → "Ali" then "ali" collided with `IntegrityError`. | `pre_save` normalization + case-insensitive serializer validation (400). | `test_case_variant_username_is_rejected_with_400` |
| 17 | `prune_expired_otps_task` only soft-deleted. | Hard delete. | `test_prune_expired_otps_hard_deletes` |
| 18 | The signal un-set the previous default address but the serializer rejected a new default. | Rejection removed; signal behaviour kept. | `accounts/tests.py::test_address_crud_and_default` |
| 19 | `Review.clean()` raised `ValueError`; no DB check on rating. | `ValidationError` + `CheckConstraint` 1..5; duplicate review → 400; reviewed object immutable. | `tests/test_reviews_regressions.py` |
| 20 | `ready()` in marketplace/sales/payments swallowed signal import errors. | Plain imports. | `tests/test_signals_wired.py` |
| 21 | Dead code: `"/api/marketplace/..//stores"` branch, duplicate `my_router`, fully commented-out modules/blocks, an invalid `core/templates/admin/base_site.html`. | Removed. | `tests/test_mystore_endpoints.py` |
| 22 | `Order`/`Cart` totals ignored prefetching (`self.items.select_related(...)`) → N+1 in list endpoints. | Totals iterate `self.items.all()`; querysets prefetch `store_item__variant__product` and `store_item__store`. | `test_order_list_has_no_n_plus_one`, `test_cart_has_no_n_plus_one` |

## Tests and CI

* The original suite had 10 of 22 tests failing (un-namespaced `reverse()` names, duplicate `Cart` creation, missing `Product.price`, `..//` URLs). The tests were fixed, not the behaviour, except where the behaviour was one of the bugs above (e.g. the default-address test).
* `conftest.py` moved to the repo root with shared factories; the cache is cleared between tests (throttling).
* `.github/workflows/ci.yml`: system check, `makemigrations --check`, OpenAPI validation with `--fail-on-warn`, `pytest --cov`. `codeql.yml` added for the README badge.

## Manual steps for the owner

1. **Revoke the Gmail app password** that was committed in `config/settings/base.py`, and revoke the SMS (Kavenegar) API key that was in a comment there. Removing them from the code does not remove them from git history.
2. **Rotate `SECRET_KEY`**: the old key is public; set a new `DJANGO_SECRET_KEY` in every environment.
3. Make the repository **Private** (the course requires it; it is currently public).
4. Reconcile the diverged `dev` branch (its reviews migrations and `static/js/admin.js` were ported here; `core/aliases.py` was intentionally not copied).
5. Local SQLite databases moved from `config/db.sqlite3` to `./db.sqlite3` and media from `config/media/` to `./media/` (BASE_DIR fix). Move the files if you want to keep local data.
