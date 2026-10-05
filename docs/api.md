# API guide

The full, always-current reference is generated from the code:

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI schema: `/api/schema/` (YAML: `/api/schema.yaml`, committed copies: `schema.yaml`, `schema.json`)

This page explains the conventions and gives a map of the endpoints.

## Conventions

### Authentication

JWT via SimpleJWT. Send the access token in every authenticated request:

```http
Authorization: Bearer <access token>
```

Access tokens live 15 minutes, refresh tokens 7 days. Refresh tokens rotate:
each refresh returns a new pair and blacklists the old refresh token.

### Pagination

Every list is paginated:

```http
GET /api/products/?page=2&page_size=50
```

```json
{"count": 134, "next": "…?page=3&page_size=50", "previous": "…?page=1&page_size=50", "results": [ … ]}
```

Default page size 20, maximum 100.

### Errors

| Situation | Status | Body |
| --- | --- | --- |
| Field validation | 400 | `{"field": ["message", …]}` |
| Business rule (stock, state machine, OTP…) | 400 | `{"detail": "…", "code": "cart_error"}` |
| Not logged in / bad token | 401 | `{"detail": "…"}` |
| Not allowed | 403 | `{"detail": "…"}` |
| Not found (or not yours) | 404 | `{"detail": "…"}` |
| Rate limited | 429 | `{"detail": "…"}` |

Business-rule codes: `cart_error`, `checkout_error`, `invalid_transition`,
`invalid_otp`. See [architecture](architecture.md#errors).

### Rate limits

| Scope | Default |
| --- | --- |
| register | 5/hour |
| login | 10/min |
| OTP request | 5/min |
| OTP verify | 10/min |

All are configurable through `THROTTLE_RATE_*` environment variables.

## Endpoint map

Roles: **anyone**, **user** (logged in), **seller** (user with a store),
**staff** (`is_staff`).

### Accounts and profile

| Path | Methods | Role | Description |
| --- | --- | --- | --- |
| `/api/accounts/register/` | POST | anyone | create an account |
| `/api/accounts/login/` | POST | anyone | `{"identifier", "password"}`; identifier = email, username or phone. Returns `access` + `refresh` |
| `/api/accounts/token/refresh/` | POST | anyone | new token pair from a refresh token |
| `/api/accounts/request-otp/` | POST | anyone | send a 6-digit code by email or SMS |
| `/api/accounts/verify-otp/` | POST | anyone | check the code; `purpose=login` returns tokens |
| `/api/myuser/` | GET, PATCH, DELETE | user | profile with recent orders; DELETE deactivates the account |
| `/api/myuser/address/` | CRUD | user | address book (`{id}/set_default/` to change the default) |
| `/api/myuser/register_as_seller/` | POST | user | become a seller, optionally creating the store |

### Catalog and stores

| Path | Methods | Role | Description |
| --- | --- | --- | --- |
| `/api/categories/` | GET | anyone | categories (`?search=`, `?ordering=`) |
| `/api/products/` | GET | anyone | products, see filters below |
| `/api/products/{id}/` | GET | anyone | product with images, variants and store offers |
| `/api/products/{id}/review_list/` | GET | anyone | product reviews |
| `/api/products/{id}/review_create/` | POST | user | `{"rating": 1-5, "comment"}`, one per user |
| `/api/stores/` | GET | anyone | stores |
| `/api/stores/{id}/items/` | GET | anyone | a store's offers |
| `/api/stores/{id}/review_list/`, `/review_create/` | GET / POST | anyone / user | store reviews |

Product filters:

| Parameter | Example | Meaning |
| --- | --- | --- |
| `search` | `?search=headphone` | title, description, category name |
| `category` / `category_slug` | `?category_slug=audio` | by category |
| `min_price`, `max_price` | `?min_price=100&max_price=500` | price range |
| `in_stock` | `?in_stock=true` | at least one store has stock |
| `store` | `?store=<uuid>` | offered by that store |
| `ordering` | `?ordering=-best_price` | `price`, `best_price`, `created_at`, `title`, `rating` (prefix `-` for descending) |

### Seller area

| Path | Methods | Role | Description |
| --- | --- | --- | --- |
| `/api/mystore/` | GET, POST, PATCH | seller | own store profile |
| `/api/mystore/addresses/` | CRUD | seller | store addresses |
| `/api/mystore/items/` | CRUD | seller | offers: `sku`, `price`, `discount_percent`, `stock` |
| `/api/mystore/orders/` | GET | seller | orders that contain the seller's items |
| `/api/mystore/order-items/{id}/` | GET, PATCH | seller | `{"status": "SHIPPED"}` etc. (see the item state machine) |

### Cart, orders and payments

| Path | Methods | Role | Description |
| --- | --- | --- | --- |
| `/api/mycart/` | GET | user | cart with `total_original_price`, `total_discount`, `total_price` |
| `/api/mycart/add_to_cart/{store_item_id}/` | POST | user | `{"quantity": n}` (default 1) |
| `/api/mycart/items/` | GET, PATCH, DELETE | user | cart lines |
| `/api/orders/checkout/` | POST | user | `{"address": <id>}`; creates the order and its payment record |
| `/api/myorders/` | GET | user | order history; `{id}/cancel/` while PENDING |
| `/api/payments/` | GET | user / staff | own payments (staff: all) |
| `/api/payments/{order_id}/start/` | POST | user | returns `startpay_url` for Zarinpal |
| `/api/payments/verify/` | GET | gateway | callback: `?Authority=…&Status=OK` |

### Staff

| Path | Methods | Description |
| --- | --- | --- |
| `/api/admin/users/` | GET, PATCH, DELETE | manage users (deleting a user with orders returns 409) |
| `/api/admin/categories/` | CRUD | manage categories |
| `/api/orders/` | GET + `{id}/mark_paid/`, `{id}/cancel/` | manage orders (through the state machine) |

The Django admin at `/admin/` covers everything else.

### Legacy paths

The per-app paths (`/api/accounts/…`, `/api/catalog/…`, `/api/marketplace/…`,
`/api/sales/…`, `/api/reviews/…`) still work and use the same views.

## Walkthrough with curl

```bash
BASE=http://127.0.0.1:8000

# 1. Register and log in
curl -s -X POST $BASE/api/accounts/register/ -H 'Content-Type: application/json' \
  -d '{"username": "sara", "email": "sara@example.com", "phone_number": "09120000000", "password": "S3cure-pass!"}'
TOKEN=$(curl -s -X POST $BASE/api/accounts/login/ -H 'Content-Type: application/json' \
  -d '{"identifier": "sara@example.com", "password": "S3cure-pass!"}' | jq -r .access)
AUTH="Authorization: Bearer $TOKEN"

# 2. Find a product and one store offer for it
curl -s "$BASE/api/products/?search=headphone&in_stock=true" | jq '.results[0]'
STORE_ITEM=<store item id from the product's offers>

# 3. Add an address, fill the cart, check out
ADDRESS=$(curl -s -X POST $BASE/api/myuser/address/ -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"line1": "Valiasr St. 10", "city": "Tehran", "postal_code": "1234567890", "is_default": true}' | jq -r .id)
curl -s -X POST $BASE/api/mycart/add_to_cart/$STORE_ITEM/ -H "$AUTH" -H 'Content-Type: application/json' -d '{"quantity": 2}'
ORDER=$(curl -s -X POST $BASE/api/orders/checkout/ -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"address\": \"$ADDRESS\"}" | jq -r .id)

# 4. Pay (redirect the user to startpay_url)
curl -s -X POST $BASE/api/payments/$ORDER/start/ -H "$AUTH"
```
