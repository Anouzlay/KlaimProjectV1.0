from openai import OpenAI

import json


def search_hospital_parent_group(hospital_name: str, api_key: str):
    client = OpenAI(api_key=api_key)
    
    search_query = f'''
    Data: {hospital_name}
    Task: IDENTIFY which hospital group/holding owns or operates {hospital_name} IN THE UAE ONLY

    CRITICAL UAE VERIFICATION:
    1. THIS FACILITY MUST BE LOCATED IN THE UNITED ARAB EMIRATES ONLY
    2. If not found in UAE, return {{"error": "Facility not found in UAE"}}
    3. VERIFY physical address is within UAE before proceeding

    KNOWN MAJOR UAE HOSPITAL GROUPS/HOLDINGS (SEARCH FOR THESE FIRST):
    - NMC Healthcare (NMC Health Group)
    - Mediclinic Middle East
    - VPS Healthcare (Burjeel Holdings)
    - Aster DM Healthcare
    - Saudi German Hospitals UAE
    - Emirates Healthcare Group
    - Thumbay Group
    - Abu Dhabi Health Services Company (SEHA)
    - Dubai Health Authority (DHA) operated facilities
    - Ministry of Health and Prevention (MOHAP) operated facilities
    - Prime Healthcare Group
    - Zulekha Healthcare Group
    - American Hospital Dubai
    - Al Zahra Hospital
    - Belhoul Specialist Hospital
    - Al Garhoud Hospital
    - Al Zahra Hospital Group

    CRITICAL OUTPUT REQUIREMENTS:
    1. You MUST return a VALID JSON object with NO text formatting
    2. Do NOT include any markdown formatting like ** or numbers
    3. Do NOT include ANY text outside the JSON structure
    4. Do NOT include any code block markers

    SEARCH METHODOLOGY:
    1. FIRST verify if the hospital is located in the UAE
    2. Search: "{hospital_name} ownership UAE" and "{hospital_name} parent company UAE"
    3. Search hospital's official website for parent company/group information
    4. Search each major hospital group's website for this facility in their network
    5. Check UAE Ministry of Health, DHA, HAAD, and other regulatory directories
    6. Search business registries and press releases about hospital ownership
    7. Search LinkedIn for hospital profiles mentioning parent organization

    VERIFICATION FACTORS:
    - Is the hospital listed on a group's official website?
    - Do press releases mention acquisition or operation?
    - Does the hospital use group branding?
    - Are management/executives shared between entities?
    - Is there regulatory filing showing ownership?
    - Do they share website domains?

    RESPONSE FORMAT:
    Return ONLY a valid JSON object with this exact structure:

    {{
      "hospital_name": "Full Hospital Name",
      "uae_address": "Full UAE Address",
      "part_of_group": true/false,
      "parent_group": {{
        "name": "Full Group Name",
        "headquarters": "Location",
        "ceo": "Name",
        "uae_facilities_count": number,
        "ownership_type": "Private/Government/Semi-Government/Public"
      }},
      "relationship_type": "Owned/Operated/Affiliated/Licensed/Independent",
      "verification_sources": [
        "Source description with URL 1",
        "Source description with URL 2"
      ],
      "date_of_acquisition": "Year or specific date if available, null if unknown",
      "additional_groups": [
        {{
          "name": "Secondary Group Name if applicable",
          "relationship": "Brief description of relationship"
        }}
      ]
    }}

    IMPORTANT JSON RULES:
    - For missing information, use null instead of empty strings
    - If no parent group is identified, set "part_of_group" to false and "parent_group" to null
    - If hospital is independent, clearly indicate this
    - Make the JSON parseable by standard JSON parsers
    - No trailing commas

    QUALITY VERIFICATION CHECKLIST:
    1. Is this facility actually in the UAE? If not, return error
    2. Has the parent group been verified from multiple sources?
    3. Are all verification sources properly documented?
    4. Is the relationship type accurately classified?
    5. Have you checked all major UAE healthcare groups for potential ownership?
    '''
    
    print(f"Searching for parent group of {hospital_name}...")
    
    # Use OpenAI's web search functionality
    completion = client.chat.completions.create(
        model="gpt-4o-mini-search-preview",
        web_search_options={},
        messages=[
            {
                "role": "system",
                "content": "You are a specialized UAE healthcare information analyst focused on hospital ownership structures and corporate relationships. Your task is to identify which group owns or operates specific hospitals in the UAE, with thorough verification from multiple sources."
            },
            {
                "role": "user",
                "content": search_query,
            }
        ]
    )
    
    # Process the search response
    search_response = completion.choices[0].message.content
    try:
        json_response = json.loads(search_response)
        return json_response
    except json.JSONDecodeError:
        print("Error: Invalid JSON response received")
        print(f"Raw response: {search_response}")
        return {"error": "Invalid JSON response", "raw_response": search_response}

# # Example usage
# if __name__ == "__main__":

#     hospital_name = "Aldhaid hospital"
#     result = search_hospital_parent_group(hospital_name, OPENAI_API_KEY)
#     print(json.dumps(result, indent=2))
