
import pytest

# fixture example (if needed)
@pytest.fixture(scope="session")
def sample_fixture():
    print("Setting up sample_fixture")
    return "sample data"