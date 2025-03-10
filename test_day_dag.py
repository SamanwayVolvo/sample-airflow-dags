from airflow import DAG, Dataset, XComArg, settings
from airflow.decorators import dag, task
from airflow.models import Connection, Variable
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.microsoft.azure.operators.data_factory import AzureDataFactoryRunPipelineOperator
from airflow.providers.microsoft.azure.sensors.data_factory import AzureDataFactoryPipelineRunStatusSensor
from airflow.providers.slack.operators.slack import SlackAPIPostOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeCheckOperator, SnowflakeOperator
from airflow.utils.task_group import TaskGroup
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from sqlalchemy.orm import exc
from typing import Any, Dict, List, Union, cast
from airflow.security import permissions

access_control = {
    # "Admin" : {
    "cld-dc-golden-path-sg" : {
        permissions.RESOURCE_DAG_RUN : { permissions.ACTION_CAN_READ, permissions.ACTION_CAN_CREATE },
        permissions.RESOURCE_DAG: { permissions.ACTION_CAN_READ, permissions.ACTION_CAN_EDIT }
    }
}

# @dag(start_date=datetime(2024, 2, 2), schedule_interval='@daily', catchup=False)
@dag(start_date=datetime(2024, 2, 2), schedule_interval='@daily', catchup=False, access_control=access_control)
def test_day_dag():

    # Define tasks
    task_1 = BashOperator(task_id='brush_teeth', bash_command='echo "Brushed teeth"', retries=3, retry_delay=timedelta(minutes=5))
    task_2 = BashOperator(task_id='eat_breakfast', bash_command='echo "Ate a healthy breakfast"', retries=3, retry_delay=timedelta(minutes=5))
    task_3 = BashOperator(task_id='exercise', bash_command='echo "Completed morning exercise"', retries=3, retry_delay=timedelta(minutes=5))

    # Define Python tasks using @task decorator
    @task
    def read_news():
        return 'Read the latest news headlines'

    @task
    def work_tasks():
        return 'Completed important work tasks'

    @task
    def relax():
        return 'Relaxed and took a break'

    # Define the final tasks
    @task
    def review_day(news, work, relaxation):
        print(f"News: {news}")
        print(f"Work: {work}")
        print(f"Relaxation: {relaxation}")

    # Set task dependencies
    task_1 >> task_2 >> task_3
    task_2 >> task_3

    # Set Python task dependencies
    news_result = read_news()
    work_result = work_tasks()
    relax_result = relax()

    # Set final task dependency
    review_day(news_result, work_result, relax_result)

test_day_dag()
