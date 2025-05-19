import litellm
from crewai import Agent, Task, Crew
import json

def run_agent(data_dict , openai_api_key):
    litellm.api_key = openai_api_key
    # Ensure we're working with a Python dictionary
    if isinstance(data_dict, str):
        try:
            data_dict = json.loads(data_dict)
        except json.JSONDecodeError:
            return "Error: Invalid JSON data provided"
    
    # Create the healthcare report agent
    healthcare_report_agent = Agent(
        role="Healthcare Intelligence Report Specialist",
        goal="Create comprehensive, executive-ready reports from healthcare facility data with complete insurance coverage information",
        backstory="""Senior healthcare consultant with 15+ years of experience in healthcare administration 
        and business intelligence. Expert in interpreting complex healthcare data, assessing data quality,
        and communicating actionable insights to executives. Known for creating clear, 
        well-structured reports that highlight key information while properly qualifying uncertainty.
        You prioritize comprehensive data presentation, particularly for insurance coverage.""",
        verbose=True,
        allow_delegation=False
    )
    
    # Parse any JSON string values in the data
    for key, value in list(data_dict.items()):
        if isinstance(value, str):
            if value.strip().startswith('{') or value.strip().startswith('['):
                try:
                    data_dict[key] = json.loads(value)
                except json.JSONDecodeError:
                    # Keep as string if not valid JSON
                    pass
    
    # Convert to string for the description parameter
    json_string = json.dumps(data_dict, indent=2)
    
    # Create task with specific emphasis on complete insurance listing
    report_generation_task = Task(
        description=f"""
        Create a comprehensive, professional Healthcare Facility Intelligence Report based on the provided
        JSON data. The data contains analyzed information about a healthcare facility, including leadership
        contacts, contact information, financial data, medical capabilities, and insurance information.
        
        The consolidated healthcare facility data is: {json_string}
        
        **Instructions:**
        
        1. Begin with an executive summary highlighting the most reliable findings
        
        2. Structure the report with these clear sections:
        - Facility Overview (Leadership & Contact Information)
        - Financial Profile
        - Medical Capabilities
        - Insurance Coverage (IMPORTANT: List ALL insurance providers with NO omissions)
        - Data Reliability Assessment
        
        3. For each data point, present information according to its confidence level:
        - High Confidence (80%+ occurrence rate): Present as factual
        - Medium Confidence (50-79%): Present as likely correct with minimal qualification
        - Low Confidence (20-49%): Present with appropriate qualifiers
        - Very Low Confidence (<20%): Present only if relevant, with clear uncertainty markers
        
        4. When multiple conflicting values exist with significant confidence, present the most likely
        value first, but mention key alternatives with their confidence levels
        
        5. In the Data Reliability Assessment section, provide an overall evaluation of the data quality,
        highlighting areas of high certainty and areas requiring further verification
        
        6. Use professional, formal language appropriate for executive leadership
        
        7. Format for readability with clear headings, concise paragraphs, and strategic use of bullet points
        
        8. CRITICAL REQUIREMENT: In the Insurance Coverage section, you MUST list ALL insurance providers 
        from the data without any omissions. Do not abbreviate this list or use statements like "selected list" 
        or "and many more." Include the complete list of all insurance providers.
        
        The final report should be comprehensive but concise, emphasizing actionable intelligence while
        maintaining appropriate levels of certainty based on the underlying data reliability.
        """,
        agent=healthcare_report_agent,
        expected_output="Complete Healthcare Facility Intelligence Report with comprehensive insurance coverage listing"
    )
    
    # Create and run the crew
    report_generation_crew = Crew(
        agents=[healthcare_report_agent],
        tasks=[report_generation_task],
        verbose=True
    )
    
    try:
        final_report = report_generation_crew.kickoff()
        return final_report
    except Exception as e:
        return f"Error generating report: {str(e)}"


# Additional function to check the data before passing to the agent
def validate_and_prepare_data(data_dict):
    """
    Validates and prepares the data dictionary before passing to the agent.
    
    Args:
        data_dict (dict): The data dictionary to validate
        
    Returns:
        dict: The validated and prepared data dictionary
    """
    # Make a copy to avoid modifying the original
    processed_data = data_dict.copy()
    
    # Check if INSURANCES_ACCEPTED is a JSON string and parse it
    if 'INSURANCES_ACCEPTED' in processed_data and isinstance(processed_data['INSURANCES_ACCEPTED'], str):
        try:
            processed_data['INSURANCES_ACCEPTED'] = json.loads(processed_data['INSURANCES_ACCEPTED'])
        except json.JSONDecodeError:
            # If it fails to parse, keep it as is
            pass
    
    # Same for other fields that might be JSON strings
    for field in ['NET_REVENUE/YEARLY', 'NO. OF_SPECIALTIES', 'NO. OF_DOCTORS']:
        if field in processed_data and isinstance(processed_data[field], str):
            try:
                processed_data[field] = json.loads(processed_data[field])
            except json.JSONDecodeError:
                # If it fails to parse, keep it as is
                pass
    
    return processed_data
