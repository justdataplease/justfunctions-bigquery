{{ function_name }}({% for argument in arguments %}{{ argument.name }}{% if not loop.last %}, {% endif %}{% endfor %})
