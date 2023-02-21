from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy import MetaData
from config import DB_USER,DB_PASS,DB_HOST,DB_PORT,DB_NAME
from db.utils import connect_database, get_models, get_inspector_schemas
from utils.schemas import get_mocks
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
# SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{DB_USRER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# inspector = inspect(engine)
# schemas = inspector.get_schema_names()
# print(schemas)
# # for schema in schemas:
# #     print("schema: %s" % schema)
# #     for table_name in inspector.get_table_names(schema=schema):
# #         print(f"Table Name:{table_name}")
# #         for column in inspector.get_columns(table_name, schema=schema):
# #             print("Column: %s" % column)

engine = connect_database('arrivals')
schemas = get_models(engine)
inspector_schemas = get_inspector_schemas(engine)

User = sqlalchemy_to_pydantic(schemas['user'])
mock = get_mocks(User, 1);

print(mock)

# print(schemas)