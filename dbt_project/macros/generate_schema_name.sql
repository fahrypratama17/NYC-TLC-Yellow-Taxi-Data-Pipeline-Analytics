-- Use the custom schema name from `+schema: …` verbatim, without the default
-- "{target.schema}_{custom_schema}" prefix. This lets the rest of the project
-- query e.g. `marts.fct_zone_features` directly, regardless of the target.

{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
