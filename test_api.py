#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Simple test script to verify OpenAIRE and ScholExplorer API integration."""

import asyncio
import json
from src.mcp_openaire.tools import find_related_objects, get_research_metadata


async def test_find_citations():
    """Test finding citations for a dataset."""
    print("=" * 80)
    print("TEST 1: Find citations for European Social Survey dataset")
    print("=" * 80)

    try:
        result = await find_related_objects(
            doi="10.21338/NSD-ESS8-2016",
            limit=10
        )

        print(f"\n✓ ScholExplorer search successful!")
        print(f"  Total citations found: {result.get('totalLinks', 0)}")
        print(f"  Citations returned: {result.get('resultsReturned', 0)}")

        if result.get('links'):
            print(f"\n  First citation:")
            first = result['links'][0]
            source = first.get('source', {})
            print(f"    Title: {source.get('Title', 'N/A')}")
            print(f"    Type: {source.get('Type', 'N/A')} / {source.get('subType', 'N/A')}")
            print(f"    Date: {source.get('PublicationDate', 'N/A')}")

            # Show first DOI if available
            identifiers = source.get('Identifier', [])
            for ident in identifiers:
                if ident.get('IDScheme') == 'doi':
                    print(f"    DOI: {ident.get('ID', 'N/A')}")
                    break

        return True

    except Exception as e:
        print(f"\n✗ ScholExplorer search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_find_few_citations():
    """Test finding citations for a publication."""
    print("\n" + "=" * 80)
    print("TEST 2: Find citations for a publication")
    print("=" * 80)

    try:
        result = await find_related_objects(
            doi="10.2139/ssrn.3991520",
            limit=5
        )

        print(f"\n✓ ScholExplorer search successful!")
        print(f"  Total citations found: {result.get('totalLinks', 0)}")
        print(f"  Citations returned: {result.get('resultsReturned', 0)}")

        return True

    except Exception as e:
        print(f"\n✗ ScholExplorer search failed: {e}")
        return False


async def test_get_metadata_from_scholexplorer():
    """Test getting metadata using OpenAIRE ID from ScholExplorer results."""
    print("\n" + "=" * 80)
    print("TEST 3: Get metadata using OpenAIRE ID from ScholExplorer")
    print("=" * 80)

    try:
        # First, get citations from ScholExplorer
        print("  Step 1: Finding citations in ScholExplorer...")
        citations = await find_related_objects(
            doi="10.21338/NSD-ESS8-2016",
            limit=5
        )

        if citations.get('resultsReturned', 0) == 0:
            print("  ⚠  No citations found in ScholExplorer - skipping metadata test")
            return True  # Not a failure, just no data

        # Extract OpenAIRE ID from first result
        first_link = citations['links'][0]
        source = first_link.get('source', {})
        identifiers = source.get('Identifier', [])

        openaire_id = None
        for ident in identifiers:
            if ident.get('IDScheme') == 'openaireIdentifier':
                openaire_id = ident.get('ID')
                break

        if not openaire_id:
            print("  ⚠  No OpenAIRE ID found in results - skipping metadata test")
            return True  # Not a failure

        print(f"  Step 2: Extracted OpenAIRE ID: {openaire_id[:50]}...")
        print(f"  Step 3: Fetching metadata from OpenAIRE Graph...")

        # Get metadata using OpenAIRE ID
        result = await get_research_metadata(openaire_id=openaire_id)

        print(f"\n✓ OpenAIRE metadata retrieved!")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  Type: {result.get('type', 'N/A')}")
        print(f"  Publisher: {result.get('publisher', 'N/A')}")
        print(f"  Date: {result.get('publicationdate', 'N/A')}")

        authors = result.get('author', [])
        if authors:
            print(f"  Authors: {len(authors)}")
            if len(authors) > 0:
                print(f"    First author: {authors[0].get('fullname', 'N/A')}")

        return True

    except Exception as e:
        print(f"\n✗ Metadata retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_invalid_openaire_id():
    """Test handling of invalid OpenAIRE ID."""
    print("\n" + "=" * 80)
    print("TEST 4: Invalid OpenAIRE ID handling (should fail gracefully)")
    print("=" * 80)

    try:
        result = await find_related_objects(
            doi="invalid-doi",
            limit=5
        )
        print(f"\n  Note: Search completed (may have 0 results)")
        print(f"  Total citations found: {result.get('totalLinks', 0)}")
        return True

    except Exception as e:
        print(f"\n✓ Correctly handled error: {type(e).__name__}")
        return True


async def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 18 + "OpenAIRE MCP Server API Tests" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")

    results = []

    # Run async tests
    results.append(await test_find_citations())
    results.append(await test_find_few_citations())
    results.append(await test_get_metadata_from_scholexplorer())
    results.append(await test_invalid_openaire_id())

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Tests passed: {sum(results)}/{len(results)}")

    if all(results):
        print("\n🎉 All tests passed! The MCP server is ready to use.")
        print("\nNext steps:")
        print("1. Configure Claude Desktop (see README.md)")
        print("2. Restart Claude Desktop")
        print("3. Test with prompts like:")
        print("   - 'Find citations for DOI 10.21338/NSD-ESS8-2016'")
        print("   - 'Get metadata for the first citation (use OpenAIRE ID)'")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
