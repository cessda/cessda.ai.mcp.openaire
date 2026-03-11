# Quick Start - Virtualenv Setup

This guide will get you up and running quickly with virtualenv.

## Automated Setup

Run the setup script:

```bash
cd MCP_OpenAIRE
./setup_virtualenv.sh
```

This script will:
- Check Python version (requires 3.10+)
- Create a virtual environment in `venv/`
- Activate the virtual environment
- Install all dependencies
- Install the mcp-openaire package
- Create a `.env` file from template

## Manual Setup

If you prefer to set up manually:

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip setuptools wheel

# 4. Install package
pip install -e .

# 5. Create .env file
cp .env.http.example .env
nano .env  # Edit as needed
```

## Testing

Once installed, test the server:

```bash
# Make sure virtualenv is activated
source venv/bin/activate

# Run API tests
python test_api.py
```

Expected output:
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                  OpenAIRE MCP Server API Tests                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
================================================================================
TEST 1: Find citations for European Social Survey dataset
================================================================================

✓ ScholExplorer search successful!
  Total citations found: 55
  Citations returned: 10
...
Tests passed: 5/5

🎉 All tests passed! The MCP server is ready to use.
```

## Running the Server

### Local Development (STDIO mode)

```bash
source venv/bin/activate
python -m mcp_openaire.server
```

### HTTP Server (for remote access)

```bash
source venv/bin/activate
python -m mcp_openaire.server_http
```

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","service":"mcp-openaire","version":"0.1.0"}
```

## Server Deployment

For production deployment on a server, see [DEPLOYMENT.md](DEPLOYMENT.md) which covers:
- Systemd service setup
- Running as a background service
- Nginx reverse proxy
- SSL/TLS configuration
- Monitoring and logs
- Security best practices

## Configuration

Edit `.env` to customize settings:

```bash
# API Configuration
OPENAIRE_API_TIMEOUT=30          # Request timeout in seconds
OPENAIRE_LOG_LEVEL=INFO          # INFO, WARN, or ERROR

# Search Parameters
OPENAIRE_DEFAULT_LIMIT=200       # Default citation limit
OPENAIRE_MAX_LIMIT=1000          # Maximum citation limit
OPENAIRE_PAGE_SIZE=50            # Results per API page

# HTTP Server (for HTTP mode only)
MCP_HOST=0.0.0.0                 # Bind address
MCP_PORT=8000                    # Port number
```

## Using with Claude Desktop

1. Activate virtualenv and note the full path to Python:
```bash
source venv/bin/activate
which python
# Output: /opt/mcp-openaire/venv/bin/python
```

2. Edit Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "openaire": {
      "command": "/opt/mcp-openaire/venv/bin/python",
      "args": ["-m", "mcp_openaire.server"],
      "env": {
        "OPENAIRE_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

3. Restart Claude Desktop

## Deactivating Virtualenv

When you're done working:

```bash
deactivate
```

## Updating

To update the package after pulling new code:

```bash
source venv/bin/activate
pip install --upgrade -e .
```

## Troubleshooting

### "python3: command not found"
Install Python 3.10+:
```bash
sudo apt install python3.10 python3.10-venv -y
```

### "No module named mcp_openaire"
Make sure virtualenv is activated and package is installed:
```bash
source venv/bin/activate
pip install -e .
```

### Port 8000 already in use
Change port in `.env`:
```bash
MCP_PORT=8001
```

### API tests fail
Check internet connection and API availability:
```bash
curl https://api.scholexplorer.openaire.eu/v3/Links
curl https://api.openaire.eu/graph/v2/researchProducts
```

## Next Steps

- Read [README.md](README.md) for full documentation
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production server setup
- Check [CLAUDE.md](CLAUDE.md) for development guidance
