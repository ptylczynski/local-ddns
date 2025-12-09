# Local DDNS Service

A lightweight Dynamic DNS service that allows you to access devices on your local network using a consistent URL, even when their IP addresses change.

## Features

- Simple token-based authentication
- Automatic IP registration and updates
- Lightweight FastAPI backend
- Docker container support
- GitHub Actions CI/CD pipeline

## Prerequisites

- Python 3.11+
- Docker (optional)
- GitHub account (for container registry)

## Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/local-ddns.git
   cd local-ddns
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Docker

Build and run using Docker:

```bash
docker build -t local-ddns .
docker run -d --name ddns -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml local-ddns
```

## Configuration

1. The service will automatically create a `config.yaml` file with an empty tokens list if it doesn't exist.
2. Add tokens to the `config.yaml` file:
   ```yaml
   tokens:
     - token: "your-secure-token-here"
       ip: ""  # Will be updated automatically
   ```

## Usage

### Register/Update IP

```
GET /register/{token}/{ip}
```

Example:
```bash
curl "http://localhost:8000/register/your-secure-token-here/192.168.1.100"
```

### Get Registered IP

```
GET /ip/{token}
```

Example:
```bash
curl "http://localhost:8000/ip/your-secure-token-here"
```

## CI/CD with GitHub Actions

This repository includes a GitHub Actions workflow that automatically builds and pushes Docker images to GitHub Container Registry (GHCR) on every push to the `main` branch.

### Accessing the Container Image

Images are available at:
```
ghcr.io/your-username/local-ddns:latest
```

## Security Considerations

- Use HTTPS in production
- Keep your tokens secure and never commit them to version control
- Consider rate limiting for production use
- Use a reverse proxy (like Nginx) for additional security features

## License

[MIT](LICENSE)
