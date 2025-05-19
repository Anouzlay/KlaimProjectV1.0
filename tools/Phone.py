from openai import OpenAI
def search_for_doctor_phone(doctor_name: str, hospital_name: str, api_key: str):
    client = OpenAI(api_key=api_key)
    search_query = '''
    Data : Dr. ''' + doctor_name + ''' at ''' + hospital_name + '''
    Task : Search for the contact phone number of Dr. ''' + doctor_name + ''' who works at ''' + hospital_name + ''' and return the phone number in JSON format
    NB : Use JSON Format for Output and dont use ```json or ``` in the output, give just raw json without anything before it or anything after it
    Json Output Example :
    {
        "doctor_name": "Dr. Example Name",
        "hospital": "Example Hospital",
        "phone_number": "+971 4 123 4567"
    }
    '''
    
    print(f"Prompt : {search_query}")
    completion = client.chat.completions.create(
        model="gpt-4o-mini-search-preview",
        web_search_options={},
        messages=[
            {
                "role": "system",
                "content": "You are a specialized medical information assistant focused exclusively on the UAE healthcare system. Only provide information about UAE doctors."
            },
            {
                "role": "user",
                "content": search_query,
            }
        ]
    )
    
    search_response = completion.choices[0].message.content
    
    return search_response

#print(search_for_doctor_phone('ABDULRAB HUSAIN ALAFEEFI', 'New Castle Medical Center', OPENAI_API_KEY))
