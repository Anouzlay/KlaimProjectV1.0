import streamlit as st
import requests
from bs4 import BeautifulSoup
import logging
import time
import re
import pdfplumber
import io
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium import webdriver
import cloudscraper
# from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
from typing import Any


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def advanced_scrape_website(url: str, selector: str = None, wait_time: int = 0, javascript: bool = False) -> str:
    st.write(f"Scraping: {url}")
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    headers = {
        'User-Agent': user_agents[0],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    
    def get_domain(url):
        parsed_uri = urlparse(url)
        return '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    
    def clean_text(text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = '\n'.join(line for line in text.splitlines() if line.strip())
        return text
    
    def extract_with_beautifulsoup(html_content, target_selector=None):
        soup = BeautifulSoup(html_content, 'html.parser')

        try:
            import lxml
            soup = BeautifulSoup(html_content, 'lxml')
        except ImportError:
            pass
        for element in soup.select('script, style, meta, link, noscript, header, footer, nav, iframe, svg'):
            element.decompose()
        if target_selector:
            selected_elements = soup.select(target_selector)
            if selected_elements:
                content = '\n'.join(element.get_text(separator='\n', strip=True) for element in selected_elements)
                return content
        for content_selector in ['main', '#content', '.content', 'article', '.article', '.post', '#main', '.main-content', '.post-content']:
            main_content = soup.select(content_selector)
            if main_content:
                content = '\n'.join(element.get_text(separator='\n', strip=True) for element in main_content)
                if len(content) > 250:  
                    return content
        
        return soup.get_text(separator='\n', strip=True)
    
    def extract_pdf_content(pdf_content):
        try:
            import PyPDF2
            
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
            
            return clean_text(text)
        except ImportError:
            st.warning("PyPDF2 is not installed. Install it with 'pip install PyPDF2'")
            return "ERROR: PyPDF2 library is required to extract PDF content. Install it with 'pip install PyPDF2'"
        except Exception as e:
            logger.error(f"Error extracting PDF content: {str(e)}")
            try:

                
                pdf_file = io.BytesIO(pdf_content)
                with pdfplumber.open(pdf_file) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + "\n\n"
                
                return clean_text(text)
            except ImportError:
                st.warning("pdfplumber is not installed. Install it with 'pip install pdfplumber'")
                return f"ERROR: Failed to extract PDF content: {str(e)}. Try installing pdfplumber with 'pip install pdfplumber'"
            except Exception as e2:
                logger.error(f"Error extracting PDF with pdfplumber: {str(e2)}")
                return f"ERROR: Failed to extract PDF content with both PyPDF2 and pdfplumber: {str(e)}, {str(e2)}"
    
    def is_pdf_url(url):
        return url.lower().endswith('.pdf') or '/pdf/' in url.lower()
    
    def try_requests_method():
        for i, agent in enumerate(user_agents):
            try:
                current_headers = headers.copy()
                current_headers['User-Agent'] = agent
                current_headers['Referer'] = get_domain(url)
                
                session = requests.Session()
                response = session.get(
                    url, 
                    headers=current_headers, 
                    timeout=15,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # Check if the response is a PDF
                content_type = response.headers.get('Content-Type', '').lower()
                if 'application/pdf' in content_type or is_pdf_url(url):
                    st.write("Detected PDF content, extracting text...")
                    return extract_pdf_content(response.content)
                
                if 'application/json' in content_type:
                    return response.json()
                
                return extract_with_beautifulsoup(response.text, selector)
            except Exception as e:
                logger.info(f"Attempt {i+1} with regular requests failed: {str(e)}")
                if i == len(user_agents) - 1:
                    raise e
                continue
    
    def try_cloudscraper_method():
        try:
            scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
            response = scraper.get(url)
            
            # Check if the response is a PDF
            content_type = response.headers.get('Content-Type', '').lower()
            if 'application/pdf' in content_type or is_pdf_url(url):
                st.write("Detected PDF content (CloudScraper), extracting text...")
                return extract_pdf_content(response.content)
                
            return extract_with_beautifulsoup(response.text, selector)
        except ImportError:
            logger.warning("CloudScraper not installed, skipping this method")
            return None
        except Exception as e:
            logger.info(f"CloudScraper method failed: {str(e)}")
            return None
    
    # def try_selenium_method():
    #     if not javascript:
    #         return None
            
    #     try:
    #         options = Options()
    #         options.add_argument("--headless")
    #         options.add_argument("--no-sandbox")
    #         options.add_argument("--disable-dev-shm-usage")
    #         options.add_argument(f"user-agent={user_agents[0]}")
            
    #         # Add PDF handling with Selenium
    #         if is_pdf_url(url):
    #             st.write("PDF URL detected, using requests method instead of Selenium")
    #             try:
    #                 response = requests.get(url, headers=headers, timeout=15)
    #                 response.raise_for_status()
    #                 return extract_pdf_content(response.content)
    #             except Exception as e:
    #                 logger.error(f"Error downloading PDF with requests: {str(e)}")
    #                 return None
            
    #         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    #         driver.get(url)
            
    #         if wait_time > 0:
    #             time.sleep(wait_time)
            
    #         # Check if the page redirected to a PDF
    #         current_url = driver.current_url
    #         if is_pdf_url(current_url):
    #             st.write("Redirected to PDF, downloading and extracting...")
    #             driver.quit()
    #             response = requests.get(current_url, headers=headers, timeout=15)
    #             response.raise_for_status()
    #             return extract_pdf_content(response.content)
            
    #         page_source = driver.page_source
    #         driver.quit()
            
    #         return extract_with_beautifulsoup(page_source, selector)
    #     except ImportError:
    #         logger.warning("Selenium not installed, skipping this method")
    #         return None
    #     except Exception as e:
    #         logger.info(f"Selenium method failed: {str(e)}")
    #         return None
    
    try:
        # Special case for PDF URLs
        if is_pdf_url(url):
            st.write("PDF URL detected, using direct PDF extraction")
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                pdf_text = extract_pdf_content(response.content)
                if pdf_text:
                    st.write(f"Successfully extracted {len(pdf_text)} characters from PDF")
                    return pdf_text
            except Exception as e:
                logger.error(f"Error downloading PDF directly: {str(e)}")
                # Continue with other methods if direct PDF download fails
        
        content = None
        try:
            content = try_requests_method()
            if content:
                st.write("Successfully scraped using standard requests")
        except Exception as e:
            logger.info(f"Standard requests method failed: {str(e)}")
        if not content:
            content = try_cloudscraper_method()
            if content:
                st.write("Successfully scraped using CloudScraper")

        # if not content and javascript:
        #     content = try_selenium_method()
        #     if content:
        #         st.write("Successfully scraped using Selenium")

        if not content:
            return "Failed to scrape the website with all available methods."
        
        if isinstance(content, dict):
            import json
            text_content = json.dumps(content, indent=2)
        else:
            text_content = clean_text(content)
        if len(text_content) > 100000:
            text_content = text_content[:100000] + "\n\n[Content truncated due to length...]"
        
        st.write(f"Successfully scraped {len(text_content)} characters")
        return text_content
        
    except Exception as e:
        st.error(f"Error scraping {url}: {str(e)}")
        return f"Error scraping this URL: {str(e)}"
    


print(advanced_scrape_website("https://www.ehs.gov.ae/en/services/health-care-facilities"))
