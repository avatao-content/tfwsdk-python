from setuptools import setup, find_packages

setup(
   name='tfwsdk',
   version='1.0.0',
   author='Avatao.com Innovative Learning Kft.',
   author_email='support@avatao.com',
   packages=find_packages(),
   url='https://github.com/avatao-content/tfwsdk',
   license='custom',
   description='An awesome package that does something',
   long_description=open('README.md').read(),
   install_requires=[
       'pyzmq >= 19.0.2',
       'tornado >= 6.0.4'
   ],
)