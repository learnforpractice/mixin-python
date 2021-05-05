from . import mixin_api
from . import mixin_bot_api

default_api = mixin_api.MixinApi()

def get_mixin_api():
    return default_api
