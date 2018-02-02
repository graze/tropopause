from setuptools import setup

setup(
    name='graze-tropopause',
    version='1.1.1',
    description="lightweight troposphere wrapper",
    long_description="lightweight troposphere wrapper to aid with boilerplate",
    author="Graze Developers",
    author_email="developers@graze.com",
    url="https://github.com/graze/tropopause",
    license="The MIT License",
    packages=['tropopause'],
    test_suite="tests",
    install_requires=[
        "troposphere[policy]>=1.9.5, <2.0"
    ],
    python_requires='~=3.3',
    use_2to3=False
)
