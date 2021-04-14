from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tfwsdk',
    version='1.0.2',
    author='Avatao.com Innovative Learning Kft.',
    author_email='support@avatao.com',
    packages=find_packages(),
    url='https://github.com/avatao-content/tfwsdk-python',
    license='Apache License 2.0',
    description='Python SDK for our Tutorial Framework',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'pyzmq >= 19.0.2',
        'tornado >= 6.0.4'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
)