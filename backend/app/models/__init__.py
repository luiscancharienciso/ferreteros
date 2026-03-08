# Importar todos los modelos para que Flask-Migrate los detecte

from .tenant import Tenant
from .branch import Branch
from .role import Role
from .user import User
from .product import Product
from .stock import Stock
from .sale import Sale
from .sale_item import SaleItem
from .ai_log import AILog