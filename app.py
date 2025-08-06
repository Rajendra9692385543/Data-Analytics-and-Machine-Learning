from flask import Flask, request, render_template
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return 'No file uploaded'
    file = request.files['file']
    if file.filename == '':
        return 'No file selected'

    # Save uploaded file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(filepath)

    # Read Excel
    df = pd.read_excel(filepath)
    df.columns = df.columns.str.strip()

    # Find roll number column (case-insensitive)
    roll_col = None
    for col in df.columns:
        if "roll" in col.lower():
            roll_col = col
            break
    if not roll_col:
        return "No Roll Number column found."

    # Define metadata columns (lowercased for matching)
    meta_keywords = ['admno', 'rollno', 'roll no', 'roll', 'student', 'name', 'division']
    subject_cols = [col for col in df.columns if not any(k in col.lower() for k in meta_keywords)]

    student_data = []
    min_roll, max_roll = float('inf'), float('-inf')

    for _, row in df.iterrows():
        roll = str(row[roll_col]).strip()
        try:
            num_roll = int(float(roll))
            min_roll = min(min_roll, num_roll)
            max_roll = max(max_roll, num_roll)
        except:
            continue

        subjects = []
        for subject in subject_cols:
            value = row[subject]
            if pd.notna(value) and isinstance(value, (int, float)):
                attendance = round(value, 2)
                subjects.append({
                    'name': subject,
                    'attendance': attendance,
                    'low_attendance': attendance < 75  # Flag low attendance
                })

        student_data.append({
            'roll': roll,
            'subjects': subjects
        })

    return render_template('result.html', data=student_data, min_roll=min_roll, max_roll=max_roll)

if __name__ == '__main__':
    app.run(debug=True)
