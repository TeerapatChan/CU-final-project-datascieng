import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from tasks.get_api_data import get_api_data
from tasks.extract_data import extract_api_data
from tasks.clean_data import clean_api_data
from tasks.concat_data import concat_data
from tasks.divide_data import divide_data

default_args = {
    'owner': 'airflow',
    'start_date': datetime.datetime(2024, 5, 7),
    'retries': 3,
    'provide_context': True,
}

with DAG(
    'data_pipeline',
    default_args=default_args,
    description='A data pipeline for preparing data to visualization',
    schedule_interval=None,
) as dag:
    
    start = DummyOperator(task_id='start')
    
    get_api_data = PythonOperator(
        task_id='get_api_data',
        python_callable=get_api_data,
    )
    
    extract_api_data = PythonOperator(
        task_id='extract_api_data',
        python_callable=extract_api_data,
        provide_context=True,
    )
    
    clean_api_data = PythonOperator(
        task_id='clean_api_data',
        python_callable=clean_api_data,
        provide_context=True,
    )
    
    concat_data = PythonOperator(
        task_id='concat_data',
        python_callable=concat_data,
        provide_context=True,
    )
    
    divide_data = PythonOperator(
        task_id='divide_data',
        python_callable=divide_data,
        provide_context=True,
    )

    end = DummyOperator(task_id='end')
    
start >> get_api_data >> extract_api_data  >> clean_api_data >> concat_data >> divide_data >> end