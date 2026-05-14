# Comprehensive Repository Analysis

Last updated: 2026-05-14
Analysis scope: Full repository audit including all Django apps, models, views, URLs, permissions, security, and dependencies.

---

## 1. Project Overview

**Healthcare Inventory Management System** is a Django 6.0.2 monolithic web application designed for managing medical inventory at the government health department (Dinas Kesehatan) level in Indonesia.

**Purpose**: Replace spreadsheet-based workflows with structured document flows, role-aware access control, and an immutable stock movement audit trail.

**Key Characteristics**:
- Server-rendered Django templates with Bootstrap 5 UI
- PostgreSQL 16 database with Redis 7 for caching/broker
- Indonesian-language product labels with English-first codebase
- Version: 1.1.0 (semantic versioning)
- State: Production-ready core modules, reports as placeholder

---

## 2. Architecture

### Tech Stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.13+ |
| Framework | Django 6.0.2 |
| Database | PostgreSQL 16 |
| Cache/Broker | Redis 7 |
| UI | Django Templates + Bootstrap 5 |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| Data Import | django-import-export 4.4.0 |
| Security | django-axes 8.3.1 |
| Task Queue | Celery 5.6.2 (configured, not actively used) |
| WSGI Server | gunicorn 25.1.0 |

### Repository Structure

```
Healthcare-Inventory-Management-System/
|- README.md
|- AGENTS.md
|- SYSTEM_MODEL.md
|- CHANGELOG.md
|- SECURITY.md
|- docker-compose.yml
|- .env.example
|- VERSION
|- LICENSE
|- docs/
|  |- erd.md
|  |- infrastructure_plan.md
|  |- README.md
|  `- system_design_renew.md
|- backend/
|  |- manage.py
|  |- requirements.txt
|  |- config/
|  |  |- settings.py
|  |  |- urls.py
|  |  `- wsgi.py
|  |- apps/
|  |  |- core/
|  |  |- users/
|  |  |- items/
|  |  |- stock/
|  |  |- receiving/
|  |  |- distribution/
|  |  |- recall/
|  |  |- expired/
|  |  |- stock_opname/
|  |  `- reports/
|  |- templates/
|  |- static/
|  |- seed/
|  `- tests/
|- scripts/
`- venv/
```

---

## 3. Django Apps

### 3.1 `core` - Shared Abstractions and Dashboard

**Responsibilities**:
- `TimeStampedModel` abstract base class (`created_at`, `updated_at`)
- Dashboard view with stats (total items, stock entries, low stock alerts, expiring soon, transaction trends)
- `@perm_required` decorator (hybrid Django permission + module-scope fallback)
- `@role_required` decorator (deprecated)
- `@module_scope_required` decorator
- `AdminPanelAccessMiddleware` - restricts `/admin/` to users with `admin_panel` MANAGE scope
- Semantic version parsing/bumping from root `VERSION` file
- Context processor injecting `app_version` into all templates
- `ImportGuideMixin` for CSV import column reference guides
- Template tags: `id_decimal`, `idr` filters for Indonesian number formatting
- Management command: `app_version` (show/bump version)

**Key Files**:
- `backend/apps/core/models.py`
- `backend/apps/core/views.py`
- `backend/apps/core/decorators.py`
- `backend/apps/core/middleware.py`
- `backend/apps/core/versioning.py`
- `backend/apps/core/context_processors.py`
- `backend/apps/core/admin_mixins.py`
- `backend/apps/core/templatetags/number_format.py`

### 3.2 `users` - Custom User and Module Access

**Responsibilities**:
- Custom `User` model extending `AbstractUser`
- `ModuleAccess` model for per-user per-module scope
- User CRUD views with module-scope inline form fields
- `post_save` signal syncing Django Groups and `is_staff` based on role
- Management commands: `sync_module_access`, `fix_group_permissions`

**Models**:
- `User`: adds `role` (ADMIN, KEPALA, ADMIN_UMUM, GUDANG, AUDITOR) and `full_name`
- `ModuleAccess`: per-user per-module scope (NONE=0, VIEW=1, OPERATE=2, APPROVE=4, MANAGE=4)

**Key Files**:
- `backend/apps/users/models.py`
- `backend/apps/users/access.py`
- `backend/apps/users/views.py`
- `backend/apps/users/forms.py`
- `backend/apps/users/signals.py`
- `backend/apps/users/admin.py`

### 3.3 `items` - Master Data and Item Catalog

**Responsibilities**:
- 7 lookup models + Item registry
- Item CRUD with search/filter
- AJAX quick-create endpoints for Unit/Category/Program/Facility
- Full django-import-export resources with `ImportGuideMixin`

**Models**:
- `Unit`, `Category`, `FundingSource`, `Program`, `Location`, `Supplier`, `Facility`
- `Item`: auto-generates `kode_barang` (ITM-YYYY-NNNNN), FKs to Unit/Category/Program, `minimum_stock` threshold

**Key Files**:
- `backend/apps/items/models.py`
- `backend/apps/items/views.py`
- `backend/apps/items/admin.py`
- `backend/apps/items/forms.py`

### 3.4 `stock` - Stock Entries and Immutable Transactions

**Responsibilities**:
- Batch-level inventory tracking
- Immutable transaction audit trail
- Stock transfer workflow
- Stock card (running balance with date/location filters)
- AJAX item/stock search APIs

**Models**:
- `Stock`: batch-level inventory with `quantity`, `reserved`, `expiry_date`, `sumber_dana`. Unique constraint on (item, location, batch_lot, sumber_dana). FEFO indexes.
- `Transaction`: **IMMUTABLE** audit trail. Types: IN, OUT, ADJUST, RETURN. Reference types: RECEIVING, DISTRIBUTION, ADJUSTMENT, INITIAL_IMPORT, RECALL, EXPIRED, TRANSFER.
- `StockTransfer`: DRAFT->COMPLETED workflow, auto-generates TRF-YYYY-NNNNN
- `StockTransferItem`: line items linking to specific stock batches

**Key Files**:
- `backend/apps/stock/models.py`
- `backend/apps/stock/views.py`
- `backend/apps/stock/admin.py`

### 3.5 `receiving` - Inbound Receiving (Regular and Planned)

**Responsibilities**:
- Regular receiving workflow
- Planned receiving workflow
- Custom CSV import endpoint in admin
- AJAX quick-create for Supplier/FundingSource/ReceivingType

**Models**:
- `ReceivingTypeOption`: custom receiving types
- `Receiving`: PROCUREMENT/GRANT types. Status: DRAFT->SUBMITTED->APPROVED->PARTIAL/RECEIVED->CLOSED, plus VERIFIED. Auto-generates RCV-YYYY-NNNNN.
- `ReceivingItem`: line items with batch, expiry, location, received_by tracking
- `ReceivingDocument`: file attachments
- `ReceivingOrderItem`: planned quantities for planned receiving workflow

**Key Files**:
- `backend/apps/receiving/models.py`
- `backend/apps/receiving/views.py`
- `backend/apps/receiving/admin.py`
- `backend/apps/receiving/forms.py`

### 3.6 `distribution` - Outbound Distribution

**Responsibilities**:
- Full workflow: create->submit->verify->prepare->distribute
- Staff assignment per document
- FEFO stock allocation
- Reject, reset-to-draft, step-back actions

**Models**:
- `Distribution`: LPLPO/ALLOCATION/SPECIAL_REQUEST types. Status: DRAFT->SUBMITTED->VERIFIED->PREPARED->DISTRIBUTED (or REJECTED). Auto-generates DIST-YYYYMM-XXXXX.
- `DistributionStaffAssignment`: staff involved per document (unique per distribution+user)
- `DistributionItem`: requested/approved quantities, stock batch assignment

**Key Files**:
- `backend/apps/distribution/models.py`
- `backend/apps/distribution/views.py`
- `backend/apps/distribution/forms.py`

### 3.7 `recall` - Supplier Return Workflow

**Responsibilities**:
- CRUD + submit, verify, complete, delete
- FEFO stock selection
- Stock deduction on verify

**Models**:
- `Recall`: Status DRAFT->SUBMITTED->VERIFIED->COMPLETED. Auto-generates REC-YYYYMM-XXXXX.
- `RecallItem`: item + specific stock batch + quantity

**Key Files**:
- `backend/apps/recall/models.py`
- `backend/apps/recall/views.py`
- `backend/apps/recall/forms.py`

### 3.8 `expired` - Expired/Disposal Workflow

**Responsibilities**:
- CRUD + submit, verify, dispose, delete
- Expired alerts monitoring page with sortable/filterable table
- FEFO stock selection
- Stock deduction on verify

**Models**:
- `Expired`: Status DRAFT->SUBMITTED->VERIFIED->DISPOSED. Auto-generates EXP-YYYYMM-XXXXX.
- `ExpiredItem`: item + specific stock batch + quantity

**Key Files**:
- `backend/apps/expired/models.py`
- `backend/apps/expired/views.py`
- `backend/apps/expired/forms.py`

### 3.9 `stock_opname` - Physical Counting Workflow

**Responsibilities**:
- CRUD + start (snapshots stock quantities)
- Input actual counts
- Complete and print discrepancy report
- MONTHLY/QUARTERLY/SEMESTER/YEARLY periods

**Models**:
- `StockOpname`: Status DRAFT->IN_PROGRESS->COMPLETED. M2M to Category and User. Auto-generates SO-YYYYMM-XXXXX.
- `StockOpnameItem`: system_quantity (snapshot) vs actual_quantity, with discrepancy tracking

**Key Files**:
- `backend/apps/stock_opname/models.py`
- `backend/apps/stock_opname/views.py`
- `backend/apps/stock_opname/forms.py`

### 3.10 `reports` - Placeholder

**Responsibilities**:
- Single `reports_index` view rendering a template
- No active business model entities

**Key Files**:
- `backend/apps/reports/models.py`
- `backend/apps/reports/views.py`
- `backend/apps/reports/urls.py`

---

## 4. Data Model Relationships

### Core Inventory Chain

```
Item -> Stock (batch-level) -> Transaction (immutable log)
  |        |
  |        +-> StockTransfer -> StockTransferItem
  |        +-> DistributionItem -> Distribution
  |        +-> RecallItem -> Recall
  |        +-> ExpiredItem -> Expired
  |        +-> StockOpnameItem -> StockOpname
  +-> ReceivingItem -> Receiving
  +-> ReceivingOrderItem -> Receiving
```

### Foreign Key Relationships

| Model | FKs |
| --- | --- |
| `Stock` | `Item`, `Location`, `FundingSource`, `Receiving` (nullable) |
| `Transaction` | `Item`, `Location`, `FundingSource` (nullable), `User` |
| `Receiving` | `Supplier` (nullable), `FundingSource`, `User` (created_by, verified_by, approved_by, closed_by) |
| `Distribution` | `Facility`, `User` (created_by, verified_by, approved_by) |
| `Recall` | `Supplier`, `User` (created_by, verified_by, completed_by) |
| `Expired` | `User` (created_by, verified_by, disposed_by) |

### Database Constraints

- `Stock`: Check constraints for `quantity >= 0` and `reserved >= 0`; Unique on (item, location, batch_lot, sumber_dana)
- `StockOpnameItem`: Unique on (stock_opname, stock)
- `ModuleAccess`: Unique on (user, module)
- `DistributionStaffAssignment`: Unique on (distribution, user)

---

## 5. Permission and Authorization System

### Hybrid Two-Layer Model

**Layer 1: Django Permissions (Groups)**
- Standard Django `has_perm()` checks
- Groups: ADMIN, KEPALA INSTALASI, ADMIN UMUM, GUDANG, AUDITOR
- Permissions assigned via Django Admin

**Layer 2: Module Scope Fallback (ModuleAccess)**
- `@perm_required` decorator checks Django permissions first, then falls back to `has_module_permission()`
- Module scopes: NONE(0), VIEW(1), OPERATE(2), APPROVE(3), MANAGE(4)
- 10 modules: users, items, stock, receiving, distribution, recall, expired, stock_opname, reports, admin_panel

### Role Default Scopes

| Module | ADMIN | KEPALA | ADMIN_UMUM | GUDANG | AUDITOR |
| --- | --- | --- | --- | --- | --- |
| users | MANAGE | VIEW | NONE | NONE | NONE |
| items | MANAGE | VIEW | VIEW | VIEW | VIEW |
| stock | MANAGE | VIEW | VIEW | OPERATE | VIEW |
| receiving | MANAGE | APPROVE | OPERATE | OPERATE | VIEW |
| distribution | MANAGE | APPROVE | OPERATE | OPERATE | VIEW |
| recall | MANAGE | APPROVE | NONE | OPERATE | VIEW |
| expired | MANAGE | APPROVE | NONE | OPERATE | VIEW |
| stock_opname | MANAGE | APPROVE | NONE | OPERATE | VIEW |
| reports | MANAGE | VIEW | VIEW | VIEW | VIEW |
| admin_panel | MANAGE | NONE | NONE | NONE | NONE |

### Special Rules

- ADMIN role can only be created via CLI (`createsuperuser`)
- For `users.*` permissions, non-view actions require MANAGE scope
- Superusers bypass all checks
- `AdminPanelAccessMiddleware` enforces admin_panel MANAGE for `/admin/`
- `post_save` signal on User automatically syncs Django Group membership and `is_staff` flag

---

## 6. URL Routing Structure

### Root Routes (from `backend/config/urls.py`)

| Pattern | View |
| --- | --- |
| `/` | dashboard |
| `/admin/` | Django admin |
| `/login/` | login |
| `/logout/` | logout |
| `/password/change/` | password change |
| `/password/change/done/` | password change done |

### Module Routes

#### Users

| Pattern | View |
| --- | --- |
| `/users/` | user_list |
| `/users/create/` | user_create |
| `/users/<pk>/edit/` | user_update |
| `/users/<pk>/delete/` | user_delete |
| `/users/<pk>/toggle-active/` | user_toggle_active |

#### Items

| Pattern | View |
| --- | --- |
| `/items/` | item_list |
| `/items/create/` | item_create |
| `/items/units/create/` | unit_create |
| `/items/categories/create/` | category_create |
| `/items/programs/create/` | program_create |
| `/items/<pk>/edit/` | item_update |
| `/items/<pk>/delete/` | item_delete |
| `/items/api/quick-create-*/` | AJAX endpoints |

#### Stock

| Pattern | View |
| --- | --- |
| `/stock/` | stock_list |
| `/stock/transactions/` | transaction_list |
| `/stock/transfers/` | transfer_list |
| `/stock/transfers/create/` | transfer_create |
| `/stock/transfers/<id>/` | transfer_detail |
| `/stock/transfers/<id>/complete/` | transfer_complete |
| `/stock/stock-card/` | stock_card_select |
| `/stock/stock-card/<item_id>/` | stock_card_detail |
| `/stock/api/item-search/` | AJAX |
| `/stock/api/location-stock-search/` | AJAX |

#### Receiving

| Pattern | View |
| --- | --- |
| `/receiving/` | receiving_list |
| `/receiving/plans/` | receiving_plan_list |
| `/receiving/plans/create/` | receiving_plan_create |
| `/receiving/plans/<pk>/` | receiving_plan_detail |
| `/receiving/plans/<pk>/submit/` | receiving_plan_submit |
| `/receiving/plans/<pk>/approve/` | receiving_plan_approve |
| `/receiving/plans/<pk>/receive/` | receiving_plan_receive |
| `/receiving/plans/<pk>/close/` | receiving_plan_close |
| `/receiving/plans/<pk>/close-items/` | receiving_plan_close_items |
| `/receiving/create/` | receiving_create |
| `/receiving/<pk>/` | receiving_detail |
| `/receiving/api/quick-create-*/` | AJAX endpoints |

#### Distribution

| Pattern | View |
| --- | --- |
| `/distribution/` | distribution_list |
| `/distribution/create/` | distribution_create |
| `/distribution/<pk>/` | distribution_detail |
| `/distribution/<pk>/edit/` | distribution_edit |
| `/distribution/<pk>/delete/` | distribution_delete |
| `/distribution/<pk>/reset-to-draft/` | distribution_reset_to_draft |
| `/distribution/<pk>/step-back/` | distribution_step_back |
| `/distribution/<pk>/submit/` | distribution_submit |
| `/distribution/<pk>/verify/` | distribution_verify |
| `/distribution/<pk>/prepare/` | distribution_prepare |
| `/distribution/<pk>/distribute/` | distribution_distribute |
| `/distribution/<pk>/reject/` | distribution_reject |

#### Recall

| Pattern | View |
| --- | --- |
| `/recall/` | recall_list |
| `/recall/create/` | recall_create |
| `/recall/<pk>/` | recall_detail |
| `/recall/<pk>/edit/` | recall_edit |
| `/recall/<pk>/submit/` | recall_submit |
| `/recall/<pk>/verify/` | recall_verify |
| `/recall/<pk>/complete/` | recall_complete |
| `/recall/<pk>/delete/` | recall_delete |

#### Expired

| Pattern | View |
| --- | --- |
| `/expired/` | expired_list |
| `/expired/alerts/` | expired_alerts |
| `/expired/create/` | expired_create |
| `/expired/<pk>/` | expired_detail |
| `/expired/<pk>/edit/` | expired_edit |
| `/expired/<pk>/submit/` | expired_submit |
| `/expired/<pk>/verify/` | expired_verify |
| `/expired/<pk>/dispose/` | expired_dispose |
| `/expired/<pk>/delete/` | expired_delete |

#### Stock Opname

| Pattern | View |
| --- | --- |
| `/stock-opname/` | opname_list |
| `/stock-opname/create/` | opname_create |
| `/stock-opname/<pk>/` | opname_detail |
| `/stock-opname/<pk>/edit/` | opname_edit |
| `/stock-opname/<pk>/start/` | opname_start |
| `/stock-opname/<pk>/input/` | opname_input |
| `/stock-opname/<pk>/complete/` | opname_complete |
| `/stock-opname/<pk>/print/` | opname_print |
| `/stock-opname/<pk>/delete/` | opname_delete |

#### Reports

| Pattern | View |
| --- | --- |
| `/reports/` | reports_index |

---

## 7. Workflow States

### Receiving (Planned)

```
DRAFT -> SUBMITTED -> APPROVED -> PARTIAL/RECEIVED -> CLOSED
```

### Receiving (Regular/Imported)

```
VERIFIED (commonly persisted after posting)
```

### Distribution

```
DRAFT -> SUBMITTED -> VERIFIED -> PREPARED -> DISTRIBUTED
                                    |
                                    v
                               REJECTED
```

- Non-distributed docs can be reset to DRAFT
- Submit requires assigned Petugas

### Recall

```
DRAFT -> SUBMITTED -> VERIFIED -> COMPLETED
```

### Expired

```
DRAFT -> SUBMITTED -> VERIFIED -> DISPOSED
```

### Stock Transfer

```
DRAFT -> COMPLETED
```

### Stock Opname

```
DRAFT -> IN_PROGRESS -> COMPLETED
```

---

## 8. Security Configuration

### Authentication

- Custom user model: `AUTH_USER_MODEL = "users.User"`
- Auth backends: `AxesStandaloneBackend` first, then `ModelBackend`
- Password validation: Minimum 10 characters, common password check, attribute similarity check

### Brute-Force Protection (django-axes)

- `AXES_FAILURE_LIMIT = 5` (lock after 5 failed attempts)
- `AXES_COOLOFF_TIME = 0.5` (30-minute cooldown)
- `AXES_RESET_ON_SUCCESS = True`
- Lockout parameters: username + IP address combination

### Session Security

- `SESSION_COOKIE_AGE = 3600` (1 hour)
- `SESSION_SAVE_EVERY_REQUEST = True` (sliding expiry)
- `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`
- `SESSION_COOKIE_HTTPONLY = True`
- `SESSION_COOKIE_SAMESITE = "Lax"`

### CSRF Security

- `CSRF_COOKIE_HTTPONLY = True`
- `CSRF_COOKIE_SAMESITE = "Lax"`
- CSRF token injected via meta tag for JS access

### Production Hardening (when DEBUG=False)

- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `X_FRAME_OPTIONS = "DENY"`
- `SECURE_SSL_REDIRECT` (env-controlled)
- HSTS: 1 year, include subdomains, preload
- `SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"`
- `SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"`
- `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`

### Admin Panel Access

- Custom middleware restricts `/admin/` to users with `admin_panel` MANAGE scope only

---

## 9. Stock Mutation Checkpoints

| Workflow | Action | Stock Effect | Transaction |
| --- | --- | --- | --- |
| Receiving | verify/receive | Creates/updates Stock | `Transaction(IN)` |
| Receiving CSV import | import | Creates/updates Stock | `Transaction(IN)` |
| Distribution | prepare | No stock mutation | None |
| Distribution | distribute | Decreases Stock.quantity | `Transaction(OUT)` |
| Recall | verify | Decreases Stock | `Transaction(OUT, RECALL)` |
| Expired | verify | Decreases Stock | `Transaction(OUT, EXPIRED)` |
| Stock Transfer | complete | Adjusts source/destination | Paired `OUT` and `IN` |
| Stock Opname | complete | May post adjustments | `Transaction(ADJUST)` (if implemented) |

**Note**: Distribution workflow does **not** use `Stock.reserved` field. The prepare phase only changes document status.

---

## 10. CSV Import Contract

### Generic Admin Import

- Uses django-import-export resources in `backend/apps/items/admin.py` and `backend/apps/stock/admin.py`
- `skip_unchanged = True` enabled in multiple resources
- Standard flow: dry-run then confirm import in admin UI

### Dedicated Receiving CSV Import

- Endpoint: `/admin/receiving/receiving/import-csv/`
- Required columns: `document_number`, `receiving_date`, `item_code`, `sumber_dana_code`, `location_code`, `quantity`
- Supported date formats: `DD/MM/YYYY`, `YYYY-MM-DD`, `DD-MM-YYYY`, `DD/MM/YY`
- Decimal parser supports comma decimal separator
- Runs in `@transaction.atomic`

---

## 11. Key Patterns and Conventions

### Document Number Generation

All workflow documents auto-generate document numbers using pattern: `PREFIX-YYYY-NNNNN` or `PREFIX-YYYYMM-NNNNN`

| Document | Pattern |
| --- | --- |
| Item | `ITM-YYYY-NNNNN` |
| Receiving | `RCV-YYYY-NNNNN` |
| Distribution | `DIST-YYYYMM-XXXXX` |
| Recall | `REC-YYYYMM-XXXXX` |
| Expired | `EXP-YYYYMM-XXXXX` |
| Stock Transfer | `TRF-YYYY-NNNNN` |
| Stock Opname | `SO-YYYYMM-XXXXX` |

### Architectural Patterns

- **Document-based workflows**: All business processes follow document header + line items pattern with status transitions
- **Formset-heavy forms**: Inline formsets for managing related line items
- **AJAX quick-create**: Modal-based creation of lookup entities without leaving parent form
- **Stock card running balance**: Chronological transaction display with opening/closing balance calculation
- **Import guide mixin**: Reusable admin mixin displaying CSV column documentation on import pages
- **Immutable transactions**: `Transaction` model is append-only; admin explicitly disables change/delete

### Code Conventions

- Schema truth: `backend/apps/*/models.py`
- Route truth: `backend/config/urls.py` + `backend/apps/*/urls.py`
- Auth/permission truth: `backend/apps/core/decorators.py`, `backend/apps/users/access.py`
- Security/config truth: `backend/config/settings.py`
- If documentation conflicts with code, code is authoritative until docs are corrected

---

## 12. Known Issues and Areas for Improvement

### Critical

1. **Race condition in document number generation**: The `save()` method generates document numbers by querying the last one - this can produce duplicates under concurrent saves. Should use `select_for_update()` or database sequences.

### Moderate

2. **`Stock.reserved` field unused**: The field exists but distribution workflow does not use it for allocation. The prepare phase only changes status, not stock.
3. **Stock opname completion does not auto-adjust**: Completing a stock opname marks it as COMPLETED but does not automatically post adjustment transactions for discrepancies.
4. **AJAX endpoints lack CSRF validation on GET**: The `@require_POST` decorator is used correctly, but some quick-create endpoints could benefit from additional validation.

### Minor

5. **Reports app is placeholder**: No actual functionality beyond an index page.
6. **No API layer**: System is template-only; REST API is noted as "planned" but not implemented.
7. **Celery configured but not actively used**: Celery and amqp are in requirements but no tasks are defined.
8. **Template structure**: All templates extend `base.html` which loads Bootstrap from CDN - no offline fallback.
9. **Test coverage**: Only one test file exists (`test_item_import.py`), covering a single import scenario.
10. **No pagination on expired alerts sort URLs**: The sort URL builder preserves all params but the paginator may lose context.

---

## 13. Module Status Summary

| Module | Status | Notes |
| --- | --- | --- |
| Core inventory management | Complete | Functional |
| Receiving workflows | Complete | Regular + planned + CSV import |
| Distribution workflow | Complete | Full state machine |
| Recall workflow | Complete | |
| Expired/disposal workflow | Complete | + alerts monitoring |
| Stock transfer | Complete | |
| Stock opname | Complete | No auto-adjustment on completion |
| User management | Complete | With module-scope UI |
| Reports | Placeholder | Empty |
| REST API | Not implemented | Planned |
| Celery tasks | Not implemented | Configured only |
| Test coverage | Minimal | 1 test file |

---

## 14. Dependencies

| Package | Version | Purpose |
| --- | --- | --- |
| Django | 6.0.2 | Web framework |
| psycopg2-binary | 2.9.11 | PostgreSQL adapter |
| django-crispy-forms | 2.5 | Form rendering |
| crispy-bootstrap5 | 2025.6 | Bootstrap 5 template pack |
| django-filter | 25.1 | Query filtering |
| django-import-export | 4.4.0 | CSV import/export |
| django-axes | 8.3.1 | Brute-force protection |
| redis | 7.2.0 | Cache/broker client |
| celery | 5.6.2 | Task queue (planned) |
| gunicorn | 25.1.0 | WSGI server |
| python-dotenv | 1.2.1 | Environment variable loading |

---

## 15. Development Commands

```bash
docker compose up -d
cd backend
python manage.py migrate
python manage.py runserver
python manage.py app_version
```

### Version Management

- Show current version: `python manage.py app_version`
- Bump patch: `python manage.py app_version --patch`
- Bump minor: `python manage.py app_version --minor`
- Bump major: `python manage.py app_version --major`
- Set explicit: `python manage.py app_version --set 2.0.0`

### Testing

```powershell
.\scripts\run-django-test.ps1 -Target apps.items
```

---

## 16. Seed and Import

- Seed templates: `backend/seed/`
- Import sequence: `units -> categories -> funding_sources -> programs -> locations -> suppliers -> facilities -> items -> receiving`
- For initial stock, prefer `receiving.csv` via custom Receiving Admin import (`/admin/receiving/receiving/import-csv/`) so stock and `Transaction(IN)` records are created together.

Details: `backend/seed/README.md` and `docs/README.md`.

---

## 17. Documentation Index

| Document | Purpose |
| --- | --- |
| `README.md` | Project overview and getting started |
| `AGENTS.md` | Coding-agent orientation and conventions |
| `SYSTEM_MODEL.md` | Canonical schema and workflow model map |
| `CHANGELOG.md` | Release notes and version history |
| `SECURITY.md` | Security policy |
| `docs/erd.md` | ERD reference |
| `docs/infrastructure_plan.md` | Infrastructure and deployment plan |
| `docs/system_design_renew.md` | Functional and architecture design narrative |
| `docs/README.md` | Import workflow and migration notes |
| `backend/seed/README.md` | CSV seed column specification |
| `docs/ANALYSIS.md` | This file - comprehensive repository analysis |

---

## 18. Documentation Governance

When code changes affect schema, routes, permissions, settings, or scripts, update all impacted docs in the same PR:

1. `README.md`
2. `AGENTS.md`
3. `SYSTEM_MODEL.md`
4. Relevant files in `docs/`
5. `backend/seed/README.md` (if CSV schema/semantics changed)

### Quality Checklist

- Routes documented in markdown exist in URLconfs
- All model/table names in docs match current models
- Env vars in docs exist in `.env.example` or settings usage
- Security behavior in docs mirrors `backend/config/settings.py`
- CSV column docs match actual import resources/forms/admin parser logic
