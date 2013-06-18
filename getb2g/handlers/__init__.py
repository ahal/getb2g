from ftptinderbox import FtpTinderboxHandler
from ftpnightly import FtpNightlyHandler
from pvtbpubtinderbox import PvtBPubTinderboxHandler
from pvtbpubnightly import PvtBPubNightlyHandler
from pvtbpvttinderbox import PvtBPvtTinderboxHandler
from pvtbpvtnightly import PvtBPvtNightlyHandler
from releases import ReleasesHandler

__all__ = ['all_handlers']
all_handlers = ['FtpTinderboxHandler',
                'FtpNightlyHandler',
                'PvtBPubTinderboxHandler',
                'PvtBPubNightlyHandler',
                'PvtBPvtTinderboxHandler',
                'PvtBPvtNightlyHandler',
                'ReleasesHandler',]
__all__.extend(all_handlers)
