from . import configurations
from . import constants

from .paths import *
from .contexts import *
from .entries import *
from .queries import *
from .utilities import *

from contextlib import contextmanager

from ZODB.DB import DB as _DB
import transaction as _transaction


@contextmanager
def open():
    configurations.STORAGE = configurations.GET_STORAGE()
    configurations.DATABASE = _DB(configurations.STORAGE)
    configurations.CONNECTION = configurations.DATABASE.open()
    configurations.ROOT = configurations.CONNECTION.root()
    try:
        yield configurations.ROOT
    finally:
        # Just in case
        _transaction.abort()
        configurations.CONNECTION.close()
        configurations.DATABASE.close()
        configurations.STORAGE.close()
        configurations.STORAGE = None
        configurations.DATABASE = None
        configurations.CONNECTION = None


del contextmanager
