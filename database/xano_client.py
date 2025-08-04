"""
Xano API Client for handling HTTP communication with Xano backend
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
import httpx
from datetime import datetime
import asyncio


class XanoAPIError(Exception):
    """Custom exception for Xano API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class XanoClient:
    """Async HTTP client for Xano API communication"""
    
    def __init__(self):
        self.base_url = os.getenv('XANO_BASE_URL', 'https://your-workspace.xano.com/api:version')
        self.api_token = os.getenv('XANO_API_TOKEN', '')  # Optional for public endpoints
        self.timeout = float(os.getenv('XANO_TIMEOUT', '30.0'))
        self._client: Optional[httpx.AsyncClient] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the HTTP client"""
        if not self._initialized:
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Only add Authorization header if API token is provided
            if self.api_token:
                headers['Authorization'] = f'Bearer {self.api_token}'
            
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=self.timeout
            )
            self._initialized = True
    
    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._initialized = False
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to Xano API"""
        if not self._initialized:
            await self.initialize()
        
        try:
            if method.upper() == 'GET':
                response = await self._client.get(endpoint, params=params)
            elif method.upper() == 'POST':
                response = await self._client.post(endpoint, json=data, params=params)
            elif method.upper() == 'PUT':
                response = await self._client.put(endpoint, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = await self._client.delete(endpoint, params=params)
            else:
                raise XanoAPIError(f"Unsupported HTTP method: {method}")
            
            # Handle HTTP errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": response.text}
                
                raise XanoAPIError(
                    f"Xano API error: {response.status_code} - {error_data}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            # Parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"success": True, "data": response.text}
                
        except httpx.TimeoutException:
            raise XanoAPIError("Request timeout while communicating with Xano")
        except httpx.RequestError as e:
            raise XanoAPIError(f"Request error: {str(e)}")
    
    # Basic CRUD conversation endpoints
    async def create_conversation(self, conversation_data: Dict) -> Dict[str, Any]:
        """Create a new conversation in Xano"""
        return await self._make_request('POST', '/conversations', data=conversation_data)
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation by conversation_id (not Xano's internal ID)"""
        try:
            params = {'search': conversation_id}
            response = await self._make_request('GET', '/conversations/search', params=params)
            
            conversations = response if isinstance(response, list) else response.get('data', [])
            return conversations[0] if conversations else None
            
        except XanoAPIError as e:
            if e.status_code == 404:
                return None
            raise
    
    async def get_conversations(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all conversations with pagination"""
        params = {'limit': limit, 'offset': offset}
        response = await self._make_request('GET', '/conversations/list', params=params)
        return response if isinstance(response, list) else response.get('data', [])
    
    async def update_conversation(self, conversation_id: str, conversation_data: Dict) -> Dict[str, Any]:
        """Update an existing conversation by conversation_id"""
        # First get the Xano ID by conversation_id
        existing = await self.get_conversation(conversation_id)
        if not existing:
            raise XanoAPIError(f"Conversation not found: {conversation_id}", status_code=404)
            
        xano_id = existing.get('id')
        return await self._make_request('PUT', f'/conversations/{xano_id}', data=conversation_data)
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation by conversation_id"""
        try:
            existing = await self.get_conversation(conversation_id)
            if not existing:
                return False
                
            xano_id = existing.get('id')
            await self._make_request('DELETE', f'/conversations/{xano_id}')
            return True
        except XanoAPIError as e:
            if e.status_code == 404:
                return False
            raise


# Global client instance
_xano_client: Optional[XanoClient] = None


async def get_xano_client() -> XanoClient:
    """Get the global Xano client instance"""
    global _xano_client
    if _xano_client is None:
        _xano_client = XanoClient()
        await _xano_client.initialize()
    return _xano_client


async def close_xano_client():
    """Close the global Xano client"""
    global _xano_client
    if _xano_client:
        await _xano_client.close()
        _xano_client = None 