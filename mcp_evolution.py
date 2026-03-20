"""
MCP Server: Evolution API Integration
Controla WhatsApp via Evolution API
"""

import requests
import json
import os
from typing import Dict, Any, Optional


class EvolutionMCPServer:
    """MCP Server para Evolution API"""
    
    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.api_key = os.getenv("EVOLUTION_API_KEY", "CONSIGNADO123")
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
    
    def create_instance(self, instance_name: str) -> Dict[str, Any]:
        """Cria nova instância WhatsApp"""
        payload = {
            "instanceName": instance_name,
            "integration": "WHATSAPP-BUSINESS"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/instance/create",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return {
                    "sucesso": True,
                    "data": response.json(),
                    "status_code": response.status_code
                }
            else:
                return {
                    "sucesso": False,
                    "erro": f"Status {response.status_code}: {response.text}"
                }
        
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    def list_instances(self) -> Dict[str, Any]:
        """Lista todas as instâncias"""
        try:
            response = requests.get(
                f"{self.base_url}/instance/fetchInstances",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "sucesso": True,
                    "instances": response.json().get("instances", [])
                }
            else:
                return {
                    "sucesso": False,
                    "erro": f"Status {response.status_code}"
                }
        
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    def get_qrcode(self, instance_name: str) -> Dict[str, Any]:
        """Obtém QR Code para conectar"""
        try:
            response = requests.get(
                f"{self.base_url}/instance/fetchInstances",
                params={"instanceName": instance_name},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                instances = response.json().get("instances", [])
                
                for inst in instances:
                    if inst.get("instance", {}).get("instanceName") == instance_name:
                        return {
                            "sucesso": True,
                            "hash": inst.get("instance", {}).get("instanceId"),
                            "qr_code": inst.get("qrcode", {}).get("base64"),
                            "status": inst.get("instance", {}).get("status")
                        }
                
                return {"sucesso": False, "erro": "Instância não encontrada"}
            else:
                return {"sucesso": False, "erro": f"Status {response.status_code}"}
        
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    def send_message(self, instance_name: str, number: str, message: str) -> Dict[str, Any]:
        """Envia mensagem"""
        payload = {
            "number": number,
            "text": message
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/message/sendText/{instance_name}",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "sucesso": True,
                    "message_id": response.json().get("key", {}).get("id"),
                    "timestamp": response.json().get("timestamp")
                }
            else:
                return {
                    "sucesso": False,
                    "erro": f"Status {response.status_code}: {response.text}"
                }
        
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    def get_instance_status(self, instance_name: str) -> Dict[str, Any]:
        """Status da instância"""
        try:
            response = requests.get(
                f"{self.base_url}/instance/fetchInstances",
                params={"instanceName": instance_name},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                instances = response.json().get("instances", [])
                
                for inst in instances:
                    if inst.get("instance", {}).get("instanceName") == instance_name:
                        return {
                            "sucesso": True,
                            "instance_name": instance_name,
                            "status": inst.get("instance", {}).get("status"),
                            "online": inst.get("instance", {}).get("isOnline", False)
                        }
                
                return {"sucesso": False, "erro": "Instância não encontrada"}
            else:
                return {"sucesso": False, "erro": f"Status {response.status_code}"}
        
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    def send_bulk_messages(self, instance_name: str, numbers: list, message: str) -> Dict[str, Any]:
        """Envia mensagens em bulk"""
        results = {
            "total": len(numbers),
            "sucesso": 0,
            "erro": 0,
            "detalhes": []
        }
        
        for number in numbers:
            result = self.send_message(instance_name, number, message)
            
            if result.get("sucesso"):
                results["sucesso"] += 1
            else:
                results["erro"] += 1
            
            results["detalhes"].append({
                "number": number,
                "status": "sucesso" if result.get("sucesso") else "erro",
                "mensagem": result.get("message_id") if result.get("sucesso") else result.get("erro")
            })
        
        return results


# Instância global
evolution_mcp = EvolutionMCPServer()


# Endpoints para MCP Protocol
MCP_TOOLS = [
    {
        "name": "create_whatsapp_instance",
        "description": "Criar nova instância WhatsApp",
        "input_schema": {
            "type": "object",
            "properties": {
                "instance_name": {
                    "type": "string",
                    "description": "Nome da instância"
                }
            },
            "required": ["instance_name"]
        }
    },
    {
        "name": "list_whatsapp_instances",
        "description": "Listar instâncias WhatsApp",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_qrcode",
        "description": "Obter QR Code para conectar",
        "input_schema": {
            "type": "object",
            "properties": {
                "instance_name": {"type": "string"}
            },
            "required": ["instance_name"]
        }
    },
    {
        "name": "send_message",
        "description": "Enviar mensagem WhatsApp",
        "input_schema": {
            "type": "object",
            "properties": {
                "instance_name": {"type": "string"},
                "number": {"type": "string"},
                "message": {"type": "string"}
            },
            "required": ["instance_name", "number", "message"]
        }
    },
    {
        "name": "get_instance_status",
        "description": "Status da instância",
        "input_schema": {
            "type": "object",
            "properties": {
                "instance_name": {"type": "string"}
            },
            "required": ["instance_name"]
        }
    }
]


def handle_tool_call(tool_name: str, tool_input: Dict) -> str:
    """Handler para chamadas de ferramentas MCP"""
    
    if tool_name == "create_whatsapp_instance":
        result = evolution_mcp.create_instance(tool_input["instance_name"])
    
    elif tool_name == "list_whatsapp_instances":
        result = evolution_mcp.list_instances()
    
    elif tool_name == "get_qrcode":
        result = evolution_mcp.get_qrcode(tool_input["instance_name"])
    
    elif tool_name == "send_message":
        result = evolution_mcp.send_message(
            tool_input["instance_name"],
            tool_input["number"],
            tool_input["message"]
        )
    
    elif tool_name == "get_instance_status":
        result = evolution_mcp.get_instance_status(tool_input["instance_name"])
    
    else:
        result = {"erro": f"Ferramenta desconhecida: {tool_name}"}
    
    return json.dumps(result, ensure_ascii=False)
