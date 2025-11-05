from datetime import datetime
from src.models.user import db

class AuditLog(db.Model):
    """
    Modelo para registro de logs de auditoria.
    Registra todas as operações realizadas no sistema DHCP.
    """
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    username = db.Column(db.String(120), nullable=False)
    action = db.Column(db.String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    resource_type = db.Column(db.String(50), nullable=False)  # HOST, USER, CONFIG
    resource_name = db.Column(db.String(255), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON string com detalhes da operação
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 ou IPv6
    status = db.Column(db.String(20), nullable=False, default='SUCCESS')  # SUCCESS, FAILURE, ERROR
    error_message = db.Column(db.Text, nullable=True)
    
    # Relacionamento com User
    user = db.relationship('User', backref='audit_logs', lazy=True)
    
    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action} {self.resource_type} by {self.username}>'
    
    def to_dict(self):
        """Converte o log para dicionário."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_name': self.resource_name,
            'details': self.details,
            'ip_address': self.ip_address,
            'status': self.status,
            'error_message': self.error_message
        }
    
    @staticmethod
    def create_log(username, action, resource_type, resource_name=None, 
                   details=None, ip_address=None, status='SUCCESS', 
                   error_message=None, user_id=None):
        """
        Método estático para criar um novo log de auditoria.
        
        Args:
            username: Nome do usuário que realizou a ação
            action: Tipo de ação (CREATE, UPDATE, DELETE, LOGIN, LOGOUT)
            resource_type: Tipo de recurso (HOST, USER, CONFIG)
            resource_name: Nome do recurso afetado
            details: Detalhes adicionais em formato JSON string
            ip_address: Endereço IP do cliente
            status: Status da operação (SUCCESS, FAILURE, ERROR)
            error_message: Mensagem de erro, se houver
            user_id: ID do usuário no banco de dados
        
        Returns:
            AuditLog: Objeto de log criado
        """
        log = AuditLog(
            username=username,
            action=action,
            resource_type=resource_type,
            resource_name=resource_name,
            details=details,
            ip_address=ip_address,
            status=status,
            error_message=error_message,
            user_id=user_id
        )
        db.session.add(log)
        db.session.commit()
        return log
