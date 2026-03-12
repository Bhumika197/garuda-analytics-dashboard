"""
Garuda Analytics Dashboard - Login Route
Handles user authentication and token generation
"""

from flask import Blueprint, request, jsonify
from auth import UserAuth, get_auth_manager
from datetime import datetime

# Create Blueprint for login routes
login_bp = Blueprint('login', __name__, url_prefix='/auth')

@login_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint
    Accepts username and password, returns JWT token
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Authenticate user
        if not UserAuth.authenticate_user(username, password):
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
        
        # Generate JWT token
        auth_manager = get_auth_manager()
        token = auth_manager.generate_token(username)
        
        # Create user session
        session_data = UserAuth.create_user_session(username)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'username': username,
                'session': session_data
            },
            'expires_in': '24 hours'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500

@login_bp.route('/verify', methods=['POST'])
def verify_token():
    """
    Verify JWT token endpoint
    Checks if token is valid and not expired
    """
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is required'
            }), 400
        
        auth_manager = get_auth_manager()
        payload = auth_manager.verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'message': 'Token is invalid or expired'
            }), 401
        
        return jsonify({
            'success': True,
            'message': 'Token is valid',
            'user': {
                'username': payload['username'],
                'issued_at': payload.get('iat'),
                'expires_at': payload.get('exp')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Token verification error: {str(e)}'
        }), 500

@login_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout endpoint
    In a production system, this would invalidate the token
    """
    try:
        return jsonify({
            'success': True,
            'message': 'Logout successful. Please discard the token.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Logout error: {str(e)}'
        }), 500
