from crewai import Agent, Task, Crew
import json
import litellm
from typing import List, Dict, Any
import tiktoken
def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count the number of tokens in a text string."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        return len(text.split()) * 1.5  

def chunk_sources(sources: List[Dict[str, str]], max_tokens: int = 100000) -> List[List[Dict[str, str]]]:
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for source in sources:
        source_text = f"SOURCE URL: {source['url']}\n{source['text']}"
        source_tokens = count_tokens(source_text)

        if current_tokens + source_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0

        if source_tokens > max_tokens:
            paragraphs = source['text'].split('\n\n')
            temp_source = {'url': source['url'], 'text': ''}
            
            for paragraph in paragraphs:
                paragraph_tokens = count_tokens(paragraph)
            
                if current_tokens + paragraph_tokens > max_tokens and temp_source['text']:
                    current_chunk.append(temp_source)
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_tokens = 0
                    temp_source = {'url': source['url'], 'text': ''}
                
                temp_source['text'] += paragraph + '\n\n'
                current_tokens += paragraph_tokens
            if temp_source['text']:
                current_chunk.append(temp_source)
                current_tokens += count_tokens(f"SOURCE URL: {temp_source['url']}\n{temp_source['text']}")
        else:

            current_chunk.append(source)
            current_tokens += source_tokens
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks
def create_chunked_task(agent, task_type, sources_chunk, chunk_index, total_chunks):
    """Generic function to create a task with chunked data."""
    sources_text = "\n\n".join([f"SOURCE {i+1} URL: {source['url']}\n{source['text']}" 
                               for i, source in enumerate(sources_chunk)])
    
    task_descriptions = {
        "revenue": f"""
            Extract ALL yearly net revenue figures from this data chunk ({chunk_index+1} of {total_chunks}):
            
            {sources_text}
            
            For each source, look for phrases like "net revenue of $X", "annual revenue", "yearly revenue".
            
            IMPORTANT:
            1. Extract ALL revenue figures you can find from EACH source
            2. Include the source URL for each extracted value
            
            Format your response as a JSON object:
            {{
                "chunk_results": [
                    {{
                        "value": "$X million/billion (YYYY)",
                        "source_url": "url1"
                    }},
                    {{
                        "value": "$Y million/billion (YYYY)",
                        "source_url": "url2"
                    }},
                    ...
                ]
            }}
            """,
        "specialties": f"""
            Extract ALL numbers of medical specialties from this data chunk ({chunk_index+1} of {total_chunks}):
            
            {sources_text}
            
            For each source, look for statements about number of specialties or lists of specialties.
            
            IMPORTANT:
            1. Extract ALL specialty counts you can find from EACH source
            2. Include the source URL for each extracted value
            
            Format your response as a JSON object:
            {{
                "chunk_results": [
                    {{
                        "value": "42",
                        "source_url": "url1"
                    }},
                    {{
                        "value": "45",
                        "source_url": "url2"
                    }},
                    ...
                ]
            }}
            """,
        "doctors": f"""
            Extract ALL numbers of doctors from this data chunk ({chunk_index+1} of {total_chunks}):
            
            {sources_text}
            
            For each source, look for statements about physician count or "X physicians on staff".
            
            IMPORTANT:
            1. Extract ALL doctor counts you can find from EACH source
            2. Include the source URL for each extracted value
            
            Format your response as a JSON object:
            {{
                "chunk_results": [
                    {{
                        "value": "157",
                        "source_url": "url1"
                    }},
                    {{
                        "value": "160",
                        "source_url": "url2"
                    }},
                    ...
                ]
            }}
            """,
        "ceo": f"""
            Extract ALL CEO information from this data chunk ({chunk_index+1} of {total_chunks}):
            
            {sources_text}
            
            For each source, look for names followed by "CEO" or "Chief Executive Officer".
            
            IMPORTANT:
            1. Extract ALL CEO names you can find from EACH source
            2. Include the source URL for each extracted value
            
            Format your response as a JSON object:
            {{
                "chunk_results": [
                    {{
                        "value": "Jane Smith, Chief Executive Officer",
                        "source_url": "url1"
                    }},
                    {{
                        "value": "John Smith, CEO",
                        "source_url": "url2"
                    }},
                    ...
                ]
            }}
            """,
        "url": f"""
            Extract ALL website URLs from this data chunk ({chunk_index+1} of {total_chunks}):
            
            {sources_text}
            
            For each source, look for URLs in the format of www.example.com or https://example.com.
            
            IMPORTANT:
            1. Extract ALL website URLs you can find from EACH source
            2. Include the source URL for each extracted value
            
            Format your response as a JSON object:
            {{
                "chunk_results": [
                    {{
                        "value": "https://www.hospitalabc.org",
                        "source_url": "url1"
                    }},
                    {{
                        "value": "https://hospitalabc.org",
                        "source_url": "url2"
                    }},
                    ...
                ]
            }}
            """,
        "management": f"""
            Extract ALL management team information from this data chunk ({chunk_index+1} of {total_chunks}):
            
            {sources_text}
            
            For each source, look for executive leadership listings and management team sections.
            
            IMPORTANT:
            1. Extract ALL management team members you can find from EACH source
            2. Include the source URL for each extracted value
            
            Format your response as a JSON object:
            {{
                "chunk_results": [
                    {{
                        "value": "John Doe, CFO; Jane Smith, COO; Mark Johnson, CMO",
                        "source_url": "url1"
                    }},
                    {{
                        "value": "John Doe, CFO; Sarah Williams, COO",
                        "source_url": "url2"
                    }},
                    ...
                ]
            }}
            """,
        "insurance": f"""
            Extract ALL insurance information from this data chunk ({chunk_index+1} of {total_chunks}):
            
            {sources_text}
            
            For each source, look for lists of accepted insurance and insurance provider names.
            
            IMPORTANT:
            1. Extract ALL insurance lists you can find from EACH source
            2. Include the source URL for each extracted value
            
            Format your response as a JSON object:
            {{
                "chunk_results": [
                    {{
                        "value": "Blue Cross Blue Shield, Aetna, Cigna, Medicare",
                        "source_url": "url1"
                    }},
                    {{
                        "value": "Aetna, Cigna, United Healthcare",
                        "source_url": "url2"
                    }},
                    ...
                ]
            }}
            """,
        "phone": f"""
            Extract ALL phone numbers from this data chunk ({chunk_index+1} of {total_chunks}):
            
            {sources_text}
            
            For each source, look for phone numbers in any format and contact information sections.
            
            IMPORTANT:
            1. Extract ALL phone numbers you can find from EACH source
            2. Include the source URL for each extracted value
            
            Format your response as a JSON object:
            {{
                "chunk_results": [
                    {{
                        "value": "+971 4 377 6666",
                        "source_url": "url1"
                    }},
                    {{
                        "value": "+971 4 377 7777",
                        "source_url": "url2"
                    }},
                    ...
                ]
            }}
            """,
        "location": f"""
            Extract ALL UAE location information from this data chunk ({chunk_index+1} of {total_chunks}):
            
            {sources_text}
            
            Focus ONLY on locations within the United Arab Emirates (UAE).
            For each source, look for specific emirate names, districts, areas, neighborhoods, and specific addresses.
            
            IMPORTANT:
            1. Extract ALL location details you can find from EACH source
            2. Include the source URL for each extracted value
            
            Format your response as a JSON object:
            {{
                "chunk_results": [
                    {{
                        "value": "Emirate: Dubai, Area: Healthcare City, Location: Building 37, Al Razi Street",
                        "source_url": "url1"
                    }},
                    {{
                        "value": "Dubai Healthcare City, Phase 2",
                        "source_url": "url2"
                    }},
                    ...
                ]
            }}
            """
    }
    
    return Task(
        description=task_descriptions[task_type],
        agent=agent,
        expected_output=f"JSON with extracted {task_type} data from chunk {chunk_index+1} of {total_chunks}"
    )

def create_aggregation_task(agent, task_type, all_chunk_results):
    chunk_results_str = json.dumps(all_chunk_results, indent=2)
    
    return Task(
        description=f"""
        Aggregate these {task_type} results from multiple data chunks:
        
        {chunk_results_str}
        
        IMPORTANT:
        1. Combine all extracted values from all chunks
        2. Identify the MOST COMMON value across all sources
        3. Count occurrences of each unique value
        
        Format your response as a JSON object:
        {{
            "most_common": {{
                "value": "The most common value",
                "count": 3,
                "source_urls": ["url1", "url2", "url3"]
            }},
            "all_values": [
                {{
                    "value": "Value 1",
                    "source_url": "url1"
                }},
                {{
                    "value": "Value 2",
                    "source_url": "url2"
                }},
                ...
            ]
        }}
        """,
        agent=agent,
        expected_output=f"Aggregated JSON with most common {task_type} and all values"
    )

def process_field_with_chunking(agent, field_type, field_data, max_tokens=100000):
    if not field_data:
        return json.dumps({
            "most_common": {
                "value": "No data available",
                "count": 0,
                "source_urls": []
            },
            "all_values": []
        })
    chunks = chunk_sources(field_data, max_tokens)
    print(f"Split {field_type} data into {len(chunks)} chunks")
    all_chunk_results = []
    for i, chunk in enumerate(chunks):
        task = create_chunked_task(agent, field_type, chunk, i, len(chunks))
        crew = Crew(agents=[agent], tasks=[task], verbose=True, process="sequential")
        
        try:
            chunk_result = crew.kickoff()
            if isinstance(chunk_result, str):
                try:
                    parsed_result = json.loads(chunk_result)
                    if "chunk_results" in parsed_result:
                        all_chunk_results.extend(parsed_result["chunk_results"])
                except json.JSONDecodeError:
                    print(f"Error parsing chunk {i} result for {field_type}")
            else:
                try:
                    result_text = str(chunk_result)
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        parsed_result = json.loads(json_str)
                        if "chunk_results" in parsed_result:
                            all_chunk_results.extend(parsed_result["chunk_results"])
                    else:
                        try:
                            parsed_result = json.loads(result_text)
                            if "chunk_results" in parsed_result:
                                all_chunk_results.extend(parsed_result["chunk_results"])
                        except:
                            print(f"Could not extract JSON from CrewOutput for chunk {i}")
                except Exception as e:
                    print(f"Error processing CrewOutput for chunk {i}: {str(e)}")
        except Exception as e:
            print(f"Error processing chunk {i} for {field_type}: {str(e)}")
    
    if len(chunks) > 1 and all_chunk_results:
        aggregation_task = create_aggregation_task(agent, field_type, all_chunk_results)
        aggregation_crew = Crew(agents=[agent], tasks=[aggregation_task], verbose=True, process="sequential")
        try:
            final_result = aggregation_crew.kickoff()
            if isinstance(final_result, str):
                return final_result
            else:
                result_text = str(final_result)
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                if json_match:
                    return json_match.group(1)
                else:
                    try:
                        json.loads(result_text)  
                        return result_text
                    except:
                        print(f"Falling back to manual aggregation for {field_type}")
                        return manually_aggregate_results(all_chunk_results)
        except Exception as e:
            print(f"Error aggregating results for {field_type}: {str(e)}")
            return manually_aggregate_results(all_chunk_results)
    elif all_chunk_results:
        return manually_aggregate_results(all_chunk_results)
    else:
        return json.dumps({
            "most_common": {
                "value": "No data available",
                "count": 0,
                "source_urls": []
            },
            "all_values": []
        })

def extract_hospital_data(raw_data_with_urls, openai_api_key, max_tokens=100000):
    litellm.api_key = openai_api_key
    normalized_data = {}
    

    revenue_agent = Agent(
        role="Revenue Data Extractor",
        goal="Extract all yearly net revenue figures from multiple sources and identify the most common value",
        backstory="Financial data analyst specialized in reconciling revenue figures from multiple sources",
        verbose=True
    )

    specialties_agent = Agent(
        role="Medical Specialties Counter",
        goal="Extract all numbers of medical specialties from multiple sources and identify the most common count",
        backstory="Healthcare data analyst specialized in reconciling specialty counts across different sources",
        verbose=True
    )

    doctors_agent = Agent(
        role="Physician Count Extractor",
        goal="Extract all numbers of doctors from multiple sources and identify the most common count",
        backstory="Healthcare staffing analyst who can reconcile physician counts across different sources",
        verbose=True
    )

    ceo_agent = Agent(
        role="CEO Information Extractor",
        goal="Extract all CEO information from multiple sources and identify the most commonly mentioned name",
        backstory="Executive data specialist who can reconcile leadership information across different sources",
        verbose=True
    )

    url_agent = Agent(
        role="Website URL Extractor",
        goal="Extract all website URLs from multiple sources and identify the most commonly mentioned URL",
        backstory="Digital analyst who can reconcile website URLs across different sources",
        verbose=True
    )

    management_agent = Agent(
        role="Management Team Extractor",
        goal="Extract all management team details from multiple sources and identify the most commonly mentioned members",
        backstory="Organizational data specialist who can reconcile management information across different sources",
        verbose=True
    )

    insurance_agent = Agent(
        role="Insurance Information Extractor",
        goal="Extract all insurance information from multiple sources and identify the most commonly accepted plans",
        backstory="Healthcare insurance specialist who can reconcile insurance information across different sources",
        verbose=True
    )

    phone_agent = Agent(
        role="Phone Number Extractor",
        goal="Extract all hospital phone numbers from multiple sources and identify the most commonly listed number",
        backstory="Contact information specialist who can reconcile phone numbers across different sources",
        verbose=True
    )

    location_agent = Agent(
        role="UAE Location Specialist",
        goal="Extract all location details within the UAE from multiple sources and identify the most commonly mentioned address",
        backstory="Geographical data analyst who can reconcile location information across different sources",
        verbose=True
    )

    coordinator_agent = Agent(
        role="Healthcare Data Integrator",
        goal="Integrate all extracted information with proper attribution and consensus analysis",
        backstory="Data integration specialist who excels at reconciling information from multiple sources",
        verbose=True
    )
    for field in ['revenue', 'specialties', 'doctors', 'ceo', 'website', 
                 'management', 'insurance', 'phone', 'location']:
        
        if field not in raw_data_with_urls:
            normalized_data[field] = []
            continue
            
        field_data = raw_data_with_urls[field]
        if isinstance(field_data, list):
            sources = []
            for item in field_data:
                if isinstance(item, dict) and 'text' in item and 'url' in item:
                    sources.append(item)
            normalized_data[field] = sources

        elif isinstance(field_data, dict):
            if 'text' in field_data and 'url' in field_data:
                normalized_data[field] = [field_data]
            else:
                sources = []
                for key, value in field_data.items():
                    if isinstance(value, dict) and 'text' in value and 'url' in value:
                        sources.append(value)
                normalized_data[field] = sources
                
        else:
            normalized_data[field] = []
    
    print("Normalized data structure:")
    for field, sources in normalized_data.items():
        print(f"{field}: {len(sources)} sources")
    print("Processing revenue data...")
    revenue_result = process_field_with_chunking(revenue_agent, "revenue", normalized_data['revenue'], max_tokens)
    
    print("Processing specialties data...")
    specialties_result = process_field_with_chunking(specialties_agent, "specialties", normalized_data['specialties'], max_tokens)
    
    print("Processing doctors data...")
    doctors_result = process_field_with_chunking(doctors_agent, "doctors", normalized_data['doctors'], max_tokens)
    
    print("Processing CEO data...")
    ceo_result = process_field_with_chunking(ceo_agent, "ceo", normalized_data['ceo'], max_tokens)
    
    print("Processing URL data...")
    url_result = process_field_with_chunking(url_agent, "url", normalized_data['website'], max_tokens)
    
    print("Processing management data...")
    management_result = process_field_with_chunking(management_agent, "management", normalized_data['management'], max_tokens)
    
    print("Processing insurance data...")
    insurance_result = process_field_with_chunking(insurance_agent, "insurance", normalized_data['insurance'], max_tokens)
    
    print("Processing phone data...")
    phone_result = process_field_with_chunking(phone_agent, "phone", normalized_data['phone'], max_tokens)
    
    print("Processing location data...")
    location_result = process_field_with_chunking(location_agent, "location", normalized_data['location'], max_tokens)
    def ensure_json_str(result):
        if isinstance(result, str):
            try:
                json.loads(result)
                return result
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
                if json_match:
                    return json_match.group(1)
                return json.dumps({
                    "most_common": {
                        "value": "Data format error",
                        "count": 0,
                        "source_urls": []
                    },
                    "all_values": []
                })
        else:
            return json.dumps({
                "most_common": {
                    "value": "Data type error",
                    "count": 0,
                    "source_urls": []
                },
                "all_values": []
            })
    agent_results = {
        'revenue': ensure_json_str(revenue_result),
        'specialties': ensure_json_str(specialties_result),
        'doctors': ensure_json_str(doctors_result),
        'ceo': ensure_json_str(ceo_result),
        'url': ensure_json_str(url_result),
        'management': ensure_json_str(management_result),
        'insurance': ensure_json_str(insurance_result),
        'phone': ensure_json_str(phone_result),
        'location': ensure_json_str(location_result)
    }
    print("\nData being sent to coordinator:")
    for field, data in agent_results.items():
        print(f"{field}: {data[:100]}..." if len(data) > 100 else f"{field}: {data}")

    coordinator_task = Task(
        description=f"""
        Integrate these extracted data points with multiple sources into a single, structured format:
        
        NETREVENUEYEARLY: {agent_results['revenue']}
        NO_OF_SPECIALTIES: {agent_results['specialties']}
        NOOFDOCTORS: {agent_results['doctors']}
        CEO: {agent_results['ceo']}
        URL website: {agent_results['url']}
        MANAGEMENT_TEAM: {agent_results['management']}
        INSURANCE: {agent_results['insurance']}
        Phone hospital: {agent_results['phone']}
        UAE_LOCATION: {agent_results['location']}
        
        Create a structured JSON object with all these fields:
        1. For each field, use the "most_common" value as the primary value
        2. Include source URLs for each piece of information
        3. Add confidence scores based on agreement across sources:
           - "High" if the same value appears in 3+ sources
           - "Medium" if the same value appears in 2 sources
           - "Low" if there's no consensus or only 1 source
        4. For each field, also include an "alternatives" section if there are different values
        
        Format your response as a complete JSON object:
        {{
            "NETREVENUEYEARLY": {{
                "value": "...",
                "source_urls": ["url1", "url2", ...],
                "confidence": "High/Medium/Low",
                "alternatives": [
                    {{
                        "value": "...",
                        "source_urls": ["url3"]
                    }},
                    ...
                ]
            }},
            "NO_OF_SPECIALTIES": {{
                "value": "...",
                "source_urls": ["url1", "url2", ...],
                "confidence": "High/Medium/Low",
                "alternatives": [
                    {{
                        "value": "...",
                        "source_urls": ["url3"]
                    }},
                    ...
                ]
            }},
            ... and so on for all fields
        }}
        """,
        agent=coordinator_agent,
        expected_output="Complete nested JSON with all data fields, confidence scores, and alternative values"
    )
    
    coordinator_crew = Crew(agents=[coordinator_agent], tasks=[coordinator_task], verbose=True, process="sequential")
    
    try:
        final_result = coordinator_crew.kickoff()
        if isinstance(final_result, str):
            try:
                return json.loads(final_result)
            except:
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', final_result, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except:
                        return {"error": "Could not parse coordinator result as JSON", "raw_result": final_result}
                return final_result
        else:
            result_text = str(final_result)
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    return {"error": "Could not parse coordinator CrewOutput as JSON", "raw_result": result_text}
            else:
                try:
                    return json.loads(result_text)
                except:
                    return {"error": "Could not parse coordinator result", "raw_result": result_text}
    except Exception as e:
        print(f"Error in coordinator: {str(e)}")
        return {
            "raw_results": agent_results,
            "error": str(e)
        }

def manually_aggregate_results(chunk_results):

    value_counts = {}
    for result in chunk_results:
        value = result.get("value", "")
        source_url = result.get("source_url", "")
        
        if value not in value_counts:
            value_counts[value] = {"count": 0, "source_urls": []}
        
        value_counts[value]["count"] += 1
        if source_url and source_url not in value_counts[value]["source_urls"]:
            value_counts[value]["source_urls"].append(source_url)
    most_common_value = None
    most_common_count = 0
    
    for value, data in value_counts.items():
        if data["count"] > most_common_count:
            most_common_value = value
            most_common_count = data["count"]
    result = {
        "most_common": {
            "value": most_common_value if most_common_value else "No data available",
            "count": most_common_count,
            "source_urls": value_counts.get(most_common_value, {}).get("source_urls", []) if most_common_value else []
        },
        "all_values": [
            {
                "value": value,
                "source_url": source_urls[0] if source_urls else ""
            }
            for value, data in value_counts.items()
            for source_urls in [data["source_urls"]]
        ]
    }
    
    return json.dumps(result)
def extract_hospital_data(raw_data_with_urls, openai_api_key, max_tokens=100000):
    litellm.api_key = openai_api_key
    normalized_data = {}
    
    # Define all agents
    revenue_agent = Agent(
        role="Revenue Data Extractor",
        goal="Extract all yearly net revenue figures from multiple sources and identify the most common value",
        backstory="Financial data analyst specialized in reconciling revenue figures from multiple sources",
        verbose=True
    )

    specialties_agent = Agent(
        role="Medical Specialties Counter",
        goal="Extract all numbers of medical specialties from multiple sources and identify the most common count",
        backstory="Healthcare data analyst specialized in reconciling specialty counts across different sources",
        verbose=True
    )

    doctors_agent = Agent(
        role="Physician Count Extractor",
        goal="Extract all numbers of doctors from multiple sources and identify the most common count",
        backstory="Healthcare staffing analyst who can reconcile physician counts across different sources",
        verbose=True
    )

    ceo_agent = Agent(
        role="CEO Information Extractor",
        goal="Extract all CEO information from multiple sources and identify the most commonly mentioned name",
        backstory="Executive data specialist who can reconcile leadership information across different sources",
        verbose=True
    )

    url_agent = Agent(
        role="Website URL Extractor",
        goal="Extract all website URLs from multiple sources and identify the most commonly mentioned URL",
        backstory="Digital analyst who can reconcile website URLs across different sources",
        verbose=True
    )

    management_agent = Agent(
        role="Management Team Extractor",
        goal="Extract all management team details from multiple sources and identify the most commonly mentioned members",
        backstory="Organizational data specialist who can reconcile management information across different sources",
        verbose=True
    )

    insurance_agent = Agent(
        role="Insurance Information Extractor",
        goal="Extract all insurance information from multiple sources and identify the most commonly accepted plans",
        backstory="Healthcare insurance specialist who can reconcile insurance information across different sources",
        verbose=True
    )

    phone_agent = Agent(
        role="Phone Number Extractor",
        goal="Extract all hospital phone numbers from multiple sources and identify the most commonly listed number",
        backstory="Contact information specialist who can reconcile phone numbers across different sources",
        verbose=True
    )

    location_agent = Agent(
        role="UAE Location Specialist",
        goal="Extract all location details within the UAE from multiple sources and identify the most commonly mentioned address",
        backstory="Geographical data analyst who can reconcile location information across different sources",
        verbose=True
    )

    coordinator_agent = Agent(
        role="Healthcare Data Integrator",
        goal="Integrate all extracted information with proper attribution and consensus analysis",
        backstory="Data integration specialist who excels at reconciling information from multiple sources",
        verbose=True
    )
    for field in ['revenue', 'specialties', 'doctors', 'ceo', 'website', 
                 'management', 'insurance', 'phone', 'location']:
        
        if field not in raw_data_with_urls:
            normalized_data[field] = []
            continue
            
        field_data = raw_data_with_urls[field]
        if isinstance(field_data, list):
            sources = []
            for item in field_data:
                if isinstance(item, dict) and 'text' in item and 'url' in item:
                    sources.append(item)
            normalized_data[field] = sources

        elif isinstance(field_data, dict):
            if 'text' in field_data and 'url' in field_data:
                normalized_data[field] = [field_data]
            else:
                sources = []
                for key, value in field_data.items():
                    if isinstance(value, dict) and 'text' in value and 'url' in value:
                        sources.append(value)
                normalized_data[field] = sources
                
        else:
            normalized_data[field] = []
    
    print("Normalized data structure:")
    for field, sources in normalized_data.items():
        print(f"{field}: {len(sources)} sources")
    print("Processing revenue data...")
    revenue_result = process_field_with_chunking(revenue_agent, "revenue", normalized_data['revenue'], max_tokens)
    
    print("Processing specialties data...")
    specialties_result = process_field_with_chunking(specialties_agent, "specialties", normalized_data['specialties'], max_tokens)
    
    print("Processing doctors data...")
    doctors_result = process_field_with_chunking(doctors_agent, "doctors", normalized_data['doctors'], max_tokens)
    
    print("Processing CEO data...")
    ceo_result = process_field_with_chunking(ceo_agent, "ceo", normalized_data['ceo'], max_tokens)
    
    print("Processing URL data...")
    url_result = process_field_with_chunking(url_agent, "url", normalized_data['website'], max_tokens)
    
    print("Processing management data...")
    management_result = process_field_with_chunking(management_agent, "management", normalized_data['management'], max_tokens)
    
    print("Processing insurance data...")
    insurance_result = process_field_with_chunking(insurance_agent, "insurance", normalized_data['insurance'], max_tokens)
    
    print("Processing phone data...")
    phone_result = process_field_with_chunking(phone_agent, "phone", normalized_data['phone'], max_tokens)
    
    print("Processing location data...")
    location_result = process_field_with_chunking(location_agent, "location", normalized_data['location'], max_tokens)
    agent_results = {
        'revenue': revenue_result,
        'specialties': specialties_result,
        'doctors': doctors_result,
        'ceo': ceo_result,
        'url': url_result,
        'management': management_result,
        'insurance': insurance_result,
        'phone': phone_result,
        'location': location_result
    }

    coordinator_task = Task(
        description=f"""
        Integrate these extracted data points with multiple sources into a single, structured format:
        
        NETREVENUEYEARLY: {agent_results['revenue']}
        NO_OF_SPECIALTIES: {agent_results['specialties']}
        NOOFDOCTORS: {agent_results['doctors']}
        CEO: {agent_results['ceo']}
        URL website: {agent_results['url']}
        MANAGEMENT_TEAM: {agent_results['management']}
        INSURANCE: {agent_results['insurance']}
        Phone hospital: {agent_results['phone']}
        UAE_LOCATION: {agent_results['location']}
        
        Create a structured JSON object with all these fields:
        1. For each field, use the "most_common" value as the primary value
        2. Include source URLs for each piece of information
        3. Add confidence scores based on agreement across sources:
           - "High" if the same value appears in 3+ sources
           - "Medium" if the same value appears in 2 sources
           - "Low" if there's no consensus or only 1 source
        4. For each field, also include an "alternatives" section if there are different values
        
        Format your response as a complete JSON object:
        {{
            "NETREVENUEYEARLY": {{
                "value": "...",
                "source_urls": ["url1", "url2", ...],
                "confidence": "High/Medium/Low",
                "alternatives": [
                    {{
                        "value": "...",
                        "source_urls": ["url3"]
                    }},
                    ...
                ]
            }},
            "NO_OF_SPECIALTIES": {{
                "value": "...",
                "source_urls": ["url1", "url2", ...],
                "confidence": "High/Medium/Low",
                "alternatives": [
                    {{
                        "value": "...",
                        "source_urls": ["url3"]
                    }},
                    ...
                ]
            }},
            ... and so on for all fields
        }}
        """,
        agent=coordinator_agent,
        expected_output="Complete nested JSON with all data fields, confidence scores, and alternative values"
    )
    
    coordinator_crew = Crew(agents=[coordinator_agent], tasks=[coordinator_task], verbose=True)
    
    try:
        final_result = coordinator_crew.kickoff()
        if isinstance(final_result, str):
            try:
                return json.loads(final_result)
            except:
                return final_result
        return final_result
    except Exception as e:
        print(f"Error in coordinator: {str(e)}")
        return {
            "raw_results": agent_results,
            "error": str(e)
        }