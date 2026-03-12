"""
test_tenant.py — Tests para tenant_service y user_service.

Cubre:
- Creación completa de tenant (transacción atómica)
- Slugify y unicidad de slugs
- Validaciones de email, contraseña y rol
- CRUD de usuarios con aislamiento multi-tenant
- Protección del último admin activo
- Autoprotección (no eliminar/desactivar a uno mismo)
"""

import pytest
from app.core.extensions import db
from app.services import tenant_service, user_service
from app.services.tenant_service import _slugify, _ensure_unique_slug


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tenant_data():
    """Datos base para crear un tenant de prueba."""
    return {
        "tenant_name":    "Ferretería Test",
        "branch_name":    "Casa Central",
        "admin_name":     "Admin Test",
        "admin_email":    "admin@test.com",
        "admin_password": "password123",
    }


@pytest.fixture
def created_tenant(app, tenant_data):
    """Crea un tenant completo y devuelve el resultado de create_tenant."""
    with app.app_context():
        result = tenant_service.create_tenant(**tenant_data)
        yield result


# ---------------------------------------------------------------------------
# Tests: _slugify
# ---------------------------------------------------------------------------

class TestSlugify:

    def test_basico(self):
        assert _slugify("Ferretería Norte") == "ferreteria-norte"

    def test_tildes(self):
        assert _slugify("Ferretería Ñoño") == "ferreteria-nono"

    def test_mayusculas(self):
        assert _slugify("FERRETERÍA EL CLAVO") == "ferreteria-el-clavo"

    def test_espacios_extremos(self):
        assert _slugify("  ferretería test  ") == "ferreteria-test"

    def test_caracteres_especiales(self):
        assert _slugify("Ferretería & Cía.") == "ferreteria-cia"

    def test_guiones_multiples(self):
        assert _slugify("ferretería - el - norte") == "ferreteria-el-norte"


# ---------------------------------------------------------------------------
# Tests: create_tenant
# ---------------------------------------------------------------------------

class TestCreateTenant:

    def test_crea_tenant(self, app, tenant_data):
        with app.app_context():
            result = tenant_service.create_tenant(**tenant_data)
            assert result["tenant"].id is not None
            assert result["tenant"].name == "Ferretería Test"
            assert result["tenant"].slug == "ferreteria-test"
            assert result["tenant"].is_active is True

    def test_crea_branch_principal(self, app, tenant_data):
        with app.app_context():
            result = tenant_service.create_tenant(**tenant_data)
            assert result["branch"].is_main is True
            assert result["branch"].tenant_id == result["tenant"].id

    def test_crea_tres_roles_base(self, app, tenant_data):
        with app.app_context():
            result = tenant_service.create_tenant(**tenant_data)
            roles = result["roles"]
            assert "admin" in roles
            assert "supervisor" in roles
            assert "cajero" in roles

    def test_admin_tiene_permisos_correctos(self, app, tenant_data):
        with app.app_context():
            result = tenant_service.create_tenant(**tenant_data)
            admin_role = result["roles"]["admin"]
            assert "manage_users" in admin_role.permissions
            assert "manage_inventory" in admin_role.permissions
            assert "view_reports" in admin_role.permissions

    def test_cajero_solo_tiene_manage_sales(self, app, tenant_data):
        with app.app_context():
            result = tenant_service.create_tenant(**tenant_data)
            cajero_role = result["roles"]["cajero"]
            assert cajero_role.permissions == ["manage_sales"]

    def test_crea_usuario_admin(self, app, tenant_data):
        with app.app_context():
            result = tenant_service.create_tenant(**tenant_data)
            admin = result["admin_user"]
            assert admin.email == "admin@test.com"
            assert admin.name == "Admin Test"
            assert admin.is_active is True
            assert admin.tenant_id == result["tenant"].id
            assert admin.role_id == result["roles"]["admin"].id

    def test_password_hasheado(self, app, tenant_data):
        from werkzeug.security import check_password_hash
        with app.app_context():
            result = tenant_service.create_tenant(**tenant_data)
            assert check_password_hash(result["admin_user"].password_hash, "password123")

    def test_falla_si_email_duplicado(self, app, tenant_data):
        with app.app_context():
            tenant_service.create_tenant(**tenant_data)
            with pytest.raises(ValueError, match="ya está registrado"):
                tenant_service.create_tenant(
                    tenant_name="Otra Ferretería",
                    branch_name="Sucursal",
                    admin_name="Otro Admin",
                    admin_email="admin@test.com",  # mismo email
                    admin_password="password123",
                )

    def test_falla_si_password_corta(self, app, tenant_data):
        with app.app_context():
            tenant_data["admin_password"] = "corta"
            with pytest.raises(ValueError, match="8 caracteres"):
                tenant_service.create_tenant(**tenant_data)

    def test_slugs_unicos_con_sufijo(self, app, tenant_data):
        with app.app_context():
            r1 = tenant_service.create_tenant(**tenant_data)
            r2 = tenant_service.create_tenant(
                tenant_name="Ferretería Test",   # mismo nombre
                branch_name="Casa Central",
                admin_name="Admin Dos",
                admin_email="admin2@test.com",
                admin_password="password123",
            )
            assert r1["tenant"].slug == "ferreteria-test"
            assert r2["tenant"].slug == "ferreteria-test-2"

    def test_rollback_si_falla(self, app, tenant_data):
        """Si create_tenant falla a mitad, no debe quedar nada en la DB."""
        from app.models.tenant import Tenant
        with app.app_context():
            tenant_data["admin_password"] = "corta"  # provocar error
            with pytest.raises(ValueError):
                tenant_service.create_tenant(**tenant_data)
            # No debe existir ningún tenant en la DB
            assert Tenant.query.count() == 0


# ---------------------------------------------------------------------------
# Tests: user_service
# ---------------------------------------------------------------------------

class TestUserService:

    @pytest.fixture
    def setup(self, app, tenant_data):
        """Crea tenant + contexto para tests de user_service."""
        with app.app_context():
            result = tenant_service.create_tenant(**tenant_data)
            yield {
                "tenant_id": result["tenant"].id,
                "branch_id": result["branch"].id,
                "admin_id":  result["admin_user"].id,
                "admin_role_id": result["roles"]["admin"].id,
                "cajero_role_id": result["roles"]["cajero"].id,
            }

    def test_get_users_filtra_por_tenant(self, app, setup):
        with app.app_context():
            users = user_service.get_users(setup["tenant_id"])
            assert all(u.tenant_id == setup["tenant_id"] for u in users)

    def test_create_user(self, app, setup):
        with app.app_context():
            user = user_service.create_user(
                tenant_id=setup["tenant_id"],
                branch_id=setup["branch_id"],
                name="Juan Cajero",
                email="cajero@test.com",
                password="password123",
                role_id=setup["cajero_role_id"],
            )
            assert user.id is not None
            assert user.email == "cajero@test.com"
            assert user.tenant_id == setup["tenant_id"]

    def test_create_user_email_duplicado_en_tenant(self, app, setup):
        with app.app_context():
            with pytest.raises(ValueError, match="ya está en uso"):
                user_service.create_user(
                    tenant_id=setup["tenant_id"],
                    branch_id=setup["branch_id"],
                    name="Otro Admin",
                    email="admin@test.com",  # ya existe
                    password="password123",
                    role_id=setup["admin_role_id"],
                )

    def test_create_user_rol_de_otro_tenant_falla(self, app, setup, tenant_data):
        with app.app_context():
            # Crear segundo tenant
            r2 = tenant_service.create_tenant(
                tenant_name="Otra Ferretería",
                branch_name="Sucursal",
                admin_name="Admin Dos",
                admin_email="admin2@test.com",
                admin_password="password123",
            )
            with pytest.raises(ValueError, match="no es válido"):
                user_service.create_user(
                    tenant_id=setup["tenant_id"],
                    branch_id=setup["branch_id"],
                    name="Usuario Raro",
                    email="raro@test.com",
                    password="password123",
                    role_id=r2["roles"]["admin"].id,  # rol de otro tenant
                )

    def test_update_user(self, app, setup):
        with app.app_context():
            updated = user_service.update_user(
                tenant_id=setup["tenant_id"],
                user_id=setup["admin_id"],
                name="Nombre Actualizado",
                email="admin@test.com",
                role_id=setup["admin_role_id"],
                is_active=True,
            )
            assert updated.name == "Nombre Actualizado"

    def test_delete_user_no_puede_eliminarse_a_si_mismo(self, app, setup):
        with app.app_context():
            with pytest.raises(ValueError, match="ti mismo"):
                user_service.delete_user(
                    tenant_id=setup["tenant_id"],
                    user_id=setup["admin_id"],
                    requesting_user_id=setup["admin_id"],
                )

    def test_delete_ultimo_admin_falla(self, app, setup):
        with app.app_context():
            # Crear segundo usuario que hará la solicitud
            segundo = user_service.create_user(
                tenant_id=setup["tenant_id"],
                branch_id=setup["branch_id"],
                name="Segundo Admin",
                email="admin2@test.com",
                password="password123",
                role_id=setup["admin_role_id"],
            )
            # El segundo intenta eliminar al primero (único admin activo restante después)
            # Primero desactivamos al segundo para que solo quede el primero
            segundo.is_active = False
            db.session.commit()

            with pytest.raises(ValueError, match="único administrador activo"):
                user_service.delete_user(
                    tenant_id=setup["tenant_id"],
                    user_id=setup["admin_id"],
                    requesting_user_id=segundo.id,
                )

    def test_aislamiento_entre_tenants(self, app, setup, tenant_data):
        """Un usuario de tenant A no debe ser visible desde tenant B."""
        with app.app_context():
            r2 = tenant_service.create_tenant(
                tenant_name="Otra Ferretería",
                branch_name="Sucursal",
                admin_name="Admin Dos",
                admin_email="admin2@test.com",
                admin_password="password123",
            )
            # Intentar obtener usuario del tenant A desde el tenant B
            user = user_service.get_user_by_id(
                tenant_id=r2["tenant"].id,
                user_id=setup["admin_id"],  # usuario del tenant A
            )
            assert user is None