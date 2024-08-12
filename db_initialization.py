import snowflake.connector as sc
import tab_config

import logging
logging.basicConfig(level=logging.DEBUG)

conn_params = {
    'account': 'vm08742.west-europe.azure',
    'user': 'HKOTARSKIIC27',
    'password': 'Ftrmnd_IC27'
}

ctx = sc.connect(**conn_params)
cs = ctx.cursor()

try:
    cs.execute("CREATE WAREHOUSE IF NOT EXISTS train_wh")
    cs.execute("CREATE DATABASE IF NOT EXISTS train_db")
    cs.execute("USE DATABASE train_db")
    cs.execute("CREATE SCHEMA IF NOT EXISTS train_schema")
    cs.execute("USE SCHEMA train_schema")
    cs.execute(tab_config.train_time_table_ddl)
    cs.execute(tab_config.stg_train_time_table_ddl)
finally:
    ctx.close()