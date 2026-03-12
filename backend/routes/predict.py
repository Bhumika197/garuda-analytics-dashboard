"""
Garuda Analytics Dashboard - Prediction Route
Handles ML model training and predictions
"""

from flask import Blueprint, request, jsonify, session
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import json
from datetime import datetime

# Create Blueprint for prediction routes
predict_bp = Blueprint('predict', __name__, url_prefix='/api')

class MLPredictor:
    """Machine Learning predictor class"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.feature_columns = None
        self.target_column = None
        self.metrics = None
    
    def prepare_data(self, df, target_column, feature_columns=None):
        """Prepare data for ML training"""
        # Validate target column exists
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in data")
        
        # Select feature columns
        if feature_columns:
            # Filter to only existing columns (excluding target)
            available_features = [col for col in feature_columns if col in df.columns and col != target_column]
        else:
            # Use all numeric columns except target
            available_features = df.select_dtypes(include=[np.number]).columns.tolist()
            available_features = [col for col in available_features if col != target_column]
        
        if not available_features:
            raise ValueError("No valid feature columns available")
        
        # Extract features and target
        X = df[available_features].select_dtypes(include=[np.number])
        y = df[target_column].select_dtypes(include=[np.number])
        
        if X.empty or y.empty:
            raise ValueError("No numeric data available for ML model")
        
        # Remove rows with missing values
        combined_data = pd.concat([X, y], axis=1).dropna()
        X_clean = combined_data[available_features]
        y_clean = combined_data[target_column]
        
        return X_clean, y_clean, available_features
    
    def train_model(self, X, y, model_type='LinearRegression'):
        """Train ML model"""
        if model_type == 'LinearRegression':
            self.model = LinearRegression()
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Calculate metrics
        y_pred = self.model.predict(X_scaled)
        self.metrics = {
            'mean_squared_error': float(mean_squared_error(y, y_pred)),
            'r2_score': float(r2_score(y, y_pred)),
            'mean_absolute_error': float(mean_absolute_error(y, y_pred)),
            'training_samples': len(X)
        }
        
        return self.metrics
    
    def make_predictions(self, X):
        """Make predictions using trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def get_feature_importance(self):
        """Get feature importance (coefficients for linear regression)"""
        if not self.is_trained or not hasattr(self.model, 'coef_'):
            return None
        
        return {
            'features': self.feature_columns,
            'coefficients': self.model.coef_.tolist()
        }

# Global predictor instance
predictor = MLPredictor()

@predict_bp.route('/predict', methods=['POST'])
def predict():
    """
    ML Prediction endpoint
    Trains model and makes predictions on uploaded data
    """
    try:
        # Check if data is available
        if 'uploaded_data' not in session:
            return jsonify({
                'success': False,
                'message': 'No data available. Please upload a CSV file first.'
            }), 400
        
        # Get request data
        data = request.get_json()
        target_column = data.get('target_column')
        feature_columns = data.get('feature_columns', [])
        model_type = data.get('model_type', 'LinearRegression')
        
        if not target_column:
            return jsonify({
                'success': False,
                'message': 'Target column is required'
            }), 400
        
        # Convert session data to DataFrame
        df = pd.DataFrame(session['uploaded_data'])
        
        # Prepare data
        X, y, actual_features = predictor.prepare_data(df, target_column, feature_columns)
        
        # Store feature and target info
        predictor.feature_columns = actual_features
        predictor.target_column = target_column
        
        # Train model
        metrics = predictor.train_model(X, y, model_type)
        
        # Make predictions
        predictions = predictor.make_predictions(X)
        
        # Prepare results
        results = []
        for i, (actual, pred) in enumerate(zip(y, predictions)):
            result = {
                'row_index': i,
                'actual': float(actual),
                'predicted': float(pred),
                'residual': float(actual - pred),
                'features': {col: float(X.iloc[i][col]) for col in X.columns}
            }
            results.append(result)
        
        # Get feature importance
        feature_importance = predictor.get_feature_importance()
        
        # Store prediction results in session
        session['prediction_results'] = {
            'results': results,
            'metrics': metrics,
            'feature_importance': feature_importance,
            'target_column': target_column,
            'feature_columns': actual_features,
            'model_type': model_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Predictions generated successfully',
            'model_info': {
                'model_type': model_type,
                'target_column': target_column,
                'feature_columns': actual_features,
                'training_samples': len(X)
            },
            'metrics': metrics,
            'feature_importance': feature_importance,
            'predictions': results[:100],  # Return first 100 predictions
            'total_predictions': len(results)
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Prediction error: {str(e)}'
        }), 500

@predict_bp.route('/prediction-results', methods=['GET'])
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

@predict_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """
    Get information about the trained model
    """
    try:
        if not predictor.is_trained:
            return jsonify({
                'success': False,
                'message': 'No model trained yet. Please run a prediction first.'
            }), 400
        
        return jsonify({
            'success': True,
            'model_info': {
                'model_type': 'LinearRegression',
                'is_trained': predictor.is_trained,
                'target_column': predictor.target_column,
                'feature_columns': predictor.feature_columns,
                'metrics': predictor.metrics,
                'feature_importance': predictor.get_feature_importance()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving model info: {str(e)}'
        }), 500
