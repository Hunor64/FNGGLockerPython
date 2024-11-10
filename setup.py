from setuptools import setup, find_packages

APP=['fngglocker.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['requests', 'aiohttp', 'colored', 'colorama', 'asyncio'],
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
        'colored',
        'colorama',
        'requests',
        'asyncio',
    ],
)