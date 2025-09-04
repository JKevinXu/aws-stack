#!/usr/bin/env python3
"""
Simplified test script for Strands Agent MCP integration
"""

import json
import boto3

# Replace with your actual token
AUTH_TOKEN = "eyJraWQiOiJiNzU3Y2QwNmY0N2YzMmIzOTQ1MjBmM2Q0MDljZTQyZCIsInR5cCI6IkpXVCIsImFsZyI6IlJTMjU2In0.eyJhdWQiOiJhbWMtcWJpei1hdWQiLCJzdWIiOiIxMDEyNzE2NTIiLCJuYmYiOjE3NTY5NTUxOTMsImF1dGhfdGltZSI6MTc1Njk1MDcwOCwiaHR0cHM6Ly9hd3MuYW1hem9uLmNvbS90YWdzIjp7InRyYW5zaXRpdmVfdGFnX2tleXMiOlsiRW1haWwiXSwicHJpbmNpcGFsX3RhZ3MiOnsiRW1haWwiOlsia2V2aW54dUBhbWF6b24uY29tIl19fSwiaXNzIjoiaHR0cHM6Ly9pZHAuZmVkZXJhdGUuYW1hem9uLmNvbSIsInByZWZlcnJlZF91c2VybmFtZSI6ImtldmlueHUiLCJleHAiOjE3NTY5NTg3OTMsImZlZGVyYXRlX3Rva2VuX3B1cnBvc2UiOiJpZF90b2tlbiIsImlhdCI6MTc1Njk1NTE5Mywibm9uY2UiOiJlNzU1NDQyNWU2Nzg0ZmU4YTViOWNmNjc1OTdmOTRlNiIsImp0aSI6IklELjQ0YmU5YWFlLWZlY2EtNGMyNy1hMTRkLTUwZTQyYTVhMjcxMiJ9.gvkcFy7yLdr0HCbbUq_eYvbNN4ht_azRikLGqWotFNV7hq7URQLLOhuqIfECyOVQfIvZhIenGiQSI9317-efcvLvIpkhy1FnX_THf5PUWGysWyGVblhi1UXSSUpqqZ5GIvdI38Zh5DuYZ2Vbs8EN1HH1nZk4NK_FwaRzjL5jWbybYAUo5GePB5o-8St62Gv82d3TqazMw9h06I2b8Pq_gJK4LnSC3Rw6m3k8s2cAMrFKZjgHcWI2blarZDD6Oj0_mMvvz6HLheGw3rmtiL_hDifmtfNMNSCTPn9WXntbjW_bc9ejelxvpilDe97hHOBtyg79xjGIEiYOhkSEEN2kDg"


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


if __name__ == "__main__":
    test_mcp_integration()
