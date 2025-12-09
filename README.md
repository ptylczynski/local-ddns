# Local DDNS Service

A lightweight, in-memory Dynamic DNS service that allows you to access devices on your local network using a consistent URL. The service is stateless, with tokens and IPs stored only in memory and loaded from environment variables at startup.

## Features

- **In-memory storage** - No persistent storage required
- **Simple token-based authentication** - Configure via environment variables
- **Automatic IP registration** - Update IPs via API
- **Lightweight FastAPI backend** - High performance with minimal overhead
- **Docker container support** - Easy deployment
- **Built-in logging** - Track IP changes in real-time

## Prerequisites

- Python 3.7+
- Docker (optional)
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
   # Set tokens as environment variables
   export TOKEN1=your-secure-token-1
   export TOKEN2=your-secure-token-2
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

### Environment Variables

Set tokens as environment variables with prefix `TOKEN` (e.g., `TOKEN1`, `TOKEN2`). Each token will be initialized with a default IP of `127.0.0.1` which can be updated via the API.

```bash
# Example for multiple tokens
export TOKEN1=your-secure-token-1
export TOKEN2=your-secure-token-2
```

> **Note:** The service is stateless and loads tokens only at startup. Changes to environment variables require a restart.

## API Endpoints

### Register/Update IP

Update the IP address for a specific token.

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

Redirects to the registered IP for the given token.

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

The service logs all IP changes and important events:
```
2025-12-09 23:30:45,678 - __main__ - INFO - Loaded 2 tokens from environment variables
2025-12-09 23:31:15,123 - __main__ - INFO - Updated IP for token your-token: 127.0.0.1 -> 192.168.1.100
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

## Important Notes

- **Stateless by Design**: All data is stored in memory and will be lost on service restart
- **Environment Variables**: Tokens must be provided at startup via environment variables
- **No Persistence**: IP changes made via the API are not persisted across restarts
- **Development Use**: Primarily designed for development and local network use

## Security Considerations

- **HTTPS**: Always use HTTPS in production environments
- **Token Security**: Keep tokens secure and never commit them to version control
- **Network Security**: Run behind a reverse proxy with authentication in production
- **Rate Limiting**: Implement rate limiting at the reverse proxy level
- **Regular Rotation**: Regularly rotate your tokens

## License

[MIT](LICENSE)
