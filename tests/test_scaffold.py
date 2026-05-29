def test_dependencies_installed():
    import fastapi
    import pydantic
    import jinja2
    import openai
    assert fastapi.__version__ is not None
    assert pydantic.__version__ is not None
    assert jinja2.__version__ is not None
    assert openai.__version__ is not None


def test_fastapi_app_runs():
    from src.main import app
    assert app is not None
    assert app.title == "OfficeGenie"
