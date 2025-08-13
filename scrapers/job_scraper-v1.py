import requests
import json
import time as tm
from typing import List, Dict
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from itertools import groupby

class LinkedInScraper:
    """
    Realiza o scraping de vagas no LinkedIn com base em parâmetros de busca,
    retornando uma lista de vagas pronta para ser usada em uma API.
    """

    def __init__(self, config_path: str = 'config.json'):
        """
        Inicializa o scraper carregando o arquivo de configuração.
        """
        self.config = self._load_config(config_path)
        self.headers = self.config.get('headers', {})

    def _load_config(self, file_name: str) -> Dict:
        """Carrega o arquivo de configuração JSON."""
        with open(file_name) as f:
            return json.load(f)

    def _get_with_retry(self, url: str, retries: int = 3, delay: int = 2) -> BeautifulSoup:
        """Faz uma requisição GET com tentativas e um delay, retornando um objeto BeautifulSoup."""
        for i in range(retries):
            try:
                r = requests.get(url, headers=self.headers, timeout=10)
                r.raise_for_status()  # Lança um erro para status 4xx/5xx
                return BeautifulSoup(r.content, 'html.parser')
            except requests.exceptions.RequestException as e:
                print(f"Erro na requisição para {url}: {e}. Tentando novamente em {delay}s...")
                tm.sleep(delay)
        print(f"Falha ao obter a URL após {retries} tentativas: {url}")
        return None

    def _transform_card(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrai as informações básicas das vagas (cards) da página de resultados."""
        job_list = []
        divs = soup.find_all('div', class_='base-search-card__info')
        for item in divs:
            title = item.find('h3').text.strip()
            company = item.find('a', class_='hidden-nested-link')
            location = item.find('span', class_='job-search-card__location')
            date_tag = item.find('time', class_='job-search-card__listdate') or item.find('time', class_='job-search-card__listdate--new')
            
            parent_div = item.parent
            entity_urn = parent_div.get('data-entity-urn', '')
            job_posting_id = entity_urn.split(':')[-1]
            job_url = f'https://www.linkedin.com/jobs/view/{job_posting_id}/'

            job = {
                'title': title,
                'company': company.text.strip() if company else '',
                'location': location.text.strip() if location else '',
                'date': date_tag['datetime'] if date_tag else '',
                'job_url': job_url
            }
            job_list.append(job)
        return job_list

    def _transform_job_description(self, soup: BeautifulSoup) -> str:
        """Extrai e limpa a descrição completa de uma vaga a partir de sua página individual."""
        div = soup.find('div', class_='description__text')
        if not div:
            return "Descrição não encontrada."
        return div.get_text(separator='\n').strip()

    def _remove_duplicates(self, job_list: List[Dict]) -> List[Dict]:
        """Remove vagas duplicadas com base no título e na empresa."""
        job_list.sort(key=lambda x: (x['title'], x['company']))
        return [next(g) for k, g in groupby(job_list, key=lambda x: (x['title'], x['company']))]

    def _filter_jobs(self, job_list: List[Dict]) -> List[Dict]:
        """Filtra a lista de vagas com base nas palavras-chave e linguagem definidas no config."""
        
        def safe_detect(text):
            try:
                return detect(text)
            except LangDetectException:
                return 'en' # Retorna um padrão se a detecção falhar

        filters = self.config.get('filters', {})
        desc_words = filters.get('desc_words_exclude', [])
        title_exclude = filters.get('title_exclude', [])
        languages = filters.get('languages', [])
        
        filtered_list = [job for job in job_list if not any(word.lower() in job['job_description'].lower() for word in desc_words)]
        filtered_list = [job for job in filtered_list if not any(word.lower() in job['title'].lower() for word in title_exclude)]
        if languages:
            filtered_list = [job for job in filtered_list if safe_detect(job['job_description']) in languages]

        return filtered_list

    def scrape_jobs(self, keywords: str, location: str, limit: int = 25) -> List[Dict]:
        """
        Método principal que orquestra o processo de scraping.
        
        Args:
            keywords (str): Palavras-chave da vaga (ex: "Engenheiro de Software").
            location (str): Localização da vaga (ex: "Recife, Pernambuco").
            limit (int): Número máximo de vagas a serem retornadas.

        Returns:
            List[Dict]: Uma lista de dicionários, cada um representando uma vaga.
        """
        print(f"Iniciando busca por '{keywords}' em '{location}'...")
        encoded_keywords = quote_plus(keywords)
        encoded_location = quote_plus(location)
        
        all_job_cards = []
        # O LinkedIn mostra 25 vagas por página
        pages_to_scrape = (limit // 25) + 1

        for page in range(pages_to_scrape):
            start_index = page * 25
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={encoded_keywords}&location={encoded_location}&start={start_index}"
            
            print(f"Buscando página {page + 1}: {url}")
            soup = self._get_with_retry(url)
            if not soup:
                continue

            job_cards = self._transform_card(soup)
            if not job_cards:
                print("Não foram encontradas mais vagas. Encerrando busca.")
                break
            
            all_job_cards.extend(job_cards)

        print(f"Total de {len(all_job_cards)} vagas encontradas inicialmente.")
        
        # Remove duplicatas básicas antes de buscar as descrições
        unique_job_cards = self._remove_duplicates(all_job_cards)
        print(f"Total de {len(unique_job_cards)} vagas únicas.")

        final_job_list = []
        for i, card in enumerate(unique_job_cards):
            if i >= limit:
                break
            
            print(f"Processando vaga {i + 1}/{limit}: {card['title']} at {card['company']}")
            desc_soup = self._get_with_retry(card['job_url'])
            if desc_soup:
                card['job_description'] = self._transform_job_description(desc_soup)
            else:
                card['job_description'] = "Falha ao obter a descrição."
            
            final_job_list.append(card)

        # Filtra a lista final com base nas descrições completas
        filtered_jobs = self._filter_jobs(final_job_list)
        print(f"Busca finalizada. Retornando {len(filtered_jobs)} vagas após a filtragem.")
        
        return filtered_jobs

# --- Exemplo de Como Usar a Classe ---
if __name__ == "__main__":
    try:
        # 1. Instancia o scraper (ele carrega o config.json automaticamente)
        scraper = LinkedInScraper()

        # 2. Chama o método de scraping com os parâmetros desejados
        vagas = scraper.scrape_jobs(keywords="Engenheiro de Dados", location="São Paulo, Brasil", limit=10)

        # 3. Imprime o resultado (em um cenário de API, você faria 'return jsonify(vagas)')
        if vagas:
            print("\n--- VAGAS ENCONTRADAS ---")
            for vaga in vagas:
                print(json.dumps(vaga, indent=2, ensure_ascii=False))
        else:
            print("\nNenhuma vaga encontrada que corresponda aos critérios.")

    except FileNotFoundError:
        print("\nERRO: Arquivo 'config.json' não encontrado. Por favor, crie o arquivo com as configurações necessárias.")
    except Exception as e:
        print(f"\nUm erro inesperado ocorreu: {e}")