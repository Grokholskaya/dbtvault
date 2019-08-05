{{config(materialized='incremental', schema='VLT', enabled=true, tags='static')}}

{% set hub_columns = 'CAST(stg.SUPPLIER_PK AS BINARY(16)) AS SUPPLIER_PK, 
CAST(stg.SUPPLIERKEY AS NUMBER(38,0)) AS SUPPLIERKEY, 
CAST(stg.LOADDATE AS DATE) AS LOADDATE, 
CAST(stg.SOURCE AS VARCHAR(4)) AS SOURCE' %}
{% set stg_columns1 = 'b.SUPPLIER_PK, 
b.SUPPLIERKEY, 
b.LOADDATE, 
b.SOURCE' %}
{% set stg_columns2 = 'a.SUPPLIER_PK, 
a.SUPPLIERKEY, 
a.LOADDATE, 
a.SOURCE' %}
{% set hub_pk = 'SUPPLIER_PK' %}
{% set stg_name = 'v_stg_inventory' %}

{{ hub_template(hub_columns, stg_columns1, hub_pk) }}

{% if is_incremental() %}

(select
 {{stg_columns2}} 
from {{ref(stg_name)}} as a 
left join {{this}} as c on a.{{hub_pk}}=c.{{hub_pk}} and c.{{hub_pk}} is null) as b) as stg 
where stg.{{hub_pk}} not in (select {{hub_pk}} from {{this}}) and stg.FIRST_SEEN is null

{% else %}

{{ref(stg_name)}} as b) as stg where stg.FIRST_SEEN is null

{% endif %}