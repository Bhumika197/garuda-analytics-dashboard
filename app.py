"""
Railway Main App - Backend + Frontend
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import pandas as pd
import numpy as np
import secrets
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Global storage
GLOBAL_DATA = {}

@app.route('/')
def index():
    """Serve frontend"""
    return send_from_directory('.', 'dashboard_simple.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Garuda Analytics API'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        token = f"dev_token_admin_{secrets.token_hex(8)}"
        return jsonify({'success': True, 'token': token})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/upload', methods=['POST'])
def upload():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'success': False, 'message': 'No token'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file'}), 400
    
    file = request.files['file']
    try:
        df = pd.read_csv(file)
        analysis = {
            'basic_info': {'rows': len(df), 'columns': len(df.columns), 'column_names': df.columns.tolist()},
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'missing_values': df.isnull().sum().to_dict()
        }
        GLOBAL_DATA[token] = {'analysis': analysis, 'filename': file.filename}
        return jsonify({'success': True, 'message': 'Uploaded', 'analysis': analysis})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/data-info', methods=['GET'])
def get_data_info():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token not in GLOBAL_DATA:
        return jsonify({'success': False, 'message': 'No data'}), 400
    return jsonify({'success': True, 'data_info': GLOBAL_DATA[token]['analysis']})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
