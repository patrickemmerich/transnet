from setuptools import setup, find_packages

setup(
    name="Transnet",
    version="0.1",
    packages=find_packages(),

    install_requires=[
        'requests',
        'matplotlib',
        'pandas',
        'sklearn',
        'statsmodels'
    ],
    entry_points={
        'console_scripts': [
            'ts_get_load_data = transnet.get_data_from_api:save_csv',
            'ts_get_feiertage = transnet.get_feiertage_from_api:save_csv',
            'ts_predict = transnet.main:predict',
            'ts_evaluate = transnet.main:evaluate',
        ]
    },

    # metadata for upload to PyPI
    author="Patrick Emmerich",
    author_email="mail@patrick-emmerich.de",
    description="",
    license="",
    keywords="",

)
