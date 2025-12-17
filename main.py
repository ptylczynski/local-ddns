import os
import ipaddress
import logging
from typing import Dict, Optional, Tuple
from fastapi import FastAPI, HTTPException, Request, Body
from starlette.responses import RedirectResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# In-memory storage for tokens, their secret tokens and IPs
# Format: {"token_value": {"secret": "secret_token", "ip": "ip_address"}}
token_store: Dict[str, Dict[str, str]] = {}

class RegisterRequest(BaseModel):
    secret_token: str
    ip: Optional[str] = None

def load_tokens_from_env() -> None:
    """Load tokens and their secrets from environment variables into memory.
    
    Expected format for environment variables:
    - TOKEN1=token_value
    - TOKEN1_SECRET=secret_value
    """
    global token_store
    
    # Clear existing tokens
    token_store.clear()
    tokens_loaded = 0
    
    # First pass: find all token values
    token_values = {}
    for key, value in os.environ.items():
        if key.startswith('TOKEN') and not key.endswith('_SECRET'):
            token_values[key] = value
    
    # Second pass: match tokens with their secrets
    for key, token_value in token_values.items():
        secret_key = f"{key}_SECRET"
        if secret_key in os.environ:
            secret_value = os.environ[secret_key]
            token_store[token_value] = {
                "secret": secret_value,
                "ip": "127.0.0.1"  # Default IP
            }
            tokens_loaded += 1
            logger.info(f"Loaded token {key} with secret from environment variables")
        else:
            logger.warning(f"No secret found for token {key}")
    
    if not token_store:
        logger.warning("No valid token-secret pairs found in environment variables")
    else:
        logger.info(f"Loaded {tokens_loaded} token-secret pairs from environment variables")


@app.on_event("startup")
async def startup_event():
    """Initialize the application by loading tokens from environment variables."""
    load_tokens_from_env()


def _token_valid(token: str, secret: Optional[str] = None) -> bool:
    """Check if token exists in the token store and optionally validate the secret."""
    if token not in token_store:
        return False
    if secret is not None and token_store[token]["secret"] != secret:
        return False
    return True


@app.get("/ip/{token}")
async def get_ip(token: str):
    """Get IP for a token."""
    if not _token_valid(token):
        raise HTTPException(status_code=400, detail="Invalid token")
    ip = token_store[token]["ip"]
    return RedirectResponse(url=f"http://{ip}/" if ip else "http://127.0.0.1/")

def _validate_ip_address(ip_str: str) -> None:
    """Validate IP address and port if present."""
    if ':' in ip_str:
        ip_part, *port_part = ip_str.rsplit(':', 1)
        try:
            port = int(port_part[0])
            if not (0 <= port <= 65535):
                raise ValueError("Port out of range")
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid port number")
        ip_to_validate = ip_part
    else:
        ip_to_validate = ip_str
    
    try:
        ipaddress.ip_address(ip_to_validate)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IP address format")

@app.post("/register/{token}")
async def register(token: str, request: Request):
    """Update IP for a token in memory.
    
    Request body should be JSON with the following structure:
    {
        "secret_token": "your_secret_token",
        "ip": "optional_ip_address"  # If not provided, will use request client IP
    }
    """
    try:
        data = await request.json()
        register_data = RegisterRequest(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")
    
    if not _token_valid(token, register_data.secret_token):
        raise HTTPException(status_code=403, detail="Invalid token or secret")
    
    # Use provided IP or client IP if not provided
    ip = register_data.ip or request.client.host
    
    if not ip:
        raise HTTPException(status_code=400, detail="Could not determine IP address")
    
    _validate_ip_address(ip)
    
    # Update IP in memory
    old_ip = token_store[token]["ip"]
    token_store[token]["ip"] = ip.strip()
    
    logger.info(f"Updated IP for token {token}: {old_ip} -> {ip.strip()}")
    return {"token": token, "ip": ip.strip()}
