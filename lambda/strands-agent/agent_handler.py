from strands import Agent
from strands_tools import http_request
from typing import Dict, Any
import json

# Define a weather-focused system prompt
WEATHER_SYSTEM_PROMPT = """You are a weather assistant with HTTP capabilities. You can:

1. Make HTTP requests to the National Weather Service API
2. Process and display weather forecast data
3. Provide weather information for locations in the United States

When retrieving weather information:
1. First get the coordinates or grid information using https://api.weather.gov/points/{latitude},{longitude} or https://api.weather.gov/points/{zipcode}
2. Then use the returned forecast URL to get the actual forecast

When displaying responses:
- Format weather data in a human-readable way
- Highlight important information like temperature, precipitation, and alerts
- Handle errors appropriately
- Convert technical terms to user-friendly language

Always explain the weather conditions clearly and provide context for the forecast.
"""

# Define a general assistant system prompt as an alternative
GENERAL_ASSISTANT_PROMPT = """You are a helpful AI assistant with web browsing capabilities. You can:

1. Make HTTP requests to public APIs and websites
2. Search for information on the web
3. Help with general questions and tasks
4. Process and analyze web content

When making web requests:
- Use appropriate headers and follow rate limits
- Handle errors gracefully
- Provide clear summaries of the information found
- Always cite your sources when providing information from web requests

Be helpful, accurate, and thorough in your responses.
"""

# The handler function signature `def handler(event, context)` is what Lambda
# looks for when invoking your function.
def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    AWS Lambda handler function for Strands Agent
    
    Args:
        event: Lambda event containing the prompt and optional configuration
        context: Lambda context object
        
    Returns:
        Dictionary containing the agent's response
    """
    try:
        # Extract prompt from event
        prompt = event.get('prompt', '')
        if not prompt:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No prompt provided',
                    'message': 'Please provide a prompt in the event payload'
                })
            }
        
        # Choose agent type based on event configuration
        agent_type = event.get('agent_type', 'weather')
        
        if agent_type == 'weather':
            system_prompt = WEATHER_SYSTEM_PROMPT
        else:
            system_prompt = GENERAL_ASSISTANT_PROMPT
        
        # Create the Strands agent with specified system prompt and tools
        agent = Agent(
            system_prompt=system_prompt,
            tools=[http_request],
        )

        # Process the prompt through the agent
        response = agent(prompt)
        
        # Return the response in the expected Lambda format
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': str(response),
                'agent_type': agent_type,
                'prompt': prompt
            })
        }
        
    except Exception as e:
        # Handle any errors that occur during processing
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'An error occurred while processing the request'
            })
        }
