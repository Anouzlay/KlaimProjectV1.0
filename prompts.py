def adress_prompt(raw_text):
    return f'''
    ## CONTACT PERSON Extraction Prompt

    Extract the name and title of the primary contact person (CEO, MD, CFO, COO, or other leadership position) from the raw text = {raw_text}.

    **Instructions:**
    1. Identify individuals with executive titles: CEO, President, Chief Medical Officer, Medical Director, CFO, COO, Managing Director, Founder, or similar leadership positions.
    2. Return the full name followed by their title.
    3. Prioritize in this order: CEO/President > Medical Director/Chief Medical Officer > COO/CFO > Managing Director > Founder.
    4. Look for sections labeled "Leadership," "Our Team," "About Us," "Management," or "Executive Team."
    5. Ignore department heads, board members, or other staff unless they are the only leadership mentioned.
    6. If multiple qualified individuals are found, choose the highest-ranking person.
    7. Include professional designations (MD, PhD, etc.) if present.

    **Example Input:**
    ```
    Our dedicated team is led by Dr. Sarah Johnson, MD, FACS, who serves as our Chief Medical Officer. The administrative operations are overseen by Michael Williams, our Chief Operating Officer. Our board includes Dr. Robert Chen, Director of Cardiology, and Samantha Davis, Director of Nursing Services. For investor relations, please contact our CFO, Jennifer Lopez, at jlopez@medicalcenter.com.
    ```

    **Expected Output:**
    ```
    Dr. Sarah Johnson, MD, FACS - Chief Medical Officer
    ```

    **Result Counter:**
    - If a valid contact person is found, return the contact information followed by "\nEXTRACTION_SUCCESS: 1"
    - If no valid contact person is found, return "No leadership contact found in the provided text.\nEXTRACTION_SUCCESS: 0"

    **Expected Complete Output Example (success):**
    ```
    Dr. Sarah Johnson, MD, FACS - Chief Medical Officer
    EXTRACTION_SUCCESS: 1
    ```

    **Expected Complete Output Example (no match):**
    ```
    No leadership contact found in the provided text.
    EXTRACTION_SUCCESS: 0
    ```

    '''
def CONTACTPERSON_prompt(raw_text):
    return f'''
## CONTACT PERSON Extraction Prompt

Extract the name and title of the primary contact person (CEO, MD, CFO, COO, or other leadership position) from the raw text = {raw_text}.

**Instructions:**
1. Identify individuals with executive titles: CEO, President, Chief Medical Officer, Medical Director, CFO, COO, Managing Director, Founder, or similar leadership positions.
2. Return the full name followed by their title.
3. Prioritize in this order: CEO/President > Medical Director/Chief Medical Officer > COO/CFO > Managing Director > Founder.
4. Look for sections labeled "Leadership," "Our Team," "About Us," "Management," or "Executive Team."
5. Ignore department heads, board members, or other staff unless they are the only leadership mentioned.
6. If multiple qualified individuals are found, choose the highest-ranking person.
7. Include professional designations (MD, PhD, etc.) if present.

**Example Input:**
```
Our dedicated team is led by Dr. Sarah Johnson, MD, FACS, who serves as our Chief Medical Officer. The administrative operations are overseen by Michael Williams, our Chief Operating Officer. Our board includes Dr. Robert Chen, Director of Cardiology, and Samantha Davis, Director of Nursing Services. For investor relations, please contact our CFO, Jennifer Lopez, at jlopez@medicalcenter.com.
```

**Expected Output:**
```
Dr. Sarah Johnson, MD, FACS - Chief Medical Officer
```

**Result Counter:**
- If a valid contact person is found, return the contact information followed by "\nEXTRACTION_SUCCESS: 1"
- If no valid contact person is found, return "No leadership contact found in the provided text.\nEXTRACTION_SUCCESS: 0"

**Expected Complete Output Example (success):**
```
Dr. Sarah Johnson, MD, FACS - Chief Medical Officer
EXTRACTION_SUCCESS: 1
```

**Expected Complete Output Example (no match):**
```
No leadership contact found in the provided text.
EXTRACTION_SUCCESS: 0
```
    '''
def CONTACTNUMBER_prompt(raw_text):
    return f'''
    ## CONTACT NUMBER Extraction Prompt

    Extract the primary contact phone number for the healthcare facility or medical practice from the raw text = {raw_text}.

    **Instructions:**
    1. Identify the main contact telephone number (not fax, emergency, or department-specific numbers).
    2. Look for numbers labeled as "Main Line," "Reception," "Appointments," "Contact Us," or "General Inquiries."
    3. Preserve the original formatting including country code if available.
    4. Prioritize numbers near phrases like "Contact us," "Call us," "Phone," "Telephone," or "For appointments."
    5. If multiple numbers are found, prioritize in this order: Main/Reception > Appointments > General Contact.
    6. Ignore numbers specifically labeled as "Fax," "Billing," "Emergency," unless they are the only numbers available.
    7. If a toll-free number and local number are both provided, prioritize the toll-free number.

    **Example Input:**
    ```
    For general inquiries, please call (800) 555-1234. To schedule an appointment, dial (800) 555-9876. For billing questions: (800) 555-4321. Our fax number is (800) 555-8765. For emergencies, call 911.
    ```

    **Expected Output:**
    ```
    (800) 555-1234
    ```

    **Result Counter:**
    - If a valid contact number is found, return the number followed by "\nEXTRACTION_SUCCESS: 1"
    - If no valid contact number is found, return "No contact number found in the provided text.\nEXTRACTION_SUCCESS: 0"

    **Expected Complete Output Example (success):**
    ```
    (800) 555-1234
    EXTRACTION_SUCCESS: 1
    ```

    **Expected Complete Output Example (no match):**
```
No contact number found in the provided text.
EXTRACTION_SUCCESS: 0
```

    '''
def URLWEBSITE_prompt(raw_text):
    return f'''
 Extract the official website URL of the healthcare facility or medical practice from the raw text = {raw_text}.
Instructions:

Identify the main website URL (not social media, third-party listings, or affiliate sites).
Return the complete URL including protocol (http:// or https://).
If protocol is missing, assume https:// as the default.
Look for URLs near terms like "Website," "Visit our website," "Official site," or "Learn more at."
Prioritize domain names that match the facility/practice name.
Ignore URLs for appointment booking platforms, insurance portals, or review sites unless they are the only URLs available.
If multiple URLs are found, choose the one that appears to be the main website (typically shorter, cleaner URL).
Remove any tracking parameters or session IDs from the URL.

Example Input:
For more information about our services, visit our website at www.medicalpractice.com. Follow us on social media: facebook.com/medicalpractice, twitter.com/medicalpractice. Book appointments online through healthbooking.com/medicalpractice.
Expected Output:
https://www.medicalpractice.com
Result Counter:

If a valid website URL is found, return the URL followed by "\nEXTRACTION_SUCCESS: 1"
If no valid website URL is found, return "No website URL found in the provided text.\nEXTRACTION_SUCCESS: 0"

Expected Complete Output Example (success):
https://www.medicalpractice.com
EXTRACTION_SUCCESS: 1
Expected Complete Output Example (no match):
No website URL found in the provided text.
EXTRACTION_SUCCESS: 0
    '''
def NETREVENUE_prompt(raw_text):
    return f'''
    ## NET REVENUE/YEARLY Extraction Prompt

    Extract the annual net revenue/income figure for the healthcare facility or medical practice from the raw text = {raw_text}.

    **Instructions:**
    1. Identify financial figures explicitly labeled as "net revenue," "annual revenue," "yearly revenue," "net income," or similar terms.
    2. Look for the most recent fiscal year or calendar year data available.
    3. Include the currency symbol/code and the full amount with proper formatting.
    4. Look in sections like "Financial Information," "About Us," "Company Profile," "Annual Report," or "Investor Relations."
    5. If revenue ranges are given, report the specific range.
    6. If gross revenue is provided instead of net, specify this in your response.
    7. Pay attention to magnitude indicators like "million," "billion," or abbreviations like "M" or "B."
    8. Note the fiscal year or date of the reported figure if available.

    **Example Input:**
    ```
    Financial Highlights 2023: Memorial Hospital Group reported gross revenue of $175.4 million for the fiscal year ending December 31, 2023, with net revenue reaching $142.8 million, a 5% increase from the previous year. Operating expenses totaled $128.5 million, resulting in an operating profit of $14.3 million.
    ```

    **Expected Output:**
    ```
    $142.8 million (FY 2023)
    ```

    **Result Counter:**
    - If valid revenue information is found, return the revenue details followed by "\nEXTRACTION_SUCCESS: 1"
    - If no revenue information is found, return "No annual revenue information found in the provided text.\nEXTRACTION_SUCCESS: 0"

    **Expected Complete Output Example (success):**
    ```
    $142.8 million (FY 2023)
    EXTRACTION_SUCCESS: 1
    ```

    **Expected Complete Output Example (no match):**
    ```
    No annual revenue information found in the provided text.
    EXTRACTION_SUCCESS: 0
    ```
    '''
def NOOFSPECIALTIES_prompt(raw_text):
    return f'''
    ## NO. OF SPECIALTIES Extraction Prompt

    Extract the number of medical specialties offered by the healthcare facility or medical practice from the raw text = {raw_text}.

    **Instructions:**
    1. Identify distinct medical specialties, departments, or service lines mentioned.
    2. Count each unique specialty only once, even if mentioned multiple times.
    3. Look for sections labeled "Our Services," "Specialties," "Departments," "What We Offer," or "Areas of Expertise."
    4. Distinguish between true medical specialties and general services (e.g., "Cardiology" is a specialty, but "Preventive Care" is a general service).
    5. Sub-specialties within the same field should be counted separately (e.g., "Pediatric Cardiology" and "Adult Cardiology" count as two specialties).
    6. Focus on clinical specialties, not administrative departments.
    7. Return both the number and list of identified specialties.
    8. If specialties are grouped or categorized, ensure you're not double-counting.

    **Example Input:**
    ```
    At Metro Medical Center, we offer comprehensive care across multiple disciplines. Our specialties include Cardiology, Dermatology, Gastroenterology, Neurology, Obstetrics & Gynecology, Orthopedics, Pediatrics, and Urology. We also provide general services such as Primary Care, Preventive Medicine, and Wellness Programs. Our Cardiology department includes both Interventional Cardiology and Electrophysiology services.
    ```

    **Expected Output:**
    ```
    10 specialties: Cardiology, Interventional Cardiology, Electrophysiology, Dermatology, Gastroenterology, Neurology, Obstetrics & Gynecology, Orthopedics, Pediatrics, Urology
    ```

    **Result Counter:**
    - If specialties are found, return the count and list followed by "\nEXTRACTION_SUCCESS: 1"
    - If no specialties are found, return "No medical specialties found in the provided text.\nEXTRACTION_SUCCESS: 0"

    **Expected Complete Output Example (success):**
    ```
    10 specialties: Cardiology, Interventional Cardiology, Electrophysiology, Dermatology, Gastroenterology, Neurology, Obstetrics & Gynecology, Orthopedics, Pediatrics, Urology
    EXTRACTION_SUCCESS: 1
    ```

    **Expected Complete Output Example (no match):**
    ```
    No medical specialties found in the provided text.
    EXTRACTION_SUCCESS: 0
    ```
    '''
def NOOFDOCTORS_prompt(raw_text):
    return f'''
    ## NO. OF DOCTORS Extraction Prompt

    Extract the number of doctors/physicians affiliated with the healthcare facility or medical practice from the raw text= {raw_text}.

    **Instructions:**
    1. Identify explicit statements about the number of doctors, physicians, clinicians, or medical staff.
    2. Look for phrases like "Our team includes X doctors," "X physicians on staff," "medical team of X," etc.
    3. Include only medical doctors (MD, DO) and exclude other healthcare professionals unless specifically stated to count them.
    4. Look in sections labeled "Our Team," "Meet Our Doctors," "Medical Staff," "About Us," or similar.
    5. If an exact number isn't stated but individual doctors are listed, count them manually.
    6. Distinguish between full-time and part-time/visiting physicians if specified.
    7. If the text mentions both the total number and breaks it down by specialty, use the total number.
    8. If a range is provided, report the range (e.g., "50-60 physicians").

    **Example Input:**
    ```
    Lakeside Health Partners is proud of our team of 37 highly qualified healthcare professionals, including 28 board-certified physicians across various specialties, 5 nurse practitioners, and 4 physician assistants. Our medical staff includes specialists in cardiology (3), gastroenterology (4), internal medicine (8), family medicine (7), neurology (2), and psychiatry (4).
    ```

    **Expected Output:**
    ```
    28 doctors
    ```

    **Result Counter:**
    - If doctor count information is found, return the count followed by "\nEXTRACTION_SUCCESS: 1"
    - If no doctor count information is found, return "No information about doctor count found in the provided text.\nEXTRACTION_SUCCESS: 0"

    **Expected Complete Output Example (success):**
    ```
    28 doctors
    EXTRACTION_SUCCESS: 1
    ```

    **Expected Complete Output Example (no match):**
    ```
    No information about doctor count found in the provided text.
    EXTRACTION_SUCCESS: 0
    ```

    '''


def INSURANCESACCEPTED_prompt(raw_text):
    return f'''

    ## INSURANCES ACCEPTED Extraction Prompt

    Extract information about insurance plans accepted by the healthcare facility or medical practice from the raw text = {raw_text}.

    **Instructions:**
    1. Identify all insurance providers and plans explicitly mentioned as accepted.
    2. Look for sections labeled "Insurance," "Insurance Information," "Accepted Plans," "Financial Information," or "Payment Options."
    3. Include both the name of insurance companies and specific plans if mentioned.
    4. Report both the count of insurance companies and the full list.
    5. Pay attention to statements about "in-network" vs. "out-of-network" coverage.
    6. Note any mentions of government programs like Medicare, Medicaid, TRICARE, etc.
    7. Exclude insurance providers specifically listed as NOT accepted.
    8. If the text mentions "most major insurance plans" or similar without specifics, note this in your response.

    **Example Input:**
    ```
    Insurance Information: We accept most major insurance plans, including Aetna, Blue Cross Blue Shield (PPO and HMO plans), Cigna, Humana, and UnitedHealthcare. We also accept Medicare and Medicaid. We are currently out-of-network with Kaiser Permanente. For questions about your specific plan, please contact our billing department.
    ```

    **Expected Output:**
    ```
    7 insurance providers: Aetna, Blue Cross Blue Shield (PPO and HMO plans), Cigna, Humana, UnitedHealthcare, Medicare, Medicaid
    ```

    **Result Counter:**
    - If insurance information is found, return the count and list followed by "\nEXTRACTION_SUCCESS: 1"
    - If no insurance information is found, return "No information about accepted insurance plans found in the provided text.\nEXTRACTION_SUCCESS: 0"

    **Expected Complete Output Example (success):**
    ```
    7 insurance providers: Aetna, Blue Cross Blue Shield (PPO and HMO plans), Cigna, Humana, UnitedHealthcare, Medicare, Medicaid
    EXTRACTION_SUCCESS: 1
    ```

    **Expected Complete Output Example (no match):**
    ```
    No information about accepted insurance plans found in the provided text.
    EXTRACTION_SUCCESS: 0
    ```

    '''

def analyze_extraction_results(extraction_results, category_name):
    return f'''
    ## EXTRACTION RESULTS ANALYSIS PROMPT

    Analyze the following extracted data results for the category "{category_name}" and identify the most frequently occurring values:

    ```
    {extraction_results}
    ```

    ### INSTRUCTIONS:
    1. Identify all unique data values that appear in the extraction results
    2. Count how many times each unique value appears
    3. Rank the values by frequency (most frequent first)
    4. Return the top 5 most frequent values (or all if fewer than 5)
    5. For each value, include the exact text and the number of occurrences
    6. Format the results as a valid JSON object

    ### IMPORTANT GUIDELINES:
    - Normalize values before counting (ignore case differences, spacing)
    - Consider synonymous or nearly identical values as the same (e.g., "Blue Cross" and "BCBS")
    - For lists (like specialties or insurance providers), treat each full list as a unique value
    - If there are less than 5 unique values, return all available values
    - Ensure the JSON is properly formatted with quotes around keys and string values

    ### RESPONSE FORMAT:
    Return a JSON object with the following structure:

    ```json
    {{
      "category": "{category_name}",
      "total_extractions_analyzed": [number of extractions analyzed],
      "results": [
        {{
          "value": "most frequent value",
          "occurrences": number of times it appears,
          "confidence_score": decimal between 0.0 and 1.0
        }},
        {{
          "value": "second most frequent value",
          "occurrences": number of times it appears,
          "confidence_score": decimal between 0.0 and 1.0
        }},
        ... up to 5 values
      ]
    }}
    ```

    The confidence_score should be calculated as: occurrences / total_extractions_analyzed

    NOTE: Only return the JSON object, with no additional text before or after.
    '''