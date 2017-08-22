from setuptools import setup

setup(
    name='tropopause',
    version='0.0.2',
    description="AWS CloudFormation creation library wrapper",
    author="Kris Holdich",
    author_email="kris.holdich@graze.com",
    url="https://github.com/graze/tropopause",
    license="The MIT License",
    packages=['tropopause'],
    test_suite="tests",
    install_requires=[
        "troposphere[policy]>=1.9.5, <2.0"
    ],
    use_2to3=False
)
