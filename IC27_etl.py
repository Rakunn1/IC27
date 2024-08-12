import random
import pandas as pd
import requests
from time import sleep
from datetime import datetime, timedelta
import snowflake.connector as sc
import pytz
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

conn_params = {
    'account': config['snowflake']['account'],
    'user': config['snowflake']['user'],
    'password': config['snowflake']['password'],
    'database': 'train_db',
    'warehouse': 'train_wh',
    'autocommit': 'false'
}


def validate_connection(conn_params):
    ctx = sc.connect(**conn_params)
    try:
        yield f'You are connected as {ctx.user}@{ctx.database}'
    except Exception as e:
        yield f'Connection FAILED'
        yield f'check connection parameters'
        yield f'{conn_params}'
        raise e
    finally:
        ctx.close()


def fetch_data(date, train_number=27):
    # returns a dataframe containing specific train run on a specific day
    # used in prepare_data()
    url = f"https://rata.digitraffic.fi/api/v1/trains/{date.strftime('%Y-%m-%d')}/{train_number}"
    yield f'Requesting: {url}'
    response = requests.get(url)
    if response.status_code == 200:
        fetched_data = pd.DataFrame(response.json())
        train_run_df = fetched_data[['trainNumber', 'departureDate']]
        train_time_table_df = pd.DataFrame(fetched_data['timeTableRows'][0])
        train_time_table_df.insert(0, 'trainNumber', train_run_df['trainNumber'].values[0])
        train_time_table_df.insert(1, 'departureDate', train_run_df['departureDate'].values[0])

        train_time_table_df['scheduledTime'] = pd.to_datetime(train_time_table_df['scheduledTime'])
        train_time_table_df['actualTime'] = pd.to_datetime(train_time_table_df['actualTime'], errors='coerce')

        train_time_table_df['actualTime'] = train_time_table_df['actualTime'].fillna(
            train_time_table_df['scheduledTime'] + pd.to_timedelta(train_time_table_df['differenceInMinutes'], unit='m')
        )

        train_time_table_df['actualTime'] = train_time_table_df['actualTime'].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        yield train_time_table_df
        yield f'Prepared data for: {train_run_df['departureDate'].values[0]}'
    else:
        yield f'API response FAILED with status code {response.status_code}'


def fetch_scheduled_time(day):
    # fetch scheduled time of arrival of train (default: IC27) at Tampere (UI Code 160)
    url = f"https://rata.digitraffic.fi/api/v1/trains/{day.strftime('%Y-%m-%d')}/27"
    response = requests.get(url)
    if response.status_code == 200:
        fetched_data = pd.DataFrame(response.json())
        data = pd.DataFrame(fetched_data['timeTableRows'][0])
        for index, row in data.iterrows():
            if row['stationUICCode'] == 160 and row['type'] == 'ARRIVAL':
                scheduledTime = row['scheduledTime']

    date = datetime.strptime(scheduledTime, '%Y-%m-%dT%H:%M:%S.%fZ')

    parsed_date = date.replace(tzinfo=pytz.utc)
    time_datetime = parsed_date.astimezone(pytz.timezone('Europe/Helsinki'))

    return time_datetime


def fetch_prediction_data():
    # fetch data for prediction, choose only time difference between actual and scheduled time
    # for thursdays arrivals at Tampere station
    query = """
    SELECT departure_date,
           DATEDIFF('second', scheduled_arrival_time, actual_arrival_time) AS time_difference
      FROM train_schema.train_time_table
     WHERE DAYNAME(departure_date) = 'Thu'
       AND type = 'ARRIVAL'
       AND station_code = 'TPE'
     ORDER BY departure_date
    """

    ctx = sc.connect(**conn_params)
    try:
        df = pd.read_sql(query, ctx)
    finally:
        ctx.close()

    return df['DEPARTURE_DATE'].values, df['TIME_DIFFERENCE'].values


def save_data(train_time_table_df):
    # merges dataframe provided to tables on train_db

    table_name = 'train_time_table'
    temp_table_name = 'stg_' + table_name

    merge_sql = f'''
        MERGE INTO {table_name} AS tgt
        USING (select * from(
                SELECT t.*, ROW_NUMBER() OVER (PARTITION BY TRAIN_NUMBER, DEPARTURE_DATE, T.station_ui_code, T.type ORDER BY departure_date) AS ROW_NUMBER
                  FROM train_schema.{temp_table_name}  t)
                where row_number = 1) AS src
           ON (tgt.train_number = src.train_number AND
               tgt.departure_date = src.departure_date AND
               tgt.station_ui_code = src.station_ui_code AND
               tgt.type = src.type)
         WHEN NOT MATCHED THEN
            INSERT (train_number, 
                    departure_date, 
                    station_code,
                    station_ui_code,
                    type,
                    scheduled_arrival_time,
                    actual_arrival_time) 
            VALUES (src.train_number, 
                    src.departure_date, 
                    src.station_code,
                    src.station_ui_code,
                    src.type,
                    src.scheduled_arrival_time,
                    src.actual_arrival_time);
    '''
    ctx = sc.connect(**conn_params)
    cs = ctx.cursor()

    try:
        cs.execute("USE SCHEMA train_schema")
        yield 'Switching to train_schema'
        yield 'Populating stage table...'
        cs.execute(f'TRUNCATE TABLE train_schema.{temp_table_name}')
        for _, row in train_time_table_df.iterrows():
            print(f"{row['trainNumber']}, '{row['departureDate']}', '{row['stationShortCode']}', {row['stationUICCode']}, '{row['type']}', '{row['scheduledTime']}', '{row['actualTime']}")
            cs.execute(f"""
            INSERT INTO {temp_table_name} (train_number, departure_date, station_code, station_ui_code, type, scheduled_arrival_time, actual_arrival_time)
            VALUES ({row['trainNumber']}, '{row['departureDate']}', '{row['stationShortCode']}', {row['stationUICCode']}, '{row['type']}', '{row['scheduledTime']}', '{row['actualTime']}')
            """)
        ctx.commit()
        yield 'DONE'
        yield 'Merging data...'
        cs.execute(merge_sql)
        ctx.commit()
        yield 'DONE'
    except Exception as e:
        yield f'ERROR: {e}'
        yield 'Rolling back last transaction...'
        ctx.rollback()
        raise e
    finally:
        ctx.close()


def wfl_fetch_period(start_date, end_date):
    # workflow to fetch data on demand for train runs for given period
    dates = pd.date_range(start=start_date, end=end_date)
    #dates = [date for date in dates if date.weekday()==3]

    def generate():
        train_time_table_df = pd.DataFrame()
        for message in validate_connection(conn_params):
            yield message

        for date in dates:
            fetched_data = None
            for step in fetch_data(date):
                if isinstance(step, str):
                    yield step
                    sleep(0.2)
                else:
                    fetched_data = step

                if fetched_data is not None:
                    train_time_table_df = pd.concat([train_time_table_df, fetched_data], ignore_index=True)

        for message in save_data(train_time_table_df):
            yield message
            sleep(0.2)

    return generate()
