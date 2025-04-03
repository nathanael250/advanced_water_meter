from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    flash,
    session,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from flask_migrate import Migrate
from flask import flash
from time import sleep
import logging
import math  # Add this import
import uuid
import base64
import requests
from datetime import datetime
from sqlalchemy import func

from sqlalchemy import func
from datetime import datetime, timedelta


import http.client
import urllib.parse


app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:@localhost/water_management"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key"  # Change this to a secure secret key
db = SQLAlchemy(app)

# Login Manager Setup
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Changed from 'admin_login' to 'login'
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "nathanaelniyogushimwa@gmail.com"
SMTP_PASSWORD = "gilo mrrg fxop embj"


# Add these constants to your configuration
MOMO_COLLECTIONS_PRIMARY_KEY = "0b6d6fa598c248fdbf0f0be435f42c35"
MOMO_COLLECTIONS_SECONDARY_KEY = "a66edefc7e8542e491de6b2626bb5625"
MOMO_DISBURSEMENT_PRIMARY_KEY = "6c1754bea0dd485a812aa065338dfc10"
MOMO_DISBURSEMENT_SECONDARY_KEY = "25738a16d3014a93aa5130c1adca7022"
# MTN MOMO API Configuration
API_USER_ID = "8339ed05-ea1a-4711-9afb-6af4113bbcd9"
MOMO_COLLECTIONS_PRIMARY_KEY = "a66edefc7e8542e491de6b2626bb5625"
API_KEY = "8befe5a7c7dd47599e95d2b20c04765a"
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSMjU2In0.eyJjbGllbnRJZCI6IjgzMzllZDA1LWVhMWEtNDcxMS05YWZiLTZhZjQxMTNiYmNkOSIsImV4cGlyZXMiOiIyMDI1LTAzLTEyVDE0OjMxOjIwLjA2NCIsInNlc3Npb25JZCI6ImZkYTBkYmY5LTRmZGEtNDM0Ny1iMzZjLTAyYzkxY2QwZWIyMCJ9.Qxlos7SbgfgNSFHNZ-coPZtQMDnQyWfi6-aabLCSJA9QmodxE4SUMMoAqBDAf4jSy3o49OtFJmoTrYGVIPEXIjAY5foEhczF-ocIZm4EbDZJ0qVmsX98gYW5XcjXI6GQcQzCDiop-0Tcy2Mvg4jTjSXoPoTqxUuShevc4yK2eZJYysu0fNCEBK6dQezoXr0YxoThPU-h4Wti72YbgJT2urJ9rIzVXz51mMu8sKAwhfvAN-pfAy59eo41HZesLynVlVeFLtyvcEaTbDf_zuWjYJEv2zCI8z6RQ3hHT09sL6NlkrdhKJ208tNdtrrBBcAu-jRNAZRAXsYSEMJmyp0tJw"
CALLBACK_URL = "https://webhook.site/080697c2-8fd1-4abb-b653-52509852a53e"


@app.template_filter("min")
def _jinja2_filter_min(value, other_value):
    return min(value, other_value)


def log_momo_response(response):
    """Log MOMO API response for debugging"""
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Body: {response.text}")


# Database Models
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    counter_id = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default="available")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_to = db.Column(db.String(50), nullable=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    id_card = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    counter_id = db.Column(db.String(50), unique=True, nullable=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    phone_number = db.Column(db.String(20), nullable=True)
    pushover_key = db.Column(db.String(30), nullable=True)
    credit_limit = db.Column(
        db.Float, default=1.0
    )  # Default credit limit in cubic meters
    balance = db.Column(db.Float, default=0.0)  # Add this field


class WaterUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    counter_id = db.Column(db.Integer, db.ForeignKey("counter.id"), nullable=False)
    usage_amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Update the Payment model
# Update the Payment model
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_ref = db.Column(db.String(100), unique=True)
    transaction_type = db.Column(
        db.String(20), default="payment"
    )  # 'payment' or 'recharge'

    user = db.relationship("User", backref="payments")


class ValveOperation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    operation = db.Column(db.String(20), nullable=False)  # 'open' or 'close'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(
        db.Integer, nullable=True
    )  # Duration in seconds if operation is 'close'

    user = db.relationship("User", backref="valve_operations")


class WaterLoan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Amount borrowed in cubic meters
    status = db.Column(db.String(20), default="active")  # active, repaid
    borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)
    repaid_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref="water_loans")


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="active")  # active, suspended, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_transaction = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref="account")


# Add this to your models section
class UserWaterBalance(db.Model):
    __tablename__ = "water_balance"  # Specify the table name explicitly
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    cubic_meters = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="water_balances")

    def __repr__(self):
        return f"<WaterBalance user_id={self.user_id} cubic_meters={self.cubic_meters}>"


@app.route("/user/account")
@login_required
def account_details():
    # Get user's account
    account = Account.query.filter_by(user_id=current_user.id).first()

    if not account:
        flash("Account not found", "error")
        return redirect(url_for("user_dashboard"))

    # Get recent transactions
    transactions = (
        Payment.query.filter_by(user_id=current_user.id)
        .order_by(Payment.timestamp.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "user/account_details.html", account=account, transactions=transactions
    )


@app.template_filter("number_format")
def number_format(value):
    if value is None:
        return "0.00"
    return "{:,.2f}".format(value)


@login_manager.user_loader
def load_user(user_id):
    # Try loading user first
    user = User.query.get(int(user_id))
    if user:
        return user
    # If not user, try loading admin
    return Admin.query.get(int(user_id))


# Admin Routes
@app.route("/create-admin", methods=["GET", "POST"])
def create_first_admin():
    admin = Admin(username="admin", password="admin123")
    db.session.add(admin)
    db.session.commit()
    return "Admin created successfully"


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.password == password:
            login_user(admin)
            return redirect(url_for("admin_dashboard"))

    return render_template("auth/login.html")


@app.route("/admin")
@login_required
def admin_dashboard():
    # Check if user is admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("index"))

    # Get total water meters
    total_meters = Counter.query.count()
    total_users = User.query.count()
    total_payments = Payment.query.count()
    total_loans = WaterLoan.query.count()

    # Get recent activities
    recent_usage = WaterUsage.query.order_by(WaterUsage.timestamp.desc()).limit(5).all()
    recent_payments = Payment.query.order_by(Payment.timestamp.desc()).limit(5).all()
    recent_loans = WaterLoan.query.order_by(WaterLoan.borrowed_at.desc()).limit(5).all()

    # Get statistics
    total_revenue = Payment.query.filter_by(status="success").with_entities(func.sum(Payment.amount)).scalar() or 0
    pending_payments = Payment.query.filter_by(status="pending").count()
    active_loans = WaterLoan.query.filter_by(status="active").count()

    # Calculate daily consumption (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    daily_usage = WaterUsage.query.filter(WaterUsage.timestamp >= yesterday).with_entities(func.sum(WaterUsage.usage_amount)).scalar() or 0
    daily_consumption = daily_usage * 1000  # Convert to liters

    # Calculate monthly revenue
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = Payment.query.filter(
        Payment.status == "success",
        Payment.timestamp >= first_day_of_month
    ).with_entities(func.sum(Payment.amount)).scalar() or 0

    # Calculate revenue growth
    last_month = first_day_of_month - timedelta(days=1)
    last_month_first_day = last_month.replace(day=1)
    last_month_revenue = Payment.query.filter(
        Payment.status == "success",
        Payment.timestamp >= last_month_first_day,
        Payment.timestamp < first_day_of_month
    ).with_entities(func.sum(Payment.amount)).scalar() or 0
    
    revenue_growth = 0
    if last_month_revenue > 0:
        revenue_growth = ((monthly_revenue - last_month_revenue) / last_month_revenue) * 100

    # Get active alerts
    active_alerts = []
    high_usage = WaterUsage.query.filter(WaterUsage.usage_amount > 1000).order_by(WaterUsage.timestamp.desc()).limit(5).all()
    for usage in high_usage:
        counter = Counter.query.get(usage.counter_id)
        if counter:
            active_alerts.append({
                "severity": "High",
                "severity_color": "red",
                "icon": '<svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
                "title": "High Water Usage",
                "details": f"Counter {counter.id} used {usage.usage_amount} m³"
            })

    # Prepare recent activities
    recent_activities = []
    for usage in recent_usage:
        counter = Counter.query.get(usage.counter_id)
        user = User.query.get(counter.user_id) if counter else None
        recent_activities.append({
            "type": "usage",
            "type_color": "blue",
            "icon": '<svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>',
            "title": "Water Usage Recorded",
            "details": f"Counter: {counter.id if counter else 'Unknown'} - User: {user.full_name if user else 'Unknown'} - {usage.usage_amount} m³",
            "timestamp": usage.timestamp
        })

    for payment in recent_payments:
        user = User.query.get(payment.user_id)
        recent_activities.append({
            "type": "payment",
            "type_color": "green",
            "icon": '<svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
            "title": "Payment Received",
            "details": f"{user.full_name} - RWF {payment.amount:,}",
            "timestamp": payment.timestamp
        })

    for loan in recent_loans:
        user = User.query.get(loan.user_id)
        recent_activities.append({
            "type": "loan",
            "type_color": "yellow",
            "icon": '<svg class="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
            "title": "Loan " + ("Repaid" if loan.status == "repaid" else "Borrowed"),
            "details": f"{user.full_name} - {loan.amount} m³",
            "timestamp": loan.repaid_at if loan.status == "repaid" else loan.borrowed_at
        })

    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)

    # Prepare consumption trend data (last 7 days)
    consumption_trend = []
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        daily_usage = WaterUsage.query.filter(
            WaterUsage.timestamp >= start_of_day,
            WaterUsage.timestamp < end_of_day
        ).with_entities(func.sum(WaterUsage.usage_amount)).scalar() or 0
        
        consumption_trend.append({
            "date": date.strftime("%Y-%m-%d"),
            "usage": float(daily_usage * 1000)  # Convert to liters
        })

    # Prepare revenue analysis data (last 6 months)
    revenue_analysis = []
    for i in range(5, -1, -1):
        date = datetime.utcnow() - timedelta(days=30*i)
        start_of_month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1)  # Get first day of next month
        
        monthly_revenue = Payment.query.filter(
            Payment.status == "success",
            Payment.timestamp >= start_of_month,
            Payment.timestamp < end_of_month
        ).with_entities(func.sum(Payment.amount)).scalar() or 0
        
        revenue_analysis.append({
            "month": date.strftime("%b %Y"),
            "revenue": float(monthly_revenue)
        })

    return render_template(
        "admin/dashboard.html",
        total_meters=total_meters,
        total_users=total_users,
        total_payments=total_payments,
        total_loans=total_loans,
        recent_activities=recent_activities,
        total_revenue=total_revenue,
        pending_payments=pending_payments,
        active_loans=active_loans,
        daily_consumption=daily_consumption,
        monthly_revenue=monthly_revenue,
        revenue_growth=revenue_growth,
        active_alerts=active_alerts,
        consumption_trend=consumption_trend,
        revenue_analysis=revenue_analysis
    )

@app.route("/admin/users")
@login_required
def admin_users():
    # Check if user is admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("index"))

    # Get filter parameters
    search = request.args.get("search", "")
    status = request.args.get("status", "")

    # Build query
    query = User.query

    # Apply filters
    if search:
        query = query.filter(
            db.or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.phone_number.ilike(f"%{search}%"),
                User.id_card.ilike(f"%{search}%")
            )
        )
    if status:
        query = query.filter(User.status == status)

    # Get paginated results
    page = request.args.get("page", 1, type=int)
    per_page = 20
    users = query.order_by(User.registration_date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template("admin/users.html", users=users, search=search, status=status)

@app.route("/admin/users/<int:user_id>/status", methods=["POST"])
@login_required
def update_user_status(user_id):
    # Check if user is admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        return jsonify({"success": False, "message": "Access denied"}), 403

    try:
        user = User.query.get_or_404(user_id)
        new_status = request.json.get("status")

        if not new_status:
            return jsonify({"success": False, "message": "Status is required"}), 400

        # Update user status
        user.status = new_status
        db.session.commit()

        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/admin/users/<int:user_id>/credit-limit", methods=["POST"])
@login_required
def update_credit_limit(user_id):
    # Check if user is admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        return jsonify({"success": False, "message": "Access denied"}), 403

    try:
        user = User.query.get_or_404(user_id)
        new_limit = request.json.get("credit_limit", type=float)

        if new_limit is None:
            return jsonify({"success": False, "message": "Credit limit is required"}), 400

        # Update credit limit
        user.credit_limit = new_limit
        db.session.commit()

        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/admin/activities")
@login_required
def admin_activities():
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        return redirect(url_for("dashboard"))

    # Get all activities
    activities = []
    
    # Add water usage activities
    water_usage = WaterUsage.query.order_by(WaterUsage.timestamp.desc()).all()
    for usage in water_usage:
        counter = Counter.query.get(usage.counter_id)
        user = User.query.get(counter.user_id) if counter else None
        activities.append({
            "type": "usage",
            "type_color": "blue",
            "icon": '<svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>',
            "title": "Water Usage Recorded",
            "details": f"Counter: {counter.id if counter else 'Unknown'} - User: {user.full_name if user else 'Unknown'} - {usage.usage_amount} m³",
            "timestamp": usage.timestamp
        })

    # Add payment activities
    payments = Payment.query.order_by(Payment.timestamp.desc()).all()
    for payment in payments:
        user = User.query.get(payment.user_id)
        activities.append({
            "type": "payment",
            "type_color": "green",
            "icon": '<svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
            "title": "Payment Received",
            "details": f"{user.full_name} - RWF {payment.amount:,}",
            "timestamp": payment.timestamp
        })

    # Add loan activities
    loans = WaterLoan.query.order_by(WaterLoan.borrowed_at.desc()).all()
    for loan in loans:
        user = User.query.get(loan.user_id)
        activities.append({
            "type": "loan",
            "type_color": "yellow",
            "icon": '<svg class="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
            "title": "Loan " + ("Repaid" if loan.status == "repaid" else "Borrowed"),
            "details": f"{user.full_name} - {loan.amount} m³",
            "timestamp": loan.repaid_at if loan.status == "repaid" else loan.borrowed_at
        })

    # Sort all activities by timestamp
    activities.sort(key=lambda x: x["timestamp"], reverse=True)

    return render_template("admin/activities.html", activities=activities)


@app.route("/admin/alerts")
@login_required
def admin_alerts():
    # Get all alerts with pagination
    page = request.args.get("page", 1, type=int)

    alerts = []

    # High usage alerts
    high_usage = (
        WaterUsage.query.filter(WaterUsage.usage_amount > 1000)
        .distinct(WaterUsage.counter_id)
        .all()
    )

    for usage in high_usage:
        alerts.append(
            {
                "severity": "Critical",
                "severity_color": "red",
                "title": "High Usage Alert",
                "details": f"Counter ID: {usage.counter_id}",
                "timestamp": usage.timestamp,
            }
        )

    # Low balance alerts
    low_balance_users = User.query.filter(User.balance < 1000).all()
    for user in low_balance_users:
        alerts.append(
            {
                "severity": "Warning",
                "severity_color": "yellow",
                "title": "Low Balance Alert",
                "details": f"User: {user.full_name}",
                "timestamp": datetime.now(),
            }
        )

    # Sort by severity and timestamp
    alerts.sort(key=lambda x: (x["severity"], x["timestamp"]), reverse=True)

    return render_template("admin/alerts.html", alerts=alerts)


def timeago(date):
    now = datetime.now()
    diff = now - date

    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days

    if days > 30:
        return date.strftime("%Y-%m-%d")
    elif days > 0:
        return f"{days} days ago"
    elif hours > 0:
        return f"{int(hours)} hours ago"
    elif minutes > 0:
        return f"{int(minutes)} minutes ago"
    else:
        return "just now"


# Register the filter
app.jinja_env.filters["timeago"] = timeago


@app.route("/admin/counters")
@login_required
def manage_counters():
    # Check if user is admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("index"))

    # Get all counters with their assignments and latest readings
    counters = Counter.query.all()
    for counter in counters:
        # Get assigned user if any
        if counter.assigned_to:
            user = User.query.filter_by(counter_id=counter.counter_id).first()
            counter.assigned_user = user
        else:
            counter.assigned_user = None

        # Get latest reading
        latest_reading = WaterUsage.query.filter_by(counter_id=counter.id).order_by(WaterUsage.timestamp.desc()).first()
        counter.latest_reading = latest_reading.usage_amount if latest_reading else None
        counter.last_reading_time = latest_reading.timestamp if latest_reading else None

        # Determine status
        if not counter.assigned_to:
            counter.display_status = "Unassigned"
        elif counter.status == "active":
            counter.display_status = "Active"
        else:
            counter.display_status = "Inactive"

    return render_template("admin/counters.html", counters=counters)


@app.route("/admin/water-usage")
@login_required
def water_usage_page():
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        return redirect(url_for("dashboard"))

    # Get water usage data
    usage_data = WaterUsage.query.order_by(WaterUsage.timestamp.desc()).all()
    return render_template("admin/water_usage.html", usage_data=usage_data)


@app.route("/admin/billing")
@login_required
def billing():
    # Check if user is admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("index"))

    # Get filter parameters
    user_id = request.args.get("user_id", type=int)
    status = request.args.get("status")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    # Build query
    query = Payment.query.join(User).order_by(Payment.timestamp.desc())

    # Apply filters
    if user_id:
        query = query.filter(Payment.user_id == user_id)
    if status:
        query = query.filter(Payment.status == status)
    if date_from:
        query = query.filter(Payment.timestamp >= datetime.strptime(date_from, "%Y-%m-%d"))
    if date_to:
        query = query.filter(Payment.timestamp <= datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1))

    # Get paginated results
    page = request.args.get("page", 1, type=int)
    per_page = 20
    payments = query.paginate(page=page, per_page=per_page, error_out=False)

    # Calculate statistics
    total_revenue = Payment.query.filter_by(status="success").with_entities(func.sum(Payment.amount)).scalar() or 0
    pending_count = Payment.query.filter_by(status="pending").count()
    pending_amount = Payment.query.filter_by(status="pending").with_entities(func.sum(Payment.amount)).scalar() or 0

    # Get all users for the filter dropdown
    users = User.query.order_by(User.full_name).all()

    return render_template(
        "admin/billing.html",
        payments=payments,
        users=users,
        total_revenue=total_revenue,
        pending_count=pending_count,
        pending_amount=pending_amount,
    )

@app.route("/admin/payments/add", methods=["POST"])
@login_required
def add_payment():
    # Check if user is admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        return jsonify({"success": False, "message": "Access denied"}), 403

    try:
        user_id = request.form.get("user_id", type=int)
        amount = request.form.get("amount", type=float)
        status = request.form.get("status")

        if not all([user_id, amount, status]):
            flash("Missing required fields", "error")
            return redirect(url_for("billing"))

        # Create new payment
        payment = Payment(
            user_id=user_id,
            amount=amount,
            status=status,
            timestamp=datetime.utcnow(),
        )
        db.session.add(payment)
        db.session.commit()

        # If payment is successful, update user's balance
        if status == "success":
            user = User.query.get(user_id)
            if user:
                user.balance += amount
                db.session.commit()

                # Send notification if user has Pushover configured
                if user.pushover_key:
                    send_pushover_notification(
                        user.pushover_key,
                        "Payment Received",
                        f"Your account has been credited with RWF {amount:,.2f}. New balance: RWF {user.balance:,.2f}",
                    )

        flash("Payment added successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding payment: {str(e)}", "error")

    return redirect(url_for("billing"))

@app.route("/admin/payments/<int:payment_id>/status", methods=["POST"])
@login_required
def update_payment_status(payment_id):
    # Check if user is admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        return jsonify({"success": False, "message": "Access denied"}), 403

    try:
        payment = Payment.query.get_or_404(payment_id)
        new_status = request.json.get("status")

        if not new_status:
            return jsonify({"success": False, "message": "Status is required"}), 400

        # Update payment status
        payment.status = new_status
        db.session.commit()

        # If payment is marked as successful, update user's balance
        if new_status == "success" and payment.status != "success":
            user = payment.user
            user.balance += payment.amount
            db.session.commit()

            # Send notification if user has Pushover configured
            if user.pushover_key:
                send_pushover_notification(
                    user.pushover_key,
                    "Payment Received",
                    f"Your account has been credited with RWF {payment.amount:,.2f}. New balance: RWF {user.balance:,.2f}",
                )

        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/admin/view-invoice/<int:invoice_id>")
@login_required
def admin_view_invoice(invoice_id):
    payment = Payment.query.get_or_404(invoice_id)
    user = User.query.get(payment.user_id)

    return render_template("admin/view_invoice.html", payment=payment, user=user)


@app.route("/admin/generate-invoice", methods=["GET", "POST"])
@login_required
def admin_generate_invoice():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        amount = request.form.get("amount")

        # Create new payment record
        new_payment = Payment(user_id=user_id, amount=amount, status="pending")
        db.session.add(new_payment)
        db.session.commit()

        flash("Invoice generated successfully", "success")
        return redirect(url_for("admin_billing"))

    users = User.query.all()
    return render_template("admin/generate_invoice.html", users=users)


@app.route("/admin/settings")
@login_required
def admin_settings():
    return render_template("admin/settings.html")


# User Routes
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        username = request.form.get("username")
        password = request.form.get("password")

        if role == "admin":
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.password == password:
                login_user(admin)
                return redirect(url_for("admin_dashboard"))

        elif role == "user":
            user = User.query.filter_by(email=username).first()
            if user and user.password == password:
                login_user(user)
                # Check if user has a counter
                if user.counter_id:
                    return redirect(url_for("user_dashboard"))
                else:
                    return redirect(url_for("register_counter"))

        flash("Invalid credentials or role selection", "error")

    return render_template("auth/login.html")


def initialize_water_balance(user_id):
    """Initialize water balance for a new user"""
    try:
        # Check if balance already exists
        existing = UserWaterBalance.query.filter_by(user_id=user_id).first()
        if not existing:
            # Create new water balance
            water_balance = UserWaterBalance(
                user_id=user_id,
                cubic_meters=0.0
            )
            db.session.add(water_balance)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing water balance: {str(e)}")


@app.route("/register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        id_card = request.form.get("id_card")
        email = request.form.get("email")
        password = request.form.get("password")
        phone_number = request.form.get("phone_number")

        # Format phone number
        if not phone_number.startswith("+250"):
            phone_number = "+250" + phone_number.lstrip("0")

        new_user = User(
            full_name=full_name,
            id_card=id_card,
            email=email,
            password=password,
            phone_number=phone_number
        )
        db.session.add(new_user)
        db.session.commit()

        # Generate a unique account number
        account_number = f"WM{new_user.id:06d}"

        # Create a new account
        new_account = Account(
            user_id=new_user.id,
            account_number=account_number,
            balance=0.0,
            status="active",
        )
        db.session.add(new_account)
        db.session.commit()

        # Initialize water balance for the new user
        initialize_water_balance(new_user.id)

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("auth/register.html")


@app.route("/user/register-counter", methods=["GET", "POST"])
@login_required
def register_counter():
    # Check if logged in user is a regular user, not an admin
    if not isinstance(current_user, User):
        return redirect(url_for("login"))

    if request.method == "POST":
        counter_id = request.form.get("counter_id")

        counter = Counter.query.filter_by(
            counter_id=counter_id, status="available"
        ).first()

        if counter:
            counter.status = "assigned"
            counter.assigned_to = current_user.id_card
            current_user.counter_id = counter_id
            db.session.commit()
            flash("Counter registered successfully!", "success")
            return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid counter ID or counter already assigned", "error")

    return render_template("user/register_counter.html")


@app.route("/api/register-counter", methods=["POST"])
def register_counter_api():
    """
    API endpoint for NodeMCU to register its counter ID
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        counter_id_str = data.get("counter_id")

        print(f"Registering counter: User {user_id}, Counter {counter_id_str}")

        if not user_id or not counter_id_str:
            return jsonify({"error": "Missing required parameters"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check if counter already exists
        counter = Counter.query.filter_by(counter_id=counter_id_str).first()
        if not counter:
            # Create new counter
            counter = Counter(
                counter_id=counter_id_str,
                status="assigned",
                assigned_to=user.id_card if user.id_card else str(user.id),
            )
            db.session.add(counter)
        else:
            # Update existing counter
            counter.status = "assigned"
            counter.assigned_to = user.id_card if user.id_card else str(user.id)

        # Update user's counter ID
        user.counter_id = counter_id_str

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Counter {counter_id_str} registered to user {user_id}",
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        print(f"Error registering counter: {str(e)}")
        return jsonify({"error": str(e)}), 500


PUSHOVER_APP_TOKEN = (
    "ajfn3rd674i467u6zoxj6chnjuyqay"  # Replace with your actual Pushover app token
)
PUSHOVER_USER_KEY = (
    "uzhqpkbpoxo4rce9o5zt42tef57u2g"  # Replace with your default user key (optional)
)


def send_pushover_notification(user_key, title, message, priority=0):
    """
    Send a notification using Pushover API

    Args:
        user_key (str): The user's Pushover key
        title (str): Notification title
        message (str): Notification message
        priority (int): Priority level (-2 to 2)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request(
            "POST",
            "/1/messages.json",
            urllib.parse.urlencode(
                {
                    "token": PUSHOVER_APP_TOKEN,
                    "user": user_key,
                    "title": title,
                    "message": message,
                    "priority": priority,
                    "sound": "pushover",
                }
            ),
            {"Content-type": "application/x-www-form-urlencoded"},
        )
        response = conn.getresponse()
        result = response.read()
        conn.close()

        logger.info(f"Pushover notification sent to {user_key}: {result}")
        return response.status == 200
    except Exception as e:
        logger.error(f"Failed to send Pushover notification: {str(e)}")
        return False


class WaterBalance:
    def __init__(self, cubic_meters=0.0, status="active"):
        self.cubic_meters = cubic_meters
        self.status = status


@app.route("/user/dashboard")
@login_required
def user_dashboard():
    today = datetime.now().date()

    # Get usage statistics using a single query
    usage_stats = (
        db.session.query(
            func.sum(WaterUsage.usage_amount).label("today_usage"),
            func.count(WaterUsage.id).label("reading_count"),
        )
        .filter(
            WaterUsage.counter_id == current_user.counter_id,
            func.date(WaterUsage.timestamp) == today,
        )
        .first()
    )

    today_usage = usage_stats.today_usage or 0

    # Get yesterday's stats
    yesterday = today - timedelta(days=1)
    yesterday_usage = (
        WaterUsage.query.filter(
            WaterUsage.counter_id == current_user.counter_id,
            func.date(WaterUsage.timestamp) == yesterday,
        )
        .with_entities(func.sum(WaterUsage.usage_amount))
        .scalar()
        or 0
    )

    usage_change = (
        ((today_usage - yesterday_usage) / yesterday_usage * 100)
        if yesterday_usage > 0
        else 0
    )

    # Get the latest valve operation
    latest_valve_op = (
        ValveOperation.query.filter_by(user_id=current_user.id)
        .order_by(ValveOperation.timestamp.desc())
        .first()
    )

    valve_status = latest_valve_op.operation if latest_valve_op else "closed"

    # Get water balance with improved error handling
    try:
        water_balance = UserWaterBalance.query.filter_by(user_id=current_user.id).first()
        if water_balance:
            remaining_cubic_meters = float(water_balance.cubic_meters)
            if math.isnan(remaining_cubic_meters):
                remaining_cubic_meters = 0.0
        else:
            # If no balance record exists, create one with 0 balance
            water_balance = UserWaterBalance(user_id=current_user.id, cubic_meters=0.0)
            db.session.add(water_balance)
            db.session.commit()
            remaining_cubic_meters = 0.0
    except Exception as e:
        print(f"Error getting water balance: {str(e)}")
        remaining_cubic_meters = 0.0

    # Ensure remaining_cubic_meters is a valid number
    if not isinstance(remaining_cubic_meters, (int, float)) or math.isnan(remaining_cubic_meters):
        remaining_cubic_meters = 0.0

    # Get billing information with payment status
    # Get billing information with payment status
    current_bill = (
        db.session.query(Payment.id, Payment.amount, Payment.timestamp, Payment.status)
        .filter(
            Payment.user_id == current_user.id,
            Payment.status.in_(["pending", "processing"]),
        )
        .order_by(Payment.timestamp.desc())
        .first()
    )

    # Generate weekly usage data efficiently
    weekly_data = (
        db.session.query(
            func.date(WaterUsage.timestamp).label("date"),
            func.sum(WaterUsage.usage_amount).label("usage"),
        )
        .filter(
            WaterUsage.counter_id == current_user.counter_id,
            WaterUsage.timestamp >= today - timedelta(days=6),
        )
        .group_by(func.date(WaterUsage.timestamp))
        .all()
    )

    weekly_usage = []
    labels = []

    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        usage = next((data.usage for data in weekly_data if data.date == date), 0)
        weekly_usage.append(usage)
        labels.append(date.strftime("%a"))

    # Get recent activities with user details
    recent_usages = (
        db.session.query(WaterUsage.usage_amount, WaterUsage.timestamp)
        .filter(WaterUsage.counter_id == current_user.counter_id)
        .order_by(WaterUsage.timestamp.desc())
        .limit(5)
        .all()
    )

    recent_payments = (
        db.session.query(Payment.amount, Payment.status, Payment.timestamp)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.timestamp.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "user/dashboard.html",
        today_usage=today_usage,
        usage_change=round(usage_change, 1),
        current_bill=current_bill,
        weekly_usage=weekly_usage,
        chart_labels=labels,
        recent_usages=recent_usages,
        recent_payments=recent_payments,
        reading_count=usage_stats.reading_count,
        valve_status=valve_status,
        remaining_cubic_meters=remaining_cubic_meters,
    )


# Add this constant at the top of your file
FLOW_RATE = 0.2  # Liters per second (adjust based on your solenoid specifications)


@app.template_filter("number_format")
def number_format(value):
    if value is None or math.isnan(value):
        return "0.00"
    return "{:,.2f}".format(float(value))


@app.route("/user/consumption")
@login_required
def consumption():
    # Get today's usage data
    today = datetime.now().date()

    # Find the counter ID first
    counter = None
    if current_user.counter_id:
        counter = Counter.query.filter_by(counter_id=current_user.counter_id).first()

    if not counter:
        flash(
            "No water meter found for your account. Please register a counter first.",
            "warning",
        )
        return redirect(url_for("register_counter"))

    # Get today's usage with proper counter ID
    today_usage = (
        WaterUsage.query.filter(
            WaterUsage.counter_id
            == counter.id,  # Use the counter.id, not counter_id string
            func.date(WaterUsage.timestamp) == today,
        )
        .order_by(WaterUsage.timestamp)
        .all()
    )

    # Get water balance with improved error handling
    try:
        water_balance = UserWaterBalance.query.filter_by(user_id=current_user.id).first()
        if water_balance:
            remaining_cubic_meters = float(water_balance.cubic_meters)
            if math.isnan(remaining_cubic_meters):
                remaining_cubic_meters = 0.0
        else:
            # If no balance record exists, create one with 0 balance
            water_balance = UserWaterBalance(user_id=current_user.id, cubic_meters=0.0)
            db.session.add(water_balance)
            db.session.commit()
            remaining_cubic_meters = 0.0
    except Exception as e:
        print(f"Error getting water balance: {str(e)}")
        remaining_cubic_meters = 0.0

    # Ensure remaining_cubic_meters is a valid number
    if not isinstance(remaining_cubic_meters, (int, float)) or math.isnan(remaining_cubic_meters):
        remaining_cubic_meters = 0.0

    # Get usage history for the past 30 days
    past_30_days = datetime.now() - timedelta(days=30)
    usage_history = (
        WaterUsage.query.filter(
            WaterUsage.counter_id == counter.id,  # Use counter.id
            WaterUsage.timestamp >= past_30_days,
        )
        .order_by(WaterUsage.timestamp.desc())
        .all()
    )

    # Calculate daily usage statistics
    daily_usage = (
        db.session.query(
            func.date(WaterUsage.timestamp).label("date"),
            func.sum(WaterUsage.usage_amount).label("total_usage"),
            func.count(WaterUsage.id).label("count"),
        )
        .filter(
            WaterUsage.counter_id == counter.id,  # Use counter.id
            WaterUsage.timestamp >= past_30_days,
        )
        .group_by(func.date(WaterUsage.timestamp))
        .order_by(func.date(WaterUsage.timestamp).desc())
        .all()
    )

    # Calculate average daily usage with error handling
    try:
        total_usage = sum(
            float(day.total_usage) for day in daily_usage if day.total_usage is not None
        )
        avg_daily_usage = total_usage / len(daily_usage) if daily_usage else 0
    except Exception as e:
        print(f"Error calculating average daily usage: {str(e)}")
        total_usage = 0
        avg_daily_usage = 0

    # Calculate monthly usage trend
    monthly_trend = []
    current_date = datetime.now().date()

    # Get data for the last 6 months
    for i in range(5, -1, -1):
        month_start = current_date.replace(day=1) - timedelta(days=30 * i)
        month_end = (
            (current_date.replace(day=1) - timedelta(days=30 * (i - 1)))
            if i > 0
            else current_date
        )

        try:
            month_usage = (
                WaterUsage.query.filter(
                    WaterUsage.counter_id == counter.id,  # Use counter.id
                    WaterUsage.timestamp >= month_start,
                    WaterUsage.timestamp < month_end,
                )
                .with_entities(func.sum(WaterUsage.usage_amount))
                .scalar()
                or 0
            )

            monthly_trend.append(
                {
                    "month": month_start.strftime("%b %Y"),
                    "usage": float(month_usage) if month_usage is not None else 0.0,
                }
            )
        except Exception as e:
            print(f"Error calculating monthly trend for {month_start}: {str(e)}")
            monthly_trend.append({"month": month_start.strftime("%b %Y"), "usage": 0.0})

    # Get peak usage times
    try:
        hour_usage = (
            db.session.query(
                func.extract("hour", WaterUsage.timestamp).label("hour"),
                func.sum(WaterUsage.usage_amount).label("total_usage"),
            )
            .filter(
                WaterUsage.counter_id == counter.id,  # Use counter.id
                WaterUsage.timestamp >= past_30_days,
            )
            .group_by(func.extract("hour", WaterUsage.timestamp))
            .order_by(func.sum(WaterUsage.usage_amount).desc())
            .limit(3)
            .all()
        )

        peak_hours = [
            {
                "hour": f"{int(h.hour)}:00",
                "usage": float(h.total_usage) if h.total_usage is not None else 0.0,
            }
            for h in hour_usage
        ]
    except Exception as e:
        print(f"Error calculating peak hours: {str(e)}")
        peak_hours = []

    # Format data for chart
    usage_data = [
        {
            "timestamp": usage.timestamp,
            "amount": (
                float(usage.usage_amount) if usage.usage_amount is not None else 0.0
            ),
        }
        for usage in today_usage
    ]

    # Get recent payments to calculate cost
    recent_payments = (
        Payment.query.filter_by(
            user_id=current_user.id, status="success", transaction_type="payment"
        )
        .order_by(Payment.timestamp.desc())
        .limit(5)
        .all()
    )

    # Calculate cost per cubic meter (based on recent payments)
    try:
        total_payment = sum(
            float(payment.amount)
            for payment in recent_payments
            if payment.amount is not None
        )
        total_cubic_meters = total_payment / 1000.0  # Assuming 1000 RWF per cubic meter
    except Exception as e:
        print(f"Error calculating total payment: {str(e)}")
        total_payment = 0
        total_cubic_meters = 0

    # Calculate estimated monthly cost based on current usage pattern
    try:
        estimated_monthly_usage = avg_daily_usage * 30.0
        estimated_monthly_cost = (
            estimated_monthly_usage * 1000.0
        )  # 1000 RWF per cubic meter
    except Exception as e:
        print(f"Error calculating estimated costs: {str(e)}")
        estimated_monthly_usage = 0
        estimated_monthly_cost = 0

    formatted_daily_usage = []
    for day in daily_usage:
        formatted_date = (
            day.date.strftime("%a, %b %d") if hasattr(day, "date") and day.date else ""
        )
        formatted_daily_usage.append(
            {"date": formatted_date, "total_usage": day.total_usage, "count": day.count}
        )

    return render_template(
        "user/consumption.html",
        remaining_cubic_meters=remaining_cubic_meters,
        usage_history=usage_history,
        usage_data=usage_data,
        daily_usage=formatted_daily_usage,
        avg_daily_usage=avg_daily_usage,
        monthly_trend=monthly_trend,
        peak_hours=peak_hours,
        estimated_monthly_usage=estimated_monthly_usage,
        estimated_monthly_cost=estimated_monthly_cost,
    )


@app.route("/user/settings")
def user_settings():
    return render_template("user/settings.html")


@app.route("/user/support")
def support():
    return render_template("user/support.html")


@app.route("/user/report")
def user_report():
    return render_template("user/report.html")


@app.route('/user/payment', methods=['GET', 'POST'])
@login_required
def payment():
    # Get user's account
    account = Account.query.filter_by(user_id=current_user.id).first()
    
    if not account:
        flash('You need to activate your account first', 'warning')
        return redirect(url_for('activate_account'))
    
    # Calculate current water balance from all successful payments minus usage
    total_payments = Payment.query.filter_by(
        user_id=current_user.id, 
        status='success',
        transaction_type='payment'
    ).with_entities(func.sum(Payment.amount)).scalar() or 0
    
    # Convert total payments to cubic meters
    total_cubic_meters = total_payments / 1000  # Assuming 1000 RWF = 1 cubic meter
    
    # Get total water usage
    total_usage = 0
    if current_user.counter_id:
        total_usage = WaterUsage.query.filter_by(
            counter_id=current_user.counter_id
        ).with_entities(func.sum(WaterUsage.usage_amount)).scalar() or 0
    
    # Calculate current water balance
    current_water_balance = max(0, total_cubic_meters - total_usage)
    
    # Debug logging
    logger.info(f"User {current_user.id} water balance calculation:")
    logger.info(f"Total payments: {total_payments} RWF = {total_cubic_meters} cubic meters")
    logger.info(f"Total usage: {total_usage} cubic meters")
    logger.info(f"Current water balance: {current_water_balance} cubic meters")
    
    # Get existing payments for display
    payments = Payment.query.filter_by(
        user_id=current_user.id,
        transaction_type='payment'
    ).order_by(Payment.timestamp.desc()).limit(5).all()
    
    # Handle new payment submission
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        
        # Check if user has sufficient balance
        if account.balance < amount:
            flash(f'Insufficient balance. Your current balance is RWF {account.balance:,.2f} but you attempted to pay RWF {amount:,.2f}', 'error')
            
            # Send notification about insufficient balance if user has Pushover key
            if current_user.pushover_key:
                send_pushover_notification(
                    current_user.pushover_key,
                    "Payment Failed - Insufficient Balance",
                    f"Your payment of RWF {amount:,.2f} could not be processed because your balance is only RWF {account.balance:,.2f}. Please recharge your account."
                )
            
            return redirect(url_for('payment'))
        
        # Generate a transaction reference
        transaction_ref = str(uuid.uuid4())
        
        try:
            # Create a new payment record
            new_payment = Payment(
                user_id=current_user.id,
                amount=amount,
                status='success',
                transaction_ref=transaction_ref,
                transaction_type='payment'
            )
            db.session.add(new_payment)
            
            # Deduct from account balance
            account.balance -= amount
            account.last_transaction = datetime.now()
            
            # Check for active loan
            active_loan = WaterLoan.query.filter_by(
                user_id=current_user.id,
                status='active'
            ).first()
            
            # Calculate loan amount in RWF
            loan_amount_rwf = 0
            if active_loan:
                loan_amount_rwf = active_loan.amount * 1000  # Convert cubic meters to RWF
            
            # First pay off the loan if there is one
            remaining_amount = amount
            if active_loan and loan_amount_rwf > 0:
                if amount >= loan_amount_rwf:
                    # Pay off the entire loan
                    active_loan.status = 'repaid'
                    active_loan.repaid_at = datetime.now()
                    remaining_amount = amount - loan_amount_rwf
                    logger.info(f"User {current_user.id} repaid their loan of {active_loan.amount} cubic meters")
                else:
                    # Partial loan repayment
                    remaining_loan = active_loan.amount - (amount / 1000)  # Convert RWF to cubic meters
                    active_loan.amount = remaining_loan
                    remaining_amount = 0
                    logger.info(f"User {current_user.id} made partial loan repayment. Remaining loan: {remaining_loan} cubic meters")
            
            # Update water balance with remaining amount
            if remaining_amount > 0:
                water_balance = UserWaterBalance.query.filter_by(user_id=current_user.id).first()
                if not water_balance:
                    water_balance = UserWaterBalance(user_id=current_user.id, cubic_meters=0)
                    db.session.add(water_balance)
                
                # Add the remaining amount to water balance (converting RWF to cubic meters)
                water_balance.cubic_meters += (remaining_amount / 1000)
                water_balance.last_updated = datetime.now()
                
                logger.info(f"Added {remaining_amount / 1000} cubic meters to water balance")
            
            # Commit the changes
            db.session.commit()
            
            # Log the successful payment
            logger.info(f"User {current_user.id} made a payment of {amount} RWF")
            if remaining_amount > 0:
                logger.info(f"New water balance: {water_balance.cubic_meters} cubic meters")
            
            # Send success notification
            if current_user.pushover_key:
                message = f"Your payment of RWF {amount:,.2f} was successful."
                if active_loan:
                    if amount >= loan_amount_rwf:
                        message += f" Your loan of {active_loan.amount} cubic meters has been fully repaid."
                    else:
                        message += f" Part of your payment was used to repay your loan. Remaining loan: {active_loan.amount} cubic meters."
                if remaining_amount > 0:
                    message += f" Added {remaining_amount / 1000} cubic meters to your water balance."
                
                send_pushover_notification(current_user.pushover_key, "Payment Successful", message)
            
            flash('Payment successful!', 'success')
            return redirect(url_for('user_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Payment processing failed: {str(e)}")
            flash("Payment processing failed. Please try again.", 'error')
    
    # Create a simple object to mimic WaterBalance for the template
    class WaterBalanceObj:
        def __init__(self, cubic_meters):
            self.cubic_meters = cubic_meters
    
    water_balance = WaterBalanceObj(current_water_balance)
    
    return render_template('user/payment.html',
                          account=account,
                          payments=payments,
                          water_balance=water_balance)


@app.route("/api/check-payment-status/<payment_id>")
@login_required
def check_payment_status(payment_id):
    payment = Payment.query.get_or_404(payment_id)

    # For development: simulate payment processing
    # In production, this would check with the payment provider
    if payment.status == "pending":
        # Simulate a successful payment (for testing purposes)
        payment.status = "success"
        db.session.commit()
        return jsonify({"status": "success"})

    # Return the current status
    return jsonify({"status": payment.status})


@app.route("/user/confirm-payment/<int:payment_id>")
@login_required
def confirm_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)

    # For development: automatically mark payment as successful after 5 seconds
    # In production, this would be handled by a webhook from the payment provider
    if payment.status == "pending":
        payment.status = "success"
        db.session.commit()

        # Send notification to the specific user who made the payment
        user = User.query.get(payment.user_id)
        if user and user.pushover_key:
            notification_sent = send_pushover_notification(
                user.pushover_key,
                "Payment Successful",
                f"Your payment of RWF {payment.amount:,.2f} was successful. Thank you for using our service!",
            )
            if notification_sent:
                flash(
                    "Payment successful! A notification has been sent to your device.",
                    "success",
                )
            else:
                flash(
                    "Payment successful! However, we could not send a notification to your device.",
                    "warning",
                )
        else:
            flash("Payment successful!", "success")

    return render_template("user/confirm_payment.html", payment=payment)


# API Endpoints
@app.route("/api/receive-data", methods=["POST"])
def receive_data():
    data = request.json
    user_id = data.get("user_id")
    usage = data.get("usage")

    if user_id and usage:
        new_usage = WaterUsage(user_id=user_id, usage_amount=usage)
        db.session.add(new_usage)
        db.session.commit()
        return jsonify({"message": "Data saved successfully"}), 200
    return jsonify({"error": "Invalid data"}), 400


@app.route("/api/water-usage", methods=["GET"])
def get_data():
    usages = WaterUsage.query.all()
    return jsonify(
        [
            {
                "user_id": usage.user_id,
                "usage_amount": usage.usage_amount,
                "timestamp": usage.timestamp,
            }
            for usage in usages
        ]
    )


@app.route("/api/verify-counter", methods=["POST"])
def verify_counter():
    counter_id = request.form.get("counter_id")
    id_card = request.form.get("id_card")

    if verify_counter_ownership(counter_id, id_card):
        return jsonify(
            {"status": "verified", "message": "Counter verified successfully"}
        )
    return jsonify({"status": "error", "message": "Invalid counter or ID card"})


@app.route("/api/send-notification", methods=["POST"])
def send_email():
    data = request.json
    subject = data.get("event")
    body = data.get("details")

    if subject and body:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = SMTP_USERNAME
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            return jsonify({"message": "Email sent successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Missing event or details"}), 400


# Helper Functions
def verify_counter_ownership(counter_id, id_card):
    with open("counters_data.json", "r") as file:
        data = json.load(file)
        for counter in data["counters"]:
            if counter["counter_id"] == counter_id and counter["owner_id"] == id_card:
                return True
    return False


@app.route("/user/logout")
@login_required
def user_logout():
    logout_user()
    return redirect(url_for("login"))  # Changed from user_login to login


@app.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/user/update-profile", methods=["POST"])
@login_required
def update_profile():
    current_user.full_name = request.form.get("full_name")
    current_user.email = request.form.get("email")
    db.session.commit()
    flash("Profile updated successfully", "success")
    return redirect(url_for("user_settings"))


@app.route("/user/update-notifications", methods=["POST"])
@login_required
def update_notifications():
    pushover_key = request.form.get("pushover_key")

    # Update the user's Pushover key
    current_user.pushover_key = pushover_key
    db.session.commit()

    # Send a test notification if a key was provided
    if pushover_key:
        success = send_pushover_notification(
            pushover_key,
            "Test Notification",
            "Your Smart Water Management notifications are now set up!",
        )
        if success:
            flash(
                "Notification settings updated and test notification sent!", "success"
            )
        else:
            flash(
                "Notification settings updated but test notification failed. Please check your Pushover key.",
                "warning",
            )
    else:
        flash("Notification settings updated", "success")

    return redirect(url_for("user_settings"))


@app.route("/user/change-password", methods=["POST"])
@login_required
def change_password():
    if request.form.get("new_password") == request.form.get("confirm_password"):
        current_user.password = request.form.get("new_password")
        db.session.commit()
        flash("Password changed successfully", "success")
    else:
        flash("Passwords do not match", "error")
    return redirect(url_for("user_settings"))


@app.route("/user/bills")
@login_required
def bills():
    # Get user's bills with pagination
    bills = (
        Payment.query.filter_by(user_id=current_user.id)
        .order_by(Payment.timestamp.desc())
        .all()
    )

    # Calculate summary statistics
    total_paid = sum(bill.amount for bill in bills if bill.status == "success")
    pending_amount = sum(bill.amount for bill in bills if bill.status == "pending")
    average_monthly = total_paid / 12 if total_paid > 0 else 0

    return render_template(
        "user/bills.html",
        bills=bills,
        total_paid=total_paid,
        pending_amount=pending_amount,
        average_monthly=average_monthly,
    )


def send_low_balance_alerts():
    """Check all users and send low balance alerts to those who need them"""
    threshold = 1000  # RWF

    # Find users who have Pushover keys configured
    users_with_notifications = User.query.filter(User.pushover_key.isnot(None)).all()

    for user in users_with_notifications:
        # Get the user's latest successful payment
        latest_payment = (
            Payment.query.filter_by(user_id=user.id, status="success")
            .order_by(Payment.timestamp.desc())
            .first()
        )

        if latest_payment:
            # Calculate remaining water based on payment amount
            remaining_water = (
                latest_payment.amount / 1000
            )  # Assuming 1000 RWF per cubic meter

            # Get total water usage since payment
            usage_since_payment = (
                WaterUsage.query.filter(
                    WaterUsage.counter_id == user.counter_id,
                    WaterUsage.timestamp > latest_payment.timestamp,
                )
                .with_entities(func.sum(WaterUsage.usage_amount))
                .scalar()
                or 0
            )

            # Calculate remaining balance
            remaining_balance = (remaining_water - usage_since_payment) * 1000

            if remaining_balance < threshold:
                send_pushover_notification(
                    user.pushover_key,
                    "Low Balance Alert",
                    f"Hello {user.full_name}, your water balance is running low (RWF {remaining_balance:,.2f}). Please top up soon to avoid service interruption.",
                )
                logger.info(
                    f"Low balance alert sent to user {user.id} ({user.full_name})"
                )


@app.route("/admin/send-notification", methods=["GET", "POST"])
@login_required
def admin_send_notification():
    # Check if the current user is an admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        return redirect(url_for("dashboard"))

    users = User.query.filter(User.pushover_key.isnot(None)).all()

    if request.method == "POST":
        user_id = request.form.get("user_id")
        title = request.form.get("title")
        message = request.form.get("message")
        send_to_all = request.form.get("send_to_all") == "on"

        if send_to_all:
            # Send to all users with Pushover keys
            success_count = 0
            for user in users:
                if send_pushover_notification(user.pushover_key, title, message):
                    success_count += 1

            flash(f"Notification sent to {success_count} users", "success")
        elif user_id:
            # Send to specific user
            user = User.query.get(user_id)
            if user and user.pushover_key:
                if send_pushover_notification(user.pushover_key, title, message):
                    flash(f"Notification sent to {user.full_name}", "success")
                else:
                    flash("Failed to send notification", "error")
            else:
                flash("User does not have notifications configured", "warning")

        return redirect(url_for("admin_send_notification"))

    return render_template("admin/send_notification.html", users=users)


# Add an API endpoint for AJAX valve control
@app.route("/api/valve-control", methods=["POST"])
@login_required
def api_valve_control():
    action = request.json.get("action")
    success = False
    message = "Invalid action"

    if action == "open":
        # Code to open the valve (in production, this would call your IoT API)
        success = True
        message = "Valve opened successfully"
    elif action == "close":
        # Code to close the valve (in production, this would call your IoT API)
        success = True
        message = "Valve closed successfully"

    # In a real implementation, you might want to log this action
    return jsonify({"success": success, "message": message, "status": action})


@app.route("/api/check-balance/<user_id>", methods=["GET"])
def check_balance(user_id):
    """
    API endpoint for NodeMCU to check user's remaining balance
    Returns remaining_turns based on the payment amount and cost per turn
    """
    try:
        # Log the request for debugging
        print(
            f"Balance check request for user_id: {user_id}, counter_id: {request.args.get('counter_id')}"
        )

        user = User.query.get(user_id)
        if not user:
            return (
                jsonify(
                    {
                        "error": "User not found",
                        "remaining_turns": 0,
                        "remaining_cubic_meters": 0,
                    }
                ),
                404,
            )

        # Get the user's water balance
        water_balance = UserWaterBalance.query.filter_by(user_id=user.id).first()

        if not water_balance:
            # Create a new water balance record if it doesn't exist
            water_balance = UserWaterBalance(user_id=user.id, cubic_meters=0.0)
            db.session.add(water_balance)
            db.session.commit()

        # Calculate remaining turns (assuming 1 cubic meter = 200 turns)
        remaining_turns = int(water_balance.cubic_meters * 200)

        return (
            jsonify(
                {
                    "remaining_turns": remaining_turns,
                    "remaining_cubic_meters": water_balance.cubic_meters,
                }
            ),
            200,
        )
    except Exception as e:
        print(f"Error in check_balance: {str(e)}")
        # Return a default response to prevent NodeMCU from getting stuck
        return (
            jsonify(
                {"error": str(e), "remaining_turns": 0, "remaining_cubic_meters": 0}
            ),
            500,
        )


@app.route('/user/valve-control', methods=['GET', 'POST'])
@login_required
def valve_control():
    # Get the current valve status from the latest operation
    latest_operation = ValveOperation.query.filter_by(user_id=current_user.id).order_by(ValveOperation.timestamp.desc()).first()
    valve_status = latest_operation.operation if latest_operation else 'closed'
    
    # Calculate current water balance from all successful payments minus usage
    total_payments = Payment.query.filter_by(
        user_id=current_user.id, 
        status='success',
        transaction_type='payment'
    ).with_entities(func.sum(Payment.amount)).scalar() or 0
    
    # Convert total payments to cubic meters
    total_cubic_meters = total_payments / 1000  # Assuming 1000 RWF = 1 cubic meter
    
    # Get total water usage
    total_usage = 0
    if current_user.counter_id:
        total_usage = WaterUsage.query.filter_by(
            counter_id=current_user.counter_id
        ).with_entities(func.sum(WaterUsage.usage_amount)).scalar() or 0
    
    # Calculate current water balance
    remaining_water = max(0, total_cubic_meters - total_usage)
    has_balance = remaining_water > 0
    
    # Debug logging
    logger.info(f"User {current_user.id} valve control:")
    logger.info(f"Total payments: {total_payments} RWF = {total_cubic_meters} cubic meters")
    logger.info(f"Total usage: {total_usage} cubic meters")
    logger.info(f"Current water balance: {remaining_water} cubic meters")
    logger.info(f"Has balance: {has_balance}")
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'open':
            if has_balance:
                # Record valve operation in database
                new_operation = ValveOperation(user_id=current_user.id, operation='open')
                db.session.add(new_operation)
                db.session.commit()
                
                valve_status = 'open'
                flash('Valve opened successfully. Water is now flowing.', 'success')
                
                # Send notification to the user
                if current_user.pushover_key:
                    send_pushover_notification(
                        current_user.pushover_key,
                        "Valve Opened",
                        f"Hello {current_user.full_name}, your water valve has been opened. Water is now flowing."
                    )
            else:
                flash('Insufficient balance to open valve. Please recharge your account.', 'error')
                
        elif action == 'close':
            # Record valve operation in database
            new_operation = ValveOperation(user_id=current_user.id, operation='close')
            db.session.add(new_operation)
            db.session.commit()
            
            valve_status = 'closed'
            flash('Valve closed successfully. Water flow has stopped.', 'success')
            
            # Send notification to the user
            if current_user.pushover_key:
                send_pushover_notification(
                    current_user.pushover_key,
                    "Valve Closed",
                    f"Hello {current_user.full_name}, your water valve has been closed. Water flow has stopped."
                )
        
        return redirect(url_for('valve_control'))
    
    # Get recent water usage
    recent_usage = WaterUsage.query.filter_by(
        counter_id=current_user.counter_id
    ).order_by(WaterUsage.timestamp.desc()).limit(5).all()
    
    return render_template('user/valve_control.html', 
                          valve_status=valve_status,
                          has_balance=has_balance,
                          remaining_water=remaining_water,
                          recent_usage=recent_usage)


@app.route("/api/update-valve/<user_id>", methods=["POST"])
def update_valve(user_id):
    """
    API endpoint to update valve status from web interface
    """
    data = request.json
    action = data.get("action")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if action not in ["open", "close"]:
        return jsonify({"error": "Invalid action"}), 400

    # In a real implementation, you would send a command to the NodeMCU
    # For now, we'll just return success

    # Log the action
    new_operation = ValveOperation(user_id=user.id, operation=action)
    db.session.add(new_operation)
    db.session.commit()

    return (
        jsonify(
            {"success": True, "message": f"Valve {action} command sent successfully"}
        ),
        200,
    )


@app.route("/api/record-usage", methods=["POST"])
def record_usage():
    """
    API endpoint for NodeMCU to record water usage
    Expects: user_id, usage_amount (in cubic meters)
    """
    data = request.json
    user_id = data.get("user_id")
    usage_amount = data.get("usage_amount")

    if not user_id or not usage_amount:
        return jsonify({"error": "Missing required parameters"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Create a new water usage record
    try:
        new_usage = WaterUsage(
            counter_id=user.counter_id, usage_amount=float(usage_amount)
        )
        db.session.add(new_usage)

        # Deduct from water balance
        water_balance = WaterBalance.query.filter_by(user_id=user.id).first()
        if water_balance:
            water_balance.cubic_meters = max(
                0, water_balance.cubic_meters - float(usage_amount)
            )
            water_balance.last_updated = datetime.utcnow()

        db.session.commit()

        # Send notification if usage is high
        if (
            float(usage_amount) > 0.5 and user.pushover_key
        ):  # 0.5 cubic meters threshold
            send_pushover_notification(
                user.pushover_key,
                "High Water Usage Alert",
                f"Hello {user.full_name}, we detected high water usage of {usage_amount} cubic meters. Please check for leaks.",
            )

        return jsonify({"success": True, "message": "Usage recorded successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/check-payment/<user_id>", methods=["GET"])
def check_payment(user_id):
    """
    API endpoint for NodeMCU to check for new payments
    Returns amount_paid in RWF if a new payment is found
    """
    try:
        counter_id = request.args.get("counter_id")

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # If counter_id is provided, verify it matches the user's counter
        if counter_id and user.counter_id != counter_id:
            print(
                f"Warning: Counter ID mismatch. User has {user.counter_id}, device sent {counter_id}"
            )
            # Optionally update the user's counter_id
            user.counter_id = counter_id
            db.session.commit()
            print(f"Updated user {user_id} to use counter {counter_id}")

        # Get the latest pending payment
        latest_payment = (
            Payment.query.filter_by(user_id=user.id, status="pending")
            .order_by(Payment.timestamp.desc())
            .first()
        )

        if not latest_payment:
            return jsonify({"amount_paid": 0}), 200

        # Mark the payment as processed
        latest_payment.status = "success"
        db.session.commit()

        return jsonify({"amount_paid": latest_payment.amount}), 200
    except Exception as e:
        print(f"Error checking payment: {str(e)}")
        return (
            jsonify({"error": str(e)}),
            500,
        )  # The send-notification endpoint is already implemented in your code


# But let's enhance it to work better with the NodeMCU


@app.route("/api/valve-status/<user_id>", methods=["POST"])
def update_valve_status(user_id):
    """
    API endpoint to update valve status from NodeMCU
    """
    try:
        data = request.json
        status = data.get("status")
        counter_id = data.get("counter_id")
        flow_rate = data.get("flow_rate", 0.2)  # Default flow rate in liters per second

        print(
            f"NodeMCU updating valve status for user {user_id}, counter {counter_id}: {status}"
        )

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if status not in ["open", "close"]:
            return jsonify({"error": "Invalid status"}), 400

        # If counter_id is provided, verify it matches the user's counter
        if counter_id and user.counter_id != counter_id:
            print(
                f"Warning: Counter ID mismatch. User has {user.counter_id}, device sent {counter_id}"
            )
            user.counter_id = counter_id
            db.session.commit()

        # Get current water balance
        water_balance = UserWaterBalance.query.filter_by(user_id=user.id).first()
        if not water_balance:
            water_balance = UserWaterBalance(user_id=user.id, cubic_meters=0.0)
            db.session.add(water_balance)
            db.session.commit()

        # If valve is being closed, calculate and record usage
        if status == "close":
            # Get the last valve open operation
            last_open = ValveOperation.query.filter_by(
                user_id=user.id, operation="open"
            ).order_by(ValveOperation.timestamp.desc()).first()

            if last_open:
                # Calculate time elapsed since valve was opened
                time_elapsed = (datetime.utcnow() - last_open.timestamp).total_seconds()
                
                # Calculate usage in cubic meters (flow_rate is in liters/second)
                usage_amount = (flow_rate * time_elapsed) / 1000  # Convert to cubic meters
                
                # Create water usage record
                new_usage = WaterUsage(
                    counter_id=user.counter_id,
                    usage_amount=usage_amount
                )
                db.session.add(new_usage)
                
                # Update water balance
                water_balance.cubic_meters = max(0, water_balance.cubic_meters - usage_amount)
                water_balance.last_updated = datetime.utcnow()

        # Log the valve operation
        new_operation = ValveOperation(user_id=user.id, operation=status)
        db.session.add(new_operation)
        db.session.commit()

        # Send notification if valve is closed and usage was recorded
        if status == "close" and user.pushover_key:
            send_pushover_notification(
                user.pushover_key,
                "Valve Closed",
                f"Your water valve has been closed. Water usage: {usage_amount:.3f} cubic meters. Remaining balance: {water_balance.cubic_meters:.3f} cubic meters."
            )

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Valve {status} status recorded",
                    "remaining_balance": water_balance.cubic_meters
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        print(f"Error updating valve status: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/update-status/<user_id>", methods=["POST"])
def update_device_status(user_id):
    """
    API endpoint for NodeMCU to update its status
    """
    try:
        data = request.json
        remaining_turns = data.get("remaining_turns")
        valve_status = data.get("valve_status")
        current_usage = data.get("current_usage")
        counter_id = data.get("counter_id")

        print(f"NodeMCU status update for user {user_id}, counter {counter_id}: {data}")

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # If counter_id is provided, verify it matches the user's counter
        if counter_id and user.counter_id != counter_id:
            print(f"Warning: Counter ID mismatch. User has {user.counter_id}, device sent {counter_id}")
            user.counter_id = counter_id
            db.session.commit()
            print(f"Updated user {user_id} to use counter {counter_id}")

        # Check for negative turn count - this indicates a device error
        if remaining_turns < 0:
            print(f"WARNING: Negative turn count ({remaining_turns}) detected for user {user_id}")
            return jsonify({
                "success": True,
                "message": "Status updated but negative turns detected",
                "reset_required": True
            }), 200

        # Get or create water balance
        water_balance = UserWaterBalance.query.filter_by(user_id=user.id).first()
        if not water_balance:
            water_balance = UserWaterBalance(user_id=user.id, cubic_meters=0.0)
            db.session.add(water_balance)
            db.session.commit()

        # If valve is closed and there was usage, record it
        if valve_status == "closed" and current_usage and float(current_usage) > 0:
            # Create water usage record
            new_usage = WaterUsage(
                counter_id=user.counter_id,
                usage_amount=float(current_usage)
            )
            db.session.add(new_usage)

            # Update water balance
            water_balance.cubic_meters = max(0, water_balance.cubic_meters - float(current_usage))
            water_balance.last_updated = datetime.utcnow()

            # Send notification if user has pushover key
            if user.pushover_key:
                send_pushover_notification(
                    user.pushover_key,
                    "Water Usage Complete",
                    f"Your water usage session has ended.\nUsage: {float(current_usage):.3f} m³\nRemaining balance: {water_balance.cubic_meters:.3f} m³"
                )

            db.session.commit()

        # If remaining turns is 0, send a notification
        if remaining_turns == 0 and water_balance.cubic_meters > 0:
            # Update water balance to 0 since turns are 0
            water_balance.cubic_meters = 0
            water_balance.last_updated = datetime.utcnow()
            
            if user.pushover_key:
                send_pushover_notification(
                    user.pushover_key,
                    "Water Balance Depleted",
                    "Your water balance has been fully used. Please recharge your account to continue using water."
                )
            
            db.session.commit()

        return jsonify({
            "success": True,
            "message": "Status updated successfully",
            "reset_required": False,
            "remaining_balance": water_balance.cubic_meters
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating device status: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/borrow-water/<user_id>', methods=['POST'])
def borrow_water(user_id):
    try:
        # Get the request data
        data = request.get_json()
        counter_id = data.get('counter_id')
        
        # Get user and check if they exist
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
            
        # Check if user already has an active loan
        active_loan = WaterLoan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if active_loan:
            return jsonify({
                'success': False,
                'error': 'You already have an active loan. Please repay it before borrowing more.'
            }), 400
            
        # Set maximum loan amount to 2 cubic meters (2000 RWF)
        max_loan_amount = 2.0
        
        # Create new loan
        new_loan = WaterLoan(
            user_id=user_id,
            amount=max_loan_amount,
            status='active',
            borrowed_at=datetime.utcnow()
        )
        
        db.session.add(new_loan)
        
        # Send notification to user
        notification = Notification(
            user_id=user_id,
            title="Water Loan Approved",
            message=f"Your water loan of {max_loan_amount} cubic meters (2000 RWF) has been approved. This will be automatically deducted from your next payment.",
            notification_type="loan_approved"
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'borrowed_amount': max_loan_amount,
            'borrowed_time': max_loan_amount * 3600,  # Convert to seconds
            'message': f"Loan of {max_loan_amount} cubic meters approved"
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in borrow_water: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/user/borrow-water", methods=["GET", "POST"])
@login_required
def borrow_water_ui():
    # Check if user already has an active loan
    active_loan = WaterLoan.query.filter_by(
        user_id=current_user.id, status="active"
    ).first()

    # Get user's credit limit (default to 1.0 if not set or None)
    credit_limit = 1.0  # Default value
    if hasattr(current_user, "credit_limit") and current_user.credit_limit is not None:
        credit_limit = current_user.credit_limit

    # Get loan history
    loan_history = (
        WaterLoan.query.filter_by(user_id=current_user.id)
        .order_by(WaterLoan.borrowed_at.desc())
        .all()
    )

    if request.method == "POST":
        # Check if user already has an active loan
        if active_loan:
            flash("You already have an active water loan", "error")
            return redirect(url_for("borrow_water_ui"))

        # Create a new loan with the non-None credit_limit
        new_loan = WaterLoan(
            user_id=current_user.id, amount=credit_limit, status="active"
        )
        db.session.add(new_loan)

        try:
            db.session.commit()
            flash(
                f"Water loan of {credit_limit} cubic meters approved! You can now use your water.",
                "success",
            )

            # Send notification to the user
            if current_user.pushover_key:
                send_pushover_notification(
                    current_user.pushover_key,
                    "Water Loan Approved",
                    f"Hello {current_user.full_name}, you've been approved for a water loan of {credit_limit} cubic meters. Please remember to pay it back with your next payment.",
                )
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating loan: {str(e)}", "error")
            print(f"Error creating loan: {str(e)}")

        return redirect(url_for("borrow_water_ui"))

    return render_template(
        "user/borrow_water.html",
        active_loan=active_loan,
        credit_limit=credit_limit,
        loan_history=loan_history,
    )


def get_water_balance(user_id):
    """
    Calculate a user's current water balance in cubic meters
    """
    user = User.query.get(user_id)
    if not user:
        return {"cubic_meters": 0.0, "status": "inactive"}

    # Get the latest successful payment
    latest_payment = (
        Payment.query.filter_by(user_id=user.id, status="success")
        .order_by(Payment.timestamp.desc())
        .first()
    )

    # Calculate remaining water based on payment amount
    remaining_water = 0.0
    if latest_payment and latest_payment.amount is not None:
        try:
            remaining_water = (
                float(latest_payment.amount) / 1000.0
            )  # Assuming 1000 RWF per cubic meter
        except (ValueError, TypeError):
            remaining_water = 0.0

    # Get total water usage since payment
    usage_since_payment = 0.0
    if latest_payment and user.counter_id:
        # Find the counter
        counter = Counter.query.filter_by(counter_id=user.counter_id).first()
        if counter:
            usage_query = (
                WaterUsage.query.filter(
                    WaterUsage.counter_id == counter.id,
                    WaterUsage.timestamp > latest_payment.timestamp,
                )
                .with_entities(func.sum(WaterUsage.usage_amount))
                .scalar()
            )

            if usage_query is not None:
                try:
                    usage_since_payment = float(usage_query)
                except (ValueError, TypeError):
                    usage_since_payment = 0.0

    # Calculate remaining water
    remaining = max(0.0, remaining_water - usage_since_payment)

    # Check if user has an active loan
    active_loan = WaterLoan.query.filter_by(user_id=user.id, status="active").first()

    status = "active"
    if remaining <= 0 and not active_loan:
        status = "depleted"

    return {"cubic_meters": remaining, "status": status}


@app.route("/api/get-water-balance/<user_id>", methods=["GET"])
def api_get_water_balance(user_id):
    """
    API endpoint to get real-time water balance
    """
    try:
        balance = get_water_balance(user_id)

        # Get current valve status to check if water is flowing
        valve_status = "closed"
        latest_operation = (
            ValveOperation.query.filter_by(user_id=int(user_id))
            .order_by(ValveOperation.timestamp.desc())
            .first()
        )

        if latest_operation:
            valve_status = latest_operation.operation

        # Calculate current usage if valve is open
        current_usage = 0
        if valve_status == "open":
            # Get the time when the valve was opened
            valve_open_time = latest_operation.timestamp

            # Calculate elapsed time in seconds
            elapsed_seconds = (datetime.utcnow() - valve_open_time).total_seconds()

            # Calculate usage based on flow rate (0.2 liters per second = 0.0002 cubic meters per second)
            current_usage = elapsed_seconds * 0.0002

        return (
            jsonify(
                {
                    "remaining_cubic_meters": balance.cubic_meters - current_usage,
                    "status": balance.status,
                    "valve_status": valve_status,
                    "current_usage": current_usage,
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error getting water balance: {str(e)}")
        return jsonify({"error": str(e)}), 500


def update_water_balance(user_id, amount, operation="add"):
    """
    Update a user's water balance

    Args:
        user_id: The user's ID
        amount: Amount in cubic meters
        operation: 'add' or 'subtract'

    Returns:
        The updated balance
    """
    balance = get_water_balance(user_id)

    if operation == "add":
        balance.cubic_meters += amount
    elif operation == "subtract":
        balance.cubic_meters -= amount
        # Ensure balance doesn't go negative
        if balance.cubic_meters < 0:
            balance.cubic_meters = 0

    balance.last_updated = datetime.utcnow()
    db.session.commit()

    return balance


@app.route("/api/test-usage", methods=["GET"])
def test_usage_api():
    """Test endpoint for water usage recording"""
    # Create a test usage record for user 1
    try:
        user = User.query.get(1)
        if not user or not user.counter_id:
            return jsonify({"error": "Test user not found or has no counter"}), 404

        counter = Counter.query.filter_by(counter_id=user.counter_id).first()
        if not counter:
            return jsonify({"error": "Counter not found"}), 404

        test_usage = WaterUsage(counter_id=counter.id, usage_amount=0.001)
        db.session.add(test_usage)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Test usage record created",
                "user_id": user.id,
                "counter_id": counter.id,
                "usage_amount": 0.001,
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/check-usage-records", methods=["GET"])
def check_usage_records():
    """Check if there are any water usage records"""
    try:
        count = WaterUsage.query.count()
        records = WaterUsage.query.order_by(WaterUsage.timestamp.desc()).limit(10).all()

        return jsonify(
            {
                "total_records": count,
                "recent_records": [
                    {
                        "id": record.id,
                        "counter_id": record.counter_id,
                        "usage_amount": record.usage_amount,
                        "timestamp": record.timestamp.isoformat(),
                    }
                    for record in records
                ],
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get-latest-usage/<user_id>", methods=["GET"])
def get_latest_usage(user_id):
    """
    API endpoint for web interface to get latest water usage data
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the latest water usage record
        latest_usage = (
            WaterUsage.query.filter_by(counter_id=user.counter_id)
            .order_by(WaterUsage.timestamp.desc())
            .first()
        )

        # Get the latest payment for remaining water calculation
        latest_payment = (
            Payment.query.filter_by(user_id=user_id, status="success")
            .order_by(Payment.timestamp.desc())
            .first()
        )

        # Calculate remaining water
        remaining_water = 0
        if latest_payment:
            remaining_water = (
                latest_payment.amount / 1000
            )  # Assuming 1000 RWF per cubic meter

        # Get total water usage since payment
        usage_since_payment = 0
        if latest_payment:
            usage_since_payment = (
                WaterUsage.query.filter(
                    WaterUsage.counter_id == user.counter_id,
                    WaterUsage.timestamp > latest_payment.timestamp,
                )
                .with_entities(func.sum(WaterUsage.usage_amount))
                .scalar()
                or 0
            )

        # Calculate remaining water
        remaining = max(0, remaining_water - usage_since_payment)

        response_data = {"remaining_cubic_meters": remaining}

        # Add latest usage data if available
        if latest_usage:
            response_data.update(
                {
                    "latest_usage": float(latest_usage.usage_amount),
                    "latest_timestamp": latest_usage.timestamp.isoformat(),
                }
            )

        return jsonify(response_data), 200
    except Exception as e:
        logger.error(f"Error getting latest usage: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/update-usage-and-check-balance/<user_id>", methods=["POST"])
def update_usage_and_check_balance(user_id):
    """
    API endpoint for NodeMCU to record usage and check remaining balance in one call
    Expects: usage_amount (in cubic meters)
    Returns: remaining_turns, remaining_cubic_meters
    """
    data = request.json
    usage_amount = data.get("usage_amount")

    if not usage_amount:
        return jsonify({"error": "Missing usage_amount parameter"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        # Convert usage_amount to float
        usage_amount = float(usage_amount)

        # Create the water usage record
        new_usage = WaterUsage(counter_id=user.counter_id, usage_amount=usage_amount)
        db.session.add(new_usage)

        # Deduct from user's water balance
        updated_balance = update_water_balance(user_id, usage_amount, "subtract")

        # Calculate remaining turns
        remaining_cubic_meters = updated_balance.cubic_meters
        remaining_turns = int(remaining_cubic_meters * 200)  # 1 cubic meter = 200 turns

        # Send notification if usage is high
        if usage_amount > 0.1 and user.pushover_key:
            send_pushover_notification(
                user.pushover_key,
                "Water Usage Update",
                f"Hello {user.full_name}, you've used {usage_amount:.3f} cubic meters of water. Your remaining balance is {remaining_cubic_meters:.3f} cubic meters.",
            )

        return (
            jsonify(
                {
                    "success": True,
                    "remaining_turns": remaining_turns,
                    "remaining_cubic_meters": remaining_cubic_meters,
                    "message": "Usage recorded successfully",
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        print(f"Error updating usage and checking balance: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/record-usage", methods=["POST"])
def record_usage_api():
    """
    API endpoint for NodeMCU to record water usage
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        counter_id_str = data.get("counter_id")
        usage_amount = data.get("usage_amount")

        print(
            f"Recording water usage: User {user_id}, Counter {counter_id_str}, Amount: {usage_amount} cubic meters"
        )

        if not user_id or usage_amount is None:
            return jsonify({"error": "Missing required parameters"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Find the counter by its string identifier
        counter_id_to_use = counter_id_str if counter_id_str else user.counter_id

        if not counter_id_to_use:
            return (
                jsonify({"error": "No counter ID provided or associated with user"}),
                400,
            )

        counter = Counter.query.filter_by(counter_id=counter_id_to_use).first()
        if not counter:
            # If counter doesn't exist, create it
            print(f"Counter {counter_id_to_use} not found, creating new counter record")
            counter = Counter(counter_id=counter_id_to_use, status="assigned")
            db.session.add(counter)
            db.session.commit()

            # Assign it to the user if not already assigned
            if not user.counter_id:
                user.counter_id = counter_id_to_use
                db.session.commit()

        # Create a new water usage record
        new_usage = WaterUsage(
            counter_id=counter.id,  # Use the counter's database ID
            usage_amount=float(usage_amount),
        )

        db.session.add(new_usage)
        db.session.commit()

        print(
            f"Successfully recorded usage of {usage_amount} cubic meters for counter {counter_id_to_use}"
        )

        return jsonify({"success": True, "message": "Usage recorded successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error recording water usage: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/get-valve-status/<user_id>", methods=["GET"])
def get_valve_status(user_id):
    """
    API endpoint for web interface to check valve status
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the latest valve operation
        latest_operation = (
            ValveOperation.query.filter_by(user_id=user.id)
            .order_by(ValveOperation.timestamp.desc())
            .first()
        )

        status = "unknown"
        if latest_operation:
            status = latest_operation.operation

        return (
            jsonify(
                {
                    "status": status,
                    "last_updated": (
                        latest_operation.timestamp.isoformat()
                        if latest_operation
                        else None
                    ),
                }
            ),
            200,
        )
    except Exception as e:
        print(f"Error getting valve status: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/report-valve-closed/<user_id>", methods=["POST"])
def report_valve_closed(user_id):
    """
    API endpoint for NodeMCU to report valve closure and record usage in one call
    Expects: usage_amount (in cubic meters)
    """
    try:
        data = request.json
        usage_amount = data.get("usage_amount")

        if usage_amount is None:
            return jsonify({"error": "Missing usage_amount parameter"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Convert usage_amount to float
        usage_amount = float(usage_amount)

        # 1. Log valve operation
        new_operation = ValveOperation(user_id=int(user_id), operation="closed")
        db.session.add(new_operation)

        # 2. Create the water usage record
        new_usage = WaterUsage(counter_id=user.counter_id, usage_amount=usage_amount)
        db.session.add(new_usage)

        # 3. Update user's balance if needed
        # This depends on how you're tracking water balance in your system

        db.session.commit()

        logger.info(
            f"Valve closed and usage of {usage_amount} cubic meters recorded for user {user_id}"
        )

        # Send notification to the user
        if user.pushover_key:
            send_pushover_notification(
                user.pushover_key,
                "Valve Closed",
                f"Hello {user.full_name}, your water valve has been closed. You used {usage_amount:.3f} cubic meters of water.",
            )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Valve closure and usage recorded successfully",
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error reporting valve closure: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/update-status/<user_id>", methods=["POST"])
def update_status(user_id):
    """
    API endpoint for NodeMCU to report current status
    Expects: remaining_turns, valve_status, current_usage
    """
    try:
        data = request.json
        remaining_turns = data.get("remaining_turns", 0)
        valve_status = data.get("valve_status", "closed")
        current_usage = data.get("current_usage", 0)

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Store the current status in a session variable
        if "user_statuses" not in session:
            session["user_statuses"] = {}

        session["user_statuses"][str(user_id)] = {
            "remaining_turns": remaining_turns,
            "valve_status": valve_status,
            "current_usage": float(current_usage),
            "timestamp": datetime.utcnow().isoformat(),
        }
        session.modified = True

        # If valve is closed and there was usage, record it
        if valve_status == "closed" and float(current_usage) > 0:
            new_usage = WaterUsage(
                counter_id=user.counter_id, usage_amount=float(current_usage)
            )
            db.session.add(new_usage)
            db.session.commit()

            # Reset usage after recording
            session["user_statuses"][str(user_id)]["current_usage"] = 0
            session.modified = True

        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating status: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/get-status/<user_id>", methods=["GET"])
def get_status(user_id):
    """
    API endpoint for web interface to get current status
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get status from session
        user_statuses = session.get("user_statuses", {})
        status = user_statuses.get(str(user_id), {})

        if not status:
            # If not in session, check database for latest valve operation
            latest_operation = (
                ValveOperation.query.filter_by(user_id=int(user_id))
                .order_by(ValveOperation.timestamp.desc())
                .first()
            )

            valve_status = "closed"
            if latest_operation:
                valve_status = latest_operation.operation

            # Get the latest payment for remaining water calculation
            latest_payment = (
                Payment.query.filter_by(user_id=user_id, status="success")
                .order_by(Payment.timestamp.desc())
                .first()
            )

            # Calculate remaining water
            remaining_water = 0
            if latest_payment:
                remaining_water = (
                    latest_payment.amount / 1000
                )  # Assuming 1000 RWF per cubic meter

            # Get total water usage since payment
            usage_since_payment = 0
            if latest_payment:
                usage_since_payment = (
                    WaterUsage.query.filter(
                        WaterUsage.counter_id == user.counter_id,
                        WaterUsage.timestamp > latest_payment.timestamp,
                    )
                    .with_entities(func.sum(WaterUsage.usage_amount))
                    .scalar()
                    or 0
                )

            # Calculate remaining water
            remaining = max(0, remaining_water - usage_since_payment)

            # Convert to turns (assuming 1 cubic meter = 200 turns)
            remaining_turns = int(remaining * 200)

            status = {
                "valve_status": valve_status,
                "remaining_turns": remaining_turns,
                "remaining_water": remaining,
                "current_usage": 0,
            }

        # Calculate remaining water in cubic meters if not provided
        if "remaining_water" not in status and "remaining_turns" in status:
            status["remaining_water"] = (
                status["remaining_turns"] * 0.005
            )  # 1 turn = 0.005 cubic meters

        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return (
            jsonify(
                {
                    "error": str(e),
                    "valve_status": "unknown",
                    "remaining_water": 0,
                    "remaining_turns": 0,
                    "current_usage": 0,
                }
            ),
            500,
        )


@app.route("/api/retry-failed-reports/<user_id>", methods=["POST"])
def retry_failed_reports(user_id):
    """
    API endpoint for NodeMCU to retry sending failed usage reports
    Expects: reports - array of {usage_amount, timestamp}
    """
    try:
        data = request.json
        reports = data.get("reports", [])

        if not reports:
            return jsonify({"message": "No reports to process"}), 200

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        successful_reports = 0

        for report in reports:
            usage_amount = float(report.get("usage_amount", 0))

            if usage_amount > 0:
                # Create the water usage record
                new_usage = WaterUsage(
                    counter_id=user.counter_id, usage_amount=usage_amount
                )
                db.session.add(new_usage)
                successful_reports += 1

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Successfully processed {successful_reports} of {len(reports)} reports",
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing failed reports: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/admin/loans")
@login_required
def admin_loans():
    # Check if the current user is an admin
    if not isinstance(current_user, Admin):
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("user_dashboard"))

    # Get all loans with pagination
    page = request.args.get("page", 1, type=int)
    per_page = 10
    loans = WaterLoan.query.order_by(WaterLoan.borrowed_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template("admin/loans.html", loans=loans)


@app.route("/admin/recharges", methods=["GET", "POST"])
@login_required
def admin_recharges():
    # Check if the current user is an admin
    if not isinstance(current_user, Admin):
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("user_dashboard"))

    if request.method == "POST":
        user_id = request.form.get("user_id")
        amount = float(request.form.get("amount", 0))
        description = request.form.get("description", "")

        user = User.query.get(user_id)
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("admin_recharges"))

        # Create a new payment record for the recharge
        payment = Payment(
            user_id=user_id,
            amount=amount,
            status="completed",
            transaction_type="recharge",
            transaction_ref=f"RECHARGE_{int(time.time())}"
        )
        db.session.add(payment)

        # Update user's balance
        user.balance += amount

        try:
            db.session.commit()
            flash(f"Successfully recharged {amount} RWF to user {user.full_name}", "success")
            
            # Send notification to user if they have Pushover configured
            if user.pushover_key:
                send_pushover_notification(
                    user.pushover_key,
                    "Account Recharged",
                    f"Your account has been recharged with {amount} RWF. New balance: {user.balance} RWF"
                )
        except Exception as e:
            db.session.rollback()
            flash(f"Error processing recharge: {str(e)}", "error")

        return redirect(url_for("admin_recharges"))

    # Get all users for the dropdown
    users = User.query.all()
    # Get recharge history
    page = request.args.get("page", 1, type=int)
    per_page = 10
    recharges = Payment.query.filter_by(transaction_type="recharge").order_by(Payment.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template("admin/recharges.html", users=users, recharges=recharges)


@app.route("/isp/recharge", methods=["GET", "POST"])
def isp_recharge():
    if request.method == "POST":
        try:
            user_id = request.form.get("user_id")
            amount = float(request.form.get("amount", 0))

            if not user_id or amount <= 0:
                flash("Invalid user or amount.", "error")
                return redirect(url_for("isp_recharge"))

            # Get user
            user = User.query.get(user_id)
            if not user:
                flash("User not found.", "error")
                return redirect(url_for("isp_recharge"))

            # Get or create user's account
            account = Account.query.filter_by(user_id=user.id).first()
            if not account:
                # Generate a unique account number
                account_number = f"ACC{int(datetime.utcnow().timestamp())}"
                account = Account(
                    user_id=user.id,
                    account_number=account_number,
                    balance=0.0,
                    status="active"
                )
                db.session.add(account)

            # Create payment record
            payment = Payment(
                user_id=user.id,
                amount=amount,
                status="success",
                transaction_type="recharge",
                transaction_ref=f"ISP_RECHARGE_{int(datetime.utcnow().timestamp())}"
            )
            db.session.add(payment)

            # Update account balance
            account.balance = float(account.balance) + amount
            account.last_transaction = datetime.utcnow()

            # Send notification if Pushover key is configured
            if user.pushover_key:
                send_pushover_notification(
                    user.pushover_key,
                    "Account Recharged",
                    f"Your account has been recharged with RWF {amount:,.2f}. New balance: RWF {account.balance:,.2f}",
                    priority=0
                )

            db.session.commit()
            flash(f"Successfully recharged RWF {amount:,.2f} to user {user.full_name}. New balance: RWF {account.balance:,.2f}", "success")
            return redirect(url_for("isp_recharge"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error processing recharge: {str(e)}", "error")
            return redirect(url_for("isp_recharge"))

    return render_template("isp/recharge.html")


@app.route("/user/activate-account", methods=["GET", "POST"])
@login_required
def activate_account():
    # Check if user already has an account
    existing_account = Account.query.filter_by(user_id=current_user.id).first()
    if existing_account:
        flash("You already have an active account", "info")
        return redirect(url_for("account_details"))

    if request.method == "POST":
        phone_number = request.form.get("phone_number")

        # Format phone number
        if not phone_number.startswith("+250"):
            phone_number = "+250" + phone_number.lstrip("0")

        # Update user's phone number
        current_user.phone_number = phone_number

        # Generate a unique account number
        account_number = f"WM{current_user.id:06d}"

        # Create a new account
        new_account = Account(
            user_id=current_user.id,
            account_number=account_number,
            balance=0.0,
            status="active",
        )

        db.session.add(new_account)
        db.session.commit()

        flash("Your account has been successfully activated!", "success")
        return redirect(url_for("account_details"))

    return render_template("user/activate_account.html")


@app.route("/user/recharge-account", methods=["GET", "POST"])
@login_required
def recharge_account():
    # Get user's account
    account = Account.query.filter_by(user_id=current_user.id).first()

    if not account:
        flash("You need to activate your account first", "warning")
        return redirect(url_for("activate_account"))

    # Get recharge history
    recharges = (
        Payment.query.filter_by(
            user_id=current_user.id, status="success", transaction_type="recharge"
        )
        .order_by(Payment.timestamp.desc())
        .limit(10)
        .all()
    )

    if request.method == "POST":
        phone_number = request.form.get("phone_number") or current_user.phone_number
        amount = float(request.form.get("amount"))

        # Format phone number (keep this for future real implementation)
        if not phone_number.startswith("+250"):
            phone_number = "+250" + phone_number.lstrip("0")

        # Generate a transaction reference
        transaction_ref = str(uuid.uuid4())

        try:
            # Create a new payment record for recharge
            new_payment = Payment(
                user_id=current_user.id,
                amount=amount,
                status="pending",
                transaction_ref=transaction_ref,
                transaction_type="recharge",  # Mark this as a recharge transaction
            )
            db.session.add(new_payment)
            db.session.commit()

            # In a real implementation, you would integrate with mobile money API here
            # For now, we'll simulate a successful recharge
            new_payment.status = "success"

            # Update account balance instead of user balance
            account.balance += amount
            account.last_transaction = datetime.utcnow()

            db.session.commit()

            # Send notification if user has Pushover key
            if current_user.pushover_key:
                send_pushover_notification(
                    current_user.pushover_key,
                    "Account Recharged",
                    f"Your account has been recharged with RWF {amount:,.2f}. Your new balance is RWF {account.balance:,.2f}.",
                )

            flash(
                f"Your account has been successfully recharged with RWF {amount:,.2f}!",
                "success",
            )
            return redirect(url_for("account_details"))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Recharge failed: {str(e)}")
            flash("Recharge processing failed. Please try again.", "error")

    return render_template(
        "user/recharge_account.html", account=account, recharges=recharges
    )


migrate = Migrate(app, db)

@app.route("/api/water-flow/<user_id>", methods=["GET"])
def get_water_flow(user_id):
    """
    API endpoint to get real-time water flow information
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the latest valve operation
        latest_operation = ValveOperation.query.filter_by(user_id=user.id).order_by(ValveOperation.timestamp.desc()).first()
        
        # Get current water balance
        water_balance = UserWaterBalance.query.filter_by(user_id=user.id).first()
        if not water_balance:
            water_balance = UserWaterBalance(user_id=user.id, cubic_meters=0.0)
            db.session.add(water_balance)
            db.session.commit()

        # Initialize response data
        response_data = {
            "valve_status": "closed",
            "remaining_balance": water_balance.cubic_meters,
            "current_flow_rate": 0.0,  # liters per second
            "estimated_usage": 0.0,    # cubic meters
            "time_elapsed": 0          # seconds
        }

        # If valve is open, calculate current usage
        if latest_operation and latest_operation.operation == "open":
            time_elapsed = (datetime.utcnow() - latest_operation.timestamp).total_seconds()
            flow_rate = 0.2  # liters per second
            estimated_usage = (flow_rate * time_elapsed) / 1000  # convert to cubic meters

            response_data.update({
                "valve_status": "open",
                "current_flow_rate": flow_rate,
                "estimated_usage": estimated_usage,
                "time_elapsed": time_elapsed
            })

        return jsonify(response_data), 200
    except Exception as e:
        print(f"Error getting water flow: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.template_filter("format_number")
def format_number(value):
    """Format number with thousand separators"""
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "0.00"

@app.route("/admin/counters/add", methods=["POST"])
@login_required
def add_counter():
    # Check if user is admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("index"))

    try:
        counter_id = request.form.get("counter_id")
        if not counter_id:
            flash("Counter ID is required.", "error")
            return redirect(url_for("manage_counters"))

        # Check if counter already exists
        existing_counter = Counter.query.filter_by(counter_id=counter_id).first()
        if existing_counter:
            flash("Counter ID already exists.", "error")
            return redirect(url_for("manage_counters"))

        # Create new counter
        new_counter = Counter(
            counter_id=counter_id,
            status="available"
        )
        db.session.add(new_counter)
        db.session.commit()

        flash("Counter added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding counter: {str(e)}", "error")

    return redirect(url_for("manage_counters"))

@app.route("/admin/counters/assign", methods=["POST"])
@login_required
def assign_counter():
    # Check if user is admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("index"))

    try:
        counter_id = request.form.get("counter_id")
        user_id = request.form.get("user_id")

        if not counter_id or not user_id:
            flash("Both counter ID and user ID are required.", "error")
            return redirect(url_for("manage_counters"))

        # Get counter and user
        counter = Counter.query.filter_by(counter_id=counter_id).first()
        user = User.query.get(user_id)

        if not counter or not user:
            flash("Counter or user not found.", "error")
            return redirect(url_for("manage_counters"))

        # Check if counter is already assigned
        if counter.assigned_to:
            flash("This counter is already assigned to a user.", "error")
            return redirect(url_for("manage_counters"))

        # Check if user already has a counter
        if user.counter_id:
            flash("This user already has a counter assigned.", "error")
            return redirect(url_for("manage_counters"))

        # Assign counter to user
        counter.assigned_to = user_id
        counter.status = "active"
        user.counter_id = counter_id

        # Initialize water balance for user if not exists
        water_balance = UserWaterBalance.query.filter_by(user_id=user_id).first()
        if not water_balance:
            water_balance = UserWaterBalance(user_id=user_id, cubic_meters=0.0)
            db.session.add(water_balance)

        db.session.commit()
        flash("Counter assigned successfully.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error assigning counter: {str(e)}", "error")

    return redirect(url_for("manage_counters"))

@app.route("/admin/water-usage/add", methods=["POST"])
@login_required
def add_reading():
    # Check if user is admin
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("index"))

    try:
        counter_id = request.form.get("counter_id")
        usage_amount = float(request.form.get("usage_amount", 0))

        if not counter_id or usage_amount <= 0:
            flash("Invalid counter ID or usage amount.", "error")
            return redirect(url_for("water_usage_page"))

        # Get counter
        counter = Counter.query.filter_by(counter_id=counter_id).first()
        if not counter:
            flash("Counter not found.", "error")
            return redirect(url_for("water_usage_page"))

        # Create new reading
        new_reading = WaterUsage(
            counter_id=counter.id,
            usage_amount=usage_amount
        )
        db.session.add(new_reading)
        db.session.commit()

        flash("Water usage reading added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding reading: {str(e)}", "error")

    return redirect(url_for("water_usage_page"))

@app.route("/api/search-users")
def search_users():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    # Search by phone number, ID card, or full name
    users = User.query.filter(
        db.or_(
            User.phone_number.ilike(f'%{query}%'),
            User.id_card.ilike(f'%{query}%'),
            User.full_name.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    results = []
    for user in users:
        results.append({
            'id': user.id,
            'full_name': user.full_name,
            'phone_number': user.phone_number or '',
            'id_card': user.id_card,
            'counter_id': user.counter_id or ''
        })
    
    return jsonify(results)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
