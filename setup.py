from setuptools import setup, find_packages

APP = ['fngglocker.py']
OPTIONS = {
    'argv_emulation': False,
    'packages': ['requests', 'aiohttp', 'asyncio'],
}

setup(
    app=APP, 
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name='FNGGLocker',
    version='1.4.2',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'requests',
        'asyncio',
        'charset_normalizer',
        'colored',
        'colorama',
    ],
)