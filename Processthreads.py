import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
from tools.serper_search import hospital_info_search
from tools.enhanced_scrape_website import advanced_scrape_website
import types
import streamlit as st

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HospitalDataExtractor:
    def __init__(self, max_threads=10):
        self.max_threads = max_threads
        self.collected_data = {
            'revenue': [],
            'specialties': [],
            'doctors': [],
            'ceo': [],
            'website': [],
            'management': [],
            'insurance': [],
            'phone': [],
            'location': []
        }
        self.lock = threading.Lock()
        self.st = None
    
    def _thread_safe_write(self, message):
        """Thread-safe wrapper for streamlit write to avoid ScriptRunContext errors"""
        # If we're in a thread, just log instead of using streamlit
        logger.info(message)
    
    def _process_info_type(self, hospital_name, info_type):
        logger.info(f"Processing {info_type} for {hospital_name}")
        
        try:
            search_results = hospital_info_search(
                hospital_name, 
                info_type,
                max_results=5
            )
            
            # Map info_type to category
            category_mapping = {
                'NETREVENUEYEARLY': 'revenue',
                'NO_OF_SPECIALTIES': 'specialties', 
                'NOOFDOCTORS': 'doctors',
                'CEO': 'ceo',
                'WEBSITE': 'website',
                'MANAGEMENT_TEAM': 'management',
                'INSURANCE': 'insurance',
                'PHONE': 'phone',
                'ADDRESS': 'location'
            }
            
            category = category_mapping.get(info_type, 'other')
            
            # Step 2: Process each search result
            for result in search_results:
                if 'link' in result and result['link']:
                    try:
                        # Create a patch for advanced_scrape_website to avoid Streamlit calls in threads
                        def patched_scrape_website(url, selector=None, wait_time=0, javascript=False):
                            # Override the st.write calls in advanced_scrape_website

                            original_write = st.write

                            def log_write(*args, **kwargs):
                                message = " ".join([str(arg) for arg in args])
                                logger.info(f"Scraper: {message}")
                                return None
                            
                            # Patch st.write temporarily
                            st.write = log_write
                            st.error = log_write
                            
                            try:
                                content = advanced_scrape_website(url, selector, wait_time, javascript)
                                return content
                            finally:

                                st.write = original_write

                        scraped_content = patched_scrape_website(
                            result['link'],
                            javascript=True if 'javascript' in result['link'].lower() else False
                        )
                        with self.lock:
                            self.collected_data[category].append({
                                "text": scraped_content,
                                "url": result['link'],
                                "metadata": {
                                    'title': result.get('title', ''),
                                    'snippet': result.get('snippet', '')
                                }
                            })
                    
                    except Exception as e:
                        logger.error(f"Error scraping {result['link']}: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {info_type}: {str(e)}")
            return False
    
    def run(self, hospital_name):
        start_time = time.time()
        logger.info(f"Starting parallel data extraction for: {hospital_name}")
        
        info_types = [
            'WEBSITE',           
            'PHONE',             
            'ADDRESS',           
            'CEO',              
            'MANAGEMENT_TEAM',   
            'INSURANCE',         
            'NO_OF_SPECIALTIES', 
            'NOOFDOCTORS',       
            'NETREVENUEYEARLY'   
        ]
        
        # Use a thread pool to process the info types in parallel
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # Submit all tasks to the executor
            futures = [
                executor.submit(self._process_info_type, hospital_name, info_type)
                for info_type in info_types
            ]
            
            # Wait for all tasks to complete
            for future in futures:
                future.result()  # This will also raise any exceptions
        
        end_time = time.time()
        logger.info(f"Data extraction completed in {end_time - start_time:.2f} seconds")
        
        return self.collected_data