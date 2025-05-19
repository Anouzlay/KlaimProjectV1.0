from openai import OpenAI

def search_for_revenue(query: str, api_key:str):

    client = OpenAI(api_key=api_key)
    
    
    search_query = '''
    Data : ''' + query + '''
      Task: Search for detailed annual revenue data for {query} hospital and analyze growth trends

      Perform a comprehensive search to find:
      1. Annual revenue figures for the past 5 years (if available)
      2. Year-over-year growth percentages
      3. Revenue breakdown by major departments/services (if available)
      4. Most recent total annual revenue

      Search Strategy:
      - Examine hospital financial reports, annual reviews, and press releases
      - Check healthcare industry databases and reports
      - Review government healthcare spending data if applicable
      - Look for merger/acquisition information that mentions revenue
      - Search news articles about the hospital's financial performance

      Data Processing Instructions:
      - Convert all revenue figures to USD if found in other currencies
      - Calculate year-over-year percentage growth for all available years
      - Identify the compound annual growth rate (CAGR) if multi-year data exists
      - Format revenue figures with appropriate suffixes (K, M, B, T)
      - If exact figures unavailable, provide researched estimate with range

      NB: Use JSON Format for Output and dont use ```json or ``` in the output, give just raw json without anything before it or anything after it

      JSON Output Example:

      {
        "hospital_name": "Hospital Name",
        "most_recent_revenue": "2.7B$",
        "revenue_year": 2024,
        "annual_revenues": [
          {"year": 2024, "revenue": "2.7B$"},
          {"year": 2023, "revenue": "2.5B$"},
          {"year": 2022, "revenue": "2.3B$"},
          {"year": 2021, "revenue": "2.0B$"},
          {"year": 2020, "revenue": "1.8B$"}
        ],
        "growth_percentages": [
          {"period": "2023-2024", "growth": "8%"},
          {"period": "2022-2023", "growth": "8.7%"},
          {"period": "2021-2022", "growth": "15%"},
          {"period": "2020-2021", "growth": "11.1%"}
        ],
        "five_year_cagr": "10.7%",
        "revenue_sources": [
          {"department": "Inpatient Services", "percentage": "45%"},
          {"department": "Outpatient Services", "percentage": "30%"},
          {"department": "Emergency Services", "percentage": "15%"},
          {"department": "Other", "percentage": "10%"}
        ],
        "data_confidence": "high/medium/low",
        "data_sources": ["Annual Report", "Press Release", "Industry Database"]
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



# print(search_for_revenue('Victory Medical Center', OPENAI_API_KEY) )