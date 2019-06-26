from behave import *

from pandas import DataFrame, Timestamp

use_step_matcher("parse")

# Distinct history of data linking two hubs is loaded into a link table


@given("I have a HUB_CUSTOMER table")
def step_impl(context):
    context.testdata.create_schema("DV_PROTOTYPE_DB", "TEST_VLT")
    context.testdata.drop_and_create("DV_PROTOTYPE_DB", "TEST_VLT", "HUB_CUSTOMER",
                                     ["CUSTOMER_PK VARCHAR(32) PRIMARY KEY", "CUSTOMERKEY VARCHAR(38)", "LOADDATE DATE",
                                      "SOURCE VARCHAR(4)"], materialise="table")
    context.testdata.insert_data_from_ct(context.table, "HUB_CUSTOMER", "TEST_VLT")


@step("I have a HUB_NATION table")
def step_impl(context):
    context.testdata.drop_and_create("DV_PROTOTYPE_DB", "TEST_VLT", "HUB_NATION",
                                     ["NATION_PK VARCHAR(32) PRIMARY KEY", "CUSTOMER_NATIONKEY VARCHAR(38)",
                                      "LOADDATE DATE", "SOURCE VARCHAR(4)"], materialise="table")
    context.testdata.insert_data_from_ct(context.table, "HUB_NATION", "TEST_VLT")


@step("I have an empty LINK_CUSTOMER_NATION table")
def step_impl(context):
    context.testdata.drop_and_create("DV_PROTOTYPE_DB", "TEST_VLT", "LINK_CUSTOMER_NATION",
                                     ["CUSTOMER_NATION_PK VARCHAR(32) PRIMARY KEY",
                                      ("CUSTOMER_PK VARCHAR(32) FOREIGN KEY REFERENCES "
                                       "DV_PROTOTYPE_DB.TEST_VLT.HUB_CUSTOMER(CUSTOMER_PK)"),
                                      ("NATION_PK VARCHAR(32) FOREIGN KEY REFERENCES "
                                       "DV_PROTOTYPE_DB.TEST_VLT.HUB_NATION(NATION_PK)"),
                                      "LOADDATE DATE", "SOURCE VARCHAR(4)"], materialise="table")


@step("I have data in the STG_CUSTOMER table")
def step_impl(context):
    context.testdata.drop_and_create("DV_PROTOTYPE_DB", "TEST_STG", "STG_CUSTOMER",
                                     ["CUSTOMER_PK VARCHAR(32)", "NATION_PK VARCHAR(32)",
                                      "CUSTOMER_NATION_PK VARCHAR(32)", "HASHDIFF VARCHAR(32)",
                                      "CUSTOMERKEY VARCHAR(38)", "CUSTOMER_NAME VARCHAR(25)",
                                      "CUSTOMER_PHONE VARCHAR(15)", "CUSTOMER_NATIONKEY NUMBER(38,0)",
                                      "SOURCE VARCHAR(4)", "LOADDATE DATE", "EFFECTIVE_FROM DATE"],
                                     materialise="table")
    context.testdata.insert_data_from_ct(context.table, "STG_CUSTOMER", "TEST_STG")


@step("I run the load to the link")
def step_impl(context):
    context.testdata.execute_sql_from_file(
        "/home/dev/PycharmProjects/SnowflakeDemo3/tests/features/helpers/sqlFiles/link_customer_nation_history_load.sql")


@step("only distinct records from the STG_CUSTOMER are loaded into the link")
def step_impl(context):
    table_df = context.testdata.context_table_to_df(context.table)
    result_df = DataFrame(context.testdata.get_table_data("DV_PROTOTYPE_DB.TEST_VLT.LINK_CUSTOMER_NATION"), dtype=str)

    if result_df.equals(table_df):
        assert True
    else:
        assert False

# Unchanged records in stage are not loaded into the link with pre-existing data


@given("there are records in the LINK_CUSTOMER_NATION table")
def step_impl(context):
    context.testdata.drop_and_create("DV_PROTOTYPE_DB", "TEST_VLT", "LINK_CUSTOMER_NATION",
                                     ["CUSTOMER_NATION_PK VARCHAR(32) PRIMARY KEY",
                                      ("CUSTOMER_PK VARCHAR(32) FOREIGN KEY REFERENCES "
                                       "DV_PROTOTYPE_DB.TEST_VLT.HUB_CUSTOMER(CUSTOMER_PK)"),
                                      ("NATION_PK VARCHAR(32) FOREIGN KEY REFERENCES "
                                       "DV_PROTOTYPE_DB.TEST_VLT.HUB_NATION(NATION_PK)"),
                                      "LOADDATE DATE", "SOURCE VARCHAR(4)"], materialise="table")
    context.testdata.insert_data_from_ct(context.table, "LINK_CUSTOMER_NATION", "TEST_VLT")


@step("only different or unchanged records are loaded to the link")
def step_impl(context):
    sql = "SELECT * FROM DV_PROTOTYPE_DB.TEST_VLT.LINK_CUSTOMER_NATION AS link ORDER BY link.LOADDATE;"
    table_df = context.testdata.context_table_to_df(context.table)
    result_df = DataFrame(context.testdata.general_sql_statement_to_df(sql), dtype=str)

    if result_df.equals(table_df):
        assert True
    else:
        assert False

# Only the first instance of a record is loaded into the link table for the history


@step("I have unchanged records but with different loaddates in the STG_CUSTOMER table")
def step_impl(context):
    context.testdata.drop_and_create("DV_PROTOTYPE_DB", "TEST_STG", "STG_CUSTOMER",
                                     ["CUSTOMER_PK VARCHAR(32)", "NATION_PK VARCHAR(32)",
                                      "CUSTOMER_NATION_PK VARCHAR(32)", "HASHDIFF VARCHAR(32)",
                                      "CUSTOMERKEY VARCHAR(38)", "CUSTOMER_NAME VARCHAR(25)",
                                      "CUSTOMER_PHONE VARCHAR(15)", "CUSTOMER_NATIONKEY NUMBER(38,0)",
                                      "SOURCE VARCHAR(4)", "LOADDATE DATE", "EFFECTIVE_FROM DATE"],
                                     materialise="table")
    context.testdata.insert_data_from_ct(context.table, "STG_CUSTOMER", "TEST_STG")


@step("only the first seen distinct records are loaded into the link")
def step_impl(context):
    table_df = context.testdata.context_table_to_df(context.table)
    result_df = DataFrame(context.testdata.get_table_data("DV_PROTOTYPE_DB.TEST_VLT.LINK_CUSTOMER_NATION"), dtype=str)

    if result_df.equals(table_df):
        assert True
    else:
        assert False