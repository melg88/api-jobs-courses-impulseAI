# Guia do Consumidor da API de Web Scraping

Este guia explica como consumir a API de Web Scraping para vagas e cursos.

## 🔑 Autenticação

### API Key
Todas as requisições devem incluir o header `X-API-Key`:

```http
X-API-Key: sua-api-key
```

### API Keys Disponíveis
- `api-key-1-change-in-production`
- `api-key-2-change-in-production`

### Exemplo de Requisição Autenticada
```bash
curl -H "X-API-Key: api-key-1-change-in-production" \
     -H "Content-Type: application/json" \
     https://sua-api.com/health
```

## 📚 Endpoints

### 1. Health Check
Verifica se a API está funcionando.

```http
GET /health
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

### 2. Buscar Vagas
Busca vagas de emprego no LinkedIn.

```http
POST /api/v1/jobs
Content-Type: application/json
X-API-Key: sua-api-key

{
  "query": "Python Developer",
  "location": "São Paulo",
  "limit": 10
}
```

**Parâmetros:**
- `query` (obrigatório): Termo de busca
- `location` (opcional): Localização da vaga
- `limit` (opcional): Número máximo de resultados (padrão: 10)

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": "job_123",
      "title": "Python Developer",
      "company": "Tech Company",
      "location": "São Paulo, SP",
      "description": "Descrição da vaga...",
      "posted_date": "2024-01-01",
      "applicants": "50+ candidatos",
      "url": "https://linkedin.com/jobs/view/123",
      "source": "linkedin"
    }
  ],
  "count": 1,
  "query": "Python Developer",
  "location": "São Paulo",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 3. Buscar Cursos
Busca cursos em múltiplas plataformas.

```http
POST /api/v1/courses
Content-Type: application/json
X-API-Key: sua-api-key

{
  "query": "Machine Learning",
  "platform": "udemy",
  "limit": 10
}
```

**Parâmetros:**
- `query` (obrigatório): Termo de busca
- `platform` (opcional): Plataforma específica (`udemy`, `coursera`, `edx`, `all`)
- `limit` (opcional): Número máximo de resultados (padrão: 10)

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": "udemy_123",
      "title": "Machine Learning A-Z",
      "instructor": "John Doe",
      "rating": 4.5,
      "students_count": 100000,
      "price": "R$ 29,90",
      "original_price": "R$ 199,90",
      "language": "Português",
      "duration": "44 horas",
      "level": "Intermediário",
      "url": "https://udemy.com/course/machine-learning",
      "image_url": "https://img-c.udemycdn.com/course/480x270/123.jpg",
      "description": "Aprenda Machine Learning do zero...",
      "source": "udemy"
    }
  ],
  "count": 1,
  "query": "Machine Learning",
  "platform": "udemy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 4. Detalhes de Vaga
Obtém detalhes completos de uma vaga específica.

```http
GET /api/v1/jobs/{job_id}
X-API-Key: sua-api-key
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": "job_123",
    "title": "Python Developer",
    "company": "Tech Company",
    "location": "São Paulo, SP",
    "description": "Descrição detalhada da vaga...",
    "requirements": ["Python", "Django", "PostgreSQL"],
    "benefits": ["Plano de saúde", "Vale refeição"],
    "salary_range": "R$ 5.000 - R$ 8.000",
    "posted_date": "2024-01-01",
    "url": "https://linkedin.com/jobs/view/123",
    "source": "linkedin"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### 5. Detalhes de Curso
Obtém detalhes completos de um curso específico.

```http
GET /api/v1/courses/{course_id}
X-API-Key: sua-api-key
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": "udemy_123",
    "title": "Machine Learning A-Z",
    "instructor": "John Doe",
    "rating": 4.5,
    "students_count": 100000,
    "price": "R$ 29,90",
    "original_price": "R$ 199,90",
    "language": "Português",
    "duration": "44 horas",
    "level": "Intermediário",
    "url": "https://udemy.com/course/machine-learning",
    "image_url": "https://img-c.udemycdn.com/course/480x270/123.jpg",
    "description": "Descrição completa do curso...",
    "curriculum": ["Seção 1: Introdução", "Seção 2: Conceitos Básicos"],
    "requirements": ["Conhecimento básico de Python"],
    "objectives": ["Entender Machine Learning", "Implementar algoritmos"],
    "source": "udemy"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🔒 Rate Limiting

A API implementa rate limiting para proteger contra abuso:

- **Vagas**: 10 requisições por minuto
- **Cursos**: 10 requisições por minuto
- **Detalhes**: 20 requisições por minuto
- **Global**: 200 requisições por dia, 50 por hora

**Resposta quando limite excedido:**
```json
{
  "error": "Rate limit excedido",
  "message": "Muitas requisições. Tente novamente em alguns minutos."
}
```

## 📝 Exemplos de Implementação

### JavaScript/Node.js
```javascript
const axios = require('axios');

class APIClient {
    constructor(baseURL, apiKey) {
        this.baseURL = baseURL;
        this.apiKey = apiKey;
        this.client = axios.create({
            baseURL,
            headers: {
                'X-API-Key': apiKey,
                'Content-Type': 'application/json'
            }
        });
    }

    async searchJobs(query, location = '', limit = 10) {
        try {
            const response = await this.client.post('/api/v1/jobs', {
                query,
                location,
                limit
            });
            return response.data;
        } catch (error) {
            throw new Error(`Erro na busca de vagas: ${error.response?.data?.error || error.message}`);
        }
    }

    async searchCourses(query, platform = 'all', limit = 10) {
        try {
            const response = await this.client.post('/api/v1/courses', {
                query,
                platform,
                limit
            });
            return response.data;
        } catch (error) {
            throw new Error(`Erro na busca de cursos: ${error.response?.data?.error || error.message}`);
        }
    }

    async getJobDetails(jobId) {
        try {
            const response = await this.client.get(`/api/v1/jobs/${jobId}`);
            return response.data;
        } catch (error) {
            throw new Error(`Erro ao obter detalhes da vaga: ${error.response?.data?.error || error.message}`);
        }
    }

    async getCourseDetails(courseId) {
        try {
            const response = await this.client.get(`/api/v1/courses/${courseId}`);
            return response.data;
        } catch (error) {
            throw new Error(`Erro ao obter detalhes do curso: ${error.response?.data?.error || error.message}`);
        }
    }
}

// Uso
const client = new APIClient('https://sua-api.com', 'api-key-1-change-in-production');

// Buscar vagas
client.searchJobs('Python Developer', 'São Paulo', 5)
    .then(data => console.log('Vagas:', data))
    .catch(error => console.error('Erro:', error));

// Buscar cursos
client.searchCourses('Machine Learning', 'udemy', 5)
    .then(data => console.log('Cursos:', data))
    .catch(error => console.error('Erro:', error));
```

### Python
```python
import requests
from typing import Dict, Any, Optional

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Faz uma requisição para a API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=self.headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                error_data = e.response.json()
                raise Exception(f"Erro da API: {error_data.get('error', str(e))}")
            else:
                raise Exception(f"Erro de conexão: {str(e)}")
    
    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> Dict[str, Any]:
        """Busca vagas de emprego"""
        data = {
            'query': query,
            'location': location,
            'limit': limit
        }
        return self._make_request('POST', '/api/v1/jobs', data)
    
    def search_courses(self, query: str, platform: str = "all", limit: int = 10) -> Dict[str, Any]:
        """Busca cursos online"""
        data = {
            'query': query,
            'platform': platform,
            'limit': limit
        }
        return self._make_request('POST', '/api/v1/courses', data)
    
    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """Obtém detalhes de uma vaga"""
        return self._make_request('GET', f'/api/v1/jobs/{job_id}')
    
    def get_course_details(self, course_id: str) -> Dict[str, Any]:
        """Obtém detalhes de um curso"""
        return self._make_request('GET', f'/api/v1/courses/{course_id}')
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica a saúde da API"""
        return self._make_request('GET', '/health')

# Uso
client = APIClient('https://sua-api.com', 'api-key-1-change-in-production')

try:
    # Verificar saúde
    health = client.health_check()
    print(f"API Status: {health['status']}")
    
    # Buscar vagas
    jobs = client.search_jobs('Python Developer', 'São Paulo', 5)
    print(f"Encontradas {jobs['count']} vagas")
    
    # Buscar cursos
    courses = client.search_courses('Machine Learning', 'udemy', 5)
    print(f"Encontrados {courses['count']} cursos")
    
except Exception as e:
    print(f"Erro: {e}")
```

### PHP
```php
<?php

class APIClient {
    private $baseURL;
    private $apiKey;
    private $headers;
    
    public function __construct($baseURL, $apiKey) {
        $this->baseURL = rtrim($baseURL, '/');
        $this->apiKey = $apiKey;
        $this->headers = [
            'X-API-Key: ' . $apiKey,
            'Content-Type: application/json'
        ];
    }
    
    private function makeRequest($method, $endpoint, $data = null) {
        $url = $this->baseURL . $endpoint;
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $this->headers);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            if ($data) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
            }
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode >= 400) {
            $errorData = json_decode($response, true);
            throw new Exception('Erro da API: ' . ($errorData['error'] ?? 'Erro desconhecido'));
        }
        
        return json_decode($response, true);
    }
    
    public function searchJobs($query, $location = '', $limit = 10) {
        $data = [
            'query' => $query,
            'location' => $location,
            'limit' => $limit
        ];
        return $this->makeRequest('POST', '/api/v1/jobs', $data);
    }
    
    public function searchCourses($query, $platform = 'all', $limit = 10) {
        $data = [
            'query' => $query,
            'platform' => $platform,
            'limit' => $limit
        ];
        return $this->makeRequest('POST', '/api/v1/courses', $data);
    }
    
    public function getJobDetails($jobId) {
        return $this->makeRequest('GET', '/api/v1/jobs/' . $jobId);
    }
    
    public function getCourseDetails($courseId) {
        return $this->makeRequest('GET', '/api/v1/courses/' . $courseId);
    }
    
    public function healthCheck() {
        return $this->makeRequest('GET', '/health');
    }
}

// Uso
$client = new APIClient('https://sua-api.com', 'api-key-1-change-in-production');

try {
    // Verificar saúde
    $health = $client->healthCheck();
    echo "API Status: " . $health['status'] . "\n";
    
    // Buscar vagas
    $jobs = $client->searchJobs('Python Developer', 'São Paulo', 5);
    echo "Encontradas " . $jobs['count'] . " vagas\n";
    
    // Buscar cursos
    $courses = $client->searchCourses('Machine Learning', 'udemy', 5);
    echo "Encontrados " . $courses['count'] . " cursos\n";
    
} catch (Exception $e) {
    echo "Erro: " . $e->getMessage() . "\n";
}

?>
```

## 🚨 Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 400 | Dados inválidos ou parâmetros obrigatórios ausentes |
| 401 | API key inválida ou ausente |
| 404 | Recurso não encontrado |
| 429 | Rate limit excedido |
| 500 | Erro interno do servidor |

## 📊 Monitoramento

### Health Check
Use o endpoint `/health` para monitorar a saúde da API:

```bash
curl https://sua-api.com/health
```

### Logs
Em caso de problemas, verifique os logs da API:

```bash
docker-compose logs -f api
```

## 🔧 Configuração de Produção

### URLs de Produção
Substitua `https://sua-api.com` pela URL real da sua API em produção.

### Certificados SSL
Para produção, use certificados SSL válidos em vez dos auto-assinados.

### Rate Limiting
Ajuste os limites de rate limiting conforme necessário no arquivo `app.py`.

## 📞 Suporte

Para suporte técnico:
- Email: seu-email@exemplo.com
- Issues: [GitHub Issues](https://github.com/seu-usuario/api-jobs-courses-impulseAI/issues)
- Documentação: [README.md](README.md)
