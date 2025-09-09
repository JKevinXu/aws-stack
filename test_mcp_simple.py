#!/usr/bin/env python3
"""
Test script for Strands Agent Lambda Function URL integration
"""

import json
import requests

# Replace with your actual token
AUTH_TOKEN = "<YOUR_AUTH_TOKEN>"

# Direct Lambda Function URL endpoint
LAMBDA_FUNCTION_URL = "https://zr5sblu3idcilhcthrpfzulrg40dlpss.lambda-url.us-west-2.on.aws/"


def test_mcp_integration():
    """Test MCP integration with the Strands Agent via Lambda Function URL."""
    
    # Use direct Lambda Function URL endpoint
    api_endpoint = LAMBDA_FUNCTION_URL
    
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
    
    # Use direct Lambda Function URL endpoint for longer operations
    api_endpoint = LAMBDA_FUNCTION_URL
    
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
