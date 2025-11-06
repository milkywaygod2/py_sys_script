"""
Setup configuration for sys_util_core package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text() if readme_file.exists() else ''

setup(
    name='sys_util_core',
    version='0.1.0',
    author='milkywaygod2',
    description='A comprehensive utility library for system automation tasks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/milkywaygod2/py_sys_script',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    keywords='utilities system automation commands files environment registry',
    project_urls={
        'Bug Reports': 'https://github.com/milkywaygod2/py_sys_script/issues',
        'Source': 'https://github.com/milkywaygod2/py_sys_script',
    },
)
