#!/usr/bin/env python3
"""
Script de teste para demonstrar o uso da API de Web Scraping
"""

import requests
import json
import time
from typing import Dict, Any

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica a saúde da API"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def search_jobs(self, query: str, location: str = "", limit: int = 5) -> Dict[str, Any]:
        """Busca vagas de emprego"""
        try:
            data = {
                'query': query,
                'location': location,
                'limit': limit
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/jobs/",
                json=data,
                headers=self.headers
            )
            
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def search_courses(self, query: str, platform: str = "all", limit: int = 5) -> Dict[str, Any]:
        """Busca cursos online"""
        try:
            data = {
                'query': query,
                'platform': platform,
                'limit': limit
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/courses/",
                json=data,
                headers=self.headers
            )
            
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """Obtém detalhes de uma vaga específica"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/jobs/{job_id}",
                headers=self.headers
            )
            
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def get_course_details(self, course_id: str) -> Dict[str, Any]:
        """Obtém detalhes de um curso específico"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/courses/{course_id}",
                headers=self.headers
            )
            
            return response.json()
        except Exception as e:
            return {'error': str(e)}

def print_response(title: str, response: Dict[str, Any]):
    """Imprime a resposta formatada"""
    print(f"\n{'='*50}")
    print(f"📋 {title}")
    print(f"{'='*50}")
    print(json.dumps(response, indent=2, ensure_ascii=False))

def main():
    """Função principal de teste"""
    
    # Configurações da API
    BASE_URL = "http://localhost:5000"  # Altere para sua URL
    API_KEY = "api-key-1-change-in-production"  # Altere para sua API key
    
    # Criar cliente da API
    client = APIClient(BASE_URL, API_KEY)
    
    print("🚀 Iniciando testes da API de Web Scraping")
    print(f"📍 URL Base: {BASE_URL}")
    print(f"🔑 API Key: {API_KEY[:10]}...")
    
    # Teste 1: Health Check
    print_response("Health Check", client.health_check())
    
    # Aguardar um pouco
    time.sleep(1)
    
    # Teste 2: Buscar vagas
    print_response(
        "Busca de Vagas - Python Developer",
        client.search_jobs("Python Developer", "São Paulo", 3)
    )
    
    # Aguardar um pouco
    time.sleep(2)
    
    # Teste 3: Buscar cursos
    print_response(
        "Busca de Cursos - Machine Learning",
        client.search_courses("Machine Learning", "udemy", 3)
    )
    
    # Aguardar um pouco
    time.sleep(2)
    
    # Teste 4: Buscar vagas de Data Science
    print_response(
        "Busca de Vagas - Data Scientist",
        client.search_jobs("Data Scientist", "Brasil", 3)
    )
    
    # Aguardar um pouco
    time.sleep(2)
    
    # Teste 5: Buscar cursos de Python
    print_response(
        "Busca de Cursos - Python",
        client.search_courses("Python", "all", 3)
    )
    
    print(f"\n{'='*50}")
    print("✅ Testes concluídos!")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
