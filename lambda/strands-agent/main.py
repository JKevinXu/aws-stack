#!/usr/bin/env python3
"""
Bedrock Agent Core entry point for Strands Agent
Wraps the Lambda handler to work with Bedrock Agent Core HTTP server
"""

import json
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncio
from agent_handler import handler

app = FastAPI(title="Strands Agent", description="Strands Agent for Bedrock Agent Core")

@app.post("/invocations")
async def invoke_agent(request: Request):
    """
    Main endpoint for Bedrock Agent Core invocations
    """
    try:
        # Get the request body
        body = await request.body()
        
        # Parse the JSON payload
        if body:
            event = json.loads(body.decode('utf-8'))
        else:
            event = {}
            
        # Call the Lambda handler with None context (not used)
        response = handler(event, None)
        
        # Return the response
        return JSONResponse(content=response)
        
    except Exception as e:
        error_response = {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'An error occurred while processing the request'
            })
        }
        return JSONResponse(content=error_response, status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "strands-agent"}

@app.get("/ping")
async def ping():
    """Ping endpoint for Bedrock Agent Core health checks"""
    return {"status": "pong"}

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
