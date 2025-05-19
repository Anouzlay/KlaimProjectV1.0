from openai import OpenAI

def search_for_website(query: str, api_key: str):
    client = OpenAI(api_key=api_key)
    search_query = '''
    Data : ''' + query + '''
    Task : Search for the official website URL of ''' + query + ''' Hospital in the UAE, give the website URL in JSON format
    NB : Use JSON Format for Output and dont use ```json or ``` in the output, give just raw json without anything before it or anything after it
    Json Output Example :
    {
        "hospital_name": "Hospital Name",
        "website_url": "https://example.com"
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

# Example usage:
# print(search_for_website('Cleveland Clinic Abu Dhabi', 'YOUR_OPENAI_API_KEY'))