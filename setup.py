# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='flashair_sync',
    version='0.0.22',
    author='Thomas Schüßler',
    author_email='vindolin@gmail.com',
    packages=['_flashair_sync'],
    scripts=['bin/flashair_sync'],
    url='https://github.com/vindolin/flashair_sync',
    license='MIT',
    description='Simple directory syncer for Toshiba Flashair SD cards (used in 3D printers).',
    long_description=open('README.rst').read(),
    install_requires=['requests', 'requests_toolbelt', 'tqdm'],
    keywords=['3d printing', 'flashair', 'sync'],
    classifiers=[
        'Development Status :: 4 - Beta',
    ],
)
