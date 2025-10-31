import pytest

from app.core.database import Base, engine
from app.models import ExampleModel


def test_base_declarative_base():
    assert Base is not None
    assert hasattr(Base, "metadata")


def test_async_engine():
    assert engine is not None
    assert hasattr(engine, "connect")
    assert hasattr(engine, "dispose")


def test_example_model_tablename():
    assert ExampleModel.__tablename__ == "examples"


def test_example_model_columns():
    assert hasattr(ExampleModel, "id")
    assert hasattr(ExampleModel, "name")
    assert hasattr(ExampleModel, "description")
    assert hasattr(ExampleModel, "created_at")


def test_models_inherit_from_base():
    assert issubclass(ExampleModel, Base)
