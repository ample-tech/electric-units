"""Functions to evaluate the maximum extractable flex."""

from setuptools import setup, find_packages

setup(
    name='electric_units',
    version='0.1.3',
    description='For handling units of measurement in electricity grid data.',
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
