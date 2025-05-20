import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time

# Assuming these functions are defined elsewhere
from Processthreads import HospitalDataExtractor
from Validater_agents import extract_hospital_data


def process_single_hospital(hospital_name , openai_key , serper_api):
    with st.spinner(f"Researching {hospital_name}..."):
        extractor = HospitalDataExtractor(serper_api ,max_threads=10)
        optimize_data = extractor.run(hospital_name)
        final_data = extract_hospital_data(optimize_data, openai_key , serper_api)
        return final_data

# Function to process multiple hospitals from CSV
def process_hospital_batch(hospital_list , openai_key , serper_api):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_hospitals = len(hospital_list)
    
    for i, hospital in enumerate(hospital_list):
        status_text.text(f"Processing hospital {i+1}/{total_hospitals}: {hospital}")
        try:
            result = process_single_hospital(hospital, openai_key , serper_api)
            results.append(result)
        except Exception as e:
            results.append({
                'HCP NAME': hospital,
                'STATUS': 'Error',
                'ERROR_MESSAGE': str(e)
            })
        
        # Update progress
        progress_bar.progress((i + 1) / total_hospitals)
    
    status_text.text("Processing complete!")
    return results
