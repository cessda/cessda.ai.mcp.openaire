# OpenAIRE MCP Server

<!--
SPDX-License-Identifier: Apache-2.0
-->

MCP (Model Context Protocol) server for exploring the OpenAIRE Research Graph and ScholExplorer citation index. Enables AI assistants like Claude to discover citation relationships, find related research outputs, and retrieve comprehensive metadata for publications, datasets, and software.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Claude Desktop Setup](#claude-desktop-setup)
  - [Available Tools](#available-tools)
  - [Example Prompts](#example-prompts)
- [Development](#development)
- [Operations](#operations)
- [License](#license)

## Overview

This MCP server provides AI assistants with access to two powerful research discovery APIs:

- **ScholExplorer**: Citation index with 3.6 billion scholarly relationships linking publications, datasets, and software
- **OpenAIRE Research Graph**: Comprehensive metadata aggregator covering millions of research outputs with full abstracts, author affiliations, citation metrics, and funding information

### Features

- 🔗 Find all research outputs citing a specific DOI (publications, datasets, software)
- 📊 Retrieve comprehensive metadata from OpenAIRE Research Graph
- 🤖 Seamless integration with Claude Desktop and other MCP clients
- 🐳 Docker containerization support
- 📝 Structured JSON logging
- ⚙️ Configuration via environment variables (12-factor app)

### Available Tools

1. **find_related_research** - Find publications, datasets, and software citing a given DOI
2. **get_metadata** - Get detailed metadata for research products from OpenAIRE Graph

## Installation

### Requirements

- Python 3.10 or higher
- pip

### Install from Source

```bash
# Clone the repository
git clone https://github.com/cessda/cessda.ai.mcp.openaire.git
cd cessda.ai.mcp.openaire

# Install in development mode
pip install -e .
```

### Verify Installation

```bash
mcp-openaire --help
```

## Configuration

The server follows the 12-factor app methodology and is configured via environment variables.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAIRE_SCHOLEXPLORER_URL` | `https://api.scholexplorer.openaire.eu/v3` | ScholExplorer API base URL |
| `OPENAIRE_GRAPH_URL` | `https://api.openaire.eu/graph/v2` | OpenAIRE Graph API base URL |
| `OPENAIRE_API_TIMEOUT` | `30` | API request timeout (seconds) |
| `OPENAIRE_API_MAX_RETRIES` | `3` | Maximum retry attempts |
| `OPENAIRE_LOG_LEVEL` | `WARN` | Logging level (INFO, WARN, ERROR) |
| `OPENAIRE_DEFAULT_LIMIT` | `200` | Default citation result limit |
| `OPENAIRE_MAX_LIMIT` | `1000` | Maximum citation result limit |
| `OPENAIRE_PAGE_SIZE` | `50` | Results per API page request |

### Configuration File (Optional)

Create a `.env` file in your working directory:

```bash
OPENAIRE_API_TIMEOUT=60
OPENAIRE_LOG_LEVEL=INFO
OPENAIRE_DEFAULT_LIMIT=100
```

## Usage

### Claude Desktop Setup

1. **Locate your Claude Desktop configuration file:**

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add the MCP server configuration:**

```json
{
  "mcpServers": {
    "openaire": {
      "command": "python",
      "args": ["-m", "mcp_openaire.server"],
      "env": {
        "OPENAIRE_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Or if installed via pip:

```json
{
  "mcpServers": {
    "openaire": {
      "command": "mcp-openaire"
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Verify the server is connected** - Look for the MCP icon or check available tools

### Available Tools

#### 1. find_related_research

Find publications, datasets, and software that cite a given DOI.

**Parameters:**
- `doi` (required): DOI to find citations for (e.g., "10.21338/NSD-ESS8-2016")
- `limit` (optional): Max results (1-1000, default: 200)

**Returns:** Citation links from ScholExplorer with:
- Total citations found
- Array of citing objects with titles, authors, DOIs, publication dates
- Relationship types (cites, references)
- Object types (publication, dataset, software)
- Link providers (OpenCitations, Crossref, DataCite)

#### 2. get_metadata

Get comprehensive metadata for a research product from OpenAIRE Research Graph.

**Parameters:**
- `identifier` (required): DOI or OpenAIRE ID (e.g., "10.2139/ssrn.3991520")

**Returns:** Enriched metadata including:
- Full title and abstract
- Complete author list with affiliations and ORCID IDs
- Publication date and publisher
- Citation metrics
- Access rights and open access status
- Funding information
- Subject classifications
- Access URLs

### Example Prompts

Try these prompts in Claude Desktop:

1. **Find citations for a dataset:**
   > "Find all publications citing the European Social Survey dataset 10.21338/NSD-ESS8-2016"

2. **Discover related research:**
   > "Show me the first 50 citations for DOI 10.2139/ssrn.3991520"

3. **Get detailed metadata:**
   > "Get me the full metadata for DOI 10.21338/NSD-ESS8-2016 including abstract and authors"

4. **Explore citation network:**
   > "Find all research citing dataset 10.5281/zenodo.1234567 and show me the top 10 by date"

5. **Combined workflow:**
   > "Find datasets in CESSDA about climate change, then for the first result, find all publications that cite it and get metadata for the most recent one"

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/cessda/cessda.ai.mcp.openaire.git
cd cessda.ai.mcp.openaire

# Install with development dependencies
pip install -e ".[dev]"
```

### Project Structure

```
mcp-openaire/
├── LICENSE.txt                    # Apache 2.0 license
├── README.md                      # This file
├── pyproject.toml                 # Python package configuration
├── Dockerfile                     # Container image (STDIO)
├── Dockerfile.http                # Container image (HTTP/SSE)
├── docker-compose.yml             # Docker Compose configuration
└── src/
    └── mcp_openaire/
        ├── __init__.py           # Package initialization
        ├── server.py             # FastMCP STDIO server
        ├── server_http.py        # FastMCP HTTP/SSE server
        ├── tools.py              # API integration logic
        ├── config.py             # Environment configuration
        └── logging_config.py     # Structured JSON logging
```

### Code Standards

- **Style**: PEP 8 (enforced via `black` and `ruff`)
- **Type Hints**: Required for all public functions
- **Documentation**: Docstrings for all modules, classes, and functions
- **Logging**: Structured JSON to stdout
- **Configuration**: Environment variables only (no hardcoded values)
- **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)

### Testing

```bash
# Run API integration tests
python test_api.py

# Format code
black src/

# Lint code
ruff check src/
```

## Operations

### Running in Docker

```bash
# Build image (STDIO mode)
docker build -t mcp-openaire:0.1.0 .

# Run container (STDIO mode)
docker run -i mcp-openaire:0.1.0

# Build HTTP/SSE image
docker build -f Dockerfile.http -t mcp-openaire-http:0.1.0 .

# Run HTTP server
docker run -d -p 8001:8000 mcp-openaire-http:0.1.0

# Using Docker Compose
docker compose up -d
docker compose logs -f
docker compose down
```

### Logging

The server outputs structured JSON logs to stdout:

```json
{
  "timestamp": "2025-01-15T10:30:45.123456Z",
  "level": "INFO",
  "message": "ScholExplorer search completed",
  "logger": "mcp_openaire",
  "doi": "10.21338/NSD-ESS8-2016",
  "total_available": 55,
  "results_returned": 55
}
```

**Log Levels:**
- `INFO`: Informational messages (API requests, results)
- `WARN`: Warnings requiring attention (validation issues, limits exceeded)
- `ERROR`: Errors requiring investigation (API failures, exceptions)

### Monitoring

Monitor the server using:
- JSON log aggregation (ELK, Splunk, etc.)
- Check for `ERROR` and `WARN` level messages
- Track API response times and failure rates
- Monitor citation search patterns

### Troubleshooting

**Issue:** Server not appearing in Claude Desktop

- Verify configuration file path and JSON syntax
- Check server installation: `which mcp-openaire`
- Review Claude Desktop logs for errors
- Restart Claude Desktop after configuration changes

**Issue:** API timeouts

- Increase `OPENAIRE_API_TIMEOUT` environment variable
- Check network connectivity to OpenAIRE APIs
- Review structured logs for timeout patterns
- Reduce `OPENAIRE_DEFAULT_LIMIT` for faster responses

**Issue:** No citations found

- Verify the DOI is correct and exists in ScholExplorer
- Not all DOIs have citations yet (especially new publications)
- Check that the DOI format is correct (starts with "10.")
- Try a well-known DOI like "10.21338/NSD-ESS8-2016" to test connectivity

**Issue:** Metadata not found

- Some DOIs may not be in OpenAIRE Graph yet
- Try searching ScholExplorer first to get an OpenAIRE ID
- Check the identifier format (DOI should start with "10.")

## Versioning

This project uses semantic versioning:

- **MAJOR**: Breaking changes to API or configuration
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Current version: **0.1.0**

## License

Copyright © 2025 CESSDA ERIC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

See [LICENSE.txt](LICENSE.txt) for full license text.

## Links

- [OpenAIRE Research Graph](https://graph.openaire.eu/)
- [ScholExplorer](https://scholexplorer.openaire.eu/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## Contributing

Contributions are welcome! Please open an issue or pull request.
