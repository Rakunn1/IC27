train_time_table_ddl = """
CREATE OR REPLACE TABLE train_schema.train_time_table (
    train_number INT NOT NULL,
    departure_date DATE NOT NULL,
    station_code VARCHAR(10) NOT NULL COLLATE 'fn',
    station_ui_code INT NOT NULL,
    type VARCHAR(16) NOT NULL,
    scheduled_arrival_time DATETIME NOT NULL,
    actual_arrival_time DATETIME,
	primary key (train_number, departure_date, station_ui_code, type)
)
"""

stg_train_time_table_ddl = """
    CREATE OR REPLACE TABLE train_schema.stg_train_time_table (
        train_number INT NOT NULL,
        departure_date DATE NOT NULL,
        station_code VARCHAR(10) NOT NULL COLLATE 'fn',
        station_ui_code INT NOT NULL,
        type VARCHAR(16) NOT NULL,
        scheduled_arrival_time DATETIME NOT NULL,
        actual_arrival_time DATETIME
    )
    """