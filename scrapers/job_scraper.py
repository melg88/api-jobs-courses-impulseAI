import logging
import json
import time
import requests
import urllib.parse
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class JobScraper:
    """
    Realiza o scraping de vagas no LinkedIn usando a biblioteca 'requests'.
    A estrutura dos métodos foi organizada para maior clareza, mantendo
    a compatibilidade com o JobService.
    """
    def __init__(self):
        """
        Inicializa o scraper, carregando configurações e headers de um arquivo.
        """

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _get_soup(self, url: str, retries: int = 3, delay: int = 2) -> Optional[BeautifulSoup]:
        """
        Acessa uma URL usando 'requests' e retorna um objeto BeautifulSoup.
        """
        for i in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()  # Lança um erro para status HTTP 4xx/5xx
                return BeautifulSoup(response.content, 'html.parser')
            except requests.exceptions.RequestException as e:
                logger.warning(f"Erro na requisição para {url} (tentativa {i+1}/{retries}): {e}")
                time.sleep(delay)
        logger.error(f"Falha ao obter a URL após {retries} tentativas: {url}")
        return None

    def _parse_job_cards(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrai as informações básicas dos cards de vagas a partir do soup."""
        job_list = []
        divs = soup.find_all('div', class_='base-card')
        
        for item in divs:
            info_div = item.find('div', class_='base-search-card__info')
            if not info_div:
                continue
            
            entity_urn = item.get('data-entity-urn', '')
            job_id = entity_urn.split(':')[-1] if entity_urn else ''
            
            date_tag = info_div.find('time', class_='job-search-card__listdate') or info_div.find('time', class_='job-search-card__listdate--new')
            company_tag = info_div.find('a', class_='hidden-nested-link')
            location_tag = info_div.find('span', class_='job-search-card__location')

            job = {
                'id': job_id,
                'title': info_div.find('h3').text.strip(),
                'company': company_tag.text.strip() if company_tag else '',
                'location': location_tag.text.strip() if location_tag else '',
                'posted_date': date_tag['datetime'] if date_tag and date_tag.has_attr('datetime') else '',
                'url': f'https://www.linkedin.com/jobs/view/{job_id}/' if job_id else '',
            }
            job_list.append(job)
        return job_list

    def _parse_job_details(self, soup: BeautifulSoup) -> str:
        """Extrai a descrição completa e formatada de uma vaga."""
        div = soup.find('div', class_='description__text')
        if not div:
            return "Descrição não encontrada."
        return div.get_text(separator='\n').strip()

    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> List[Dict]:
        """
        Busca vagas no LinkedIn, orquestrando a obtenção e o parsing dos dados.
        """
        encoded_keywords = urllib.parse.quote_plus(query)
        encoded_location = urllib.parse.quote_plus(location)
        
        all_job_cards = []
        pages_to_scrape = (limit // 10) + 2
        
        logger.info(f"Iniciando busca por '{query}' em '{location}'. Limite: {limit} vagas.")

        for page in range(max_pages_to_scrape):
            # Condição de parada: se já atingimos o limite, não precisamos buscar mais páginas.
            if len(all_job_cards) >= limit:
            break
        
            start_index = page * 25 # O 'start' do LinkedIn ainda é baseado em 25
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={encoded_keywords}&location={encoded_location}&start={start_index}"
        
            logger.info(f"Buscando página {page + 1}...")
            soup = self._get_soup(url)

            if not soup:
                continue

            cards_on_page = self._parse_job_cards(soup)
            # Condição de parada: se a página não retornou nenhuma vaga, paramos a busca.
            if not cards_on_page:
                logger.info("Não foram encontradas mais vagas para esta busca.")
                break
        
            all_job_cards.extend(cards_on_page)
            
        # Processa os detalhes de cada vaga até atingir o limite
        final_jobs = []
        # Remove duplicatas por ID para evitar requisições repetidas
        unique_cards = {card['id']: card for card in all_job_cards}.values()

        for i, card in enumerate(unique_cards):
            if i >= limit:
                break

            logger.info(f"Processando detalhes da vaga {i + 1}/{limit}: {card['title']}")
            details_soup = self._get_soup(card['url'])
            description = self._parse_job_details(details_soup) if details_soup else "Falha ao obter descrição."
            
            job_data = {
                'id': card.get('id', f'job_{i}'),
                'title': card.get('title', ''),
                'company': card.get('company', ''),
                'location': card.get('location', ''),
                'description': description,
                'posted_date': card.get('posted_date', ''),
                'url': card.get('url', ''),
                'source': 'linkedin'
            }
            final_jobs.append(job_data)
        
        logger.info(f"Busca finalizada. Encontradas e processadas {len(final_jobs)} vagas.")
        return final_jobs

    def close(self):
        """
        Método mantido para compatibilidade com o JobService.
        Não há recursos para fechar ao usar 'requests'.
        """
        pass

    def __del__(self):
        """Destrutor para chamar o close, mantendo a compatibilidade."""
        self.close()