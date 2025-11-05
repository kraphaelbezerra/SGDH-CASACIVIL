import json
from functools import wraps
from flask import request
from flask_login import current_user
from src.models.audit_log import AuditLog

def get_client_ip():
    """Obtém o endereço IP do cliente."""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ.get('REMOTE_ADDR', 'unknown')
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def log_action(action, resource_type, resource_name=None, details=None, status='SUCCESS', error_message=None):
    """
    Registra uma ação no log de auditoria.
    
    Args:
        action: Tipo de ação (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, VIEW)
        resource_type: Tipo de recurso (HOST, USER, CONFIG, SYSTEM)
        resource_name: Nome do recurso afetado
        details: Dicionário com detalhes adicionais
        status: Status da operação (SUCCESS, FAILURE, ERROR)
        error_message: Mensagem de erro, se houver
    """
    try:
        # Obter informações do usuário
        if current_user and current_user.is_authenticated:
            username = current_user.username
            user_id = current_user.id
        else:
            username = 'anonymous'
            user_id = None
        
        # Converter detalhes para JSON se for um dicionário
        details_json = None
        if details:
            if isinstance(details, dict):
                details_json = json.dumps(details, ensure_ascii=False)
            else:
                details_json = str(details)
        
        # Obter IP do cliente
        ip_address = get_client_ip()
        
        # Criar log
        AuditLog.create_log(
            username=username,
            action=action,
            resource_type=resource_type,
            resource_name=resource_name,
            details=details_json,
            ip_address=ip_address,
            status=status,
            error_message=error_message,
            user_id=user_id
        )
    except Exception as e:
        # Em caso de erro ao registrar log, apenas imprimir (não deve interromper a operação)
        print(f"Erro ao registrar log de auditoria: {str(e)}")

def audit_log(action, resource_type):
    """
    Decorator para registrar automaticamente ações em rotas.
    
    Usage:
        @audit_log('CREATE', 'HOST')
        def create_host():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resource_name = kwargs.get('host_name') or kwargs.get('hostname') or kwargs.get('id')
            
            try:
                # Executar a função
                result = f(*args, **kwargs)
                
                # Registrar sucesso
                log_action(
                    action=action,
                    resource_type=resource_type,
                    resource_name=str(resource_name) if resource_name else None,
                    status='SUCCESS'
                )
                
                return result
            except Exception as e:
                # Registrar falha
                log_action(
                    action=action,
                    resource_type=resource_type,
                    resource_name=str(resource_name) if resource_name else None,
                    status='ERROR',
                    error_message=str(e)
                )
                raise
        
        return decorated_function
    return decorator

def log_host_create(host_name, mac_address, ip_address, rule_name):
    """Registra criação de host."""
    details = {
        'host_name': host_name,
        'mac_address': mac_address,
        'ip_address': ip_address,
        'rule_name': rule_name
    }
    log_action('CREATE', 'HOST', host_name, details)

def log_host_update(host_name, old_data, new_data):
    """Registra atualização de host."""
    details = {
        'old_data': old_data,
        'new_data': new_data,
        'changes': {}
    }
    
    # Identificar mudanças
    for key in new_data:
        if key in old_data and old_data[key] != new_data[key]:
            details['changes'][key] = {
                'from': old_data[key],
                'to': new_data[key]
            }
    
    log_action('UPDATE', 'HOST', host_name, details)

def log_host_delete(host_name, mac_address, ip_address):
    """Registra exclusão de host."""
    details = {
        'host_name': host_name,
        'mac_address': mac_address,
        'ip_address': ip_address
    }
    log_action('DELETE', 'HOST', host_name, details)

def log_user_login(username, success=True):
    """Registra tentativa de login."""
    log_action(
        'LOGIN',
        'USER',
        username,
        status='SUCCESS' if success else 'FAILURE'
    )

def log_user_logout(username):
    """Registra logout de usuário."""
    log_action('LOGOUT', 'USER', username)

def log_config_change(config_type, details):
    """Registra mudança de configuração."""
    log_action('UPDATE', 'CONFIG', config_type, details)
