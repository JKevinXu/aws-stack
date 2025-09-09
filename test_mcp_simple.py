#!/usr/bin/env python3
"""
Test script for Strands Agent API Gateway integration
"""

import json
import requests
import boto3

# Replace with your actual token
AUTH_TOKEN = "eyJraWQiOiJiNzU3Y2QwNmY0N2YzMmIzOTQ1MjBmM2Q0MDljZTQyZCIsInR5cCI6IkpXVCIsImFsZyI6IlJTMjU2In0.eyJhdWQiOiJhbWMtcWJpei1hdWQiLCJzdWIiOiIxMDEyNzE2NTIiLCJuYmYiOjE3NTczODA3NTksImF1dGhfdGltZSI6MTc1NzM3ODQzMSwiaHR0cHM6Ly9hd3MuYW1hem9uLmNvbS90YWdzIjp7InRyYW5zaXRpdmVfdGFnX2tleXMiOlsiRW1haWwiXSwicHJpbmNpcGFsX3RhZ3MiOnsiRW1haWwiOlsia2V2aW54dUBhbWF6b24uY29tIl19fSwiaXNzIjoiaHR0cHM6Ly9pZHAuZmVkZXJhdGUuYW1hem9uLmNvbSIsInByZWZlcnJlZF91c2VybmFtZSI6ImtldmlueHUiLCJleHAiOjE3NTczODQzNTksImZlZGVyYXRlX3Rva2VuX3B1cnBvc2UiOiJpZF90b2tlbiIsImlhdCI6MTc1NzM4MDc1OSwibm9uY2UiOiI3Yjg0ZDJhNjNmOGU0ZTJmOWQ3YmUzNDU0NDU4MzQ4NiIsImp0aSI6IklELjkyYjE1NzUwLWI1MzgtNDM5NC1iYTZhLTVjOTcwM2I3ZmI4ZiJ9.Psv4RNLNHxfPDbFKr6nSbS0ptB9WwmlZWpLfpXBpbxLvABp7Tr6vEdYXHvpiXBL3HoRKAER69xB-YU5UWZzmAG8VK3gERX7dv1kixgA1CAanMBphM3it9X9lfxiXIH5e7RAb_kvjbRpl7gC3yNFo9Uucw1RSvCIqPEViIeen-C1gI17MhBBo3J4jIe8cylTD4wJ6MrujSZYNG-YQjbldskuLgIt57IvFLgXy3yVLghDHVKdvuWk6oHU9E1YXoixqjifaDSzb_W3h-n3k7ixa2LfO2oRevV_uJcacv3sXLu0-9zeKRXikjRSmSorlYfGkO54eyMmL4Bm8Wqkv439A0Q"

# Lambda Function URL will be retrieved from CloudFormation outputs




def get_function_url():
    """Get the Lambda Function URL from CloudFormation outputs."""
    try:
        # Initialize CloudFormation client
        cf_client = boto3.client('cloudformation', region_name='us-west-2')
        
        # Get stack outputs
        response = cf_client.describe_stacks(StackName='StrandsAgentLambdaStack')
        outputs = response['Stacks'][0]['Outputs']
        
        # Find the Function URL
        for output in outputs:
            if output['OutputKey'] == 'StrandsAgentFunctionUrl':
                return output['OutputValue']
        
        print("⚠️  Could not find Function URL in CloudFormation outputs")
        return None
        
    except Exception as e:
        print(f"⚠️  Could not retrieve Function URL: {e}")
        return None


def test_mcp_integration():
    """Test MCP integration with the Strands Agent via Lambda Function URL."""
    
    # Get Function URL endpoint
    api_endpoint = get_function_url()
    if not api_endpoint:
        print("❌ Cannot proceed without Function URL")
        return
    
    # Test prompt
    test_prompt = "List all available tools and their capabilities. Then help me create an email activity summary."
    
    # Payload with MCP token
    payload = {
        "prompt": test_prompt,
        "mcp_authorization_token": AUTH_TOKEN
    }
    
    # HTTP headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("=" * 80)
    print("🔗 STRANDS AGENT MCP INTEGRATION TEST (Lambda Function URL)")
    print("=" * 80)
    print(f"🌐 Function URL: {api_endpoint}")
    print(f"🌐 MCP Server: https://bwzo9wnhy3.execute-api.us-west-2.amazonaws.com/beta/mcp")
    print(f"🔑 Token Length: {len(AUTH_TOKEN)} characters")
    print(f"📝 Test Prompt: {test_prompt[:100]}...")
    print("🚀 Making HTTP POST request...")
    
    try:
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=payload,
            timeout=90
        )
        
        print(f"📊 HTTP Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        result = response.json()
        
        print(f"✅ Lambda Function Success:")
        print(f"   Status Code: 200")
        
        mcp_enabled = result.get("mcp_enabled", False)
        mcp_tools_count = result.get("mcp_tools_count", 0)
        response_text = result.get("response", "No response")
        
        print(f"   MCP Enabled: {'✅' if mcp_enabled else '❌'}")
        print(f"   MCP Tools Count: {mcp_tools_count}")
        print(f"   Response Length: {len(response_text)} characters")
        print(f"   Response Preview: {response_text[:500]}...")
        
        if mcp_enabled and mcp_tools_count > 0:
            print(f"\n🎉 SUCCESS! MCP Integration Working with {mcp_tools_count} tools!")
        else:
            print(f"\n⚠️  MCP Issue: Enabled={mcp_enabled}, Tools={mcp_tools_count}")
        
        print("=" * 80)
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout (90 seconds)")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - check Function URL endpoint")
    except Exception as e:
        print(f"❌ Exception: {e}")


def test_email_activity_with_mcp():
    """Test email activity creation with MCP tools via Lambda Function URL (for longer timeout)."""
    
    # Get Function URL endpoint for longer operations
    api_endpoint = get_function_url()
    if not api_endpoint:
        print("❌ Cannot proceed without Function URL")
        return
    
    # Email test case
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
    
    # Create email activity prompt
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
    
    # Payload with MCP token
    payload = {
        "prompt": email_prompt,
        "mcp_authorization_token": AUTH_TOKEN
    }
    
    # HTTP headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("\n" + "=" * 80)
    print("📧 STRANDS AGENT EMAIL ACTIVITY TEST (Function URL - 90s timeout)")
    print("=" * 80)
    print(f"🌐 Function URL: {api_endpoint}")
    print(f"📧 Subject: {test_case['subject']}")
    print(f"📤 Sender: {test_case['sender_email']}")
    print(f"📅 Due Date: {test_case['due_date']}")
    print(f"📝 Content Length: {len(test_case['email_content'])} characters")
    print("🚀 Making HTTP POST request...")
    
    try:
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=payload,
            timeout=90
        )
        
        print(f"📊 HTTP Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        result = response.json()
        
        print(f"✅ Email Activity Test Success:")
        print(f"   Status Code: 200")
        
        mcp_enabled = result.get("mcp_enabled", False)
        mcp_tools_count = result.get("mcp_tools_count", 0)
        response_text = result.get("response", "No response")
        
        print(f"   MCP Enabled: {'✅' if mcp_enabled else '❌'}")
        print(f"   MCP Tools Count: {mcp_tools_count}")
        print(f"   Response Length: {len(response_text)} characters")
        print(f"\n📋 Email Activity Response:")
        print(f"{response_text}")
        
        print("=" * 80)
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout (90 seconds)")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - check Function URL endpoint")
    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    # Run MCP integration test
    test_mcp_integration()
    
    # Then run email activity test
    test_email_activity_with_mcp()
