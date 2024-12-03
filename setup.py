from setuptools import setup, find_packages

setup(
    name='Bad-Comment-Detector',
    version='0.1.0-alpha',
    author='Scrappyz',
    author_email='ghostmic3000@gmail.com',
    description='A bad comment detector using both rule-based and AI methods.',
    url='https://github.com/Scrappyz/Bad-Comment-Detector',
    license='MIT',  # Choose an appropriate license
    install_requires=[
        'pyahocorasick>=2.1.0',
        'contractions>=0.1.73',
        'spacy>=3.7.6',
        'thefuzz>=0.22.0',
        'fastapi>=0.115.5'
        # Add more dependencies as required
    ],
    packages=find_packages(include=['detector'])
)
