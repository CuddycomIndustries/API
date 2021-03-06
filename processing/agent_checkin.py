from base64 import b64decode
from datetime import datetime

from flask import json
from flask_socketio import SocketIO
from backend.rabbitmq import rpc_client
from models.agent import Agent
from models.agent_checkin import AgentCheckin
from models.agent_task_update import AgentTaskUpdate
from processing import agent_task_message

socketio = SocketIO()

def agent_checkin_json(agent_checkin):
    result = dict(
        {
            'AgentId' : agent_checkin.AgentId,
            'IV': agent_checkin.IV,
            'HMAC': agent_checkin.HMAC,
            'Message' : agent_checkin.Message
         })
    return result

def get_agent_checkin(agent_checkin_id='all'):
    if agent_checkin_id == 'all':
        result = []
        agent_messages = AgentCheckin.query.all()
        for agent_message in agent_messages:
            result.append(agent_checkin_json(agent_message))
    else:
        agent_message = AgentCheckin.query.get(agent_checkin_id)
        result = agent_checkin_json(agent_message)
    return result


def add_agent_checkin(agent_name, message=None):
    hmac = None
    iv = None
    msg = None
    if message:
        decoded_checkin = b64decode(message)
        checkin_dict = json.loads(decoded_checkin)
        hmac = checkin_dict["HMAC"]
        iv = checkin_dict["IV"]
        msg = checkin_dict["Message"]

    checkin = {
        'AgentName': agent_name,
        'HMAC': hmac,
        'IV': iv,
        'Message': msg
    }


    print("[add_agent_task_response] publishing?")
    #publish_message('Core', 'AgentCheckin', json_string)
    rpc_client.send_request('NewAgentCheckin', checkin)
    return {
        'Success': True,
        'Result': checkin
    }


def process_agent_checkin(agent_name, message=None):
    result = add_agent_checkin(agent_name, message)
    return agent_task_message.get_unsent_agent_task_messages(agent_name)