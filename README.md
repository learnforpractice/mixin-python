# Python Bindings for Mixin
<h3>
  <a
    target="_blank"
    href="https://mybinder.org/v2/gh/learnforpractice/mixin-python/HEAD?filepath=notebook%2Fhelloworld.ipynb"
  >
    Quick Start
    <img alt="Binder" valign="bottom" height="25px"
    src="https://mybinder.org/badge_logo.svg"
    />
  </a>
</h3>

# Dependencies

clang & go 1.6 & cmake


# Build

```
git clone https://github.com/learnforpractice/mixin-python --recursive
cd mixin-python
python3 -m pip install -r requirements-dev.txt 
```

Linux

```
./build_linux.sh
```

macOS X

```
./build_mac.sh
```

# Installation

```bash
python3 -m pip install dist/mixin-0.1.0-*
```

# Quick Start

```python
from mixin.mixin_api import MixinApi
api = MixinApi('http://mixin-node0.exinpool.com:8239')
api.create_address()
```

    {'address': 'XIN9M9T32UhraHpJ9Do4s7FVFeTpery49JB1u6bAcgLe2wY4As918roNTVmbh3GXuuoRLx5FyeuhvUQUmvtWtUthGdgBCdMG',
     'view_key': '6396fd4201bbec6f495ded697428003dfd227578174f97e034c94e1abb420d0f',
     'spend_key': '02f0ea8504740a1c2916e1b9965c23c242aeeb02d093f3f1ed0e5e0d494bc603'}

# Run mixin from Python

```bash
python3 -m mixin.main kernel --dir config --port 9000
```

# Reference

https://github.com/wenewzhang/mixin-python3-sdk

# License

[GPL3.0](./LICENSE)

