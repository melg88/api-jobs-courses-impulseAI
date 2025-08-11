"""
Services para o módulo de vagas
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

from scrapers.job_scraper import JobScraper
from .models import (
    JobSearchRequest, 
    JobDetailRequest, 
    Job, 
    JobDetail, 
    JobSearchResult,
    JobHealthStatus
)

logger = logging.getLogger(__name__)

class JobService:
    """Serviço para gerenciar operações relacionadas a vagas de emprego"""
    
    def __init__(self):
        self.scraper = JobScraper()
        self._rate_limit_counter = 0
        self._last_request_time = 0
    
    def search_jobs(self, request: JobSearchRequest) -> Dict[str, Any]:
        """
        Busca vagas baseado nos critérios fornecidos
        
        Args:
            request: Objeto com os critérios de busca
            
        Returns:
            Dicionário com os resultados da busca
        """
        try:
            # Aplicar rate limiting
            self._check_rate_limit()
            
            logger.info(f"Iniciando busca de vagas: {request.query} em {request.location or 'todas as localizações'}")
            
            # Executar busca usando o scraper
            raw_jobs = self.scraper.search_jobs(
                query=request.query,
                location=request.location,
                limit=request.limit
            )
            
            # Converter para objetos Job
            jobs = []
            for raw_job in raw_jobs:
                job = Job(
                    id=raw_job.get('id', ''),
                    title=raw_job.get('title', ''),
                    company=raw_job.get('company', ''),
                    location=raw_job.get('location', ''),
                    description=raw_job.get('description', ''),
                    url=raw_job.get('url', ''),
                    posted_date=self._parse_date(raw_job.get('posted_date')),
                    experience_level=raw_job.get('experience_level'),
                    job_type=raw_job.get('job_type'),
                    source=raw_job.get('source', 'linkedin')
                )
                jobs.append(job)
            
            # Aplicar filtros adicionais
            jobs = self._apply_filters(jobs, request)
            
            # Criar resultado
            result = JobSearchResult(
                jobs=jobs,
                total=len(jobs),
                query=request.query,
                timestamp=datetime.now()
            )
            
            logger.info(f"Busca concluída: {len(jobs)} vagas encontradas")
            
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Erro na busca de vagas: {str(e)}")
            raise
    
    def get_job_details(self, request: JobDetailRequest) -> Optional[Dict[str, Any]]:
        """
        Obtém detalhes completos de uma vaga específica
        
        Args:
            request: Objeto com o ID da vaga
            
        Returns:
            Dicionário com os detalhes da vaga ou None se não encontrada
        """
        try:
            # Aplicar rate limiting
            self._check_rate_limit()
            
            logger.info(f"Obtendo detalhes da vaga: {request.job_id}")
            
            # Executar busca de detalhes usando o scraper
            raw_details = self.scraper.get_job_details(request.job_id)
            
            if not raw_details:
                logger.warning(f"Vaga não encontrada: {request.job_id}")
                return None
            
            # Converter para objeto JobDetail
            job_detail = JobDetail(
                id=raw_details.get('id', ''),
                title=raw_details.get('title', ''),
                company=raw_details.get('company', ''),
                location=raw_details.get('location', ''),
                description=raw_details.get('description', ''),
                url=raw_details.get('url', ''),
                posted_date=self._parse_date(raw_details.get('posted_date')),
                experience_level=raw_details.get('experience_level'),
                job_type=raw_details.get('job_type'),
                source=raw_details.get('source', 'linkedin'),
                full_description=raw_details.get('full_description'),
                requirements=raw_details.get('requirements'),
                benefits=raw_details.get('benefits'),
                salary_range=raw_details.get('salary_range'),
                application_count=raw_details.get('application_count'),
                skills=raw_details.get('skills')
            )
            
            logger.info(f"Detalhes obtidos com sucesso para: {request.job_id}")
            
            return job_detail.to_dict()
            
        except Exception as e:
            logger.error(f"Erro ao obter detalhes da vaga {request.job_id}: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde do serviço de vagas
        
        Returns:
            Dicionário com o status de saúde
        """
        try:
            # Testar conexão com o scraper
            test_result = self.scraper.search_jobs("test", limit=1)
            
            health_status = JobHealthStatus(
                status="healthy",
                message="Serviço de vagas funcionando normalmente"
            )
            
            return health_status.to_dict()
            
        except Exception as e:
            logger.error(f"Erro no health check: {str(e)}")
            
            health_status = JobHealthStatus(
                status="unhealthy",
                message="Erro no serviço de vagas",
                error=str(e)
            )
            
            return health_status.to_dict()
    
    def _apply_filters(self, jobs: List[Job], request: JobSearchRequest) -> List[Job]:
        """
        Aplica filtros adicionais às vagas
        
        Args:
            jobs: Lista de vagas
            request: Requisição com filtros
            
        Returns:
            Lista de vagas filtrada
        """
        filtered_jobs = jobs
        
        # Filtrar por nível de experiência
        if request.experience_level:
            filtered_jobs = [
                job for job in filtered_jobs 
                if job.experience_level and job.experience_level.lower() == request.experience_level.lower()
            ]
        
        # Filtrar por tipo de contratação
        if request.job_type:
            filtered_jobs = [
                job for job in filtered_jobs 
                if job.job_type and job.job_type.lower() == request.job_type.lower()
            ]
        
        # Filtrar por localização (se especificada)
        if request.location:
            filtered_jobs = [
                job for job in filtered_jobs 
                if job.location and request.location.lower() in job.location.lower()
            ]
        
        return filtered_jobs
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Converte string de data para datetime
        
        Args:
            date_str: String com a data
            
        Returns:
            Objeto datetime ou None se inválido
        """
        if not date_str:
            return None
        
        try:
            # Tentar diferentes formatos de data
            formats = [
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            logger.warning(f"Formato de data não reconhecido: {date_str}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao parsear data {date_str}: {str(e)}")
            return None
    
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
