import os
from dotenv import load_dotenv

projects = {
    'justfunctions': {
        "project_id": 'justfunctions',
        "datasets": ['us', 'eu'],
        "bucket_path": 'justfunctions/bigquery-functions',
        "cloud_storage_directory": 'gs://justfunctions/bigquery-functions',
        "allow_private": False,
    }
}
