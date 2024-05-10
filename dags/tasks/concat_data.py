from glob import glob
import re
from minio import Minio
import pandas as pd

def remove_special_characters(text):
    if type(text) == int or type(text) == float:
        return str(text)
    if type(text) != str:
        return ""
    return re.sub(r"[^a-zA-Z0-9\s()\[\]=,'\"]", ' ', text)

def upload_to_minio(minio_client, bucket_name, object_name, file_path):
    try:
        minio_client.fput_object(bucket_name, object_name, file_path)
        print(f"Uploaded {object_name} to Minio")
    except Exception as e:
        print(f"Failed to upload {object_name} to Minio:", e)
        
def concat_data(**context):

    df = context['ti'].xcom_pull(task_ids='clean_api_data')
    print(df['publication_year'])
    minio_client = Minio(
        endpoint='minio:9000',
        access_key='OtqbQ3XWQFhk7kzxmryo',
        secret_key='UUqH5EKb706o27tI33qlhYZDnZKN3mWK1s23Xe2N',
        secure=False
    )
    
    file_path_to_upload = "/opt/airflow/data/database.csv"
    bucket_name = "datapipeline"
    database_file_path = "data/database.csv"
    
    minio_client.fget_object(bucket_name, database_file_path, file_path_to_upload)
    
    database = pd.read_csv(file_path_to_upload)
    
    database = pd.concat([database, df], ignore_index=True)
    database.drop_duplicates(subset=['title'], keep='first', inplace=True)

    # for col in database.columns:
    #     database[col] = database[col].apply(remove_special_characters)
        
    database.to_csv(file_path_to_upload, index=False)

    upload_to_minio(minio_client, bucket_name, database_file_path, file_path_to_upload)


    return database
    
    
# This function is used only one time to concatenate all the raw data into a single file
# You need to prepare the raw data files before running this function to the path airflow_data/raw_data_csv
def concat_raw_data():
    df = pd.concat([pd.read_csv(f) for f in glob('airflow_data/raw_data_csv/*.csv')], ignore_index=True)
    df = df.map(lambda x: re.sub(r'[^\x00-\x7F]+', '', x) if isinstance(x, str) else x)
    for col in df.columns:
        df[col] = df[col].apply(remove_special_characters)
    df.to_csv('airflow_data/database.csv', index=False)

