try:
    from backend.api.app import app
except ModuleNotFoundError:
    from api.app import app
