# 🧠 FERRETEROS — SKILL MAESTRO DEL PROYECTO
> Actúa como **Software Architect Senior** especializado en SaaS multi-tenant escalable con Python/Flask.
> Este documento es la fuente de verdad del proyecto. Nunca generes código que rompa estas reglas.

---

# 🎯 VISIÓN DEL PRODUCTO

**FERRETEROS** no es solo un POS. Es un **ecosistema digital completo para el sector ferretero**:

| Módulo | Descripción |
|---|---|
| POS profesional | Venta rápida tipo retail con control de stock en tiempo real |
| Inventario | Gestión de productos, stock, alertas automáticas |
| Ecommerce | Tienda virtual por ferretería |
| Marketplace B2B | Abastecimiento mayorista entre ferreterías |
| Catálogo universal | Base de datos compartida de productos del sector |
| SaaS multi-tenant | Una plataforma, miles de ferreterías aisladas |
| API REST | Base para app móvil y terceros |
| IA & Analytics | Predicción de demanda, reordenamientos, reportes |

La arquitectura se diseña **desde Fase 1** para soportar todas las fases sin rehacer estructura.

---

# 📐 ARQUITECTURA MULTI-TENANT

## Modelo de aislamiento
- **Una sola base de datos** con aislamiento por `tenant_id`
- Cada ferretería es un **Tenant**
- Una ferretería puede tener **múltiples sucursales** (Branch)

## Regla de oro del multi-tenant
Todas las tablas de negocio deben incluir obligatoriamente:
```python
tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
```

## Jerarquía de entidades
```
Tenant (Ferretería)
  └── Branch (Sucursal)
        └── User (Usuario con rol)
        └── Stock (Inventario por sucursal)
        └── Sale (Ventas por sucursal)
```

## Middleware de tenant
- Cada request autenticado debe inyectar `current_tenant` en el contexto
- Nunca hacer queries sin filtrar por `tenant_id`
- Usar `TenantMixin` como clase base para todos los modelos de negocio

---

# ⚙️ STACK TECNOLÓGICO OBLIGATORIO

## Backend
| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Framework | Flask (Application Factory Pattern) |
| ORM | SQLAlchemy + Flask-SQLAlchemy |
| Migraciones | Flask-Migrate (Alembic) |
| Autenticación | Flask-Login + JWT (para API) |
| Validación | Marshmallow o WTForms |
| Base de datos | PostgreSQL (producción) / SQLite (dev local) |
| Servidor | Gunicorn |
| Variables de entorno | python-dotenv |
| Logs | Python logging nativo + archivo de log |

## Frontend
| Componente | Tecnología |
|---|---|
| Templates | Jinja2 |
| Estilos | Tailwind CSS (CDN en dev, build en prod) |
| Interactividad | Alpine.js o Vanilla JS + AJAX |
| Iconos | Heroicons o Lucide |
| Diseño | SaaS profesional estilo Stripe/Linear/Shopify |

## Deploy
| Componente | Tecnología |
|---|---|
| Plataforma | Render |
| Proceso web | Gunicorn + wsgi.py |
| Base de datos | PostgreSQL en Render |
| Config | Variables de entorno (.env) |
| CI/CD | GitHub → Render auto-deploy |

## Fases futuras (NO implementar aún)
- **Fase 4 App móvil:** Flutter (preferido) consumiendo API REST v1

---

# 📦 ESTRUCTURA DE CARPETAS OBLIGATORIA

```
ferreteros/
│
├── frontend/
│   │
│   ├── src/
│   │   │
│   │   ├── assets/                      # Recursos estáticos globales
│   │   │   ├── fonts/
│   │   │   ├── icons/                   # SVGs / Heroicons descargados
│   │   │   └── images/
│   │   │
│   │   ├── styles/
│   │   │   ├── base.css                 # Reset + variables CSS globales
│   │   │   ├── tailwind.css             # Entrada principal de Tailwind
│   │   │   └── components/              # Clases @apply reutilizables
│   │   │       ├── buttons.css
│   │   │       ├── forms.css
│   │   │       ├── badges.css
│   │   │       └── tables.css
│   │   │
│   │   ├── js/
│   │   │   ├── core/
│   │   │   │   ├── api.js               # Cliente fetch centralizado (base URL, headers, JWT)
│   │   │   │   ├── auth.js              # Manejo de sesión / token
│   │   │   │   └── utils.js             # Helpers globales (formateo, fechas, moneda)
│   │   │   │
│   │   │   ├── modules/                 # Un archivo JS por módulo
│   │   │   │   ├── dashboard.js         # Métricas, gráficos KPI
│   │   │   │   ├── inventory.js         # Búsqueda, filtros, alertas de stock
│   │   │   │   ├── pos.js               # Lógica de venta rápida (carrito, cálculos)
│   │   │   │   ├── sales.js             # Historial, filtros de fecha
│   │   │   │   └── users.js             # ABM usuarios
│   │   │   │
│   │   │   └── components/              # Componentes UI reutilizables (Alpine.js o Vanilla)
│   │   │       ├── modal.js             # Abrir/cerrar modales genérico
│   │   │       ├── toast.js             # Notificaciones tipo toast
│   │   │       ├── datatable.js         # Tabla con paginación / búsqueda
│   │   │       └── confirm.js           # Modal de confirmación de borrado
│   │   │
│   │   └── templates/                   # Jinja2 (servidos por Flask)
│   │       ├── base.html                # Layout raíz (head, scripts globales)
│   │       │
│   │       ├── layouts/
│   │       │   ├── app.html             # Layout autenticado (sidebar + topbar)
│   │       │   └── auth.html            # Layout centrado (login / register)
│   │       │
│   │       ├── partials/
│   │       │   ├── sidebar.html
│   │       │   ├── topbar.html
│   │       │   └── flash_messages.html
│   │       │
│   │       ├── modals/
│   │       │   ├── confirm_delete.html
│   │       │   └── product_form.html
│   │       │
│   │       ├── auth/
│   │       │   ├── login.html
│   │       │   └── register.html
│   │       │
│   │       ├── dashboard/
│   │       │   └── index.html
│   │       │
│   │       ├── inventory/
│   │       │   ├── index.html           # Lista de productos
│   │       │   ├── create.html
│   │       │   └── edit.html
│   │       │
│   │       ├── pos/
│   │       │   └── index.html           # Pantalla de venta rápida
│   │       │
│   │       ├── sales/
│   │       │   ├── index.html           # Historial de ventas
│   │       │   └── detail.html          # Detalle de una venta
│   │       │
│   │       └── users/
│   │           ├── index.html
│   │           ├── create.html
│   │           └── edit.html
│   │
│   ├── tailwind.config.js               # Config Tailwind (colores, fuentes, breakpoints)
│   ├── postcss.config.js
│   └── package.json
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py                  # Application Factory: create_app()
│   │   │
│   │   ├── core/
│   │   │   ├── config.py                # Config por entorno (Dev/Prod/Test)
│   │   │   ├── extensions.py            # db, login_manager, migrate, etc.
│   │   │   ├── middleware.py            # TenantMiddleware, RequestLogger
│   │   │   └── logging_config.py        # Configuración de logs
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py              # Exporta todos los modelos
│   │   │   ├── mixins.py                # TenantMixin, TimestampMixin
│   │   │   ├── tenant.py                # Tenant (la ferretería)
│   │   │   ├── branch.py                # Branch (sucursal)
│   │   │   ├── user.py                  # User
│   │   │   ├── role.py                  # Role + Permission
│   │   │   ├── product.py               # Product (catálogo)
│   │   │   ├── stock.py                 # Stock por sucursal
│   │   │   ├── sale.py                  # Sale (cabecera)
│   │   │   ├── sale_item.py             # SaleItem (detalle)
│   │   │   └── ai_log.py                # AILog (registro de IA)
│   │   │
│   │   ├── services/                    # Lógica de negocio PURA (sin Flask)
│   │   │   ├── __init__.py
│   │   │   ├── inventory_service.py     # CRUD inventario, alertas stock
│   │   │   ├── sale_service.py          # Procesar ventas, validaciones
│   │   │   ├── report_service.py        # Generación de reportes
│   │   │   ├── tenant_service.py        # Gestión de tenants
│   │   │   └── ai_service.py            # Interfaz con módulo IA
│   │   │
│   │   ├── ai/                          # Módulo IA (producción)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # Clase base AIAnalyzer
│   │   │   ├── inventory_ai.py          # Predicción de stock
│   │   │   ├── sales_ai.py              # Análisis de ventas
│   │   │   └── prompts.py               # Prompts para LLM (si aplica)
│   │   │
│   │   ├── blueprints/
│   │   │   ├── auth/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py            # /login, /logout, /register
│   │   │   │   └── forms.py
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py            # / (home post-login)
│   │   │   │
│   │   │   ├── inventory/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py            # /inventory/*
│   │   │   │   └── forms.py
│   │   │   │
│   │   │   ├── pos/
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py            # /pos/*
│   │   │   │
│   │   │   ├── sales/
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py            # /sales/* (historial)
│   │   │   │
│   │   │   ├── users/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py            # /users/*
│   │   │   │   └── forms.py
│   │   │   │
│   │   │   └── api/
│   │   │       └── v1/
│   │   │           ├── __init__.py
│   │   │           ├── auth.py          # POST /api/v1/auth/login
│   │   │           ├── users.py
│   │   │           ├── products.py
│   │   │           ├── inventory.py
│   │   │           ├── sales.py
│   │   │           ├── reports.py
│   │   │           ├── ai.py
│   │   │           ├── schemas.py       # Marshmallow schemas
│   │   │           └── utils.py         # Helpers, decoradores JWT
│   │   │
│   │   │              # templates/ y static/ se resuelven desde frontend/
│   │   │              # Flask se configura en create_app():
│   │   │              #   template_folder="../../frontend/src/templates"
│   │   │              #   static_folder="../../frontend/dist"
│   │   │
│   │   └── static/ → ../../frontend/dist/   # build output (Tailwind + JS minificado)
│   │                                         # En dev: CDN Tailwind + JS sin compilar
│   │
│   ├── ai/                              # Entrenamiento offline (no en producción)
│   │   ├── models/
│   │   ├── training/
│   │   ├── notebooks/
│   │   └── data/
│   │
│   ├── migrations/
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_inventory.py
│   │   ├── test_pos.py
│   │   ├── test_api.py
│   │   ├── test_tenant.py
│   │   └── test_ai.py
│   │
│   ├── .env
│   ├── .env.example
│   ├── requirements.txt
│   ├── run.py                           # Entrypoint desarrollo
│   └── wsgi.py                          # Entrypoint producción (Gunicorn)
│
└── docs/
    ├── architecture.md
    ├── api.md
    └── deployment.md
```

---

# 🗄️ MODELOS DE BASE DE DATOS

## Mixins base (models/mixins.py)
```python
class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TenantMixin:
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
```

## Modelos principales

### ✅ Heredan TenantMixin + TimestampMixin
Todos los modelos de negocio **deben** heredar `TenantMixin` por defecto.
Si un modelo nuevo NO lo hereda, debe justificarse con un comentario en el código.

```python
class User(TenantMixin, TimestampMixin, db.Model):
    # id, branch_id, email, password_hash, role_id, is_active
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    ...

class Role(TenantMixin, TimestampMixin, db.Model):
    # id, name, permissions (JSON)
    ...

class Stock(TenantMixin, TimestampMixin, db.Model):
    # Inventario POR ferretería POR sucursal — aquí vive el precio también
    # Un producto global puede tener precio diferente en cada ferretería
    branch_id  = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False, default=0)
    min_stock  = db.Column(db.Integer, default=0)
    max_stock  = db.Column(db.Integer, nullable=True)
    price      = db.Column(db.Numeric(10, 2), nullable=False)   # precio local del tenant
    cost       = db.Column(db.Numeric(10, 2), nullable=True)    # costo local del tenant
    ...

class Sale(TenantMixin, TimestampMixin, db.Model):
    # id, branch_id, user_id, total, discount, payment_method, status
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    ...

class AILog(TenantMixin, TimestampMixin, db.Model):
    # id, type, input_data (JSON), output_data (JSON)
    ...
```

### 🌐 Modelos GLOBALES — sin TenantMixin (catálogo compartido)
Estos modelos son propiedad de la **plataforma**, no de un tenant.
Permiten el Catálogo Universal y el Marketplace B2B sin duplicación de datos.

```python
class Product(TimestampMixin, db.Model):
    # ❌ SIN tenant_id — es un catálogo global compartido por TODAS las ferreterías
    # Duplicar Product por tenant rompería el Marketplace B2B y el catálogo universal.
    # El precio y stock viven en Stock (tenant), no aquí.
    id          = db.Column(db.Integer, primary_key=True)
    sku         = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name        = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category    = db.Column(db.String(100), nullable=True)
    brand       = db.Column(db.String(100), nullable=True)
    image_url   = db.Column(db.String(500), nullable=True)
    is_active   = db.Column(db.Boolean, default=True)
    # precio y costo NO van aquí — cada tenant define el suyo en Stock
    ...
```

### ⚠️ Excluidos de TenantMixin por ser entidades raíz
```python
class Tenant(TimestampMixin, db.Model):
    # ES el tenant — no tiene tenant_id, es la raíz del sistema
    # id, name, slug, plan, is_active
    ...

class Branch(TimestampMixin, db.Model):
    # Tiene FK directa a tenant, no usa el mixin para evitar columna duplicada
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    # id, name, address, is_main
    ...

class SaleItem(TimestampMixin, db.Model):
    # Aislamiento garantizado transitivamente via sale_id → Sale.tenant_id
    sale_id    = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    # quantity, unit_price, discount
    ...
```

### 📊 Resumen de responsabilidades por modelo

| Modelo | Global/Tenant | Responsabilidad |
|---|---|---|
|  | 🌐 Global | Qué existe (SKU, nombre, categoría, marca) |
|  | 🏪 Tenant | Cuánto hay, a qué precio, en qué sucursal |
|  | 🏪 Tenant | Quién compró, cuándo, cuánto |
|  | 🏪 Tenant (transitivo) | Qué productos y cantidades por venta |
|  | 🌐 Raíz | La ferretería en sí |
|  | 🏪 Sub-raíz | Sucursales del tenant |
|  | 🏪 Tenant | Empleados del tenant |
|  | 🏪 Tenant | Permisos por tenant |

---

# 🎨 SISTEMA DE DISEÑO UI

## Filosofía
Diseño SaaS profesional estilo **Stripe / Linear / Shopify**. Limpio, moderno, minimalista, altamente usable.

## Tokens de diseño (Tailwind)

| Elemento | Clases |
|---|---|
| Bordes | `rounded-2xl` (cards), `rounded-lg` (inputs/botones) |
| Sombras | `shadow-sm` (cards), `shadow-md` (modales) |
| Espaciado | `p-6` (cards), `gap-4` (grids), `space-y-4` (forms) |
| Transiciones | `transition duration-200 ease-in-out` |
| Focus | `focus:ring-2 focus:ring-indigo-500 focus:outline-none` |

## Sidebar
- Fondo oscuro: `bg-gray-900` o `bg-slate-900`
- Item activo: `bg-indigo-600 text-white rounded-lg`
- Item hover: `hover:bg-gray-800 transition duration-200`
- Íconos alineados con `flex items-center gap-3`

## Cards KPI (Dashboard)
```html
<!-- Estructura obligatoria para tarjetas métricas -->
<div class="bg-white rounded-2xl shadow-sm p-6 flex items-center gap-4 hover:shadow-md transition duration-200">
  <div class="p-3 bg-indigo-50 rounded-xl"><!-- Ícono --></div>
  <div>
    <p class="text-2xl font-bold text-gray-900">1,240</p>
    <p class="text-sm text-gray-500">Productos en stock</p>
  </div>
</div>
```

## Badges de stock
```html
<!-- Alto -->    <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">Normal</span>
<!-- Bajo -->    <span class="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-700 rounded-full">Bajo</span>
<!-- Crítico --> <span class="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">Crítico</span>
```

## Tablas
- Encabezado sticky: `sticky top-0 bg-gray-50`
- Hover en filas: `hover:bg-gray-50 transition duration-150`
- Botones de acción: icon-only con tooltip, `p-2 rounded-lg hover:bg-gray-100`

## Formularios
- Grid de 2 columnas: `grid grid-cols-1 md:grid-cols-2 gap-4`
- Input estándar: `w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500`
- Botón primario: `bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-4 py-2 rounded-lg transition duration-200`

---

# 🔒 REGLAS INQUEBRANTABLES

## Negocio
- ✅ Control de stock en tiempo real (nunca permitir venta sin stock)
- ✅ Descuentos por producto Y por total de venta
- ✅ Validaciones robustas en backend (nunca solo en frontend)
- ✅ Logs de operaciones críticas (ventas, ajustes de stock)
- ✅ Todo dato de negocio filtrado por `tenant_id`

## Arquitectura
- ✅ Lógica de negocio SOLO en `services/` — nunca en blueprints ni templates
- ✅ Blueprints son solo routing + llamada al service correcto
- ✅ Templates solo presentan datos — sin lógica compleja
- ✅ API REST versionada desde el inicio (`/api/v1/`)
- ✅ Todo modelo de negocio nuevo **debe** heredar `TenantMixin` por defecto — si no lo hace, comentar el motivo en el código
- ✅ `SaleItem` y modelos hijos de un padre con `TenantMixin` están exentos (aislamiento transitivo via FK)
- ✅ `Tenant`, `Branch` y `Product` son los únicos modelos sin `TenantMixin` — `Product` es un catálogo **global** de la plataforma
- ❌ NUNCA agregar `tenant_id` a `Product` — el precio y stock por ferretería viven en `Stock`, no en `Product`

## Código
- ❌ NO mover carpetas sin justificación
- ❌ NO mezclar lógica de negocio en templates
- ❌ NO crear deuda técnica
- ❌ NO hacer queries sin filtrar por `tenant_id` en modelos de negocio
- ❌ NO romper estructura Flask al modificar UI
- ❌ NO cambiar nombres de variables Jinja al refactorizar HTML

---

# 📋 CONVENCIONES DE CÓDIGO

## Python / Flask
```python
# Nombres de funciones en blueprints: verbo_recurso
def get_products(): ...
def create_product(): ...
def update_product(product_id): ...

# Services siempre reciben tenant_id como parámetro
def get_stock(tenant_id: int, branch_id: int) -> list[Stock]: ...

# Respuestas de API siempre con estructura estándar
{"success": True, "data": {...}, "message": "OK"}
{"success": False, "error": "Producto no encontrado", "code": 404}
```

## Commits
```
feat: agregar módulo de ventas POS
fix: corregir validación de stock negativo
refactor: mover lógica de descuentos a sale_service
style: mejorar diseño de tabla de inventario
```

---

# 📦 ENTREGA ESPERADA DE LA IA

Cuando generes código para este proyecto, siempre entrega:

1. **Ubicación exacta del archivo** (ruta completa)
2. **Código completo y funcional** (no fragmentos)
3. **Sin romper** la estructura de carpetas definida
4. **Con docstrings** en servicios y funciones complejas
5. **Explicación breve** antes del código si hay decisiones de diseño importantes
6. **Tailwind correcto** si modificas templates (no CSS inline)

---

*Versión: 1.0 — FERRETEROS Master Skill | Stack: Python + Flask + PostgreSQL + Tailwind*
