#!/usr/bin/env python3
"""
Simplified test script for Strands Agent MCP integration
"""

import json
import boto3

# Replace with your actual token
AUTH_TOKEN = "eyJraWQiOiJiNzU3Y2QwNmY0N2YzMmIzOTQ1MjBmM2Q0MDljZTQyZCIsInR5cCI6IkpXVCIsImFsZyI6IlJTMjU2In0.eyJhdWQiOiJhbWMtcWJpei1hdWQiLCJzdWIiOiIxMDEyNzE2NTIiLCJuYmYiOjE3NTY5NzQ5MzcsImF1dGhfdGltZSI6MTc1Njk2MjExMywiaHR0cHM6Ly9hd3MuYW1hem9uLmNvbS90YWdzIjp7InRyYW5zaXRpdmVfdGFnX2tleXMiOlsiRW1haWwiXSwicHJpbmNpcGFsX3RhZ3MiOnsiRW1haWwiOlsia2V2aW54dUBhbWF6b24uY29tIl19fSwiaXNzIjoiaHR0cHM6Ly9pZHAuZmVkZXJhdGUuYW1hem9uLmNvbSIsInByZWZlcnJlZF91c2VybmFtZSI6ImtldmlueHUiLCJleHAiOjE3NTY5Nzg1MzcsImZlZGVyYXRlX3Rva2VuX3B1cnBvc2UiOiJpZF90b2tlbiIsImlhdCI6MTc1Njk3NDkzNywibm9uY2UiOiIyMjhkNzQyYTJiOGM0MjE3OGRhZTE1MGJjODNiMzA1NSIsImp0aSI6IklELjEzMWJlYmQwLTFiZDctNDJhZi1hODM2LTFmNTQ1YTNjZGFmOSJ9.DKQ1e6yklIy36Zt35M04tOP2guOtVduIPuRdeqti-nZ9ZpVzNfElVqlBodwKLy9Qgb9R5IOJ2HNyV1QhLMp07VcwwrTsN71z4P9SF4RHnyYtDGqgQUGwx5frpJKvBLozwoY35gBprLe2G7LDQ83AMSpXp4qPCyjuDS8PRt5QZIgNm3PiFGW0S_bTFBMszz5V0NSOdr2JFCTpjB23weQdeI8pE8M08KWj4o_JxmT54NMtnGn3L8r24Z9DxbpuCAX43JNzFv3znA9Sj6d1eoSF-ZgoD-hMxT1Vfx21C1KNsez3HVspXaTUKXJZ9aaBViuRZ5B-bkq6aoQHMVSWVK4OOw"


def test_mcp_integration():
    """Test MCP integration with the Strands Agent Lambda."""
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    function_name = "StrandsAgentFunction"
    
    # Test prompt
    test_prompt = "List all available tools and their capabilities. Then help me create an email activity summary."
    
    # Payload with MCP token
    payload = {
        "prompt": test_prompt,
        "mcp_authorization_token": AUTH_TOKEN,
        "use_mcp": True
    }
    
    print("=" * 80)
    print("🔗 STRANDS AGENT MCP INTEGRATION TEST")
    print("=" * 80)
    print(f"🌐 MCP Server: https://bwzo9wnhy3.execute-api.us-west-2.amazonaws.com/beta/mcp")
    print(f"🔑 Token Length: {len(AUTH_TOKEN)} characters")
    print(f"📝 Test Prompt: {test_prompt[:100]}...")
    print("🚀 Invoking Lambda function...")
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        
        # Display results
        if "error" in result:
            print(f"❌ Lambda Error: {result['error']}")
            return
        
        print(f"✅ Lambda Success:")
        print(f"   Status Code: {result.get('statusCode', 'N/A')}")
        
        if "body" in result:
            body = json.loads(result["body"]) if isinstance(result["body"], str) else result["body"]
            
            mcp_enabled = body.get("mcp_enabled", False)
            mcp_tools_count = body.get("mcp_tools_count", 0)
            response_text = body.get("response", "No response")
            
            print(f"   MCP Enabled: {'✅' if mcp_enabled else '❌'}")
            print(f"   MCP Tools Count: {mcp_tools_count}")
            print(f"   Response Length: {len(response_text)} characters")
            print(f"   Response Preview: {response_text[:500]}...")
            
            if mcp_enabled and mcp_tools_count > 0:
                print(f"\n🎉 SUCCESS! MCP Integration Working with {mcp_tools_count} tools!")
            else:
                print(f"\n⚠️  MCP Issue: Enabled={mcp_enabled}, Tools={mcp_tools_count}")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Exception: {e}")


def test_email_activity_with_mcp():
    """Test email activity creation with MCP tools."""
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    function_name = "StrandsAgentFunction"
    
    # Email test case
    test_case = {
        "subject": "Follow-up on Product Demo",
        "sender_email": "kevinxu@amazon.com", 
        "due_date": "2025-11-13T20:20:39.321Z",
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
        "mcp_authorization_token": AUTH_TOKEN,
        "use_mcp": True
    }
    
    print("\n" + "=" * 80)
    print("📧 STRANDS AGENT EMAIL ACTIVITY TEST (WITH MCP)")
    print("=" * 80)
    print(f"📧 Subject: {test_case['subject']}")
    print(f"📤 Sender: {test_case['sender_email']}")
    print(f"📅 Due Date: {test_case['due_date']}")
    print(f"📝 Content Length: {len(test_case['email_content'])} characters")
    print("🚀 Invoking Lambda function...")
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        
        # Display results
        if "error" in result:
            print(f"❌ Lambda Error: {result['error']}")
            return
        
        print(f"✅ Email Activity Test Success:")
        print(f"   Status Code: {result.get('statusCode', 'N/A')}")
        
        if "body" in result:
            body = json.loads(result["body"]) if isinstance(result["body"], str) else result["body"]
            
            mcp_enabled = body.get("mcp_enabled", False)
            mcp_tools_count = body.get("mcp_tools_count", 0)
            response_text = body.get("response", "No response")
            
            print(f"   MCP Enabled: {'✅' if mcp_enabled else '❌'}")
            print(f"   MCP Tools Count: {mcp_tools_count}")
            print(f"   Response Length: {len(response_text)} characters")
            print(f"\n📋 Email Activity Response:")
            print(f"{response_text}")
            
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    # Run MCP integration test first
    test_mcp_integration()
    
    # Then run email activity test
    test_email_activity_with_mcp()
