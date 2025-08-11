#!/usr/bin/env python3
"""
Script para servir a documentação Swagger da API
Permite visualizar a documentação interativa em http://localhost:5000/docs
"""

import os
import yaml
from flask import Flask, render_template_string, send_from_directory, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Template HTML para a documentação Swagger
SWAGGER_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API de Web Scraping - Documentação Swagger</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin:0;
            background: #fafafa;
        }
        .swagger-ui .topbar {
            background-color: #2c3e50;
        }
        .swagger-ui .topbar .download-url-wrapper .select-label {
            color: #fff;
        }
        .swagger-ui .topbar .download-url-wrapper input[type=text] {
            border: 2px solid #34495e;
        }
        .swagger-ui .info .title {
            color: #2c3e50;
        }
        .swagger-ui .scheme-container {
            background: #ecf0f1;
            margin: 0 0 20px;
            padding: 20px 0;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/api-docs/openapi.yaml',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                validatorUrl: null,
                tryItOutEnabled: true,
                requestInterceptor: function(request) {
                    // Adicionar API key automaticamente para testes
                    if (!request.headers['X-API-Key']) {
                        request.headers['X-API-Key'] = 'api-key-1-change-in-production';
                    }
                    return request;
                },
                responseInterceptor: function(response) {
                    console.log('Response:', response);
                    return response;
                }
            });
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página inicial com links para a documentação"""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API de Web Scraping - Vagas e Cursos</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }
            .feature {
                background: #ecf0f1;
                padding: 20px;
                margin: 15px 0;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                margin: 10px 5px;
                background-color: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background-color 0.3s;
            }
            .btn:hover {
                background-color: #2980b9;
            }
            .btn-secondary {
                background-color: #95a5a6;
            }
            .btn-secondary:hover {
                background-color: #7f8c8d;
            }
            .endpoints {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .endpoint {
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 3px;
                border-left: 3px solid #27ae60;
            }
            .method {
                font-weight: bold;
                color: #27ae60;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 API de Web Scraping - Vagas e Cursos</h1>
            
            <div class="feature">
                <h3>📚 Funcionalidades Principais</h3>
                <ul>
                    <li><strong>Busca de Vagas:</strong> Scraping de vagas no LinkedIn</li>
                    <li><strong>Busca de Cursos:</strong> Scraping de cursos em múltiplas plataformas (Udemy, Coursera, edX)</li>
                    <li><strong>Autenticação:</strong> Sistema de API keys para controle de acesso</li>
                    <li><strong>Rate Limiting:</strong> Proteção contra abuso da API</li>
                </ul>
            </div>

            <div class="feature">
                <h3>🎯 Implementação Avançada do Udemy</h3>
                <ul>
                    <li><strong>Cloudscraper:</strong> Contorna proteções anti-bot da Udemy</li>
                    <li><strong>Pandas:</strong> Processamento e ordenação de dados</li>
                    <li><strong>Múltiplas Páginas:</strong> Busca automática em várias páginas</li>
                </ul>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="/docs" class="btn">📖 Ver Documentação Swagger</a>
                <a href="/health" class="btn btn-secondary">🔍 Health Check</a>
            </div>

            <div class="endpoints">
                <h3>🔗 Endpoints Principais</h3>
                
                <div class="endpoint">
                    <span class="method">GET</span> /health - Verificar status da API
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> /api/v1/jobs - Buscar vagas de emprego
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> /api/v1/jobs/{job_id} - Detalhes de uma vaga
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> /api/v1/courses - Buscar cursos online
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> /api/v1/courses/{course_id} - Detalhes de um curso
                </div>
            </div>

            <div class="feature">
                <h3>🔑 Autenticação</h3>
                <p>Todas as requisições devem incluir o header <code>X-API-Key</code> com uma das chaves válidas:</p>
                <ul>
                    <li><code>api-key-1-change-in-production</code></li>
                    <li><code>api-key-2-change-in-production</code></li>
                </ul>
            </div>

            <div class="feature">
                <h3>⚡ Rate Limiting</h3>
                <ul>
                    <li><strong>Vagas:</strong> 10 requisições por minuto</li>
                    <li><strong>Cursos:</strong> 10 requisições por minuto</li>
                    <li><strong>Detalhes:</strong> 20 requisições por minuto</li>
                    <li><strong>Global:</strong> 200 requisições por dia, 50 por hora</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/docs')
def docs():
    """Página da documentação Swagger"""
    return render_template_string(SWAGGER_TEMPLATE)

@app.route('/api-docs/openapi.yaml')
def openapi_spec():
    """Servir a especificação OpenAPI"""
    try:
        with open('openapi.yaml', 'r', encoding='utf-8') as file:
            spec = yaml.safe_load(file)
        return jsonify(spec)
    except FileNotFoundError:
        return jsonify({"error": "Arquivo openapi.yaml não encontrado"}), 404

@app.route('/health')
def health():
    """Health check da API de documentação"""
    return jsonify({
        "status": "healthy",
        "service": "documentation-server",
        "version": "1.0.0",
        "message": "Servidor de documentação funcionando normalmente"
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor de documentação...")
    print("📖 Documentação disponível em: http://localhost:5000/docs")
    print("🏠 Página inicial: http://localhost:5000")
    print("🔍 Health check: http://localhost:5000/health")
    print("\nPressione Ctrl+C para parar o servidor")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
