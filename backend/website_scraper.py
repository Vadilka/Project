import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
import re

logger = logging.getLogger(__name__)

class SANScraper:
    def __init__(self):
        self.base_url = "https://san.edu.pl"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep Polish characters
        text = re.sub(r'[^\w\s.,!?ąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]', '', text)
        return text.strip()

    def get_page_content(self, url: str) -> str:
        """Get page content with error handling"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return ""

    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page"""
        # Remove navigation, footer, and other non-content elements
        for element in soup.find_all(['nav', 'footer', 'header', 'script', 'style']):
            element.decompose()
        
        # Get text from main content
        text = soup.get_text(separator=' ', strip=True)
        return self.clean_text(text)

    def get_study_programs(self) -> List[Dict]:
        """Get information about study programs"""
        programs = []
        try:
            # Get main page
            main_page = self.get_page_content(self.base_url)
            soup = BeautifulSoup(main_page, 'html.parser')
            
            # Find study program links
            program_links = soup.find_all('a', href=re.compile(r'/studia/'))
            
            for link in program_links:
                program_url = self.base_url + link['href'] if link['href'].startswith('/') else link['href']
                program_page = self.get_page_content(program_url)
                if program_page:
                    program_soup = BeautifulSoup(program_page, 'html.parser')
                    content = self.extract_main_content(program_soup)
                    if content:
                        programs.append({
                            'title': link.text.strip(),
                            'url': program_url,
                            'content': content
                        })
            
        except Exception as e:
            logger.error(f"Error getting study programs: {str(e)}")
        
        return programs

    def get_general_info(self) -> List[Dict]:
        """Get general information about the university"""
        info = []
        try:
            # Get main page
            main_page = self.get_page_content(self.base_url)
            soup = BeautifulSoup(main_page, 'html.parser')
            
            # Extract main sections
            sections = soup.find_all(['section', 'article'])
            for section in sections:
                title = section.find(['h1', 'h2', 'h3'])
                if title:
                    content = self.extract_main_content(section)
                    if content:
                        info.append({
                            'title': title.text.strip(),
                            'content': content
                        })
            
        except Exception as e:
            logger.error(f"Error getting general info: {str(e)}")
        
        return info

    def get_all_content(self) -> List[Dict]:
        """Get all content from the website"""
        all_content = []
        
        # Get study programs
        programs = self.get_study_programs()
        all_content.extend(programs)
        
        # Get general information
        general_info = self.get_general_info()
        all_content.extend(general_info)
        
        return all_content

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test scraper
    scraper = SANScraper()
    content = scraper.get_all_content()
    print(f"Scraped {len(content)} content items") 