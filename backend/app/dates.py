import dateparser
from datetime import datetime

def get_current_date() -> str:
    """Returns the current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")

def resolve_relative_date(relative_expression: str) -> str:
    """
    Resolves relative date expressions like "today", "tomorrow", "next Tuesday" to YYYY-MM-DD.
    If the expression is already a date or unresolvable, returns it as is.
    
    This function uses `dateparser` for robust parsing of natural language dates.
    It defaults to the current date if parsing fails but the input is empty or None.
    If parsing completely fails for a non-empty string, it returns the original string
    to let downstream services (like WeatherAPI) try to handle it or error out.
    """
    if not relative_expression:
        return get_current_date()
        
    # dateparser returns a datetime object or None
    parsed_date = dateparser.parse(
        relative_expression,
        settings={'PREFER_DATES_FROM': 'future'} # e.g. "Tuesday" usually means next Tuesday
    )
    
    if parsed_date:
        return parsed_date.strftime("%Y-%m-%d")
        
    return relative_expression
