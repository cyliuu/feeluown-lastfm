#!/usr/bin/env python3

from setuptools import setup


setup(
    name='fuo_lastfm',
    version='0.0.1',
    description='feeluown lastfm plugin',
    author='Cyliuu',
    author_email='lcy940903@gmail.com',
    packages=[
        'fuo_lastfm',
    ],
    package_data={
        '': []
        },
    url='https://github.com/cyliuu/feeluown-lastfm',
    keywords=['feeluown', 'plugin', 'lastfm'],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        ),
    install_requires=[
        'pylast',
    ],
    entry_points={
        'fuo.plugins_v1': [
            'local = fuo_lastfm',
        ]
    },
)
