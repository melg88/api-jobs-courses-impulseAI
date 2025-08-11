"""
Services para o módulo de cursos
Responsável pela lógica de negócio e integração com scrapers
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys
import os

# Adicionar o diretório raiz ao path para importar o scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.course_scraper import CourseScraper
from .models import (
    CourseSearchRequest, 
    CourseDetailRequest, 
    Course, 
    CourseDetail, 
    CourseSearchResult,
    CourseHealthStatus
)

logger = logging.getLogger(__name__)

class CourseService:
    """Serviço para gerenciar operações relacionadas a cursos"""
    
    def __init__(self):
        self.scraper = CourseScraper()
        self._rate_limit_counter = 0
        self._last_request_time = 0
    
    def search_courses(self, request: CourseSearchRequest) -> Dict[str, Any]:
        """
        Busca cursos baseado nos critérios fornecidos
        
        Args:
            request: Objeto com os critérios de busca
            
        Returns:
            Dicionário com os resultados da busca
        """
        try:
            # Aplicar rate limiting
            self._check_rate_limit()
            
            logger.info(f"Iniciando busca de cursos: {request.query} na plataforma {request.platform}")
            
            # Executar busca usando o scraper
            raw_courses = self.scraper.search_courses(
                query=request.query,
                platform=request.platform,
                limit=request.limit,
                language=request.language
            )
            
            # Converter para objetos Course
            courses = []
            for raw_course in raw_courses:
                course = Course(
                    id=raw_course.get('id', ''),
                    title=raw_course.get('title', ''),
                    instructor=raw_course.get('instructor', ''),
                    num_reviews=raw_course.get('num_reviews'),
                    rating=raw_course.get('rating'),
                    students_count=raw_course.get('students_count'),
                    price=raw_course.get('price'),
                    original_price=raw_course.get('original_price'),
                    language=raw_course.get('language'),
                    duration=raw_course.get('duration'),
                    level=raw_course.get('level'),
                    url=raw_course.get('url'),
                    image_url=raw_course.get('image_url'),
                    description=raw_course.get('description'),
                    source=raw_course.get('source', 'unknown')
                )
                courses.append(course)
            
            # Aplicar filtros adicionais
            courses = self._apply_filters(courses, request)
            
            # Criar resultado
            result = CourseSearchResult(
                courses=courses,
                total=len(courses),
                query=request.query,
                platform=request.platform,
                timestamp=datetime.now()
            )
            
            logger.info(f"Busca concluída: {len(courses)} cursos encontrados")
            
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Erro na busca de cursos: {str(e)}")
            raise
    
    def get_course_details(self, request: CourseDetailRequest) -> Optional[Dict[str, Any]]:
        """
        Obtém detalhes completos de um curso específico
        
        Args:
            request: Objeto com o ID do curso
            
        Returns:
            Dicionário com os detalhes do curso ou None se não encontrado
        """
        try:
            # Aplicar rate limiting
            self._check_rate_limit()
            
            logger.info(f"Obtendo detalhes do curso: {request.course_id}")
            
            # Executar busca de detalhes usando o scraper
            raw_details = self.scraper.get_course_details(request.course_id)
            
            if not raw_details:
                logger.warning(f"Curso não encontrado: {request.course_id}")
                return None
            
            # Converter para objeto CourseDetail
            course_detail = CourseDetail(
                id=raw_details.get('id', ''),
                title=raw_details.get('title', ''),
                instructor=raw_details.get('instructor', ''),
                num_reviews=raw_details.get('num_reviews'),
                rating=raw_details.get('rating'),
                students_count=raw_details.get('students_count'),
                price=raw_details.get('price'),
                original_price=raw_details.get('original_price'),
                language=raw_details.get('language'),
                duration=raw_details.get('duration'),
                level=raw_details.get('level'),
                url=raw_details.get('url'),
                image_url=raw_details.get('image_url'),
                description=raw_details.get('description'),
                source=raw_details.get('source', 'unknown'),
                full_description=raw_details.get('full_description'),
                curriculum=raw_details.get('curriculum'),
                requirements=raw_details.get('requirements'),
                objectives=raw_details.get('objectives'),
                last_updated=raw_details.get('last_updated'),
                certificate=raw_details.get('certificate'),
                subtitles=raw_details.get('subtitles')
            )
            
            logger.info(f"Detalhes obtidos com sucesso para: {request.course_id}")
            
            return course_detail.to_dict()
            
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do curso {request.course_id}: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde do serviço de cursos
        
        Returns:
            Dicionário com o status de saúde
        """
        try:
            # Testar conexão com o scraper
            test_result = self.scraper.search_courses("test", platform="udemy", limit=1)
            
            health_status = CourseHealthStatus(
                status="healthy",
                message="Serviço de cursos funcionando normalmente"
            )
            
            return health_status.to_dict()
            
        except Exception as e:
            logger.error(f"Erro no health check: {str(e)}")
            
            health_status = CourseHealthStatus(
                status="unhealthy",
                message="Erro no serviço de cursos",
                error=str(e)
            )
            
            return health_status.to_dict()
    
    def _apply_filters(self, courses: List[Course], request: CourseSearchRequest) -> List[Course]:
        """
        Aplica filtros adicionais aos cursos
        
        Args:
            courses: Lista de cursos
            request: Requisição com filtros
            
        Returns:
            Lista de cursos filtrada
        """
        filtered_courses = courses
        
        # Filtrar por nível
        if request.level and request.level != 'all':
            filtered_courses = [
                course for course in filtered_courses 
                if course.level and course.level.lower() == request.level.lower()
            ]
        
        # Filtrar por idioma
        if request.language:
            filtered_courses = [
                course for course in filtered_courses 
                if course.language and request.language.lower() in course.language.lower()
            ]
        
        # Filtrar por faixa de preço
        if request.price_range == 'free':
            filtered_courses = [
                course for course in filtered_courses 
                if course.price == 0 or course.price is None
            ]
        elif request.price_range == 'paid':
            filtered_courses = [
                course for course in filtered_courses 
                if course.price and course.price > 0
            ]
        
        return filtered_courses
    
    def _check_rate_limit(self):
        """
        Verifica e aplica rate limiting
        """
        current_time = time.time()
        
        # Rate limit: 10 requisições por minuto
        if current_time - self._last_request_time < 6:  # 6 segundos entre requisições
            time.sleep(6 - (current_time - self._last_request_time))
        
        self._last_request_time = time.time()
        self._rate_limit_counter += 1
    
    def __del__(self):
        """Destrutor para limpar recursos"""
        if hasattr(self, 'scraper'):
            try:
                self.scraper.close()
            except Exception as e:
                logger.error(f"Erro ao fechar scraper: {str(e)}")
