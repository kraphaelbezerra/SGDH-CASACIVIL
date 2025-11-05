from flask import Blueprint, request, jsonify
from flask_login import login_required
from src.models.audit_log import AuditLog
from datetime import datetime, timedelta

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/logs', methods=['GET'])
@login_required
def get_logs():
    """
    Retorna logs de auditoria com filtros opcionais.
    
    Query parameters:
        - action: Filtrar por tipo de ação (CREATE, UPDATE, DELETE, LOGIN, LOGOUT)
        - resource_type: Filtrar por tipo de recurso (HOST, USER, CONFIG)
        - username: Filtrar por nome de usuário
        - status: Filtrar por status (SUCCESS, FAILURE, ERROR)
        - start_date: Data inicial (formato: YYYY-MM-DD)
        - end_date: Data final (formato: YYYY-MM-DD)
        - limit: Número máximo de resultados (padrão: 100)
        - offset: Offset para paginação (padrão: 0)
    """
    try:
        # Obter parâmetros de filtro
        action = request.args.get('action')
        resource_type = request.args.get('resource_type')
        username = request.args.get('username')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # Construir query
        query = AuditLog.query
        
        if action:
            query = query.filter(AuditLog.action == action.upper())
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type.upper())
        
        if username:
            query = query.filter(AuditLog.username.ilike(f'%{username}%'))
        
        if status:
            query = query.filter(AuditLog.status == status.upper())
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(AuditLog.timestamp >= start_dt)
            except ValueError:
                return jsonify({
                    'message': 'Formato de data inicial inválido. Use YYYY-MM-DD',
                    'success': False
                }), 400
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(AuditLog.timestamp < end_dt)
            except ValueError:
                return jsonify({
                    'message': 'Formato de data final inválido. Use YYYY-MM-DD',
                    'success': False
                }), 400
        
        # Ordenar por timestamp decrescente (mais recente primeiro)
        query = query.order_by(AuditLog.timestamp.desc())
        
        # Obter total de registros
        total = query.count()
        
        # Aplicar paginação
        logs = query.limit(limit).offset(offset).all()
        
        # Converter para dicionários
        logs_data = [log.to_dict() for log in logs]
        
        return jsonify({
            'success': True,
            'total': total,
            'limit': limit,
            'offset': offset,
            'logs': logs_data
        })
        
    except Exception as e:
        return jsonify({
            'message': f'Erro ao buscar logs: {str(e)}',
            'success': False
        }), 500

@audit_bp.route('/logs/<int:log_id>', methods=['GET'])
@login_required
def get_log(log_id):
    """Retorna um log específico pelo ID."""
    try:
        log = AuditLog.query.get(log_id)
        
        if not log:
            return jsonify({
                'message': 'Log não encontrado',
                'success': False
            }), 404
        
        return jsonify({
            'success': True,
            'log': log.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'message': f'Erro ao buscar log: {str(e)}',
            'success': False
        }), 500

@audit_bp.route('/logs/stats', methods=['GET'])
@login_required
def get_logs_stats():
    """Retorna estatísticas dos logs de auditoria."""
    try:
        # Total de logs
        total_logs = AuditLog.query.count()
        
        # Logs por ação
        actions_stats = {}
        for action in ['CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT']:
            count = AuditLog.query.filter(AuditLog.action == action).count()
            actions_stats[action] = count
        
        # Logs por tipo de recurso
        resources_stats = {}
        for resource in ['HOST', 'USER', 'CONFIG']:
            count = AuditLog.query.filter(AuditLog.resource_type == resource).count()
            resources_stats[resource] = count
        
        # Logs por status
        status_stats = {}
        for status in ['SUCCESS', 'FAILURE', 'ERROR']:
            count = AuditLog.query.filter(AuditLog.status == status).count()
            status_stats[status] = count
        
        # Logs das últimas 24 horas
        yesterday = datetime.utcnow() - timedelta(days=1)
        logs_24h = AuditLog.query.filter(AuditLog.timestamp >= yesterday).count()
        
        # Logs da última semana
        last_week = datetime.utcnow() - timedelta(days=7)
        logs_week = AuditLog.query.filter(AuditLog.timestamp >= last_week).count()
        
        # Usuários mais ativos
        from sqlalchemy import func
        top_users = AuditLog.query.with_entities(
            AuditLog.username,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.username).order_by(func.count(AuditLog.id).desc()).limit(10).all()
        
        top_users_data = [{'username': user[0], 'count': user[1]} for user in top_users]
        
        return jsonify({
            'success': True,
            'stats': {
                'total_logs': total_logs,
                'logs_24h': logs_24h,
                'logs_week': logs_week,
                'by_action': actions_stats,
                'by_resource': resources_stats,
                'by_status': status_stats,
                'top_users': top_users_data
            }
        })
        
    except Exception as e:
        return jsonify({
            'message': f'Erro ao obter estatísticas: {str(e)}',
            'success': False
        }), 500

@audit_bp.route('/logs/recent', methods=['GET'])
@login_required
def get_recent_logs():
    """Retorna os logs mais recentes (últimas 50 entradas)."""
    try:
        limit = int(request.args.get('limit', 50))
        
        logs = AuditLog.query.order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).all()
        
        logs_data = [log.to_dict() for log in logs]
        
        return jsonify({
            'success': True,
            'logs': logs_data
        })
        
    except Exception as e:
        return jsonify({
            'message': f'Erro ao buscar logs recentes: {str(e)}',
            'success': False
        }), 500
