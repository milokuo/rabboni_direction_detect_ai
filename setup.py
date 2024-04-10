# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rabboni_multi_python_sdk']

package_data = \
{'': ['*']}

install_requires = \
['bleak==0.20.2']

setup_kwargs = {
    'name': 'rabboni-multi-python-sdk',
    'version': '1.1.0',
    'description': '',
    'long_description': '',
    'author': 'NCTUTWT Lab',
    'author_email': 'nctutwtlab@nctu.edu.tw',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': {"":"src"},
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
