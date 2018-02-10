from setuptools import setup, find_packages

setup(
    name="Transnet",
    version="0.1",
    packages=find_packages(),

    install_requires=[
        'requests',
        'matplotlib',
        'pandas'
    ],
    entry_points={
        'console_scripts': [
            'get_load_data = transnet.get_data:save_csv',
            'plot_data = transnet.plot:plot_data',
        ]
    },

    # metadata for upload to PyPI
    author="Patrick Emmerich",
    author_email="mail@patrick-emmerich.de",
    description="",
    license="",
    keywords="",

)
