from setuptools import setup, find_packages

setup(
    name='llomics',
    version='0.1.0',
    url='https://github.com/mniederhuber/llomics',  
    packages=find_packages(), 
    install_requires=[
        'pandas',  
        'openai',
        'tiktoken',
        'biopython',
        'pydantic'
        ],
    classifiers=[
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3', 
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',  
)
