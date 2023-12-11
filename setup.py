#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

requirements = ["pandas", "numpy", "pathos", "shared_memory_wrapper", "kaleido", "plotly", "tabulate"]

test_requirements = ['pytest>=3', "hypothesis"]

setup(
    author="Ivar Grytten",
    author_email='ivar.grytten@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description="Snakehelp: Making snakemake easier to use.",
    long_description="Snakehelp",
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords='snakehelp',
    name='snakehelp',
    packages=find_packages(include=['snakehelp', 'snakehelp.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ivargr/snakehelp',
    version='0.0.20',
    zip_safe=False,
)
