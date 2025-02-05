from setuptools import setup

setup(
    name = 'mfid',
    
    version = '1.0.0',
    
    description = 'MFID: a Mighty Fine Identifier',
    long_description =open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    
    # Author details
    author='Edward S. Barnard',
    author_email='esbarnard@lbl.gov',

    # license
    license='BSD',
    
    url='https://github.com/MolecularFoundry/mfid',

    py_modules=["mfid"],

    install_requires=["uuid7"],

)
