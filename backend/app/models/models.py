from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

# Schema: manufacturing
class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"schema": "manufacturing"}
    product_id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String, unique=True, index=True)
    standard_cycle_time_min = Column(Float)

class Material(Base):
    __tablename__ = "materials"
    __table_args__ = {"schema": "manufacturing"}
    material_id = Column(Integer, primary_key=True, index=True)
    lead_time_days = Column(Integer)
    safety_stock_level = Column(Integer)
    reorder_point = Column(Integer)
    holding_cost_per_unit = Column(Float)
    ordering_cost = Column(Float)

class BomHeader(Base):
    __tablename__ = "bom_headers"
    __table_args__ = {"schema": "manufacturing"}
    bom_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("manufacturing.products.product_id"))

class BomItem(Base):
    __tablename__ = "bom_items"
    __table_args__ = {"schema": "manufacturing"}
    bom_item_id = Column(Integer, primary_key=True, index=True)
    bom_id = Column(Integer, ForeignKey("manufacturing.bom_headers.bom_id"))
    material_id = Column(Integer, ForeignKey("manufacturing.materials.material_id"))
    quantity_required = Column(Float)
    scrap_percentage = Column(Float)

class Machine(Base):
    __tablename__ = "machines"
    __table_args__ = {"schema": "manufacturing"}
    machine_id = Column(Integer, primary_key=True, index=True)
    rated_capacity_per_hour = Column(Float)
    status = Column(String)
    utilization_percentage = Column(Float)

class ProductionLine(Base):
    __tablename__ = "production_lines"
    __table_args__ = {"schema": "manufacturing"}
    line_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class WorkOrder(Base):
    __tablename__ = "work_orders"
    __table_args__ = {"schema": "manufacturing"}
    work_order_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("manufacturing.products.product_id"))
    planned_quantity = Column(Integer)
    status = Column(String)

class ProductionSchedule(Base):
    __tablename__ = "production_schedules"
    __table_args__ = {"schema": "manufacturing"}
    schedule_id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("manufacturing.work_orders.work_order_id"))
    machine_id = Column(Integer, ForeignKey("manufacturing.machines.machine_id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)

class MachineMaintenance(Base):
    __tablename__ = "machine_maintenance"
    __table_args__ = {"schema": "manufacturing"}
    maintenance_id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("manufacturing.machines.machine_id"))
    scheduled_date = Column(DateTime)
    status = Column(String)

# Schema: inventory
class Warehouse(Base):
    __tablename__ = "warehouses"
    __table_args__ = {"schema": "inventory"}
    warehouse_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)

class InventoryStock(Base):
    __tablename__ = "inventory_stock"
    __table_args__ = {"schema": "inventory"}
    stock_id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("manufacturing.materials.material_id"))
    warehouse_id = Column(Integer, ForeignKey("inventory.warehouses.warehouse_id"))
    quantity_on_hand = Column(Integer)
    quantity_reserved = Column(Integer)
    safety_stock = Column(Integer)

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    __table_args__ = {"schema": "inventory"}
    transaction_id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("manufacturing.materials.material_id"))
    transaction_type = Column(String)
    quantity = Column(Integer)
    transaction_time = Column(DateTime, default=datetime.utcnow)

# Schema: procurement
class Supplier(Base):
    __tablename__ = "suppliers"
    __table_args__ = {"schema": "procurement"}
    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    lead_time_days = Column(Integer)
    reliability_score = Column(Float)
    quality_score = Column(Float)

class SupplierMaterial(Base):
    __tablename__ = "supplier_materials"
    __table_args__ = {"schema": "procurement"}
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("procurement.suppliers.supplier_id"))
    material_id = Column(Integer, ForeignKey("manufacturing.materials.material_id"))
    unit_price = Column(Float)
    lead_time_days = Column(Integer)
    minimum_order_quantity = Column(Integer)

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    __table_args__ = {"schema": "procurement"}
    po_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("procurement.suppliers.supplier_id"))
    expected_delivery_date = Column(DateTime)
    status = Column(String)

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    __table_args__ = {"schema": "procurement"}
    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("procurement.purchase_orders.po_id"))
    material_id = Column(Integer, ForeignKey("manufacturing.materials.material_id"))
    ordered_quantity = Column(Integer)
    received_quantity = Column(Integer)

# Schema: orders
class CustomerOrder(Base):
    __tablename__ = "customer_orders"
    __table_args__ = {"schema": "orders"}
    order_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("manufacturing.products.product_id"))
    quantity = Column(Integer)
    requested_date = Column(DateTime)
    priority = Column(String)
    status = Column(String)

# Schema: application
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "application"}
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "application"}
    role_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "application"}
    user_id = Column(Integer, ForeignKey("application.users.user_id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("application.roles.role_id"), primary_key=True)

# Schema: audit
class AgentExecution(Base):
    __tablename__ = "agent_executions"
    __table_args__ = {"schema": "audit"}
    execution_id = Column(Integer, primary_key=True, index=True)
    query_id = Column(String, index=True)
    agent_name = Column(String)
    input = Column(Text)
    output = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration_ms = Column(Integer)

class ToolExecution(Base):
    __tablename__ = "tool_executions"
    __table_args__ = {"schema": "audit"}
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("audit.agent_executions.execution_id"))
    tool_name = Column(String)
    input = Column(Text)
    output = Column(Text)

class DecisionAudit(Base):
    __tablename__ = "decision_audits"
    __table_args__ = {"schema": "audit"}
    decision_id = Column(Integer, primary_key=True, index=True)
    query_id = Column(String, index=True)
    final_recommendation = Column(String)
    confidence = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
