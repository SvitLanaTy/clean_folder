from setuptools import setup, find_namespace_packages

setup(
    name='clean_folder',
    version='1.0.0',
    description='Script for sorting files',
    url='https://github.com/SvitLanaTy/clean_folder',
    author='Svitlana Tymchenko',
    license='MIT',
    packages=find_namespace_packages(),
    entry_points={'console_scripts': [
        'clean-folder=clean_folder.clean:start']}
)
