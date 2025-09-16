#!/usr/bin/env python3
"""
Test script for Strands Agent deployed on Amazon Bedrock Agent Core - Email Activity Test
"""

import json
import requests
import time
import urllib.parse
import logging

# Replace with your actual token
AUTH_TOKEN = "<YOUR_AUTH_TOKEN>"

# Bedrock Agent Core ARN (from deployment output)
AGENT_ARN = "arn:aws:bedrock-agentcore:us-west-2:313117444016:runtime/agent_handler-MjzZZ55Om5"

# AWS region
AWS_REGION = "us-west-2"


def test_email_activity_agentcore():
    """Test email activity creation via Bedrock Agent Core with JWT authentication."""
    print("=" * 80)
    print("📧 BEDROCK AGENT CORE EMAIL ACTIVITY TEST (JWT Authentication)")
    print("=" * 80)
    
    # Bedrock Agent Core HTTP endpoint (correct format)
    # URL encode the agent ARN
    escaped_agent_arn = urllib.parse.quote(AGENT_ARN, safe='')
    endpoint_url = f"https://bedrock-agentcore.{AWS_REGION}.amazonaws.com/runtimes/{escaped_agent_arn}/invocations?qualifier=DEFAULT"
    
    # Email test case from test_mcp_simple.py
    test_case = {
        "subject": "Follow-up on Product Demo",
        "sender_email": "kevinxu@amazon.com", 
        "due_date": "2025-12-13T20:20:39.321Z",
        "email_content": """Hi there,

I wanted to follow up on the product demo we discussed last week. Our team is very interested in your solution and would like to schedule a technical deep-dive session.

We have a few specific questions about:
1. Integration capabilities with our existing CRM
2. Pricing for enterprise deployment
3. Timeline for implementation

Could we schedule a call for next week? I'm available Tuesday-Thursday afternoons.

Best regards,
John Smith
Senior Solutions Architect
ACME Corporation"""
    }
    
    # Create email activity prompt (same as test_mcp_simple.py)
    email_prompt = f"""Create email activity with brief summary:

Subject: {test_case["subject"]}
Due Date: {test_case["due_date"]}
Sender Email: {test_case["sender_email"]}

Email Content:
{test_case["email_content"]}

Instructions:
- Set status to WORK IN PROGRESS by default
- FIRST: Call the seller lookup tool with contactType="EMAIL" and contactValue="{test_case["sender_email"]}" to get the seller name
- Include the seller name in the activity description (e.g., "Email activity from [Seller Name]:")
- Provide only a brief summary of this email in 2-3 sentences
- If seller lookup fails, proceed without seller name"""
    
    # Payload for the agent
    payload = {
        "prompt": email_prompt,
        "mcp_authorization_token": AUTH_TOKEN
    }
    
    print(f"🤖 Agent ARN: {AGENT_ARN}")
    print(f"🌐 AWS Region: {AWS_REGION}")
    print(f"🔗 Endpoint URL: {endpoint_url}")
    print(f"📧 Subject: {test_case['subject']}")
    print(f"📤 Sender: {test_case['sender_email']}")
    print(f"📅 Due Date: {test_case['due_date']}")
    print(f"📝 Content Length: {len(test_case['email_content'])} characters")
    print("🚀 Invoking Bedrock Agent Core for email processing...")
    
    try:
        start_time = time.time()
        
        # Prepare headers with JWT authentication (based on sample)
        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Enable debug logging for detailed request/response info
        logging.basicConfig(level=logging.INFO)
        
        # Make HTTP request to Bedrock Agent Core (using data instead of json)
        response = requests.post(
            endpoint_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=120  # 2 minute timeout
        )
        
        end_time = time.time()
        
        print(f"📊 Response received in {end_time - start_time:.2f} seconds")
        
        # Check response status
        print(f"🔍 HTTP Status Code: {response.status_code}")
        print(f"🔍 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                # Parse JSON response
                response_data = response.json()
                print(f"🔍 Response JSON keys: {response_data.keys() if isinstance(response_data, dict) else 'Not a dict'}")
                
                # Extract the actual response body if it's in API Gateway format
                if 'body' in response_data:
                    actual_response = json.loads(response_data['body'])
                else:
                    actual_response = response_data
                    
                full_response = json.dumps(actual_response)
                print(f"🔍 Parsed response length: {len(full_response)}")
                    
            except Exception as parse_error:
                print(f"❌ Response parsing error: {parse_error}")
                full_response = response.text
            
            if full_response:
                try:
                    # Parse the outer response (API Gateway format)
                    api_response = json.loads(full_response)
                    
                    # Extract the actual response body
                    if 'body' in api_response:
                        actual_response = json.loads(api_response['body'])
                    else:
                        actual_response = api_response
                    
                    print("✅ Email Activity Test Success:")
                    print(f"   Processing Time: {end_time - start_time:.2f} seconds")
                    print(f"   Status Code: {api_response.get('statusCode', 'N/A')}")
                    print(f"   MCP Enabled: {'✅' if actual_response.get('mcp_enabled') else '❌'}")
                    print(f"   MCP Tools Count: {actual_response.get('mcp_tools_count', 0)}")
                    response_text = actual_response.get('response', '')
                    print(f"   Response Length: {len(str(response_text))} characters")
                    print(f"\n📋 Email Activity Response:")
                    print(f"{str(response_text)}")
                    print("=" * 80)
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"📄 Raw response: {full_response[:500]}...")
            else:
                print("❌ No content in response")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP Request Error: {e}")
    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    # Run the email activity test
    test_email_activity_agentcore()