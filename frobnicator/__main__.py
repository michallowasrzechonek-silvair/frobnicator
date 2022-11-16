import sys
import logging
from . import frobnicate

logging.basicConfig(level=logging.INFO)

frobnicate(sys.argv[1])
