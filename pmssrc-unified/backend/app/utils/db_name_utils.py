"""
Utility functions for database name sanitization.
"""

def sanitize_organisation_id(organisation_id: str) -> str:
    """
    Sanitize organisation_id to be used as a MongoDB database name.
    Replaces spaces with underscores and strips leading/trailing whitespace.
    """
    if organisation_id:
        return organisation_id.strip().replace('.', '_').replace(' ', '_')
    return organisation_id 