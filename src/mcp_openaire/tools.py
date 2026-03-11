# SPDX-License-Identifier: Apache-2.0
"""OpenAIRE API integration tools for research graph exploration."""

from typing import Any, Dict, List, Optional
from urllib.parse import quote
import httpx
from .config import config
from .logging_config import logger, log_with_context


async def find_related_objects(
    doi: str,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Find research objects citing the given DOI using ScholExplorer.

    Searches ScholExplorer's citation index to find publications, datasets, and
    software that cite the specified DOI. Automatically handles pagination to
    retrieve all results up to the specified limit.

    Args:
        doi: DOI of the research object to find citations for
             Example: "10.21338/NSD-ESS8-2016"
        limit: Maximum number of results to return (1-1000, defaults to 200)

    Returns:
        Dictionary containing:
        - doi: The queried DOI
        - totalLinks: Total number of citations found
        - resultsReturned: Number of results in this response
        - links: Array of citation objects with:
          - relationshipType: Type of relationship (e.g., "cites")
          - source: Object citing the DOI with:
            - identifiers: List of DOI, handle, OpenAIRE IDs
            - title: Title of the citing work
            - type: Object type (publication, dataset, software)
            - subType: More specific type (Article, Collection, etc.)
            - creators: List of authors with ORCID IDs
            - publicationDate: Publication date
            - publishers: List of publishers/repositories
          - linkProvider: Source of the citation link (e.g., "OpenCitations")

    Raises:
        httpx.HTTPError: If API request fails
        ValueError: If DOI is invalid or limit is out of range

    Examples:
        Find all citations for a dataset:
        {"doi": "10.21338/NSD-ESS8-2016"}

        Limit to first 50 citations:
        {"doi": "10.21338/NSD-ESS8-2016", "limit": 50}
    """
    # Validate and set limit
    limit = limit or config.default_links_limit
    if limit > config.max_links_limit:
        log_with_context(
            logger,
            "WARN",
            "Links limit exceeds maximum",
            requested_limit=limit,
            max_limit=config.max_links_limit,
        )
        limit = config.max_links_limit

    # Validate DOI
    if not doi or not isinstance(doi, str):
        raise ValueError("DOI must be a non-empty string")

    log_with_context(
        logger,
        "INFO",
        "Starting ScholExplorer search",
        doi=doi,
        limit=limit,
    )

    # Collect all results across pages
    all_links = []
    current_page = 0
    total_links = 0

    url = f"{config.scholexplorer_base_url}/Links"

    try:
        async with httpx.AsyncClient(timeout=config.api_timeout) as client:
            while len(all_links) < limit:
                # Calculate how many results we need
                remaining = limit - len(all_links)
                page_size = min(config.links_page_size, remaining)

                params = {
                    "targetPid": doi,
                    "page": current_page,
                    "size": page_size,
                }

                log_with_context(
                    logger,
                    "INFO",
                    "Fetching ScholExplorer page",
                    page=current_page,
                    page_size=page_size,
                    url=url,
                )

                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                # Update total count from first page
                if current_page == 0:
                    total_links = data.get("totalLinks", 0)
                    log_with_context(
                        logger,
                        "INFO",
                        "ScholExplorer total links found",
                        total_links=total_links,
                    )

                # Get results from this page
                page_results = data.get("result", [])
                if not page_results:
                    # No more results
                    break

                all_links.extend(page_results)

                # Check if we've reached the end
                if len(page_results) < page_size or len(all_links) >= total_links:
                    break

                current_page += 1

    except httpx.TimeoutException as e:
        log_with_context(
            logger,
            "ERROR",
            "ScholExplorer API timeout",
            url=url,
            timeout=config.api_timeout,
            error=str(e),
        )
        raise

    except httpx.HTTPStatusError as e:
        log_with_context(
            logger,
            "ERROR",
            "ScholExplorer API request failed",
            url=url,
            status_code=e.response.status_code,
            error=str(e),
        )
        raise

    except Exception as e:
        log_with_context(
            logger,
            "ERROR",
            "Unexpected error during ScholExplorer request",
            url=url,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise

    log_with_context(
        logger,
        "INFO",
        "ScholExplorer search completed",
        doi=doi,
        total_available=total_links,
        results_returned=len(all_links),
    )

    return {
        "doi": doi,
        "totalLinks": total_links,
        "resultsReturned": len(all_links),
        "links": all_links,
    }


async def get_research_metadata(
    openaire_id: str,
) -> Dict[str, Any]:
    """Get detailed metadata for a research product from OpenAIRE Graph.

    Retrieves comprehensive metadata from the OpenAIRE Research Graph including
    abstracts, full author information with affiliations, citation metrics,
    access status, and funding information.

    IMPORTANT: This function requires an OpenAIRE dedup ID (not a DOI).
    To get OpenAIRE IDs, first use find_related_objects() which returns
    ScholExplorer results containing OpenAIRE IDs in the identifiers array.

    Args:
        openaire_id: OpenAIRE dedup identifier
                    (e.g., "doi_________::54b6bf0019fbdb3682539bcff4d0ff56")
                    Extract from ScholExplorer results at:
                    result['source']['Identifier'] where IDScheme == 'openaireIdentifier'

    Returns:
        Dictionary containing rich metadata:
        - id: OpenAIRE identifier
        - originalId: Original identifier (DOI, etc.)
        - title: Full title
        - description: Abstract/description
        - authors: List of authors with:
          - fullname: Author name
          - rank: Author position
          - pid: ORCID or other persistent ID
        - publisher: Publisher name
        - publicationdate: Publication date
        - type: Resource type (publication, dataset, software)
        - language: Language code
        - subjects: List of subject classifications
        - embargoenddate: Embargo date if applicable
        - collectedfrom: Data sources
        - instance: Access instances with URLs
        - country: Associated countries
        - contributors: Contributors list
        - format: Resource format
        - bestaccessright: Best available access right

    Raises:
        httpx.HTTPError: If API request fails
        ValueError: If identifier is invalid

    Examples:
        Get metadata by OpenAIRE ID from ScholExplorer result:
        {"openaire_id": "doi_________::54b6bf0019fbdb3682539bcff4d0ff56"}
    """
    if not openaire_id or not isinstance(openaire_id, str):
        raise ValueError("OpenAIRE ID must be a non-empty string")

    log_with_context(
        logger,
        "INFO",
        "Fetching research metadata",
        openaire_id=openaire_id,
    )

    # Validate that this looks like an OpenAIRE ID (contains ::)
    if "::" not in openaire_id:
        raise ValueError(
            f"Invalid OpenAIRE ID format: {openaire_id}. "
            "Expected format: 'prefix::hash' (e.g., 'doi_________::abc123...'). "
            "Get OpenAIRE IDs from ScholExplorer results first."
        )

    # ScholExplorer IDs have format: "50|doi_dedup___::hash"
    # Graph API needs just: "doi_dedup___::hash"
    # Strip the numeric prefix if present
    if '|' in openaire_id:
        openaire_id = openaire_id.split('|', 1)[1]
        log_with_context(
            logger,
            "INFO",
            "Stripped numeric prefix from OpenAIRE ID",
            cleaned_id=openaire_id,
        )

    # URL-encode the OpenAIRE ID (contains :: characters)
    encoded_id = quote(openaire_id, safe='')

    # Fetch metadata from Graph API
    url = f"{config.graph_api_base_url}/researchProducts/{encoded_id}"

    try:
        async with httpx.AsyncClient(timeout=config.api_timeout) as client:
            log_with_context(
                logger,
                "INFO",
                "Requesting OpenAIRE Graph API",
                url=url,
                openaire_id=openaire_id,
            )

            response = await client.get(url)
            response.raise_for_status()

            data = response.json()

            log_with_context(
                logger,
                "INFO",
                "OpenAIRE metadata retrieved",
                openaire_id=openaire_id,
                title=data.get("title", "N/A"),
            )

            return data

    except httpx.TimeoutException as e:
        log_with_context(
            logger,
            "ERROR",
            "OpenAIRE Graph API timeout",
            url=url,
            timeout=config.api_timeout,
            error=str(e),
        )
        raise

    except httpx.HTTPStatusError as e:
        log_with_context(
            logger,
            "ERROR",
            "OpenAIRE Graph API request failed",
            url=url,
            status_code=e.response.status_code,
            error=str(e),
        )
        raise

    except Exception as e:
        log_with_context(
            logger,
            "ERROR",
            "Unexpected error during OpenAIRE Graph request",
            url=url,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise
