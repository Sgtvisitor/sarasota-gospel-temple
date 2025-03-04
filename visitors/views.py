from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json
import os
import logging
from dotenv import load_dotenv
from .forms import VisitorForm
from .models import Visitor
import mysql.connector
import requests
import firebase_admin
from firebase_admin import credentials, auth
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .utils import send_email_via_sendgrid, add_visitor_to_clearstream, send_followup_sms

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# Set the Django settings module explicitly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visitor_manager.settings')

# Initialize Firebase Admin SDK (Ensure it initializes only once)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase-adminsdk.json")
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")

# Admin email for notifications
ADMIN_EMAIL = "visit@sarasotagospeltemple.com"

# ✅ Connect to AWS RDS MySQL
def connect_db():
    """Connect to AWS RDS MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", "3306"))
        )
        logger.info("Connected to AWS RDS successfully!")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database Connection Error: {err}")
        return None

# ✅ Fetch List of Visitors
def list_visitors():
    """Fetch all visitors from the database."""
    conn = connect_db()
    if conn is None:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, phone, visit_status, visit_request, visit_date FROM visitors")
        visitors = cursor.fetchall()
        conn.close()
        logger.info(f"Fetched {len(visitors)} visitors from the database.")
        return visitors
    except mysql.connector.Error as err:
        logger.error(f"Query Error: {err}")
        return []

# ✅ Home View
def home(request):
    """Render the home page."""
    return render(request, 'visitors/home.html')

# ✅ Contact View
def contact(request):
    """Render the contact page."""
    if request.method == 'POST':
        # Add contact form handling logic here if needed (e.g., form submission)
        return render(request, 'visitors/contact.html')
    return render(request, 'visitors/contact.html')

# ✅ Success Page View
def success(request):
    """Render the success page after form submission."""
    return render(request, 'visitors/success.html')

logger = logging.getLogger(__name__)

# Configure logging
logger = logging.getLogger(__name__)

# Configure logging
logger = logging.getLogger(__name__)

# Configure logging
logger = logging.getLogger(__name__)

def visitor_form(request):
    """Handle visitor form submission, including AJAX requests."""
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        form = VisitorForm(request.POST)
        if form.is_valid():
            try:
                visitor = form.save()
                logger.info(f"Visitor {visitor.name} saved to the database.")
                
                # Handle name for notifications
                if " " in visitor.name:
                    first_name, last_name = visitor.name.split(" ", 1)
                else:
                    first_name, last_name = visitor.name, ""
                
                # Send notifications (use flexible address handling)
                send_email_via_sendgrid(visitor, first_name=first_name, last_name=last_name)
                add_visitor_to_clearstream(visitor.phone, first_name, last_name)
                send_followup_sms(visitor.phone)
                
                if is_ajax:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Visitor information submitted successfully!'
                    }, status=201)
                else:
                    messages.success(request, "Visitor information submitted successfully!")
                    return redirect('home')
            except Exception as e:
                logger.error(f"Error processing visitor form: {e}")
                if is_ajax:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Error submitting visitor information: {str(e)}'
                    }, status=500)
                else:
                    messages.error(request, f"Error submitting visitor information: {str(e)}")
                    return render(request, 'visitors/visitor_form.html', {'form': form})
        else:
            logger.error(f"Form validation failed: {form.errors}")
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors
                }, status=400)
            else:
                return render(request, 'visitors/visitor_form.html', {'form': form})
    else:
        form = VisitorForm()
    
    return render(request, 'visitors/visitor_form.html', {'form': form})

# Other views remain unchanged unless needed

# ✅ Django API View to Fetch Visitors (GET Request)
def get_visitors(request):
    """API endpoint to return visitor data as JSON."""
    visitors = list_visitors()
    return JsonResponse({"visitors": visitors}, safe=False)

# ✅ API View to Save a Visitor (POST Request)
@csrf_exempt
def save_visitor(request):
    """Saves visitor details to the database via API and returns a response."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            name = data.get("name", "").strip()
            phone = data.get("phone", "").strip()
            address = data.get("address", "").strip()
            visit_request = data.get("visit_request", "No")
            visit_status = data.get("visit_status", "Pending")
            visit_date = data.get("visit_date", None)
            sms_opt_in = data.get("sms_opt_in", False)

            if not name or not phone:
                return JsonResponse({"error": "Name and Phone are required!"}, status=400)

            conn = connect_db()
            if conn is None:
                return JsonResponse({"error": "Database Connection Failed!"}, status=500)

            cursor = conn.cursor()
            query = """
            INSERT INTO visitors (name, phone, address, visit_request, visit_status, visit_date, sms_opt_in)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, phone, address, visit_request, visit_status, visit_date, sms_opt_in))
            conn.commit()
            visitor_id = cursor.lastrowid
            conn.close()

            # Fetch the newly created visitor to send notifications
            visitor = Visitor.objects.get(id=visitor_id)
            send_email_via_sendgrid(visitor)
            first_name, last_name = visitor.name.split(" ", 1) if " " in visitor.name else (visitor.name, "")
            add_visitor_to_clearstream(visitor.phone, first_name, last_name)
            send_followup_sms(visitor.phone)

            logger.info(f"Visitor {name} added successfully via API.")
            return JsonResponse({"message": "Visitor added successfully!", "id": visitor_id}, status=201)

        except mysql.connector.Error as err:
            logger.error(f"Database error in save_visitor: {err}")
            return JsonResponse({"error": f"Database error: {err}"}, status=500)
        except Exception as e:
            logger.error(f"Error in save_visitor: {e}")
            return JsonResponse({"error": f"Error processing request: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)

# ✅ API View to Delete a Visitor (POST Request)
@csrf_exempt
def delete_visitor(request):
    """Deletes a visitor from the database via API."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            visitor_id = data.get("id")

            if not visitor_id:
                return JsonResponse({"error": "Visitor ID is required!"}, status=400)

            conn = connect_db()
            if conn is None:
                return JsonResponse({"error": "Database Connection Failed!"}, status=500)

            cursor = conn.cursor()
            cursor.execute("DELETE FROM visitors WHERE id = %s", (visitor_id,))
            conn.commit()
            conn.close()

            logger.info(f"Visitor with ID {visitor_id} deleted successfully via API.")
            return JsonResponse({"message": "Visitor deleted successfully!"}, status=200)

        except mysql.connector.Error as err:
            logger.error(f"Database error in delete_visitor: {err}")
            return JsonResponse({"error": f"Database error: {err}"}, status=500)
        except Exception as e:
            logger.error(f"Error in delete_visitor: {e}")
            return JsonResponse({"error": f"Error processing request: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)

# ✅ Register User (Firebase & MySQL)
def register_user(email, password, role):
    """Registers a user in Firebase and stores their role in AWS MySQL."""
    try:
        # Create user in Firebase
        user = auth.create_user(email=email, password=password)
        logger.info(f"Firebase user created: {email}")

        # Store user in AWS RDS MySQL
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
                          (email, hashed_password, role))
            conn.commit()
            conn.close()
            logger.info(f"User {email} stored in AWS MySQL with role {role}")
            return True
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return False

# ✅ Delete User (Firebase & MySQL)
def delete_user(email):
    """Deletes a user from Firebase Authentication and MySQL database."""
    try:
        user = auth.get_user_by_email(email)
        auth.delete_user(user.uid)
        logger.info(f"Firebase user {email} deleted.")

        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE email = %s", (email,))
            conn.commit()
            conn.close()
            logger.info(f"User {email} deleted from AWS MySQL.")
            return True
    except firebase_admin.auth.UserNotFoundError:
        logger.warning(f"User {email} not found in Firebase.")
        return False
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return False