import json
from glob import glob
import os
import pprint
import pandas as pd
from minio import Minio

def upload_to_minio(minio_client, bucket_name, object_name, file_path):
    try:
        minio_client.fput_object(bucket_name, object_name, file_path)
        print(f"Uploaded {object_name} to Minio")
    except Exception as e:
        print(f"Failed to upload {object_name} to Minio:", e)
    


def extract_api_data(**context):
    minio_client = Minio(
        endpoint='minio:9000',
        access_key='OtqbQ3XWQFhk7kzxmryo',
        secret_key='UUqH5EKb706o27tI33qlhYZDnZKN3mWK1s23Xe2N',
        secure=False
    )
    bucket_name = "datapipeline"
    extracted_data = []
    
    for obj in minio_client.list_objects(bucket_name, prefix='data/api_data_json/'):
        data = minio_client.get_object(bucket_name, obj.object_name)
        try:
            loaded_data = json.load(data)
            print(f"Extracting data from {obj.object_name}")
            citation_title = loaded_data.get("abstracts-retrieval-response", {}).get("item", {}).get("bibrecord", {}).get("head", {}).get("citation-title", None)
            affiliation = loaded_data.get("abstracts-retrieval-response", {}).get("affiliation", {})
            affiliation_name = []
            affiliation_country = []
            if affiliation and isinstance(affiliation, list):
                for aff in affiliation:
                    aff_name = aff.get("affilname", None)
                    aff_country = aff.get("affiliation-country", {})
                    affiliation_name.append(aff_name)
                    affiliation_country.append(aff_country)
            elif affiliation and isinstance(affiliation, dict):
                aff_name = affiliation.get("affilname", None)
                aff_country = affiliation.get("affiliation-country", {})
                affiliation_name.append(aff_name)
                affiliation_country.append(aff_country)
                
            publication_year = loaded_data.get("abstracts-retrieval-response", {}).get("coredata", {}).get("prism:coverDate", None)
            
            keywords = []
            raw_keywords = loaded_data["abstracts-retrieval-response"]["authkeywords"]
            
            if raw_keywords:
                if isinstance(raw_keywords["author-keyword"], list):
                    for k in raw_keywords["author-keyword"]:
                        keywords.append(k["$"])
                else:
                    keywords.append(raw_keywords["author-keyword"]["$"])

            print(publication_year.split("-")[0])
            extracted_data.append({
                "title": citation_title,
                "affiliation_name": affiliation_name,
                "affiliation_country": affiliation_country,
                "publication_year": publication_year.split("-")[0],
                "keywords": keywords,
            })
            print(f"Extracted data from {obj.object_name}")
        except Exception as e:
            print(f"Failed to extract data from {obj.object_name}:", e)
    df = pd.DataFrame(extracted_data)
    return df

def extract_raw_data(file_path):
    extracted_data = []
    for f_name in glob(file_path+'*'):
        with open(f_name, encoding='utf-8') as f:
            loaded_data = json.load(f)
            citation_title = loaded_data.get("abstracts-retrieval-response", {}).get("item", {}).get("bibrecord", {}).get("head", {}).get("citation-title", None)
            affiliation = loaded_data.get("abstracts-retrieval-response", {}).get("affiliation", {})
            affiliation_name = []
            affiliation_country = []
            if affiliation and isinstance(affiliation, list):
                for aff in affiliation:
                    aff_name = aff.get("affilname", None)
                    aff_country = aff.get("affiliation-country", {})
                    affiliation_name.append(aff_name)
                    affiliation_country.append(aff_country)
            elif affiliation and isinstance(affiliation, dict):
                aff_name = affiliation.get("affilname", None)
                aff_country = affiliation.get("affiliation-country", {})
                affiliation_name.append(aff_name)
                affiliation_country.append(aff_country)
                
            publication_year = loaded_data.get("abstracts-retrieval-response", {}).get("coredata", {}).get("prism:coverDate", None)
            
            keywords = []
            raw_keywords = loaded_data["abstracts-retrieval-response"]["authkeywords"]
            
            if raw_keywords:
                if isinstance(raw_keywords["author-keyword"], list):
                    for k in raw_keywords["author-keyword"]:
                        keywords.append(k["$"])
                else:
                    keywords.append(raw_keywords["author-keyword"]["$"])

            extracted_data.append({
                "title": citation_title,
                "affiliation_name": affiliation_name,
                "affiliation_country": affiliation_country,
                "publication_year": publication_year.split("-")[0],
                "keywords": keywords,
            })
    return extracted_data

# This function used only one time to extract data from raw json files and save it to csv
# You need to prepare the data before running this function to the path data/2018, data/2019, data/2020, data/2021, data/2022, data/2023
def raw_json_data_to_csv():
    file_paths = ['data/2018/', 'data/2019/', 'data/2020/', 'data/2021/', 'data/2022/', 'data/2023/']
    
    for file_path in file_paths:
        extracted_data = extract_raw_data(file_path)
        df = pd.DataFrame(extracted_data)
        df.to_csv(f'airflow_data/raw_data_csv/{file_path.split("/")[-2]}.csv', index=False)
        print(f"Saved {file_path.split('/')[-2]}.csv")
