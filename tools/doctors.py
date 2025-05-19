from openai import OpenAI

def search_for_doctors(query: str, api_key:str):
   
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    
    # For comprehensive searches, try to extract all key information in one search
    search_query = '''
    Data : ''' + query + '''
    Task : Search for the number of doctors in the ''' + query + ''' Hospital, give the number of doctors in JSON format
    NB : Use JSON Format for Output and dont use ```json or ``` in the output, give just raw json without anything before it or anything after it
    Json Output Exemple : 
    {
        "number_of_doctors": X
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



# print(search_for_doctors('Victory Medical Center', OPENAI_API_KEY) )