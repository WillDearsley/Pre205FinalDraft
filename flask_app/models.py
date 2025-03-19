from flask_app import db
from datetime import datetime
from flask_login import UserMixin

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    #username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    companies = db.relationship('Companies', backref='owner', lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

class Companies(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invoices = db.relationship('Invoices', backref='company', lazy=True)

    def __repr__(self):
        return f"<Company {self.name}>"

class Invoices(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), nullable=True)
    client_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, paid, overdue
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)