from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import logging
from datetime import datetime
import json
from functools import wraps
import hashlib
import hmac
import time

# Importando os módulos de scraping
from scrapers.job_scraper import JobScraper
from scrapers.course_scraper import CourseScraper

app = Flask(__name__)
CORS(app)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configurações da API
API_SECRET_KEY = os.environ.get('API_SECRET_KEY', 'your-secret-key-change-in-production')
API_KEYS = {
    'client1': 'api-key-1-change-in-production',
    'client2': 'api-key-2-change-in-production'
}

def require_api_key(f):
    """Decorator para verificar API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key é obrigatória'}), 401
        
        if api_key not in API_KEYS.values():
            return jsonify({'error': 'API key inválida'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def verify_signature(f):
    """Decorator para verificar assinatura HMAC (opcional para maior segurança)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get('X-Signature')
        timestamp = request.headers.get('X-Timestamp')
        
        if signature and timestamp:
            # Verificar se o timestamp não é muito antigo (5 minutos)
            if time.time() - float(timestamp) > 300:
                return jsonify({'error': 'Timestamp expirado'}), 401
            
            # Verificar assinatura
            expected_signature = hmac.new(
                API_SECRET_KEY.encode(),
                request.get_data(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return jsonify({'error': 'Assinatura inválida'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/v1/jobs', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key
def search_jobs():
    """Endpoint para buscar vagas de emprego"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        query = data.get('query')
        location = data.get('location', '')
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({'error': 'Parâmetro "query" é obrigatório'}), 400
        
        # Inicializar scraper de vagas
        job_scraper = JobScraper()
        
        # Realizar busca
        jobs = job_scraper.search_jobs(query, location, limit)
        
        return jsonify({
            'success': True,
            'data': jobs,
            'count': len(jobs),
            'query': query,
            'location': location,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar vagas: {str(e)}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@app.route('/api/v1/courses', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key
def search_courses():
    """Endpoint para buscar cursos"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        query = data.get('query')
        platform = data.get('platform', 'all')  # udemy, coursera, etc.
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({'error': 'Parâmetro "query" é obrigatório'}), 400
        
        # Inicializar scraper de cursos
        course_scraper = CourseScraper()
        
        # Realizar busca
        courses = course_scraper.search_courses(query, platform, limit)
        
        return jsonify({
            'success': True,
            'data': courses,
            'count': len(courses),
            'query': query,
            'platform': platform,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar cursos: {str(e)}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@app.route('/api/v1/jobs/<job_id>', methods=['GET'])
@limiter.limit("20 per minute")
@require_api_key
def get_job_details(job_id):
    """Endpoint para obter detalhes de uma vaga específica"""
    try:
        job_scraper = JobScraper()
        job_details = job_scraper.get_job_details(job_id)
        
        if not job_details:
            return jsonify({'error': 'Vaga não encontrada'}), 404
        
        return jsonify({
            'success': True,
            'data': job_details,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter detalhes da vaga: {str(e)}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@app.route('/api/v1/courses/<course_id>', methods=['GET'])
@limiter.limit("20 per minute")
@require_api_key
def get_course_details(course_id):
    """Endpoint para obter detalhes de um curso específico"""
    try:
        course_scraper = CourseScraper()
        course_details = course_scraper.get_course_details(course_id)
        
        if not course_details:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': course_details,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do curso: {str(e)}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handler para rate limit excedido"""
    return jsonify({
        'error': 'Rate limit excedido',
        'message': 'Muitas requisições. Tente novamente em alguns minutos.'
    }), 429

@app.errorhandler(404)
def not_found(e):
    """Handler para rotas não encontradas"""
    return jsonify({
        'error': 'Endpoint não encontrado',
        'message': 'Verifique a URL e o método HTTP'
    }), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
