"""
Garuda Analytics Dashboard - Main Flask Application (Development Version)
This is the main entry point for the backend API server.
Development version that works without PostgreSQL database.
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime, timedelta
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import os
import secrets

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate random secret key for session

# Enable CORS for all routes
CORS(app)

# Secret key for JWT
SECRET_KEY = 'garuda_analytics_secret_key'

@app.route('/auth/verify', methods=['POST'])
def verify_token():
    """
    Verify session token endpoint
    """
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is required'
            }), 400
        
        # Check if token exists in session or recreate it
        if session.get('user_token') == token:
            return jsonify({
                'success': True,
                'message': 'Token is valid',
                'username': session.get('username')
            })
        elif token.startswith('dev_token_'):
            username = token.split('_')[2]
            if username in ['admin', 'user', 'demo']:
                session['user_token'] = token
                session['username'] = username
                return jsonify({
                    'success': True,
                    'message': 'Token recreated and valid',
                    'username': username
                })
        
        return jsonify({
            'success': False,
            'message': 'Token is invalid'
        }), 401
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Token verification error: {str(e)}'
        }), 500

@app.route('/debug/token', methods=['GET'])
def debug_token():
    """Debug endpoint to check token validation"""
    token = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(" ")[1]
    
    return jsonify({
        'received_token': token,
        'session_token': session.get('user_token'),
        'session_username': session.get('username'),
        'valid': session.get('user_token') == token
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Garuda Analytics Dashboard API (Dev Mode)'
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
        valid_users = {
            'admin': 'admin123',
            'user': 'user123',
            'demo': 'demo123'
        }
        
        if username in valid_users and valid_users[username] == password:
            # Create simple session token (dev mode)
            session_token = f"dev_token_{username}_{secrets.token_hex(8)}"
            session['user_token'] = session_token
            session['username'] = username
            
            return jsonify({
                'success': True,
                'token': session_token,
                'username': username,
                'message': 'Login successful'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500

def token_required(f):
    """Decorator to require session token for endpoints (dev version)"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        elif request.args.get('token'):
            token = request.args.get('token')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        # Check if token exists in session
        if session.get('user_token') != token:
            # Try to extract username from token and check if session exists
            if token.startswith('dev_token_'):
                username = token.split('_')[2]
                # Create a new session if username matches
                if username in ['admin', 'user', 'demo']:
                    session['user_token'] = token
                    session['username'] = username
                    return f(*args, **kwargs)
            
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
        # Handle both form data and JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
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
                
                # Store data in session for prediction use
                data_preview = df.head(10).to_dict('records')
                columns = df.columns.tolist()
                row_count = len(df)
                
                # Store in session
                session['uploaded_data'] = df.to_dict('records')
                session['columns'] = columns
                
                # Analyze data
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
                
                session['data_analysis'] = analysis
                
                return jsonify({
                    'success': True,
                    'message': 'File uploaded successfully',
                    'file_info': {
                        'filename': file.filename,
                        'size': len(df),
                        'columns': columns,
                        'upload_time': datetime.utcnow().isoformat()
                    },
                    'data_preview': data_preview,
                    'analysis': analysis
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Please upload a CSV file'
                }), 400
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid content type. Please use multipart/form-data'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Upload error: {str(e)}'
        }), 500

@app.route('/api/data-info', methods=['GET'])
@token_required
def get_data_info():
    """
    Get information about currently uploaded data
    """
    try:
        if 'data_analysis' not in session:
            return jsonify({
                'success': False,
                'message': 'No data available. Please upload a CSV file first.'
            }), 400
        
        analysis = session.get('data_analysis', {})
        
        return jsonify({
            'success': True,
            'data_info': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving data info: {str(e)}'
        }), 500

@app.route('/api/clear-data', methods=['DELETE'])
@token_required
def clear_data():
    """
    Clear uploaded data from session
    """
    try:
        keys_to_remove = ['uploaded_data', 'data_analysis', 'columns']
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
                'residual': float(y.iloc[i] - pred) if i < len(y) else None,
                'features': {col: float(X.iloc[i][col]) for col in X.columns}
            }
            results.append(result)
        
        # Calculate model metrics
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
        mse = mean_squared_error(y, predictions)
        r2 = r2_score(y, predictions)
        mae = mean_absolute_error(y, predictions)
        
        # Store prediction results in session
        prediction_results = {
            'success': True,
            'target_column': target_column,
            'feature_columns': available_columns,
            'metrics': {
                'mean_squared_error': float(mse),
                'r2_score': float(r2),
                'mean_absolute_error': float(mae)
            },
            'feature_importance': {
                'features': available_columns,
                'coefficients': model.coef_.tolist()
            },
            'predictions': results,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        session['prediction_results'] = prediction_results
        
        return jsonify(prediction_results)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Prediction error: {str(e)}'
        }), 500

@app.route('/api/prediction-results', methods=['GET'])
@token_required
def get_prediction_results():
    """
    Get stored prediction results
    """
    try:
        if 'prediction_results' not in session:
            return jsonify({
                'success': False,
                'message': 'No prediction results available. Please run a prediction first.'
            }), 400
        
        results = session['prediction_results']
        
        return jsonify({
            'success': True,
            'prediction_results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving prediction results: {str(e)}'
        }), 500

@app.route('/api/model-info', methods=['GET'])
@token_required
def get_model_info():
    """
    Get information about the trained model
    """
    try:
        if 'prediction_results' not in session:
            return jsonify({
                'success': False,
                'message': 'No model trained yet. Please run a prediction first.'
            }), 400
        
        results = session['prediction_results']
        
        return jsonify({
            'success': True,
            'model_info': {
                'model_type': 'LinearRegression',
                'is_trained': True,
                'target_column': results['target_column'],
                'feature_columns': results['feature_columns'],
                'metrics': results['metrics'],
                'feature_importance': results['feature_importance']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving model info: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Starting Garuda Analytics Dashboard Backend (Development Mode)...")
    print("Server will be available at: http://localhost:5000")
    print("Note: This version uses session storage instead of PostgreSQL database")
    app.run(host='0.0.0.0', port=5000, debug=True)
