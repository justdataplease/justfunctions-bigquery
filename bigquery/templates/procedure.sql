CREATE OR REPLACE PROCEDURE `{{ project_id }}.{{ dataset_id }}.{{ function_name }}`({% for argument in arguments %}{% if argument.out %}out {% endif %}`{{ argument.name }}` {{ argument.type}}{% if not loop.last %}, {% endif %}{% endfor %})
options(
    description = '''{{ description }}'''
)
BEGIN

{{ code }}

END;
