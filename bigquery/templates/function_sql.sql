CREATE OR REPLACE FUNCTION `{{ project_id }}.{{ dataset_id }}.{{ function_name }}`({% for argument in arguments %}`{{ argument.name }}` {{ argument.type}}{% if not loop.last %}, {% endif %}{% endfor %}) {% if output.type != 'any type' %}
  RETURNS {{ output.type }}{% endif %} AS ({{ code }})
  OPTIONS ( description = '''{{ description }}''')
