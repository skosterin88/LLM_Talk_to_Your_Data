import pandas as pd
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase

from typing import List


def get_db_schemas(db_connection_string: str) -> List[str]:
    """
    Connects to the PostgreSQL database and retrieves the list of schema names.
    """
    engine = create_engine(db_connection_string)
    connection = engine.connect()
    
    df_schemas = pd.read_sql("SELECT table_schema, table_name FROM information_schema.tables", connection)
    
    connection.close()
    
    schemas = [schema for schema in df_schemas['table_schema'].unique() if schema not in ('information_schema', 'pg_catalog')]
    
    return schemas

def get_db_connection_string(server_name: str, port: int, database_name: str) -> str:
    
    db_connection_string = f"postgresql+psycopg2://{server_name}:{port}/{database_name}"
    
    schemas = get_db_schemas(db_connection_string)
    if schemas:
        search_path = ",".join(schemas)
        db_connection_string += f"?options=-csearch_path%3D{search_path}"
    
    return db_connection_string

def get_database(server_name: str, port: int, database_name: str) -> SQLDatabase:
    
    db_connection_string = get_db_connection_string(server_name, port, database_name)
    
    database = SQLDatabase.from_uri(db_connection_string)
    
    return database

