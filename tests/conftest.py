# content of conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption("--newtestnet", action="store_true", help="Create a fresh new testnet")

def pytest_generate_tests(metafunc):
    pass

@pytest.fixture()
def master(request):
    return request.config.getoption("--master")
