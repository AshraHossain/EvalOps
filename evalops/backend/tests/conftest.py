import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as prompt regression test"
    )


pytest_plugins = ('pytest_asyncio',)
