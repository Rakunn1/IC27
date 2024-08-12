import snowflake.connector as sc
import tab_config
import logging
#logging.basicConfig(level=logging.DEBUG)
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

conn_params = {
    'account': config['snowflake']['account'],
    'user': config['snowflake']['user'],
    'password': config['snowflake']['password']
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
