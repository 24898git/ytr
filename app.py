from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import sqlite3
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'patient_management_secret_key_2024'

# Database configuration
DATABASE = 'patients.db'

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with patients table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            contact TEXT,
            email TEXT,
            address TEXT,
            medical_history TEXT,
            allergies TEXT,
            medications TEXT,
            last_visit DATE,
            emergency_contact TEXT,
            blood_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def generate_patient_id():
    """Generate a unique patient ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    current_year = datetime.now().year
    cursor.execute("SELECT COUNT(*) FROM patients WHERE patient_id LIKE ?", (f'PAT{current_year}%',))
    count = cursor.fetchone()[0] + 1
    
    patient_id = f'PAT{current_year}{count:04d}'
    conn.close()
    return patient_id

@app.route('/')
def index():
    """Home page - Show all patients"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT * FROM patients 
        ORDER BY created_at DESC
    ''')
    patients = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                         patients=patients,
                         total_patients=total_patients)

@app.route('/add', methods=['GET', 'POST'])
def add_patient():
    """Add new patient"""
    if request.method == 'POST':
        try:
            patient_id = generate_patient_id()
            
            # Get form data
            name = request.form.get('name', '').strip()
            age = request.form.get('age', '0').strip()
            gender = request.form.get('gender', '').strip()
            contact = request.form.get('contact', '').strip()
            email = request.form.get('email', '').strip()
            address = request.form.get('address', '').strip()
            medical_history = request.form.get('medical_history', '').strip()
            allergies = request.form.get('allergies', '').strip()
            medications = request.form.get('medications', '').strip()
            last_visit = request.form.get('last_visit', '').strip()
            emergency_contact = request.form.get('emergency_contact', '').strip()
            blood_type = request.form.get('blood_type', '').strip()
            
            # Validate required fields
            if not name or not age or not gender:
                flash('Please fill in all required fields (Name, Age, Gender).', 'error')
                return render_template('add_patient.html')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO patients 
                (patient_id, name, age, gender, contact, email, address, 
                 medical_history, allergies, medications, last_visit, 
                 emergency_contact, blood_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, name, age, gender, contact, email, address,
                  medical_history, allergies, medications, last_visit,
                  emergency_contact, blood_type))
            
            conn.commit()
            conn.close()
            
            flash(f'✅ Patient {patient_id} added successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'❌ Error adding patient: {str(e)}', 'error')
    
    return render_template('add_patient.html')

@app.route('/edit/<string:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    """Edit patient information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            age = request.form.get('age', '0').strip()
            gender = request.form.get('gender', '').strip()
            contact = request.form.get('contact', '').strip()
            email = request.form.get('email', '').strip()
            address = request.form.get('address', '').strip()
            medical_history = request.form.get('medical_history', '').strip()
            allergies = request.form.get('allergies', '').strip()
            medications = request.form.get('medications', '').strip()
            last_visit = request.form.get('last_visit', '').strip()
            emergency_contact = request.form.get('emergency_contact', '').strip()
            blood_type = request.form.get('blood_type', '').strip()
            
            # Validate required fields
            if not name or not age or not gender:
                flash('Please fill in all required fields (Name, Age, Gender).', 'error')
                return redirect(url_for('edit_patient', patient_id=patient_id))
            
            cursor.execute('''
                UPDATE patients SET 
                name=?, age=?, gender=?, contact=?, email=?, address=?, 
                medical_history=?, allergies=?, medications=?, last_visit=?,
                emergency_contact=?, blood_type=?
                WHERE patient_id=?
            ''', (name, age, gender, contact, email, address,
                  medical_history, allergies, medications, last_visit,
                  emergency_contact, blood_type, patient_id))
            
            conn.commit()
            flash(f'✅ Patient {patient_id} updated successfully!', 'success')
            
        except Exception as e:
            flash(f'❌ Error updating patient: {str(e)}', 'error')
        finally:
            conn.close()
            return redirect(url_for('index'))
    
    # GET request - show edit form
    cursor.execute("SELECT * FROM patients WHERE patient_id=?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    
    if patient:
        return render_template('edit_patient.html', patient=patient)
    else:
        flash('❌ Patient not found!', 'error')
        return redirect(url_for('index'))

@app.route('/delete/<string:patient_id>')
def delete_patient(patient_id):
    """Delete patient"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM patients WHERE patient_id=?", (patient_id,))
        conn.commit()
        conn.close()
        
        flash(f'✅ Patient {patient_id} deleted successfully!', 'success')
    except Exception as e:
        flash(f'❌ Error deleting patient: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/view/<string:patient_id>')
def view_history(patient_id):
    """View patient history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM patients WHERE patient_id=?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    
    if patient:
        return render_template('view_history.html', patient=patient)
    else:
        flash('❌ Patient not found!', 'error')
        return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_patients():
    """Search patients by name or patient ID"""
    patients = []
    search_query = ""
    
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        
        if search_query:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM patients 
                WHERE name LIKE ? OR patient_id LIKE ? OR contact LIKE ?
                ORDER BY name
            ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
            
            patients = cursor.fetchall()
            conn.close()
            
            if not patients:
                flash('🔍 No patients found matching your search.', 'info')
        else:
            flash('⚠️ Please enter a search term.', 'warning')
    
    return render_template('search.html', patients=patients, search_query=search_query)

@app.route('/print')
def print_list():
    """Print patient list with export options"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM patients ORDER BY name")
    patients = cursor.fetchall()
    conn.close()
    
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('print_list.html', patients=patients, current_date=current_date)

@app.route('/export/csv')
def export_csv():
    """Export patients to CSV"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT patient_id, name, age, gender, contact, email, address, 
               medical_history, allergies, medications, last_visit,
               emergency_contact, blood_type, created_at
        FROM patients ORDER BY name
    ''')
    patients = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Patient ID', 'Name', 'Age', 'Gender', 'Contact', 'Email', 'Address',
        'Medical History', 'Allergies', 'Medications', 'Last Visit',
        'Emergency Contact', 'Blood Type', 'Created At'
    ])
    
    # Write data
    for patient in patients:
        writer.writerow([
            patient['patient_id'], patient['name'], patient['age'], 
            patient['gender'], patient['contact'], patient['email'],
            patient['address'], patient['medical_history'], 
            patient['allergies'], patient['medications'], patient['last_visit'],
            patient['emergency_contact'], patient['blood_type'],
            patient['created_at']
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'patients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/stats')
def statistics():
    """Show statistics about patients"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total patients
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]
    
    # Patients by gender
    cursor.execute("SELECT gender, COUNT(*) FROM patients GROUP BY gender")
    gender_stats = cursor.fetchall()
    
    # Recent registrations (last 30 days)
    cursor.execute('''
        SELECT COUNT(*) FROM patients 
        WHERE date(created_at) >= date('now', '-30 days')
    ''')
    recent_result = cursor.fetchone()
    recent_registrations = recent_result[0] if recent_result else 0
    
    conn.close()
    
    return render_template('statistics.html',
                         total_patients=total_patients,
                         gender_stats=gender_stats,
                         recent_registrations=recent_registrations)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    print("🚀 Patient Management System starting...")
    print("📊 Access the application at: http://localhost:8000")
    app.run(debug=True, host='0.0.0.0', port=8000)