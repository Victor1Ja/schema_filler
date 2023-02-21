from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.automap import automap_base, AutomapBase
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT


def connect_database(database_name)->Engine:
    SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{database_name}'

    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    return engine

def automap(engine:Engine)->AutomapBase:
    Base = automap_base()
    Base.prepare(autoload_with=engine)
    return Base

def get_models(engine:Engine):
    Base = automap(engine)
    models = {}
    for model in Base.classes:
        print(model)
        models[model.__name__] = model
    return models
    # for table_name in inspector.get_table_names(schema='public'):
    #     for column in inspector.get_columns(table_name, schema='public'):
    #         models[table_name] = 


def get_inspector_schemas(engine:Engine)->dict:
    inspector = inspect(engine)
    tables_schema = {}
    for table_name in inspector.get_table_names(schema='public'):
        tables_schema[table_name] = []
        for column in inspector.get_columns(table_name, schema='public'):
            tables_schema[table_name].append(column)
    return tables_schema
    

# for schema in schemas:
#     print("schema: %s" % schema)
#     for table_name in inspector.get_table_names(schema=schema):
#         print(f"Table Name:{table_name}")
#         for column in inspector.get_columns(table_name, schema=schema):
#             print("Column: %s" % column)
