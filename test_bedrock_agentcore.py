#!/usr/bin/env python3
"""
Test script for Strands Agent deployed on Amazon Bedrock Agent Core - Email Activity Test
"""

import json
import boto3
import time
from botocore.exceptions import ClientError

# Replace with your actual token
<<<<<<< HEAD
AUTH_TOKEN = "eyJraWQiOiJiNzU3Y2QwNmY0N2YzMmIzOTQ1MjBmM2Q0MDljZTQyZCIsInR5cCI6IkpXVCIsImFsZyI6IlJTMjU2In0.eyJhdWQiOiJhbWMtcWJpei1hdWQiLCJzdWIiOiIxMDEyNzE2NTIiLCJuYmYiOjE3NTc5ODg3NTIsImF1dGhfdGltZSI6MTc1Nzk4NzEyMywiaHR0cHM6Ly9hd3MuYW1hem9uLmNvbS90YWdzIjp7InRyYW5zaXRpdmVfdGFnX2tleXMiOlsiRW1haWwiXSwicHJpbmNpcGFsX3RhZ3MiOnsiRW1haWwiOlsia2V2aW54dUBhbWF6b24uY29tIl19fSwiaXNzIjoiaHR0cHM6Ly9pZHAuZmVkZXJhdGUuYW1hem9uLmNvbSIsInByZWZlcnJlZF91c2VybmFtZSI6ImtldmlueHUiLCJleHAiOjE3NTc5OTIzNTIsImZlZGVyYXRlX3Rva2VuX3B1cnBvc2UiOiJpZF90b2tlbiIsImlhdCI6MTc1Nzk4ODc1Miwibm9uY2UiOiJjMDkwZWFlNDcxZTc0ZTNkOGUzMmUyZmIzOWExMTNjYSIsImp0aSI6IklELjI1ZDQ0OWQwLWZmNzAtNDNhMy1hZGIxLTA2OGVjNmNiOWIzMCJ9.f_SI9LIYlkYWHl5jACsapiqTIHe89YJlFBb_MDAbts4Jj8MPNesFnGK6mqmflpt5EAxgGtTPKWI2SYNKfMah6rF-hi-MGU7dDBgCJ4aoN2A04PWuGqjhfX8IO4lf__LzVZPX6hv0qOFooo_eGomHHu5phDg5kc3Xq_V2QVsBnH8wiP8Rr6pZYzKJ8JLx62ufJvwcBn4FWIb44F5yZF7DAQuCGgFbWHgdadO3G5PK12-4ZmzJnFGdkrDKwsT3CK4vqCHH8RjPAc3oCmww3uSrELbMI7gbKNvxeM3Cu28cbiigMOBb3ZKw9o1Z5vsPaqh0kV9MpiR9IZk2ILPQ8IBSAg"
=======
AUTH_TOKEN = "eyJraWQiOiJiNzU3Y2QwNmY0N2YzMmIzOTQ1MjBmM2Q0MDljZTQyZCIsInR5cCI6IkpXVCIsImFsZyI6IlJTMjU2In0.eyJhdWQiOiJhbWMtcWJpei1hdWQiLCJzdWIiOiIxMDEyNzE2NTIiLCJuYmYiOjE3NTc5OTI4NjEsImF1dGhfdGltZSI6MTc1Nzk4NzEyMywiaHR0cHM6Ly9hd3MuYW1hem9uLmNvbS90YWdzIjp7InRyYW5zaXRpdmVfdGFnX2tleXMiOlsiRW1haWwiXSwicHJpbmNpcGFsX3RhZ3MiOnsiRW1haWwiOlsia2V2aW54dUBhbWF6b24uY29tIl19fSwiaXNzIjoiaHR0cHM6Ly9pZHAuZmVkZXJhdGUuYW1hem9uLmNvbSIsInByZWZlcnJlZF91c2VybmFtZSI6ImtldmlueHUiLCJleHAiOjE3NTc5OTY0NjEsImZlZGVyYXRlX3Rva2VuX3B1cnBvc2UiOiJpZF90b2tlbiIsImlhdCI6MTc1Nzk5Mjg2MSwibm9uY2UiOiJkOWY4ODZjZWZiMWM0Y2Q3YTUwYzlhOThlZTA2NmM0MSIsImp0aSI6IklELjVlZjEzNTZhLWY5OTItNGViYi05NjEyLWJiNWViY2Y2N2FiYiJ9.jMQvyxpGKc3Y_5Kwop71bDNy6hgQovlMWPdCbiZVpXOEqT6xuTtF44OaM1lHAAWB9Vuh6wDeA7WaZwapSKhQbSn5qUJtUW7MdzRrMsOXtqt6VE1ui7IG3x6pH0YTJEOkZRqoKMOU484gJQB-iGxxbvECVC2OCsfVrsShnGAGbJ-tapcqTj0y4gAh447H3VhlfMc-BeB7wwbFqLmd21vXPpJa3oH7E3hp5xJBfv08L48YAuv6edRZPEUDMjp1l-v7JilvlJtWOirYPfCvDS2ywfQSgRRD4JD5lS3h2G5VrxMwu1hkzXUYY2J1riMUSI1XEXVi1toReCT3ReduWB-_4A"
>>>>>>> 3e7022a (feat: Add Bedrock Agent Core deployment support)

# Bedrock Agent Core ARN (from deployment output)
AGENT_ARN = "arn:aws:bedrock-agentcore:us-west-2:313117444016:runtime/agent_handler-MjzZZ55Om5"

# AWS region
AWS_REGION = "us-west-2"


def test_email_activity_agentcore():
    """Test email activity creation via Bedrock Agent Core (from test_mcp_simple.py)."""
    print("=" * 80)
    print("📧 BEDROCK AGENT CORE EMAIL ACTIVITY TEST")
    print("=" * 80)
    
    try:
        client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)
    except Exception as e:
        print(f"❌ Failed to create Bedrock Agent Core client: {e}")
        return
    
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
    print(f"📧 Subject: {test_case['subject']}")
    print(f"📤 Sender: {test_case['sender_email']}")
    print(f"📅 Due Date: {test_case['due_date']}")
    print(f"📝 Content Length: {len(test_case['email_content'])} characters")
    print("🚀 Invoking Bedrock Agent Core for email processing...")
    
    try:
        start_time = time.time()
        
        # Invoke the agent
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_ARN,
            payload=json.dumps(payload).encode('utf-8')
        )
        
        end_time = time.time()
        
        print(f"📊 Response received in {end_time - start_time:.2f} seconds")
        
        # Debug the response structure
        print(f"🔍 Response type: {type(response)}")
        print(f"🔍 Response keys: {response.keys() if hasattr(response, 'keys') else 'No keys method'}")
        
        # Process the response
        if 'response' in response:
            print(f"🔍 Response['response'] type: {type(response['response'])}")
            try:
                # Handle StreamingBody response
                response_data = response['response']
                if hasattr(response_data, 'read'):
                    # It's a streaming body - read all data
                    raw_data = response_data.read()
                    if isinstance(raw_data, bytes):
                        full_response = raw_data.decode('utf-8')
                    else:
                        full_response = str(raw_data)
                elif isinstance(response_data, bytes):
                    full_response = response_data.decode('utf-8')
                else:
                    # Fallback to string conversion
                    full_response = str(response_data)
                    
                print(f"🔍 Raw response length: {len(full_response)}")
                print(f"🔍 Raw response preview: {full_response[:200]}...")
                    
            except Exception as parse_error:
                print(f"❌ Response parsing error: {parse_error}")
                full_response = str(response['response'])
            
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
            print(f"❌ Unexpected response format: {response}")
            
    except ClientError as e:
        print(f"❌ AWS Client Error: {e}")
    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    # Run the email activity test
    test_email_activity_agentcore()