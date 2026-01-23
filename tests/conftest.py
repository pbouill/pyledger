import logging

# Set up basic logging configuration for all tests
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(levelname)s %(name)s %(message)s",
    force=True
)