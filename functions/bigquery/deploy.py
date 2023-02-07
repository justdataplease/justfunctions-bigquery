import json
from google.cloud import bigquery
import yaml
import jinja2
import requests
import os
from dotenv import load_dotenv
from secrets import projects

load_dotenv()
TEMPLATE_FOLDER = "./templates"
functions_directory = './'


def get_keys(old_dict, selected_keys):
    return {key: old_dict[key] for key in selected_keys}


def construct_function(conf, project_id, dataset_id, function_name, filename):
    template_file = f'{TEMPLATE_FOLDER}/{conf["type"]}.sql'
    template = jinja2.Template(open(template_file, encoding='utf-8').read())
    query = template.render(
        project_id=project_id,
        dataset_id=dataset_id,
        function_name=function_name,
        filename=filename,
        **conf,
    )
    return query


def construct_example(conf, project_id, dataset_id, function_name, filename):
    if 'function' in conf["type"]:
        template_file = f'{TEMPLATE_FOLDER}/function_example.sql'
    template = jinja2.Template(open(template_file, encoding='utf-8').read())
    example_query = template.render(
        project_id=project_id,
        dataset_id=dataset_id,
        function_name=function_name,
        filename=filename,
        **conf,
    )

    example_output = conf['examples'][0]['output']
    return example_query, example_output


def deploy_function(conf, client, project_id, dataset_id, filename):
    statement = construct_function(conf=conf, project_id=project_id, dataset_id=dataset_id,
                                   function_name=filename.split(".")[0],
                                   filename=filename)

    example_query, example_output = construct_example(conf=conf, project_id=project_id, dataset_id=dataset_id,
                                                      function_name=filename.split(".")[0],
                                                      filename=filename)

    print(statement)
    # Run the query
    query_job = client.query(statement)
    query_job.result()
    # Check the status of the query job
    if query_job.state == 'DONE':
        print(f'Query job {query_job.job_id} completed successfully')
    else:
        print(f'Query job {query_job.job_id} failed')
    return statement, example_query, example_output


def deploy_all_functions(project_id, allow_private, datasets, cloud_storage_directory, specific=False):
    # Create a BigQuery client
    client = bigquery.Client(project=project_id)

    # Loop through the files in the directory
    documentation = []
    for folder in os.listdir(functions_directory):
        subdirectory = os.path.join(functions_directory, folder)
        if os.path.isdir(subdirectory):
            for filename in os.listdir(subdirectory):
                # Check if the file is a JSON file
                if filename.endswith('.yaml'):
                    # If we want to deploy specific function
                    if specific:
                        if not filename == specific:
                            continue

                    filepath = os.path.join(subdirectory, filename)
                    conf = yaml.safe_load(open(filepath, encoding='utf-8').read())
                    if not conf.get('production', True):
                        print(f"{filename} not for production")
                        continue
                    if conf.get('private'):
                        if not allow_private:
                            continue

                    conf['name'] = filename.split(".")[0]
                    conf['region'] = datasets
                    conf['github'] = f"[link]({conf.get('github')})" if conf.get('github') else ""
                    conf['source'] = f"[link]({conf.get('source')})" if conf.get('source') else ""
                    conf['tutorial'] = f"[link]({conf.get('tutorial')})" if conf.get('tutorial') else ""
                    conf['ftype'] = conf['type'].replace("function_", "").upper()
                    if conf.get('libraries'):
                        conf['libraries'] = [{"cloudstorage_url": f"{cloud_storage_directory}/{l['cloudstorage_url']}"} for l in conf['libraries']]
                    # Loop through different regions
                    for dataset_id in datasets:
                        conf['statement'], conf['example_query'], conf['example_output'] = deploy_function(conf=conf, client=client, project_id=project_id,
                                                                                                           dataset_id=dataset_id,
                                                                                                           filename=filename)
                    documentation.append(conf)
    return documentation


def process_documentation(documentation, doc_columns):
    if not doc_columns:
        doc_columns = ['name', 'ftype', 'source', 'tutorial', 'github', 'category', 'region', 'description', 'statement', 'example_query', 'example_output']
    res = [dict((k, doc.get(k)) for k in doc_columns
                if k in doc) for doc in documentation]
    return res


def deploy_airtable(res, base_id, table_name, api_key):
    url = "https://api.airtable.com/v0/" + base_id + "/" + table_name
    headers = {"Authorization": "Bearer " + api_key,
               "Content-Type": "application/json"}

    # Clean Table
    response = requests.get(url, headers=headers)
    records = response.json()["records"]
    for record in records:
        record_id = record["id"]
        delete_url = f"{url}/{record_id}"
        requests.delete(delete_url, headers=headers)

    # Write to table
    for r in res:
        upload_dict = {"records": [{"fields": r}]}
        upload_json = json.dumps(upload_dict)
        response = requests.post(url, data=upload_json, headers=headers)
        print(response.text)


if __name__ == "__main__":
    selected = []
    specific = ''
    if selected:
        projects_selected = get_keys(projects, selected)
    else:
        projects_selected = projects

    for project in projects_selected:
        project = projects[project]
        project_id = project['project_id']
        allow_private = project['allow_private']
        datasets = project['datasets']
        cloud_storage_directory = project['cloud_storage_directory']
        base_id = project['airtable_base_id']
        table_name = project['airtable_table_name']
        api_key = project['airtable_api_key']

        documentation = deploy_all_functions(project_id, allow_private, datasets, cloud_storage_directory, specific=specific)
        if not specific:
            documentation = process_documentation(documentation, doc_columns=project.get('doc_columns'))
            deploy_airtable(documentation, base_id, table_name, api_key)
