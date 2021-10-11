# Python Bindings for [Mixin](https://github.com/mixinNetwork/mixin)
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

# Install mixin-python

```bash
pip install mixin-python
```

# Quick Start

```python
import asyncio
from pymixin.mixin_api import MixinApi
api = MixinApi('http://mixin-node0.exinpool.com:8239')
addr = api.create_address()
print(addr)

async def get_info():
  info = await api.get_info()
  print(info)

asyncio.run(get_info())

```

```
    {'address': 'XIN9M9T32UhraHpJ9Do4s7FVFeTpery49JB1u6bAcgLe2wY4As918roNTVmbh3GXuuoRLx5FyeuhvUQUmvtWtUthGdgBCdMG',
     'view_key': '6396fd4201bbec6f495ded697428003dfd227578174f97e034c94e1abb420d0f',
     'spend_key': '02f0ea8504740a1c2916e1b9965c23c242aeeb02d093f3f1ed0e5e0d494bc603'}
```

# Run Mixin from Python

```bash
python3 -m pymixin.main kernel --dir config --port 9000
```

# Run a Local Mixin Testnet

```bash
python3 tests/start_testnet.py
```

Connect to Local Testnet

```python
import asyncio
from pymixin.mixin_api import MixinApi
api = MixinApi('http://127.0.0.1:8001')

async def get_info():
  info = await api.get_info()
  print(info)

asyncio.run(get_info())
```

# [Releases](https://github.com/learnforpractice/mixin-python/releases)

# [Docs](https://learnforpractice.github.io/mixin-python/)

# Install Build Dependencies

clang & go 1.16 & cmake

Ubuntu
```
sudo apt install python3-dev
sudo apt install python3-pip
sudo apt install clang
sudo apt install cmake
```

[Intall golang](https://golang.org/doc/install)


# Building

### Download Source Code

```
git clone https://github.com/learnforpractice/mixin-python --recursive
cd mixin-python
python3 -m pip install -r requirements-dev.txt 
```

### Update mixin-python Source Code

```bash
git pull
git submodule update --init --recursive
```

### Build on Linux

```
./build-linux.sh
```

### Build on macOS X

```
./build-mac.sh
```

# Run Tests in Jupyter Notebook
```bash
python3 -m pip install notebook
cd notebook
python3 -m notebook
```

Open helloworld.ipynb, hit Ctrl+Enter to run the test code in cell

Do not forget to run testnet.stop() to stop the testnet, otherwise the testnet processes will still running in the backgroud.

# Reference

https://github.com/wenewzhang/mixin-python3-sdk

# License

[GPL3.0](./LICENSE)

