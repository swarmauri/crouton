![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)



[![Hits](https://hits.sh/github.com/swarmauri/swarmakit.svg)](https://hits.sh/github.com/swarmauri/crouton/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![PyPI - Version](https://img.shields.io/pypi/v/crouton?label=Crouton)
![PyPI - Downloads](https://img.shields.io/pypi/dm/crouton?label=Crouton%20Downloads)
![PyPI - Version](https://img.shields.io/pypi/v/crouton-client?label=Crouton-Client)
![PyPI - Downloads](https://img.shields.io/pypi/dm/crouton-client?label=Crouton-Client%20Downloads)





![Static Badge](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&labelColor=black)


---

# Crouton

crouton streamlines CRUD operations in FastAPI applications by auto-generating endpoints for SQLAlchemy models, reducing the need for repetitive code and improving development speed.

By integrating Pydantic for data validation, Crouton ensures type safety and consistent data handling, allowing developers to focus on application logic instead of boilerplate code.

# Installation

## 1. Prerequisites

To install Crouton libraries. Run the following command:

```bash
pip install crouton
pip install crouton-client
```

## 2. Development Release Installation
```bash
pip install crouton --pre
pip install crouton-client --pre
```
# Basic Usage
Below is a simple example of what the CRUDRouter can do. In just ten lines of code, you can generate all the crud routes you need for any model. A full list of the routes generated can be found here.

```python
from sqlalchemy import Column, String, Float, Integer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pydantic import BaseModel
from fastapi import FastAPI
from crouton import SQLAlchemyCRUDRouter

app = FastAPI()
engine = create_engine(
    "sqlite:///./app.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()


class PotatoCreate(BaseModel):
    thickness: float
    mass: float
    color: str
    type: str


class Potato(PotatoCreate):
    id: int

    class Config:
        orm_mode = True


class PotatoModel(Base):
    __tablename__ = 'potatoes'
    id = Column(Integer, primary_key=True, index=True)
    thickness = Column(Float)
    mass = Column(Float)
    color = Column(String)
    type = Column(String)


Base.metadata.create_all(bind=engine)

router = SQLAlchemyCRUDRouter(
    schema=Potato,
    create_schema=PotatoCreate,
    db_model=PotatoModel,
    db=get_db,
    prefix='potato'
)

app.include_router(router)

```

# Example
![image](https://github.com/user-attachments/assets/22e6ce3a-6eb1-4a80-a37f-93fef545b49e)
