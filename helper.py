from urllib.parse import quote_plus
import requests
import json
from pyairtable import Api
import re
from typing import Dict, Any, Optional
import os 
import random
import logging
import time

###
def validate_hospital(OPENAI_API_KEY, hospital_name: str) -> Dict[str, Any]:
        base_url = "https://api.openai.com/v1/chat/completions"
        system_prompt = """
        You are a specialized hospital name validation assistant. Your sole purpose is to check if a hospital name provided by the user exists, and if it contains errors, to correct them and provide the accurate hospital information.

        When a user provides a hospital name:
        1. Check if the name appears to be a valid hospital
        2. If the name contains spelling errors or minor mistakes, identify the correct hospital name
        3. Provide the corrected name along with location and relevant details
        4. If multiple possible matches exist, list the most likely options
        5. If no match can be found, clearly state this and ask for more information

        Format your response in a clean, structured way with the following sections:
        - CORRECTED: [The correct hospital name]
        - LOCATION: [City, State/Region, Country]
        - TYPE: [Type of hospital if known]

        Do not include any explanation about your process, just provide the validated result directly.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Validate this hospital name: {hospital_name}"}
            ],
            "max_tokens": 300
        }
        
        try:
            response = requests.post(base_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        

def analyse_raw(GEMINI_API_KEY, prompt, category, max_retries=3) -> Dict[str, Any]:
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('gemini_api')
    
    # Validate API key
    if not GEMINI_API_KEY or len(GEMINI_API_KEY) < 10:
        return {"error": "Invalid API key provided"}
    
    # Gemini API endpoint
    endpoint = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
    
    # Combine prompt and input
    user_message = f"{prompt}\n\nInput: {category}"
    
    # Rough token estimation (4 chars ≈ 1 token)
    approx_tokens = len(user_message) // 4
    logger.info(f"Approximate tokens: {approx_tokens}")
    
    # Limit content size if it might exceed rate limits
    if approx_tokens > 25000:  # Conservative limit below the 32K/min threshold
        logger.warning("Large input detected, trimming to avoid rate limits")
        # Trim to approximately 25K tokens (100K chars)
        user_message = user_message[:100000] + "...[content truncated]"
    
    # Attempt the API call with retries
    for attempt in range(max_retries + 1):
        try:
            # If not first attempt, add delay with exponential backoff
            if attempt > 0:
                # Calculate backoff with jitter (2^attempt seconds + random)
                backoff = (2 ** attempt) + random.uniform(0.1, 1.0)
                logger.info(f"Retry {attempt}/{max_retries} after {backoff:.2f}s delay")
                time.sleep(backoff)
            
            # API request URL with key
            url = f"{endpoint}?key={GEMINI_API_KEY}"
            
            # Request headers
            headers = {
                "Content-Type": "application/json"
            }
            
            # Request payload
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": user_message}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 500,
                    "topP": 0.95,
                    "topK": 40
                }
            }
            
            # Make the API call
            logger.info(f"Sending request to Gemini API")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Handle success case (HTTP 200)
            if response.status_code == 200:
                raw_response = response.json()
                
                # Process and format the response
                if "candidates" in raw_response and len(raw_response["candidates"]) > 0:
                    candidate = raw_response["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        # Extract text from all parts
                        text_parts = [part.get("text", "") for part in candidate["content"]["parts"] if "text" in part]
                        content = "".join(text_parts)
                        
                        # Format response to match expected structure (OpenAI-like)
                        formatted_response = {
                            "choices": [
                                {
                                    "message": {
                                        "content": content
                                    }
                                }
                            ],
                            "model": "gemini-1.5-pro",
                            "usage": raw_response.get("usage", {})
                        }
                        
                        logger.info("Successfully received Gemini API response")
                        return formatted_response
                
                # Return raw response if we can't extract properly formatted content
                logger.info("Received non-standard response format, returning raw response")
                return raw_response
            
            # Handle rate limit errors (HTTP 429)
            elif response.status_code == 429:
                error_data = response.json()
                retry_delay = None
                
                # Try to extract retry delay from the response
                if "error" in error_data and "details" in error_data["error"]:
                    for detail in error_data["error"]["details"]:
                        if "@type" in detail and "RetryInfo" in detail["@type"]:
                            if "retryDelay" in detail:
                                # Parse the retry delay (format like "41s")
                                delay_str = detail["retryDelay"]
                                if delay_str.endswith("s"):
                                    try:
                                        retry_delay = float(delay_str[:-1])
                                    except ValueError:
                                        pass
                
                # Use recommended delay or fallback to exponential backoff
                if retry_delay:
                    # Add a small random jitter
                    retry_delay += random.uniform(0.1, 2.0)
                    logger.warning(f"Rate limit exceeded. API suggests waiting {retry_delay:.2f}s")
                    
                    # Don't wait if this was the last attempt
                    if attempt < max_retries:
                        time.sleep(retry_delay)
                
                # Continue to next retry attempt
                continue
            
            # Handle other errors
            else:
                error_msg = f"API error: {response.status_code} {response.reason}"
                
                # Try to extract detailed error message
                try:
                    error_data = response.json()
                    if "error" in error_data and "message" in error_data["error"]:
                        error_msg = f"{error_msg} - {error_data['error']['message']}"
                except:
                    error_msg = f"{error_msg} - {response.text[:200]}"
                
                logger.error(error_msg)
                
                # Don't retry on client errors (except rate limits which are handled above)
                if response.status_code >= 400 and response.status_code < 500:
                    return {"error": error_msg}
                
                # Continue to next retry for server errors
                continue
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            
            # Don't wait if this was the last attempt
            if attempt < max_retries:
                continue
    
    # If we've exhausted all retries
    logger.error("Failed after all retry attempts")
    return {
        "error": "Failed to get successful response from Gemini API after multiple retries"
    }

def extract_validation_result(response: Dict[str, Any]) -> Dict[str, str]:

        if "error" in response:
            return {"status": "error", "message": response["error"]}
        
        try:
            content = response["choices"][0]["message"]["content"]
            result = {}
            if "CORRECTED:" in content:
                result["hospital_name"] = content.split("CORRECTED:")[1].split("\n")[0].strip()
            
            if "LOCATION:" in content:
                result["location"] = content.split("LOCATION:")[1].split("\n")[0].strip()
            
            if "TYPE:" in content:
                result["type"] = content.split("TYPE:")[1].split("\n")[0].strip()
            
            result["status"] = "success"
            result["full_response"] = content
            
            return result
        except (KeyError, IndexError) as e:
            return {"status": "error", "message": f"Failed to parse response: {str(e)}"}

###
def ask_gpt(result):
    try:
        prompt = f"""
                You are a specialized data extraction assistant focused on retrieving JSON data from CrewAI agent outputs.

                ## TASK:
                Extract ONLY the final JSON object from the CrewAI result text below. Do not modify the JSON structure or content.

                ## CONTEXT:
                CrewAI agents often generate reports that contain a final JSON object summarizing their findings. This JSON contains the key information needed for further processing. The JSON may be embedded within explanatory text, surrounded by code blocks, or have additional information before or after it.

                ## INSTRUCTIONS:
                1. Analyze the entire input text
                2. Locate and extract ONLY the JSON object
                3. Return the exact JSON object without any modifications
                4. Do not add any explanatory text, comments, or additional formatting
                5. If multiple JSON objects exist, return only the final/most complete one
                6. Return the JSON with proper indentation preserved

                ## INPUT TEXT:
                {result}

                ## IMPORTANT:
                - Return ONLY the JSON object, nothing else
                - Preserve the exact structure and content of the original JSON
                - Do not add or remove any fields
                - If no valid JSON is found, return: {{"error": "No JSON object found in the input text"}}
                """
        encoded_prompt = quote_plus(prompt)
        urlapi = f"https://a.picoapps.xyz/ask-ai?prompt={encoded_prompt}"
        response = requests.get(urlapi)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "{}")
        else:
            print(f"API request failed: {response.status_code}")
            return "{}"
    except Exception as e:
        print(f"API call failed: {e}")
        return "{}"

###

###
def create_category_queries(query, category):
    if category == "ADDRESS":
        return [
            f"{query} hospital clinic address location",
            f"{query} healthcare facility physical address",
            f"{query} medical center address directions",
            f"{query} locations facilities branches",
            f"{query} contact information address"
        ]
    
    elif category == "CONTACT PERSON":
        return [
            f"{query} CEO MD CFO COO contact information",
            f"{query} executive leadership team contact",
            f"{query} chief medical officer profile contact",
            f"{query} board of directors leadership team",
            f"{query} hospital administration contact information"
        ]
    
    elif category == "CONTACT NUMBER":
        return [
            f"{query} hospital clinic phone number",
            f"{query} healthcare organization main contact number",
            f"{query} department directory contact numbers",
            f"{query} medical center phone contacts",
            f"{query} emergency contact number"
        ]
    
    elif category == "URL WEBSITE":
        return [
            f"{query} official website",
            f"{query} healthcare organization website URL",
            f"{query} medical center website link",
            f"{query} online presence website",
            f"{query} patient portal website URL"
        ]
    
    elif category == "NET REVENUE/YEARLY":
        return [
            f"{query} annual revenue financial performance",
            f"{query} yearly revenue statistics",
            f"{query} financial statements reports",
            f"{query} fiscal year earnings report",
            f"{query} healthcare organization size revenue"
        ]
    
    elif category == "NO. OF SPECIALTIES":
        return [
            f"{query} medical specialties services offered",
            f"{query} number of specialty departments",
            f"{query} healthcare service specialties count",
            f"{query} specialty care areas provided",
            f"{query} medical specialty departments list"
        ]
    
    elif category == "NO. OF DOCTORS":
        return [
            f"{query} number of physicians doctors staff",
            f"{query} medical staff count",
            f"{query} physician directory size",
            f"{query} healthcare practitioners count",
            f"{query} medical professionals employed"
        ]
    
    elif category == "INSURANCES ACCEPTED":
        return [
            f"{query} accepted insurance plans",
            f"{query} insurance network participation",
            f"{query} medicare medicaid acceptance",
            f"{query} insurance verification process", 
            f"{query} in-network providers insurance"
        ]
    
    else:
        return [f"{query} {category}"]


###

###
def extract_urls_from_json(json_data):
    if isinstance(json_data, str):
        # Replace single quotes with double quotes for proper JSON parsing
        json_str = json_data.replace("'", '"')
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # If standard parsing fails, use regex to extract URLs
            url_regex = r"'url': '([^']+)'"
            matches = re.findall(url_regex, json_data)
            return matches
    else:
        data = json_data
    
    # Extract URLs from the results list
    urls = []
    if 'results' in data:
        for item in data['results']:
            if 'url' in item:
                urls.append(item['url'])
    
    return urls

###
def airtable_add(data, API_KEY_AIRTABLE):
    my_data = ask_gpt(data)
    BASE_ID = "appWEs2a6pzb2ETrA"
    TABLE_ID = "tblukmdE2zYOqo1fN"
    api = Api(API_KEY_AIRTABLE)
    table = api.table(BASE_ID, TABLE_ID)
    print(my_data)
    print(type(my_data))
    
    match = re.search(r'\{[\s\S]*\}', my_data)
    if match:
        json_str = match.group(0)
        try:
            data_json = json.loads(json_str)
            print(data_json)
            
            # Process all fields to handle potential nested objects/dictionaries
            for field_name, field_value in list(data_json.items()):
                # Process the field if it's not already a simple string/number
                if not isinstance(field_value, (str, int, float)) or (isinstance(field_value, str) and field_value.strip().startswith('{')):
                    # If it's a string that looks like JSON, try to parse it
                    if isinstance(field_value, str):
                        try:
                            parsed_value = json.loads(field_value)
                            field_value = parsed_value  # Replace with parsed object if successful
                        except json.JSONDecodeError:
                            # Not a valid JSON string, keep as is
                            continue
                            
                    # Format dictionary values
                    if isinstance(field_value, dict):
                        formatted_items = []
                        for key, value in field_value.items():
                            formatted_items.append(f"{key}: {value}")
                        data_json[field_name] = ", ".join(formatted_items)
                        
                    # Format list values
                    elif isinstance(field_value, list):
                        # Handle lists of dictionaries
                        if field_value and isinstance(field_value[0], dict):
                            formatted_items = []
                            for item in field_value:
                                item_parts = []
                                for k, v in item.items():
                                    item_parts.append(f"{k}: {v}")
                                formatted_items.append("(" + ", ".join(item_parts) + ")")
                            data_json[field_name] = "; ".join(formatted_items)
                        else:
                            # Simple list of values
                            data_json[field_name] = ", ".join(str(item) for item in field_value)
            
            try:
                new_record = table.create(data_json)
                print("Created record:", new_record["id"])
                return new_record
            except Exception as e:
                print("Error creating record:", e)
                return None
        except json.JSONDecodeError as e:
            print("JSON parsing error:", e)
            return None
    return None