# Python Bindings for [ Mixin](https://github.com/mixinNetwork/mixin)
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

# [Releases](https://github.com/learnforpractice/mixin-python/releases/tag/v0.1)



# Install Build Dependencies

clang & go 1.16 & cmake

## Ubuntu
```
sudo apt install python3-dev
sudo apt install python3-pip
sudo apt install clang
sudo apt install cmake
```

[Intall golang](https://golang.org/doc/install)


# Building

### Download source code

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

# Installation

```bash
python3 -m pip install dist/mixin-0.1.0-*
```

## Install from Prebuild Package

Ubuntu python3.7
```bash
python3.7 -m pip install https://github.com/learnforpractice/mixin-python/releases/download/v0.1/mixin-0.1.0-cp37-cp37m-linux_x86_64.whl
```

Ubuntu python3.8
```bash
python3.8 -m pip install https://github.com/learnforpractice/mixin-python/releases/download/v0.1/mixin-0.1.0-cp38-cp38-linux_x86_64.whl
```

macOS X
```bash
python3.7 -m pip install https://github.com/learnforpractice/mixin-python/releases/download/v0.1/mixin-0.1.0-cp37-cp37m-macosx_10_9_x86_64.whl
```

# Quick Start

```python
from mixin.mixin_api import MixinApi
api = MixinApi('http://mixin-node0.exinpool.com:8239')
api.create_address()
```

```
    {'address': 'XIN9M9T32UhraHpJ9Do4s7FVFeTpery49JB1u6bAcgLe2wY4As918roNTVmbh3GXuuoRLx5FyeuhvUQUmvtWtUthGdgBCdMG',
     'view_key': '6396fd4201bbec6f495ded697428003dfd227578174f97e034c94e1abb420d0f',
     'spend_key': '02f0ea8504740a1c2916e1b9965c23c242aeeb02d093f3f1ed0e5e0d494bc603'}
```

```
api.get_info()
```

# Run Mixin from Python

```bash
python3 -m mixin.main kernel --dir config --port 9000
```

# Run a Local Mixin Testnet

```bash
python3 tests/start_testnet.py
```

# Run Tests in Jupyter Notebook
```bash
python3 -m pip install notebook
cd notebook
python3 -m notebook
```
Open helloworld.ipynb, hit Ctrl+Enter to run the test code in cell

Do not forget to run testnet.stop() to stop the testnet, otherwise the testnet processes will still running in the backgroud.

# [Mixin API document](mixin_api.md)


# Reference

https://github.com/wenewzhang/mixin-python3-sdk

# License

[GPL3.0](./LICENSE)
