import re
import pandas as pd
from minio import Minio
import re

def upload_to_minio(minio_client, bucket_name, object_name, file_path):
    try:
        minio_client.fput_object(bucket_name, object_name, file_path)
        print(f"Uploaded {object_name} to Minio")
    except Exception as e:
        print(f"Failed to upload {object_name} to Minio:", e)
    
def clean_text(text):
    pattern = r'[a-zA-Z0-9-/()[],.{}]+'
    return text.replace(f'[^{pattern}]', ' ')

def remove_special_characters(text):
    if type(text) == int or type(text) == float:
        return str(text)
    if type(text) != str:
        return ""
    return re.sub(  "[^a-zA-Z0-9\s()\[\]=,'\"]", ' ', text)

def clean_api_data(**context):
    df = []
    for k,v in context.items():
        if k == 'ti':
            df = context[k].xcom_pull(task_ids='extract_api_data')
    df = pd.DataFrame(df)

    minio_client = Minio(
        endpoint='minio:9000',
        access_key='OtqbQ3XWQFhk7kzxmryo',
        secret_key='UUqH5EKb706o27tI33qlhYZDnZKN3mWK1s23Xe2N',
        secure=False
    )
    
    file_path_to_upload = "/opt/airflow/data/api_data_csv/api_data.csv"
    bucket_name = "datapipeline"
    object_name = "data/api_data_csv/api_data.csv"
    
    df.dropna(inplace=True)
    
    for col in df.columns:
       df[col] = df[col].apply(remove_special_characters)
       print(f"Cleaning {col} column")
       print(df[col])

    df.to_csv(file_path_to_upload, index=False, encoding='utf-8')

    print(f"Saved data to {file_path_to_upload}api_data.csv")
    upload_to_minio(minio_client, bucket_name, object_name, file_path_to_upload)

    return  df
