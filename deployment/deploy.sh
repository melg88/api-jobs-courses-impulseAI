#!/bin/bash

# Script de deploy automatizado para a API de Web Scraping

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Verificar se Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado. Por favor, instale o Docker primeiro."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
        exit 1
    fi
    
    print_message "Docker e Docker Compose encontrados"
}

# Verificar arquivo .env
check_env_file() {
    if [ ! -f .env ]; then
        print_warning "Arquivo .env não encontrado. Criando a partir do exemplo..."
        if [ -f env.example ]; then
            cp env.example .env
            print_message "Arquivo .env criado. Por favor, edite-o com suas configurações."
            print_warning "IMPORTANTE: Edite o arquivo .env antes de continuar!"
            exit 1
        else
            print_error "Arquivo env.example não encontrado."
            exit 1
        fi
    fi
    
    print_message "Arquivo .env encontrado"
}

# Criar diretórios necessários
create_directories() {
    print_message "Criando diretórios necessários..."
    
    mkdir -p logs
    mkdir -p ssl
    
    print_message "Diretórios criados"
}

# Gerar certificados SSL (auto-assinados para teste)
generate_ssl_certificates() {
    if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
        print_warning "Certificados SSL não encontrados. Gerando certificados auto-assinados..."
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem -out ssl/cert.pem \
            -subj "/C=BR/ST=SP/L=Sao Paulo/O=API/CN=localhost"
        
        print_message "Certificados SSL gerados (apenas para teste)"
        print_warning "Para produção, substitua por certificados válidos!"
    else
        print_message "Certificados SSL encontrados"
    fi
}

# Construir e iniciar containers
deploy_containers() {
    print_message "Construindo e iniciando containers..."
    
    # Parar containers existentes
    docker-compose down --remove-orphans
    
    # Construir imagens
    docker-compose build --no-cache
    
    # Iniciar containers
    docker-compose up -d
    
    print_message "Containers iniciados"
}

# Verificar saúde da API
check_health() {
    print_message "Verificando saúde da API..."
    
    # Aguardar um pouco para a API inicializar
    sleep 10
    
    # Tentar fazer health check
    for i in {1..5}; do
        if curl -f http://localhost:5000/health &> /dev/null; then
            print_message "✅ API está funcionando corretamente!"
            return 0
        else
            print_warning "Tentativa $i: API ainda não está pronta..."
            sleep 5
        fi
    done
    
    print_error "❌ API não está respondendo após 30 segundos"
    print_message "Verificando logs..."
    docker-compose logs api
    return 1
}

# Mostrar informações finais
show_info() {
    print_header "Deploy Concluído!"
    
    echo -e "${GREEN}🎉 API de Web Scraping está rodando!${NC}"
    echo ""
    echo -e "${BLUE}📋 Informações:${NC}"
    echo -e "  • API URL: ${GREEN}http://localhost:5000${NC}"
    echo -e "  • Health Check: ${GREEN}http://localhost:5000/health${NC}"
    echo -e "  • Nginx (HTTPS): ${GREEN}https://localhost${NC}"
    echo ""
    echo -e "${BLUE}🔑 API Keys disponíveis:${NC}"
    echo -e "  • ${GREEN}api-key-1-change-in-production${NC}"
    echo -e "  • ${GREEN}api-key-2-change-in-production${NC}"
    echo ""
    echo -e "${BLUE}📚 Endpoints:${NC}"
    echo -e "  • POST ${GREEN}/api/v1/jobs${NC} - Buscar vagas"
    echo -e "  • POST ${GREEN}/api/v1/courses${NC} - Buscar cursos"
    echo -e "  • GET  ${GREEN}/api/v1/jobs/{id}${NC} - Detalhes da vaga"
    echo -e "  • GET  ${GREEN}/api/v1/courses/{id}${NC} - Detalhes do curso"
    echo ""
    echo -e "${BLUE}🧪 Testar API:${NC}"
    echo -e "  • ${GREEN}python test_api.py${NC}"
    echo ""
    echo -e "${BLUE}📊 Monitoramento:${NC}"
    echo -e "  • Logs: ${GREEN}docker-compose logs -f api${NC}"
    echo -e "  • Status: ${GREEN}docker-compose ps${NC}"
    echo -e "  • Parar: ${GREEN}docker-compose down${NC}"
}

# Função principal
main() {
    print_header "Deploy da API de Web Scraping"
    
    # Verificações
    check_docker
    check_env_file
    
    # Preparação
    create_directories
    generate_ssl_certificates
    
    # Deploy
    deploy_containers
    
    # Verificação
    if check_health; then
        show_info
    else
        print_error "Deploy falhou. Verifique os logs acima."
        exit 1
    fi
}

# Executar função principal
main "$@"
