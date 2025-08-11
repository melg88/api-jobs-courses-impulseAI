#!/usr/bin/env python3
"""
Script de teste para o scraper do Udemy
Testa a nova implementação usando cloudscraper e pandas
"""

import sys
import os
import json
import logging

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.course_scraper import CourseScraper

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_udemy_scraper():
    """Testa o scraper do Udemy"""
    print("🧪 Testando o scraper do Udemy...")
    
    scraper = CourseScraper()
    
    try:
        # Teste 1: Buscar cursos de Python
        print("\n📚 Teste 1: Buscando cursos de 'Python'...")
        courses = scraper.search_courses("Python", platform="udemy", limit=5)
        
        if courses:
            print(f"✅ Encontrados {len(courses)} cursos:")
            for i, course in enumerate(courses, 1):
                print(f"  {i}. {course['title']}")
                print(f"     Rating: {course.get('rating', 'N/A')}")
                print(f"     Reviews: {course.get('num_reviews', 'N/A')}")
                print(f"     Instructor: {course.get('instructor', 'N/A')}")
                print(f"     URL: {course.get('url', 'N/A')}")
                print()
        else:
            print("❌ Nenhum curso encontrado")
        
        # Teste 2: Buscar cursos de Machine Learning
        print("\n🤖 Teste 2: Buscando cursos de 'Machine Learning'...")
        courses_ml = scraper.search_courses("Machine Learning", platform="udemy", limit=3)
        
        if courses_ml:
            print(f"✅ Encontrados {len(courses_ml)} cursos:")
            for i, course in enumerate(courses_ml, 1):
                print(f"  {i}. {course['title']}")
                print(f"     Rating: {course.get('rating', 'N/A')}")
                print(f"     Reviews: {course.get('num_reviews', 'N/A')}")
                print()
        else:
            print("❌ Nenhum curso encontrado")
        
        # Teste 3: Testar detalhes de um curso (se houver cursos)
        if courses:
            first_course_id = courses[0]['id']
            print(f"\n🔍 Teste 3: Obtendo detalhes do curso {first_course_id}...")
            
            course_details = scraper.get_course_details(first_course_id)
            if course_details:
                print("✅ Detalhes do curso obtidos:")
                print(f"   Título: {course_details.get('title', 'N/A')}")
                print(f"   Instructor: {course_details.get('instructor', 'N/A')}")
                print(f"   Rating: {course_details.get('rating', 'N/A')}")
                print(f"   Reviews: {course_details.get('num_reviews', 'N/A')}")
                print(f"   Estudantes: {course_details.get('students_count', 'N/A')}")
                print(f"   Duração: {course_details.get('duration', 'N/A')}")
                print(f"   Nível: {course_details.get('level', 'N/A')}")
            else:
                print("❌ Não foi possível obter detalhes do curso")
        
        # Teste 4: Verificar estrutura dos dados
        print("\n📊 Teste 4: Verificando estrutura dos dados...")
        if courses:
            sample_course = courses[0]
            required_fields = ['id', 'title', 'instructor', 'rating', 'num_reviews', 'source']
            
            missing_fields = []
            for field in required_fields:
                if field not in sample_course:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Campos ausentes: {missing_fields}")
            else:
                print("✅ Todos os campos obrigatórios estão presentes")
                
            # Verificar se os dados estão sendo ordenados corretamente
            if len(courses) > 1:
                ratings = [c.get('rating', 0) for c in courses if c.get('rating')]
                if ratings == sorted(ratings, reverse=True):
                    print("✅ Dados ordenados corretamente por rating")
                else:
                    print("⚠️  Dados não estão ordenados por rating")
        
        print("\n🎉 Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        logging.error(f"Erro no teste: {str(e)}")
    
    finally:
        scraper.close()

def test_api_integration():
    """Testa a integração com a API Flask"""
    print("\n🌐 Testando integração com a API...")
    
    try:
        import requests
        
        # URL da API (assumindo que está rodando localmente)
        api_url = "http://localhost:5000"
        
        # Teste de health check
        print("🔍 Testando health check...")
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            print("✅ Health check OK")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
        
        # Teste de busca de cursos (requer API key)
        print("🔍 Testando busca de cursos...")
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': 'api-key-1-change-in-production'  # Usar uma das chaves do env.example
        }
        
        data = {
            'query': 'Python',
            'platform': 'udemy',
            'limit': 3
        }
        
        response = requests.post(f"{api_url}/api/v1/courses", json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Busca de cursos OK: {len(result.get('courses', []))} cursos encontrados")
        else:
            print(f"❌ Busca de cursos falhou: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API não está rodando. Execute 'python app.py' primeiro.")
    except Exception as e:
        print(f"❌ Erro no teste da API: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando testes do scraper do Udemy...")
    
    # Teste do scraper
    test_udemy_scraper()
    
    # Teste da integração com a API
    test_api_integration()
    
    print("\n✨ Todos os testes concluídos!")
