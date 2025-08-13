# API de Web Scraping - Vagas e Cursos

API Flask para web scraping de vagas de emprego (LinkedIn) e cursos online (Udemy, Coursera, edX).

## 🚀 Funcionalidades

- **Busca de Vagas**: Scraping de vagas no LinkedIn
- **Busca de Cursos**: Scraping de cursos em múltiplas plataformas (Udemy, Coursera, edX)
  - **Udemy**: Implementação avançada usando `cloudscraper` para contornar proteções anti-bot
  - **Processamento de Dados**: Uso de `pandas` para ordenação e estruturação dos dados
  - **Múltiplas Páginas**: Busca automática em várias páginas para resultados mais completos
- **Autenticação**: Sistema de API keys para controle de acesso
- **Rate Limiting**: Proteção contra abuso da API
- **Docker**: Containerização completa para deploy
- **HTTPS**: Configuração SSL com Nginx

## 📋 Pré-requisitos

- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento local)
- Chrome/ChromeDriver (para scraping)

### Dependências Especiais
- **cloudscraper**: Para contornar proteções anti-bot da Udemy
- **pandas**: Para processamento e ordenação de dados dos cursos
- **linkedin_scrapper**: Para busca de dados na api do linkedin

## 🛠️ Instalação e Deploy

### Opção 1: Deploy Automático (Recomendado)

#### Configurar CI/CD com GitHub Actions e Railway

1. **Configure os secrets no GitHub:**
   - Vá em `Settings > Secrets and variables > Actions`
   - Adicione: `RAILWAY_TOKEN`, `RAILWAY_PROJECT_ID`

2. **Configure o projeto no Railway:**
   - Crie projeto no [Railway](https://railway.app)
   - Conecte com seu repositório GitHub
   - Configure as variáveis de ambiente

3. **Deploy automático:**
   - Faça push para `main` ou `master`
   - O pipeline executará automaticamente
   - Acesse a URL gerada pelo Railway
   - Para ambiente de desenvolvimento, PR para a branch `feature/api-web-scraping`

📖 **Documentação completa**: [docs/CI_CD_SETUP.md](docs/CI_CD_SETUP.md)

### Opção 2: Deploy Local

#### 1. Clone o repositório
```bash
git clone <https://github.com/melg88/api-jobs-courses-impulseAI>
cd api-jobs-courses-impulseAI
```

#### 2. Configure as variáveis de ambiente
```bash
cp config/env.example .env (para uso local)
# Edite o arquivo .env com suas configurações
```

#### 3. Deploy com Docker Compose
```bash
# Construir e iniciar os containers
cd deployment
docker-compose up -d

# Verificar logs
docker-compose logs -f api
```

#### 4. Deploy manual (sem Docker)
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente 
export API_SECRET_KEY="secret-key-uuid-secreta"
export LINKEDIN_EMAIL="seu-email@exemplo.com" # não é necessário mas melhora a performance
export LINKEDIN_PASSWORD="sua-senha" # não é necessário mas melhora a performance

# Executar a aplicação
python main.py
```

### 5. Testar a nova implementação do Udemy
```bash
# Testar o scraper do Udemy especificamente
python tests/test_udemy_scraper.py

# Testar a API completa
python tests/test_api.py
```

### 6. Visualizar a documentação Swagger
```bash
# Opção 1: Servidor de documentação dedicado
python docs/serve_docs.py

# Opção 2: Abrir arquivo HTML diretamente
open docs/swagger-ui.html  # macOS/Linux
start docs/swagger-ui.html  # Windows
```

**URLs disponíveis:**
- **Documentação Swagger**: http://localhost:5000/docs
- **Página inicial**: http://localhost:5000
- **Health check**: http://localhost:5000/health

## 🔑 Autenticação

A API utiliza sistema de API keys para autenticação. Todas as requisições devem incluir o header:

```
X-API-Key: sua-api-key
```

### API Keys disponíveis:
- `1e6a8d8f-9b0c-4c7e-8a3d-5f2b1c9d8e7a` 

## 🎯 Implementação Avançada do Udemy

### Características da Nova Implementação
- **Cloudscraper**: Utiliza `cloudscraper` para contornar as proteções anti-bot da Udemy
- **Headers Específicos**: Implementa headers corretos incluindo `Referer` para simular navegação real
- **Busca em Múltiplas Páginas**: Itera automaticamente por várias páginas para obter mais resultados
- **Processamento com Pandas**: Usa `pandas` para ordenar cursos por rating e número de reviews
- **Rate Limiting Inteligente**: Pausa entre requisições para evitar bloqueios
- **Logging Detalhado**: Logs para debug e monitoramento
-- **Esteira dedicada no Github e Railway**: Acompanhamento e troubleshooting para deploy**

### Estrutura de Dados Retornada
```json
{
  "id": "udemy_123456",
  "title": "Python for Beginners",
  "instructor": "John Doe",
  "num_reviews": 1500,
  "rating": 4.5,
  "students_count": 50000,
  "price": 29.99,
  "original_price": 199.99,
  "language": "English",
  "duration": "10.5 hours",
  "level": "Beginner",
  "url": "https://www.udemy.com/course/python-for-beginners/",
  "image_url": "https://img-c.udemycdn.com/course/480x270/123456.jpg",
  "description": "Learn Python from scratch",
  "source": "udemy"
}
```

## 📚 Endpoints da API

### Health Check
```http
GET /health
```

### Buscar Vagas
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

### Buscar Cursos
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

### Detalhes de Vaga
```http
GET /api/v1/jobs/{job_id}
X-API-Key: sua-api-key
```

### Detalhes de Curso
```http
GET /api/v1/courses/{course_id}
X-API-Key: sua-api-key
```

## 🔒 Segurança

### Rate Limiting
- **Vagas**: 30 requisições por minuto
- **Cursos**: 30 requisições por minuto
- **Detalhes**: 20 requisições por minuto
- **Global**: 3000 requisições por dia, 1800 por hora

### Headers de Segurança
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000

## 📝 Exemplos de Uso

### JavaScript/Node.js
```javascript
const axios = require('axios');

const apiKey = 'sua-api-key';
const baseURL = 'https://sua-api.com';

// Buscar vagas
const searchJobs = async () => {
  try {
    const response = await axios.post(`${baseURL}/api/v1/jobs/`, {
      query: 'Python Developer',
      location: 'São Paulo',
      limit: 10
    }, {
      headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json'
      }
    });
    
    console.log(response.data);
  } catch (error) {
    console.error('Erro:', error.response.data);
  }
};

// Buscar cursos
const searchCourses = async () => {
  try {
    const response = await axios.post(`${baseURL}/api/v1/courses/`, {
      query: 'Machine Learning',
      platform: 'udemy',
      limit: 10
    }, {
      headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json'
      }
    });
    
    console.log(response.data);
  } catch (error) {
    console.error('Erro:', error.response.data);
  }
};
```

### Python
```python
import requests

api_key = '1e6a8d8f-9b0c-4c7e-8a3d-5f2b1c9d8e7a'
base_url = 'api-jobs-courses-impulseai-develop.up.railway.app' # Develop 
base_url = 'api-jobs-courses-impulseai.up.railway.app' # Production 

headers = {
    'X-API-Key': api_key,
    'Content-Type': 'application/json'
}

# Buscar vagas
def search_jobs():
    data = {
        'query': 'Python Developer',
        'location': 'São Paulo',
        'limit': 10
    }
    
    response = requests.post(
        f'{base_url}/api/v1/jobs',
        json=data,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Erro: {response.json()}')

# Buscar cursos
def search_courses():
    data = {
        'query': 'Machine Learning',
        'platform': 'udemy',
        'limit': 10
    }
    
    response = requests.post(
        f'{base_url}/api/v1/courses',
        json=data,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Erro: {response.json()}')
```

### cURL
```bash
# Buscar vagas
curl -X POST https://sua-api.com/api/v1/jobs \
  -H "X-API-Key: sua-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python Developer",
    "location": "São Paulo",
    "limit": 10
  }'

# Buscar cursos
curl -X POST https://sua-api.com/api/v1/courses \
  -H "X-API-Key: sua-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Machine Learning",
    "platform": "udemy",
    "limit": 10
  }'
```

## 📚 Documentação da API

### OpenAPI/Swagger
A API possui documentação completa usando OpenAPI 3.0.3:

- **Arquivo OpenAPI**: `openapi.yaml`
- **Interface Swagger**: `swagger-ui.html`

Para visualizar a documentação interativa:
```bash
# Abrir o arquivo HTML no navegador
open swagger-ui.html
# ou
start swagger-ui.html  # Windows
```

### Características da Documentação
- **Especificação Completa**: Todos os endpoints documentados
- **Schemas Detalhados**: Modelos de dados para vagas e cursos
- **Exemplos de Uso**: Requisições e respostas de exemplo
- **Autenticação**: Documentação do sistema de API keys
- **Rate Limiting**: Informações sobre limites de uso
- **Códigos de Erro**: Todos os possíveis códigos de resposta
- **Testes Unitários**: Testes realizados na API e no Scraper de Cursos

## 🏗️ Estrutura do Projeto

O projeto segue o padrão de organização por domínio/funcionalidade:

```
api-jobs-courses-impulseAI/
├── main.py              # Aplicação principal (ponto de entrada)
├── courses/             # Módulo de cursos
│   ├── __init__.py
│   ├── controllers.py   # Controllers da API (endpoints)
│   ├── models.py        # Modelos de dados e validações
│   └── services.py      # Lógica de negócio e integração com scrapers
├── jobs/                # Módulo de vagas
│   ├── __init__.py
│   ├── controllers.py   # Controllers da API (endpoints)
│   ├── models.py        # Modelos de dados e validações
│   └── services.py      # Lógica de negócio e integração com scrapers
├── scrapers/            # Módulos de scraping (legado)
│   ├── __init__.py
│   ├── job_scraper.py   # Scraper de vagas (LinkedIn)
│   └── course_scraper.py # Scraper de cursos (Udemy, Coursera, edX)
├── config/              # Configurações
│   ├── __init__.py
│   └── env.example      # Exemplo de variáveis de ambiente
├── tests/               # Testes
│   ├── __init__.py
│   ├── test_api.py      # Teste da API
│   └── test_udemy_scraper.py # Teste do scraper Udemy
├── docs/                # Documentação
│   ├── __init__.py
│   ├── openapi.yaml     # Especificação OpenAPI/Swagger
│   ├── swagger-ui.html  # Interface Swagger UI
│   ├── serve_docs.py    # Servidor de documentação
│   └── API_CONSUMER_GUIDE.md # Guia para consumidores
├── deployment/          # Configurações de deploy
│   ├── __init__.py
│   ├── Dockerfile       # Configuração Docker
│   ├── docker-compose.yml # Orquestração de containers
│   ├── nginx.conf       # Configuração Nginx
│   ├── deploy.sh        # Script de deploy
│   └── gunicorn.conf.py # Configuração Gunicorn
├── .github/             # GitHub Actions (CI/CD)
│   └── workflows/
│       └── deploy.yml   # Pipeline de CI/CD
├── railway.json         # Configuração Railway
├── requirements.txt     # Dependências Python
├── .gitignore          # Arquivos ignorados pelo Git
├── app.py              # Aplicação Flask (legado - será removida)
├── web-scraping.py     # Exemplo de scraping (legado)
└── README.md           # Documentação
```

### 📁 Organização por Domínio

- **`courses/`**: Tudo relacionado a cursos online
- **`jobs/`**: Tudo relacionado a vagas de emprego
- **`scrapers/`**: Módulos de scraping (serão migrados para os domínios)
- **`config/`**: Configurações da aplicação
- **`tests/`**: Testes organizados por funcionalidade
- **`docs/`**: Documentação completa da API
- **`deployment/`**: Configurações de deploy e infraestrutura
- **`.github/`**: Pipeline de CI/CD com GitHub Actions

## 🚀 CI/CD Pipeline

### GitHub Actions + Railway

O projeto inclui um pipeline completo de CI/CD configurado com:

- **Testes Automatizados**: Linting, testes unitários e cobertura
- **Security Scan**: Análise de segurança com Bandit
- **Deploy Automático**: Deploy no Railway a cada push
- **Health Check**: Verificação automática após deploy
- **Docker Build**: Construção de imagem Docker

### Configuração Rápida

1. **Fork/Clone** o repositório
2. **Configure secrets** no GitHub:
   - `RAILWAY_TOKEN`
   - `RAILWAY_PROJECT_ID`
3. **Faça push** para `feature/api-web-scraping para develop e `main` paras Production
4. **Acesse** a URL gerada pelo Railway

📖 **Documentação detalhada**: [docs/CI_CD_SETUP.md](docs/CI_CD_SETUP.md)

### Troubleshooting
Se o health check falhar, consulte: [docs/HEALTH_CHECK_TROUBLESHOOTING.md](docs/HEALTH_CHECK_TROUBLESHOOTING.md)

## 🔧 Configuração de Produção

### 1. SSL/TLS
Para produção, configure certificados SSL válidos:
```bash
# Gerar certificados auto-assinados (apenas para teste)
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem
```

### 2. Variáveis de Ambiente
Configure as seguintes variáveis no arquivo `.env`:
- `API_SECRET_KEY`: Chave secreta para assinaturas HMAC
- `LINKEDIN_EMAIL`: Email do LinkedIn (opcional)
- `LINKEDIN_PASSWORD`: Senha do LinkedIn (opcional)

### 3. Monitoramento
```bash
# Verificar saúde da API
curl https://sua-api.com/health

# Verificar logs
docker-compose logs -f api
```

## 🚨 Limitações e Considerações

1. **LinkedIn**: Requer credenciais válidas para acesso completo
2. **Rate Limiting**: Respeite os limites da API para evitar bloqueios
3. **Web Scraping**: Pode ser afetado por mudanças nas páginas web
4. **Legal**: Certifique-se de respeitar os termos de uso dos sites

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte, entre em contato através de:
- Email: melg@cin.ufpe.br
- Issues: [GitHub Issues](https://github.com/seu-usuario/api-jobs-courses-impulseAI/issues)