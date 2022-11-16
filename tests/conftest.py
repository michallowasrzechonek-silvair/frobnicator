def pytest_make_parametrize_id(config, val):
    if hasattr(val, "__pytestid__"):
        return f"{val.__pytestid__()}"
