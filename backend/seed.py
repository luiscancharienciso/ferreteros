import os
from werkzeug.security import generate_password_hash

from app import create_app
from app.core.extensions import db

from app.models.user import User
from app.models.tenant import Tenant
from app.models.branch import Branch
from app.models.role import Role

from app.services import tenant_service


def seed_database():
    """
    Inicializa la base de datos con:

    1️⃣  Tenant interno de plataforma + superadmin
    2️⃣  Tenant demo para pruebas (opcional)

    Configuración via variables de entorno:

        SEED_SUPERADMIN_EMAIL     Email del superadmin de plataforma
        SEED_SUPERADMIN_PASSWORD  Contraseña del superadmin (mín. 8 caracteres)
        SEED_DEMO_NAME            Nombre del admin del tenant demo
        SEED_DEMO_EMAIL           Email del admin del tenant demo
        SEED_DEMO_PASSWORD        Contraseña del admin del tenant demo

    Si SEED_DEMO_EMAIL no está definido, el tenant demo no se crea.
    Esto es útil en producción donde no se quiere un tenant de pruebas.
    """

    if User.query.first():
        print("⚠️  Seed omitido: ya existen usuarios.")
        return

    # --- Leer y validar variables requeridas ---
    superadmin_email    = os.getenv("SEED_SUPERADMIN_EMAIL", "").strip()
    superadmin_password = os.getenv("SEED_SUPERADMIN_PASSWORD", "").strip()

    if not superadmin_email or not superadmin_password:
        raise EnvironmentError(
            "SEED_SUPERADMIN_EMAIL y SEED_SUPERADMIN_PASSWORD son requeridas.\n"
            "Definílas en tu .env antes de correr seed.py"
        )

    if len(superadmin_password) < 8:
        raise ValueError("SEED_SUPERADMIN_PASSWORD debe tener al menos 8 caracteres.")

    print("🌱 Creando datos iniciales...")

    # -------------------------------------------------------
    # 1️⃣  Tenant interno de plataforma
    # -------------------------------------------------------

    platform = Tenant(
        name="FERRETEROS PLATFORM",
        slug="platform",
        plan="internal",
        is_active=True
    )
    db.session.add(platform)
    db.session.flush()

    branch = Branch(
        name="Platform Main",
        tenant_id=platform.id,
        is_main=True
    )
    db.session.add(branch)
    db.session.flush()

    role = Role(
        name="admin",
        tenant_id=platform.id,
        permissions=[
            "manage_users",
            "manage_inventory",
            "manage_sales",
            "view_reports",
        ]
    )
    db.session.add(role)
    db.session.flush()

    superadmin = User(
        name="Platform Admin",
        email=superadmin_email,
        password_hash=generate_password_hash(superadmin_password),
        tenant_id=platform.id,
        branch_id=branch.id,
        role_id=role.id,
        is_superadmin=True,
        is_active=True
    )
    db.session.add(superadmin)

    # -------------------------------------------------------
    # 2️⃣  Tenant demo (solo si SEED_DEMO_EMAIL está definido)
    # -------------------------------------------------------

    demo_email    = os.getenv("SEED_DEMO_EMAIL", "").strip()
    demo_password = os.getenv("SEED_DEMO_PASSWORD", "").strip()
    demo_name     = os.getenv("SEED_DEMO_NAME", "Admin Demo").strip()

    demo_result = None

    if demo_email:
        if not demo_password:
            raise EnvironmentError(
                "SEED_DEMO_PASSWORD es requerida cuando SEED_DEMO_EMAIL está definido."
            )
        if len(demo_password) < 8:
            raise ValueError("SEED_DEMO_PASSWORD debe tener al menos 8 caracteres.")

        demo_result = tenant_service.create_tenant(
            tenant_name="Ferretería Demo",
            branch_name="Sucursal Principal",
            admin_name=demo_name,
            admin_email=demo_email,
            admin_password=demo_password,
        )

    db.session.commit()

    print("✅ Seed completado")
    print(f"   Superadmin : {superadmin.email}")
    if demo_result:
        print(f"   Tenant demo: {demo_result['admin_user'].email}")
    else:
        print("   Tenant demo: no creado (SEED_DEMO_EMAIL no definido)")


if __name__ == "__main__":

    app = create_app()

    with app.app_context():
        seed_database()