import requests
import json

def contact_number(hcp_name, person_name):
    url = f"https://api.apollo.io/api/v1/people/match?name={person_name}&organization_name={hcp_name}"

    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "x-api-key": "-LPEt-IYXa2hkePwKW0KbQ"
    }

    response = requests.post(url, headers=headers)
    print(response.text)

    try:
        json_res = response.json()
    except json.JSONDecodeError:
        return f"Invalid JSON response for {person_name}"

    person = json_res.get("person", {})
    person_name = person.get("name", person_name)

    org_phone = None
    person_phone = None

    # Only try to get org phone if 'organization' exists
    if "organization" in person:
        org_phone = person["organization"].get("primary_phone", {}).get("number")

    # Only try to get person phone if 'contact' and phone numbers exist
    if "contact" in person and person["contact"].get("phone_numbers"):
        person_phone = person["contact"]["phone_numbers"][0].get("raw_number")

    # Return logic
    if not org_phone and not person_phone:
        return person_name
    elif org_phone and person_phone:
        return {"organization_phone": org_phone, "person_phone": person_phone}
    elif org_phone:
        return {"organization_phone": org_phone}
    elif person_phone:
        return {"person_phone": person_phone}


# print(contact_number('AL AHLI HOSPITAL COMPANY LLC' , 'Khalid Al-Emadi'))