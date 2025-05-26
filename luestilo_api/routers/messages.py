from http import HTTPStatus
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from luestilo_api.database import get_session
from luestilo_api.models import Client as ClientModel 
from luestilo_api.schemas import SendMessageToClientBody, CurrentUser 
from luestilo_api.security import get_current_user


router = APIRouter(tags=['message'])

def simulate_whatsapp_send(phone_number: str, message: str):
    print(f"--- SIMULANDO ENVIO DE WHATSAPP ---")
    print(f"Para: {phone_number}")
    print(f"Mensagem: {message}")
    print(f"------------------------------------")
    return True


@router.post("/send_to_client/{client_id}", status_code=HTTPStatus.OK)
def send_message_to_client(
    client_id: int,
    message_data: SendMessageToClientBody, 
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    client = session.scalar(select(ClientModel).where(ClientModel.id == client_id)) 

    if client is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    if not client.aceita_notificacoes_whatsapp:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Cliente não aceita notificações via WhatsApp."
        )

    if not client.numero_whatsapp:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Número de WhatsApp não cadastrado para este cliente."
        )

    send_success = simulate_whatsapp_send(client.numero_whatsapp, message_data.mensagem)

    if not send_success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao enviar mensagem de WhatsApp.")

    return {"message": "Mensagem enviada com sucesso!", "client_id": client.id}


@router.post("/send_to_all_clients", status_code=HTTPStatus.OK)
def send_message_to_all_clients(
    message_data: SendMessageToClientBody, 
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    clients_to_notify = session.scalars(
        select(ClientModel).where(
            ClientModel.aceita_notificacoes_whatsapp == True,
            ClientModel.numero_whatsapp.isnot(None)
        )
    ).all()

    if not clients_to_notify:
        return {"message": "Nenhum cliente elegível para receber notificações."}

    sent_count = 0
    failed_clients = []

    for client in clients_to_notify:
        send_success = simulate_whatsapp_send(client.numero_whatsapp, message_data.mensagem)
        if send_success:
            sent_count += 1
        else:
            failed_clients.append({"id": client.id, "reason": "Falha no envio da API de WhatsApp"})

    return {
        "message": f"Mensagens enviadas para {sent_count} clientes elegíveis.",
        "total_eligible": len(clients_to_notify),
        "failed_to_send_count": len(failed_clients),
        "failed_clients_details": failed_clients
    }
   