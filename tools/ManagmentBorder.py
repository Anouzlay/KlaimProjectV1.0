from openai import OpenAI
import json

def search_for_hospital_ceo(hospital_name: str, api_key: str):
    client = OpenAI(api_key=api_key)
    
    search_query = '''
    Data : ''' + hospital_name + '''
    Task: Search for comprehensive executive leadership contact information for ''' + hospital_name + ''' IN THE UAE ONLY

    CRITICAL UAE VERIFICATION:
    1. THIS FACILITY MUST BE LOCATED IN THE UNITED ARAB EMIRATES ONLY
    2. If not found in UAE, return {"error": "Facility not found in UAE"}
    3. VERIFY physical address is within UAE before proceeding

    KNOWN UAE FACILITIES WITH PRIORITY EXECUTIVES - MUST PRIORITIZE THESE NAMES:
    - For "New Castle Medical Center" - MUST search for and include:
    * Founder: Abdulrab Husain Alafeefi
    * Director of Operations: Gawaher
    -Search for other
    - For "Planet Pharmacies LLC" - MUST search for and include:
    * Finance Manager: Inayatullah Rajar
      -Search for other
    - For "The Heart Medical Center" - MUST search for and include:
    * Owner: Tarek Kaplan
    * Phone number is REQUIRED for this executive
    -Search for other

    CRITICAL OUTPUT REQUIREMENTS:
    1. You MUST return a VALID JSON object with NO text formatting
    2. Do NOT include any markdown formatting like ** or numbers
    3. Do NOT include ANY text outside the JSON structure
    4. Do NOT include any code block markers

    Search for ALL executive contact information, prioritizing:
    - Known executives listed above (HIGHEST PRIORITY)
    - All C-Suite executives (CEO, CFO, COO, CMO)
    - Founders and Directors
    - Medical Director
    - Hospital Administrator
    - Department Heads
    - Board members

    For each person found, include:
    - Full name (with proper capitalization)
    - Exact title/position
    - LinkedIn profile URL (complete URL, not just username)

    - Professional email address (make educated guess if not publicly available)
    - Years of experience in current role (if available)
    - DO NOT include any executives with just initials or partially redacted names

    SEARCH METHODOLOGY:
    1. FIRST check if the facility matches any of the known UAE facilities listed above
    2. For known facilities, PRIORITIZE finding information about the specific executives mentioned
    3. Specifically search: "[Executive Name] [Facility Name] UAE LinkedIn" 
    4. Search: "[Executive Name] [Facility Name] UAE contact"
    5. Search official UAE facility website for leadership page
    6. Search UAE business directories and professional registries
    7. Check UAE Chamber of Commerce, MOH, DHA, HAAD directories if applicable

    RESPONSE FORMAT:
    Return ONLY a valid JSON object with this exact structure:

    {
    "facility_name": "Full Facility Name",
    "uae_address": "Full UAE Address",
    "executives": [
        {
        "position": "Founder",
        "name": "Abdulrab Husain Alafeefi",
        "linkedin_url": "https://www.linkedin.com/in/abdulrabalafeefi/",
        "email": "abdulrab@newcastlemc.ae",
        "years_in_role": 7
        },
        {
        "position": "Director of Operations",
        "name": "Gawaher",
        "linkedin_url": null,
        "email": "gawaher@newcastlemc.ae",
        "years_in_role": null
        }
    ]
    }

    IMPORTANT JSON RULES:
    - For missing information, use null instead of empty strings
    - Do NOT include any text or explanations outside the JSON
    - Make the JSON parseable by standard JSON parsers
    - No trailing commas

    QUALITY VERIFICATION CHECKLIST:
    1. Is this facility actually in the UAE? If not, return error
    2. For New Castle Medical Center - MUST include Abdulrab and Gawaher
    3. For Planet Pharmacies LLC - MUST include Inayatullah Rajar
    4. Email domains should match the UAE facility's domain
    5. NO executives from facilities outside UAE
    '''
    
    print(f"Prompt : {search_query}")
    
    # Use OpenAI's web search functionality
    completion = client.chat.completions.create(
        model="gpt-4o-mini-search-preview",
        web_search_options={},
        messages=[
                            {
                                "role": "system",
                                "content": "You are a specialized medical information assistant focused exclusively on the UAE healthcare system. Only provide information about UAE hospitals."
                            },
                            {
                                "role": "user",
                                "content": search_query,
                            }
                        ]
    )
    
    # Process the search response
    search_response = completion.choices[0].message.content
    json_response = json.loads(search_response)
    return json_response

#print(search_for_hospital_ceo("Public Health Centre -Al Dhaid" , OPENAI_API_KEY))
