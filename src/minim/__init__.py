import warnings

warnings.formatwarning = lambda message, *args, **kwargs: f"Warning: {message}"

__all__ = ["audio", "itunes", "spotify", "tidal", "utility"]