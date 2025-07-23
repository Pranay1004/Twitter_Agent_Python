"""
Configuration Validator
Checks for the presence and validity of required API keys and settings.
"""

import os
from dotenv import load_dotenv
from .logger import setup_logger

logger = setup_logger(__name__)

def validate_config():
    """
    Validates that all required environment variables are set.
    Logs warnings for missing non-critical keys and raises an error for critical ones.
    """
    load_dotenv()
    logger.info("Starting configuration validation...")

    required_keys = {
        "CRITICAL": [
            ("X_CLIENT_ID", "Twitter/X Client ID"),
            ("X_CLIENT_SECRET", "Twitter/X Client Secret"),
            ("GEMINI_API_KEY", "Gemini API Key"),
        ],
        "OPTIONAL": [
            ("PERPLEXITY_API_KEY", "Perplexity API Key"),
            ("UNSPLASH_ACCESS_KEY", "Unsplash Access Key"),
            ("PEXELS_API_KEY", "Pexels API Key"),
            ("BITLY_ACCESS_TOKEN", "Bitly Access Token"),
            ("STABILITY_API_KEY", "Stability API Key"),
        ]
    }

    missing_critical_keys = []
    is_valid = True

    # Check critical keys
    for key, name in required_keys["CRITICAL"]:
        if not os.getenv(key):
            logger.error(f"CRITICAL CONFIG ERROR: {name} ({key}) is not set in .env file.")
            missing_critical_keys.append(name)
            is_valid = False

    # Check optional keys
    for key, name in required_keys["OPTIONAL"]:
        if not os.getenv(key):
            logger.warning(f"Optional config missing: {name} ({key}) is not set. Some features may be disabled.")

    if not is_valid:
        error_message = (
            "Application cannot start due to missing critical configurations: "
            f"{', '.join(missing_critical_keys)}. "
            "Please check your .env file."
        )
        logger.critical(error_message)
        raise ValueError(error_message)

    logger.info("Configuration validation successful.")
    return True

if __name__ == "__main__":
    # Example of how to run the validator
    try:
        validate_config()
        print("✅ Configuration is valid.")
    except ValueError as e:
        print(f"❌ Configuration validation failed: {e}")
