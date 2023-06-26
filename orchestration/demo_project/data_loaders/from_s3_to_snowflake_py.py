from mage_ai.data_preparation.repo_manager import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.s3 import S3
import snowflake.connector
from os import path
import pandas as pd
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_to_snowflake():
    
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    config = ConfigFileLoader(config_path, config_profile)

    # Connect to Snowflake
    con = snowflake.connector.connect(
        user=config.get('SNOWFLAKE_USER'),
        password=config.get('SNOWFLAKE_PASSWORD'),
        account=config.get('SNOWFLAKE_ACCOUNT'),
        warehouse=config.get('SNOWFLAKE_DEFAULT_WH'),
        database=config.get('SNOWFLAKE_DEFAULT_DB'),
        schema=config.get('SNOWFLAKE_DEFAULT_SCHEMA'),
        stage_name = config.get('SNOWFLAKE_STAGE_NAME'),
        login_timeout=config.get('SNOWFLAKE_TIMEOUT'),
        logging_level='DEBUG'
    )
    cur = con.cursor()

    cur.execute("SHOW DATABASES LIKE 'STAGING'")
    result = cur.fetchone()
    if not result:
        try:
            cur.execute("CREATE DATABASE STAGING")
            print("Database 'STAGING' created successfully.")
        except Exception as e:
            print("Failed to create the database: ", e)

    try:
        cur.execute("USE DATABASE STAGING")
        print("Database 'STAGING' is in use.")
    except Exception as e:
        print("Failed to use the database: ", e)

    try:
        cur.execute(f"USE WAREHOUSE {config.get('SNOWFLAKE_DEFAULT_WH')}")
        print(f"Warehouse '{config.get('SNOWFLAKE_DEFAULT_WH')}' is in use.")
    except Exception as e:
        print("Failed to use the warehouse: ", e)    

    cur.execute("SHOW STAGES LIKE 'my_stage'")
    result = cur.fetchone()
    if not result:
        try:
            cur.execute(f"""
                CREATE STAGE my_stage  
                URL = 's3://ingestion-rawdata/' 
                CREDENTIALS = (
                    AWS_KEY_ID='{config.get('AWS_ACCESS_KEY_ID')}' 
                    AWS_SECRET_KEY='{config.get('AWS_SECRET_ACCESS_KEY')}'
                );
            """)
            print("Stage 'my_stage' created successfully.")
        except Exception as e:
            print("Failed to create the stage: ", e)

    files = [
        'olist_customers_dataset.csv',
        'olist_geolocation_dataset.csv',
        'olist_order_items_dataset.csv',
        'olist_order_payments_dataset.csv',
        'olist_order_reviews_dataset.csv',
        'olist_orders_dataset.csv',
        'olist_products_dataset.csv',
        'olist_sellers_dataset.csv',
    ]

    engine = create_engine(URL(
        user=config.get('SNOWFLAKE_USER'),
        password=config.get('SNOWFLAKE_PASSWORD'),
        account=config.get('SNOWFLAKE_ACCOUNT'),
        warehouse=config.get('SNOWFLAKE_DEFAULT_WH'),
        database=config.get('SNOWFLAKE_DEFAULT_DB'),
        schema=config.get('SNOWFLAKE_DEFAULT_SCHEMA')
    ))
    df = pd.DataFrame()

    for file in files:
        table_name = file.replace('.csv', '')
        cur.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cur.fetchone()

        if not result:
            try:
                df = pd.read_csv(f's3://ingestion-rawdata/{file}', nrows=1000)
                df.to_sql(table_name, con=engine, index=False, if_exists='replace', method='multi')
                print(f"Table '{table_name}' created successfully.")
            except Exception as e:
                print("Failed to create the table: ", e)

            try:
                cur.execute(f"""
                    COPY INTO {table_name} 
                    FROM @my_stage/{file} 
                    FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"')
                    ON_ERROR = 'CONTINUE'
                """)
                print(f"Data successfully loaded into the table {table_name}")
            except Exception as e:
                print("Failed to load the table: ", e)

    cur.close()
    con.close()


    # Return a sample dataframe for testing purposes
    return df

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'