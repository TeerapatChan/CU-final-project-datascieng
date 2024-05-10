from io import BytesIO
import os
import requests, json
from minio import Minio

def upload_to_minio(minio_client, bucket_name, object_name, file_path):
    try:
        minio_client.fput_object(bucket_name, object_name, file_path)
        print(f"Uploaded {object_name} to Minio")
    except Exception as e:
        print(f"Failed to upload {object_name} to Minio:", e)

def fetch_data(idx, apiKey, last_page, pages):
    dois = []
    public_year = 2018
    affiliation = "chulalongkorn%20niversity"
    country = "thailand"
    for i in range(last_page,pages):
        URL = f"https://api.elsevier.com/content/search/scopus?query=AFFILCOUNTRY({country})%20AND%20AFFILORG({affiliation})%20AND%20PUBYEAR%20<%20{public_year}&apiKey={apiKey}&start={str(idx * i)}&httpAccept=application/json"
        response = requests.get(URL)

        if response.status_code == 200:
            for j in range(idx):
                if 'prism:doi' in response.json()["search-results"]['entry'][j]:
                    doi = response.json()["search-results"]['entry'][j]['prism:doi']
                    dois.append(doi)
        else:
            print('Failed to retrieve data:', response.status_code)
        print(f"Retrieved data for page {i}")
    return dois

def get_api_data():
    apiKey = "94da3310047d027793b893cf94e4f374"

    minio_client = Minio(
        endpoint='minio:9000',
        access_key='OtqbQ3XWQFhk7kzxmryo',
        secret_key='UUqH5EKb706o27tI33qlhYZDnZKN3mWK1s23Xe2N',
        secure=False
    )
    idx = 25
    first_page = 0
    num_pages = 40
    dois = fetch_data(idx, apiKey, first_page, first_page + num_pages)
    bucket_name = "datapipeline"

    for i in range(len(dois)):
        research_data = requests.get('https://api.elsevier.com/content/abstract/DOI:' + dois[i] + '?apiKey=' + apiKey + '&view=FULL&httpAccept=application/json')

        if not os.path.exists('/opt/airflow/data/api_data_json'):
            os.makedirs('/opt/airflow/data/api_data_json')
            
        file_path = f"/opt/airflow/data/api_data_json/research_{i}.json"
        object_name = f"data/api_data_json/research_{i}.json"
        if research_data.status_code == 200:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(research_data.json(), f)
            
            upload_to_minio(minio_client, bucket_name, object_name, file_path)
        else:
            print('Failed to retrieve data:', research_data.status_code)
