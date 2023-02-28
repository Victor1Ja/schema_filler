# Hello World
Hi, this module is intended to convert SqlAlchemy models into Pydantic models and generate how many example data you want

## Features
### Completed
- Convert SqlAlchemy models to Pydantic
- Generate dummy data according to the specification of pydantic, and pydantic specific types
### Working on 
- Specify types likes name, descriptions and other so the data generated has "sense".
- Have in count foreign key when generate the dummy data. 
### Soon
- Parse models from database and infer the specific types
- Create Pydantic Models with the remote fields 
- Create ModelBase, ModelCreate, ModelUpdate, ModelDelete and Model according to FastApi schemas guides

## How to use
### When creating models with SqlAlchemy
#### ***Create the models***
The idea is that when SqlAlchemy models are created leave a field with specifications of how to deal with the specific types, using pydantic specific and this module specific.
``` python
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
```
Can be used PydanticSpecific types to specify the types or can be use the specific type implemented on this modules.

Whit the PydanticSpecific is only need to specify the type:
``` python
    'email':{
        'type':EmailStr,
        'models':['base']
    }
```

Otherwise can be specified with our specific types:
```
    specifics_type = ["choice", "incremental_id", "name", "paragraph", "age"]
```

This way
``` python
    'name':{
        'type':str,
        'specific':'name',
        'models':['base']
    }
```

Soon will be implemented more.
## Relationships
In order to generate data with proper external key constrains is needed to define the specific type according to the relationship.

- For one to many relationships is needed to use the specific type 'choices'. With this type the module will only select ids from the given choices.
``` python
    'owner':{
        'type':str,
        'specific':'choices',
    }
```
- For one to one relationships is needed to use the specific type 'unique_choices'. With this type the module will only select one ids per field  from the given choices.
``` python
    'owner':{
        'type':str,
        'specific':'unique_choices',
    }
```

## **Create the Data**

### Manual

To create the data first is needed to convert the SqlAlchemy models to Pydantic Models
``` Python
from utils.schemas import models_to_pydantic
from utils.schemas import FactoryMaker

models = models_to_pydantic({'humans':Human})

sf = FactoryMaker()

humans = sf.create_factory(models['human']['model'])

print(humans.batch(3))
```

### Automatic 
.....
