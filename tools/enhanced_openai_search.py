from typing import Dict, Any, Optional, List
import os 
import time 
import random 
from urllib.parse import urlparse
import re
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
def enhanced_openai_search(
    query: str, 
    num_results: int = 8, 
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    global _search_cache
    
    # Use provided API key or fall back to environment variable
    openai_api_key = api_key or OPENAI_API_KEY
    if not openai_api_key:
        raise ValueError("OpenAI API key is required but not provided")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=openai_api_key)
    
    # Check cache first
    if query in _search_cache:
        print(f"Using cached results for query: {query}")
        return _search_cache[query]
    
    # For comprehensive searches, try to extract all key information in one search
    comprehensive_query = query
    if not ("leadership" in query.lower() and "insurance" in query.lower() and "specialties" in query.lower()):
        comprehensive_query = f"{query} comprehensive information leadership contact address specialties insurance revenue"
    
    results = []
    
    # Define more efficient search categories
    query_categories = {
        "comprehensive": [
            f"{comprehensive_query} official website",
            f"{comprehensive_query} organization profile"
        ]
    }
    
    # Initialize tracking variables
    successful_queries = 0
    failed_queries = 0
    seen_domains = set()
    seen_content_hashes = set()
    target_total_results = min(num_results, 6)  # Limit results to save tokens
    
    print(f"Beginning optimized search for: {query}")
    progress_bar = st.progress(0)
    total_queries = sum(len(queries) for queries in query_categories.values())
    query_index = 0
    
    # Process queries by category
    for category, queries in query_categories.items():
        # Skip category if we already have enough results
        if len(results) >= target_total_results:
            st.success(f"Sufficient results found. Skipping remaining queries.")
            break
            
        st.write(f"Searching {category} information...")
        
        for search_query in queries:
            max_retries = 1
            retry_count = 0
            backoff_time = 2
            
            # Skip if we've reached our target
            if len(results) >= target_total_results:
                break
            
            while retry_count < max_retries:
                try:
                    st.write(f"Searching: {search_query}")
                    
                    # Use OpenAI's web search functionality
                    completion = client.chat.completions.create(
                        model="gpt-4o-mini-search-preview",
                        web_search_options={},
                        messages=[
                            {
                                "role": "user",
                                "content": search_query + " Return all available information including address, contact, leadership, revenue, specialties, doctors count, and insurance.",
                            }
                        ]
                    )
                    
                    # Process the search response
                    search_response = completion.choices[0].message.content
                    
                    # Check if response is similar to existing content
                    content_hash = hash(search_response[:200])
                    if content_hash in seen_content_hashes:
                        st.write("Skipping duplicate content")
                        break
                        
                    seen_content_hashes.add(content_hash)
                    
                    # Extract URLs and check for domain diversity
                    urls = _extract_urls(search_response)
                    new_urls = [url for url in urls if _get_domain(url) not in seen_domains]
                    
                    # If we found any new URLs, add them to seen domains
                    for url in new_urls:
                        domain = _get_domain(url)
                        if domain:
                            seen_domains.add(domain)
                    
                    # Create result with category
                    result = {
                        "href": new_urls[0] if new_urls else None,
                        "domain": _get_domain(new_urls[0]) if new_urls else None,
                        "title": f"Search: {search_query}",
                        "body": search_response,
                        "source_query": search_query,
                        "category": category
                    }
                    
                    results.append(result)
                    successful_queries += 1
                    
                    # Add progressive delay between queries
                    time.sleep(1)
                    break  # Exit retry loop on success
                    
                except Exception as e:
                    retry_count += 1
                    failed_queries += 1
                    
                    st.warning(f"Error on query '{search_query}': {str(e)}")
                    
                    # Handle rate limiting and other errors
                    if "rate" in str(e).lower():
                        backoff_time *= 2  # Exponential backoff
                        st.warning(f"Rate limited. Waiting {backoff_time} seconds before retry")
                        time.sleep(backoff_time)
                    else:
                        st.warning(f"Search error. Waiting 2 seconds before retry")
                        time.sleep(2)
            
            # Update progress
            query_index += 1
            progress_bar.progress(query_index / total_queries)
    
    # Process results - remove duplicates and categorize
    processed_results = _process_results(results)
    
    # Summary statistics
    st.success(f"Search complete! Found {len(processed_results)} unique results")
    print(f"Successful queries: {successful_queries}/{query_index}")
    
    if failed_queries > 0:
        st.warning(f"Failed queries: {failed_queries}")
    
    # Return categorized results
    categorized = {
        "results": processed_results,
        "statistics": {
            "total_unique_results": len(processed_results),
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "categories": {}
        }
    }
    
    # Count results by category
    for result in processed_results:
        cat = result["category"]
        if cat not in categorized["statistics"]["categories"]:
            categorized["statistics"]["categories"][cat] = 0
        categorized["statistics"]["categories"][cat] += 1
    
    # Store in cache
    _search_cache[query] = categorized
    
    return categorized

def _extract_urls(text: str) -> List[str]:
    # Better URL regex pattern
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    urls = re.findall(url_pattern, text)
    return [url.strip(".,()[]{}\"'") for url in urls]

def _get_domain(url: str) -> Optional[str]:
    if not url:
        return None
    try:
        return urlparse(url).netloc
    except:
        return None

def _process_results(results: List[Dict]) -> List[Dict]:
    processed_results = []
    seen_content_hashes = set()
    
    # Category detection patterns
    category_patterns = {
        "Contact Information": ["contact", "phone", "email", "address"],
        "Organization Information": ["about", "history", "overview", "mission"],
        "Leadership": ["leadership", "ceo", "executive", "board", "director"],
        "Financial Information": ["financial", "revenue", "annual report", "profit"],
        "Locations": ["location", "facilities", "address", "campus"],
        "Insurance Information": ["insurance", "coverage", "plan", "accept", "network"],
        "Doctors/Specialties": ["doctor", "physician", "specialist", "specialty", "practice"]
    }
    
    for r in results:
        content = r.get("body", "")
        # Create a more robust content hash
        content_hash = hash(content[:300].lower())
        
        if content_hash not in seen_content_hashes:
            seen_content_hashes.add(content_hash)
            
            # Determine content category based on patterns
            category = r.get("category", "General")
            content_lower = content.lower()
            
            # Override category if we detect specific content
            for cat_name, patterns in category_patterns.items():
                if any(pattern in content_lower for pattern in patterns):
                    category = cat_name
                    break
            
            # Create enriched search result
            processed_result = {
                "content": content,
                "title": r.get("title", ""),
                "category": category,
                "source_query": r.get("source_query", "")
            }
            
            # Add URL if available
            if r.get("href"):
                processed_result["url"] = r.get("href")
                processed_result["domain"] = r.get("domain")
            
            processed_results.append(processed_result)
    
    return processed_results


