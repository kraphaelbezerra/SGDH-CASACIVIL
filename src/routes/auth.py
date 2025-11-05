from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from src.models.user import User, db
from src.utils.audit import log_user_login, log_user_logout, log_action

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra um novo usuário."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'message': 'Dados JSON são obrigatórios',
                'success': False
            }), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validações básicas
        if not all([username, email, password]):
            return jsonify({
                'message': 'Todos os campos são obrigatórios',
                'success': False
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'message': 'A senha deve ter pelo menos 6 caracteres',
                'success': False
            }), 400
        
        # Verificar se o usuário já existe
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                return jsonify({
                    'message': 'Nome de usuário já existe',
                    'success': False
                }), 400
            else:
                return jsonify({
                    'message': 'Email já está cadastrado',
                    'success': False
                }), 400
        
        # Criar novo usuário
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário registrado com sucesso!',
            'success': True,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': f'Erro interno do servidor: {str(e)}',
            'success': False
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Realiza o login do usuário."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'message': 'Dados JSON são obrigatórios',
                'success': False
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        remember = data.get('remember', False)
        
        if not all([username, password]):
            return jsonify({
                'message': 'Nome de usuário e senha são obrigatórios',
                'success': False
            }), 400
        
        # Buscar usuário por username ou email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            # Registrar tentativa de login falhada
            log_user_login(username, success=False)
            return jsonify({
                'message': 'Credenciais inválidas',
                'success': False
            }), 401
        
        if not user.is_active:
            return jsonify({
                'message': 'Conta desativada',
                'success': False
            }), 401
        
        # Fazer login do usuário
        login_user(user, remember=remember)
        
        # Registrar login bem-sucedido
        log_user_login(user.username, success=True)
        
        return jsonify({
            'message': 'Login realizado com sucesso!',
            'success': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'message': f'Erro interno do servidor: {str(e)}',
            'success': False
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Realiza o logout do usuário."""
    try:
        username = current_user.username
        logout_user()
        
        # Registrar logout
        log_user_logout(username)
        
        return jsonify({
            'message': 'Logout realizado com sucesso!',
            'success': True
        })
    except Exception as e:
        return jsonify({
            'message': f'Erro interno do servidor: {str(e)}',
            'success': False
        }), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Retorna informações do usuário logado."""
    try:
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        })
    except Exception as e:
        return jsonify({
            'message': f'Erro interno do servidor: {str(e)}',
            'success': False
        }), 500

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Verifica se o usuário está autenticado."""
    try:
        if current_user.is_authenticated:
            return jsonify({
                'authenticated': True,
                'user': current_user.to_dict()
            })
        else:
            return jsonify({
                'authenticated': False
            })
    except Exception as e:
        return jsonify({
            'message': f'Erro interno do servidor: {str(e)}',
            'success': False
        }), 500
