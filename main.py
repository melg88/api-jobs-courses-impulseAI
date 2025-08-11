"""
Aplicação principal da API de Web Scraping
Integra todos os módulos (courses, jobs) e configura a aplicação Flask
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Importar blueprints dos módulos
from courses.controllers import courses_bp
from jobs.controllers import jobs_bp

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.getenv('API_SECRET_KEY', 'your-super-secret-key-change-this-in-production')
    app.config['JSON_SORT_KEYS'] = False
    
    # CORS
    CORS(app)
    
    # Rate Limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Registrar blueprints
    app.register_blueprint(courses_bp)
    app.register_blueprint(jobs_bp)
    
    # Health check global
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check global da API"""
        try:
            # Verificar saúde dos módulos
            from courses.services import CourseService
            from jobs.services import JobService
            
            course_service = CourseService()
            job_service = JobService()
            
            course_health = course_service.health_check()
            job_health = job_service.health_check()
            
            # Determinar status geral
            overall_status = "healthy"
            if course_health['status'] == "unhealthy" or job_health['status'] == "unhealthy":
                overall_status = "degraded"
            
            return jsonify({
                'status': overall_status,
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'uptime': 'N/A',  # Implementar se necessário
                'modules': {
                    'courses': course_health,
                    'jobs': job_health
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Erro no health check: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }), 500
    
    # Endpoint raiz
    @app.route('/', methods=['GET'])
    def root():
        """Endpoint raiz com informações da API"""
        return jsonify({
            'name': 'API de Web Scraping - Vagas e Cursos',
            'version': '1.0.0',
            'description': 'API para scraping de vagas de emprego e cursos online',
            'endpoints': {
                'health': '/health',
                'courses': {
                    'search': 'POST /api/v1/courses',
                    'details': 'GET /api/v1/courses/{course_id}',
                    'health': 'GET /api/v1/courses/health'
                },
                'jobs': {
                    'search': 'POST /api/v1/jobs',
                    'details': 'GET /api/v1/jobs/{job_id}',
                    'health': 'GET /api/v1/jobs/health'
                }
            },
            'documentation': '/docs',
            'timestamp': datetime.now().isoformat()
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'not_found',
            'message': 'Endpoint não encontrado',
            'details': {'path': request.path}
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'method_not_allowed',
            'message': 'Método HTTP não permitido',
            'details': {'method': request.method, 'path': request.path}
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Erro interno: {str(error)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro interno do servidor'
        }), 500
    
    # Rate limit error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'rate_limit_exceeded',
            'message': 'Limite de requisições excedido',
            'details': {
                'retry_after': e.retry_after,
                'limit': e.description
            }
        }), 429
    
    return app

if __name__ == '__main__':
    # Criar diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    
    # Criar aplicação
    app = create_app()
    
    # Configurar host e porta
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Iniciando aplicação na porta {port}")
    logger.info(f"Modo debug: {debug}")
    
    # Executar aplicação
    app.run(host=host, port=port, debug=debug)
