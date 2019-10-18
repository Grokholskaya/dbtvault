{#- Copyright 2019 Business Thinking LTD. trading as Datavault

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
-#}
{%- macro sat_template(src_pk, src_hashdiff, src_payload,
                       src_eff, src_ldts, src_source,
                       tgt_pk, tgt_hashdiff, tgt_payload,
                       tgt_eff, tgt_ldts, tgt_source,
                       source) -%}
-- Generated by dbtvault. Copyright 2019 Business Thinking LTD. trading as Datavault
{%- set tgt_cols = dbtvault.get_col_list([tgt_pk, tgt_hashdiff, tgt_payload,
                                          tgt_eff, tgt_ldts, tgt_source])  %}

SELECT DISTINCT {{ dbtvault.cast([tgt_hashdiff, tgt_pk, tgt_payload, tgt_ldts, tgt_eff, tgt_source], 'e') }}
FROM {{ source[0] }} AS e
{% if is_incremental() -%}
LEFT JOIN (
    SELECT {{ dbtvault.prefix(tgt_cols, 'd') }}
    FROM (
          SELECT {{ dbtvault.prefix(tgt_cols, 'c') }},
          CASE WHEN RANK()
          OVER (PARTITION BY {{ dbtvault.prefix([tgt_pk|last], 'c') }}
          ORDER BY {{ dbtvault.prefix([tgt_ldts|last], 'c') }} DESC) = 1
          THEN 'Y' ELSE 'N' END CURR_FLG
          FROM (
            SELECT {{ dbtvault.prefix(tgt_cols, 'a') }}
            FROM {{ this }} as a
            JOIN {{ source[0] }} as b
            ON {{ dbtvault.prefix([tgt_pk|last], 'a') }} = {{ dbtvault.prefix([src_pk], 'b') }}
          ) as c
    ) AS d
WHERE d.CURR_FLG = 'Y') AS src
ON {{ dbtvault.prefix([tgt_hashdiff|last], 'src') }} = {{ dbtvault.prefix([src_hashdiff], 'e') }}
WHERE {{ dbtvault.prefix([tgt_hashdiff|last], 'src') }} IS NULL
{%- endif -%}

{% endmacro %}