import pytest

def pytest_addoption(parser):
    parser.addoption("--wc-host", action="store", help="Host address of the Watson controller service")


@pytest.fixture
def wc_host(request):
    return request.config.getoption("--wc-host")
