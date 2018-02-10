from setuptools import setup, find_packages

setup(
    name="Transnet",
    version="0.1",
    packages=find_packages(),

    install_requires=[
        'requests',
        'matplotlib'
    ],
    entry_points={
        'console_scripts': [
            'save_csv = transnet.get_data:save_csv',
        ]
    },

    # metadata for upload to PyPI
    author="Patrick Emmerich",
    author_email="mail@patrick-emmerich.de",
    description="",
    license="",
    keywords="",

)
