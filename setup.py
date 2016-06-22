# -*- coding: utf-8 -*-

import os
from setuptools import setup


def package_data(pkg, root_list):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for root in root_list:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


BLOCKS = [
    'audio = audio:AudioBlock',
]

setup(
    name='xblock-audio',
    version='0.1.0',
    description='XBlock - Audio',
    packages=['audio'],
    install_requires=[
        'XBlock',
        'xblock-utils',
    ],
    entry_points={
        'xblock.v1': BLOCKS,
    },
    package_data=package_data("audio", ["templates", "public"]),
)
