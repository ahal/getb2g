import getpass
import os
import sys

from base import (Base, EmulatorBase, GeckoBase, SymbolsBase, TestBase)

import mozlog
import mozfile

__all__ = ('TinderboxHandler')

class TinderboxHandler(Base, GeckoBase, SymbolsBase, TestBase):
    """
    Downloads resources from uploaded tinderbox builds
    """

    def __init__(self, branch, username=None, password=None):
        super(TinderboxHandler, self).__init__()

class PvtbuildsHandler(Base):
    """
    Downloads resources from pvtbuilds.mozilla.org
    """

