from openai import OpenAI

def search_for_specialities(query: str, api_key:str):
    client = OpenAI(api_key=api_key)
    search_query = '''
    Data : ''' + query + '''
    Task : Search for the number of specialities in the ''' + query + ''' Hospital, give the number of specialities in JSON format
    NB : Use JSON Format for Output and dont use ```json or ``` in the output, give just raw json without anything before it or anything after it
    Json Output Exemple : 
    {
        "number_of_specialities": X
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



# print(search_for_specialities('Victory Medical Center', OPENAI_API_KEY) )