from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from pydantic import EmailStr
from typing import Dict, List
from utils.schemas import models_to_pydantic
from utils.schemas import FactoryMaker


DB_USER = 'postgres'
DB_PASS = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'pets_travels'



# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Human(Base):
    __tablename__ = "humans"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    
    __pydantic__ = {
        'id':{
            'type':int,
            'specific':'incremental_id',
            'models':['final']
        },
        'email':{
            'type':EmailStr,
            'models':['base']
        },
        'name':{
            'type':str,
            'specific':'name',
            'models':['base']
        }
    }
    # relations
    travels = relationship("PetTravel", back_populates="human")
    pets = relationship("Pet", back_populates="owner")

# Specification = Dict[]
class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    breed = Column(String, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("humans.id"))
    __pydantic__ = {
        'id':{
            'type':int,
            'specific':'incremental_id',
            'models':['final']
        },
        'name':{
            'type':str,
            'specific':'name',
            'models':['base']
        },
        'breed':{
            'type':str,
            'specific':'paragraph',
            'models':['base']
        },
        'owner_id':{
            'type':int,
            'specific':'choice',
            'models':['base']
        }
    }
    # relations
    travels = relationship("PetTravel", back_populates="pet")
    owner = relationship("Human", back_populates="pets")


class PetTravel(Base):
    __tablename__ = "pet_travels"
    pet_id = Column(Integer,ForeignKey("pets.id"),primary_key=True)
    human_id = Column(Integer, ForeignKey("humans.id"),primary_key=True)
    length = Column(Integer)

    __pydantic__ = {
        'length':{
            'type':int,
            'models':['base']
        }
    }
    # relations
    pet = relationship("Pet", back_populates="travels")
    human = relationship("Human", back_populates="travels")

    

models = models_to_pydantic({'humans':Human, 'pets':Pet})
# print(models['human'].schema())

sf = FactoryMaker()
# set message when left choices 
#  modify for get the choices from  the field name
humans = sf.create_factory(models['human']['model'])
sf.set_choices([1,2,3], "owner_id")

pets = sf.create_factory(models['pets']['model'])
# results = humans.batch(3)

print(humans.batch(3))
print('\n')
print(pets.batch(3))

