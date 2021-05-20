#!/usr/bin/env python

from setuptools import setup

setup(
    name="RemoteGamer",
    version="1.0",
    description="Receive and replay input over internet.",
    author="Kevin Yen",
    author_email="yenkevin1203@gmail.com",
    url="https://github.com/NivekNey/RemoteGamer",
    packages=["remotegamer"],
    requires=["zmq"],
    extras_require={
        "remote": ["inputs"],
        "station": ["vgamepad"],
    },
    entry_points={"console_scripts": ["remotegamer=remotegamer.cli:main"]},
)
