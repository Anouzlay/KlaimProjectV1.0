import requests

data = {
            'hospital_name': 'Aldhaid hospital',
            'executives': [
                {'position': 'Chief Executive Officer', 'name': 'Salahudeen Aboobacker'}
            ]
        }

def send_data_into_people_base():
        url_people="https://api.clay.com/v3/sources/webhook/pull-in-data-from-a-webhook-d1692ecc-0247-4916-99bd-ebdc9e5fe60c"

        positions = []
        names = []

        for exec in data['executives']:
            payload = {
            'CEO_python' : exec['name'],
            "Position" :  exec['position'] ,
            "Domain" : "pearldentalclinics.com", #exec['position']
        }
            
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url_people, json=payload, headers=headers)



            print("Status Code:", response.status_code)
            print("Response:", response.text)



def send_data_into_company():
    url_company = "https://api.clay.com/v3/sources/webhook/pull-in-data-from-a-webhook-f0010c06-8241-42e6-9c6a-1530e02bfd1b"
    payload = {
        "name": data['hospital_name'],
        # "Domain" : "ehs.gov.ae"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url_company, json=payload, headers=headers)

    print("Status Code:", response.status_code)
    print("Response:", response.text)



# send_data_into_people_base()
send_data_into_company()