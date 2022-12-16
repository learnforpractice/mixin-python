from . import mixin_api
from . import mixin_bot_api
from . import _mixin

__VERSION__ = '0.2.6'

_mixin.init()

default_api = mixin_api.MixinApi()

def get_mixin_api():
    return default_api
