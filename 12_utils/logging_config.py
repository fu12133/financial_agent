"""
Unified Logging Configuration - Control log output for the entire system
"""
import logging
import sys


def setup_logging(verbose: bool = False, log_file: str = None):
    """
    Configure global logging

    Args:
        verbose: Whether to show detailed logs (DEBUG level)
        log_file: Log file path (optional)
    """
    # Root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    root_logger.handlers.clear()

    # Set log level
    if verbose:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.WARNING)  # Default to WARNING and above only

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Log format
    if verbose:
        format_str = '%(levelname)s:%(name)s:%(message)s'
    else:
        format_str = '%(message)s'

    formatter = logging.Formatter(format_str)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
        root_logger.addHandler(file_handler)

    # Suppress third-party library logs
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('requests').setLevel(logging.ERROR)
    logging.getLogger('pymilvus').setLevel(logging.ERROR)
    logging.getLogger('huggingface_hub').setLevel(logging.ERROR)
    logging.getLogger('transformers').setLevel(logging.ERROR)
    logging.getLogger('FlagEmbedding').setLevel(logging.ERROR)

    # Key module log level control
    if not verbose:
        # In non-verbose mode, only keep critical information
        logging.getLogger('08_pipeline.embedding').setLevel(logging.WARNING)
        logging.getLogger('10_storage.milvus_manager').setLevel(logging.WARNING)
        logging.getLogger('09_retrieve.rag_service').setLevel(logging.WARNING)
        logging.getLogger('09_retrieve.rag_searcher').setLevel(logging.WARNING)
        logging.getLogger('09_retrieve.llm_client').setLevel(logging.WARNING)
        logging.getLogger('07_memory').setLevel(logging.WARNING)
        logging.getLogger('06_intent').setLevel(logging.WARNING)
        logging.getLogger('11_report').setLevel(logging.WARNING)


# Convenience functions
def set_quiet_mode():
    """Set to quiet mode (only show errors and critical information)"""
    setup_logging(verbose=False)


def set_verbose_mode():
    """Set to verbose mode (show all debugging information)"""
    setup_logging(verbose=True)