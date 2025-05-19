import pandas as pd
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus
import logging

def process_healthcare_provider(hcp_name, max_links=8):
    """
    A global function that processes a healthcare provider name to extract relevant information,
    specifically focusing on UAE hospitals and healthcare providers.
    
    Args:
        hcp_name (str): Name of the healthcare provider
        max_links (int, optional): Maximum number of links to scrape. Defaults to 8.
    
    Returns:
        dict: A dictionary containing the extracted information about the healthcare provider
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('healthcare_provider')
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    
    # Internal function to search using DuckDuckGo with rate limit handling
    def search_google_duckduckgo(query, max_results=10, max_retries=3):
        # Add UAE focus to the query if not already present
        if not any(keyword in query.lower() for keyword in ['uae', 'dubai', 'abu dhabi', 'sharjah']):
            query = f"{query} UAE hospital"
        
        logger.info(f"Searching for: {query}")
        
        for retry in range(max_retries):
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=max_results))
                    
                # If we got results, filter them to prioritize UAE content
                if results:
                    # Filter for UAE-related content
                    uae_keywords = ['uae', 'dubai', 'abu dhabi', 'sharjah', 'ajman', 
                                   'ras al khaimah', 'umm al quwain', 'fujairah', 
                                   'emirates', 'دبي', 'أبوظبي', 'الإمارات']
                    
                    filtered_results = []
                    for r in results:
                        # Skip non-string results (shouldn't happen, but just in case)
                        if not isinstance(r, str) and not hasattr(r, 'lower'):
                            continue
                            
                        # Check if result is related to UAE
                        text = str(r).lower()
                        if any(keyword in text for keyword in uae_keywords):
                            filtered_results.append(r)
                    
                    # If we have UAE results, return them, otherwise return original results
                    return filtered_results[:max_results] if filtered_results else results[:max_results]
                return []  # Return empty list if no results
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Search error (attempt {retry+1}/{max_retries}): {error_msg}")
                
                if "Ratelimit" in error_msg:
                    # Exponential backoff with jitter for rate limits
                    wait_time = (2 ** retry) + random.uniform(1, 3)
                    logger.info(f"Rate limited. Waiting {wait_time:.2f} seconds before retry")
                    time.sleep(wait_time)
                else:
                    # For other errors, wait a shorter time
                    time.sleep(random.uniform(1, 2))
        
        # If we've exhausted all retries, use a backup approach
        logger.warning("All search retries failed, using fallback approach")
        return fallback_search(query, max_results)
    
    # Fallback search function when DuckDuckGo fails
    def fallback_search(query, max_results=10):
        # Simple approach: just return the query as a single result
        # In a production system, you might integrate an alternative search API here
        logger.info("Using fallback search mechanism")
        return [f"Unable to search for '{query}' due to rate limits. Please try manually searching for {hcp_name} in UAE."]
    
    # Internal function to scrape website content with retry mechanism
    def scrape_contact_info(url, max_retries=3):
        for retry in range(max_retries):
            try:
                # Randomize user agent to avoid detection
                user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
                ]
                current_headers = HEADERS.copy()
                current_headers["User-Agent"] = random.choice(user_agents)
                
                res = requests.get(url, timeout=15, headers=current_headers)
                
                # Only proceed if status code is successful
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    
                    # Extract meta description for additional context
                    meta_desc = ""
                    meta_tag = soup.find("meta", attrs={"name": "description"})
                    if meta_tag and meta_tag.get("content"):
                        meta_desc = f"META DESCRIPTION: {meta_tag.get('content')}\n\n"
                    
                    # Get contact information sections first, if possible
                    contact_sections = soup.find_all(["div", "section", "p"], 
                                                  class_=lambda c: c and any(term in str(c).lower() 
                                                  for term in ["contact", "location", "address", "about"]))
                    
                    contact_text = ""
                    for section in contact_sections:
                        contact_text += section.get_text(" ", strip=True) + "\n"
                    
                    # Get the main page text as well
                    main_text = soup.get_text(" ", strip=True)
                    
                    # Combine, with priority to contact sections
                    combined_text = meta_desc + contact_text + "\n" + main_text
                    
                    # Limit output size but prioritize the beginning which often has important info
                    return combined_text[:3000]
                
                # If access denied or other client error (except 429), don't retry
                elif 400 <= res.status_code < 500 and res.status_code != 429:
                    logger.warning(f"Client error {res.status_code} accessing {url}")
                    return ""
                
                # For server errors or rate limits, retry with backoff
                else:
                    wait_time = (2 ** retry) + random.uniform(0.5, 1.5)
                    logger.warning(f"HTTP error {res.status_code}. Waiting {wait_time:.2f}s before retry")
                    time.sleep(wait_time)
            
            except Exception as e:
                logger.warning(f"Scraping error (attempt {retry+1}/{max_retries}): {str(e)}")
                if retry < max_retries - 1:
                    time.sleep((2 ** retry) + random.uniform(0.5, 1.5))
        
        return ""  # Return empty string if all attempts fail
    
    # Internal function to communicate with the AI API with retry
    def ask_gpt(prompt, max_retries=3):
        for retry in range(max_retries):
            try:
                encoded_prompt = quote_plus(prompt)
                urlapi = f"https://a.picoapps.xyz/ask-ai?prompt={encoded_prompt}"
                
                # Add a random delay between requests
                if retry > 0:
                    delay = (2 ** retry) + random.uniform(0.5, 2.0)
                    time.sleep(delay)
                
                response = requests.get(urlapi, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "{}")
                else:
                    logger.warning(f"API request failed: {response.status_code}")
                    # Don't immediately retry for client errors
                    if 400 <= response.status_code < 500 and response.status_code != 429:
                        return "{}"
            except Exception as e:
                logger.warning(f"API call failed (attempt {retry+1}/{max_retries}): {e}")
                
        return "{}"  # Return empty JSON if all attempts fail
    
    # Internal function to search for relevant links
    def deep_search_links(hcp_name, max_links=8):
        all_results = []
        
        # UAE-focused search queries
        queries = [
            f"{hcp_name} hospital UAE",
            f"{hcp_name} clinic address UAE",
            f"{hcp_name} medical center UAE",
            f"{hcp_name} healthcare UAE",
            # Add more specific emirate searches if needed
            f"{hcp_name} Dubai healthcare",
            f"{hcp_name} Abu Dhabi medical",
        ]
        
        # Shuffle queries to avoid predictable patterns
        random.shuffle(queries)
        
        # Limit to first 4 queries to avoid rate limits
        for query in queries[:4]:
            try:
                # Add delay between searches to reduce rate limiting
                if all_results:  # If not the first search
                    time.sleep(random.uniform(2, 4))
                
                results = search_google_duckduckgo(query, max_results=8)
                if results:
                    logger.info(f"Found {len(results)} results for: {query}")
                    all_results.extend(results)
                    # If we have enough results, stop searching
                    if len(all_results) >= max_links * 3:  # Get 3x desired to allow for filtering
                        break
            except Exception as e:
                logger.error(f"Error searching for {query}: {e}")
        
        # Process URLs from the results
        urls_to_scrape = []
        seen_urls = set()
        
        for result in all_results:
            # Handle both string results and dictionary results
            if isinstance(result, dict) and "href" in result:
                url = result.get("href")
                title = result.get("title", "")
            elif isinstance(result, str) and ("http://" in result or "https://" in result):
                # Extract URL from text result if possible
                parts = result.split(" - ")
                url = next((part for part in parts if part.startswith("http")), None)
                title = parts[0] if len(parts) > 0 else ""
            else:
                continue
                
            # Skip if URL is None or already seen
            if not url or url in seen_urls:
                continue
                
            # Skip social media or video platforms that are unlikely to have useful info
            if any(platform in url.lower() for platform in ["youtube.com", "facebook.com", "twitter.com", 
                                                         "instagram.com", "tiktok.com"]):
                continue
                
            seen_urls.add(url)
            urls_to_scrape.append({"url": url, "title": title})
            
            # Stop if we have enough unique URLs
            if len(urls_to_scrape) >= max_links:
                break
        
        # Scrape content from the URLs
        scraped_content = []
        
        # Use a smaller thread pool to avoid overwhelming the target servers
        with ThreadPoolExecutor(max_workers=3) as executor:
            def scrape_url(item):
                url = item["url"]
                title = item["title"]
                try:
                    content = scrape_contact_info(url)
                    if content:
                        logger.info(f"Successfully scraped {url}")
                        return {"url": url, "title": title, "content": content}
                    else:
                        logger.warning(f"No content retrieved from {url}")
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                return None
            
            # Schedule all scraping tasks
            scrape_tasks = [executor.submit(scrape_url, item) for item in urls_to_scrape[:max_links]]
            
            # Process results as they complete
            for task in scrape_tasks:
                try:
                    result = task.result()
                    if result:
                        scraped_content.append(result)
                except Exception as e:
                    logger.error(f"Error in scrape task: {e}")
        
        return scraped_content
    
    # Internal function to analyze a single link
    def analyze_individual_link(hcp_name, link_data):
        prompt = f"""
        You are an expert at extracting healthcare provider data from web content, with specific focus on UAE hospitals.
        
        From the following web content about {hcp_name}, extract these fields if present:
        - HCP Name (exact official name)
        - Status (e.g. Hospital, Clinic, Rehabilitation Center)
        - Address (full postal address in UAE)
        - Zone/Area (specific healthcare zone, medical district, or neighborhood in UAE)
        - Emirate (Dubai, Abu Dhabi, Sharjah, etc.)
        - Contact Person (CEO / MD / Director names and titles)
        - Website URL (official website)
        - Phone (main contact number)

        Source: {link_data['url']}
        Title: {link_data['title']}
        
        Content: {link_data['content'][:3500]}

        Return ONLY a JSON object with these fields, nothing else. If information is not found, use empty string.
        """
        result = ask_gpt(prompt)
        logger.info(f"Analyzed content from {link_data['url']}")
        return result
    
    # Internal function to extract and consolidate information from multiple links
    def extract_info_from_links(hcp_name, scraped_links):
        if not scraped_links:
            logger.warning("No scraped links available for analysis")
            return "{}"
            
        link_analyses = []
        
        for link in scraped_links:
            try:
                analysis_json = analyze_individual_link(hcp_name, link)
                try:
                    analysis = json.loads(analysis_json)
                    analysis["source"] = link["url"]
                    link_analyses.append(analysis)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from {link['url']}")
                    # Try to salvage partial information
                    if isinstance(analysis_json, str) and len(analysis_json) > 5:
                        # Add as text for potential manual extraction
                        link_analyses.append({
                            "source": link["url"], 
                            "partial_text": analysis_json[:500],
                            "error": "Invalid JSON format"
                        })
                
                # Add delay between API calls
                time.sleep(random.uniform(1.0, 2.0))
                
            except Exception as e:
                logger.error(f"Error analyzing link {link['url']}: {str(e)}")
        
        if not link_analyses:
            logger.warning("No valid analyses produced from any links")
            return "{}"
            
        urls = "\n".join([f"- {link['url']}" for link in scraped_links])
        
        # Limit the JSON data size to avoid overloading the API
        cleaned_analyses = []
        for analysis in link_analyses:
            # Create a copy without potentially large text fields
            clean_analysis = {k: v for k, v in analysis.items() 
                             if k != "partial_text" or len(str(v)) < 100}
            cleaned_analyses.append(clean_analysis)
        
        sources_data = json.dumps(cleaned_analyses, indent=2)
        
        aggregate_prompt = f"""
        You are an expert data analyst specializing in UAE healthcare provider information.

        Below is data extracted from {len(link_analyses)} different sources about {hcp_name} in the UAE.
        Your job is to analyze all sources and create the most accurate, complete profile.

        When sources disagree:
        1. Prefer information from official UAE government or healthcare authority sources
        2. Look for consistency across multiple sources
        3. Choose the most specific and detailed information

        Sources analyzed:
        {urls}

        Source data:
        {sources_data}

        Create a final, accurate profile with these fields:
        - HCP Name (the most accurate, complete version)
        - Status (e.g. Hospital, Clinic, Rehabilitation Center)
        - Address (most complete postal address in UAE)
        - Zone/Area (specific healthcare zone, medical district, or neighborhood in UAE)
        - Emirate (Dubai, Abu Dhabi, Sharjah, etc.)
        - Contact Person (CEO/Director's name and title)
        - Website URL (official website)
        - Phone (main contact number)

        Return ONLY a valid JSON object with exactly these fields.
        """
        final_result = ask_gpt(aggregate_prompt)
        return final_result
    
    # Main execution flow
    logger.info(f"Starting search for healthcare provider: {hcp_name}")
    
    # First try with direct search
    scraped_links = deep_search_links(hcp_name, max_links)
    
    # If insufficient results, try a more general search
    if len(scraped_links) < 3:
        logger.info(f"Insufficient results ({len(scraped_links)}), trying more general search")
        # Try with variations or more general terms
        alternative_name = hcp_name.replace("Center", "Centre").replace("Hospital", "Medical")
        additional_links = deep_search_links(alternative_name, max_links - len(scraped_links))
        scraped_links.extend(additional_links)
    
    # Still no results, create empty result
    if not scraped_links:
        logger.warning(f"No information found for {hcp_name}")
        return {
            "HCP Name": hcp_name,
            "Status": "Not Found",
            "Address": "",
            "Zone/Area": "",
            "Emirate": "",
            "Contact Person": "",
            "Phone": "",
            "URL Website": "",
        }
    
    logger.info(f"Extracted information from {len(scraped_links)} sources")
    extracted_data_json = extract_info_from_links(hcp_name, scraped_links)
    
    try:
        extracted_data = json.loads(extracted_data_json)
        logger.info(f"Successfully processed data for {hcp_name}")
    except:
        logger.error(f"Failed to parse final JSON data for {hcp_name}")
        extracted_data = {}
    
    # Return the extracted data with fallback to original name
    return {
        "HCP Name": extracted_data.get("HCP Name", hcp_name),
        "Status": extracted_data.get("Status", ""),
        "Address": extracted_data.get("Address", ""),
        "Zone/Area": extracted_data.get("Zone/Area", ""),
        "Emirate": extracted_data.get("Emirate", ""),
        "Contact Person": extracted_data.get("Contact Person", ""),
        "Phone": extracted_data.get("Phone", ""),
        "URL Website": extracted_data.get("Website URL", "")
    }