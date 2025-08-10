import sys
import os

# Get the current notebook's directory
current_dir = os.path.dirname(os.path.abspath('__file__' if '__file__' in globals() else '.'))

utils_dir = os.path.join(current_dir, '..')
utils_dir = os.path.join(utils_dir, '..')
utils_dir = os.path.abspath(utils_dir)

# Add to sys.path
sys.path.insert(0, utils_dir)
print("sys.path[0]:", sys.path[0])

from utils import create_agentcore_role

agent_name="agentcore_strands"
agentcore_iam_role = create_agentcore_role(agent_name=agent_name)

from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
boto_session = Session()
region = boto_session.region_name
region

agentcore_runtime = Runtime()

response = agentcore_runtime.configure(
    entrypoint="strands_claude.py",
    execution_role=agentcore_iam_role['Role']['Arn'],
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region=region,
    agent_name=agent_name
)
response

status_response = agentcore_runtime.status()
status = status_response.endpoint['status']
end_status = ['READY', 'CREATE_FAILED', 'DELETE_FAILED', 'UPDATE_FAILED']
while status not in end_status:
    time.sleep(10)
    status_response = agentcore_runtime.status()
    status = status_response.endpoint['status']
    print(status)
status

invoke_response = agentcore_runtime.invoke({"prompt": "How is the weather now?"})
invoke_response

from IPython.display import Markdown, display
import json
response_text = json.loads(invoke_response['response'][0].decode("utf-8"))
display(Markdown(response_text))

import boto3
agent_arn = launch_result.agent_arn
agentcore_client = boto3.client(
    'bedrock-agentcore',
    region_name=region
)

boto3_response = agentcore_client.invoke_agent_runtime(
    agentRuntimeArn=agent_arn,
    qualifier="DEFAULT",
    payload=json.dumps({"prompt": "What is 2+2?"})
)
if "text/event-stream" in boto3_response.get("contentType", ""):
    content = []
    for line in boto3_response["response"].iter_lines(chunk_size=1):
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                line = line[6:]
                logger.info(line)
                content.append(line)
    display(Markdown("\n".join(content)))
else:
    try:
        events = []
        for event in boto3_response.get("response", []):
            events.append(event)
    except Exception as e:
        events = [f"Error reading EventStream: {e}"]
    display(Markdown(json.loads(events[0].decode("utf-8"))))