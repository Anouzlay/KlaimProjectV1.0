import time
import random
import requests
import json
from urllib.parse import urlparse
import logging
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERPER_API_URL = "https://google.serper.dev/search"

def search_serper(query, max_results=10, max_retries=3 , serper_api):
    if not any(keyword in query.lower() for keyword in ['uae', 'dubai', 'abu dhabi', 'sharjah']):
        query = f"{query} UAE hospital"
        
    logger.info(f"Searching with Serper: {query}")
    if not SERPER_API_KEY:
        logger.error("Serper API key is not set. Set the SERPER_API_KEY environment variable.")
        return {"error": "Serper API key is not set. Set the SERPER_API_KEY environment variable."}
    
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json", 
    }
    
    payload = {
        "q": query,
        "num": max_results,
        "location": "United Arab Emirates",
        "gl": "ae"
    }
    
    for retry in range(max_retries):
        try:
            response = requests.post(
                SERPER_API_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            search_results = response.json()
            
            results = []
            if "organic" in search_results:
                for item in search_results["organic"]:
                    snippet = item.get("snippet", "")
                    title = item.get("title", "")
                    link = item.get("link", "")
                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet
                    })
                
                logger.info(f"Found {len(results)} search results")
                return results
            result_types = [key for key in search_results if key not in ["searchParameters", "timestampUsec"]]
            if result_types:
                logger.warning(f"No organic results found, but found other result types: {result_types}")
                alternative_results = []
                if "knowledgeGraph" in search_results:
                    kg = search_results["knowledgeGraph"]
                    title = kg.get("title", "")
                    link = kg.get("website", "")
                    description = kg.get("description", "")
                    
                    alternative_results.append({
                        "title": title,
                        "link": link,
                        "snippet": description
                    })
                if "peopleAlsoAsk" in search_results:
                    for item in search_results["peopleAlsoAsk"]:
                        question = item.get("question", "")
                        answer = item.get("answer", "")
                        
                        alternative_results.append({
                            "title": question,
                            "link": "",
                            "snippet": answer
                        })

                if alternative_results:
                    logger.info(f"Found {len(alternative_results)} alternative results")
                    return alternative_results
            logger.warning("No search results found in any category")
            return []
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            logger.warning(f"Serper API error (attempt {retry+1}/{max_retries}): {error_msg}")
            
            if "429" in error_msg:
                wait_time = (2 ** retry) + random.uniform(1, 3)
                logger.info(f"Rate limited. Waiting {wait_time:.2f} seconds before retry")
                time.sleep(wait_time)
            else:

                time.sleep(random.uniform(1, 2))
    logger.error(f"Failed to get search results after {max_retries} attempts")
    return {"error": f"Failed to get search results after {max_retries} attempts: {error_msg}"} 

def fallback_search(query, max_results=10):

    logger.info("Using fallback search mechanism")
    return [f"Unable to search for '{query}' due to API limits or errors. Please try manually searching for {query} in UAE."]

def hospital_info_search(hospital_name, info="GENERAL", max_results=10, max_retries=3):

    query = f"{hospital_name} UAE hospital"
    
    info = info.upper()
    
    if info == "NETREVENUEYEARLY":
        query = f"{hospital_name} yearly revenue financial report UAE"
        logger.info(f"Searching for yearly revenue of {hospital_name}")
    
    elif info == "NO_OF_SPECIALTIES":
        query = f"{hospital_name} medical specialties departments services UAE"
        logger.info(f"Searching for number of specialties at {hospital_name}")
    
    elif info == "NOOFDOCTORS":
        query = f"{hospital_name} number of doctors physicians staff UAE"
        logger.info(f"Searching for number of doctors at {hospital_name}")
    
    elif info == "CEO":
        query = f"{hospital_name} CEO director management leadership UAE"
        logger.info(f"Searching for CEO of {hospital_name}")
    
    elif info == "WEBSITE":
        query = f"{hospital_name} official website URL UAE"
        logger.info(f"Searching for official website of {hospital_name}")
    
    elif info == "MANAGEMENT_TEAM":
        query = f"{hospital_name} management team directors board executives UAE"
        logger.info(f"Searching for management team of {hospital_name}")
    
    elif info == "INSURANCE":
        query = f"{hospital_name} insurance accepted coverage providers UAE"
        logger.info(f"Searching for insurance accepted at {hospital_name}")
    
    elif info == "PHONE":
        query = f"{hospital_name} contact phone number UAE"
        logger.info(f"Searching for phone number of {hospital_name}")
    
    else:
        logger.info(f"Performing general search for {hospital_name}")
    
    return search_serper(query, max_results, max_retries)
