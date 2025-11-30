def get_log_colors(dark_mode: bool = False) -> dict:
    """Get colors for log levels."""
    if dark_mode:
        return {
            'DEBUG': '#888888',
            'INFO': '#4ec9b0',
            'WARNING': '#ce9178',
            'ERROR': '#f48771',
            'CRITICAL': '#c586c0',
        }
    else:
        return {
            'DEBUG': '#888888',
            'INFO': '#00aa00',
            'WARNING': '#ffaa00',
            'ERROR': '#ff0000',
            'CRITICAL': '#ff00ff',
        }


def get_threat_colors(dark_mode: bool = False) -> dict:
    """Get colors for threat levels."""
    if dark_mode:
        return {
            'none': '#4ec9b0',
            'low': '#dcdcaa',
            'medium': '#ce9178',
            'high': '#f48771',
            'following': '#c586c0',
        }
    else:
        return {
            'none': '#00aa00',
            'low': '#ffaa00',
            'medium': '#ff5500',
            'high': '#ff0000',
            'following': '#ff00ff',
        }