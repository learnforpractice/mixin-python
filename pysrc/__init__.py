from . import mixin_api
from . import mixin_bot_api
__VERSION__ = '0.2.0'

default_api = mixin_api.MixinApi()

def get_mixin_api():
    return default_api
