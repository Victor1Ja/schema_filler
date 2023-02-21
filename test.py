from pydantic_factories import ModelFactory
from faker import Faker
from datetime import date, datetime
from typing import Dict, Union, Any

from pydantic import BaseModel, UUID4, EmailStr

from pydantic_factories import ModelFactory

from utils.schemas import SpecificFactory

faker = Faker(["en_US", "es_ES"])


class NameStr(str):
    specific: str = "name"

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type="string", format="name")


class LoreStr(str):
    specific: str = "paragraph"

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type="string", format="paragraph")


class My_Id(int):
    specific: str = "ref_id"

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type="int", format="ID")


class Age(int):
    specific: str = "age"

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type="int", format="Age")


class Person(BaseModel):
    id: My_Id
    name: NameStr
    description: LoreStr
    email: EmailStr
    age: Age
    birthday: Union[datetime, date]


class PersonDactory(ModelFactory):
    __model__ = Person
    #
    name = lambda: faker.name()


sf = SpecificFactory()
sf.set_choices([3, 4, 5], "id")
classTest = sf.create_factory(Person)
# print(faker.name())
# print(Person.schema_json())
# print("\n\n")
# result = PersonFactory.build()
results = PersonDactory.batch(3)
results2 = classTest.batch(3)

for result in results2:
    print(result)
    print("\n")
