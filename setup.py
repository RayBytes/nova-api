import setuptools

with open('README.md', 'r', encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='nova-api',
    version='0.0.1',
    author='NovaOSS Contributors',
    author_email='owner@nova-oss.com',
    description='Nova API Server',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ]
)
