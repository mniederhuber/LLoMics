from setuptools import setup, find_packages

setup(
    name='sragent',  # Replace 'sragent' with your package name
    version='0.1.0',  # Replace '0.1.0' with your package version
    author='m',  # Replace 'Your Name' with the package author's name
    author_email='your.email@example.com',  # Replace with the author's email
    description='place holder',  # Package description
    long_description=open('README.md').read(),  # Long description from README.md
    long_description_content_type='text/markdown',  # Content type of the long description
    url='https://github.com/yourusername/sragent',  # Replace with your repository URL
    packages=find_packages(),  # Automatically find and include all packages
    install_requires=[
        'pandas',  
        'openai',
        'biopython',
        'pydantic',
        'sqlite3',
        ],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Change as appropriate for your project's maturity
        'Intended Audience :: Developers',  # Change as appropriate for your target audience
        'License :: OSI Approved :: MIT License',  # Assuming MIT License; change as needed
        'Programming Language :: Python :: 3',  # Specify the supported Python versions
        'Programming Language :: Python :: 3.9',
        # Add additional Python versions as supported
    ],
    python_requires='>=3.6',  # Minimum version requirement of the Python interpreter
)