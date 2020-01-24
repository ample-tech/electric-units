"""Functions to evaluate the maximum extractable flex."""

from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='electric_units',
    version='1.0.0',
    description='For handling units of measurement in electricity grid data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='http://github.com/ample-tech/electric-units',
    author='ample sustainable brands',
    author_email='administrator@ample.tech',
    zip_safe=False,
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    keywords=['energy', 'grid', 'data', 'data transformation'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    setup_requires=['pytest-runner', 'pytest-pylint'],
    tests_require=['pytest', 'pylint'],
    install_requires=[
        'attrs',
        'python-dateutil',
        'pytz',
        'requests',
    ],
    extras_require={
        'pandas': [
            'numpy',
            'pandas>0.25',
        ]
    }
)
