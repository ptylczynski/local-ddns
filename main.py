import os
import ipaddress
import logging
import aiofiles
from fastapi import FastAPI, HTTPException
import yaml
from starlette.responses import RedirectResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
CONFIG_FILE = "config.yaml"

app = FastAPI()
config = {}


async def load_config():
    # Initialize with default config
    default_config = {"tokens": []}
    
    # Load tokens from environment variables (TOKEN1, TOKEN2, etc.)
    tokens_from_env = []
    for key, value in os.environ.items():
        if key.startswith('TOKEN'):
            tokens_from_env.append({
                "token": value,
                "ip": "127.0.0.1"
            })
    
    if tokens_from_env:
        # Use tokens from environment variables
        default_config["tokens"] = tokens_from_env
    elif os.path.isfile(CONFIG_FILE):
        # Fall back to config file if no tokens in environment
        async with aiofiles.open(CONFIG_FILE, "r") as f:
            content = await f.read()
            config = yaml.safe_load(content)
            # Ensure all tokens have an IP set to 127.0.0.1 by default
            for token in config.get("tokens", []):
                if "ip" not in token:
                    token["ip"] = "127.0.0.1"
            return config
    
    # Save default config if no config file exists
    if not os.path.isfile(CONFIG_FILE):
        async with aiofiles.open(CONFIG_FILE, "w") as f:
            await f.write(yaml.safe_dump(default_config))
    
    return default_config


@app.on_event("startup")
async def startup_event():
    global config
    config = await load_config()


def _token_valid(token: str) -> bool:
    """Check if token exists in config."""
    return any(t["token"] == token for t in config["tokens"])


async def save_config():
    """Save the current config to file asynchronously."""
    async with aiofiles.open(CONFIG_FILE, "w") as f:
        await f.write(yaml.safe_dump(config))


@app.get("/ip/{token}")
async def get_ip(token: str):
    """Get IP for a token."""
    if not _token_valid(token):
        raise HTTPException(status_code=400, detail="Invalid token")
    for t in config["tokens"]:
        if t["token"] == token:
            return RedirectResponse(url=f"http://{t['ip']}/")
    return RedirectResponse(url="http://127.0.0.1/")

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
    """Register or update IP for a token."""
    if not _token_valid(token):
        raise HTTPException(status_code=400, detail="Invalid token")
    if ip is None:
        raise HTTPException(status_code=400, detail="Missing IP")
    _validate_ip_address(ip)
    # Check if token exists and update IP
    for t in config["tokens"]:
        if t["token"] == token:
            old_ip = t.get("ip", "not set")
            t["ip"] = ip.strip()
            await save_config()
            logger.info(f"Updated IP for token {token}: {old_ip} -> {ip.strip()}")
            return {"token": token, "ip": t.get("ip")}
    return {"response": "registered"}
