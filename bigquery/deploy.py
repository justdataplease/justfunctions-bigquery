from google.cloud import bigquery
import yaml
import jinja2
import os
from dotenv import load_dotenv
from secrets import projects
import copy

load_dotenv()
TEMPLATE_FOLDER = "./bigquery/templates"
functions_directory = './bigquery/'


def get_keys(old_dict, selected_keys):
    return {key: old_dict[key] for key in selected_keys}


def construct_function_name(conf, function_name):
    """
    Constructs function query
    :param conf:
    :param function_name:
    :return:
    """
    template_file = f'{TEMPLATE_FOLDER}/function_name.sql'
    template = jinja2.Template(open(template_file, encoding='utf-8').read())
    name = template.render(
        function_name=function_name,
        **conf,
    )
    return name


def construct_function(conf, project_id, dataset_id, function_name, filename):
    """
    Constructs function query
    :param conf:
    :param project_id:
    :param dataset_id:
    :param function_name:
    :param filename:
    :return:
    """
    conf_ = copy.deepcopy(conf)
    conf_['code'] = conf_['code'].replace("_project_id_", project_id).replace("_dataset_id_", dataset_id)
    template_file = f'{TEMPLATE_FOLDER}/{conf_["type"]}.sql'
    template = jinja2.Template(open(template_file, encoding='utf-8').read())
    query = template.render(
        project_id=project_id,
        dataset_id=dataset_id,
        function_name=function_name,
        filename=filename,
        **conf_,
    )
    return query


def construct_example(conf, project_id, dataset_id, function_name, filename):
    """
    Constructs an example for documentation
    :param conf:
    :param project_id:
    :param dataset_id:
    :param function_name:
    :param filename:
    :return:
    """
    if 'function' in conf["type"]:
        template_file = f'{TEMPLATE_FOLDER}/function_example.sql'
        template_file_overview = f'{TEMPLATE_FOLDER}/function_example_overview.sql'
    elif 'procedure' in conf["type"]:
        template_file = f'{TEMPLATE_FOLDER}/procedure_example.sql'
        template_file_overview = f'{TEMPLATE_FOLDER}/function_example_overview.sql'

    template = jinja2.Template(open(template_file, encoding='utf-8').read())
    template_file_overview = jinja2.Template(open(template_file_overview, encoding='utf-8').read())

    example_query = template.render(
        project_id=project_id,
        dataset_id=dataset_id,
        function_name=function_name,
        filename=filename,
        **conf,
    )

    example_output = conf['examples'][0]['output']

    example_overview = template_file_overview.render(
        project_id=project_id,
        dataset_id=dataset_id,
        function_name=function_name,
        filename=filename,
        out=example_output,
        **conf,
    )

    return example_query, example_output, example_overview


def deploy_function(conf, client, project_id, dataset_id, filename):
    """
    Deploy function to BigQuery
    :param conf:
    :param client:
    :param project_id:
    :param dataset_id:
    :param filename:
    :return:
    """
    statement = construct_function(conf=conf, project_id=project_id, dataset_id=dataset_id,
                                   function_name=filename.split(".")[0],
                                   filename=filename)

    example_query, example_output, example_overview = construct_example(conf=conf, project_id=project_id,
                                                                        dataset_id=dataset_id,
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
    return statement, example_query, example_output, example_overview


def deploy_all_functions(project_id, allow_private, datasets, cloud_storage_directory, specific=False):
    """
    Procedure to deploy all functions to BigQuery
    :param project_id:
    :param allow_private:
    :param datasets:
    :param cloud_storage_directory:
    :param specific:
    :return:
    """
    # Create a BigQuery client (you need to install gcloud CLI and perform gcloud auth login)
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
                            print(f"{filename} not specific")
                            continue

                    filepath = os.path.join(subdirectory, filename)
                    conf = yaml.safe_load(open(filepath, encoding='utf-8').read())
                    if not conf.get('production', True):
                        print(f"{filename} not for production")
                        continue
                    if conf.get('private'):
                        if not allow_private:
                            print(f"{filename} not private")
                            continue

                    conf['title'] = construct_function_name(conf=conf, function_name=filename.split(".")[0])
                    conf['slug'] = filename.split(".")[0]
                    conf['tags'] = conf['category']
                    conf['region'] = ",".join(datasets)
                    conf['github'] = f"[link]({conf.get('github')})" if conf.get('github') else ""
                    conf['source'] = f"[link]({conf.get('source')})" if conf.get('source') else ""
                    conf['tutorial'] = f"[link]({conf.get('tutorial')})" if conf.get('tutorial') else ""
                    conf['ftype'] = conf['type'].replace("function_", "").upper()
                    if conf.get('libraries'):
                        conf['libraries'] = [{"cloudstorage_url": f"{cloud_storage_directory}/{l['cloudstorage_url']}"}
                                             for l in conf['libraries']]
                    # Loop through different regions
                    for dataset_id in datasets:
                        conf['statement'], conf['example_query'], conf['example_output'], conf[
                            'example_overview'] = deploy_function(conf=conf,
                                                                  client=client,
                                                                  project_id=project_id,
                                                                  dataset_id=dataset_id,
                                                                  filename=filename)
                    documentation.append(conf)
    return documentation


def process_documentation(documentation, doc_columns):
    """
    Keep only specific columns for documentation
    :param documentation:
    :param doc_columns:
    :return:
    """
    if not doc_columns:
        doc_columns = ['title', 'slug', 'ftype', 'source', 'tutorial', 'tags', 'github', 'region',
                       'description',
                       'statement', 'example_query', 'example_output', 'example_overview']
    res = [dict((k, doc.get(k)) for k in doc_columns
                if k in doc) for doc in documentation]
    return res


def create_md_file(functions_list, filename='functions_documentation.md'):
    """
    Creates an md file from scratch
    :param functions_list:
    :param filename:
    :return:
    """
    with open(filename, 'w', encoding='utf-8') as md_file:
        md_file.write("# Documentation for BigQuery Open Source library of UDFs Functions and Procedures | by JustDataPlease\n\n")

        # Contents Section
        md_file.write("## Contents\n")
        for idx, func in enumerate(functions_list, 1):
            link_slug = func['slug']  # assuming slug can be used as the ID for links
            md_file.write(f"{idx}. [{func['title']}](#{link_slug})\n")
        md_file.write("\n---\n")

        for idx, func in enumerate(functions_list, 1):
            link_slug = func['slug']
            md_file.write(f"## <a id='{link_slug}'></a>{idx}. {func['title']}\n\n")
            if func.get('ftype'):
                md_file.write(f"- **Type**: {func['ftype']}\n")
            if func.get('tags'):
                md_file.write(f"- **Tags**: {', '.join(func['tags'])}\n")
            if func.get('region'):
                md_file.write(f"- **Region**: {func['region']}\n")
            if func.get('description'):
                md_file.write(f"- **Description**: {func['description']}\n\n")
            if func.get('statement'):
                md_file.write("```sql\n")
                md_file.write(func['statement'])
                md_file.write("\n```\n")
            if func.get('example_query'):
                md_file.write(f"**Example Query**:\n\n```sql\n{func['example_query']}\n```\n")
                md_file.write(f"\n**Example Output**:\n\n```\n{func['example_output']}\n```\n")
            md_file.write("---\n")

    print(f"Documentation has been written to {filename}")


def run():
    # Deploy functions to BigQuery
    try:
        selected = []
        specific = False
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

            documentation = deploy_all_functions(project_id, allow_private, datasets, cloud_storage_directory,
                                                 specific=specific)
    except Exception as exc:
        raise exc

    # Write documentation
    doc_columns = ['title', 'slug', 'ftype', 'source', 'tutorial', 'tags', 'github', 'region', 'description',
                   'statement', 'example_query', 'example_overview', 'example_output']

    data = process_documentation(documentation, doc_columns)
    create_md_file(data)

    # Write documentation for GPT
    doc_columns = ['title', 'slug', 'ftype', 'source', 'tutorial', 'tags', 'github', 'region', 'description',
                   'example_query', 'example_overview', 'example_output']
    data = process_documentation(documentation, doc_columns)
    create_md_file(data, filename="functions_documentation_gpt.txt")

    print("Finished")


if __name__ == '__main__':
    run()
