from pydantic_factories import ModelFactory
from faker import Faker
from random import choice, randint
from typing import List, Any, Dict, Container, Optional, Type, Literal
from pydantic import BaseConfig, BaseModel, create_model
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty

specifics_type = ["choice", "incremental_id", "name", "paragraph", "age"]


def __create_specific__(field_type: type, specific: str):
    """Function that create a Specific DataType. Just inherited a python standard type and add a field (specific) to store the specific type

    Args:
        field_type (type): Python type
        specific (str): _description_

    Returns:
        _type_: The the type
    """

    @classmethod
    def validate(cls, v):
        if not isinstance(v, field_type):
            raise TypeError(f"{type.__name__} required")
        return v

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type=type, format=specific.capitalize())

    specific_type = type(
        specific.capitalize(),
        (type,),
        {
            "specific": specific,
            "__modify_schema__": __modify_schema__,
            "validate": validate,
            "__get_validators__": __get_validators__,
        },
    )
    return specific_type


class OrmConfig(BaseConfig):
    orm_mode = True
    allow_reuse = True


def sqlalchemy_to_pydantic(
    db_model: Type, *, config: Type = OrmConfig, exclude: Container[str] = []
) -> Dict[str, (Type[BaseModel] | Dict[str, List[str]])]:
    """Convert a model of SqlAlchemy to model of Pydantic

    Returns:
        (dict){model, foreign_keys}: A model of Pydantic and the foreign keys
    """
    mapper = inspect(db_model)
    specific = db_model.__pydantic__
    fields: Dict[str, Any] = {}
    foreign_keys: Dict[str, List[str]] = {}

    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                column = attr.columns[0]
                column_foreign_keys = column.foreign_keys
                if column_foreign_keys:
                    keys = []
                    for key in column_foreign_keys:
                        keys.append(key.target_fullname)
                    foreign_keys[name] = keys

                python_type: Optional[type] = None
                if specific.get(name) is not None:
                    field_specs = specific.get(name)
                    field_type = (
                        field_specs["type"]
                        if field_specs.get("specific") is None
                        else __create_specific__(
                            field_specs["type"], field_specs["specific"]
                        )
                    )
                    python_type = field_type
                elif hasattr(column.type, "impl"):
                    if hasattr(column.type.impl, "python_type"):
                        python_type = column.type.impl.python_type
                elif hasattr(column.type, "python_type"):
                    python_type = column.type.python_type
                assert python_type, f"Could not infer python_type for {column}"
                default = None
                if column.default is None and not column.nullable:
                    default = ...
                fields[name] = (python_type, default)
            if isinstance(attr, RelationshipProperty):
                print(
                    "create field of the remote pydantic type"
                )  # ! this may be complicated

    pydantic_model = create_model(
        db_model.__name__, __config__=config, **fields  # type: ignore
    )
    return {"model": pydantic_model, "foreign_keys": foreign_keys}


def models_to_pydantic(models: dict):
    """Convert SqlAlchemy models to pydantic

    Args:
        models (dict): dictionary with the models to convert to pydantic models

    Returns:
         (dict): A dict with models of SqlAlchemy converted into Pydantic models, and their respective Foreign keys
    """
    pydantic_models: Dict[str, Dict] = {}

    for key in models.keys():
        pydantic_models[key] = sqlalchemy_to_pydantic(models[key])

    return pydantic_models


def get_mocks(model, amount: int):
    """_summary_

    Args:
        model (BaseModel): A model of Pydantic
        amount (int): The amount of pydantic Models

    Returns:
        (List): A list with instances of the pydantic model fill with respective data types
    """

    class Factory(ModelFactory):
        __model__ = model

    results = []
    for _ in range(amount):
        results.append(Factory.build())
    return results


class FactoryMaker:
    """A class that generate a ModelFactory class with specification of how to fill specific data types"""

    faker: Faker
    increment: Dict[str, int]
    choices: Dict[str, List[Any]]
    # variables_init: List[str] = [] # this variables will be init inside the factory created
    sql_models: Dict[str, Type]
    pydantic_models: Dict[str, Dict]
    models_ids: Dict[str, List[List[Any]]]
    dummy_data: Dict[str, List[Any]] = {}

    @classmethod
    def get_faker(cls):
        return cls.faker

    @classmethod
    def set_unique_choices(cls, choices: List[Any], specific: str):
        # cls.variables_init.append(specific)
        cls.choices[specific] = choices

    @classmethod
    def set_choices(
        cls, choices: List[Any], *, specific: str = "choice", key: str = ""
    ):
        """Set the choices of a a field type choice

        Args:
            choices (List[Any]): The choices
            specific (str): type of the field
            model (str, optional): key of the field id left in blank is set to all field with the specific type. Defaults to "".
        """
        cls.choices[f"{specific}{'_' + key if len(key) >=1 else ''}"] = choices

    @classmethod
    def set_faker(cls, faker: Faker):
        cls.faker = faker

    @classmethod
    def __init__(cls):
        cls.choices = {}
        cls.increment = {}
        cls.faker = Faker(["en_US", "es_ES"])

    @classmethod
    def get_provider(cls, specific: str, field: str, model: str):
        faker = cls.faker
        
        choices: List[Any] | None = cls.choices.get(f"{specific}{'_' + field if len(field) >=1 else ''}")

        def get_next_increment(field: str, model: str):
            value = cls.increment.get(f"{model}_{field}")
            if value is None:
                value = 1
            cls.increment[f"{model}_{field}"] = value + 1
            return value

        # TODO Add here more specific types
        switcher = {
            "choice": lambda: choice(choices) if choices is not None else None,
            # "unique_choice":   unique_choice,
            "incremental_id": lambda: get_next_increment(field, model),  #!not working
            "name": faker.name,
            "paragraph": faker.paragraph,
            "age": lambda: randint(1, 99),
        }

        return switcher.get(specific)

    @classmethod
    def create_factory(cls, model):
        """Create the ModelFactory with the specif types specifications

        Args:
            model (_type_): The model that the Factory will make

        Returns:
            _type_: A ModelFactory specific for the model
        """
        name = model.__name__ + "Factory"
        obj = {}
        for field in model.__fields__:
            class_field = model.__fields__[field].type_
            # print(model.__fields__[field].type_)
            if hasattr(class_field, "specific"):
                obj[field] = cls.get_provider(
                    class_field.specific, field, model.__name__
                )

        # for init in cls.variables_init:
        #     obj[f"__static_{init}__"] = 0

        obj["__model__"] = model
        # print(obj, name)
        factory_created = type(name, (ModelFactory,), obj)
        return factory_created

    @classmethod
    def generate_model_data(cls, data, amount):
        pydantic = data["model"]
        foreign_keys: Dict[str, List[str]] = data["foreign_keys"]
        if len(foreign_keys) >= 1:
            a = 0
            for key in foreign_keys:
                key_data = foreign_keys[key]
                info = key_data[0].split(".")
                model = info[0]
                # foreign_key = info[1]
                if cls.dummy_data[model]:
                    continue
                cls.dummy_data[model] = cls.generate_model_data(
                    cls.pydantic_models[model], amount
                )

        for key in foreign_keys:
            # TODO get the keys of the data previously generated
            # TODO set the specific type
            key_data = foreign_keys[key]
            info = key_data[0].split(".")
            model = info[0]
            foreign_key = info[1]
            dummy_keys = []
            for item in cls.dummy_data[model]:
                print(item.__getattribute__(foreign_key))
                dummy_keys.append(item.__getattribute__(foreign_key))
            cls.set_choices(dummy_keys, key=key)
        model_factory = cls.create_factory(pydantic)
        dummy_data = model_factory.batch(amount)
        return dummy_data

    @classmethod
    def generate_data(cls, models: Dict[str, Any], amount):
        """Generate dummy data according to the extended specifications of the SqlAlchemy models

        Args:
            models (Dict[str,Any]): A dict with the SqlAlchemy models.
        Returns:
            data (Dict[str, List[Any]]) Return a List with Data generated
        """
        data = models_to_pydantic(models)
        cls.pydantic_models = data
        for model in cls.pydantic_models:
            cls.dummy_data[model] = cls.generate_model_data(data[model], amount)
        return {"data": cls.dummy_data, "pydantic_models": data}
