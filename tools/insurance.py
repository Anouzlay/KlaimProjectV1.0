from openai import OpenAI

def search_for_insurance(query: str, api_key:str):
    client = OpenAI(api_key=api_key)
    search_query = '''
    Data : ''' + query + '''
    Task: Search for a complete list of all insurance plans and providers accepted by {query} Hospital

    Perform an exhaustive search to identify:
    1. All major insurance networks accepted
    2. All specific insurance plans accepted within each network
    3. Medicare/Medicaid acceptance status and specific programs
    4. International insurance providers (if applicable)
    5. Self-pay and financial assistance options

    Search Strategy:
    - Check the hospital's official website, specifically their "Insurance" or "Billing" pages
    - Review the hospital's patient financial services documentation
    - Search for the hospital's provider directories
    - Examine hospital network affiliations for insurance information
    - Look for press releases about new insurance partnerships
    - Check insurance provider websites for inclusion of this hospital
    - Search for patient forums mentioning insurance acceptance at this facility

    Data Collection Requirements:
    - Group insurance by type (Private, Medicare, Medicaid, Military, International)
    - Include full formal names of insurance companies and specific plans
    - Note any recently added or discontinued insurance relationships
    - Identify any insurance plans with special relationships or preferred status
    - Document any network limitations or special conditions

    NB: Use JSON Format for Output and dont use ```json or ``` in the output, give just raw json without anything before it or anything after it
    Json Output Exemple : 
    {
        "insurance_accepted": [
            "x1",
            "x2",
            "x3",
            "..."
        ]
    } 
'''

    print(f"Prompt : {search_query}")
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
    search_response = completion.choices[0].message.content
                    
    return search_response

