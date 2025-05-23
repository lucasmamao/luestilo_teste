from sqlalchemy import select

from luestilo_api.models import Client


def test_create_client(session):
    new_client = Client(
        name='test', email='test@test.com', cpf='383.625.200-78'
    )

    session.add(new_client)
    session.commit()

    client = session.scalar(select(Client).where(Client.name == 'test'))
    assert client.name == 'test'
