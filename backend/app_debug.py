"""
Debug Flask App - Global Storage
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import pandas as pd
import numpy as np
import secrets

app = Flask(__name__)
CORS(app)

# Global storage for data (simple solution)
GLOBAL_DATA = {}

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Debug API'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        token = f"dev_token_admin_{secrets.token_hex(8)}"
        return jsonify({'success': True, 'token': token, 'username': 'admin'})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/upload', methods=['POST'])
def upload():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'success': False, 'message': 'No token provided'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    try:
        df = pd.read_csv(file)
        
        # Store in global variable
        analysis = {
            'basic_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist()
            },
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'missing_values': df.isnull().sum().to_dict()
        }
        
        # Store globally with token as key
        GLOBAL_DATA[token] = {
            'analysis': analysis,
            'filename': file.filename,
            'upload_time': datetime.utcnow().isoformat()
        }
        
        print(f"Data stored for token: {token}")
        print(f"Global data keys: {list(GLOBAL_DATA.keys())}")
        
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
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error reading file: {str(e)}'}), 500

@app.route('/api/data-info', methods=['GET'])
def get_data_info():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'success': False, 'message': 'No token provided'}), 401
    
    print(f"Looking for data with token: {token}")
    print(f"Available tokens: {list(GLOBAL_DATA.keys())}")
    
    if token not in GLOBAL_DATA:
        return jsonify({
            'success': False,
            'message': 'No data available. Please upload a CSV file first.'
        }), 400
    
    return jsonify({
        'success': True,
        'data_info': GLOBAL_DATA[token]['analysis']
    })

if __name__ == '__main__':
    print("Starting debug server with global storage...")
    app.run(host='0.0.0.0', port=5000, debug=True)
