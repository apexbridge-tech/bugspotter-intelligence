"""Utility functions for extracting relevant information from bug metadata"""

from typing import Optional


def extract_console_errors(console_logs: list[dict], max_errors: int = 5) -> list[str]:
    """
    Extract error messages and stack traces from console logs

    Args:
        console_logs: List of console log objects from BugSpotter
        max_errors: Maximum number of errors to extract

    Returns:
        List of formatted error strings
    """
    if not console_logs:
        return []

    errors = []
    for log in console_logs:
        level = log.get('level', '').lower()

        # Extract errors and warnings (both are important for similarity)
        if level in ('error', 'warn'):
            message = log.get('message', '')
            stack = log.get('stack', '')

            # Combine message and first 3 lines of stack trace
            parts = [message]

            if stack:
                # Get first 3 lines of stack trace (most relevant)
                stack_lines = stack.strip().split('\n')[:3]
                parts.extend(stack_lines)

            error_text = ' | '.join(parts)
            errors.append(error_text)

    return errors[:max_errors]


def extract_failed_requests(network_logs: list[dict], max_requests: int = 3) -> list[str]:
    """
    Extract failed HTTP requests from network logs

    Args:
        network_logs: List of network request objects
        max_requests: Maximum number of failed requests to extract

    Returns:
        List of formatted request strings
    """
    if not network_logs:
        return []

    failed = []
    for req in network_logs:
        status = req.get('status', 200)

        # Extract 4xx and 5xx errors
        if status >= 400:
            method = req.get('method', 'GET')
            url = req.get('url', '')
            duration = req.get('duration', 0)

            # Format: "POST /api/login returned 500 (took 234ms)"
            failed.append(
                f"{method} {url} returned {status} (took {duration}ms)"
            )

    return failed[:max_requests]


def extract_environment_info(metadata: dict) -> str:
    """
    Extract relevant environment information

    Args:
        metadata: Metadata object from BugSpotter

    Returns:
        Formatted environment string
    """
    if not metadata:
        return ""

    parts = []

    if browser := metadata.get('browser'):
        parts.append(f"Browser: {browser}")

    if os := metadata.get('os'):
        parts.append(f"OS: {os}")

    if url := metadata.get('url'):
        # Extract just the path (domain might be different per environment)
        from urllib.parse import urlparse
        path = urlparse(url).path
        if path and path != '/':
            parts.append(f"Page: {path}")

    return " | ".join(parts)


def build_embedding_text(
        title: str,
        description: Optional[str],
        console_logs: Optional[list[dict]] = None,
        network_logs: Optional[list[dict]] = None,
        metadata: Optional[dict] = None
) -> str:
    """
    Build the complete text for embedding generation

    Combines all relevant information into a single string optimized
    for similarity search.

    Args:
        title: Bug title
        description: Bug description
        console_logs: Console log objects
        network_logs: Network request objects
        metadata: Environment metadata

    Returns:
        Combined text ready for embedding

    Example:
        >>> build_embedding_text(
        ...     title="Search crashes",
        ...     description="App fails when searching",
        ...     console_logs=[{
        ...         "level": "error",
        ...         "message": "TypeError: null reference"
        ...     }]
        ... )
        'Search crashes | App fails when searching | TypeError: null reference'
    """
    parts = [title]

    if description:
        parts.append(description)

    # Add console errors
    if console_logs:
        errors = extract_console_errors(console_logs)
        parts.extend(errors)

    # Add failed requests
    if network_logs:
        failed = extract_failed_requests(network_logs)
        parts.extend(failed)

    # Add environment (helps group platform-specific bugs)
    if metadata:
        env = extract_environment_info(metadata)
        if env:
            parts.append(env)

    # Join with separator that's meaningful but won't confuse embedding
    return " | ".join(filter(None, parts))