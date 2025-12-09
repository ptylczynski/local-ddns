import os
import ipaddress
import aiofiles
from fastapi import FastAPI, HTTPException
import yaml
from starlette.responses import RedirectResponse

# Constants
CONFIG_FILE = "config.yaml"

app = FastAPI()
config = {}


async def load_config():
    if not os.path.isfile(CONFIG_FILE):
        default_config = {"tokens": []}
        async with aiofiles.open(CONFIG_FILE, "w") as f:
            await f.write(yaml.safe_dump(default_config))

    async with aiofiles.open(CONFIG_FILE, "r") as f:
        content = await f.read()
        return yaml.safe_load(content)


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
    
    for t in config["tokens"]:
        if t["token"] == token:
            t["ip"] = ip.strip()
            await save_config()
            return {"token": token, "ip": t.get("ip")}

    return {"response": "registered"}
