"""Initial schema with 11 tables and RLS policies.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-04-20 23:52:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create STORES table
    op.create_table(
        "stores",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("sii_rut", sa.String(20), nullable=True),
        sa.Column("sii_config", postgresql.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.literal(True), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sii_rut", name="uq_stores_sii_rut"),
    )
    op.create_index("idx_stores_owner_id", "stores", ["owner_id"])

    # Create USERS table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("pin", sa.String(4), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.literal(True), nullable=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.CheckConstraint("role IN ('ADMIN', 'GERENTE', 'CAJERO', 'OPERADOR')", name="check_user_role"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("idx_users_store_id", "users", ["store_id"])
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_role", "users", ["role"])

    # Add foreign key for stores.owner_id AFTER users table exists
    op.create_foreign_key("fk_stores_owner_id", "stores", "users", ["owner_id"], ["id"])

    # Create CATEGORIES table
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "name", name="uq_categories_store_name"),
    )
    op.create_index("idx_categories_store_id", "categories", ["store_id"])

    # Create PRODUCTS table
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("barcode", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("stock_quantity", sa.Numeric(10, 3), server_default=sa.literal(0), nullable=False),
        sa.Column("min_stock", sa.Numeric(10, 3), server_default=sa.literal(0), nullable=False),
        sa.Column("reorder_quantity", sa.Numeric(10, 3), nullable=True),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.literal(True), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.CheckConstraint("unit IN ('kg', 'unit', 'L', 'ml')", name="check_product_unit"),
        sa.CheckConstraint("price > 0", name="check_product_price_positive"),
        sa.CheckConstraint("stock_quantity >= 0", name="check_product_stock_non_negative"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "barcode", name="uq_products_store_barcode"),
    )
    op.create_index("idx_products_by_barcode", "products", ["store_id", "barcode"])
    op.create_index("idx_products_store_id", "products", ["store_id"])
    op.create_index("idx_products_barcode", "products", ["barcode"])
    op.create_index("idx_products_category_id", "products", ["category_id"])

    # Create STATIONS table
    op.create_table(
        "stations",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), server_default=sa.literal("idle"), nullable=False),
        sa.Column("current_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.CheckConstraint("number BETWEEN 1 AND 4", name="check_station_number_range"),
        sa.CheckConstraint("status IN ('idle', 'active', 'maintenance')", name="check_station_status"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "number", name="uq_stations_store_number"),
    )
    op.create_index("idx_stations_store_id", "stations", ["store_id"])

    # Create ORDERS table
    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("uuid", sa.String(36), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("station_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(50), server_default=sa.literal("pending"), nullable=False),
        sa.Column("total", sa.Numeric(10, 2), server_default=sa.literal(0), nullable=False),
        sa.Column("item_count", sa.Integer(), server_default=sa.literal(0), nullable=True),
        sa.Column("qr_code", postgresql.BYTEA(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.CheckConstraint("status IN ('pending', 'confirmed', 'cancelled')", name="check_order_status"),
        sa.CheckConstraint("total > 0 OR status = 'pending'", name="check_order_total"),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"]),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid", name="uq_orders_uuid"),
    )
    op.create_index("idx_orders_by_uuid", "orders", ["store_id", "uuid"])
    op.create_index("idx_orders_store_id", "orders", ["store_id"])
    op.create_index("idx_orders_station_id", "orders", ["station_id"])
    op.create_index("idx_orders_uuid", "orders", ["uuid"])
    op.create_index("idx_orders_created_at", "orders", ["created_at"])

    # Update STATIONS table with foreign key to orders
    op.create_foreign_key("fk_stations_current_order_id", "stations", "orders", ["current_order_id"], ["id"])

    # Create ORDER_ITEMS table
    op.create_table(
        "order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.CheckConstraint("quantity > 0", name="check_order_item_quantity_positive"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_order_items_order_id", "order_items", ["order_id"])
    op.create_index("idx_order_items_product_id", "order_items", ["product_id"])

    # Create TRANSACTIONS table
    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=False),
        sa.Column("amount_paid", sa.Numeric(10, 2), nullable=False),
        sa.Column("change_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("status", sa.String(50), server_default=sa.literal("completed"), nullable=False),
        sa.Column("boleta_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.CheckConstraint(
            "payment_method IN ('cash', 'debit_card', 'credit_card', 'transfer')",
            name="check_transaction_payment_method",
        ),
        sa.CheckConstraint("status IN ('completed', 'voided', 'refunded')", name="check_transaction_status"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id", name="uq_transactions_order_id"),
    )
    op.create_index("idx_transactions_store_id", "transactions", ["store_id"])
    op.create_index("idx_transactions_user_id", "transactions", ["user_id"])
    op.create_index("idx_transactions_order_id", "transactions", ["order_id"])
    op.create_index("idx_transactions_by_date", "transactions", ["store_id", "created_at"])

    # Create BOLETAS table
    op.create_table(
        "boletas",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("folio_sii", sa.Integer(), nullable=True),
        sa.Column("xml_dte", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), server_default=sa.literal("pending"), nullable=False),
        sa.Column("emission_timestamp", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("provider", sa.String(50), nullable=True),
        sa.Column("external_reference", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.CheckConstraint("status IN ('pending', 'emitted', 'rejected', 'cancelled')", name="check_boleta_status"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id", name="uq_boletas_transaction_id"),
    )
    op.create_index("idx_boletas_transaction_id", "boletas", ["transaction_id"])
    op.create_index("idx_boletas_folio_sii", "boletas", ["folio_sii"])
    op.create_index("idx_boletas_status", "boletas", ["status"])

    # Update TRANSACTIONS table with foreign key to boletas
    op.create_foreign_key("fk_transactions_boleta_id", "transactions", "boletas", ["boleta_id"], ["id"])

    # Create INVENTORY_MOVEMENTS table
    op.create_table(
        "inventory_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("quantity_before", sa.Numeric(10, 3), nullable=False),
        sa.Column("quantity_after", sa.Numeric(10, 3), nullable=False),
        sa.Column("delta", sa.Numeric(10, 3), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.CheckConstraint("type IN ('sale', 'adjustment', 'restock', 'loss')", name="check_inventory_movement_type"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_inventory_movements_product_id", "inventory_movements", ["product_id"])
    op.create_index("idx_inventory_movements_transaction_id", "inventory_movements", ["transaction_id"])
    op.create_index("idx_inventory_movements_type", "inventory_movements", ["type"])
    op.create_index("idx_inventory_movements_timeline", "inventory_movements", ["product_id", "created_at"])
    op.create_index("idx_inventory_movements_user_id", "inventory_movements", ["user_id"])

    # Create AUDIT_LOGS table
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("old_values", postgresql.JSON(), nullable=True),
        sa.Column("new_values", postgresql.JSON(), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), server_default=sa.literal("success"), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("idx_audit_logs_action", "audit_logs", ["action"])
    op.create_index("idx_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("idx_audit_logs_timeline", "audit_logs", ["created_at"])

    # ============================================================================
    # ROW-LEVEL SECURITY (RLS) POLICIES
    # ============================================================================
    # Enable RLS y crear policies para tablas con store_id (multi-tenant isolation)

    # Helper function to get current store_id from context
    op.execute(
        """
        CREATE OR REPLACE FUNCTION get_current_store_id()
        RETURNS UUID AS $$
        BEGIN
            RETURN COALESCE(current_setting('app.current_store_id', true)::uuid, '00000000-0000-0000-0000-000000000000'::uuid);
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # Enable RLS on USERS table
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY users_rls_policy ON users
        USING (store_id = get_current_store_id());
        """
    )

    # Enable RLS on CATEGORIES table
    op.execute("ALTER TABLE categories ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY categories_rls_policy ON categories
        USING (store_id = get_current_store_id());
        """
    )

    # Enable RLS on PRODUCTS table
    op.execute("ALTER TABLE products ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY products_rls_policy ON products
        USING (store_id = get_current_store_id());
        """
    )

    # Enable RLS on STATIONS table
    op.execute("ALTER TABLE stations ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY stations_rls_policy ON stations
        USING (store_id = get_current_store_id());
        """
    )

    # Enable RLS on ORDERS table
    op.execute("ALTER TABLE orders ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY orders_rls_policy ON orders
        USING (store_id = get_current_store_id());
        """
    )

    # Enable RLS on TRANSACTIONS table
    op.execute("ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY transactions_rls_policy ON transactions
        USING (store_id = get_current_store_id());
        """
    )

    # Enable RLS on INVENTORY_MOVEMENTS table (indirecto via product)
    # For simplicity, we check via join to products table
    op.execute("ALTER TABLE inventory_movements ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY inventory_movements_rls_policy ON inventory_movements
        USING (
            product_id IN (
                SELECT id FROM products WHERE store_id = get_current_store_id()
            )
        );
        """
    )

    # Enable RLS on AUDIT_LOGS table (tenant-aware if user has store_id)
    op.execute("ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY audit_logs_rls_policy ON audit_logs
        USING (
            user_id IS NULL OR
            user_id IN (
                SELECT id FROM users WHERE store_id = get_current_store_id()
            )
        );
        """
    )


def downgrade() -> None:
    # Drop RLS policies first
    op.execute("DROP POLICY IF EXISTS audit_logs_rls_policy ON audit_logs;")
    op.execute("DROP POLICY IF EXISTS inventory_movements_rls_policy ON inventory_movements;")
    op.execute("DROP POLICY IF EXISTS transactions_rls_policy ON transactions;")
    op.execute("DROP POLICY IF EXISTS orders_rls_policy ON orders;")
    op.execute("DROP POLICY IF EXISTS stations_rls_policy ON stations;")
    op.execute("DROP POLICY IF EXISTS products_rls_policy ON products;")
    op.execute("DROP POLICY IF EXISTS categories_rls_policy ON categories;")
    op.execute("DROP POLICY IF EXISTS users_rls_policy ON users;")
    op.execute("DROP FUNCTION IF EXISTS get_current_store_id();")

    # Disable RLS
    op.execute("ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE inventory_movements DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE transactions DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE orders DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE stations DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE products DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE categories DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")

    # Drop tables in reverse order of creation
    op.drop_table("audit_logs")
    op.drop_table("inventory_movements")
    op.drop_table("boletas")
    op.drop_table("transactions")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("stations")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("users")
    op.drop_table("stores")
