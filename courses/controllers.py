"""
Controllers para o módulo de cursos
Responsável por gerenciar as requisições HTTP relacionadas a cursos
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging
from .services import CourseService
from .models import CourseSearchRequest, CourseDetailRequest

logger = logging.getLogger(__name__)

# Blueprint para rotas de cursos
courses_bp = Blueprint('courses', __name__, url_prefix='/api/v1/courses')

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

@courses_bp.route('', methods=['POST'])
@require_api_key
def search_courses():
    """
    Endpoint para buscar cursos
    POST /api/v1/courses
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
        search_request = CourseSearchRequest(
            query=data.get('query'),
            platform=data.get('platform', 'all'),
            limit=data.get('limit', 10),
            level=data.get('level'),
            language=data.get('language'),
            price_range=data.get('price_range', 'all')
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
        course_service = CourseService()
        result = course_service.search_courses(search_request)
        
        return jsonify({
            'success': True,
            'courses': result['courses'],
            'total': result['total'],
            'query': search_request.query,
            'platform': search_request.platform,
            'timestamp': result['timestamp']
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar cursos: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro interno do servidor',
            'details': {'error': str(e)}
        }), 500

@courses_bp.route('/<course_id>', methods=['GET'])
@require_api_key
def get_course_details(course_id):
    """
    Endpoint para obter detalhes de um curso específico
    GET /api/v1/courses/{course_id}
    """
    try:
        # Validar course_id
        if not course_id:
            return jsonify({
                'error': 'validation_error',
                'message': 'ID do curso é obrigatório',
                'details': {'field': 'course_id', 'constraint': 'required'}
            }), 400
        
        # Criar objeto de requisição
        detail_request = CourseDetailRequest(course_id=course_id)
        
        # Executar busca de detalhes
        course_service = CourseService()
        course_details = course_service.get_course_details(detail_request)
        
        if not course_details:
            return jsonify({
                'error': 'not_found',
                'message': 'Curso não encontrado',
                'details': {'course_id': course_id}
            }), 404
        
        return jsonify(course_details), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do curso {course_id}: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro interno do servidor',
            'details': {'error': str(e)}
        }), 500

@courses_bp.route('/health', methods=['GET'])
def courses_health():
    """
    Health check para o módulo de cursos
    GET /api/v1/courses/health
    """
    try:
        course_service = CourseService()
        health_status = course_service.health_check()
        
        return jsonify({
            'status': 'healthy',
            'module': 'courses',
            'timestamp': health_status['timestamp'],
            'message': 'Módulo de cursos funcionando normalmente'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no health check de cursos: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'module': 'courses',
            'error': str(e)
        }), 500
