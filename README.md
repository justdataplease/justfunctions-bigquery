# JustFunctions for BigQuery

[![BigQuery](https://img.shields.io/badge/Platform-BigQuery-yellow.svg)](#)
[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](#)
[![Auto Deployment](https://img.shields.io/badge/Deployment-Auto-green)](#)
[![Documentation](https://img.shields.io/badge/Documentation-Markdown-blue)](#)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![UDFs Count](https://img.shields.io/badge/UDFs-Count-blue)](#)

Make your daily interaction with BigQuery easier
with [JustFunctions](https://justdataplease.com/justfunctions-bigquery/) - a collection of open-source functions (UDFs)
to extend BigQuery capabilities.
You can use them directly in any of your projects or auto-deploy them to your BigQuery and generate insightful markdown
documentation.

https://justdataplease.com/justfunctions-bigquery/

## Features

- **Comprehensive UDF Collection**: Extend your BigQuery capabilities with a diverse set of UDFs.
- **Auto Deployment**: No more manual deployments. Just run the script to deploy your SQL functions instantly to
  BigQuery.
- **Markdown Documentation**: Post deployment, auto-generate a comprehensive markdown documentation, detailing each
  function, its usage, and examples.
- **Recreation on Run**: Ensure you have the latest and greatest. Each run of the script recreates all functions and
  their corresponding documentation.

## Prerequisites

1. Google Cloud SDK installed and authenticated.
2. Google Cloud BigQuery Python SDK (`google-cloud-bigquery`).
3. `jinja2` for template rendering.
4. `PyYAML` to parse YAML files.

## Setup

1. Clone the repository and navigate to the root directory.
2. Install the required Python packages:
    ```bash
    pip install requirements.txt
    ```

3. Ensure you're authenticated with Google Cloud:
    ```bash
    gcloud auth login
    ```

4. Make sure you have the necessary BigQuery configurations set in the `projects` variable in `bigquery.secrets.py`.

## Usage

Run the main script:

```bash
python bigquery/deploy.py
```

✨ Explore the freshly deployed functions in BigQuery and refer to the locally-generated markdown documentation in functions_documentation.md! ✨

## Acknowledgments

Special thanks to [BigFunctions team](https://unytics.io/bigfunctions/) for their inspiring project.

## Join Us

Join us in our quest to make BigQuery even more powerful. If you have suggestions, UDFs to contribute, or any feedback,
feel free to get involved!

Created by the [JustDataPlease team](https://justdataplease.com).
