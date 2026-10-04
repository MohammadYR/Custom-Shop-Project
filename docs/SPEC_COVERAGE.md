# Spec coverage (Maktab130 final project)

## خلاصه فارسی
این جدول هر نیازمندی سند پروژه نهایی مکتب ۱۳۰ را به endpoint، مدل و تست مربوطه نگاشت می‌کند. همه نیازمندی‌های اجباری پیاده‌سازی شده‌اند. موارد «جزئی» یا تصمیم‌های طراحی در ستون توضیحات آمده‌اند (مثلاً تخفیف به‌صورت درصدی روی StoreItem است و کوپن پیاده‌سازی نشده؛ حذف حساب کاربری آن را غیرفعال می‌کند).

Status: ✅ done · ⚠️ done with a documented limitation · ❌ not done

## Delivery and technical notes
| Requirement | Where | Status |
|---|---|---|
| Complete README (install, run, env vars, tests) | `README.md` | ✅ |
| ERD | `docs/ERD.png` (generated from models), `docs/ERD_v1.pdf` (original) | ✅ |
| Repository private until the end | GitHub settings | ❌ owner action: the repo is public |
| Instructors added as collaborators | GitHub settings | ❌ owner action |
| Small commits, clear messages, branches + pull requests | branches `fix/security-and-logic`, `feat/spec-alignment`, PRs #13 and #14 | ✅ |
| `core` app and logical delete (HackSoft BaseModel) | `core/models.py` (`BaseModel`, `SoftDeleteQuerySet`); soft-delete aware unique constraints | ✅ `core/tests.py`, `tests/core/test_soft_delete_product.py` |
| Deploy with docker and docker compose | `Dockerfile` (gunicorn, healthcheck), `docker-compose.yml` (db, redis, web, worker, beat) | ✅ CI job `docker` |
| Settings split cleanly with `.env` | `config/settings/{base,dev,test,prod}.py`, `config/env.py`, `.env.example` | ✅ `tests/test_health_and_settings.py` |
| Up-to-date docs with request/response | drf-spectacular `/api/docs/`, `/api/redoc/`, `schema.yaml`; CI validates with `--fail-on-warn` | ✅ |
| Redis and Celery where needed | OTP delivery, order emails, seller notifications, low-stock alerts, transaction log, OTP cleanup (beat); Redis cache for throttling in prod | ✅ `tests/test_signals_wired.py`, `tests/test_order_state_machine.py` |

## Accounts (tests required)
| Requirement | Endpoint / model | Tests | Status |
|---|---|---|---|
| Register and log in with email / phone | `POST /api/accounts/register/`, `POST /api/accounts/login/` (`identifier` = email, username or phone) | `tests/test_spec_accounts.py::test_register_login_refresh_flow`, `accounts/tests.py` | ✅ |
| JWT login | SimpleJWT, `POST /api/accounts/token/refresh/` | same | ✅ |
| Login / verification via OTP | `POST /api/accounts/request-otp/`, `POST /api/accounts/verify-otp/` (email or Kavenegar SMS, 5 attempts, throttled) | `test_otp_request_verify_spec_paths_with_frontend_field_names`, `tests/test_accounts_regressions.py`, `tests/test_sms.py` | ✅ |
| View and edit profile | `GET/PATCH /api/myuser/` | `test_myuser_view_and_edit` | ✅ |
| Add, edit, delete addresses | `/api/myuser/address/` (`accounts.Address`) | `test_myuser_address_crud`, `accounts/tests.py::test_address_crud_and_default` | ✅ |
| Recent orders and order history in the profile | `/api/myuser/` → `recent_orders`, `orders_count`; `/api/myorders/` | `test_myuser_shows_recent_orders`, `tests/test_spec_cart_orders_payments.py::test_full_buyer_flow` | ✅ |
| Delete own account | `DELETE /api/myuser/` | `test_myuser_delete_deactivates` | ⚠️ deactivates (`is_active=False`) so orders/payments are kept |

## Sellers and stores (tests required)
| Requirement | Endpoint / model | Tests | Status |
|---|---|---|---|
| Any user can request to become a seller | `POST /api/myuser/register_as_seller/` (`marketplace.services.register_as_seller`, atomic) | `test_register_as_seller_spec_path`, `test_register_as_seller_*` | ✅ |
| A seller has one store with details and address | `Store` (+ `phone_number`, `email`, `website`), `StoreAddress`; `GET/POST/PATCH /api/mystore/`, `/api/mystore/addresses/` | `tests/test_spec_mystore.py`, `tests/test_store_profile.py` | ✅ one store per seller enforced in the API |
| Seller manages store items | `/api/mystore/items/` | `test_items_crud_store_is_automatic`, `test_items_of_other_sellers_are_invisible` | ✅ |
| Seller sees orders that contain their products | `GET /api/mystore/orders/` (only the seller's lines, `seller_total`) | `test_seller_sees_orders_with_only_own_lines` | ✅ |
| Seller changes the status of each order item | `OrderItem.status`; `PATCH /api/mystore/order-items/{id}/` (PENDING → SHIPPED → DELIVERED / CANCELLED) | `test_seller_changes_item_status`, `tests/test_order_item_status.py` | ✅ |

## Products and categories
| Requirement | Endpoint / model | Tests | Status |
|---|---|---|---|
| Products belong to categories | `catalog.Product.category` | `tests/test_catalog_api.py` | ✅ |
| Name, description, category, images, stock, price | `Product` (`title`/`name`, `description`, `price`), `ProductImage` (many), `stock` and `best_price` computed from store items | `tests/test_catalog_search_filter.py` | ✅ |
| A product can be sold by many stores | `StoreItem` (store × variant, own price/stock/discount) | `test_stock_best_price_and_rating` | ✅ |
| View, search and filter products | `GET /api/products/` (`search`, `category`, `category_slug`, `min_price`, `max_price`, `in_stock`, `store`, `ordering`, pagination) | `tests/test_catalog_search_filter.py`, `tests/test_spec_catalog_stores.py` | ✅ |
| Reviews and ratings for products | `POST /api/products/{id}/review_create/`, `GET …/review_list/` (`ProductReview`, rating 1-5) | `test_product_review_create_and_list`, `tests/test_reviews_regressions.py` | ✅ |
| Reviews and ratings for stores | `POST /api/stores/{id}/review_create/` (`StoreReview`) | `test_store_review_create_and_store_items` | ✅ |

## Cart and orders
| Requirement | Endpoint / model | Tests | Status |
|---|---|---|---|
| Add to cart via StoreItem | `POST /api/mycart/add_to_cart/{store_item_id}/`, `/api/mycart/items/` | `test_full_buyer_flow`, `test_add_to_cart_unknown_or_out_of_stock` | ✅ |
| Cart total and discount | `StoreItem.discount_percent`; cart `total_original_price`, `total_discount`, `total_price` | `tests/test_discounts.py` | ⚠️ percentage discount per store item; no coupons |
| Checkout | `POST /api/orders/checkout/` (`sales.services.create_order_from_cart`: row locks, no overselling) | `tests/test_checkout_regressions.py` | ✅ |
| Order contains address and items | `Order.shipping_*` snapshot + `shipping_address`, `OrderItem` price snapshot | `tests/test_checkout_address.py` | ✅ |

## Payments
| Requirement | Endpoint / model | Tests | Status |
|---|---|---|---|
| A payment record for each order | `payments.Payment` created at checkout; `GET /api/payments/` | `test_checkout_snapshots_prices_creates_payment_and_decrements_stock`, `test_payments_list_is_scoped` | ✅ |
| Order status changes after payment verification | `POST /api/payments/{order_id}/start/`, `GET /api/payments/verify/` → `mark_order_paid` (idempotent) | `tests/test_payments_api.py`, `payments/tests.py` | ✅ (Zarinpal mocked in tests; sandbox needs a merchant id) |

## Admin API
| Requirement | Endpoint | Tests | Status |
|---|---|---|---|
| Manage users (list, edit, delete) | `/api/admin/users/` | `test_admin_can_list_edit_delete_users`, `test_admin_cannot_delete_user_with_orders` | ✅ users with orders return 409 (deactivate instead) |
| Manage categories | `/api/admin/categories/` | `test_admin_categories_crud` | ✅ |
| Manage orders and payments | `/api/orders/` (+ `mark_paid`, `cancel`), `/api/payments/` | `test_staff_orders_management`, `test_payments_list_is_scoped` | ✅ |

## Django admin panel
| Requirement | Where | Status |
|---|---|---|
| Custom title instead of "Django administration" | `JAZZMIN_SETTINGS` (`site_title`, `site_header`, `site_brand`) | ✅ |
| Logo and colours | Jazzmin theme + `static/css/admin.css`; logo path from `ADMIN_LOGO` | ⚠️ logo files live in git-ignored `static/icons/` |
| Header / footer text | `welcome_sign`, `copyright` | ✅ |
| Admin actions (bulk approve orders, change status of many items, (de)activate users/products) | `OrderAdmin.mark_paid/mark_cancelled`, `OrderItemAdmin.mark_shipped/...`, user/product/seller activate actions | ✅ `tests/test_sales_admin.py`, `test_admin_bulk_ship` |
| Inlines (e.g. addresses on the user page) | `CustomUserAdmin` (profile, addresses), orders (items, payment), products (images, variants), stores (addresses, items) | ✅ |
| `list_display`, `list_filter`, `search_fields`; advanced filters | all admins; custom filters for users, orders and payments | ✅ |

## API map from the spec
All paths listed in the spec are routed in `config/api_urls.py` (and `accounts/urls.py`, `payments/urls.py`) to the same viewsets used by the older `/api/<app>/` paths, which keep working.
