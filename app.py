from flask import Flask, render_template, request, send_from_directory, jsonify, session, redirect, url_for
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a secret key for session management

# Directory to store invoices
INVOICE_DIR = 'invoices'
os.makedirs(INVOICE_DIR, exist_ok=True)
if not os.path.exists(INVOICE_DIR):
    os.makedirs(INVOICE_DIR)

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin@123'

@app.route('/')
def Invoice():
    # Show login page if not logged in
    if 'logged_in' not in session:
        return render_template('invoice.html')
    else:
        return redirect(url_for('admin_panel'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True  # Set session to indicate logged-in state
        return jsonify({'status': 'success', 'message': 'Login successful'})
    return jsonify({'status': 'error', 'message': 'Invalid credentials'})


@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('index'))  # Redirect to the login page


@app.route('/admin-panel')
def admin_panel():
    if 'logged_in' in session:
        return render_template('invoice.html')  # Show the admin panel if logged in
    else:
        return redirect(url_for('index'))  # Redirect to login if not logged in



@app.route('/create-invoice', methods=['POST'])
def create_invoice():
    if 'logged_in' not in session:
        return jsonify({'status': 'error', 'message': 'You must log in first'}), 401

    # Extract form data
    customer_name = request.form.get('customer_name')
    mobile_number = request.form.get('mobile_number')
    invoice_date = datetime.now().strftime('%Y-%m-%d')  # Set current date as invoice date
    due_date = request.form.get('due_date')
    items = request.form.get('items')  # Comma-separated items
    amount = float(request.form.get('amount'))
    tax = float(request.form.get('tax'))
    total_amount = amount + tax

    # Business Information
    business_name = "Sisodiya Timber"
    business_phone = "9981222262"
    business_address = "51 GNT Market, Dhar Rd, Indore"

    # Generate invoice file name
    invoice_id = len(os.listdir(INVOICE_DIR)) + 1
    file_name = f"invoice_{invoice_id}_{mobile_number}.pdf"
    file_path = os.path.join(INVOICE_DIR, file_name)

    # Create a PDF with a professional format
    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(200, 750, f"{business_name.upper()}")
    
    # Add a line separator after the business name
    c.setLineWidth(1)
    c.line(50, 740, 550, 740)

    # Business Information (Header)
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Phone: {business_phone}")
    c.drawString(50, 705, f"Address: {business_address}")

    # Invoice Header Information
    c.setFont("Helvetica-Bold", 14)
    c.drawString(400, 720, f"Invoice Date: {invoice_date}")
    c.drawString(50, 680, f"Invoice ID: {invoice_id}")
    c.drawString(400, 705, f"Due Date: {due_date}")

    # Customer Information
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 660, f"Customer Name: {customer_name}")
    c.drawString(50, 645, f"Mobile Number: {mobile_number}")
    
    # Add a line separator after customer details
    c.line(50, 635, 550, 635)

    # Table Header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 610, "Item Description")
    c.drawString(350, 610, "Amount")
    c.line(50, 605, 550, 605)

    # Items list
    c.setFont("Helvetica", 10)
    y_position = 590
    for item in items.split(','):
        c.drawString(50, y_position, f"- {item.strip()}")
        y_position -= 15

    # Amounts and totals
    c.setFont("Helvetica", 10)
    c.drawString(350, 590, f"{amount:.2f}")
    c.drawString(50, y_position - 10, f"Tax:")
    c.drawString(350, y_position - 10, f"{tax:.2f}")
    y_position -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Total Amount:")
    c.drawString(350, y_position, f"{total_amount:.2f}")

    # Add a footer separator line
    c.line(50, 100, 550, 100)

    # Footer Message
    c.setFont("Helvetica", 8)
    c.drawString(50, 80, "Thank you for your business!")
    c.drawString(50, 65, "This invoice is system-generated and does not require a signature.")

    c.save()

    return jsonify({'status': 'success', 'message': 'Invoice created successfully!'})

@app.route('/view-invoices', methods=['GET'])
def view_invoices():
    if 'logged_in' not in session:
        return jsonify({'status': 'error', 'message': 'You must log in first'}), 401

    try:
        invoice_files = os.listdir(INVOICE_DIR)
        invoice_list = [file for file in invoice_files if file.endswith('.pdf')]
        return jsonify({'status': 'success', 'invoices': invoice_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/delete-invoice/<filename>', methods=['DELETE'])
def delete_invoice(filename):
    if 'logged_in' not in session:
        return jsonify({'status': 'error', 'message': 'You must log in first'}), 401

    try:
        file_path = os.path.join(INVOICE_DIR, filename)
        
        # Ensure file exists before deleting
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'status': 'success', 'message': f'Invoice {filename} deleted successfully!'})
        else:
            return jsonify({'status': 'error', 'message': f'Invoice {filename} not found!'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/download-invoice', methods=['POST'])
def download_invoice():
    mobile_number = request.form['mobile_number']
    # Find the file matching the mobile number
    for file_name in os.listdir(INVOICE_DIR):
        if mobile_number in file_name:
            return send_from_directory(INVOICE_DIR, file_name, as_attachment=True)
    return jsonify({'status': 'error', 'message': 'Invoice not found'})


if __name__ == '__main__':
    app.run(debug=True)
