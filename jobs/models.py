"""
Models para o módulo de vagas
Definição das estruturas de dados e validações
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

@dataclass
class JobSearchRequest:
    """Modelo para requisição de busca de vagas"""
    query: str
    location: Optional[str] = None
    limit: int = 10
    experience_level: Optional[str] = None
    job_type: Optional[str] = None
    
    def validate(self) -> Optional[str]:
        """Valida os dados da requisição"""
        if not self.query or not self.query.strip():
            return "Query é obrigatória"
        
        if len(self.query.strip()) < 2:
            return "Query deve ter pelo menos 2 caracteres"
        
        if self.limit < 1 or self.limit > 50:
            return "Limit deve estar entre 1 e 50"
        
        if self.experience_level and self.experience_level not in [
            'entry', 'associate', 'mid-senior', 'senior', 'executive', 'internship', 'entry level', 'director'
        ]:
            return "Experience level deve ser entry, associate, mid-senior, senior ou executive"
        
        if self.job_type and self.job_type not in [
            'full-time', 'part-time', 'contract', 'temporary', 'internship'
        ]:
            return "Job type deve ser full-time, part-time, contract, temporary ou internship"
        
        return None

@dataclass
class JobDetailRequest:
    """Modelo para requisição de detalhes de vaga"""
    job_id: str
    
    def validate(self) -> Optional[str]:
        """Valida os dados da requisição"""
        if not self.job_id or not self.job_id.strip():
            return "Job ID é obrigatório"
        
        # Validar formato do ID (platform_id)
        if not re.match(r'^[a-zA-Z]+_\d+$', self.job_id):
            return "Job ID deve estar no formato: platform_id"
        
        return None

@dataclass
class Job:
    """Modelo para representar uma vaga"""
    id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_date: Optional[datetime] = None
    experience_level: Optional[str] = None
    job_type: Optional[str] = None
    source: str = 'linkedin'
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a vaga para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'url': self.url,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'experience_level': self.experience_level,
            'job_type': self.job_type,
            'source': self.source
        }

@dataclass
class JobDetail(Job):
    """Modelo para representar detalhes completos de uma vaga"""
    full_description: Optional[str] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    salary_range: Optional[Dict[str, Any]] = None
    application_count: Optional[int] = None
    skills: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte os detalhes da vaga para dicionário"""
        base_dict = super().to_dict()
        base_dict.update({
            'full_description': self.full_description,
            'requirements': self.requirements,
            'benefits': self.benefits,
            'salary_range': self.salary_range,
            'application_count': self.application_count,
            'skills': self.skills
        })
        return base_dict

@dataclass
class JobSearchResult:
    """Modelo para resultado de busca de vagas"""
    jobs: List[Job]
    total: int
    query: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o resultado para dicionário"""
        return {
            'success': True,
            'jobs': [job.to_dict() for job in self.jobs],
            'total': self.total,
            'query': self.query,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class JobHealthStatus:
    """Modelo para status de saúde do módulo de vagas"""
    status: str
    module: str = 'jobs'
    timestamp: datetime = None
    message: str = 'Módulo de vagas funcionando normalmente'
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
