import re
from minio import Minio
import pandas as pd
from ast import literal_eval

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

def divide_data(**context):
    
    df = context['ti'].xcom_pull(task_ids='concat_data')
    
    minio_client = Minio(
        endpoint='minio:9000',
        access_key='OtqbQ3XWQFhk7kzxmryo',
        secret_key='UUqH5EKb706o27tI33qlhYZDnZKN3mWK1s23Xe2N',
        secure=False
    )
    
    file_path_to_upload = "/opt/airflow/data/"
    bucket_name = "datapipeline"
    database_file_path = "data/"
    
    title_keywords_year(df, file_path_to_upload)
    title_affiliation(df, file_path_to_upload)
    
    # upload_to_minio(minio_client, bucket_name, database_file_path + 'title_keywords.csv', file_path_to_upload + 'title_keywords.csv')
    
    # upload_to_minio(minio_client, bucket_name, database_file_path + 'title_affiliation.csv', file_path_to_upload + 'title_affiliation.csv')

def title_keywords_year(df, file_path_to_upload):

    df = pd.DataFrame(df)
    df.drop(columns=['affiliation_country','affiliation_name'], inplace=True)

    for index, row in df.iterrows():
        keywords = row['keywords']
        if len(keywords) > 2:
            l = keywords[1:-1].split(',')
            l = [x.strip() for x in l]
            df.at[index, 'keywords'] = l
        else:
            df.at[index, 'keywords'] = []

    df_affiliation_name_expanded = df.explode('keywords')
    
    df_affiliation_name_expanded.dropna(subset=['keywords'], inplace=True)

    new_df = pd.DataFrame({
        'title': df_affiliation_name_expanded['title'].tolist() ,
        'keyword': df_affiliation_name_expanded['keywords'].tolist() ,
        'publication_year': df_affiliation_name_expanded['publication_year'],
    })

    # Loop through each column and each row, and apply the function
    for col in new_df.columns:
        new_df[col] = new_df[col].apply(remove_special_characters)
    
    new_df.to_csv(file_path_to_upload + 'title_keywords.csv', index=False)
    return new_df

def string_to_list(column, index, df, column_name):
    if len(column) > 2:
        l = column[1:-1].split(',')
        l = [x.strip() for x in l]
        df.at[index, column_name] = l
    else:
        df.at[index, column_name] = []

def title_affiliation(df, file_path_to_upload):

    df = pd.DataFrame(df)
    df.drop(columns=['publication_year'], inplace=True)
    
    print(df['affiliation_name'])
    print(df['affiliation_country'])

    # print(df_affiliation_name_expanded.head()['affiliation_name'], len(df_affiliation_name_expanded))
    # print(df_affiliation_country_expanded.head()['affiliation_country'], len(df_affiliation_country_expanded))

    # new_df = pd.DataFrame({
    #     'title': df_affiliation_name_expanded['title'].tolist(),
    #     'affiliation_name': df_affiliation_name_expanded['affiliation_name'].tolist(),
    #     'affiliation_country': df_affiliation_country_expanded['affiliation_country'].tolist(),
    #     'keywords': df_affiliation_name_expanded['keywords'].tolist(),
    # })

    # new_df.dropna(subset=['affiliation_name'], inplace=True)
    # new_df.dropna(subset=['affiliation_country'], inplace=True)
    
    # # print(new_df.head()['affiliation_name'])
    # grouped_df = new_df.groupby(['title', 'affiliation_name', 'affiliation_country', 'keywords']).size().reset_index(name='count')

    # print(grouped_df.head()['affiliation_name'])