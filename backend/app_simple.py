"""
Simple Flask App for Testing Upload
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import pandas as pd
import numpy as np
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Simple Test API'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        token = f"dev_token_admin_{secrets.token_hex(8)}"
        session['token'] = token
        session['username'] = 'admin'
        return jsonify({'success': True, 'token': token, 'username': 'admin'})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/upload', methods=['POST'])
def upload():
    # Simple token check - accept any token for now
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'success': False, 'message': 'No token provided'}), 401
    
    # Store token in session for consistency
    session['token'] = token
    session['username'] = token.split('_')[2] if '_' in token else 'admin'
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    try:
        df = pd.read_csv(file)
        
        # Store data in session for dashboard
        session['uploaded_data'] = df.to_dict('records')
        session['data_analysis'] = {
            'basic_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist()
            },
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'missing_values': df.isnull().sum().to_dict()
        }
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file_info': {
                'filename': file.filename,
                'size': len(df),
                'columns': df.columns.tolist(),
                'upload_time': datetime.utcnow().isoformat()
            },
            'data_preview': df.head(10).to_dict('records'),
            'analysis': session['data_analysis']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error reading file: {str(e)}'}), 500

@app.route('/api/data-info', methods=['GET'])
def get_data_info():
    # Simple token check
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'success': False, 'message': 'No token provided'}), 401
    
    # Update session with current token
    session['token'] = token
    session['username'] = token.split('_')[2] if '_' in token else 'admin'
    
    if 'data_analysis' not in session:
        return jsonify({
            'success': False,
            'message': 'No data available. Please upload a CSV file first.'
        }), 400
    
    return jsonify({
        'success': True,
        'data_info': session['data_analysis']
    })

if __name__ == '__main__':
    print("Starting simple test server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
