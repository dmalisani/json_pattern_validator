import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
long_description = (HERE / "README.md").read_text()

setup(
    name='json_pattern_validator',
    packages=['json_pattern_validator'],
    description='Utility for evaluate matching json with a template',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.1',
    url='https://github.com/dmalisani/json_pattern_validator',
    author='Daniel Malisani',
    author_email='dmalisani@gmail.com',
    keywords=['json','schema','validation', 'validator', 'payload'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    include_package_data=False,
    extras_required = {
        "dev": ["pytest>6",]
    }
    )
