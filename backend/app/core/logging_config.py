import logging
import sys

def configure_logging():
    """
    Configuración básica de logging para aplicación.
    """

    logging.basicConfig(
        level= logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
    )

    logger = logging.getLogger("ferreteros")
    return logger