"""
Controllers para o módulo de vagas
Responsável por gerenciar as requisições HTTP relacionadas a vagas de emprego
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging
from .services import JobService
from .models import JobSearchRequest, JobDetailRequest

logger = logging.getLogger(__name__)

# Blueprint para rotas de vagas
jobs_bp = Blueprint('jobs', __name__, url_prefix='/api/v1/jobs')

def require_api_key(f):
    """Decorator para verificar API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'error': 'authentication_error',
                'message': 'API key é obrigatória',
                'details': {'field': 'X-API-Key', 'constraint': 'required'}
            }), 401
        
        # Aqui você pode adicionar validação da API key
        valid_keys = ['api-key-1-change-in-production', 'api-key-2-change-in-production']
        if api_key not in valid_keys:
            return jsonify({
                'error': 'authentication_error',
                'message': 'API key inválida',
                'details': {'field': 'X-API-Key', 'constraint': 'invalid'}
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

@jobs_bp.route('', methods=['POST'])
@require_api_key
def search_jobs():
    """
    Endpoint para buscar vagas de emprego
    POST /api/v1/jobs
    """
    try:
        # Validar dados de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'validation_error',
                'message': 'Dados JSON são obrigatórios',
                'details': {'field': 'body', 'constraint': 'required'}
            }), 400
        
        # Criar objeto de requisição
        search_request = JobSearchRequest(
            query=data.get('query'),
            location=data.get('location'),
            limit=data.get('limit', 10),
            experience_level=data.get('experience_level'),
            job_type=data.get('job_type')
        )
        
        # Validar requisição
        validation_error = search_request.validate()
        if validation_error:
            return jsonify({
                'error': 'validation_error',
                'message': validation_error,
                'details': {'field': 'query', 'constraint': 'required'}
            }), 400
        
        # Executar busca
        job_service = JobService()
        result = job_service.search_jobs(search_request)
        
        return jsonify({
            'success': True,
            'jobs': result['jobs'],
            'total': result['total'],
            'query': search_request.query,
            'timestamp': result['timestamp']
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar vagas: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro interno do servidor',
            'details': {'error': str(e)}
        }), 500

@jobs_bp.route('/<job_id>', methods=['GET'])
@require_api_key
def get_job_details(job_id):
    """
    Endpoint para obter detalhes de uma vaga específica
    GET /api/v1/jobs/{job_id}
    """
    try:
        # Validar job_id
        if not job_id:
            return jsonify({
                'error': 'validation_error',
                'message': 'ID da vaga é obrigatório',
                'details': {'field': 'job_id', 'constraint': 'required'}
            }), 400
        
        # Criar objeto de requisição
        detail_request = JobDetailRequest(job_id=job_id)
        
        # Executar busca de detalhes
        job_service = JobService()
        job_details = job_service.get_job_details(detail_request)
        
        if not job_details:
            return jsonify({
                'error': 'not_found',
                'message': 'Vaga não encontrada',
                'details': {'job_id': job_id}
            }), 404
        
        return jsonify(job_details), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter detalhes da vaga {job_id}: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro interno do servidor',
            'details': {'error': str(e)}
        }), 500

@jobs_bp.route('/health', methods=['GET'])
def jobs_health():
    """
    Health check para o módulo de vagas
    GET /api/v1/jobs/health
    """
    try:
        job_service = JobService()
        health_status = job_service.health_check()
        
        return jsonify({
            'status': 'healthy',
            'module': 'jobs',
            'timestamp': health_status['timestamp'],
            'message': 'Módulo de vagas funcionando normalmente'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no health check de vagas: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'module': 'jobs',
            'error': str(e)
        }), 500
