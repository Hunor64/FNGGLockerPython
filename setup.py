from setuptools import setup, find_packages

APP = ['fngglocker.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['ctypes'],
    # 'frameworks': ['/System/Library/Frameworks/Carbon.framework'],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=['py2app'],
    name='FNGGLocker',
    version='2.0',
    packages=find_packages(),
)