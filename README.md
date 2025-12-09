# Local DDNS Service

A lightweight Dynamic DNS service that allows you to access devices on your local network using a consistent URL, even when their IP addresses change. The service supports token-based authentication and can be configured via environment variables or a config file.

## Features

- Token-based authentication via environment variables or config file
- Automatic IP registration and updates
- Lightweight FastAPI backend
- Docker container support
- GitHub Actions CI/CD pipeline
- Built-in logging for IP changes

## Prerequisites

- Python 3.7+
- Docker (optional)
- aiofiles
- PyYAML
- FastAPI
- uvicorn (ASGI server)

## Installation

### Using pip

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/local-ddns.git
   cd local-ddns
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Using Docker

Build and run using Docker:

```bash
docker build -t local-ddns .
docker run -d --name ddns -p 8000:8000 \
  -e TOKEN1=your-secure-token-1 \
  -e TOKEN2=your-secure-token-2 \
  local-ddns
```

## Configuration

### Option 1: Environment Variables (Recommended)
Set tokens as environment variables with prefix `TOKEN` (e.g., `TOKEN1`, `TOKEN2`):

```bash
export TOKEN1=your-secure-token-1
export TOKEN2=your-secure-token-2
```

### Option 2: Config File
If no tokens are found in environment variables, the service will use `config.yaml`:

```yaml
tokens:
  - token: "your-secure-token-1"
    ip: "127.0.0.1"  # Default IP if not specified
  - token: "your-secure-token-2"
    ip: "192.168.1.100"
```

## API Endpoints

### Register/Update IP

```
GET /register/{token}/{ip}
```

Example:
```bash
curl "http://localhost:8000/register/your-secure-token-1/192.168.1.100"
```

Response:
```json
{
  "token": "your-secure-token-1",
  "ip": "192.168.1.100"
}
```

### Get Registered IP

```
GET /ip/{token}
```

Example:
```bash
curl -v "http://localhost:8000/ip/your-secure-token-1"
```

Response:
- On success: HTTP 302 redirect to `http://{registered-ip}/`
- On error: HTTP 400 with error message

## Logging

The service logs all IP changes and registrations:
```
2025-12-09 22:44:15,123 - __main__ - INFO - Updated IP for token your-token: 192.168.1.1 -> 192.168.1.2
```

## Docker Compose Example

```yaml
version: '3.8'

services:
  ddns:
    image: local-ddns:latest
    ports:
      - "8000:8000"
    environment:
      - TOKEN1=your-secure-token-1
      - TOKEN2=your-secure-token-2
    restart: unless-stopped
```

## Security Considerations

- Always use HTTPS in production
- Keep your tokens secure and never commit them to version control
- Regularly rotate your tokens
- Use a reverse proxy with rate limiting in production

## License

[MIT](LICENSE)
