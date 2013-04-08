import getpass
import os
import sys

from base import (Base, EmulatorBase, GeckoBase, SymbolsBase, TestBase)

import mozlog
import mozfile

__all__ = ['all_handlers']

all_handlers = ['TinderboxHandler', 'PvtbuildsHandler']
__all__.extend(all_handlers)

class TinderboxHandler(Base, GeckoBase, SymbolsBase, TestBase):
    """
    Downloads resources from uploaded tinderbox builds
    """

    def __init__(self, username=None, password=None):
        super(TinderboxHandler, self).__init__()
        self.username = username
        self.password = password

    def prompt_story(self):
        pass

class PvtbuildsHandler(Base):
    """
    Downloads resources from pvtbuilds.mozilla.org
    """

