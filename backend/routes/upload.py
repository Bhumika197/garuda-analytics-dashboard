"""
Garuda Analytics Dashboard - Upload Route
Handles CSV file uploads and data processing
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import os
from datetime import datetime
import json

# Create Blueprint for upload routes
upload_bp = Blueprint('upload', __name__, url_prefix='/api')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_data(df):
    """Analyze uploaded data and return statistics"""
    analysis = {
        'basic_info': {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'memory_usage': df.memory_usage(deep=True).sum()
        },
        'data_types': df.dtypes.to_dict(),
        'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
        'missing_values': df.isnull().sum().to_dict(),
        'statistics': {}
    }
    
    # Add statistics for numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        analysis['statistics'] = {
            'describe': numeric_df.describe().to_dict(),
            'correlation': numeric_df.corr().to_dict()
        }
    
    return analysis

@upload_bp.route('/upload', methods=['POST'])
def upload_csv():
    """
    Upload CSV file endpoint
    Accepts CSV file and returns data analysis
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Please upload a CSV file.'
            }), 400
        
        # Read and process CSV
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error reading CSV file: {str(e)}'
            }), 400
        
        # Validate DataFrame
        if df.empty:
            return jsonify({
                'success': False,
                'message': 'CSV file is empty'
            }), 400
        
        # Analyze data
        analysis = analyze_data(df)
        
        # Store data in session for later use
        session['uploaded_data'] = df.to_dict('records')
        session['data_analysis'] = analysis
        session['upload_timestamp'] = datetime.utcnow().isoformat()
        
        # Prepare preview data
        preview_data = df.head(10).to_dict('records')
        
        return jsonify({
            'success': True,
            'message': 'File uploaded and analyzed successfully',
            'file_info': {
                'filename': secure_filename(file.filename),
                'size': len(df),
                'columns': df.columns.tolist(),
                'upload_time': session['upload_timestamp']
            },
            'data_preview': preview_data,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Upload error: {str(e)}'
        }), 500

@upload_bp.route('/data-info', methods=['GET'])
def get_data_info():
    """
    Get information about currently uploaded data
    """
    try:
        if 'uploaded_data' not in session:
            return jsonify({
                'success': False,
                'message': 'No data available. Please upload a CSV file first.'
            }), 400
        
        analysis = session.get('data_analysis', {})
        upload_time = session.get('upload_timestamp')
        
        return jsonify({
            'success': True,
            'data_info': analysis,
            'upload_time': upload_time
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving data info: {str(e)}'
        }), 500

@upload_bp.route('/clear-data', methods=['DELETE'])
def clear_data():
    """
    Clear uploaded data from session
    """
    try:
        keys_to_remove = ['uploaded_data', 'data_analysis', 'upload_timestamp']
        for key in keys_to_remove:
            session.pop(key, None)
        
        return jsonify({
            'success': True,
            'message': 'Data cleared successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error clearing data: {str(e)}'
        }), 500
