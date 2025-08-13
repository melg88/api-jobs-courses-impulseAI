import os
import time
import logging
import requests
import cloudscraper
import pandas as pd
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import requests
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class CourseScraper:
    def __init__(self):
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Inicializar cloudscraper para Udemy
        self.udemy_scraper = cloudscraper.create_scraper()
        
    def _setup_driver(self):
        """Configura o driver do Chrome com opções headless"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar driver: {str(e)}")
            return False
    
    def search_courses(self, query: str, platform: str = "all", limit: int = 10, language: str = "en") -> List[Dict]:
        """
        Busca cursos em diferentes plataformas
        
        Args:
            query: Termo de busca
            platform: Plataforma específica (udemy, coursera, edx, all)
            limit: Número máximo de resultados
            
        Returns:
            Lista de cursos encontrados
        """
        courses = []
        
        try:
            if platform.lower() == "all" or platform.lower() == "udemy":
                udemy_courses = self._search_udemy(query, limit, language)
                courses.extend(udemy_courses)
            
            if platform.lower() == "all" or platform.lower() == "coursera":
                coursera_courses = self._search_coursera(query, limit)
                courses.extend(coursera_courses)
            
            if platform.lower() == "all" or platform.lower() == "edx":
                edx_courses = self._search_edx(query, limit)
                courses.extend(edx_courses)
            
            # Ordenar por relevância e limitar resultados
            courses = courses[:limit]
            
            logger.info(f"Encontrados {len(courses)} cursos para '{query}' na plataforma {platform}")
            return courses
            
        except Exception as e:
            logger.error(f"Erro na busca de cursos: {str(e)}")
            return []
    
    def _search_udemy(self, query: str, limit: int, language: str) -> List[Dict]:
        """Busca cursos na Udemy usando cloudscraper e pandas"""
        if query != "":
            query_optimized = quote_plus(query)
        try:
            # Headers específicos para Udemy
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': f'https://www.udemy.com/courses/search/?q={query_optimized}&src=ukw&p=1',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                #"Referer": f"https://www.udemy.com/courses/search/?p=1&q={query}&src=ukw",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            }
            
            cursos_totais = []
            max_pages = min(3, (limit // 12) + 1)  # Udemy retorna ~12 cursos por página

            
            for i in range(1, max_pages + 1):
                try:

                    # URL da API da Udemy
                    #url_api = f'https://www.udemy.com/api-2.0/search-courses/?src=ukw&q={query_optimized}&skip_price=true&lang={language}&p={i}'
                    url_api = f'https://www.udemy.com/api-2.0/search-courses/?src=ukw&q={query_optimized}&p={i}'
                    print(url_api)

                    response = self.udemy_scraper.get(url_api, headers=headers)
                    response.raise_for_status()
                    
                    # Parsear a resposta JSON
                    data = response.json()
                    
                    # Extrair dados dos cursos
                    cursos = data.get("courses", [])
                    
                    for curso in cursos:
                        curso_data = {
                            "id": f"udemy_{curso.get('id')}",
                            "title": curso.get("title"),
                            "instructor": curso.get("visible_instructors", [{}])[0].get("display_name", ""),
                            "num_reviews": curso.get("num_reviews"),
                            "rating": curso.get("rating"),
                            "students_count": curso.get("num_students"),
                            "price": curso.get("price"),
                            "original_price": curso.get("price_detail", {}).get("list_price"),
                            "language": curso.get("lang_s"),
                            "duration": curso.get("content_info"),
                            "level": curso.get("instructional_level"),
                            "url": f"https://www.udemy.com{curso.get('url')}",
                            "image_url": curso.get("image_480x270"),
                            "description": curso.get("headline"),
                            "source": "udemy"
                        }
                        cursos_totais.append(curso_data)
                        
                        # Log para debug
                        logger.debug(f"Curso encontrado: {curso_data['title']}")
                        logger.debug(f"Reviews: {curso_data['num_reviews']}")
                        logger.debug(f"Rating: {curso_data['rating']}")
                    
                    # Pausa entre requisições para evitar rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Erro ao buscar página {i} da Udemy: {str(e)}")
                    continue
            
            # Usar pandas para processar e ordenar os dados
            if cursos_totais:
                df = pd.DataFrame(cursos_totais)
                
                # Ordenar por rating (se disponível) e número de reviews
                if 'rating' in df.columns and 'num_reviews' in df.columns:
                    df = df.sort_values(['rating', 'num_reviews'], ascending=[False, False])
                
                # Converter de volta para lista de dicionários
                cursos_totais = df.head(limit).to_dict('records')
                
                logger.info(f"Total de cursos encontrados na Udemy: {len(cursos_totais)}")
            
            return cursos_totais
            
        except Exception as e:
            logger.error(f"Erro ao buscar cursos na Udemy: {str(e)}")
            return []
    
    def _search_coursera(self, query: str, limit: int) -> List[Dict]:
        """Busca cursos na Coursera"""
        try:
            # URL de busca da Coursera
            search_url = f"https://www.coursera.org/api/searchQuery?query={query}&start=0&limit={limit}"
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            data = response.json()
            courses = []
            
            for course in data.get('linked', {}).get('onDemandCourses', {}).get('v1', []):
                course_data = {
                    'id': f"coursera_{course.get('id')}",
                    'title': course.get('name'),
                    'instructor': course.get('instructorIds', []),
                    'rating': course.get('averageFiveStarRating'),
                    'students_count': course.get('enrolledLearnersCount'),
                    'price': course.get('price'),
                    'language': course.get('language'),
                    'duration': course.get('duration'),
                    'level': course.get('level'),
                    'url': f"https://www.coursera.org/learn/{course.get('slug')}",
                    'image_url': course.get('photoUrl'),
                    'description': course.get('description'),
                    'source': 'coursera'
                }
                courses.append(course_data)
            
            return courses
            
        except Exception as e:
            logger.error(f"Erro ao buscar cursos na Coursera: {str(e)}")
            return []
    
    def _search_edx(self, query: str, limit: int) -> List[Dict]:
        """Busca cursos na edX"""
        try:
            # URL de busca da edX
            search_url = f"https://www.edx.org/api/v1/search/catalog/?q={query}&page=1&page_size={limit}"
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            data = response.json()
            courses = []
            
            for course in data.get('objects', {}).get('results', []):
                course_data = {
                    'id': f"edx_{course.get('key')}",
                    'title': course.get('title'),
                    'instructor': course.get('staff', []),
                    'rating': course.get('rating'),
                    'students_count': course.get('enrollment_count'),
                    'price': course.get('price'),
                    'language': course.get('language'),
                    'duration': course.get('effort'),
                    'level': course.get('level'),
                    'url': f"https://www.edx.org{course.get('url')}",
                    'image_url': course.get('image', {}).get('src'),
                    'description': course.get('short_description'),
                    'source': 'edx'
                }
                courses.append(course_data)
            
            return courses
            
        except Exception as e:
            logger.error(f"Erro ao buscar cursos na edX: {str(e)}")
            return []
    
    def get_course_details(self, course_id: str) -> Optional[Dict]:
        """
        Obtém detalhes completos de um curso específico
        
        Args:
            course_id: ID do curso
            
        Returns:
            Dicionário com detalhes do curso ou None se não encontrado
        """
        try:
            # Determinar a plataforma baseado no ID ou implementar lógica específica
            if course_id.startswith('udemy_'):
                return self._get_udemy_course_details(course_id)
            elif course_id.startswith('coursera_'):
                return self._get_coursera_course_details(course_id)
            elif course_id.startswith('edx_'):
                return self._get_edx_course_details(course_id)
            else:
                # Tentar detectar automaticamente
                return self._detect_and_get_course_details(course_id)
                
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do curso {course_id}: {str(e)}")
            return None
    
    def _get_udemy_course_details(self, course_id: str) -> Optional[Dict]:
        """Obtém detalhes de um curso da Udemy usando cloudscraper"""
        try:
            # Remover prefixo
            actual_id = course_id.replace('udemy_', '')
            
            # Headers específicos para Udemy
            headers = {
                "Referer": f"https://www.udemy.com/course/{actual_id}/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            }
            
            url = f"https://www.udemy.com/api-2.0/courses/{actual_id}/"
            
            response = self.udemy_scraper.get(url, headers=headers)
            response.raise_for_status()
            
            course = response.json()
            
            return {
                'id': course_id,
                'title': course.get('title'),
                'instructor': course.get('visible_instructors', [{}])[0].get('display_name', ''),
                'rating': course.get('rating'),
                'num_reviews': course.get('num_reviews'),
                'students_count': course.get('num_students'),
                'price': course.get('price'),
                'original_price': course.get('price_detail', {}).get('list_price'),
                'language': course.get('locale', {}).get('title'),
                'duration': course.get('content_info'),
                'level': course.get('instructional_level'),
                'url': f"https://www.udemy.com{course.get('url')}",
                'image_url': course.get('image_480x270'),
                'description': course.get('description'),
                'curriculum': course.get('curriculum', []),
                'requirements': course.get('requirements'),
                'objectives': course.get('objectives'),
                'source': 'udemy'
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do curso Udemy {course_id}: {str(e)}")
            return None
    
    def _get_coursera_course_details(self, course_id: str) -> Optional[Dict]:
        """Obtém detalhes de um curso da Coursera"""
        # Implementar lógica específica para Coursera
        return None
    
    def _get_edx_course_details(self, course_id: str) -> Optional[Dict]:
        """Obtém detalhes de um curso da edX"""
        # Implementar lógica específica para edX
        return None
    
    def _detect_and_get_course_details(self, course_id: str) -> Optional[Dict]:
        """Detecta a plataforma e obtém detalhes do curso"""
        # Implementar lógica de detecção automática
        return None
    
    def close(self):
        """Fecha o driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Erro ao fechar driver: {str(e)}")
            finally:
                self.driver = None
    
    def __del__(self):
        """Destrutor para garantir que o driver seja fechado"""
        self.close()
