
import requests
import pytest


def get_top_todos():
    url="https://jsonplaceholder.typicode.com/todos?_limit=5"
    response = requests.get(url)
    todos = response.json()
    # filter todos which are not completed
    todos = [todo for todo in todos if not todo["completed"]]
    return todos
    

def test_get_top_five_todos(monkeypatch):
    class MockResponse:
        @staticmethod
        def json():
            return [
                {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": False},
                {"userId": 1, "id": 2, "title": "quis ut nam facilis et officia qui", "completed": False},
                {"userId": 1, "id": 3, "title": "fugiat veniam minus", "completed": True},
                {"userId": 1, "id": 4, "title": "et porro tempora", "completed": True},
                {"userId": 1, "id": 5, "title": "laboriosam mollitia et enim quasi adipisci quia provident illum", "completed": False},
            ]

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    todos = get_top_todos()
    assert len(todos) == 3
    

@pytest.fixture(
        params=[
            (100, "account_A", "account_B"),
            (200, "account_C", "account_D"),
            (300, "account_E", "account_F"),
        ]
)
def test_data(request):
    return request.param

def test_transfer(test_data):
    amount, from_account, to_account = test_data
    #...
