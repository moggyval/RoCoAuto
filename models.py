import uuid
from datetime import datetime
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def uuid_str():
    return str(uuid.uuid4())

class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.String(36), primary_key=True, default=uuid_str)

    name = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(40), nullable=True, index=True)
    email = db.Column(db.String(255), nullable=True, index=True)

    address1 = db.Column(db.String(255), nullable=True)
    address2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    state = db.Column(db.String(40), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)

    source = db.Column(db.String(80), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

class Vehicle(db.Model):
    __tablename__ = "vehicles"
    id = db.Column(db.String(36), primary_key=True, default=uuid_str)
    customer_id = db.Column(db.String(36), db.ForeignKey("customers.id"), nullable=False, index=True)

    year = db.Column(db.Integer, nullable=True)
    make = db.Column(db.String(60), nullable=True, index=True)
    model = db.Column(db.String(60), nullable=True, index=True)
    engine = db.Column(db.String(80), nullable=True)

    vin = db.Column(db.String(32), nullable=True, index=True)
    plate = db.Column(db.String(20), nullable=True)
    odometer_last = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class RepairOrder(db.Model):
    __tablename__ = "repair_orders"
    id = db.Column(db.String(36), primary_key=True, default=uuid_str)
    ro_number = db.Column(db.Integer, unique=True, index=True, nullable=False)

    customer_id = db.Column(db.String(36), db.ForeignKey("customers.id"), nullable=False, index=True)
    vehicle_id = db.Column(db.String(36), db.ForeignKey("vehicles.id"), nullable=False, index=True)

    status = db.Column(db.String(30), nullable=False, default="open")  # open/estimate_sent/work_in_progress/closed/canceled
    concern = db.Column(db.Text, nullable=True)
    findings = db.Column(db.Text, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)

    opened_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    closed_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

class ROEvent(db.Model):
    __tablename__ = "ro_events"
    id = db.Column(db.String(36), primary_key=True, default=uuid_str)
    ro_id = db.Column(db.String(36), db.ForeignKey("repair_orders.id"), nullable=False, index=True)

    event_type = db.Column(db.String(40), nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.String(36), primary_key=True, default=uuid_str)
    ro_id = db.Column(db.String(36), db.ForeignKey("repair_orders.id"), nullable=False, index=True)

    doc_type = db.Column(db.String(20), nullable=False)  # estimate/invoice
    version = db.Column(db.Integer, nullable=False, default=1)

    status = db.Column(db.String(20), nullable=False, default="draft")  # draft/sent/approved/declined/locked/paid
    share_token = db.Column(db.String(64), unique=True, nullable=True)

    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    tax = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    locked_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("ro_id", "doc_type", "version", name="uq_doc_ro_type_version"),
        db.Index("ix_doc_ro_type_status", "ro_id", "doc_type", "status"),
    )

class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.String(36), primary_key=True, default=uuid_str)
    ro_id = db.Column(db.String(36), db.ForeignKey("repair_orders.id"), nullable=False, index=True)
    tech_id = db.Column(db.String(36), db.ForeignKey("technicians.id"), nullable=True, index=True)

    title = db.Column(db.String(180), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="pending")  # pending/approved/work_in_progress/completed/declined
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    completed_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class LineItem(db.Model):
    __tablename__ = "line_items"
    id = db.Column(db.String(36), primary_key=True, default=uuid_str)

    document_id = db.Column(db.String(36), db.ForeignKey("documents.id"), nullable=False, index=True)
    job_id = db.Column(db.String(36), db.ForeignKey("jobs.id"), nullable=True, index=True)

    item_type = db.Column(db.String(20), nullable=False)  # labor/part/fee/discount
    description = db.Column(db.String(255), nullable=False)

    qty = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("1.00"))
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    taxable = db.Column(db.Boolean, nullable=False, default=False)

    labor_hours = db.Column(db.Numeric(10, 2), nullable=True)
    cost = db.Column(db.Numeric(10, 2), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.String(36), primary_key=True, default=uuid_str)
    ro_id = db.Column(db.String(36), db.ForeignKey("repair_orders.id"), nullable=False, index=True)

    title = db.Column(db.String(200), nullable=False)
    start_at = db.Column(db.DateTime, nullable=False, index=True)
    end_at = db.Column(db.DateTime, nullable=False, index=True)

    location = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Technician(db.Model):
    __tablename__ = "technicians"
    id = db.Column(db.String(36), primary_key=True, default=uuid_str)
    name = db.Column(db.String(120), nullable=False)
    total_hours = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# -----------------------------
# Matrix tables (Tekmetric-ish)
# -----------------------------

class LaborMatrixTier(db.Model):
    """
    Tiered labor rate based on labor hours.
    Example:
      0.00 - 1.00 hrs => 140/hr
      1.01 - 3.00 hrs => 130/hr
      3.01+ hrs      => 115/hr
    """
    __tablename__ = "labor_matrix_tiers"
    id = db.Column(db.String(36), primary_key=True, default=uuid_str)
    min_hours = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    max_hours = db.Column(db.Numeric(10, 2), nullable=True)  # NULL means infinity
    rate_per_hour = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class PartsMatrixTier(db.Model):
    """
    Tiered parts markup based on part cost (per unit).
    unit_price = cost * multiplier
    Example:
      $0 - $25 => x2.0
      $25.01 - $100 => x1.6
      $100.01+ => x1.35
    """
    __tablename__ = "parts_matrix_tiers"
    id = db.Column(db.String(36), primary_key=True, default=uuid_str)
    min_cost = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    max_cost = db.Column(db.Numeric(10, 2), nullable=True)  # NULL means infinity
    multiplier = db.Column(db.Numeric(10, 4), nullable=False, default=Decimal("1.0000"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
