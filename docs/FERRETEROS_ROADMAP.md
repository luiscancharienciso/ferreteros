# 🗺️ FERRETEROS — ROADMAP OFICIAL DE DESARROLLO
> **Versión:** 1.0 | **Stack:** Python + Flask + PostgreSQL + Tailwind CSS
> Este documento define la secuencia oficial de desarrollo del sistema FERRETEROS.
> El objetivo es construir el sistema siguiendo arquitectura profesional SaaS, evitando deuda técnica y asegurando escalabilidad futura.
> El roadmap está dividido en **6 fases principales** con sus respectivos pasos.

---

## 🔑 PRINCIPIO RECTOR

> La arquitectura se diseña **desde la Fase 1** para soportar todas las fases sin rehacer estructura.
> Cada fase es una **capa que se apoya en la anterior** — nunca se retrocede a modificar lo ya construido.

---

## 📊 RESUMEN EJECUTIVO

| Fase | Nombre | Alcance | Estado |
|---|---|---|---|
| **1** | Cimientos | Setup, arquitectura base, modelos, CI/CD | ✅ Implementar ahora |
| **2** | Sistema Interno | Dashboard, Inventario, POS, Ventas, Usuarios | ✅ Implementar ahora |
| **3** | API REST + IA | API pública versionada, reportes, analytics, IA | 🔜 Fase siguiente |
| **4** | Ecommerce | Tienda virtual por ferretería, carrito, pedidos | 🔜 Futuro |
| **5** | SaaS Completo | Multi-tenant activado, subdominios, suscripciones | 🔜 Futuro |
| **6** | App Móvil + Marketplace | Flutter + Marketplace B2B entre ferreterías | 🔜 Futuro |

---

---

# ⚙️ FASE 1 — CIMIENTOS DEL PROYECTO
> **Objetivo:** Construir la base técnica sólida sobre la que se apoya todo el sistema.
> Sin esta fase bien hecha, todas las demás fases sufren deuda técnica.

---

## Paso 1.1 — Estructura de repositorio y entorno

**Qué hacer:**
- Crear repositorio GitHub con la estructura de carpetas definida en el skill
- Configurar `.gitignore`, `README.md`, `LICENSE`
- Configurar entorno virtual Python 3.11+
- Crear `requirements.txt` con todas las dependencias base:
  - `flask`, `flask-sqlalchemy`, `flask-migrate`, `flask-login`
  - `psycopg2-binary`, `python-dotenv`, `gunicorn`
  - `marshmallow`, `wtforms`, `pyjwt`
- Crear `.env` y `.env.example` con todas las variables necesarias
- Configurar `package.json` en `frontend/` con Tailwind + PostCSS

**Archivos clave a crear:**
```
backend/run.py
backend/wsgi.py
backend/.env.example
backend/requirements.txt
frontend/package.json
frontend/tailwind.config.js
frontend/postcss.config.js
```

**Criterio de completado:** `python run.py` levanta el servidor sin errores.

---

## Paso 1.2 — Application Factory y extensiones

**Qué hacer:**
- Implementar `create_app()` con Application Factory Pattern en `backend/app/__init__.py`
- Configurar las tres clases de entorno en `backend/app/core/config.py`:
  - `DevelopmentConfig` → SQLite + DEBUG=True
  - `ProductionConfig` → PostgreSQL + DEBUG=False
  - `TestingConfig` → SQLite en memoria + TESTING=True
- Inicializar todas las extensiones en `backend/app/core/extensions.py`:
  - `db = SQLAlchemy()`
  - `migrate = Migrate()`
  - `login_manager = LoginManager()`
- Configurar Flask para apuntar templates a `frontend/src/templates` y static a `frontend/dist`

**Archivos clave:**
```
backend/app/__init__.py
backend/app/core/config.py
backend/app/core/extensions.py
```

**Criterio de completado:** `create_app()` funciona con los tres entornos sin error.

---

## Paso 1.3 — Modelos base y mixins

**Qué hacer:**
- Implementar `TimestampMixin` con `created_at` y `updated_at` automáticos
- Implementar `TenantMixin` con `tenant_id` como FK indexada a `tenants.id`
- Crear todos los modelos del sistema en el orden correcto (respetando FKs):
  1. `Tenant` — sin TenantMixin, es la raíz
  2. `Branch` — FK directa a tenant
  3. `Role` — con TenantMixin
  4. `User` — con TenantMixin, FK a branch y role
  5. `Product` — **SIN TenantMixin**, catálogo global
  6. `Stock` — con TenantMixin, FK a branch y product (precio y cantidad aquí)
  7. `Sale` — con TenantMixin, FK a branch y user
  8. `SaleItem` — sin TenantMixin (aislamiento transitivo via sale_id)
  9. `AILog` — con TenantMixin

**Reglas críticas de modelos:**
- `Product` NUNCA lleva `tenant_id` — precio y stock viven en `Stock`
- `SaleItem` no necesita `tenant_id` — lo hereda transitivamente de `Sale`
- Todo modelo de negocio nuevo que no use `TenantMixin` debe tener un comentario justificando por qué

**Archivos clave:**
```
backend/app/models/mixins.py
backend/app/models/tenant.py
backend/app/models/branch.py
backend/app/models/role.py
backend/app/models/user.py
backend/app/models/product.py
backend/app/models/stock.py
backend/app/models/sale.py
backend/app/models/sale_item.py
backend/app/models/ai_log.py
backend/app/models/__init__.py
```

**Criterio de completado:** `flask db migrate` genera las migraciones sin errores. `flask db upgrade` crea todas las tablas.

---

## Paso 1.4 — Middleware de tenant y logging

**Qué hacer:**
- Implementar `TenantMiddleware` en `backend/app/core/middleware.py`:
  - En cada request autenticado, inyectar `current_tenant` en el contexto de Flask (`g.tenant`)
  - Registrar tiempo de respuesta y path de cada request
- Implementar `RequestLogger` para auditoría
- Configurar `logging_config.py`:
  - Logs a consola en development
  - Logs a archivo (`logs/ferreteros.log`) en producción
  - Niveles: DEBUG en dev, WARNING en prod

**Archivos clave:**
```
backend/app/core/middleware.py
backend/app/core/logging_config.py
```

**Criterio de completado:** Cada request loguea correctamente. El tenant se inyecta en `g` en requests autenticados.

---

## Paso 1.5 — Layouts base UI y sistema de diseño

**Qué hacer:**
- Crear `frontend/src/templates/base.html` con head, scripts globales y meta tags
- Crear `frontend/src/templates/layouts/app.html` — layout autenticado con sidebar y topbar
- Crear `frontend/src/templates/layouts/auth.html` — layout centrado para login/register
- Crear partials: `sidebar.html`, `topbar.html`, `flash_messages.html`
- Implementar el sistema de diseño Tailwind completo:
  - Sidebar con fondo `bg-gray-900`, ítem activo `bg-indigo-600`
  - Cards KPI con estructura `rounded-2xl shadow-sm p-6`
  - Badges de stock: verde/amarillo/rojo con `rounded-full`
  - Formularios con grid de 2 columnas y focus `ring-indigo-500`
- Crear `frontend/src/js/components/`: `modal.js`, `toast.js`, `datatable.js`, `confirm.js`
- Crear `frontend/src/js/core/`: `api.js`, `auth.js`, `utils.js`

**Archivos clave:**
```
frontend/src/templates/base.html
frontend/src/templates/layouts/app.html
frontend/src/templates/layouts/auth.html
frontend/src/templates/partials/sidebar.html
frontend/src/templates/partials/topbar.html
frontend/src/templates/partials/flash_messages.html
frontend/src/styles/base.css
frontend/src/styles/tailwind.css
frontend/src/js/core/api.js
frontend/src/js/core/utils.js
frontend/src/js/components/modal.js
frontend/src/js/components/toast.js
```

**Criterio de completado:** El layout base renderiza sin errores. Sidebar, topbar y flash messages funcionan.

---

## Paso 1.6 — CI/CD y deploy base en Render

**Qué hacer:**
- Configurar GitHub Actions para lint y tests automáticos en cada push
- Configurar `wsgi.py` como entrypoint de Gunicorn
- Vincular repositorio con Render (auto-deploy desde rama `main`)
- Crear base de datos PostgreSQL en Render y vincular con variables de entorno
- Verificar que `flask db upgrade` corre en el deploy correctamente
- Crear tenant de prueba y usuario admin por defecto en script de seed

**Archivos clave:**
```
backend/wsgi.py
backend/tests/conftest.py
docs/deployment.md
```

**Criterio de completado:** Push a `main` despliega automáticamente en Render. La app corre con PostgreSQL en producción.

---

---

# 🏪 FASE 2 — SISTEMA INTERNO
> **Objetivo:** Construir el núcleo operativo de la ferretería: la herramienta diaria que usan los empleados.
> Esta es la fase que genera valor inmediato para el negocio.

---

## Paso 2.1 — Autenticación completa

**Qué hacer:**
- Blueprint `auth` con rutas: `GET/POST /login`, `GET /logout`, `GET/POST /register`
- Formularios con WTForms: `LoginForm`, `RegisterForm`
- Validaciones backend: email único por tenant, contraseña mínimo 8 caracteres, hash con `werkzeug`
- `flask-login`: `@login_required` en todas las rutas protegidas
- Redirigir a `/dashboard` tras login exitoso, a `/login` si no autenticado
- Manejo de errores: flash messages para credenciales incorrectas
- Templates: `auth/login.html`, `auth/register.html` usando `layouts/auth.html`

**Archivos clave:**
```
backend/app/blueprints/auth/__init__.py
backend/app/blueprints/auth/routes.py
backend/app/blueprints/auth/forms.py
frontend/src/templates/auth/login.html
frontend/src/templates/auth/register.html
backend/tests/test_auth.py
```

**Criterio de completado:** Login, logout y registro funcionan. Rutas protegidas redirigen correctamente.

---

## Paso 2.2 — Gestión de usuarios y roles

**Qué hacer:**
- Service `tenant_service.py`: crear tenant + branch principal + usuario admin en una sola transacción
- Service `user_service.py` (dentro de `inventory_service.py` o separado): CRUD de usuarios
- Blueprint `users` con rutas: `GET /users`, `GET /users/create`, `POST /users`, `GET /users/<id>/edit`, `PUT /users/<id>`, `DELETE /users/<id>`
- Sistema de roles con permisos en JSON: `admin`, `cajero`, `supervisor`
- Decorador `@require_permission('manage_users')` para proteger rutas administrativas
- Templates: `users/index.html`, `users/create.html`, `users/edit.html`
- Filtro obligatorio por `tenant_id` en todos los queries de usuarios

**Archivos clave:**
```
backend/app/services/tenant_service.py
backend/app/blueprints/users/routes.py
backend/app/blueprints/users/forms.py
frontend/src/templates/users/index.html
frontend/src/templates/users/create.html
frontend/src/templates/users/edit.html
frontend/src/js/modules/users.js
backend/tests/test_tenant.py
```

**Criterio de completado:** Admin puede crear, editar y desactivar usuarios. Roles limitan acceso a rutas.

---

## Paso 2.3 — Inventario y gestión de productos

**Qué hacer:**
- `inventory_service.py` con funciones:
  - `get_products(tenant_id, branch_id, filters)` — con paginación y filtros
  - `create_product(tenant_id, branch_id, data)` — crea Product global + Stock del tenant
  - `update_stock(tenant_id, branch_id, product_id, data)`
  - `get_low_stock_alerts(tenant_id, branch_id)` — productos bajo `min_stock`
  - `adjust_stock(tenant_id, branch_id, product_id, quantity, reason)` — con log
- Blueprint `inventory` con CRUD completo
- Búsqueda por nombre, SKU, categoría, marca
- Alertas visuales de stock: badge verde/amarillo/rojo según `quantity` vs `min_stock`
- Modal de confirmación para eliminaciones
- Importación masiva de productos (CSV)
- Templates con tabla paginada y filtros dinámicos via JS

**Archivos clave:**
```
backend/app/services/inventory_service.py
backend/app/blueprints/inventory/routes.py
backend/app/blueprints/inventory/forms.py
frontend/src/templates/inventory/index.html
frontend/src/templates/inventory/create.html
frontend/src/templates/inventory/edit.html
frontend/src/templates/modals/product_form.html
frontend/src/js/modules/inventory.js
backend/tests/test_inventory.py
```

**Criterio de completado:** CRUD de productos funciona. Alertas de stock se muestran correctamente. Búsqueda y filtros operativos.

---

## Paso 2.4 — POS (Punto de Venta)

**Qué hacer:**
- `sale_service.py` con funciones:
  - `process_sale(tenant_id, branch_id, user_id, items, payment_method, discount)`:
    - Validar stock disponible para cada ítem (nunca vender sin stock)
    - Calcular totales, descuentos por ítem y por venta
    - Crear `Sale` + `SaleItem`s en una sola transacción
    - Decrementar stock en `Stock` de forma atómica
    - Registrar en log de operaciones
  - `cancel_sale(tenant_id, sale_id)` — revertir stock
  - `search_products_pos(tenant_id, branch_id, query)` — búsqueda rápida por nombre/SKU
- Blueprint `pos` con rutas: `GET /pos`, `POST /pos/sale`, `GET /pos/search`
- Template POS tipo retail: dos columnas (buscador + carrito), cálculo en tiempo real via JS
- Soporte para múltiples métodos de pago: efectivo, tarjeta, transferencia
- Ticket de venta generado al completar (imprimible)

**Archivos clave:**
```
backend/app/services/sale_service.py
backend/app/blueprints/pos/routes.py
frontend/src/templates/pos/index.html
frontend/src/js/modules/pos.js
backend/tests/test_pos.py
```

**Regla crítica:** Nunca permitir venta si `stock.quantity < cantidad_solicitada`. Validar en backend, no solo en frontend.

**Criterio de completado:** Venta completa funciona end-to-end. Stock se descuenta en tiempo real. Descuentos calculan correctamente.

---

## Paso 2.5 — Historial de ventas y reportes básicos

**Qué hacer:**
- `report_service.py` con funciones:
  - `get_sales_history(tenant_id, branch_id, filters)` — con paginación y filtros de fecha
  - `get_sale_detail(tenant_id, sale_id)` — detalle completo de una venta
  - `get_daily_summary(tenant_id, branch_id, date)` — totales del día
- Blueprint `sales` con rutas: `GET /sales`, `GET /sales/<id>`
- Filtros: rango de fechas, cajero, método de pago, estado
- Vista de detalle con todos los ítems de la venta
- Exportación a CSV del historial filtrado
- Templates: `sales/index.html`, `sales/detail.html`

**Archivos clave:**
```
backend/app/services/report_service.py
backend/app/blueprints/sales/routes.py
frontend/src/templates/sales/index.html
frontend/src/templates/sales/detail.html
frontend/src/js/modules/sales.js
```

**Criterio de completado:** Historial muestra todas las ventas del tenant filtradas. Detalle de venta es correcto. CSV exporta bien.

---

## Paso 2.6 — Dashboard con métricas KPI

**Qué hacer:**
- Dashboard como pantalla principal post-login
- Cards KPI usando la estructura obligatoria definida en el skill:
  - Ventas del día / semana / mes
  - Productos con stock bajo o crítico
  - Total de ingresos del período
  - Últimas 5 ventas realizadas
- Gráfico de ventas últimos 7 días (Chart.js o similar via CDN)
- Accesos rápidos a POS e Inventario
- Datos cargados via AJAX desde endpoints del dashboard blueprint
- Todo filtrado por `tenant_id` y `branch_id` del usuario activo

**Archivos clave:**
```
backend/app/blueprints/dashboard/routes.py
frontend/src/templates/dashboard/index.html
frontend/src/js/modules/dashboard.js
```

**Criterio de completado:** Dashboard carga con métricas reales del tenant. KPIs se actualizan sin recargar la página.

---

## Paso 2.7 — Tests de Fase 2

**Qué hacer:**
- Tests unitarios de servicios con pytest:
  - `test_inventory.py`: CRUD, alertas de stock, ajustes
  - `test_pos.py`: venta exitosa, venta sin stock (debe fallar), cancelación
  - `test_tenant.py`: aislamiento de datos entre dos tenants distintos
- Tests de integración para blueprints principales
- Cobertura mínima: 70% en servicios críticos (`sale_service`, `inventory_service`)
- Fixture de tenant de prueba con datos seed en `conftest.py`

**Archivos clave:**
```
backend/tests/conftest.py
backend/tests/test_inventory.py
backend/tests/test_pos.py
backend/tests/test_tenant.py
```

**Criterio de completado:** `pytest` corre sin fallos. Aislamiento multi-tenant verificado por tests.

---

---

# 🔌 FASE 3 — API REST + ANALYTICS + IA
> **Objetivo:** Exponer la lógica de negocio como API versionada y agregar inteligencia al sistema.
> Esta fase habilita la app móvil futura y enriquece la toma de decisiones.

---

## Paso 3.1 — API REST v1 completa

**Qué hacer:**
- Estructura de rutas bajo `/api/v1/` con autenticación JWT
- Endpoints obligatorios:
  - `POST /api/v1/auth/login` → devuelve JWT token
  - `GET /api/v1/products` → lista productos del tenant (paginada)
  - `GET /api/v1/inventory` → stock por sucursal
  - `POST /api/v1/sales` → registrar venta desde app externa
  - `GET /api/v1/sales` → historial de ventas
  - `GET /api/v1/reports/daily` → resumen diario
  - `GET /api/v1/users` → usuarios del tenant
- Schemas Marshmallow para serialización/deserialización
- Decorador `@jwt_required` y `@tenant_required` para proteger endpoints
- Respuesta estándar: `{"success": true, "data": {}, "message": "OK"}`
- Versionado desde el inicio: `/api/v1/` nunca `/api/`

**Archivos clave:**
```
backend/app/blueprints/api/v1/__init__.py
backend/app/blueprints/api/v1/auth.py
backend/app/blueprints/api/v1/products.py
backend/app/blueprints/api/v1/inventory.py
backend/app/blueprints/api/v1/sales.py
backend/app/blueprints/api/v1/reports.py
backend/app/blueprints/api/v1/schemas.py
backend/app/blueprints/api/v1/utils.py
backend/tests/test_api.py
docs/api.md
```

**Criterio de completado:** Todos los endpoints responden con el formato estándar. JWT válido requerido en todos. Tests de API pasan.

---

## Paso 3.2 — Reportes avanzados

**Qué hacer:**
- Extender `report_service.py` con:
  - Reporte de productos más vendidos (top 10)
  - Reporte de rentabilidad por producto (precio - costo)
  - Reporte de movimientos de stock (entradas/salidas)
  - Comparativa de ventas por período
- Endpoints API: `GET /api/v1/reports/top-products`, `GET /api/v1/reports/profitability`
- Dashboard extendido con nuevos gráficos
- Exportación a PDF de reportes

**Criterio de completado:** Reportes devuelven datos correctos y filtrados por tenant. Exportación PDF funciona.

---

## Paso 3.3 — Módulo de IA básico

**Qué hacer:**
- `AIAnalyzer` como clase base en `backend/app/ai/base.py`
- `InventoryAI` en `inventory_ai.py`:
  - Predicción de reabastecimiento basada en histórico de ventas
  - Detección de productos con rotación baja
  - Sugerencia de cantidad óptima de reorden
- `SalesAI` en `sales_ai.py`:
  - Identificación de patrones de venta por día/hora
  - Predicción de demanda para los próximos 7 días
- Guardar resultados en `AILog` con `tenant_id`
- `ai_service.py` como intermediario entre blueprints y módulo IA
- Endpoint: `GET /api/v1/ai/reorder-suggestions`

**Archivos clave:**
```
backend/app/ai/base.py
backend/app/ai/inventory_ai.py
backend/app/ai/sales_ai.py
backend/app/services/ai_service.py
backend/tests/test_ai.py
```

**Criterio de completado:** IA genera sugerencias basadas en datos reales del tenant. AILog registra cada análisis.

---

---

# 🛒 FASE 4 — ECOMMERCE
> **Objetivo:** Cada ferretería tiene su propia tienda virtual accesible desde internet.
> Los clientes finales pueden ver catálogo, agregar al carrito y hacer pedidos online.

---

## Paso 4.1 — API pública de productos por tenant

**Qué hacer:**
- Endpoint público (sin JWT): `GET /api/v1/store/<tenant_slug>/products`
- Filtros públicos: categoría, marca, precio mínimo/máximo, búsqueda
- Solo muestra productos con `is_active=True` y `stock.quantity > 0`
- Incluir precio del tenant en la respuesta (desde `Stock`)
- Rate limiting para evitar abuso

---

## Paso 4.2 — Tienda virtual por ferretería

**Qué hacer:**
- Blueprint `store` con rutas accesibles por subdominio: `<slug>.ferreteros.app`
- Configurar routing por subdominio en Flask + Nginx
- Template de tienda: catálogo de productos, búsqueda, filtros, paginación
- Página de detalle de producto con imágenes y descripción
- Diseño adaptado para el sector ferretero (no el sidebar interno)

---

## Paso 4.3 — Carrito y proceso de pedido

**Qué hacer:**
- Carrito de compras en sesión (o localStorage para usuarios no registrados)
- Proceso de checkout: datos del cliente, dirección, método de pago
- Modelo `Order` y `OrderItem` — con `TenantMixin`
- Notificación al propietario de la ferretería cuando hay un pedido nuevo
- Panel interno para gestionar pedidos: `GET /orders`, cambio de estados (pendiente/confirmado/enviado/entregado)

---

---

# ☁️ FASE 5 — SAAS COMPLETO
> **Objetivo:** Convertir FERRETEROS en una plataforma SaaS donde cualquier ferretería puede registrarse y empezar a usar el sistema de forma autónoma.

---

## Paso 5.1 — Registro público de ferreterías (self-service)

**Qué hacer:**
- Landing page pública en `ferreteros.app`
- Formulario de registro de nueva ferretería → crea Tenant + Branch + Admin en una transacción
- Verificación de email antes de activar el tenant
- Slugs únicos por tenant validados en registro

---

## Paso 5.2 — Subdominios por ferretería

**Qué hacer:**
- Routing por subdominio: `<slug>.ferreteros.app` apunta al tenant correcto
- Certificados SSL automáticos por subdominio (Let's Encrypt + Nginx)
- Middleware actualizado para resolver `current_tenant` desde el subdominio además del JWT

---

## Paso 5.3 — Planes y suscripciones

**Qué hacer:**
- Modelo `Plan` (free, starter, pro, enterprise) con límites: `max_branches`, `max_users`, `max_products`
- Modelo `Subscription` con `TenantMixin`: plan activo, fecha de renovación, estado
- Integración con Stripe para cobro recurrente
- Middleware de validación de límites del plan antes de operaciones
- Panel de administración de la plataforma (superadmin): ver todos los tenants, gestionar planes

---

## Paso 5.4 — Panel de administración de plataforma

**Qué hacer:**
- Blueprint `admin` solo accesible para superadmins de la plataforma
- Métricas globales: tenants activos, ARR, churn, nuevos registros
- Gestión de tenants: activar/desactivar, cambiar plan, ver estadísticas
- Logs de operaciones críticas a nivel plataforma

---

---

# 📱 FASE 6 — APP MÓVIL + MARKETPLACE B2B
> **Objetivo:** Llevar FERRETEROS al bolsillo de los dueños y abrir un canal mayorista entre ferreterías.

---

## Paso 6.1 — App móvil con Flutter

**Qué hacer:**
- Proyecto Flutter separado que consume la API REST v1 ya construida
- Autenticación con JWT — mismo sistema del backend
- Módulos móviles prioritarios:
  - Dashboard con KPIs del día
  - Consulta de stock en tiempo real
  - Registro de ventas desde el celular
  - Alertas de stock bajo (push notifications)
- Soporte iOS y Android desde un único código base

---

## Paso 6.2 — Catálogo universal de productos

**Qué hacer:**
- Interfaz de administración del catálogo global (solo superadmins)
- Carga masiva de productos con SKU universal, categorías normalizadas y marcas
- API para que ferreterías busquen en el catálogo global y agreguen productos a su inventario
- Endpoint: `GET /api/v1/catalog/search?q=tornillo`

---

## Paso 6.3 — Marketplace B2B

**Qué hacer:**
- Modelo `B2BOrder` con `TenantMixin` (tenant comprador)
- Una ferretería puede publicar excedente de stock como oferta mayorista
- Otra ferretería puede comprar ese stock directamente desde la plataforma
- Sistema de reputación básico (calificaciones entre ferreterías)
- Notificaciones de nuevas ofertas mayoristas por categoría de interés
- El catálogo universal compartido evita duplicación de datos de productos

---

---

# 📋 GUÍA DE TRANSICIÓN ENTRE FASES

## ¿Cuándo pasar a la siguiente fase?

| Fase completada | Requisito para avanzar |
|---|---|
| Fase 1 → Fase 2 | Estructura de carpetas creada, modelos con migraciones, CI/CD funcional |
| Fase 2 → Fase 3 | POS funcional, inventario con alertas, usuarios y roles, tests de aislamiento multi-tenant pasan |
| Fase 3 → Fase 4 | API REST v1 documentada y testeada, IA generando sugerencias, cobertura 70%+ en servicios críticos |
| Fase 4 → Fase 5 | Tienda virtual funcional por tenant, carrito y pedidos operativos |
| Fase 5 → Fase 6 | Sistema SaaS estable con suscripciones y subdominios, +10 tenants activos en producción |

## Regla de no regresión

> Una vez que una fase está completa, **no se modifica su estructura base**.
> Si se detecta una mejora necesaria, se implementa como una capa adicional, nunca reescribiendo desde cero.

---

# 🔒 INVARIANTES QUE NO CAMBIAN EN NINGUNA FASE

Estas reglas aplican en **todas las fases** sin excepción:

- Todo modelo de negocio nuevo hereda `TenantMixin` — si no, justificar en código
- Ningún query sobre datos de negocio sin filtrar por `tenant_id`
- `Product` NUNCA lleva `tenant_id` — precio y stock viven en `Stock`
- Lógica de negocio SOLO en `services/` — nunca en blueprints ni templates
- API REST siempre bajo `/api/v1/` — nunca romper el versionado
- Código completo entregado — sin fragmentos ni placeholders
- Tailwind CSS para UI — sin CSS inline

---

*FERRETEROS — Roadmap Oficial v1.0 | Basado en FERRETEROS SKILL MASTER 1.0*
*Stack: Python 3.11 + Flask + PostgreSQL + Tailwind CSS + Flutter (Fase 6)*
