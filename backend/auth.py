"""
Garuda Analytics Dashboard - Authentication Module
Handles JWT token generation and validation
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app

class AuthManager:
    """Authentication manager for JWT tokens"""
    
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.algorithm = 'HS256'
    
    def generate_token(self, username, expires_in_hours=24):
        """Generate JWT token for user"""
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return token
    
    def verify_token(self, token):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def token_required(self, f):
        """Decorator to require JWT token for endpoints"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Check token in Authorization header
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1]  # Bearer token
                except IndexError:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid token format. Use: Bearer <token>'
                    }), 401
            
            if not token:
                return jsonify({
                    'success': False,
                    'message': 'Token is missing. Please provide a valid token.'
                }), 401
            
            # Verify token
            payload = self.verify_token(token)
            if not payload:
                return jsonify({
                    'success': False,
                    'message': 'Token is invalid or expired.'
                }), 401
            
            # Add user info to request context
            request.current_user = payload['username']
            
            return f(*args, **kwargs)
        
        return decorated_function

# Initialize AuthManager with secret key
def get_auth_manager():
    """Get AuthManager instance"""
    secret_key = current_app.config.get('SECRET_KEY', 'garuda_analytics_secret_key')
    return AuthManager(secret_key)

# Example usage for authentication
class UserAuth:
    """User authentication utilities"""
    
    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticate user credentials
        In production, this should check against a database with hashed passwords
        """
        # Simple authentication for demo purposes
        # In production, use proper password hashing and database lookup
        valid_users = {
            'admin': 'admin123',
            'user': 'user123',
            'demo': 'demo123'
        }
        
        if username in valid_users and valid_users[username] == password:
            return True
        return False
    
    @staticmethod
    def create_user_session(username):
        """Create user session data"""
        return {
            'username': username,
            'login_time': datetime.utcnow().isoformat(),
            'session_id': f"session_{username}_{int(datetime.utcnow().timestamp())}"
        }
