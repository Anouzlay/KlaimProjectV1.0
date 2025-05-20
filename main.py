import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import pandas as pd
#Tools using OpenAI websearch engine

from tools.ManagmentBorder import   search_for_hospital_ceo
from tools.insurance import   search_for_insurance
from tools.adress import search_for_address
from tools.url import search_for_website
from  tools.phone_number import contact_number
from tools.revenue import search_for_revenue
from tools.specialitie import search_for_specialities
from tools.doctors import search_for_doctors
from Processthreads import HospitalDataExtractor
#Tools using Normal websearch and scraper techniques
# from prompts import adress_prompt , CONTACTPERSON_prompt , CONTACTNUMBER_prompt , analyze_extraction_results,URLWEBSITE_prompt , NETREVENUE_prompt , NOOFSPECIALTIES_prompt , NOOFDOCTORS_prompt , INSURANCESACCEPTED_prompt
# from helper import airtable_add , extract_validation_result , validate_hospital , create_category_queries , extract_urls_from_json , analyse_raw
#Agents
from main_agent_reporter import run_agent
from ProcessResult import process_single_hospital , process_hospital_batch

def main():
    st.set_page_config(page_title="Klaim Project", layout="wide")
    image_paths = [
        # Try relative paths
        "Company_image/2023-04-03.png",
        "2023-04-03.png",
        # Try absolute path for the deployed environment
        "/mount/src/klaimprojectv1.0/Company_image/2023-04-03.png",
    ]
    
    logo = None
    for path in image_paths:
        try:
            logo = Image.open(path)
            print(f"Successfully loaded image from: {path}")
            break
        except FileNotFoundError:
            continue
    st.image(logo, width=300, output_format="PNG")

    # Set up a column for the menu
    with st.container():
        selected = option_menu(
            menu_title=None,
            options=["Settings", "Dashboard", "Analytics"],
            icons=["gear", "speedometer2", "graph-up"],
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "0!important", 
                    "background-color": "#f8f9fa",
                    "border-radius": "10px", 
                    "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
                    "width": "100%"
                },
                "icon": {"color": "#4f46e5", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "center",
                    "margin": "0px",
                    "padding": "10px 15px",
                    "--hover-color": "#eef2ff",
                    "font-weight": "500",
                },
                "nav-link-selected": {"background-color": "#4f46e5", "color": "white", "border-radius": "7px"},
            },
        )
    if 'openai_key' not in st.session_state:
        st.session_state.openai_key = ""
    if 'serper_key' not in st.session_state:
        st.session_state.serper_key = ""
    st.markdown('</div>', unsafe_allow_html=True)
    if selected == "Settings" :
        st.header("Configuration")
        with st.form("api_keys_form"):
            openai_key = st.text_input("OpenAI API Key", 
                                      type="password", key="openai_key_input")
            serper_key = st.text_input("Serper API Key", 
                                      type="password", key="serper_key_input")
            submit_keys = st.form_submit_button("Save API Keys")
            if submit_keys:
                if openai_key:
                    st.session_state.openai_key = openai_key
                else:
                    st.session_state.openai_key = st.secrets["OPENAI_API_KEY"]

                if serper_key:
                    st.session_state.serper_key = serper_key
                else:
                    st.session_state.serper_key = st.secrets["SERPER_API_KEY"]
                    
                st.success("API keys saved!")

    
    if selected == "Dashboard" :

        tab1, tab2 = st.tabs(["Search a Single Hospital", "Upload a CSV File"])
        with tab1:
            with st.form("single_hospital_form"):
                hcp_name = st.text_input("Enter the name of the hospital or clinic:")
                submitted = st.form_submit_button("Research This Hospital")
                
                if submitted:
                    if hcp_name and len(hcp_name.strip()) > 0:
                        #Using openai web search 
                        # NETREVENUEYEARLY = search_for_revenue(hcp_name  , openai_key)
                        # NO_OF_SPECIALTIES = search_for_specialities(hcp_name, openai_key)
                        # NOOFDOCTORS = search_for_doctors(hcp_name , openai_key)
                        # INSURANCES_ACCEPTED = search_for_insurance(hcp_name , openai_key)
                        # URL_WEBSITE = search_for_website(hcp_name  , openai_key)
                        # CONTACT_PERSON_result=search_for_hospital_ceo(hcp_name , openai_key)
                        # ADDRESS_search_result= search_for_address(hcp_name  , openai_key)

                        result = process_single_hospital(hcp_name , st.session_state.openai_key , st.session_state.serper_key)
                        st.subheader("Research Results")
                        st.markdown(result)
                    else:
                        st.warning("Please enter a hospital or clinic name.")

        with tab2:
            st.write("Upload a CSV file with hospital names to research multiple facilities at once.")
            uploaded_file = st.file_uploader("Upload a CSV file with a column named 'HCP NAME'", type=["csv" , "xlsx"])   
            if uploaded_file is not None:
                try:

                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    st.write(f"File type: {file_extension}")
                    st.write(f"File size: {uploaded_file.size} bytes")                
                    if file_extension == 'xlsx' or file_extension == 'xls':
                        try:
                            uploaded_file.seek(0)
                            input_df = pd.read_excel(uploaded_file, engine='openpyxl')
                            st.success("Successfully read Excel file")
                        except Exception as e:
                            st.error(f"Error reading Excel file: {str(e)}")
                            
                    elif file_extension == 'csv':
                        uploaded_file.seek(0)
                        encodings_to_try = ['utf-8', 'latin-1', 'ISO-8859-1', 'cp1252']
                        for encoding in encodings_to_try:
                            try:

                                uploaded_file.seek(0)
                                input_df = pd.read_csv(uploaded_file, encoding=encoding)
                                st.success(f"Successfully read CSV file with encoding: {encoding}")
                                break
                            except UnicodeDecodeError:
                                continue
                            except Exception as e:
                                st.error(f"Error reading CSV with encoding {encoding}: {str(e)}")
                    if 'input_df' in locals() and not input_df.empty:
                        st.write("Available columns:", input_df.columns.tolist())
                        hcp_col = None
                        for col in input_df.columns:
                            if col.upper() == 'HCP NAME':
                                hcp_col = col
                                break
                        
                        if hcp_col is None:
                            st.error("The file must contain a column named 'HCP NAME'. Please check your file format.")
                        else:
                            st.write("Preview of uploaded data:")
                            hospital_count = len(input_df[hcp_col].dropna())
                            st.write(f"Found {hospital_count} hospitals to process.")
                            
                            if st.button("Start Processing Hospitals"):
                                hospital_list = input_df[hcp_col].dropna().tolist()                    
                                if not hospital_list:
                                    st.warning("No hospital names found in the file.")
                                else:
                                    with st.spinner(f"Processing {len(hospital_list)} hospitals..."):

                                        results = process_hospital_batch(hospital_list,  st.session_state.openai_key)

                                        results_df = pd.DataFrame(results)

                                        st.subheader("Research Results")
                                        st.dataframe(results_df)
                    else:
                        st.error("Could not read any data from the file. The file might be empty or in an unsupported format.")
                            
                except Exception as e:
                    st.error(f"Error processing the file: {str(e)}")
                    st.write("Please try uploading the file in CSV format if you're having issues with Excel.")  
                #     st.subheader("Research Report")
                #     st.markdown('################')
                #     st.markdown(run_agent(Final_data , openai_key))


        # elif 'submitted' not in locals() or not submitted:
        
        #         st.header("Research Results")
        #         st.info("Enter a research topic and click 'Research This Topic' to begin.")

    if selected == "Analytics" :
        st.write('Main Analytics ')
if __name__ == "__main__":
    main()

