"""
Garuda Analytics Dashboard - Main Flask Application
This is the main entry point for the backend API server.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from database import Database
import jwt
from datetime import datetime, timedelta
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for all routes
CORS(app)

# Initialize database connection
db = Database()

# Secret key for JWT
SECRET_KEY = app.config.get('SECRET_KEY', 'garuda_analytics_secret_key')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Garuda Analytics Dashboard API'
    })

@app.route('/login', methods=['POST'])
def login():
    """
    Login endpoint - JWT Authentication
    Returns JWT token for authenticated users
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Simple authentication (in production, use proper password hashing)
        if username and password:
            # Create JWT token
            token = jwt.encode({
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, SECRET_KEY, algorithm='HS256')
            
            return jsonify({
                'success': True,
                'token': token,
                'username': username,
                'message': 'Login successful'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Username and password required'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500

def token_required(f):
    """Decorator to require JWT token for endpoints"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(*args, **kwargs)
    return decorated

@app.route('/upload', methods=['POST'])
@token_required
def upload_csv():
    """
    Upload CSV file endpoint
    Accepts CSV file and stores data for ML processing
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        if file and file.filename.endswith('.csv'):
            # Read CSV using pandas
            df = pd.read_csv(file)
            
            # Store data in database (simplified - in production, use proper table)
            data_preview = df.head(10).to_dict('records')
            columns = df.columns.tolist()
            row_count = len(df)
            
            # Store in session for prediction use
            from flask import session
            session['uploaded_data'] = df.to_dict('records')
            session['columns'] = columns
            
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'data_preview': data_preview,
                'columns': columns,
                'row_count': row_count
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Please upload a CSV file'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Upload error: {str(e)}'
        }), 500

@app.route('/predict', methods=['POST'])
@token_required
def predict():
    """
    ML Prediction endpoint
    Uses LinearRegression to make predictions on uploaded data
    """
    try:
        data = request.get_json()
        target_column = data.get('target_column')
        feature_columns = data.get('feature_columns', [])
        
        from flask import session
        if 'uploaded_data' not in session:
            return jsonify({
                'success': False,
                'message': 'No data available for prediction. Please upload a CSV file first.'
            }), 400
        
        # Convert session data back to DataFrame
        df = pd.DataFrame(session['uploaded_data'])
        
        if target_column not in df.columns:
            return jsonify({
                'success': False,
                'message': f'Target column "{target_column}" not found in data'
            }), 400
        
        # Filter feature columns to only those that exist in the data
        available_columns = [col for col in feature_columns if col in df.columns and col != target_column]
        
        if not available_columns:
            return jsonify({
                'success': False,
                'message': 'No valid feature columns provided'
            }), 400
        
        # Prepare data for ML model
        X = df[available_columns].select_dtypes(include=[np.number])  # Only numeric columns
        y = df[target_column].select_dtypes(include=[np.number])  # Only numeric target
        
        if X.empty or y.empty:
            return jsonify({
                'success': False,
                'message': 'No numeric data available for ML model'
            }), 400
        
        # Train Linear Regression model
        model = LinearRegression()
        model.fit(X, y)
        
        # Make predictions
        predictions = model.predict(X)
        
        # Prepare results
        results = []
        for i, pred in enumerate(predictions):
            result = {
                'row_index': i,
                'actual': float(y.iloc[i]) if i < len(y) else None,
                'predicted': float(pred),
                'features': {col: float(X.iloc[i][col]) for col in X.columns}
            }
            results.append(result)
        
        # Calculate model metrics
        from sklearn.metrics import mean_squared_error, r2_score
        mse = mean_squared_error(y, predictions)
        r2 = r2_score(y, predictions)
        
        return jsonify({
            'success': True,
            'message': 'Predictions generated successfully',
            'results': results,
            'model_metrics': {
                'mean_squared_error': float(mse),
                'r2_score': float(r2),
                'feature_columns': available_columns,
                'target_column': target_column
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Prediction error: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Starting Garuda Analytics Dashboard Backend...")
    print("Server will be available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
