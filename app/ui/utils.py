from __future__ import annotations


def format_percentage_colored(value: float, threshold: float = 0.90) -> str:
    """
    Format percentage value with color if above threshold.
    
    Args:
        value: Percentage value (0.0 to 1.0)
        threshold: Threshold for coloring (default 0.90)
    
    Returns:
        Formatted string, with HTML span if value >= threshold
    """
    pct_text = f"{value:.0%}"
    if value >= threshold:
        return f"<span style='color:limegreen; font-weight:700'>{pct_text}</span>"
    return pct_text

