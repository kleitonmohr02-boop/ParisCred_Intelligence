# 🔌 MCP Server - Evolution API

**Purpose**: Provide Copilot with direct integration to Evolution API for WhatsApp management.

## Configuration

```json
{
  "mcpServers": {
    "evolution-api": {
      "command": "python",
      "args": ["run_evolution_mcp.py"],
      "env": {
        "EVOLUTION_API_URL": "http://localhost:8080",
        "EVOLUTION_API_KEY": "CONSIGNADO123"
      }
    }
  }
}
```

## Available Tools

### 1. List WhatsApp Instances
```
get_whatsapp_instances()
Returns: List of all connected WhatsApp numbers
```

### 2. Create WhatsApp Instance
```
create_whatsapp_instance(instance_name, phone_number)
Returns: Instance ID and QR Code
```

### 3. Send Message
```
send_whatsapp_message(instance_name, phone_number, message, media_url=None)
Returns: Message ID or error
```

### 4. Get Instance Status
```
get_instance_status(instance_name)
Returns: Connection status, last activity, health metrics
```

### 5. Update Instance Settings
```
update_instance_settings(instance_name, settings_dict)
Returns: Success confirmation
```

## Implementation File (run_evolution_mcp.py)

```python
#!/usr/bin/env python3
"""
MCP Server for Evolution API Integration
Provides tools for WhatsApp management
"""

import json
import requests
import os
from typing import Any

EVOLUTION_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_KEY = os.getenv("EVOLUTION_API_KEY", "CONSIGNADO123")

class EvolutionMCPServer:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "apikey": EVOLUTION_KEY
        }
    
    def create_instance(self, instance_name: str) -> dict:
        """Create new WhatsApp instance"""
        payload = {
            "instanceName": instance_name,
            "integration": "WHATSAPP-BUSINESS"
        }
        
        response = requests.post(
            f"{EVOLUTION_URL}/instance/create",
            json=payload,
            headers=self.headers
        )
        
        return response.json()
    
    def get_instances(self) -> dict:
        """List all instances"""
        response = requests.get(
            f"{EVOLUTION_URL}/instance/fetchInstances",
            headers=self.headers
        )
        
        return response.json()
    
    def send_message(self, instance_name: str, number: str, message: str) -> dict:
        """Send text message"""
        payload = {
            "number": number,
            "text": message
        }
        
        response = requests.post(
            f"{EVOLUTION_URL}/message/sendText/{instance_name}",
            json=payload,
            headers=self.headers
        )
        
        return response.json()
    
    def get_qrcode(self, instance_name: str) -> dict:
        """Get QR code for connection"""
        response = requests.get(
            f"{EVOLUTION_URL}/instance/fetchInstances",
            params={"instanceName": instance_name},
            headers=self.headers
        )
        
        return response.json()

# Initialize
mcp = EvolutionMCPServer()

# Tool definitions for MCP protocol
TOOLS = [
    {
        "name": "create_whatsapp_instance",
        "description": "Create a new WhatsApp instance with Evolution API",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance_name": {
                    "type": "string",
                    "description": "Name for the new instance"
                }
            },
            "required": ["instance_name"]
        }
    },
    {
        "name": "list_whatsapp_instances",
        "description": "List all connected WhatsApp instances",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "send_whatsapp_message",
        "description": "Send a message via WhatsApp",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance_name": {"type": "string"},
                "number": {"type": "string"},
                "message": {"type": "string"}
            },
            "required": ["instance_name", "number", "message"]
        }
    }
]
```

## Usage Examples

When Copilot needs to work with WhatsApp:

1. **Check connected numbers**:
   ```
   I'll list all your connected WhatsApp instances...
   ```

2. **Send bulk messages**:
   ```
   I'll create a campaign and send messages to all customers in batch...
   ```

3. **Setup maturation**:
   ```
   I'll create a new instance and start the number maturation process...
   ```

## Security Notes

- API key is stored securely in environment
- All requests use HTTPS/HTTP as configured
- Rate limiting should be implemented
- Webhook validation for incoming messages
