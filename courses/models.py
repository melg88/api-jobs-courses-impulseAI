"""
Models para o módulo de cursos
Definição das estruturas de dados e validações
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

@dataclass
class CourseSearchRequest:
    """Modelo para requisição de busca de cursos"""
    query: str
    platform: str = 'all'
    limit: int = 10
    level: Optional[str] = None
    language: Optional[str] = None
    price_range: str = 'all'
    
    def validate(self) -> Optional[str]:
        """Valida os dados da requisição"""
        if not self.query or not self.query.strip():
            return "Query é obrigatória"
        
        if len(self.query.strip()) < 2:
            return "Query deve ter pelo menos 2 caracteres"
        
        if self.limit < 1 or self.limit > 50:
            return "Limit deve estar entre 1 e 50"
        
        valid_platforms = ['all', 'udemy', 'coursera', 'edx']
        if self.platform not in valid_platforms:
            return f"Platform deve ser uma das opções: {', '.join(valid_platforms)}"
        
        if self.level and self.level not in ['beginner', 'intermediate', 'advanced', 'all']:
            return "Level deve ser beginner, intermediate, advanced ou all"
        
        if self.price_range not in ['free', 'paid', 'all']:
            return "Price range deve ser free, paid ou all"
        
        return None

@dataclass
class CourseDetailRequest:
    """Modelo para requisição de detalhes de curso"""
    course_id: str
    
    def validate(self) -> Optional[str]:
        """Valida os dados da requisição"""
        if not self.course_id or not self.course_id.strip():
            return "Course ID é obrigatório"
        
        # Validar formato do ID (platform_id)
        if not re.match(r'^[a-zA-Z]+_\d+$', self.course_id):
            return "Course ID deve estar no formato: platform_id"
        
        return None

@dataclass
class Course:
    """Modelo para representar um curso"""
    id: str
    title: str
    instructor: str
    num_reviews: Optional[int] = None
    rating: Optional[float] = None
    students_count: Optional[int] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    lang_s: Optional[str] = None
    duration: Optional[str] = None
    level: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    source: str = 'unknown'
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o curso para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'instructor': self.instructor,
            'num_reviews': self.num_reviews,
            'rating': self.rating,
            'students_count': self.students_count,
            'price': self.price,
            'original_price': self.original_price,
            'language': self.lang_s,
            'duration': self.duration,
            'level': self.level,
            'url': self.url,
            'image_url': self.image_url,
            'description': self.description,
            'source': self.source
        }

@dataclass
class CourseDetail(Course):
    """Modelo para representar detalhes completos de um curso"""
    full_description: Optional[str] = None
    curriculum: Optional[List[Dict[str, Any]]] = None
    requirements: Optional[List[str]] = None
    objectives: Optional[List[str]] = None
    last_updated: Optional[str] = None
    certificate: Optional[bool] = None
    subtitles: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte os detalhes do curso para dicionário"""
        base_dict = super().to_dict()
        base_dict.update({
            'full_description': self.full_description,
            'curriculum': self.curriculum,
            'requirements': self.requirements,
            'objectives': self.objectives,
            'last_updated': self.last_updated,
            'certificate': self.certificate,
            'subtitles': self.subtitles
        })
        return base_dict

@dataclass
class CourseSearchResult:
    """Modelo para resultado de busca de cursos"""
    courses: List[Course]
    total: int
    query: str
    platform: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o resultado para dicionário"""
        return {
            'success': True,
            'courses': [course.to_dict() for course in self.courses],
            'total': self.total,
            'query': self.query,
            'platform': self.platform,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class CourseHealthStatus:
    """Modelo para status de saúde do módulo de cursos"""
    status: str
    module: str = 'courses'
    timestamp: datetime = None
    message: str = 'Módulo de cursos funcionando normalmente'
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o status para dicionário"""
        return {
            'status': self.status,
            'module': self.module,
            'timestamp': self.timestamp.isoformat(),
            'message': self.message,
            'error': self.error
        }
