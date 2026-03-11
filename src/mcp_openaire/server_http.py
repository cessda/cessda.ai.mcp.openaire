# SPDX-License-Identifier: Apache-2.0
"""MCP server for OpenAIRE research graph using HTTP/SSE transport."""

import os
from typing import Any, Dict, Optional
from fastmcp import FastMCP
from .tools import find_related_objects, get_research_metadata
from .logging_config import logger, log_with_context


# Initialize FastMCP server
mcp = FastMCP("OpenAIRE Research Graph")


@mcp.tool()
async def find_related_research(
    doi: str,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Find publications, datasets, and software that cite a given DOI.

    This tool searches ScholExplorer's comprehensive citation index to discover
    research outputs that cite the specified DOI. ScholExplorer aggregates citation
    links from major scholarly data sources including OpenCitations, Crossref, and
    DataCite, covering publications, datasets, and software.

    Use this tool when you want to:
    - Find what publications cite a specific dataset
    - Discover research that builds upon a particular paper
    - Explore the impact and usage of a research output
    - Map the citation network around a DOI

    Args:
        doi: DOI of the research object to find citations for.
             Example: "10.21338/NSD-ESS8-2016" (a dataset DOI)
                      "10.2139/ssrn.3991520" (a publication DOI)
        limit: Maximum number of citing objects to return (1-1000).
               Defaults to 200. The tool automatically handles pagination
               to retrieve all results up to this limit.

    Returns:
        Dictionary containing:
        - doi: The queried DOI
        - totalLinks: Total number of citations found in ScholExplorer
        - resultsReturned: Number of citations returned in this response
        - links: Array of citation objects, each containing:
          - relationshipType: Type of citation relationship
            - name: "IsRelatedTo"
            - subType: "cites" or "references"
          - source: The citing research object with:
            - identifiers: List of DOI, handle, and OpenAIRE IDs
            - title: Full title of the citing work
            - type: Object type ("publication", "dataset", "software")
            - subType: Specific type ("Article", "Part of book", "Collection", etc.)
            - creators: Array of authors with:
              - name: Author name
              - identifier: ORCID IDs if available
            - publicationDate: ISO date (YYYY-MM-DD)
            - publishers: Array of publishers/repositories
          - target: The cited object (your queried DOI)
          - linkProvider: Source of citation link ("OpenCitations", "Crossref", etc.)

    Raises:
        Error if DOI is invalid or API request fails

    Examples:
        Find all citations for a dataset (up to 200):
        {"doi": "10.21338/NSD-ESS8-2016"}

        Find first 50 citations for a paper:
        {"doi": "10.2139/ssrn.3991520", "limit": 50}

        Find all citations for a software release:
        {"doi": "10.5281/zenodo.1234567", "limit": 1000}
    """
    try:
        log_with_context(
            logger,
            "INFO",
            "Processing find_related_research request",
            doi=doi,
            limit=limit,
        )

        result = await find_related_objects(doi=doi, limit=limit)
        return result

    except Exception as e:
        error_msg = f"Failed to find related research: {str(e)}"
        log_with_context(
            logger,
            "ERROR",
            "Find related research request failed",
            doi=doi,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise Exception(error_msg)


@mcp.tool()
async def get_metadata(openaire_id: str) -> Dict[str, Any]:
    """Get comprehensive metadata for a research product from OpenAIRE Research Graph.

    This tool retrieves detailed metadata from the OpenAIRE Research Graph, which
    aggregates information from thousands of repositories worldwide. The Graph
    provides enriched metadata including abstracts, full author information with
    institutional affiliations, citation metrics, access rights, and funding details.

    IMPORTANT: This tool requires an OpenAIRE dedup ID, not a DOI.

    **Workflow to get metadata:**
    1. First use find_related_research() to find citations for a DOI
    2. Extract the OpenAIRE ID from the results (look for IDScheme: 'openaireIdentifier')
    3. Use this tool with that OpenAIRE ID to get full metadata

    Use this tool when you want to:
    - Get the full abstract and description of a research output
    - See complete author information with affiliations and ORCID IDs
    - Check access rights and find open access versions
    - View citation metrics and impact indicators
    - Discover funding information and project connections

    Args:
        openaire_id: OpenAIRE dedup identifier (e.g., "doi_________::54b6bf0019fbdb3682539bcff4d0ff56")
                    Extract this from ScholExplorer (find_related_research) results at:
                    result['links'][i]['source']['Identifier'] where IDScheme == 'openaireIdentifier'

    Returns:
        Dictionary containing comprehensive metadata:
        - id: OpenAIRE persistent identifier
        - originalId: Original identifier (DOI, handle, etc.)
        - title: Full title of the research output
        - description: Abstract or description
        - authors: Array of authors with:
          - fullname: Complete author name
          - rank: Author position in list
          - pid: Persistent identifier (ORCID, ISNI, etc.)
        - publisher: Publisher name
        - publicationdate: Publication date (YYYY-MM-DD)
        - type: Resource type (publication, dataset, software, other)
        - language: Language code (ISO 639-1)
        - subjects: Array of subject classifications (FOS, keywords, etc.)
        - embargoenddate: Embargo end date if applicable
        - collectedfrom: Array of data sources providing this record
        - instance: Array of access instances with:
          - url: Access URL
          - license: License information
          - accessright: Access rights (OPEN, RESTRICTED, etc.)
          - type: Version type (Published, Accepted, etc.)
        - country: Array of associated countries
        - contributors: Array of contributors
        - format: Resource format
        - bestaccessright: Best available access right across all instances

    Raises:
        Error if identifier is invalid or not found in OpenAIRE

    Examples:
        Get metadata by OpenAIRE ID from ScholExplorer result:
        {"openaire_id": "doi_________::54b6bf0019fbdb3682539bcff4d0ff56"}
    """
    try:
        log_with_context(
            logger,
            "INFO",
            "Processing get_metadata request",
            openaire_id=openaire_id,
        )

        result = await get_research_metadata(openaire_id=openaire_id)
        return result

    except Exception as e:
        error_msg = f"Failed to get research metadata: {str(e)}"
        log_with_context(
            logger,
            "ERROR",
            "Get metadata request failed",
            openaire_id=openaire_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise Exception(error_msg)


def main():
    """Main entry point for HTTP/SSE MCP server using uvicorn."""
    import uvicorn
    from starlette.responses import JSONResponse

    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))

    log_with_context(
        logger,
        "INFO",
        "Starting OpenAIRE MCP server via HTTP/SSE",
        host=host,
        port=port,
    )

    # Add health check route to MCP
    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request):
        from starlette.responses import JSONResponse
        return JSONResponse({"status": "healthy", "service": "mcp-openaire", "version": "0.1.0"})

    # Run server with uvicorn using FastMCP's SSE app
    uvicorn.run(
        mcp.http_app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
