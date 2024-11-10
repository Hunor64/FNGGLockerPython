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
    version='2.0',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'colored',
        'colorama',
        'requests',
        'asyncio',
    ],
    entry_points={
        'console_scripts': [
            'fngglocker=fngglocker:main',
        ],
    },
)