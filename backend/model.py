"""
Garuda Analytics Dashboard - Data Models
Contains data models for the application
"""

from datetime import datetime
import json

class User:
    """User model for authentication"""
    
    def __init__(self, username, user_id=None):
        self.id = user_id
        self.username = username
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat()
        }

class Dataset:
    """Dataset model for file uploads"""
    
    def __init__(self, filename, file_size, user_id=None, dataset_id=None):
        self.id = dataset_id
        self.filename = filename
        self.file_size = file_size
        self.user_id = user_id
        self.upload_date = datetime.utcnow()
    
    def to_dict(self):
        """Convert dataset to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'user_id': self.user_id,
            'upload_date': self.upload_date.isoformat()
        }

class Prediction:
    """Prediction model for ML results"""
    
    def __init__(self, dataset_id, model_type, predictions, metrics=None, prediction_id=None):
        self.id = prediction_id
        self.dataset_id = dataset_id
        self.model_type = model_type
        self.predictions = predictions
        self.metrics = metrics
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert prediction to dictionary"""
        return {
            'id': self.id,
            'dataset_id': self.dataset_id,
            'model_type': self.model_type,
            'predictions': self.predictions,
            'metrics': self.metrics,
            'created_at': self.created_at.isoformat()
        }

class MLModel:
    """Machine Learning Model wrapper"""
    
    def __init__(self, model_type='LinearRegression'):
        self.model_type = model_type
        self.model = None
        self.is_trained = False
    
    def train(self, X, y):
        """Train the ML model"""
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler
        
        if self.model_type == 'LinearRegression':
            self.model = LinearRegression()
        
        # Scale features for better performance
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict(self, X):
        """Make predictions using trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def get_metrics(self, X, y):
        """Calculate model performance metrics"""
        if not self.is_trained:
            raise ValueError("Model must be trained before calculating metrics")
        
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
        
        predictions = self.predict(X)
        
        metrics = {
            'mean_squared_error': mean_squared_error(y, predictions),
            'r2_score': r2_score(y, predictions),
            'mean_absolute_error': mean_absolute_error(y, predictions)
        }
        
        return metrics
