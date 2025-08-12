import os
import time
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from linkedin_scraper import JobSearch, actions

logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self):
        self.driver = None
        self.email = os.environ.get('LINKEDIN_EMAIL', '')
        self.password = os.environ.get('LINKEDIN_PASSWORD', '')
        self.is_logged_in = False
        
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
    
    def _login(self):
        """Faz login no LinkedIn"""
        if not self.email or not self.password:
            logger.warning("Credenciais do LinkedIn não configuradas")
            return False
            
        try:
            if not self.driver:
                if not self._setup_driver():
                    return False
            
            actions.login(self.driver, self.email, self.password)
            self.is_logged_in = True
            logger.info("Login no LinkedIn realizado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro no login: {str(e)}")
            return False
    
    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> List[Dict]:
        """
        Busca vagas no LinkedIn
        
        Args:
            query: Termo de busca
            location: Localização (opcional)
            limit: Número máximo de resultados
            
        Returns:
            Lista de vagas encontradas
        """
        try:
            if not self.driver:
                if not self._setup_driver():
                    return []
            
            if not self.is_logged_in:
                if not self._login():
                    logger.warning("Continuando sem login - resultados limitados")
            
            # Criar instância do JobSearch
            job_search = JobSearch(
                driver=self.driver, 
                close_on_complete=False, 
                scrape=False
            )
            
            # Realizar busca
            search_query = query
            if location:
                search_query += f" {location}"
            
            job_listings = job_search.search(search_query)
            
            # Processar resultados
            jobs = []
            for i, job in enumerate(job_listings):
                if i >= limit:
                    break
                    
                try:
                    job_data = {
                        'id': getattr(job, 'job_id', f'job_{i}'),
                        'title': getattr(job, 'title', ''),
                        'company': getattr(job, 'company', ''),
                        'location': getattr(job, 'location', ''),
                        'description': getattr(job, 'description', ''),
                        'posted_date': getattr(job, 'posted_date', ''),
                        'applicants': getattr(job, 'applicants', ''),
                        'url': getattr(job, 'job_url', ''),
                        'source': 'linkedin'
                    }
                    print(job_data)
                    jobs.append(job_data)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar vaga {i}: {str(e)}")
                    continue
            
            logger.info(f"Encontradas {len(jobs)} vagas para '{query}'")
            return jobs
            
        except Exception as e:
            logger.error(f"Erro na busca de vagas: {str(e)}")
            return []
    
    def close(self):
        """Fecha o driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Erro ao fechar driver: {str(e)}")
            finally:
                self.driver = None
                self.is_logged_in = False
    
    def __del__(self):
        """Destrutor para garantir que o driver seja fechado"""
        self.close()
