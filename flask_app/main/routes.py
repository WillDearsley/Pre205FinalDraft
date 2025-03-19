import os
from flask import render_template, request, make_response, Blueprint, url_for, send_from_directory, current_app, redirect, flash, jsonify, session
from flask_app import db # -------------------> THIS IS THE DATABASE ABJECT <------------------------------------
from flask_login import login_required, current_user
from flask_app.models import Companies, Invoices
from datetime import datetime, timedelta

main = Blueprint("main", __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@main.route("/", methods=["GET", "POST"])
@main.route("/index", methods=["GET", "POST"])
def index():

    meta = {
        "title": "Home - Speckle Invoice",
        "description": "Join Speckle Invoice today to simplify invoice generation for your bussiness",
        "og_url": url_for('main.index', _external=True)
    }

    return render_template("index.html", meta=meta)

@main.route("/signup", methods=["GET", "POST"])
def signup():

    meta = {
        "title": "Sign Up - Speckle Invoice",
        "description": "Create an account on Speck Invoice today. It's Free!",
        "og_url": url_for('main.signup', _external=True)
    }

    return render_template("signup.html", meta=meta)

@main.route("/signin", methods=["GET", "POST"])
def signin():

    meta = {
        "title": "Sign In - Speckle Invoice",
        "description": "Sign in to Speck Invoice today",
        "og_url": url_for('main.signin', _external=True)
    }

    return render_template("signin.html", meta=meta)


@main.route('/dashboard')
@login_required
def dashboard():
    meta = {
        "title": "Dashboard - Speckle Invoice",
        "description": "Dashboard for Speckle Invoice",
        "og_url": url_for('main.dashboard', _external=True)
    }   
    if not current_user.companies:
        return redirect(url_for('main.create_company'))
    
    # Get current company from session or default to first company
    current_company_id = session.get('current_company_id')
    if not current_company_id or not any(c.id == current_company_id for c in current_user.companies):
        current_company_id = current_user.companies[0].id
        session['current_company_id'] = current_company_id
    
    current_company = Companies.query.get(current_company_id)
    
    # Get invoice statistics
    total_invoices = Invoices.query.filter_by(company_id=current_company_id).count()
    pending_invoices = Invoices.query.filter_by(company_id=current_company_id, status='pending').count()
    paid_invoices = Invoices.query.filter_by(company_id=current_company_id, status='paid').count()
    total_revenue = db.session.query(db.func.sum(Invoices.amount)).filter(
        Invoices.company_id == current_company_id,
        Invoices.status == 'paid'
    ).scalar() or 0
    
    # Get recent invoices
    recent_invoices = Invoices.query.filter_by(company_id=current_company_id).order_by(
        Invoices.created_at.desc()
    ).limit(3).all()
    
    # Get upcoming due dates
    upcoming_invoices = Invoices.query.filter(
        Invoices.company_id == current_company_id,
        Invoices.status == 'pending',
        Invoices.due_date >= datetime.utcnow()
    ).order_by(Invoices.due_date.asc()).limit(3).all()
    
    return render_template(
        "dashboard.html",
        user=current_user,
        current_company=current_company,
        total_invoices=total_invoices,
        pending_invoices=pending_invoices,
        paid_invoices=paid_invoices,
        total_revenue=total_revenue,
        recent_invoices=recent_invoices,
        upcoming_invoices=upcoming_invoices,
        meta = meta
    )

@main.route('/switch-company/<int:company_id>', methods=['POST'])
@login_required
def switch_company(company_id):
    # Verify the company belongs to the current user
    if not any(c.id == company_id for c in current_user.companies):
        return jsonify({'error': 'Invalid company'}), 403
    
    session['current_company_id'] = company_id
    return jsonify({'success': True})
    

@main.route("/forgot", methods=["GET", "POST"])
def forgot():

    meta = {
        "title": "Forgot Password - Speckle Invoice",
        "description": "If your having issues remembering your password",
        "og_url": url_for('main.index', _external=True)
    }

    return render_template("forgot.html", meta=meta)

@main.route('/create-company', methods=['GET', 'POST'])
@login_required
def create_company():
    meta = {
        "title": "Create Company - Speckle Invoice",
        "description": "Create a company on Speckle Invoice today",
        "og_url": url_for('main.index', _external=True)
    }

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Company name is required', 'error')
            return redirect(url_for('main.create_company'))
            
        company = Companies(
            name=name,
            description=description,
            user_id=current_user.id
        )
        
        db.session.add(company)
        db.session.commit()
        
        flash('Company created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('create_company.html', meta=meta)

@main.route("/sitemap.xml")
def sitemap():
    pages = [
      {"loc": url_for("main.index", _external=True)},
      {"loc": url_for("main.search", _external=True)},
    ]
  
    sitemap_xml = render_template("sitemap_template.xml", pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
  
    return response

@main.route("/robots.txt")
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])

@main.route('/invoices')
@login_required
def invoices():
    meta = {
        "title": "Invoices - Speckle Invoice",
        "description": "Invoices for Speckle Invoice",
        "og_url": url_for('main.invoices', _external=True)
    }
    # Get the current company from session or default to first company
    current_company_id = session.get('current_company_id')
    if not current_company_id:
        current_company = current_user.companies.first()
        if current_company:
            current_company_id = current_company.id
            session['current_company_id'] = current_company_id
        else:
            return redirect(url_for('main.create_company'))
    
    # Get all invoices for the current company
    invoices = Invoices.query.filter_by(company_id=current_company_id).order_by(Invoices.created_at.desc()).all()
    
    return render_template('invoices.html', 
                         user=current_user,
                         invoices=invoices,
                         current_company=Companies.query.get(current_company_id),
                         meta = meta)

@main.route('/profile')
@login_required
def profile():
    current_company_id = session.get('current_company_id')
    if not current_company_id or not any(c.id == current_company_id for c in current_user.companies):
        current_company_id = current_user.companies[0].id
        session['current_company_id'] = current_company_id

    meta = {
        "title": "Profile Settings - Speckle Invoice",
        "description": "Manage your SpeckleInvoice profile settings",
        "og_url": url_for('main.profile', _external=True)
    }
    return render_template('profile.html', user=current_user, meta=meta, current_company=Companies.query.get(current_company_id))