#!/usr/bin/env python3
"""
Test script for the deployed Strands Agent Lambda function
Tests email activity creation functionality
"""

import json
import boto3
import requests
from typing import Dict, Any, Optional


class StrandsAgentTester:
    def __init__(self, function_name: str = "StrandsAgentFunction", region: str = "us-west-2"):
        """Initialize the tester with Lambda function details."""
        self.function_name = function_name
        self.region = region
        self.lambda_client = boto3.client('lambda', region_name=region)
        
        # Function URL from deployment (you may need to update this)
        self.function_url = "https://qqn2gktkhqjiycclsp5drxhxqq0gcnnq.lambda-url.us-west-2.on.aws/"
        
    def create_email_activity_prompt(
        self, 
        subject: str, 
        email_content: str, 
        sender_email: str,
        due_date: Optional[str] = None
    ) -> str:
        """Create the email activity prompt following the specified format."""
        
        summary_prompt = f"""Create email activity with brief summary:

Subject: {subject}
{f'Due Date: {due_date}' if due_date else ''}
{f'Sender Email: {sender_email}' if sender_email else ''}

Email Content:
{email_content}

Instructions:
- Set status to WORK IN PROGRESS by default
- FIRST: Call the seller lookup tool with contactType="EMAIL" and contactValue="{sender_email}" to get the seller name
- Include the seller name in the activity description (e.g., "Email activity from [Seller Name]:")
- Provide only a brief summary of this email in 2-3 sentences
- If seller lookup fails, proceed without seller name"""
        
        return summary_prompt
    
    def test_via_lambda_invoke(self, prompt: str, agent_type: str = "general") -> Dict[str, Any]:
        """Test the agent via direct Lambda invocation."""
        payload = {
            "prompt": prompt,
            "agent_type": agent_type
        }
        
        try:
            print("🚀 Invoking Lambda function directly...")
            response = self.lambda_client.invoke(
                FunctionName=self.function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            response_payload = json.loads(response['Payload'].read())
            return response_payload
            
        except Exception as e:
            return {"error": str(e), "method": "lambda_invoke"}
    
    def test_via_function_url(self, prompt: str, agent_type: str = "general") -> Dict[str, Any]:
        """Test the agent via Function URL."""
        payload = {
            "prompt": prompt,
            "agent_type": agent_type
        }
        
        try:
            print("🌐 Invoking via Function URL...")
            response = requests.post(
                self.function_url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "method": "function_url"
                }
                
        except Exception as e:
            return {"error": str(e), "method": "function_url"}
    
    def run_email_activity_test(self, method: str = "lambda"):
        """Run a simple test of email activity creation."""
        
        # Single test case
        test_case = {
            "subject": "Follow-up on Product Demo",
            "sender_email": "john.smith@acmecorp.com",
            "due_date": "2024-01-15",
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
        
        print("=" * 80)
        print("🧪 STRANDS AGENT EMAIL ACTIVITY TEST")
        print("=" * 80)
        
        print(f"\n📧 Testing: {test_case['subject']}")
        print("-" * 60)
        
        # Create the prompt
        prompt = self.create_email_activity_prompt(
            subject=test_case["subject"],
            email_content=test_case["email_content"],
            sender_email=test_case["sender_email"],
            due_date=test_case.get("due_date")
        )
        
        print(f"📤 Sender: {test_case['sender_email']}")
        print(f"📅 Due Date: {test_case.get('due_date', 'Not specified')}")
        print(f"📝 Content Length: {len(test_case['email_content'])} characters")
        
        # Execute the test
        if method == "lambda":
            result = self.test_via_lambda_invoke(prompt)
        else:
            result = self.test_via_function_url(prompt)
        
        # Display results
        self._display_result(result, 1)
        
        print("\n" + "="*80)
    
    def _display_result(self, result: Dict[str, Any], test_number: int):
        """Display the test result in a formatted way."""
        
        if "error" in result:
            print(f"❌ Test {test_number} FAILED:")
            print(f"   Error: {result['error']}")
            return
        
        print(f"✅ Test {test_number} SUCCESS:")
        
        # Extract response based on structure
        if "body" in result:
            # Lambda response format
            try:
                body = json.loads(result["body"]) if isinstance(result["body"], str) else result["body"]
                response_text = body.get("response", "No response text found")
                agent_type = body.get("agent_type", "unknown")
                
                print(f"   Status Code: {result.get('statusCode', 'N/A')}")
                print(f"   Agent Type: {agent_type}")
                print(f"   Response Length: {len(response_text)} characters")
                print(f"   Response Preview: {response_text[:200]}...")
                
            except json.JSONDecodeError:
                print(f"   Raw Response: {result}")
                
        else:
            # Direct response format
            response_text = result.get("response", str(result))
            print(f"   Response Length: {len(response_text)} characters")
            print(f"   Response Preview: {response_text[:200]}...")


def main():
    """Main function to run the test."""
    print("🚀 Testing Strands Agent Email Activity Creation...")
    
    # Initialize tester with default settings
    tester = StrandsAgentTester()
    
    # Run the email activity test using Lambda invoke method
    tester.run_email_activity_test("lambda")


if __name__ == "__main__":
    main()
