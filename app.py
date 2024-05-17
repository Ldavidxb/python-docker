from flask import Flask, import click, flask.cli import with_appcontext, request, jsonify, render_template, redirect, url_forrender_template, redirect, url_for, flash, g
from flask_login import LoginManager, logout_user, login_required, current_user, 
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import stripe
from .token_utils import generate_invitation_token, decode_invitation_token
from .email_utils import send_invitation_email
from flask_sqlalchemy import SQLAlchemy
from your_model_file import User, Import your models, 
from dotenv import load_dotenv
from io import StringIO
from config import DevelopmentConfig, ProductionConfig
from .models import db, initialize_permissions
from config import DevelopmentConfig  # or whichever config you're using
import click
from dotenv import load_dotenv
from flask.cli import with_appcontext
from your_application import create_app, db
from role_permission_setup import initialize_permissions, initialize_roles, assign_common_permissions
from models import db_session 
from models import MCXCustomer, Vendor, Buyer, Import Service Provider, Export Service Provider, Vendor Procurement Contract, Buyer Sales Contract, Import Freight Contract, Export Freight Contract
from models import db, initialize_permissions  
from database import db  # Database instance
import re  # For regular expression operations
from flask import Flask, request, jsonify, abort
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from werkzeug.utils import redirect, url_for
from werkzeug.utils import secure_filename
from utils import validate_email
from utils import generate_upload_path
from confluent_kafka import Consumer, KafkaError
from watchdog.observers import Observer
from confluent_kafka import Producer
from watchdog.events import FileSystemEventHandler
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from google.cloud import vision
import psycopg2 # Import psycopg2 for PostgreSQL
import cv2
from PIL import Image
import pytesseract
import numpy as np
from pdfplumber import pdfplumber
import tensorflow
import io
import datetime
import os
import pandas as pd
import azureformrecognizer 
from werkzeug.utils import secure_filename
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from nvocdr import nvOCDR_init, nvOCDR_inference, nvOCDR_deinit
from mcxocrapp_v0.5_01-01-2024 import db, initialize_permissions
from mcxocrapp_v0.5_01-01-2024.models import Permission  # Make sure to import the models
from flask import Flask, request, jsonify
from services.ocrservice import ocrservice
from config import KAFKA_API_KEY, KAFKA_API_SECRET
from backend.kafka.producer import kafka_producer
from factory import create_app
flask start-kafka-consumer
from flask.cli import with_appcontext
from your_project.kafka_consumer import kafka_consumer_setup, consume_messages
import threading
from models.roles_permission_setup import create_tenants_and_rls
from models.security.tenant_roles import create_tenant_roles
from models.security.rls_policies import create_rls_policies


# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """Create and configure an instance of the Flask application."""
    load_dotenv()
    app = Flask(__name__)

# Environment variable adjustments
    os.environ['MATCH_MANIFEST_VERSIONS'] = 'false'  
    print(f"Hello, {os.environ.get('NAME', 'Default')}!")

# Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['KAFKA_API_KEY'] = os.getenv('KAFKA_API_KEY')
    app.config['KAFKA_API_SECRET'] = os.getenv('KAFKA_API_SECRET')

    db.init_app(app)  # Initialize SQLAlchemy
    login_manager.init_app(app)  # Initialize Flask-Login

@click.command('start-kafka-consumer')
@with_appcontext
def start_kafka_consumer_command():
    consumer_thread = threading.Thread(target=consume_messages, args=(consumer,), daemon=True)
    consumer_thread.start()
    click.echo("Kafka consumer started in background thread.")

app.cli.add_command(start_kafka_consumer_command)

# Assuming auth_blueprint and main_blueprint are defined in your auth.py and main.py respectively
    from yourapplication.auth import auth_blueprint
    from yourapplication.main import main_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)

# Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self' https://trusted-cdn.com; script-src 'self' 'unsafe-inline' https://trusted-scripts.com"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    @app.route('/')
    def index():
        return render_template('index.html')  # Ensure 'index.html' exists in your templates directory

    # Setup permissions and roles before the first request
    @app.before_first_request
    def setup_application():
        db.create_all()
        initialize_permissions()
        initialize_roles_permissions()

    return app

@click.command('init-permissions')
@with_appcontext
def init_permissions_command():
    """CLI command for initializing permissions."""
    # Assuming these functions are defined elsewhere and imported correctly
    initialize_permissions()
    print('Initialized the database with permissions.')

if __name__ == '__main__':
    create_tenants_and_rls()
    create_tenant_roles()
    create_rls_policies()
    app_instance = create_app()
    app_instance.cli.add_command(init_permissions_command)
    app_instance.run(debug=True)
if __name__ == '__main__':
    


# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(**db_params)

# Retrieve the encryption key from the environment variable
encryption_key = os.environ.get('ENCRYPTION_KEY')  # Ensure this key is set in your environment
UPLOAD_FOLDER = '/path/to/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpeg', 'png', 'csv', 'xls', 'xlsx', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_document(folder_type, document_type, identifiers):
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = generate_upload_path(folder_type, document_type, identifiers)

        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        return f'File uploaded successfully to {file_path}', 200

    return 'File not allowed', 400

@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/register_company', methods=['GET', 'POST'])
@login_required
def register_company():
    company_form = CompanyForm(request.form)
    contact_form = ContactForm()
    address_form = AddressForm()
    
    if request.method == 'POST' and company_form.validate() and contact_form.validate() and address_form.validate():
        existing_company = Company.query.filter_by(company_name=company_form.company_name.data).first()
        if existing_company:
            flash('Company with this name already exists.', 'error')
        else:
            new_company = Company(
                company_name=company_form.company_name.data,
                partner_type=company_form.partner_type.data,
                hq_type=company_form.hq_type.data,
                department=company_form.department.data,
                function=company_form.function.data,
                title=company_form.title.data,
                business_type=company_form.business_type.data,
                incorporation_type=company_form.incorporation_type.data,
                address_type=company_form.address_type.data,
                industry_vertical=company_form.industry_vertical.data
            )
            new_contact = Contact(
                first_name=contact_form.first_name.data,
                last_name=contact_form.last_name.data,
                phone=contact_form.phone.data,
                email=contact_form.email.data,
                company=new_company
            )
            new_address = Address(
                address_line_1=address_form.address_line_1.data,
                address_line_2=address_form.address_line_2.data,
                address_line_3=address_form.address_line_3.data,
                city=address_form.city.data,
                state=address_form.state.data,
                zip_code=address_form.zip_code.data,
                country=address_form.country.data,
                company=new_company
            )
            db.session.add(new_company)
            db.session.add(new_contact)
            db.session.add(new_address)
            
            # Assign default role based on the company_form.partner_type.data
            if company_form.partner_type.data == 'MCXCustomer':
                default_role_name = 'MCXCustomer Admin'
            else:
                default_role_name = 'Company User'
            default_role = Role.query.filter_by(name=default_role_name).first()
            if default_role:
                current_user.roles.append(default_role)
            else:
                flash(f'Role {default_role_name} not found.', 'error')

            try:
                db.session.commit()
                flash('Registration successful!', 'success')
                # Example: sending an invitation to a department within the MCXCustomer
                # Adjust the function call as per your implementation
                # send_invitation(new_company.id, 'Sales', 'Sales Manager')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error during registration: {str(e)}', 'error')
    return render_template('register_company.html', company_form=company_form, contact_form=contact_form, address_form=address_form)

@app.route('/send_invitations')
@login_required
def send_invitations():
    mcxcustomer_id = current_user.mcxcustomer_id  # Assuming this attribute exists
    send_trading_partner_invitations(mcxcustomer_id)
    flash('Invitations sent successfully!', 'success')
    return redirect(url_for('dashboard'))


        

    @app.route('/register_partner', methods=['GET', 'POST'])
    def register_partner(invitation_token):
    # Decode invitation token to prefill or determine the registration flow
    decoded_info = decode_invitation_token(invitation_token)
    # Show registration forms prefilled with decoded information
    # On POST, validate forms and create partner instances

        else:  # Handling registration for trading partners
        # If using invitation tokens
        invitation_token = request.form.get('invitation_token')
        invitation = Invitation.query.filter_by(token=invitation_token).first()
        if not invitation:
            flash('Invalid or expired invitation token.', 'error')
            return render_template('register_company.html', form=form)
    
        # Create a new instance for the trading partner
        # Here, partner_type can be Vendor, Buyer, etc., depending on your form's input
            new_partner = create_partner_instance_from_form(form, partner_type, invitation.mcxcustomer_id)
        db.session.add(new_partner)
    
        # Assigning default roles/permissions based on the user_type
        user_role = UserRole[form.user_type.data.upper()]
        assign_role_to_user(current_user, user_role)

        # Link this new partner to the MCXCustomer who sent the invitation
        # This could be direct association or through a relationship table
            new_partner.mcxcustomer_id = invitation.mcxcustomer_id

         def send_invitations_to_trading_partners(mcxcustomer, department_type, user_type):
        # Example logic to send invitations
            for partner_type in [Vendor, Buyer, ImportServiceProvider, ExportServiceProvider]:
            invitation_token = generate_invitation_token(mcxcustomer, department_type, user_type, partner_type)
            send_invitation_email(partner_type, invitation_token)
        # Ensure you have a mechanism to generate and handle these invitation tokens

        else:
            # Handle registration for trading partners
            # This could involve checking invitation tokens or directly linking to the MCXCustomer
            # based on the user's selections or inputs

        if request.method == 'POST' and form.validate():
        # Custom validation logic to check if company_name already exists
        existing_company = Company.query.filter_by(company_name=form.company_name.data).first()
        if existing_company:
            flash('Company with this name already exists.', 'error')
            return render_template('register_company.html', form=form) 
    
        try:
            db.session.commit()
            flash('Company, contact, and address registered successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error occurred. Company registration failed.', 'error')
            print(e)  # Consider using logging in production

    return render_template('register_company.html', form=form)



@app.route('/api/airports')
def get_airports():
    airports = Airport.query.all()
    airports_data = [{'id': airport.id, 'country_name': airport.country_name, 'airport_name': airport.airport_name} for airport in airports]
    return jsonify(airports_data)

Step 4: Use Enums in Application Logic
When creating or updating a VPC, BSC, IFC, or EFC instance, use the enum to refer to specific airports:

python
Copy code
# Example of how to set an airport for a contract
vpc = VPC()
vpc.origin_airport_id = Airport.query.filter_by(orig=AirportEnum.HERAT.value).first().id































@app.route('/register_company', methods=['GET', 'POST'])
@login_required  
def register_company():
    form = CompanyForm(request.form)
    if request.method == 'POST' and form.validate():
        # Extract data from form
        company_name = form.company_name.data
        bu_number = form.bu_number.data
        bu_activity_type = form.bu_activity_type.data
        global_hq = form.global_hq.data
        regional_hq = form.regional_hq.data
        country_hq = form.country_hq.data
        corporate_office = form.corporation_office.data
        regional_office = form.regional_office.data
        country_office = form.country_office.data
        branch_office = form.branch_office.data
        manufacturer = form.manufacturer.data
        distributor = form.distributor.data
        wholesaler = form.wholesaler.data
        retailer = form.retailer.data
        trader = form.trader.data
        distribution_center = form.distribution_center.data
        parts_center = form.parts_center.data
        warehouse = form.warehouse.data

        # Perform your custom validation logic here
        # For example, check if company_name already exists
        existing_company = Company.query.filter_by(company_name=company_name).first()
        if existing_company:
            flash('Company with this name already exists.', 'error')
            return render_template('register_company.html', form=form)

        # Create new instances for related models as necessary
        new_company = Company(company_name=company_name)
        new_bu_number = BuNumber(bu_number=bu_number)
        new_bu_activity_type = BUActivity(bu_activity=bu_activity)
        new_global_hq = GlobalHq(global_hq=global_hq)
        new_regional_hq = RegionalHq(regional_hq=regional_hq)
        new_country_hq = CountryHq(country_hq=country_hq)
        new_corporate_office = CorporateOffice(corporation_office=corporation_office)
        new_regional_office = regionalOffice(regional_office=regional_office)
        new_country_office = CountryOffice(country_office=country)
        new_manufacturer = Manufacturer(manufacturer=manufacturer)
        new_distributor = Distributor(distributor=distributor)
        new_wholesaler = Wholesaler(wholesaler=wholesaler)
        new_retailer = Retailer(retailer=retailer)
        new_trader = Trader(trader=trader)
        new_distribution_center = DistributionCenter(distribution_center=distribution_center)
        new_parts_center = PartsCenter(parts_center=parts_center)
        new_warehouse = Warehouse(warehouse=warehouse)
        
        # Create an Address instance from form data
        address_id = db.Column(db.BigInteger, db.ForeignKey('address.id'), nullable=True)
        new_address_line_1 = AddressLine(address_line_1=AddressLine)
        new_address_line_2 = AddressLine(address_line_2=AddressLine)
        new_address_line_3 = AddressLine(address_line_3=AddressLine_3)
        city = City(city=City)
        state = State(state=State)
        zip_code = ZipCode(zip_code=ZipCode)
        country = Country(country=Country)

        # You might need to associate the new address with the new company
        # new_company.address = new_address

        # Create an Department instance from form data
        new_supply_chain = SupplyChain(supply_chain=supply_chain)
        new_procurement = Procurement(procurement=procurement)
        new_finance = Finance(finance=finance)
        new_logistics = Logistics(logistics=logistics)
        new_production = Production(production=production)
        new_assembly =assembly(assembly=assembly)
        new_operations = Operations(operations=operations)
        new_sales_operations = Operations(operations=operations)
        new_accounts_payable = AccountsPayable(accounts_payable=accounts_payable)
        new accounts_receivable = AccountsReceivable(accounts_receivable=accounts_receivable)

        # Create an Title instance from form data
        new_chief_executive_officer = ChiefExecutiveOfficer(chief_executive_officer=chief_executive_officer)
        new_chief_operations_officer = ChiefOperationsOfficer(chief_operations_officer=chief_executive_officer)
        new_chief_finance_officer = ChiefFinanceOfficer(chief_finance_officer=chief_finance_officer)
        new_chief_procurement_officer = ChiefProcurementOfficer(chief_procurement_officer=chief_procurement_officer)
        new_managing_director = ManagingDirector(managing_director=managing_director)
        new_general_manager = GeneralManager(general_manager=general_manager)
        new_branch_manager = BranchManager(branch_manager=branch_manager)
        new_bu_head = BUHead(bu_head=bu_head)
        new_division_manager =divisionManager(division_manager=division_manager)
        new_finance_operations_officer = FinanceOperationsOfficer(finance_operations_officer=finance_operations_officer)
        new_senior_vice_president = SeniorVicePresident(senior_vice_president=senior_vice_president)
        new_vice_president = VicePresident(vice_president=vice_president)
        new_senior_director = SeniorDirector(senior_director=senior_director)
        new_director = Director(director=director)
        new_senior_manager = SeniorManager(senior_manager=senior_manager)
        new_manager = Manager(manager=manager)
        new_officer = Officer(officer=officer)
        new_supervisor = supervisor(supervisor=supervisor)
        new_executive = Executive(executive=executive)
        
         # Create an Approver Role instance from form data
        new_global_principal_admin = GlobalPrincipalAdmin(global_principal_admin=global_principal_admin)
        new_regional_principal_admin = RegionalPrincipalAdmin(regional_principal_admin=regional_principal_admin)
        new_country_principal_admin = CountryPrincipalAdmin(country_principal_admin=country_principal_admin)
        new_global_supply_chain_admin = GlobalSupplyChain((global_supply_chain_admin=global_supply_chain_admin)
        new_regional_supply_chain_admin = RegionalSupplyChainAdmin(regional_supply_chain_admin=regional_supply_chain_admin)
        new_country_supply_chain_admin = CountrySupplyChainAdmin(country_supply_chain_admin=country_suply_chain_admin)
        new_global_procurement_admin = GlobalProcurementAdmin(global_procurement_admin=global_procurement_admin)
        new_regional_procurement_admin = RegionalProcurementAdmin(regional_procurement_admin=regional_procurement_admin)
        new_country_procurement_admin = CountryProcurementAdmin(country_procurement_admin=country_procurement_admin)
        new_global_finance_admin = GlobalFinanceAdmin(global_finance_admin=global_finance_admin)
        new_regional_finance_admin = RegionalFinanceAdmin(regional_finance_admin=regional_finance_admin)
        new_country_finance_admin = CountryFinanceAdmin(country_finance_admin=country_finance_admin)
        new_global_logistics_admin = GlobalLogisticsAdmin(global_logistics_admin=global_logistics_admin)
        new_regional_logistics_admin =ionalLogisticsAdmin(regional_logistics_admin=regional_logistics_admin)
        new_country_logistics_admin = CountryLogisticsAdmin(country_logistics_admin=country_logistics_admin)

        db.session.add(new_company)
        try:
            db.session.commit()
            flash('Company registered successfully!', 'success')
            return redirect(url_for('some_route_after_success'))  # Redirect to another page on success
        except Exception as e:
            db.session.rollback()  # Important to avoid partial commits
            flash('Error registering company.', 'error')
            print(e)  # For debugging purposes, consider logging this instead

    return render_template('register_company.html', form=form)


4. Flask Application (mcxocr.py)
In your Flask application, you'll create endpoints for training and inference.

python
Copy code
from flask import Flask, request, jsonify
from services.ocr_service import ocr_service

app = Flask(__name__)

@app.route('/train', methods=['POST'])
def train_model():
    # Endpoint to trigger training
    # You'll need to handle how the training data is provided
    train_data = request.json.get('data')
    ocr_service.train(train_data)
    return jsonify({"message": "Training started"}), 200

@app.route('/infer', methods=['POST'])
def infer_image():
    # Endpoint for OCR inference
    # You'll need to handle how the image is received (e.g., as a file upload)
    image = request.files['image']
    extracted_text = ocr_service.infer(image)
    return jsonify({"extracted_text": extracted_text}), 200

if __name__ == '__main__':
    app.run(debug=True)


















# Set up login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Sample User model
class User(UserMixin, db.Model):
    id = db.Column(db.String(100), primary_key=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Sample database for user storage
users_db = {}

@login_manager.user_loader
def load_user(username):
    return users_db.get(username)

def user_can_register(username, password):
    # Check if the username is already taken
    if username in users_db:
        return False, "Username already exists"
    
    # Validate password (e.g., minimum length, complexity requirements)
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Hash the password before storing it
    hashed_password = generate_password_hash(password)
    
    # Store the user in the database
    users_db[username] = User(username, hashed_password)
    return True, "Registration successful"

# Custom decorator to check if a user has a specific role
def roles_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_roles' in g and required_role in g.user_roles:
                return func(*args, **kwargs)
            else:
                return jsonify({'message': 'Access Forbidden. Insufficient permissions.'}), 403

        return wrapper

    return decorator

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users_db.get(username)

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))  # Redirect to a dashboard or appropriate page
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Attempt to register the user
        registration_success, message = user_can_register(username, password)

        if registration_success:
            # Log in the user after successful registration
            user = users_db.get(username)
            login_user(user)
            flash('Registration successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(message, 'error')

    # Fetch the plan details from Stripe to display on the signup page
    return render_template('signup.html')

@app.route('/get-plan-details/<plan_id>', methods=['GET'])
def get_plan_details(plan_id):
    try:
        # Retrieve the plan details from Stripe using the plan_id
        plan = stripe.Plan.retrieve(plan_id)

        # Extract pricing information from the plan (modify based on your plan structure)
        amount = plan.amount

        # Return the amount to the client-side JavaScript
        return jsonify({'amount': amount}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    return "Welcome to the dashboard!"


# Example: Route restricted to users with the 'admin' role
@app.route('/admin', methods=['GET'])
@login_required
@roles_required('admin')
def admin_dashboard():
    return "Welcome to the admin dashboard!"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Error handler for 403 Forbidden
@app.errorhandler(403)
def handle_403(error):
    return "Access Denied", 403

def user_can_register(username, password):
    # Check if the username is already taken
    if username in users_db:
        return False, "Username already exists"

    # Validate password (e.g., minimum length, complexity requirements)
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    # Store the user in the database
    user = User(id=username, password_hash=hashed_password)
    users_db[username] = user
    return True, "Registration successful"


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
    

# RBAC Functions and Route
def roles_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_roles' in g and required_role in g.user_roles:
                return func(*args, **kwargs)
            else:
                return jsonify({'message': 'Access Forbidden. Insufficient permissions.'}), 403
        return wrapper
    return decorator

@app.route('/checkrole', methods=['GET'])
@login_required
def checkrole():
    required_role = request.args.get('role')

    if not required_role:
        return jsonify({'message': 'Invalid role provided.'}), 400

    if has_role(current_user.id, required_role):
        return jsonify({'message': f'User has the required role: {required_role}.'})
    else:
        return jsonify({'message': f'User does not have the required role: {required_role}.'}), 403

@app.route('/some-protected-route')
@login_required
@roles_required('some_role')
def protected_route():
    # Your route logic here
    if 'some_role' in current_user.roles:
        # User has 'some_role', perform some action
        return "Access granted to some_role: You can perform some special actions here."
    else:
        # User doesn't have 'some_role', handle accordingly
        return "You don't have the required role to access this route."

    # Check if the user has specific permissions within RBAC
        if has_permission(current_user.id, 'can_subscribe'):
            # User can subscribe, perform subscription logic here
            result = "You can subscribe to plans."
        elif has_permission(current_user.id, 'can_view'):
            # User can only view, no subscription allowed
            result = "You can view but cannot subscribe."

    return result
    else:
        # User doesn't have the required role, handle accordingly
        return "You don't have the required role to access this route."

# Error handler for 403 Forbidden
@app.errorhandler(403)
def handle_403(error):
    return "Access Denied", 403

if __name__ == '__main__':
    app.run(debug=True)

# Route for sign-up and KYC
# Function to encrypt data
def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())

@app.route('/company/<int:company_id>', methods=['GET'])
def get_company(company_id):
    company = Company.query.get_or_404(company_id)
    return jsonify(company.serialize())

@app.route('/address/<int:address_id>', methods=['GET'])
def get_address(address_id):
    address = Address.query.get_or_404(address_id)
    return jsonify(address.serialize())

# Function to decrypt data
def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()

# Function to check if a user has a specific role
def has_role(user, role):
    # Logic to check if the user has the specified role
    return role in user.roles

# Route for checking user roles
@app.route('/checkrole/<role>', methods=['GET'])
@login_required
def check_role(role):
    if has_role(current_user, role):
        return jsonify({'message': f'User has the {role} role.'})
    else:
        return jsonify({'message': f'User does not have the {role} role.'}), 403  

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        mcxcustomer_name = data.get('mcxcustomer_name')
        mcxcustomer_bu_number = data.get('mcxcustomer_business_unit_number')
        mcxcustomer_bu_name = data.get('mcxcustomer_business_unit_name')
        mcxcustomer_bu_contact_name = data.get('mcxcustomer_business_unit_contact_name')
        mcxcustomer_bu_approver_name = data.get('mcxcustomer_business_unit_approver_name')
        mcxcustomer_type = data.get('mcxcustomer_type')
        mcxcustomer_address = data.get('mcxcustomer_address')
        mcxcustomer_address_line_1 = data.get('mcxcustomer_address_line_1')
        mcxcustomer_address_line_2 = data.get('mcxcustomer_address_line_2')
        mcxcustomer_address_line_3 = data.get('mcxcustomer_address_line_3')
        mcxcustomer_city = data.get('mcxcustomer_city')
        mcxcustomer_state = data.get('mcxcustomer_state')
        mcxcustomer_zip = data.get('mcxcustomer_zip')
        mcxcustomer_country = data.get('mcxcustomer_country')
        kyc_details = data.get('kyc_details')

        # Create a new mcxcustomer instance and add it to the database
        new_mcxcustomer = McxCustomer(**data)
        db.session.add(new_mcxcustomer)
        db.session.commit()

        # Validate required fields
        if not all([mcxcustomer_name, kyc_details]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(kyc_details, encryption_key)

        # Create and store the McxCustomer
        account_number = create_mcxcustomer_db(mcxcustomer_account, new_mcxcustomer_name, encrypted_kyc)
        return jsonify({'mcxcustomer_account_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_mcxcustomer: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

def signup_and_kyc_customer(mcxcustomer_name, encrypted_kyc):
    # Generate a reference number for the MCXCustomer entity
    mcxcustomer_reference = generate_mcxcustomer_reference(mcxcustomer_name)

    # Create an MCXCustomer object
    mcxcustomer = create_mcxcustomer(mcxcustomer_reference)

    # Store customer data
    mcxcustomer.name = mcxcustomer_name
    mcxcustomer.encrypted_kyc = encrypted_kyc
    mcxcustomer.vendor = {
        'kyc', 'vendor_procurement_contract', 'import_freight_contract', 'vendor_procurement_contract_document_folder'
    }
    mcxcustomer.buyer = {
        'kyc', 'buyer_sales_contract', 'export_freight_contract', 'buyer_sales_contract_document_folder'
    }
    mcxcustomer.import_service_provider = {
        'kyc', 'import_freight_contract', 'import_freight_contract_document_folder'
    }
    mcxcustomer.export_service_provider = {
        'kyc', 'export_freight_contract', 'export_freight_contract_document_folder'
    }

    # Return the account number
    return mcxcustomer.account_number

# Example route to retrieve and decrypt KYC details
@app.route('/mcxcustomer_kyc/<account_number>', methods=['GET'])
def get_kyc_details(account_number):
    mcxcustomer = mcxcustomers.get(account_number)
    if mcxcustomer:
        encrypted_kyc = mcxcustomer.get('encrypted_kyc')
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        decrypted_kyc = decrypt_data(encrypted_kyc, encryption_key)
        
        # Return the customer details including KYC
        return jsonify({
            'mcxcustomer_name': mcxcustomer['mcxcustomer_name'],
            'mcxcustomer_bu_number': mcxcustomer['mcxcustomer_business_unit_number'],
            'mcxcustomer_bu_name': mcxcustomer['mcxcustomer_business_unit_name'],
            'mcxcustomer_bu_contact_name': mcxcustomer['mcxcustomer_business_unit_contact_name'],
            'mcxcustomer_bu_approver_name': mcxcustomer['mcxcustomer_business_unit_approver_name'],
            'mcxcustomer_type': mcxcustomer['mcxcustomer_type'],
            'mcxcustomer_address': mcxcustomer['mcxcustomer_address'],
            'mcxcustomer_address_line_1': mcxcustomer['mcxcustomer_address_line_1'],
            'mcxcustomer_address_line_2': mcxcustomer['mcxcustomer_address_line_2'],
            'mcxcustomer_address_line_3': mcxcustomer['mcxcustomer_address_line_3'],
            'mcxcustomer_city': mcxcustomer['mcxcustomer_city'],
            'mcxcustomer_state': mcxcustomer['mcxcustomer_state'],
            'mcxcustomer_zip': mcxcustomer['mcxcustomer_zip'],
            'mcxcustomer_country': mcxcustomer['mcxcustomer_country'],
            'kyc_details': decrypted_kyc
        }), 200
    else:
        return jsonify({'error': 'MCX Customer not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

# Stripe payment route
@app.route('/subscribe', methods=['POST'])
@login_required  # Requires the user to be logged in
def subscribe():
    try:
        # Get the current user's email (you may have a different way of doing this)
        customer_email = current_user.email  # Replace with your user object's email field

        # Retrieve the pricing table ID and token from the POST request
        pricing_table_id = request.form['pricing_table_id']
        token = request.form['stripeToken']

        # Create a subscription using the Stripe API
        subscription = stripe.Subscription.create(
            customer=customer_email,
            items=[{'price': pricing_table_id}],  # Subscribe to the selected pricing table
            source=token,  # Payment source (credit card token)
        )

        # You can save the subscription details to your database if needed

        return 'Subscription successful! Thank you for subscribing.'

    except stripe.error.StripeError as e:
        return f'Error: {e.user_message}', 400

# ... Other routes and configurations ...

if __name__ == '__main__':
    app.run(debug=True)

# Function to encrypt data
def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())

# Function to decrypt data
def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()

# Function to check if a user has a specific role
def has_role(user, role):
    # Logic to check if the user has the specified role
    return role in user.roles

# Route for checking user roles
@app.route('/checkrole/<role>', methods=['GET'])
@login_required
def check_role(role):
    if has_role(current_user, role):
        return jsonify({'message': f'User has the {role} role.'})
    else:
        return jsonify({'message': f'User does not have the {role} role.'}), 403

@app.route('/createvendor', methods=['POST'])
def create_vendor_db_route():
    try:
        # Extract data from the request
        data = request.json
        mcxcustomer_account = data.get('mcxcustomer_account')
        vendor_name = data.get('vendor_name')
        vendor_bu_number = data.get('vendor_bu_number')
        vendor_bu_name = data.get('vendor_bu_name')
        vendor_bu_contact_name = data.get('vendor_bu_contact_name')
        vendor_bu_approver_name = data.get('vendor_bu_approver_name')
        vendor_type = data.get('vendor_type')
        vendor_address = data.get('vendor_address')
        vendor_address_line_1 = data.get('vendor_address_line_1')
        vendor_address_line_2 = data.get('vendor_address_line_2')
        vendor_address_line_3 = data.get('vendor_address_line_3')
        vendor_city = data.get('vendor_city')
        vendor_state = data.get('vendor_state')
        vendor_zip = data.get('vendor_zip')
        vendor_country = data.get('vendor_country')
        kyc_details = data.get('kyc_details')
        
# Create a new Vendor using the create_vendor function from utils.py
        vendor = create_vendor(vendor_name, mcxcustomer_account)

        # Generate a reference number for the Vendor using the generate_vendor_reference function from utils.py
        vendor_reference = generate_vendor_reference(
            'VND', vendor_name, business_unit_name, business_unit_number, vendor_account_number, 'Vendor', 'REF')

        # Placeholder dictionary to simulate a database
        vendor_db = {}

# Add the Vendor to the database
        vendor_db[vendor_reference] = {
            'mcxcustomer_account_number': mcxcustomer_account_number,
            'vendor_name': vendor_name,
            'vendor_bu_number': vendor_bu_number,
            'vendor_bu_name': vendor_bu_name,
            'vendor_bu_contact_name': vendor_bu_contact_name,
            'vendor_bu_approver_name': vendor_bu_approver_name,
            'vendor_type': vendor_type,
            'vendor_address': vendor_address,
            'vendor_address_line_1': vendor_address_line_1,
            'vendor_address_line_2': vendor_address_line_2,
            'vendor_address_line_3': vendor_address_line_3,
            'vendor_city': vendor_city,
            'vendor_state': vendor_state,
            'vendor_zip': vendor_zip,
            'vendor_country': vendor_country,
            'kyc_details': kyc_details,
        }
# Create a new Vendor instance and add it to the database (if necessary)
        new_vendor = Vendor(**data)
        db.session.add(new_vendor)
        db.session.commit()

        # Validate required fields
        if not all([mcxcustomer_account, vendor_name, kyc_details]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(kyc_details, encryption_key)

        # Create and store the vendor (if necessary)
        account_number = create_vendor_db(mcxcustomer_account, vendor_name, encrypted_kyc)
        return jsonify({'vendor_account_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_vendor_db_route: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Vendor Creation Route
def create_vendor_db(mcxcustomer_account, vendor_name, encrypted_kyc):
    # Generate a reference number for the vendor entity
    vendor_reference = mcx_customer.generate_reference_number("VND")

    # Create a Vendor object (if necessary)
    vendor = Vendor(vendor_reference, mcx_customer)
    # Store vendor data (if necessary)
    vendor.name = vendor_name
    vendor.encrypted_kyc = encrypted_kyc
    vendor = {
        'kyc', 'vendor_procurement_contract', 'vendor_procurement_contract_document_folder'
    }
    import_service_provider = {
        'kyc', 'import_freight_contract', 'import_freight_contract_document_folder'
    }

    # Return the account number (if necessary)
    return vendor.account_number

# Vendor Retrieval Route
@app.route('/vendor/<vendor_account_number>', methods=['GET'])
def get_vendor(vendor_account_number):  # Corrected parameter name
    vendor_data = vendor_db.get(vendor_account_number)
    if vendor_data:
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        decrypted_kyc = decrypt_data(vendor_data['encrypted_kyc'], encryption_key)
        return jsonify({
            'vendor_name': vendor_data['vendor_name'],
            'vendor_bu_number': vendor_data['vendor_bu_number'],
            'vendor_bu_name': vendor_data['vendor_bu_name'],
            'vendor_bu_contact_name': vendor_data['vendor_bu_contact_name'],
            'vendor_bu_approver_name': vendor_data['vendor_bu_approver_name'],
            'vendor_type': vendor_data['vendor_type'],
            'vendor_address': vendor_data['vendor_address'],
            'vendor_address_line_1': vendor_data['vendor_address_line_1'],
            'vendor_address_line_2': vendor_data['vendor_address_line_2'],
            'vendor_address_line_3': vendor_data['vendor_address_line_3'],
            'vendor_city': vendor_data['vendor_city'],
            'vendor_state': vendor_data['vendor_state'],
            'vendor_zip': vendor_data['vendor_zip'],
            'vendor_country': vendor_data['vendor_country'],
            'kyc_details': decrypted_kyc
        })
    else:
        return jsonify({'error': 'Vendor not found'}), 404

# Route to create a folder for a vendor procurement contract
@app.route('/create/vendor_procurement_contract_document/folder', methods=['POST'])
@login_required  # Ensure MCXCustomer is authenticated
def create_vendor_procurement_contract_document_folder():
    try:
        data = request.json
        # Validate and extract necessary data
        vendor_procurement_contract_document_folder_name = data.get('vendor_procurement_contract_document_folder_name')
        vendor_procurement_contract_document_folder_number = data.get('vendor_procurement_contract_document_folder_number')
        vendor_name = data.get('vendor_name')
        vendor_account_number = data.get('vendor_account_number')
        vendor_id = data.get('vendor_id')

        # Create instances of reference number generators for different entities
        vendor_procurement_contract_document_folder_reference_generator = ReferenceNumberGenerator('VPCDF')

        # Generate a reference number for the document folder
        vendor_procurement_contract_document_folder_reference = vendor_procurement_contract_document_folder_reference_generator.generate_reference_number(
            'VendorProcurementContractDocumentFolder', vendor_procurement_contract_document_folder_number)

        # Validate required fields
        if not all([vendor_name, vendor_account_number, vendor_procurement_contract_document_folder_number]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details if needed
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(kyc_details, encryption_key)

        # Create and store the vendor procurement contract document folder in your database
        new_vendor_procurement_contract_document_folder = VendorProcurementContractDocumentFolder(
            vendor_procurement_contract_document_folder_name=vendor_procurement_contract_document_folder_name,
            vendor_procurement_contract_document_folder_reference=vendor_procurement_contract_document_folder_reference,
            vendor_procurement_contract_document_folder_number=vendor_procurement_contract_document_folder_number,
            vendor_name=vendor_name,
            vendor_account_number=vendor_account_number,
            vendor_id=vendor_id,
            encrypted_kyc=encrypted_kyc
        )
        db.session.add(new_vendor_procurement_contract_document_folder)
        db.session.commit()

        # Make an HTTP POST request to the Python utility API to get the reference number
        payload = {
            'folder_type': 'VendorProcurementContractDocumentFolder',
            'folder_number': vendor_procurement_contract_document_folder_number,
            'other_data': 'other_data',  # Include any other relevant data
        }

        response = requests.post('http://your-python-utility-api-url/generate-reference-number', json=payload)

        if response.status_code == 200:
            # The request was successful, extract the reference number from the response
            reference_number = response.json().get('reference_number')

            # You can use the 'reference_number' in your application as needed
            # ...

            return jsonify({'vendor_procurement_contract_document_folder_number': reference_number}), 201
        else:
            return jsonify({'error': 'Failed to generate reference number'}), 500

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_vendor_procurement_contract_document_folder: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/createvendorprocurementcontract', methods=['POST'])
def create_vendor_procurement_contract():
    try:
        data = request.json
        mcxcustomer_account_number = data.get('mcxcustomer_account_number')
        vpc_code = data.get('vpc_code')
        vendor_name = data.get('vendor_name')
        vendor_account_number = data.get('vendor_account_number')
        vendor_id = data.get('vendor_id')
        vendor_procurement_contract_number = data.get('vendor_procurement_contract_number')
        vendor_procurement_contract_id = data.get('vendor_procurement_contract_id')
        vendor_business_unit_name = data.get('vendor_business_unit_name')
        vendor_business_unit_number = data.get('vendor_business_unit_number')
        kyc_details = data.get('kyc_details')

        # Retrieve the reference or identifier of the associated Vendor Procurement Contract Document Folder
        document_folder_reference = data.get('VPCDF')

        # Create a new vendor procurement contract instance and associate it with the Document Folder
        new_vendor_procurement_contract = VendorProcurementContract(
            mcxcustomer_account_number=mcxcustomer_account_number,
            vpcdf=vpcdf  # Associate with Document Folder Reference
            vpc_code=vpc_code,
            vendor_name=vendor_name,
            vendor_bu_name=vendor_bu_name,
            vendor_bu_number=vendor_bu_number,
            vendor_account_number=vendor_account_number,
            vendor_procurement_contract_number=vendor_procurement_contract_number,
            encrypted_kyc=kyc_details,
        )

        db.session.add(new_vendor_procurement_contract)
        db.session.commit()

        # Validate required fields
        if not all([mcxcustomer_account, vpcdf_code, vpc_code, vendor_name, vendor_bu_name, vendor_bu_number, vendor_account_number, vendor_procurement_contract_number, kyc_details]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(kyc_details, encryption_key)

        # Create and store the vendor_procurement_contract
        account_number = create_vendor_procurement_contract_db(mcxcustomer_account, vpcdf_code, vpc_code, vendor_name, vendor_bu_name, vendor_bu_number, vendor_account_number, vendor_procurement_contract_number, encrypted_kyc)
        return jsonify({'vendor_procurement_contract_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_vendor_procurement_contract: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Vendor Procurement Contract Creation Route
def create_vendor_procurement_contract_db(mcxcustomer_account_number, vpcdf_code, vpc_code, vendor_name, vendor_bu_name, vendor_bu_number, vendor_account_number, vendor_procurement_contract_number, encrypted_kyc):
    # Implement the logic to generate the account number based on your requirements
    account_number = generate_vendor_procurement_contract_reference_number()  # Implement this function
    # Assuming vendor procurement contract is a dictionary to store vendor procurement contract data
    vendor_procurement_contract[account_number] = {
        'mcxcustomer_account_number': mcxcustomer_account_number,
        'vpcdf_code': vpcdf_code,
        'vpc_code': vpc_code,
        'name': vendor_name,
        'vendor_bu_name': vendor_bu_name,
        'vendor_bu_number': vendor_bu_number, 
        'vendor_account_number': vendor_account_number,
        'vendor_procurement_contract_number': vendor_procurement_contract_number
        'encrypted_kyc': encrypted_kyc,
        'vendor_procurement_contract': {},
        'vendor_procurement_contract_document_folder': {}
    }
    return account_number

# Vendor Procurement Contract Retrieval Route
@app.route('/VendorProcurementContract/<vendor_procurement_contract_account_number>', methods=['GET'])
def get_vendor_procurement_contract(vendor_procurement_contract_account_number):
    vendor_procurement_contract_data = vendor_procurement_contract.get(vendor_procurement_contract_account_number)
    if vendor_procurement_contract_data:
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        decrypted_kyc = decrypt_data(vendor_procurement_contract_data['encrypted_kyc'], encryption_key)
        return jsonify({
            'mcxcustomer_account_number': mcxcustomer_data['mcxcustomer_account_number'],
            'vpcdf_code': vendor_procurement_contract_data['vpcdf_code'],
            'vpc_code': vendor_procurement_contract_data['vpc_code'],
            'vendor_name': vendor_procurement_contract_data['vendor_name'],
            'vendor_bu_name': vendor_procurement_contract_data['vendor_bu_name'],
            'vendor_bu_number': vendor_procurement_contract_data['vendor_bu_number'],
            'vendor_procurement_contract_number': vendor_procurement_contract_data['vendor_procurement_contract_number'],
            'encrypted_kyc': decrypted_kyc,
        })
    else:
        return jsonify({'error': 'Vendor Procurement Contract not found'}), 404

# Example function to receive and store a document in the specified folder
def receive_and_store_document(vpcdf_code, vpc_code, vendor_name, vendor_account_number, vendor_bu_name, vendor_bu_number, document_type, document_data):
    try:
        # Determine the document class based on the document type
        if document_type == 'VendorPurchaseOrder':
            document_class == VendorPurchaseOrder
        elif document_type == 'VendorInvoice':
            document_class == VendorInvoice
        elif document_type == 'VendorPackingList':
            document_class == VendorPackingList
        elif document_type == 'VendorGoodsReceiptNote':
            document_class == VendorGoodsReceiptNote
        else:
            return {'error': 'Invalid document type'}, 400
        
        # Generate reference numbers
        document_reference = generate_document_reference(
            document_type, vpcdf_code, vpc_code, vendor_name, vendor_bu_name, vendor_bu_number, vendor_account_number, 'VendorProcurementContract', document_data['document_number']
        )

        # Create an instance of the document class
        document = document_class()
         
        # Create an instance of the document folder with appropriate arguments
        document_folder = VendorProcurementContractDocumentFolder(
            vpcdf_code, vpc_code, vendor_name, vendor_account_number, vendor_bu_name, vendor_bu_number
        )

        # Store the document in the document folder
        document_folder.store_document(document)
        
        # Save metadata in the database linking the document to the folder and contract
        store_document_metadata(
            document, document_folder, vpc_code
        )

        return {'message': f'{document_type} received and stored successfully.'}, 201
    except Exception as e:
        print(f"Exception in receive_and_store_document: {str(e)}")
        return {'error': 'Internal Server Error'}, 500

# Example usage to receive and store a Vendor Purchase Order
vpcdf_code = generate_vendor_procurement_contract_document_folder_reference()  # Replace with actual code to generate vpcdf_code using UUID
vpc_code = generate_vendor_procurement_contract_reference()  # Replace with actual code to generate vpc_code using UUID
# Replace with the actual vendor name entered by the user
vendor_name = 'VendorName'  # User should provide the actual vendor name
# Replace with the actual vendor account number generated using UUID or entered by the user
vendor_account_number = '12345'  # User should provide the actual vendor account number
# Replace with the actual vendor bu name entered by the user
vendor_bu_name = 'VendorBuName'  # User should provide the actual vendor bu name
# Replace with the actual vendor bu number generated using UUID or entered by the user
vendor_bu_number = '001'  # User should provide the actual vendor bu number
document_type = 'VendorPurchaseOrder'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'VPO123'  # User should provide the actual document number
# Use the generate_vendor_purchase_order_reference function to generate the VPO reference number
vpo_reference = generate_vendor_purchase_order_reference(
    vpcdf_code, vpc_code, vendor_name, vendor_bu_name, vendor_bu_number, vendor_account_number, document_number
)
document_data = {
    'document_number': vpo_reference,  # Use the generated VPO reference as the document number
    # Add other data for the Vendor Purchase Order here
}

response, status_code = receive_and_store_document(
    vpcdf_code, vpc_code, vpo_reference,   vendor_name,
    vendor_account_number, vendor_bu_name,
    vendor_bu_number, document_type, document_data
)

# Example usage to receive and store a Vendor Invoice
vpcdf_code = generate_vendor_procurement_contract_document_folder_reference()  # Replace with actual code to generate vpcdf_code using UUID
vpc_code = generate_vendor_procurement_contract_reference()  # Replace with actual code to generate vpc_code using UUID
# Replace with the actual vendor name entered by the user
vendor_name = 'VendorName'  # User should provide the actual vendor name
# Replace with the actual vendor account number generated using UUID or entered by the user
vendor_account_number = '12345'  # User should provide the actual vendor account number
# Replace with the actual vendor bu name entered by the user
vendor_bu_name = 'VendorBuName'  # User should provide the actual vendor bu name
# Replace with the actual vendor bu number generated using UUID or entered by the user
vendor_bu_number = '001'  # User should provide the actual vendor bu number
document_type = 'VendorInvoice'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'VINV123'  # User should provide the actual document number
# Use the generate_vendor_invoice_reference function to generate the VINV reference number
vinv_reference = generate_vendor_invoice_reference(
    vpc_code, vpcdf_code, vendor_name, vendor_bu_name, vendor_bu_number, vendor_account_number, document_number
)
document_data = {
    'document_number': vinv_reference,  # Use the generated VINV reference as the document number
    # Add other data for the Vendor Invoice here
}

response, status_code = receive_and_store_document(
    vpcdf_code, vinv_reference,  vpc_code, vendor_name,
    vendor_account_number, vendor_bu_name,
    vendor_bu_number, document_type, document_data
)

# Example usage to receive and store a Vendor Packing List
vpcdf_code = generate_vendor_procurement_contract_document_folder_reference()  # Replace with actual code to generate vpcdf_code using UUID
vpc_code = generate_vendor_procurement_contract_reference()  # Replace with actual code to generate vpc_code using UUID
# Replace with the actual vendor name entered by the user
vendor_name = 'VendorName'  # User should provide the actual vendor name
# Replace with the actual vendor account number generated using UUID or entered by the user
vendor_account_number = '12345'  # User should provide the actual vendor account number
# Replace with the actual vendor bu name entered by the user
vendor_bu_name = 'VendorBuName'  # User should provide the actual vendor bu name
# Replace with the actual vendor bu number generated using UUID or entered by the user
vendor_bu_number = '001'  # User should provide the actual vendor bu number
document_type = 'VendorPackingList'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'VPL123'  # User should provide the actual document number
# Use the generate_vendor_packing_list_reference function to generate the VPL reference number
vpl_reference = generate_vendor_packing_list_reference(
    vpc_code, vpcdf_code, vendor_name, vendor_bu_name, vendor_bu_number, vendor_account_number, document_number
)
document_data = {
    'document_number': vpl_reference,  # Use the generated VPL reference as the document number
    # Add other data for the Vendor Packing List
}

response, status_code = receive_and_store_document(
    vpcdf_code, vpl_code, vpl_reference, vendor_name,
    vendor_account_number, vendor_bu_name,
    vendor_bu_number, document_type, document_data
)

# Example usage to receive and store a Vendor Goods Receipt Note
vpcdf_code = generate_vendor_procurement_contract_document_folder_reference()  # Replace with actual code to generate vpcdf_code using UUID
vpc_code = generate_vendor_procurement_contract_reference()  # Replace with actual code to generate vpc_code using UUID
# Replace with the actual vendor name entered by the user
vendor_name = 'VendorName'  # User should provide the actual vendor name
# Replace with the actual vendor account number generated using UUID or entered by the user
vendor_account_number = '12345'  # User should provide the actual vendor account number
# Replace with the actual vendor bu name entered by the user
vendor_bu_name = 'VendorBuName'  # User should provide the actual vendor bu name
# Replace with the actual vendor bu number generated using UUID or entered by the user
vendor_bu_number = '001'  # User should provide the actual vendor bu number
document_type = 'VendorGoodsReceiptNote'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'VGRN123'  # User should provide the actual document number
# Use the generate_vendor_goods_receipt_note_reference function to generate the VINV reference number
vinv_reference = vendor_goods_receipt_note_reference(
    vpc_code, vpcdf_code, vendor_name, vendor_bu_name, vendor_bu_number, vendor_account_number, document_number
)
document_data = {
    'document_number': vgrn_reference,  # Use the generated VGRN reference as the document number
    # Add other data for the Vendor Goods Receipt Note here
}

response, status_code = receive_and_store_document(
    vpcdf_code, vgrn_reference,  vpc_code, vendor_name,
    vendor_account_number, vendor_bu_name,
    vendor_bu_number, document_type, document_data
)
if __name__ == '__main__':
    app.run(debug=True)


# Function to encrypt data
def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())

# Function to decrypt data
def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()

# Function to check if a user has a specific role
def has_role(user, role):
    # Logic to check if the user has the specified role
    return role in user.roles

# Route for checking user roles
@app.route('/checkrole/<role>', methods=['GET'])
@login_required
def check_role(role):
    if has_role(current_user, role):
        return jsonify({'message': f'User has the {role} role.'})
    else:
        return jsonify({'message': f'User does not have the {role} role.'}), 403

@app.route('/createbuyer', methods=['POST'])
def create_buyer_db_route():
    try:
        # Extract data from the request
        data = request.json
        mcxcustomer_account = data.get('mcxcustomer_account')
        buyer_name = data.get('vendor_name')
        buyer_bu_number = data.get('buyer_business_unit_number')
        buyer_bu_name = data.get('buyer_business_unit_name')
        buyer_bu_contact_name = data.get('buyer_business_unit_contact_name')
        buyer_bu_approver_name = data.get('buyer_business_unit_approver_name')
        buyer_type = data.get('buyer_type')
        buyer_address = data.get('buyer_address')
        buyer_address_line_1 = data.get('buyer_address_line_1')
        buyer_address_line_2 = data.get('buyer_address_line_2')
        buyer_address_line_3 = data.get('buyer_address_line_3')
        buyer_city = data.get('buyer_city')
        buyer_state = data.get('buyer_state')
        buyer_zip = data.get('buyer_zip')
        buyer_country = data.get('buyer_country')
        kyc_details = data.get('kyc_details')
        
# Create a new Buyer using the create_buyer function from utils.py
        buyer = create_buyer(buyer_name, mcxcustomer_account)

        # Generate a reference number for the Buyer using the generate_buyer_reference function from utils.py
        buyer_reference = generate_buyer_reference(
            'BUY', buyer_name, business_unit_name, business_unit_number, buyer_account_number, 'Buyer', 'REF')

        # Placeholder dictionary to simulate a database
        buyer_db = {}

# Add the Buyer to the database
        Buyer_db[buyer_reference] = {
            'mcxcustomer_account_number': mcxcustomer_account_number,
            'buyer_name': buyer_name,
            'buyer_bu_number': buyer_bu_number,
            'buyer_bu_name': buyer_bu_name,
            'buyer_bu_contact_name': buyer_bu_contact_name,
            'buyer_bu_approver_name': buyer_bu_approver_name,
            'buyer_type': buyer_type,
            'buyer_address': buyer_address,
            'buyer_address_line_1': buyer_address_line_1,
            'buyer_address_line_2': buyer_address_line_2,
            'buyer_address_line_3': buyer_address_line_3,
            'buyer_city': buyer_city,
            'buyer_state': buyer_state,
            'buyer_zip': buyer_zip,
            'buyer_country': buyer_country,
            'kyc_details': kyc_details,
        }
# Create a new Buyer instance and add it to the database (if necessary)
        new_buyer = Buyer(**data)
        db.session.add(new_buyer)
        db.session.commit()

        # Validate required fields
        if not all([mcxcustomer_account, buyer_name, kyc_details]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(kyc_details, encryption_key)

        # Create and store the buyer (if necessary)
        account_number = create_buyer_db(mcxcustomer_account, buyer_name, encrypted_kyc)
        return jsonify({'buyer_account_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_buyer_db_route: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Buyer Creation Route
def create_buyer_db(mcxcustomer_account, buyer_name, encrypted_kyc):
    # Generate a reference number for the buyer entity
    buyer_reference = mcx_customer.generate_reference_number("BUY")

    # Create a Buyer object (if necessary)
    buyer = Buyer(buyer_reference, mcx_customer)
    # Store buyer data (if necessary)
    buyer.name = buyer_name
    buyer.encrypted_kyc = encrypted_kyc
    buyer = {
        'kyc', 'buyer_sales_contract', 'buyer_sales_contract_document_folder'
    }
    import_service_provider = {
        'kyc', 'export_freight_contract', 'export_freight_contract_document_folder'
    }

    # Return the account number (if necessary)
    return buyer.account_number

# Buyer Retrieval Route
@app.route('/buyer/<buyer_account_number>', methods=['GET'])
def get_buyer(buyer_account_number):  
    buyer_data = buyer_db.get(buyer_account_number)
    if buyer_data:
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        decrypted_kyc = decrypt_data(buyer_data['encrypted_kyc'], encryption_key)
        return jsonify({
            'buyer_name': buyer_data['buyer_name'],
            'buyer_bu_number': buyer_data['buyer_bu_number'],
            'buyer_bu_name': buyer_data['buyer_bu_name'],
            'buyer_bu_contact_name': buyer_data['buyer_bu_contact_name'],
            'buyer_bu_approver_name': buyer_data['buyer_bu_approver_name'],
            'buyer_type': buyer_data['buyer_type'],
            'buyer_address': buyer_data['buyer_address'],
            'buyer_address_line_1': buyer_data['buyer_address_line_1'],
            'buyer_address_line_2': buyer_data['buyer_address_line_2'],
            'buyer_address_line_3': buyer_data['buyer_address_line_3'],
            'buyer_city': buyer_data['buyer_city'],
            'buyer_state': buyer_data['buyer_state'],
            'buyer_zip': buyer_data['buyer_zip'],
            'buyer_country': buyer_data['buyer_country'],
            'kyc_details': decrypted_kyc
        })
    else:
        return jsonify({'error': 'Buyer not found'}), 404

# Route to create a folder for a buyer sales contract
@app.route('/create/buyer_sales_contract_document/folder', methods=['POST'])
@login_required  # Ensure MCXCustomer is authenticated
def create_buyer_sales_contract_document_folder():
    try:
        data = request.json
        # Validate and extract necessary data
        buyer_sales_contract_document_folder_name = data.get('buyer_sales_contract_document_folder_name')
        buyer_sales_contract_document_folder_number = data.get('buyer_sales_contract_document_folder_number')
        buyer_name = data.get('buyer_name')
        buyer_account_number = data.get('buyer_account_number')
        buyer_id = data.get('buyer_id')

        # Create instances of reference number generators for different entities
        buyer_sales_contract_document_folder_reference_generator = ReferenceNumberGenerator('BSCDF')

        # Generate a reference number for the document folder
        buyer_sales_contract_document_folder_reference = buyer_sales_contract_document_folder_reference_generator.generate_reference_number(
            'BuyerSalesContractDocumentFolder', buyer_sales_contract_document_folder_number)

        # Create a new buyer_sales_contract_document_folder instance and add it to the database
        new_buyer_sales_contract_document_folder = BuyerSalesContractDocumentFolder(
            buyer_sales_contract_document_folder_name=buyer_sales_contract_document_folder_name,
            buyer_sales_contract_document_folder_reference=buyer_sales_contract_document_folder_reference,
            buyer_sales_contract_document_folder_number=buyer_sales_contract_document_folder_number,
            buyer_name=buyer_name,
            buyer_account_number=buyer_account_number,
            buyer_id=buyer_id,
        )
        db.session.add(new_buyer_sales_contract_document_folder)
        db.session.commit()

        # Validate required fields
        if not all([buyer_name, buyer_account_number, buyer_sales_contract_document_folder_number]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details if needed
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(data.get('kyc_details'), encryption_key)

        # Create and store the buyer sales contract document folder
        account_number = create_buyer_sales_contract_document_folder_db(
            bscdf_code, bsc_code, buyer_name, buyer_account_number, buyer_bu_name,
            buyer_bu_number, buyer_sales_contract_document_folder_number, encrypted_kyc)
        return jsonify({'buyer_sales_contract_document_folder_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_buyer_sales_contract_document_folder: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/createbuyersalescontract', methods=['POST'])
def create_buyer_sales_contract():
    try:
        data = request.json
        mcxcustomer_account = data.get('mcxcustomer_account')
        buyer_name = data.get('buyer_name')
        buyer_account_number = data.get('buyer_account_number')
        buyer_id = data.get('buyer_id')
        buyer_sales_contract_number = data.get('buyer_sales_contract_number')
        buyer_sales_contract_id = data.get('buyer_sales_contract_id')
        bsc_code = data.get('bsc_code')
        buyer_bu_name = data.get('buyer_bu_name')
        buyer_bu_number = data.get('buyer_bu_number')
        kyc_details = data.get('kyc_details')

        # Retrieve the reference or identifier of the associated Buyer Sales Contract Document Folder
        document_folder_reference = data.get('BSCDF')

        # Create a new buyer sales contract instance and associate it with the Document Folder
        new_buyer_sales_contract = BuyerSalesContract(
            mcxcustomer_account_number=mcxcustomer_account_number,
            bscdf_code=bscdf_code, # Associate with Document Folder Reference
            bsc_code=bsc_code,
            buyer_name=buyer_name,
            buyer_bu_name=buyer_bu_name,
            buyer_bu_number=buyer_bu_number,
            buyer_account_number=buyer_account_number,
            buyer_sales_contract_number=buyer_sales_contract_number,
            encrypted_kyc=kyc_details,
        )

        db.session.add(new_buyer_sales_contract)
        db.session.commit()

        # Validate required fields
        if not all([mcxcustomer_account, bscdf_code, bsc_code, buyer_name, buyer_bu_name, buyer_bu_number, buyer_account_number, buyer_sales_contract_number, kyc_details]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(kyc_details, encryption_key)

        # Create and store the buyer_sales_contract
        account_number = create_buyer_sales_contract_db(mcxcustomer_account_number, bscdf_code, bsc_code, buyer_name, buyer_bu_name, buyer_bu_number, buyer_account_number, buyer_sales_contract_number, encrypted_kyc)
        return jsonify({'buyer_sales_contract_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_buyer_sales_contract: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Buyer Sales Contract Creation Route
def create_buyer_sales_contract_db(mcxcustomer_account, bscdf_code, bsc_code, buyer_name, buyer_bu_name, buyer_bu_number, buyer_account_number, buyer_sales_contract_number, encrypted_kyc):
    # Implement the logic to generate the account number based on your requirements
    account_number = generate_buyer_sales_contract_reference_number()  # Implement this function
    # Assuming buyer sales contract is a dictionary to store buyer sales contract data
    buyer_sales_contract[account_number] = {
        'mcxcustomer_account_number': mcxcustomer_account_number,
        'bscdf_code': bscdf_code,
        'bsc_code': bsc_code,
        'buyer_name': buyer_name,
        'buyer_bu_name': buyer_bu_name,
        'buyer_bu_number': buyer_bu_number, 
        'buyer_account_number': buyer_account_number,
        'buyer_sales_contract_number': buyer_sales_contract_number
        'encrypted_kyc': encrypted_kyc,
        'buyer_sales_contract': {},
        'buyer_sales_contract_document_folder': {}
    }
    return account_number

# Buyer Sales Contract Retrieval Route
@app.route('/BuyerSalesContract/<buyer_sales_contract_account_number>', methods=['GET'])
def get_buyer_sales_contract(buyer_sales_contract_account_number):
    buyer_sales_contract_data = buyer_sales_contract.get(buyer_sales_contract_account_number)
    if buyer_sales_contract_data:
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        decrypted_kyc = decrypt_data(buyer_sales_contract_data['encrypted_kyc'], encryption_key)
        return jsonify({
            'mcxcustomer_account_number': mcxcustomer_data['mcxcustomer_account_number'],
            'bscdf_code': buyer_sales_contract_data['bscdf_code'],
            'bsc_code': buyer_sales_contract_data['bsc_code'],
            'buyer_name': buyer_sales_contract_data['buyer_name'],
            'buyer_bu_name': buyer_sales_contract_data['buyer_bu_name'],
            'buyer_bu_number': buyer_sales_contract_data['buyer_bu_number'],
            'buyer_sales_contract_number': buyer_sales_contract_data['buyer_sales_contract_number'],
            'encrypted_kyc': decrypted_kyc,
        })
    else:
        return jsonify({'error': 'Buyer Sales Contract not found'}), 404

# Example function to receive and store a document in the specified folder
def receive_and_store_document(bscdf_code, bsc_code, buyer_name, buyer_account_number, buyer_bu_name, buyer_bu_number, document_type, document_data):
    try:
        # Determine the document class based on the document type
        if document_type == 'BuyerSalesOrder':
            document_class == BuyerSalesOrder
        elif document_type == 'BuyerInvoice':
            document_class == BuyerInvoice
        elif document_type == 'BuyerPackingList':
            document_class == BuyerPackingList
        elif document_type == 'BuyerGoodsReceiptNote':
            document_class == BuyerGoodsReceiptNote
        else:
            return {'error': 'Invalid document type'}, 400
        
        # Generate reference numbers
        document_reference = generate_document_reference(
            document_type, bscdf_code, bsc_code, buyer_name, buyer_bu_name, buyer_bu_number, buyer_account_number, 'BuyerSalesContract', document_data['document_number']
        )

        # Create an instance of the document class
        document = document_class()
         
        # Create an instance of the document folder with appropriate arguments
        document_folder = BuyerSalesContractDocumentFolder(
            bscdf_code, bsc_code, buyer_name, buyer_account_number, buyer_bu_name, buyer_bu_number
        )

        # Store the document in the document folder
        document_folder.store_document(document)
        
        # Save metadata in the database linking the document to the folder and contract
        store_document_metadata(
            document, document_folder, bsc_code
        )

        return {'message': f'{document_type} received and stored successfully.'}, 201
    except Exception as e:
        print(f"Exception in receive_and_store_document: {str(e)}")
        return {'error': 'Internal Server Error'}, 500

# Example usage to receive and store a Buyer Sales Order
bscdf_code = generate_buyer_sales_contract_document_folder_reference()  # Replace with actual code to generate bscdf_code using UUID
bsc_code = generate_buyer_sales_contract_reference()  # Replace with actual code to generate bsc_code using UUID
# Replace with the actual buyer name entered by the user
buyer_name = 'BuyerName'  # User should provide the actual buyer name
# Replace with the actual buyer account number generated using UUID or entered by the user
buyer_account_number = '12345'  # User should provide the actual buyer account number
# Replace with the actual buyer bu name entered by the user
buyer_bu_name = 'BuyerBuName'  # User should provide the actual buyer bu name
# Replace with the actual buyer bu number generated using UUID or entered by the user
buyer_bu_number = '001'  # User should provide the actual buyer bu number
document_type = 'BuyerSalesOrder'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'BSO123'  # User should provide the actual document number
# Use the generate_buyer_sales_order_reference function to generate the BSO reference number
bso_reference = generate_buyer_sales_order_reference(
    bscdf_code, bsc_code, buyer_name, buyer_bu_name, buyer_bu_number, buyer_account_number, document_number
)
document_data = {
    'document_number': bso_reference,  # Use the generated BSO reference as the document number
    # Add other data for the Buyer Sales Order here
}

response, status_code = receive_and_store_document(
    bscdf_code, bsc_code, bso_reference, buyer_name,
    buyer_account_number, buyer_bu_name,
    buyer_bu_number, document_type, document_data
)

# Example usage to receive and store a Buyer Invoice
bscdf_code = generate_buyer_sales_contract_document_folder_reference()  # Replace with actual code to generate vpcdf_code using UUID
bsc_code = generate_buyer_sales_contract_reference()  # Replace with actual code to generate vpc_code using UUID
# Replace with the actual buyer name entered by the user
buyer_name = 'BuyerName'  # User should provide the actual buyer name
# Replace with the actual buyer account number generated using UUID or entered by the user
buyer_account_number = '12345'  # User should provide the actual buyer account number
# Replace with the actual buyer bu name entered by the user
buyer_bu_name = 'BuyerBuName'  # User should provide the actual buyer bu name
# Replace with the actual buyer bu number generated using UUID or entered by the user
buyer_bu_number = '001'  # User should provide the actual buyer bu number
document_type = 'BuyerInvoice'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'BINV123'  # User should provide the actual document number
# Use the generate_buyer_invoice_reference function to generate the BINV reference number
binv_reference = generate_buyer_invoice_reference(
    bscdf_code, bsc_code, buyer_name, buyer_bu_name, buyer_bu_number, buyer_account_number, document_number
)
document_data = {
    'document_number': binv_reference,  # Use the generated BINV reference as the document number
    # Add other data for the Buyer Invoice here
}

response, status_code = receive_and_store_document(
    bscdf_code, bsc_code, binv_reference, buyer_name,
    buyer_account_number, buyer_bu_name,
    buyer_bu_number, document_type, document_data
)

# Example usage to receive and store a Buyer Packing List
bscdf_code = generate_buyer_sales_contract_document_folder_reference()  # Replace with actual code to generate bscdf_code using UUID
bsc_code = generate_buyer_sales_contract_reference()  # Replace with actual code to generate bsc_code using UUID
# Replace with the actual buyer name entered by the user
buyer_name = 'BuyerName'  # User should provide the actual buyer name
# Replace with the actual buyer account number generated using UUID or entered by the user
buyer_account_number = '12345'  # User should provide the actual buyer account number
# Replace with the actual buyer bu name entered by the user
buyer_bu_name = 'BuyerBuName'  # User should provide the actual buyer bu name
# Replace with the actual buyer bu number generated using UUID or entered by the user
buyer_bu_number = '001'  # User should provide the actual buyer bu number
document_type = 'BuyerPackingList'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'BPL123'  # User should provide the actual document number
# Use the generate_buyer_packing_list_reference function to generate the BPL reference number
bpl_reference = generate_buyer_packing_list_reference(
    bsc_code, bscdf_code, buyer_name, buyer_bu_name, buyer_bu_number, buyer_account_number, document_number
)
document_data = {
    'document_number': bpl_reference,  # Use the generated BPL reference as the document number
    # Add other data for the Buyer Packing List
}

response, status_code = receive_and_store_document(
    vpcdf_code, bsc_code, bpl_reference, buyer_name,
    buyer_account_number, buyer_bu_name,
    buyer_bu_number, document_type, document_data
)

# Example usage to receive and store a Buyer Goods Receipt Note
bscdf_code = generate_buyer_sales_contract_document_folder_reference()  # Replace with actual code to generate vpcdf_code using UUID
bsc_code = generate_buyer_sales_contract_reference()  # Replace with actual code to generate vpc_code using UUID
# Replace with the actual buyer name entered by the user
buyer_name = 'BuyerName'  # User should provide the actual buyer name
# Replace with the actual buyer account number generated using UUID or entered by the user
buyer_account_number = '12345'  # User should provide the actual buyer account number
# Replace with the actual buyer bu name entered by the user
buyer_bu_name = 'BuyerBuName'  # User should provide the actual buyer bu name
# Replace with the actual buyer bu number generated using UUID or entered by the user
buyer_bu_number = '001'  # User should provide the actual buyer bu number
document_type = 'BuyerGoodsReceiptNote'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'BGRN123'  # User should provide the actual document number
# Use the generate_buyer_goods_receipt_note_reference function to generate the BINV reference number
vinv_reference = buyer_goods_receipt_note_reference(
    bscdf_code, bsc_code, buyer_name, buyer_bu_name, buyer_bu_number, buyer_account_number, document_number
)
document_data = {
    'document_number': bgrn_reference,  # Use the generated BGRN reference as the document number
    # Add other data for the Buyer Goods Receipt Note here
}

response, status_code = receive_and_store_document(
    bscdf_code, bsc_code, bgrn_reference, buyer_name,
    buyer_account_number, buyer_bu_name,
    buyer_bu_number, document_type, document_data
)
if __name__ == '__main__':
    app.run(debug=True)


# Function to encrypt data
def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())

# Function to decrypt data
def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()

# Function to check if a user has a specific role
def has_role(user, role):
    # Logic to check if the user has the specified role
    return role in user.roles

# Route for checking user roles
@app.route('/checkrole/<role>', methods=['GET'])
@login_required
def check_role(role):
    if has_role(current_user, role):
        return jsonify({'message': f'User has the {role} role.'})
    else:
        return jsonify({'message': f'User does not have the {role} role.'}), 403

@app.route('/createimportserviceprovider', methods=['POST'])
def create_import_service_provider_db_route():
    try:
        # Extract data from the request
        data = request.json
        mcxcustomer_account = data.get('mcxcustomer_account')
        import_service_provider_name = data.get('import_service_provider_name')
        import_service_provider_bu_number = data.get('import_service_provider_business_unit_number')
        import_service_provider_bu_name = data.get('import_service_provider_unit_name')
        import_service_provider_bu_contact_name = data.get('import_service_provider_business_unit_contact_name')
        import_service_provider_bu_approver_name = data.get('import_service_provider_business_unit_approver_name')
        import_service_provider_type = data.get('import_service_provider_type')
        import_service_provider_address = data.get('import_service_provider_address')
        import_service_provider_address_line_1 = data.get('import_service_provider_address_line_1')
        import_service_provider_address_line_2 = data.get('import_service_provider_address_line_2')
        import_service_provider_address_line_3 = data.get('import_service_provider_address_line_3')
        import_service_provider_city = data.get('import_service_provider_city')
        import_service_provider_state = data.get('import_service_provider_state')
        import_service_provider_zip = data.get('import_service_provider_zip')
        import_service_provider_country = data.get('import_service_provider_country')
        kyc_details = data.get('kyc_details')
        
# Create a new Import Service Provider using the create_import_service_provider function from utils.py
        import_service_provider = create_import_service_provider(import_service_provider_name, mcxcustomer_account)

        # Generate a reference number for the Import Service Provider using the generate_import_service_provider_reference function from utils.py
        import_service_provider_reference = generate_import_service_provider_reference(
            'IMPSVC', import_service_provider_name, import_service_provider_bu_name, import_service_provider_bu_number, import_service_provider_account_number, 'ImpSvc', 'REF')

        # Placeholder dictionary to simulate a database
        import_service_provider_db = {}

# Add the Import Service Provider to the database
        import_service_provider_db[import_service_provider_reference] = {
            'mcxcustomer_account_number': mcxcustomer_account_number,
            'import_service_provider_name': import_service_provider_name,
            'import_service_provider_bu_number': import_service_provider_bu_number,
            'import_service_provider_bu_name': import_service_provider_bu_name,
            'import_service_provider_bu_contact_name': import_service_provider_bu_contact_name,
            'import_service_provider_bu_approver_name': import_service_provider_bu_approver_name,
            'import_service_provider_type': import_service_provider_type,
            'import_service_provider_address': import_service_provider_address,
            'import_service_provider_address_line_1': import_service_provider_address_line_1,
            'import_service_provider_address_line_2': import_service_provider_address_line_2,
            'import_service_provider_address_line_3': import_service_provider_address_line_3,
            'import_service_provider_city': import_service_provider_city,
            'import_service_provider_state': import_service_provider_state,
            'import_service_provider_zip': import_service_provider_zip,
            'import_service_provider_country': import_service_provider_country,
            'kyc_details': kyc_details,
        }
# Create a new Import Service Provider instance and add it to the database (if necessary)
        new_import_service_provider = ImportServiceProvider(**data)
        db.session.add(new_import_service_provider)
        db.session.commit()

        # Validate required fields
        if not all([mcxcustomer_account, import_service_provider_name, kyc_details]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(kyc_details, encryption_key)

        # Create and store the import service provider (if necessary)
        account_number = create_import_service_provider_db(mcxcustomer_account, import_service_provider_name, encrypted_kyc)
        return jsonify({'import_service_provider_account_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_import_service_provider_db_route: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Import Service Provider Creation Route
def create_import_service_provider_db(mcxcustomer_account, import_service_provider_name, encrypted_kyc):
    # Generate a reference number for the import service provider entity
    import_service_provider_reference = mcx_customer.generate_reference_number("ImpSvc")

    # Create a Import Service Provider object (if necessary)
    import_service_provider = import_service_provider(import_service_provider_reference, mcx_customer)
    # Store import service provider data (if necessary)
    import_service_provider.name = import_service_provider_name
    import_service_provider.encrypted_kyc = encrypted_kyc
    import_service_provider = {
        'kyc', 'import_freight_contract', 'import_freight_contract_document_folder'
    }

    # Return the account number (if necessary)
    return import_service_provider.account_number

# Import Service Provider Retrieval Route
@app.route('/import_service_provider/<import_service_provider_account_number>', methods=['GET'])
def get_import_service_provider(import_service_provider_account_number):  
    import_service_provider_data = import_service_provider_db.get(import_service_provider_account_number)
    if import_service_provider_data:
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        decrypted_kyc = decrypt_data(import_service_provider_data['encrypted_kyc'], encryption_key)
        return jsonify({
            'import_service_provider_name': import_service_provider_data['import_service_provider_name'],
            'import_service_provider_bu_number': import_service_provider_data['import_service_provider_bu_number'],
            'import_service_provider_bu_name': import_service_provider_data['import_service_provider_bu_name'],
            'import_service_provider_bu_contact_name': import_service_provider_data['import_service_provider_bu_contact_name'],
            'import_service_provider_bu_approver_name': import_service_provider_data['import_service_provider_bu_approver_name'],
            'import_service_provider_type': import_service_provider_data['import_service_provider_type'],
            'import_service_provider_address': import_service_provider_data['import_service_provider_address'],
            'import_service_provider_address_line_1': import_service_provider_data['import_service_provider_address_line_1'],
            'import_service_provider_address_line_2': import_service_provider_data['import_service_provider_address_line_2'],
            'import_service_provider_address_line_3': import_service_provider_data['import_service_provider_address_line_3'],
            'import_service_provider_city': import_service_provider_data['import_service_provider_city'],
            'import_service_provider_state': import_service_provider_data['import_service_provider_state'],
            'import_service_provider_zip': import_service_provider_data['import_service_provider_zip'],
            'import_service_provider_country': import_service_provider_data['import_service_provider_country'],
            'kyc_details': decrypted_kyc
        })
    else:
        return jsonify({'error': 'Import Service Provider not found'}), 404

# Route to create a folder for an import freight contract
@app.route('/create/import_freight_contract_document/folder', methods=['POST'])
@login_required  # Ensure MCXCustomer is authenticated
def create_import_freight_contract_document_folder():
    try:
        data = request.json
        # Validate and extract necessary data
        import_freight_contract_document_folder_name = data.get('import_freight_contract_document_folder_name')
        import_freight_contract_document_folder_number = data.get('import_freight_contract_document_folder_number')
        import_service_provider_name = data.get('import_service_provider_name')
        import_service_provider_account_number = data.get('import_service_provider_account_number')
        import_service_provider_id = data.get('import_service_provider_id')

        # Create instances of reference number generators for different entities
        import_freight_contract_document_folder_reference_generator = ReferenceNumberGenerator('IFCDF')

        # Generate a reference number for the document folder
        import_freight_contract_document_folder_reference = import_freight_contract_document_folder_reference_generator.generate_reference_number(
            'ImportFreightContractDocumentFolder', import_freight_contract_document_folder_number)

        # Create a new import_freight_contract_document_folder instance and add it to the database
        new_import_freight_contract_document_folder = ImportFreightContractDocumentFolder(
            import_freight_contract_document_folder_name=import_freight_contract_document_folder_name,
            import_freight_contract_document_folder_reference=import_freight_contract_document_folder_reference,
            import_freight_contract_document_folder_number=import_freight_contract_document_folder_number,
            import_service_provider_name=import_service_provider_name,
            import_service_provider_account_number=import_service_provider_account_number,
            import_service_provider_id=import_service_provider_id,
        )
        db.session.add(new_import_freight_contract_document_folder)
        db.session.commit()

        # Validate required fields
        if not all([import_service_provider_name, import_service_provider_account_number, import_freight_contract_document_folder_number]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details if needed
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(data.get('kyc_details'), encryption_key)

        # Create and store the import freight contract document folder
        account_number = create_import_freight_contract_document_folder_db(
            ifcdf_code, ifc_code, import_service_provider_name, import_service_provider_account_number, import_service_provider_bu_name,
            import_service_provider_bu_number, import_freight_contract_document_folder_number, encrypted_kyc)
        return jsonify({'import_freight_contract_document_folder_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_import_freight_contract_document_folder: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/createimportfreightcontract', methods=['POST'])
def create_import_freight_contract():
    try:
        data = request.json
        mcxcustomer_account_number = data.get('mcxcustomer_account_number')
        ifc_code = data.get('ifc_code')
        import_freight_contract_number = data.get('import_freight_contract_number')
        import_freight_contract_id = data.get('import_freight_contract_id')
        import_service_provider_name = data.get('import_service_provider_name')
        import_service_provider_account_number = data.get('import_service_provider_account_number')
        import_service_provider_id = data.get('import_service_provider_id')
        import_service_provider_bu_name = data.get('import_service_provider_bu_name')
        import_service_provider_bu_number = data.get('import_service_provider_bu_number')
        kyc_details = data.get('kyc_details')

        # Retrieve the reference or identifier of the associated Import Freight Contract Document Folder
        document_folder_reference = data.get('IFCDF')

        # Create a new import freight contract instance and associate it with the Document Folder
        new_import_freight_contract = ImportFreightContract(
            mcxcustomer_account_number=mcxcustomer_account_number,
            ifcdf_code=ifcdf_code, # Associate with Document Folder Reference
            ifc_code=ifc_code,
            import_service_provider_name=import_service_provider_name,
            import_service_provider_bu_name=import_service_provider_bu_name,
            import_service_provider_bu_number=import_service_provider_bu_number,
            import_service_provider_account_number=import_service_provider_account_number,
            import_freight_contract_number=import_freight_contract_number,
            encrypted_kyc=kyc_details,
        )

        db.session.add(new_import_freight_contract)
        db.session.commit()

        # Validate required fields
        if not all([mcxcustomer_account, ifcdf_code, ifc_code, import_service_provider_name, import_service_provider_bu_name, import_service_provider_bu_number, import_service_provider_account_number, import_freight_contract_number, kyc_details]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(kyc_details, encryption_key)

        # Create and store the import_freight_contract
        account_number = create_import_freight_contract_db(mcxcustomer_account_number, ifcdf_code, ifc_code, import_service_provider_name, import_service_provider_bu_name, import_service_provider_bu_number, import_service_provider_account_number, import_freight_contract_number, encrypted_kyc)
        return jsonify({'import_freight_contract_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_import_freight_contract: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Import Freight Contract Creation Route
def create_import_freight_contract_db(mcxcustomer_account, ifcdf_code, ifc_code, import_service_provider_name, import_service_provider_name_bu_name, import_service_provider_bu_number, import_service_provider_account_number, import_freight_contract_number, encrypted_kyc):
    # Implement the logic to generate the account number based on your requirements
    account_number = generate_import_freight_contract_reference_number()  # Implement this function
    # Assuming import freight contract is a dictionary to store import freight contract data
    import_freight_contract[account_number] = {
        'mcxcustomer_account_number': mcxcustomer_account_number,
        'ifcdf_code': ifcdf_code,
        'ifc_code': ifc_code,
        'import_service_provider_name': import_service_provider_name,
        'import_service_provider_bu_name': import_service_provider_bu_name,
        'import_service_provider_bu_number': import_service_provider_bu_number, 
        'import_service_provider_account_number': import_service_provider_account_number,
        'import_freight_contract_number': import_freight_contract_number
        'encrypted_kyc': encrypted_kyc,
        'import_freight_contract': {},
        'import_freight_contract_contract_document_folder': {}
    }
    return account_number

# Import Freight Contract Retrieval Route
@app.route('/ImportFreightContract/<import_freight_contract_account_number>', methods=['GET'])
def get_import_freight_contract(import_freight_contract_account_number):
    import_freight_contract_data = import_freight_contract.get(import_freight_contract_account_number)
    if import_freight_contract_data:
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        decrypted_kyc = decrypt_data(import_freight_contract_data['encrypted_kyc'], encryption_key)
        return jsonify({
            'mcxcustomer_account_number': mcxcustomer_data['mcxcustomer_account_number'],
            'ifcdf_code': import_freight_contract_data['ifcdf_code'],
            'ifc_code': import_freight_contract_data['ifc_code'],
            'import_service_provider_name': import_freight_contract_data['import_service_provider_name'],
            'import_service_provider_bu_name': import_freight_contract_data['import_service_provider_bu_name'],
            'import_service_provider_bu_number': import_freight_contract_data['import_service_provider_bu_number'],
            'import_freight_contract_number': import_freight_contract_data['import_freight_contract_number'],
            'encrypted_kyc': decrypted_kyc,
        })
    else:
        return jsonify({'error': 'Import Freight Contract not found'}), 404

# Example function to receive and store a document in the specified folder
def receive_and_store_document(ifcdf_code, ifc_code, import_service_provider_name, import_service_provider_account_number, import_service_provider_bu_name, import_service_provider_bu_number, document_type, document_data):
    try:
        # Determine the document class based on the document type
        if document_type == 'ImportRoutingOrder':
            document_class == ImportRoutingOrder
        elif document_type == 'ImportFreightInvoice':
            document_class == ImportFreightInvoice
        elif document_type == 'ImportAirwayBill':
            document_class == ImportAirwayBill
        elif document_type == 'ImportBillOfLading':
            document_class == ImportBillOfLading
        elif document_type == 'ImportBillOfEntry':
            document_class == ImportBillOfEntry    
        else:
            return {'error': 'Invalid document type'}, 400
        
        # Generate reference numbers
        document_reference = generate_document_reference(
            document_type, ifcdf_code, ifc_code, import_service_provider_name, import_service_provider_bu_name, import_service_provider_bu_number, import_service_provider_account_number, 'ImportFreightContract', document_data['document_number']
        )

        # Create an instance of the document class
        document = document_class()
         
        # Create an instance of the document folder with appropriate arguments
        document_folder = ImportFreightContractDocumentFolder(
            ifcdf_code, ifc_code, import_service_provider_name, import_service_provider_account_number, import_service_provider_bu_name, import_service_provider_bu_number
        )

        # Store the document in the document folder
        document_folder.store_document(document)
        
        # Save metadata in the database linking the document to the folder and contract
        store_document_metadata(
            document, document_folder, ifc_code
        )

        return {'message': f'{document_type} received and stored successfully.'}, 201
    except Exception as e:
        print(f"Exception in receive_and_store_document: {str(e)}")
        return {'error': 'Internal Server Error'}, 500

# Example usage to receive and store a Import Routing Order
ifcdf_code = generate_import_freight_contract_document_folder_reference()  # Replace with actual code to generate ifcdf_code using UUID
ifc_code = generate_import_freight_contract_reference()  # Replace with actual code to generate ifc_code using UUID
# Replace with the actual import service provider name entered by the user
import_service_provider_name = 'ImportServiceProviderName'  # User should provide the actual import service provider name
# Replace with the actual import service provider account number generated using UUID or entered by the user
import_service_provider_account_number = '12345'  # User should provide the actual import service provider account number
# Replace with the actual import service provider bu name entered by the user
import_service_provider_bu_name = 'ImportServiceProviderBuName'  # User should provide the actual import service provider bu name
# Replace with the actual import service provider bu number generated using UUID or entered by the user
import_service_provider_bu_number = '001'  # User should provide the actual import service provider bu number
document_type = 'ImportRoutingOrder'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'IRO123'  # User should provide the actual document number
# Use the generate_import_routing_order_reference function to generate the IRO reference number
iro_reference = generate_import_routing_order_reference(
    ifcdf_code, ifc_code, import_service_provider_name, import_service_provider_bu_name, import_service_provider_bu_number, import_service_provider_account_number, document_number
)
document_data = {
    'document_number': iro_reference,  # Use the generated IRO reference as the document number
    # Add other data for the Import Routing Order here
}

response, status_code = receive_and_store_document(
    ifcdf_code, ifc_code, iro_reference, import_service_provider_name,
    import_service_provider_account_number, import_service_provider_bu_name,
    import_service_provider_bu_number, document_type, document_data
)

# Example usage to receive and store a Import Freight Invoice
ifcdf_code = generate_import_freight_contract_document_folder_reference()  # Replace with actual code to generate ifcdf_code using UUID
ifc_code = generate_import_freight_contract_reference()  # Replace with actual code to generate ifc_code using UUID
# Replace with the actual import service provider name entered by the user
import_service_provider_name = 'ImportServiceProviderName'  # User should provide the actual import service provider name
# Replace with the actual import service provider account number generated using UUID or entered by the user
import_service_provider_account_number = '12345'  # User should provide the actual import service provider account number
# Replace with the actual import service provider bu name entered by the user
import_service_provider_bu_name = 'ImportServiceProviderBuName'  # User should provide the actual import service provider bu name
# Replace with the actual import service provider bu number generated using UUID or entered by the user
import_service_provider_bu_number = '001'  # User should provide the actual import service provider bu number
document_type = 'ImportFreightInvoice'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'IFINV123'  # User should provide the actual document number
# Use the generate_import_freight_invoice_reference function to generate the IFINV reference number
ifinv_reference = generate_import_freight_invoice_reference(
    ifcdf_code, ifc_code, import_service_provider_name, import_service_provider_bu_name, import_service_provider_bu_number, import_service_provider_account_number, document_number
)
document_data = {
    'document_number': ifinv_reference,  # Use the generated IFINV reference as the document number
    # Add other data for the Import Freight Invoice here
}

response, status_code = receive_and_store_document(
    ifcdf_code, ifc_code, ifinv_reference, import_service_provider_name,
    import_service_provider_account_number, import_service_provider_bu_name,
    import_service_provider_bu_number, document_type, document_data
)

# Example usage to receive and store a Import Airway Bill
ifcdf_code = generate_import_freight_contract_document_folder_reference()  # Replace with actual code to generate ifcdf_code using UUID
ifc_code = generate_import_freight_contract_reference()  # Replace with actual code to generate ifc_code using UUID
# Replace with the actual import service provider name entered by the user
import_service_provider_name = 'ImportServiceProviderName'  # User should provide the actual import service provider name
# Replace with the actual import service provider account number generated using UUID or entered by the user
import_service_provider_account_number = '12345'  # User should provide the actual import service provider account number
# Replace with the actual import service provider bu name entered by the user
import_service_provider_bu_name = 'ImportServiceProviderBuName'  # User should provide the actual import service provider bu name
# Replace with the actual import service provider bu number generated using UUID or entered by the user
import_service_provider_bu_number = '001'  # User should provide the actual import service provider bu number
document_type = 'ImportAirwaybill'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'IAWB123'  # User should provide the actual document number
# Use the generate_import_airway_bill_reference function to generate the IAWB reference number
iawb_reference = generate_import_airway_bill_reference(
    ifc_code, ifcdf_code, import_service_provider_name, import_service_provider_bu_name, import_service_provider_bu_number, import_service_provider_account_number, document_number
)
document_data = {
    'document_number': iawb_reference,  # Use the generated IAWB reference as the document number
    # Add other data for the Import Airway Bill
}

response, status_code = receive_and_store_document(
    ifcdf_code, ifc_code, iawb_reference, import_service_provider_name,
    import_service_provider_account_number, import_service_provider_bu_name,
    import_service_provider_bu_number, document_type, document_data
)

# Example usage to receive and store a Import Bill Of Lading
ifcdf_code = generate_import_freight_contract_document_folder_reference()  # Replace with actual code to generate ifcdf_code using UUID
ifc_code = generate_import_freight_contract_reference()  # Replace with actual code to generate ifc_code using UUID
# Replace with the actual import service provider name entered by the user
import_service_provider_name = 'ImportServiceProviderName'  # User should provide the actual import service provider name
# Replace with the actual import service provider account number generated using UUID or entered by the user
import_service_provider_account_number = '12345'  # User should provide the actual import service provider account number
# Replace with the actual import service provider bu name entered by the user
import_service_provider_bu_name = 'ImportServiceProviderBuName'  # User should provide the actual import service provider bu name
# Replace with the actual import service provider bu number generated using UUID or entered by the user
import_service_provider_bu_number = '001'  # User should provide the actual import service provider bu number
document_type = 'ImportbillOfLading'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'IBOL123'  # User should provide the actual document number
# Use the generate_import_bill_of_lading_reference function to generate the IBOL reference number
iawb_reference = generate_import_bill_of_lading_reference(
    ifc_code, ifcdf_code, import_service_provider_name, import_service_provider_bu_name, import_service_provider_bu_number, import_service_provider_account_number, document_number
)
document_data = {
    'document_number': ibol_reference,  # Use the generated IBOL reference as the document number
    # Add other data for the Import Bill Of Lading
}

response, status_code = receive_and_store_document(
    ifcdf_code, ifc_code, ibol_reference, import_service_provider_name,
    import_service_provider_account_number, import_service_provider_bu_name,
    import_service_provider_bu_number, document_type, document_data
)

# Example usage to receive and store a Import Bill Of Entry
ifcdf_code = generate_import_freight_contract_document_folder_reference()  # Replace with actual code to generate ifcdf_code using UUID
ifc_code = generate_import_freight_contract_reference()  # Replace with actual code to generate ifc_code using UUID
# Replace with the actual import service provider name entered by the user
import_service_provider_name = 'ImportServiceProviderName'  # User should provide the actual import service provider name
# Replace with the actual import service provider account number generated using UUID or entered by the user
import_service_provider_account_number = '12345'  # User should provide the actual import service provider account number
# Replace with the actual import service provider bu name entered by the user
import_service_provider_bu_name = 'ImportServiceProviderBuName'  # User should provide the actual import service provider bu name
# Replace with the actual import service provider bu number generated using UUID or entered by the user
import_service_provider_bu_number = '001'  # User should provide the actual import service provider bu number
document_type = 'ImportbillOfEntry'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'IBOENT123'  # User should provide the actual document number
# Use the generate_import_bill_of_entry_reference function to generate the IBOENT reference number
iboent_reference = generate_import_bill_of_entry_reference(
    ifc_code, ifcdf_code, import_service_provider_name, import_service_provider_bu_name, import_service_provider_bu_number, import_service_provider_account_number, document_number
)
document_data = {
    'document_number': iboent_reference,  # Use the generated IBOENT reference as the document number
    # Add other data for the Import Bill Of Entry
}

response, status_code = receive_and_store_document(
    ifcdf_code, ifc_code, iboent_reference, import_service_provider_name,
    import_service_provider_account_number, import_service_provider_bu_name,
    import_service_provider_bu_number, document_type, document_data
)


if __name__ == '__main__':
    app.run(debug=True)


# Function to encrypt data
def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())

# Function to decrypt data
def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()

# Function to check if a user has a specific role
def has_role(user, role):
    # Logic to check if the user has the specified role
    return role in user.roles

# Route for checking user roles
@app.route('/checkrole/<role>', methods=['GET'])
@login_required
def check_role(role):
    if has_role(current_user, role):
        return jsonify({'message': f'User has the {role} role.'})
    else:
        return jsonify({'message': f'User does not have the {role} role.'}), 403  

@app.route('/createexportserviceprovider', methods=['POST'])
def create_export_service_provider_db_route():
    try:
        # Extract data from the request
        data = request.json
        mcxcustomer_account = data.get('mcxcustomer_account')
        export_service_provider_name = data.get('import_service_provider_name')
        export_service_provider_bu_number = data.get('export_service_provider_business_unit_number')
        export_service_provider_bu_name = data.get('export_service_provider_unit_name')
        export_service_provider_bu_contact_name = data.get('export_service_provider_business_unit_contact_name')
        export_service_provider_bu_approver_name = data.get('export_service_provider_business_unit_approver_name')
        export_service_provider_type = data.get('export_service_provider_type')
        export_service_provider_address = data.get('export_service_provider_address')
        export_service_provider_address_line_1 = data.get('export_service_provider_address_line_1')
        export_service_provider_address_line_2 = data.get('export_service_provider_address_line_2')
        export_service_provider_address_line_3 = data.get('export_service_provider_address_line_3')
        export_service_provider_city = data.get('export_service_provider_city')
        export_service_provider_state = data.get('export_service_provider_state')
        export_service_provider_zip = data.get('export_service_provider_zip')
        export_service_provider_country = data.get('export_service_provider_country')
        kyc_details = data.get('kyc_details')
        
# Create a new Export Service Provider using the create_export_service_provider function from utils.py
        export_service_provider = create_export_service_provider(export_service_provider_name, mcxcustomer_account)

        # Generate a reference number for the Export Service Provider using the generate_export_service_provider_reference function from utils.py
        export_service_provider_reference = generate_export_service_provider_reference(
            'EXPSVC', export_service_provider_name, export_service_provider_bu_name, export_service_provider_bu_number, export_service_provider_account_number, 'ExpSvc', 'REF')

        # Placeholder dictionary to simulate a database
        export_service_provider_db = {}

# Add the Export Service Provider to the database
        export_service_provider_db[export_service_provider_reference] = {
            'mcxcustomer_account_number': mcxcustomer_account_number,
            'export_service_provider_name': export_service_provider_name,
            'export_service_provider_bu_number': export_service_provider_bu_number,
            'export_service_provider_bu_name': export_service_provider_bu_name,
            'export_service_provider_bu_contact_name': export_service_provider_bu_contact_name,
            'export_service_provider_bu_approver_name': export_service_provider_bu_approver_name,
            'export_service_provider_type': export_service_provider_type,
            'export_service_provider_address': export_service_provider_address,
            'export_service_provider_address_line_1': export_service_provider_address_line_1,
            'export_service_provider_address_line_2': export_service_provider_address_line_2,
            'export_service_provider_address_line_3': export_service_provider_address_line_3,
            'export_service_provider_city': export_service_provider_city,
            'export_service_provider_state': export_service_provider_state,
            'export_service_provider_zip': export_service_provider_zip,
            'export_service_provider_country': export_service_provider_country,
            'kyc_details': kyc_details,
        }
# Create a new export Service Provider instance and add it to the database (if necessary)
        new_export_service_provider = ExportServiceProvider(**data)
        db.session.add(new_export_service_provider)
        db.session.commit()

        # Validate required fields
        if not all([mcxcustomer_account, export_service_provider_name, kyc_details]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(kyc_details, encryption_key)

        # Create and store the export service provider (if necessary)
        account_number = create_export_service_provider_db(mcxcustomer_account, export_service_provider_name, encrypted_kyc)
        return jsonify({'export_service_provider_account_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_export_service_provider_db_route: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Export Service Provider Creation Route
def create_export_service_provider_db(mcxcustomer_account, export_service_provider_name, encrypted_kyc):
    # Generate a reference number for the export service provider entity
    export_service_provider_reference = mcx_customer.generate_reference_number("ImpSvc")

    # Create a Export Service Provider object (if necessary)
    export_service_provider = export_service_provider(export_service_provider_reference, mcx_customer)
    # Store export service provider data (if necessary)
    export_service_provider.name = export_service_provider_name
    export_service_provider.encrypted_kyc = encrypted_kyc
    export_service_provider = {
        'kyc', 'export_freight_contract', 'export_freight_contract_document_folder'
    }

    # Return the account number (if necessary)
    return export_service_provider.account_number

# Export Service Provider Retrieval Route
@app.route('/export_service_provider/<export_service_provider_account_number>', methods=['GET'])
def get_export_service_provider(export_service_provider_account_number):  
    export_service_provider_data = export_service_provider_db.get(export_service_provider_account_number)
    if export_service_provider_data:
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        decrypted_kyc = decrypt_data(export_service_provider_data['encrypted_kyc'], encryption_key)
        return jsonify({
            'export_service_provider_name': export_service_provider_data['export_service_provider_name'],
            'export_service_provider_bu_number': export_service_provider_data['export_service_provider_bu_number'],
            'export_service_provider_bu_name': export_service_provider_data['export_service_provider_bu_name'],
            'export_service_provider_bu_contact_name': export_service_provider_data['export_service_provider_bu_contact_name'],
            'export_service_provider_bu_approver_name': export_service_provider_data['export_service_provider_bu_approver_name'],
            'export_service_provider_type': export_service_provider_data['export_service_provider_type'],
            'export_service_provider_address': export_service_provider_data['export_service_provider_address'],
            'export_service_provider_address_line_1': export_service_provider_data['export_service_provider_address_line_1'],
            'export_service_provider_address_line_2': export_service_provider_data['export_service_provider_address_line_2'],
            'export_service_provider_address_line_3': export_service_provider_data['export_service_provider_address_line_3'],
            'export_service_provider_city': export_service_provider_data['export_service_provider_city'],
            'export_service_provider_state': export_service_provider_data['export_service_provider_state'],
            'export_service_provider_zip': export_service_provider_data['export_service_provider_zip'],
            'export_service_provider_country': export_service_provider_data['export_service_provider_country'],
            'kyc_details': decrypted_kyc
        })
    else:
        return jsonify({'error': 'Export Service Provider not found'}), 404

# Route to create a folder for an export freight contract
@app.route('/create/export_freight_contract_document/folder', methods=['POST'])
@login_required  # Ensure MCXCustomer is authenticated
def create_export_freight_contract_document_folder():
    try:
        data = request.json
        # Validate and extract necessary data
        export_freight_contract_document_folder_name = data.get('export_freight_contract_document_folder_name')
        export_freight_contract_document_folder_number = data.get('export_freight_contract_document_folder_number')
        export_service_provider_name = data.get('export_service_provider_name')
        export_service_provider_account_number = data.get('export_service_provider_account_number')
        export_service_provider_id = data.get('export_service_provider_id')

        # Create instances of reference number generators for different entities
        export_freight_contract_document_folder_reference_generator = ReferenceNumberGenerator('EFCDF')

        # Generate a reference number for the document folder
        export_freight_contract_document_folder_reference = export_freight_contract_document_folder_reference_generator.generate_reference_number(
            'ExportFreightContractDocumentFolder', export_freight_contract_document_folder_number)

        # Create a new export_freight_contract_document_folder instance and add it to the database
        new_export_freight_contract_document_folder = ExportFreightContractDocumentFolder(
            export_freight_contract_document_folder_name=export_freight_contract_document_folder_name,
            export_freight_contract_document_folder_reference=export_freight_contract_document_folder_reference,
            export_freight_contract_document_folder_number=export_freight_contract_document_folder_number,
            export_service_provider_name=export_service_provider_name,
            export_service_provider_account_number=export_service_provider_account_number,
            export_service_provider_id=export_service_provider_id,
        )
        db.session.add(new_export_freight_contract_document_folder)
        db.session.commit()

        # Validate required fields
        if not all([export_service_provider_name, export_service_provider_account_number, export_freight_contract_document_folder_number]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details if needed
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(data.get('kyc_details'), encryption_key)

        # Create and store the export freight contract document folder
        account_number = create_export_freight_contract_document_folder_db(
            efcdf_code, efc_code, export_service_provider_name, export_service_provider_account_number, export_service_provider_bu_name,
            export_service_provider_bu_number, export_freight_contract_document_folder_number, encrypted_kyc)
        return jsonify({'export_freight_contract_document_folder_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_export_freight_contract_document_folder: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/createexportfreightcontract', methods=['POST'])
def create_export_freight_contract():
    try:
        data = request.json
        mcxcustomer_account_number = data.get('mcxcustomer_account_number')
        efc_code = data.get('efc_code')
        export_freight_contract_number = data.get('export_freight_contract_number')
        export_freight_contract_id = data.get('export_freight_contract_id')
        export_service_provider_name = data.get('export_service_provider_name')
        export_service_provider_account_number = data.get('export_service_provider_account_number')
        export_service_provider_id = data.get('export_service_provider_id')
        export_service_provider_bu_name = data.get('export_service_provider_bu_name')
        export_service_provider_bu_number = data.get('export_service_provider_bu_number')
        kyc_details = data.get('kyc_details')

        # Retrieve the reference or identifier of the associated Export Freight Contract Document Folder
        document_folder_reference = data.get('EFCDF')

        # Create a new export freight contract instance and associate it with the Document Folder
        new_export_freight_contract = ExportFreightContract(
            mcxcustomer_account_number=mcxcustomer_account_number,
            efcdf_code=efcdf_code, # Associate with Document Folder Reference
            efc_code=efc_code,
            export_service_provider_name=export_service_provider_name,
            export_service_provider_bu_name=export_service_provider_bu_name,
            export_service_provider_bu_number=export_service_provider_bu_number,
            export_service_provider_account_number=export_service_provider_account_number,
            export_freight_contract_number=export_freight_contract_number,
            encrypted_kyc=kyc_details,
        )

        db.session.add(new_export_freight_contract)
        db.session.commit()

        # Validate required fields
        if not all([mcxcustomer_account, efcdf_code, efc_code, export_service_provider_name, export_service_provider_bu_name, export_service_provider_bu_number, export_service_provider_account_number, export_freight_contract_number, kyc_details]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Encrypt KYC details
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        encrypted_kyc = encrypt_data(kyc_details, encryption_key)

        # Create and store the export_freight_contract
        account_number = create_export_freight_contract_db(mcxcustomer_account_number, efcdf_code, efc_code, export_service_provider_name, export_service_provider_bu_name, export_service_provider_bu_number, export_service_provider_account_number, export_freight_contract_number, encrypted_kyc)
        return jsonify({'export_freight_contract_number': account_number}), 201

    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Exception in create_export_freight_contract: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Export Freight Contract Creation Route
def create_export_freight_contract_db(mcxcustomer_account, efcdf_code, efc_code, export_service_provider_name, export_service_provider_name_bu_name, export_service_provider_bu_number, export_service_provider_account_number, export_freight_contract_number, encrypted_kyc):
    # Implement the logic to generate the account number based on your requirements
    account_number = generate_export_freight_contract_reference_number()  # Implement this function
    # Assuming export freight contract is a dictionary to store import freight contract data
    export_freight_contract[account_number] = {
        'mcxcustomer_account_number': mcxcustomer_account_number,
        'efcdf_code': efcdf_code,
        'efc_code': efc_code,
        'export_service_provider_name': export_service_provider_name,
        'export_service_provider_bu_name': export_service_provider_bu_name,
        'export_service_provider_bu_number': export_service_provider_bu_number, 
        'export_service_provider_account_number': export_service_provider_account_number,
        'export_freight_contract_number': export_freight_contract_number
        'encrypted_kyc': encrypted_kyc,
        'export_freight_contract': {},
        'export_freight_contract_contract_document_folder': {}
    }
    return account_number

# Export Freight Contract Retrieval Route
@app.route('/ExportFreightContract/<export_freight_contract_account_number>', methods=['GET'])
def get_export_freight_contract(export_freight_contract_account_number):
    export_freight_contract_data = export_freight_contract.get(export_freight_contract_account_number)
    if export_freight_contract_data:
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        decrypted_kyc = decrypt_data(export_freight_contract_data['encrypted_kyc'], encryption_key)
        return jsonify({
            'mcxcustomer_account_number': mcxcustomer_data['mcxcustomer_account_number'],
            'efcdf_code': export_freight_contract_data['efcdf_code'],
            'efc_code': export_freight_contract_data['efc_code'],
            'export_service_provider_name': export_freight_contract_data['export_service_provider_name'],
            'export_service_provider_bu_name': export_freight_contract_data['export_service_provider_bu_name'],
            'export_service_provider_bu_number': export_freight_contract_data['export_service_provider_bu_number'],
            'export_freight_contract_number': export_freight_contract_data['export_freight_contract_number'],
            'encrypted_kyc': decrypted_kyc,
        })
    else:
        return jsonify({'error': 'Export Freight Contract not found'}), 404

# Example function to receive and store a document in the specified folder
def receive_and_store_document(efcdf_code, efc_code, export_service_provider_name, export_service_provider_account_number, export_service_provider_bu_name, export_service_provider_bu_number, document_type, document_data):
    try:
        # Determine the document class based on the document type
        if document_type == 'ExportRoutingOrder':
            document_class == ExportRoutingOrder
        elif document_type == 'ExportFreightInvoice':
            document_class == ExportFreightInvoice
        elif document_type == 'ExportAirwayBill':
            document_class == ExportAirwayBill
        elif document_type == 'ExportBillOfLading':
            document_class == ExportBillOfLading
        elif document_type == 'ExportBillOfExit':
            document_class == ExportBillOfExit    
        else:
            return {'error': 'Invalid document type'}, 400
        
        # Generate reference numbers
        document_reference = generate_document_reference(
            document_type, efcdf_code, efc_code, export_service_provider_name, export_service_provider_bu_name, export_service_provider_bu_number, export_service_provider_account_number, 'ExportFreightContract', document_data['document_number']
        )

        # Create an instance of the document class
        document = document_class()
         
        # Create an instance of the document folder with appropriate arguments
        document_folder = ExportFreightContractDocumentFolder(
            efcdf_code, efc_code, export_service_provider_name, export_service_provider_account_number, export_service_provider_bu_name, export_service_provider_bu_number
        )

        # Store the document in the document folder
        document_folder.store_document(document)
        
        # Save metadata in the database linking the document to the folder and contract
        store_document_metadata(
            document, document_folder, efc_code
        )

        return {'message': f'{document_type} received and stored successfully.'}, 201
    except Exception as e:
        print(f"Exception in receive_and_store_document: {str(e)}")
        return {'error': 'Internal Server Error'}, 500

# Example usage to receive and store a Export Routing Order
efcdf_code = generate_export_freight_contract_document_folder_reference()  # Replace with actual code to generate efcdf_code using UUID
efc_code = generate_export_freight_contract_reference()  # Replace with actual code to generate efc_code using UUID
# Replace with the actual export service provider name entered by the user
export_service_provider_name = 'ExportServiceProviderName'  # User should provide the actual export service provider name
# Replace with the actual export service provider account number generated using UUID or entered by the user
export_service_provider_account_number = '12345'  # User should provide the actual export service provider account number
# Replace with the actual export service provider bu name entered by the user
export_service_provider_bu_name = 'ExportServiceProviderBuName'  # User should provide the actual export service provider bu name
# Replace with the actual export service provider bu number generated using UUID or entered by the user
export_service_provider_bu_number = '001'  # User should provide the actual export service provider bu number
document_type = 'ExportRoutingOrder'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'ERO123'  # User should provide the actual document number
# Use the generate_export_routing_order_reference function to generate the ERO reference number
ero_reference = generate_export_routing_order_reference(
    efcdf_code, efc_code, export_service_provider_name, export_service_provider_bu_name, export_service_provider_bu_number, export_service_provider_account_number, document_number
)
document_data = {
    'document_number': ero_reference,  # Use the generated ERO reference as the document number
    # Add other data for the Export Routing Order here
}

response, status_code = receive_and_store_document(
    efcdf_code, efc_code, ero_reference, export_service_provider_name,
    export_service_provider_account_number, export_service_provider_bu_name,
    export_service_provider_bu_number, document_type, document_data
)

# Example usage to receive and store a Export Freight Invoice
efcdf_code = generate_export_freight_contract_document_folder_reference()  # Replace with actual code to generate efcdf_code using UUID
efc_code = generate_export_freight_contract_reference()  # Replace with actual code to generate efc_code using UUID
# Replace with the actual export service provider name entered by the user
export_service_provider_name = 'ExportServiceProviderName'  # User should provide the actual export service provider name
# Replace with the actual export service provider account number generated using UUID or entered by the user
export_service_provider_account_number = '12345'  # User should provide the actual export service provider account number
# Replace with the actual export service provider bu name entered by the user
export_service_provider_bu_name = 'ExportServiceProviderBuName'  # User should provide the actual export service provider bu name
# Replace with the actual export service provider bu number generated using UUID or entered by the user
export_service_provider_bu_number = '001'  # User should provide the actual export service provider bu number
document_type = 'ExportFreightInvoice'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'EFINV123'  # User should provide the actual document number
# Use the generate_export_freight_invoice_reference function to generate the EFINV reference number
efinv_reference = generate_export_freight_invoice_reference(
    efcdf_code, efc_code, export_service_provider_name, export_service_provider_bu_name, export_service_provider_bu_number, export_service_provider_account_number, document_number
)
document_data = {
    'document_number': efinv_reference,  # Use the generated EFINV reference as the document number
    # Add other data for the Export Freight Invoice here
}

response, status_code = receive_and_store_document(
    efcdf_code, efc_code, efinv_reference, export_service_provider_name,
    export_service_provider_account_number, export_service_provider_bu_name,
    export_service_provider_bu_number, document_type, document_data
)

# Example usage to receive and store a Export Airway Bill
efcdf_code = generate_export_freight_contract_document_folder_reference()  # Replace with actual code to generate efcdf_code using UUID
efc_code = generate_export_freight_contract_reference()  # Replace with actual code to generate efc_code using UUID
# Replace with the actual export service provider name entered by the user
export_service_provider_name = 'ExportServiceProviderName'  # User should provide the actual export service provider name
# Replace with the actual export service provider account number generated using UUID or entered by the user
export_service_provider_account_number = '12345'  # User should provide the actual export service provider account number
# Replace with the actual export service provider bu name entered by the user
export_service_provider_bu_name = 'ExportServiceProviderBuName'  # User should provide the actual export service provider bu name
# Replace with the actual export service provider bu number generated using UUID or entered by the user
export_service_provider_bu_number = '001'  # User should provide the actual export service provider bu number
document_type = 'ExportAirwaybill'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'EAWB123'  # User should provide the actual document number
# Use the generate_export_airway_bill_reference function to generate the EAWB reference number
eawb_reference = generate_export_airway_bill_reference(
    efc_code, efcdf_code, export_service_provider_name, export_service_provider_bu_name, export_service_provider_bu_number, export_service_provider_account_number, document_number
)
document_data = {
    'document_number': eawb_reference,  # Use the generated EAWB reference as the document number
    # Add other data for the Export Airway Bill
}

response, status_code = receive_and_store_document(
    efcdf_code, efc_code, eawb_reference, export_service_provider_name,
    export_service_provider_account_number, export_service_provider_bu_name,
    export_service_provider_bu_number, document_type, document_data
)

# Example usage to receive and store a Export Bill Of Lading
efcdf_code = generate_export_freight_contract_document_folder_reference()  # Replace with actual code to generate efcdf_code using UUID
efc_code = generate_export_freight_contract_reference()  # Replace with actual code to generate efc_code using UUID
# Replace with the actual export service provider name entered by the user
export_service_provider_name = 'ExportServiceProviderName'  # User should provide the actual export service provider name
# Replace with the actual export service provider account number generated using UUID or entered by the user
export_service_provider_account_number = '12345'  # User should provide the actual export service provider account number
# Replace with the actual export service provider bu name entered by the user
export_service_provider_bu_name = 'ExportServiceProviderBuName'  # User should provide the actual export service provider bu name
# Replace with the actual export service provider bu number generated using UUID or entered by the user
export_service_provider_bu_number = '001'  # User should provide the actual export service provider bu number
document_type = 'ExportbillOfLading'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'EBOL123'  # User should provide the actual document number
# Use the generate_export_bill_of_lading_reference function to generate the EBOL reference number
iawb_reference = generate_export_bill_of_lading_reference(
    efc_code, efcdf_code, export_service_provider_name, export_service_provider_bu_name, export_service_provider_bu_number, export_service_provider_account_number, document_number
)
document_data = {
    'document_number': ebol_reference,  # Use the generated EBOL reference as the document number
    # Add other data for the Export Bill Of Lading
}

response, status_code = receive_and_store_document(
    efcdf_code, efc_code, ebol_reference, export_service_provider_name,
    export_service_provider_account_number, export_service_provider_bu_name,
    export_service_provider_bu_number, document_type, document_data
)

# Example usage to receive and store a Export Bill Of Exit
efcdf_code = generate_export_freight_contract_document_folder_reference()  # Replace with actual code to generate efcdf_code using UUID
efc_code = generate_export_freight_contract_reference()  # Replace with actual code to generate efc_code using UUID
# Replace with the actual export service provider name entered by the user
export_service_provider_name = 'ExportServiceProviderName'  # User should provide the actual export service provider name
# Replace with the actual export service provider account number generated using UUID or entered by the user
export_service_provider_account_number = '12345'  # User should provide the actual export service provider account number
# Replace with the actual export service provider bu name entered by the user
export_service_provider_bu_name = 'ExportServiceProviderBuName'  # User should provide the actual export service provider bu name
# Replace with the actual export service provider bu number generated using UUID or entered by the user
export_service_provider_bu_number = '001'  # User should provide the actual export service provider bu number
document_type = 'ExportbillOfExit'
# Replace with the actual document number generated using UUID or entered by the user
document_number = 'IBOEXT123'  # User should provide the actual document number
# Use the generate_export_bill_of_exit_reference function to generate the IBOEXT reference number
eboext_reference = generate_import_bill_of_entry_reference(
    efc_code, efcdf_code, export_service_provider_name, export_service_provider_bu_name, export_service_provider_bu_number, export_service_provider_account_number, document_number
)
document_data = {
    'document_number': iboext_reference,  # Use the generated EBOEXT reference as the document number
    # Add other data for the Export Bill Of Exit
}

response, status_code = receive_and_store_document(
    efcdf_code, efc_code, iboext_reference, export_service_provider_name,
    export_service_provider_account_number, export_service_provider_bu_name,
    export_service_provider_bu_number, document_type, document_data
)

if __name__ == '__main__':
    app.run(debug=True)
















































































# Route for creating a vendor procurement contract
@app.route('/createvendorprocurementcontract', methods=['POST'])
def create_vendor_procurement_contract():
    data = request.json
    vendor_name = data['vendor_name']
    business_unit_name = data['business_unit_name']
    business_unit_number = data['business_unit_number']                          
    document_type = data['document_type']  # 'vendor procurement contract'
    vendor_procurement_contract_number = data['vendor_procurement_contract_number']
    current_date = data['current_date']
    unique_suffix = data['unique_suffix']
    reference_number = create_contract('VPC', vendor_name, business_unit_name, business_unit_number, vendor_account_number, 'VendorProcurementContract', vendor_procurement_contract_number)
    return jsonify({'reference_number': reference_number})

# Route for creating a buyer sales contract
@app.route('/createbuyersalescontract', methods=['POST'])
def create_buyer_sales_contract():
    data = request.json
    buyer_name = data['buyer_name']
    business_unit_name = data['business_unit_name']
    business_unit_number = data['business_unit_number']                          
    document_type = data['document_type']  # 'buyer sales contract'
    buyer_sales_contract_number = data['buyer_sales_contract_number']
    current_date = data['current_date']
    unique_suffix = data['unique_suffix']
    reference_number = create_contract('BSC', buyer_name, business_unit_name, business_unit_number, buyer_account_number, 'BuyerSalesContract', buyer_sales_contract_number)
    return jsonify({'reference_number': reference_number})

# Route for creating a import freight contract
@app.route('/createimportfreightcontract', methods=['POST'])
def create_import_freight_contract():
    data = request.json
    import_service_provider_name = data['import_service_provider_name']
    business_unit_name = data['business_unit_name']
    business_unit_number = data['business_unit_number']                          
    document_type = data['document_type']  # 'import freight contract'
    import_freight_contract_number = data['import_freight_contract_number']
    current_date = data['current_date']
    unique_suffix = data['unique_suffix']
    reference_number = create_contract('IFC', import_service_provider_name, 'N/A', 'N/A', import_service_provider_account_number, 'ImportFreightContract', import_freight_contract_number)
    return jsonify({'reference_number': reference_number})

# Route for creating a export freight contract
@app.route('/createexportfreightcontract', methods=['POST'])
def create_export_freight_contract():
    data = request.json
    export_service_provider_name = data['export_service_provider_name']
    business_unit_name = data['business_unit_name']
    business_unit_number = data['business_unit_number']                          
    document_type = data['document_type']  # 'export freight contract'
    export_freight_contract_number = data['export_freight_contract_number']
    current_date = data['current_date']
    unique_suffix = data['unique_suffix']
    reference_number = create_contract('EFC', export_service_provider_name, 'N/A', 'N/A', export_service_provider_account_number, 'ExportFreightContract', export_freight_contract_number)
    return jsonify({'reference_number': reference_number})

# Route for creating a import freight contract document folder
@app.route('/createimportfreightcontractdocumentfolder', methods=['POST'])
def create_import_freight_contract_document_folder():
    data = request.json
    import_service_provider_name = data['import_service_provider_name']
    business_unit_name = data['business_unit_name']
    business_unit_number = data['business_unit_number']                          
    document_type = data['document_type']  # 'import freight contract document folder'
    import_freight_contract_number = data['import_freight_contract_document_folder_number']
    current_date = data['current_date']
    unique_suffix = data['unique_suffix']
    reference_number = create_contract('IFCDF', import_service_provider_name, business_unit_name, business_unit_number, import_service_provider_account_number, 'ImportFreightContractDocFolder', import_freight_contract_document_folder_number)
    return jsonify({'reference_number': reference_number})

# Route for creating a export freight contract document folder
@app.route('/createexportfreightcontractdocumentfolder', methods=['POST'])
def create_export_freight_contract_document_folder():
    data = request.json
    export_service_provider_name = data['export_service_provider_name']
    business_unit_name = data['business_unit_name']
    business_unit_number = data['business_unit_number']                          
    document_type = data['document_type']  # 'export freight contract document folder'
    export_freight_contract_number = data['export_freight_contract_document_folder_number']
    current_date = data['current_date']
    unique_suffix = data['unique_suffix']
    reference_number = create_contract('EFCDF', export_service_provider_name, business_unit_name, business_unit_number, export_service_provider_account_number, 'ExportFreightContractDocFolder', export_freight_contract_document_folder_number)
    return jsonify({'reference_number': reference_number})
    }
    return reference_number

@app.route('/checkrole/<role>', methods=['GET'])
@login_required
def check_role(role):
    # Validate the role against a list of permissible roles
    if role not in USER_ROLES:
        return jsonify({'message': 'Invalid role'}), 400

    # Assuming 'has_role' function checks the role properly
    if has_role(current_user, role):
        return jsonify({'message': f'User has the {role} role.'})
    else:
        return jsonify({'message': f'User does not have the {role} role.'}), 403

if __name__ == '__main__':
    app.run(debug=True)


def generate_upload_path(contract_type, document_type, identifiers):
    base_path = '/path/to/uploads'

    if contract_type == 'vendor_procurement_contract':
        vendor_name, business_unit_name, business_unit_number, vendor_account_number, vendor_procurement_contract_number = identifiers
        return os.path.join(base_path, 'VPC', *identifiers)
    elif contract_type == 'buyer_sales_contract':
        buyer_name, business_unit_name, business_unit_number, buyer_account_number, buyer_sales_contract_number = identifiers
        return os.path.join(base_path, 'BSC', *identifiers)
    elif contract_type == 'import_freight_contract':
        import_service_provider_name, import_service_provider_account_number, import_freight_contract_number = identifiers
        return os.path.join(base_path, 'IFC', *identifiers)
    elif contract_type == 'export_freight_contract':
        export_service_provider_name, export_service_provider_account_number, export_freight_contract_number = identifiers
        return os.path.join(base_path, 'EFC', *identifiers)
    
    # Vendor_procurement_contract_document-specific paths
    elif document_type == 'vendor_purchase_order':
        vendor_name, business_unit_name, business_unit_number, vendor_account_number, 'VendorPurchaseOrder', vendor_purchase_order_number = identifiers
        return os.path.join(base_path, 'VPO', *identifiers)
    elif document_type == 'vendor_invoice':
        vendor_name, business_unit_name, business_unit_number, vendor_account_number, 'VendorInvoice', vendor_invoice_number = identifiers
        return os.path.join(base_path, 'VINV', *identifiers)
    elif document_type == 'vendor_packing_list':
        vendor_name, 'N/A', 'N/A', vendor_account_number, 'VendorPackingList', vendor_packing_list_number = identifiers
        return os.path.join(base_path, 'VPL', *identifiers)
    elif document_type == 'vendor_goods_receipt_note':
        vendor_name, business_unit_name, business_unit_number, vendor_account_number, 'VendorGoodsReceiptNote', vendor_goods_receipt_note_number = identifiers
        return os.path.join(base_path, 'VGRN', *identifiers)

# Buyer_sales_contract_document-specific paths
elif document_type == 'buyer_sales_order':
        buyer_name, business_unit_name, business_unit_number, buyer_account_number, 'BuyerSalesOrder', buyer_sales_order_number = identifiers
        return os.path.join(base_path, 'BSO', *identifiers)
    elif document_type == 'buyer_invoice':
        buyer_name, business_unit_name, business_unit_number, buyer_account_number, 'BuyerInvoice', buyer_invoice_number = identifiers
        return os.path.join(base_path, 'BINV', *identifiers)
    elif document_type == 'buyer_packing_list':
        buyer_name, 'N/A', 'N/A', buyer_account_number, 'BuyerPackingList', buyer_packing_list_number = identifiers
        return os.path.join(base_path, 'VPL', *identifiers)
    elif document_type == 'buyer_goods_receipt_note':
        buyer_name, business_unit_name, business_unit_number, buyer_account_number, 'BuyerGoodsReceiptNote', buyer_goods_receipt_note_number = identifiers
        return os.path.join(base_path, 'BGRN', *identifiers)
    # Add similar conditions for other contract types
    
# Import_freight_contract_document-specific paths
    elif document_type == 'import_routing_order':
        import_service_provider_name, business_unit_name, business_unit_number, import_service_provider_account_number, 'ImportRoutingOrder', import_routing_order_number = identifiers
        return os.path.join(base_path, 'IRO', *identifiers)
    elif document_type == 'import_freight_invoice':
        import_service_provider_name, business_unit_name, business_unit_number, import_service_provider_account_number, 'ImportFreightInvoice', import_freight_invoice_number = identifiers
        return os.path.join(base_path, 'IFINV', *identifiers)
    elif document_type == 'import_airway_bill':
        vendor_name, 'N/A', 'N/A', vendor_account_number, 'ImportAirwayBill', import_airway_bill_number = identifiers
        return os.path.join(base_path, IAWB', *identifiers)
    elif document_type == 'import_bill_of_lading':
        vendor_name, 'N/A', 'N/A', vendor_account_number, 'ImportBillOfLading', import_bill_of_lading_number = identifiers
        return os.path.join(base_path, 'IBOL', *identifiers)
    elif document_type == 'import_bill_of_entry':
        vendor_name, 'N/A', 'N/A', vendor_account_number, 'ImportBillOfEntry', import_bill_of_entry_number = identifiers
        return os.path.join(base_path, 'IBOENT', *identifiers)


# Export_freight_contract_document-specific paths
    elif document_type == 'buyer_routing_order':
        export_service_provider_name, business_unit_name, business_unit_number, export_service_provider_account_number, 'ExportRoutingOrder', export_routing_order_number = identifiers
        return os.path.join(base_path, 'ERO', *identifiers)
    elif document_type == 'export_freight_invoice':
        export_service_provider_name, business_unit_name, business_unit_number, export_service_provider_account_number, 'ExportFreightInvoice', export_freight_invoice_number = identifiers
        return os.path.join(base_path, 'EFINV', *identifiers)
    elif document_type == 'export_airway_bill':
        vendor_name, 'N/A', 'N/A', vendor_account_number, 'ExportAirwayBill', export_airway_bill_number = identifiers
        return os.path.join(base_path, EAWB', *identifiers)
    elif document_type == 'export_bill_of_lading':
        vendor_name, 'N/A', 'N/A', vendor_account_number, 'ExportBillOfLading', export_bill_of_lading_number = identifiers
        return os.path.join(base_path, 'EBOL', *identifiers)
    elif document_type == 'export_bill_of_exit':
        vendor_name, 'N/A', 'N/A', vendor_account_number, 'ExportBillOfExit', export_bill_of_exit_number = identifiers
        return os.path.join(base_path, 'EBOEXT', *identifiers)
    
    else:
        return None  # Or a default path

@app.route('/upload/<c(contract_type, document_type, identifiers)>', methods=['POST'])
def upload_file(contract_type, contract_document_folder _type, document_type):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # Generate the appropriate upload path based on contract type and document id
        identifiers = get_identifiers_from_document_id(contract_type, document_id)
        upload_path = generate_upload_path(contract_type, identifiers)

        if not upload_path:
            return jsonify({'error': 'Invalid contract type or document id'}), 400

        filename = secure_filename(document_id + '.pdf')  # Assuming PDF, modify as needed
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, filename))
        return jsonify({'message': f'File uploaded successfully to {upload_path}'}), 201

    return jsonify({'error': 'File type not allowed'}), 400



























































