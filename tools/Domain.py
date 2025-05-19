from openai import OpenAI

OPENAI_API_KEY = "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"
def search_for_hospital_domain(hospital_name: str, api_key: str):
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Create a search query to find the domain name
    search_query = '''
    Data : ''' + hospital_name + '''
    Task : Search for the official website domain of the ''' + hospital_name + ''' Hospital and return the domain name in JSON format
    NB : Use JSON Format for Output and dont use ```json or ``` in the output, give just raw json without anything before it or anything after it
    Json Output Example :
    {
        "hospital_name": "Example Hospital",
        "domain_name": "examplehospital.com"
    }
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
    
    return search_response

# Example usage:
print(search_for_hospital_domain('New Castle Medical Center', OPENAI_API_KEY))