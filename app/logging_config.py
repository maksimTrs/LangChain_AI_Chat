import logging
import sys

def setup_logging(log_level=logging.INFO):
    """
    Configures basic logging for the application.
    """
    # Get the root logger
    logger = logging.getLogger()

    # Remove any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s"
    )

    # Create a handler for stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(log_level)
    stdout_handler.setFormatter(formatter)

    # Add the handler to the root logger
    logger.addHandler(stdout_handler)
    logger.setLevel(log_level)

    # Suppress overly verbose loggers from dependencies if necessary
    logging.getLogger("httpx").setLevel(logging.WARNING) # httpx can be very verbose with INFO
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING) # PIL can be verbose

    # Test message
    # logging.info("Logging configured successfully.")

# Call setup_logging by default when this module is imported,
# but allow for re-configuration if needed by calling it explicitly.
# setup_logging()
