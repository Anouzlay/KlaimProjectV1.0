import re
import time
import random
from urllib.parse import urlparse
from typing import Dict, Any, List
from duckduckgo_search import DDGS
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_google_duckduckgo(query, max_results=10, max_retries=3):
    """
    General search function using DuckDuckGo search with UAE focus
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        max_retries: Maximum number of retry attempts
        
    Returns:
        List of search results
    """
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

def fallback_search(query, max_results=10):
    """Fallback search mechanism when main search fails"""
    logger.info("Using fallback search mechanism")
    return [f"Unable to search for '{query}' due to rate limits. Please try manually searching for {query} in UAE."]

def hospital_info_search(hospital_name, info="GENERAL", max_results=10, max_retries=3):
    """
    Unified search function for different types of hospital information
    
    Args:
        hospital_name: Name of the hospital to search for
        info: Type of information to search for:
              - NETREVENUEYEARLY: Annual revenue information
              - NO_OF_SPECIALTIES: Medical specialties and departments
              - NOOFDOCTORS: Number of physicians and medical staff
              - CEO: Chief Executive Officer information
              - WEBSITE: Official website URL
              - MANAGEMENT_TEAM: Directors and executive management
              - INSURANCE: Accepted insurance providers
              - PHONE: Contact phone numbers
              - GENERAL: General hospital information (default)
        max_results: Maximum number of results to return
        max_retries: Maximum number of retry attempts
        
    Returns:
        List of search results about the requested hospital information
    """
    # Default query if info type is not specified
    query = f"{hospital_name} UAE hospital"
    
    # Convert info parameter to uppercase for case-insensitive comparison
    info = info.upper()
    
    # Define search queries based on information type
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
    
    # Use the base search function with the constructed query
    return search_google_duckduckgo(query, max_results, max_retries)
