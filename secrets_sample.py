import os

projects = {
    'justfunctions': {
        "project_id": 'justfunctions',
        "datasets": ['us', 'eu'],
        "documentation_dataset_id": 'eu',
        "bucket_path": 'justfunctions/bigquery-functions',
        "cloud_storage_directory": 'gs://justfunctions/bigquery-functions',
        "allow_private": False,
        "airtable_base_id": os.getenv("AIRTABLE_BASE_ID"),
        "airtable_api_key": os.getenv("AIRTABLE_TOKEN"),
        "airtable_table_name": os.getenv("AIRTABLE_TABLE_ID"),
    }
}
