import os
import ipaddress
import logging
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from starlette.responses import RedirectResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# In-memory storage for tokens and their IPs
# Format: {"token_value": "ip_address"}
token_store: Dict[str, str] = {}

def load_tokens_from_env() -> None:
    """Load tokens from environment variables into memory."""
    global token_store
    
    # Clear existing tokens
    token_store.clear()
    
    # Load tokens from environment variables (TOKEN1, TOKEN2, etc.)
    for key, value in os.environ.items():
        if key.startswith('TOKEN'):
            token_store[value] = "127.0.0.1"  # Default IP
            logger.info(f"Loaded token {key} from environment variables")
    
    if not token_store:
        logger.warning("No tokens found in environment variables")
    else:
        logger.info(f"Loaded {len(token_store)} tokens from environment variables")


@app.on_event("startup")
async def startup_event():
    """Initialize the application by loading tokens from environment variables."""
    load_tokens_from_env()


def _token_valid(token: str) -> bool:
    """Check if token exists in the token store."""
    return token in token_store


@app.get("/ip/{token}")
async def get_ip(token: str):
    """Get IP for a token."""
    if not _token_valid(token):
        raise HTTPException(status_code=400, detail="Invalid token")
    ip = token_store[token]
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

@app.get("/register/{token}/{ip}")
async def register(token: str, ip: str = None):
    """Update IP for a token in memory."""
    if not _token_valid(token):
        raise HTTPException(status_code=400, detail="Invalid token")
    if ip is None:
        raise HTTPException(status_code=400, detail="Missing IP")
    
    _validate_ip_address(ip)
    
    # Update IP in memory
    old_ip = token_store.get(token, "not set")
    token_store[token] = ip.strip()
    
    logger.info(f"Updated IP for token {token}: {old_ip} -> {ip.strip()}")
    return {"token": token, "ip": ip.strip()}
