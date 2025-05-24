from http import HTTPStatus

from luestilo_api.schemas import ClientPublic


def test_root_deve_retornar_ola_mundo(client):
    response = client.get('/')
    assert response.json() == {'message': 'Olá Mundo!'}
    assert response.status_code == HTTPStatus.OK


def test_create_clients(client):
    response = client.post(
        '/clients/',
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'cpf': '383.625.200-78',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'name': 'alice',
        'email': 'alice@example.com',
        'cpf': '383.625.200-78',
    }


def test_read_clients(client):
    response = client.get('/clients')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'clients': []}


def test_read_clients_with_clients(client, cliente):
    client_schema = ClientPublic.model_validate(cliente).model_dump()
    response = client.get('/clients/')
    assert response.json() == {'clients': [client_schema]}


def test_update_user(client, cliente):
    response = client.put(
        '/clients/1',
        json={
            'name': 'bob',
            'email': 'bob@example.com',
            'cpf': '125.242.550-34',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'name': 'bob',
        'email': 'bob@example.com',
        'cpf': '125.242.550-34',
        'id': 1,
    }
