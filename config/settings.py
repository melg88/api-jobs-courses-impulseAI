"""
Configurações centralizadas da aplicação
"""

import os
from typing import List

class Config:
    """Configuração base"""
    
    # Configurações da API
    API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'your-super-secret-key-change-this-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Configurações de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'
    
    # Configurações de rate limiting
    RATE_LIMIT_DEFAULT = "200 per day"
    RATE_LIMIT_HOURLY = "50 per hour"
    RATE_LIMIT_MINUTE = "10 per minute"
    
    # Configurações de scraping
    SCRAPER_TIMEOUT = 30
    SCRAPER_RETRY_ATTEMPTS = 3
    SCRAPER_DELAY_BETWEEN_REQUESTS = 1  # segundos
    
    # Configurações do LinkedIn
    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')
    
    # API Keys válidas
    VALID_API_KEYS = [
        os.getenv('API_KEY_CLIENT', 'api-key-1-change-in-production')
    ]
    
    # Configurações de plataformas de cursos
    COURSE_PLATFORMS = ['udemy', 'coursera', 'edx']
    COURSE_SEARCH_LIMIT_MAX = 50
    COURSE_SEARCH_LIMIT_DEFAULT = 10
    
    # Configurações de vagas
    JOB_SEARCH_LIMIT_MAX = 50
    JOB_SEARCH_LIMIT_DEFAULT = 10
    
    # Configurações de CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # Configurações de segurança
    SECURITY_HEADERS = {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    FLASK_ENV = 'development'
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # CORS mais permissivo para desenvolvimento
    CORS_ORIGINS = ["*"]

class ProductionConfig(Config):
    """Configuração para produção"""
    FLASK_ENV = 'production'
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Configurações de segurança mais rigorosas
    SECURITY_HEADERS = {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }

class TestingConfig(Config):
    """Configuração para testes"""
    FLASK_ENV = 'testing'
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    
    # Configurações específicas para testes
    SCRAPER_DELAY_BETWEEN_REQUESTS = 0.1
    COURSE_SEARCH_LIMIT_DEFAULT = 5
    JOB_SEARCH_LIMIT_DEFAULT = 5

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> Config:
    """
    Retorna a configuração baseada no ambiente
    
    Args:
        config_name: Nome da configuração (development, production, testing)
        
    Returns:
        Classe de configuração
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])
