# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

from setuptools import setup, find_packages

# read the contents of the README file
from os import path
from urllib.request import urlopen

with urlopen(url="https://github.com/akashnag/ash/raw/master/PYPI_README.md") as f:
	long_description = f.read().decode("utf-8")

setup(
	name="ash-editor",
    version="0.1.0-dev14",
	description='A modern terminal text-editor',
	classifiers=[
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 3.8',
	'Topic :: Text Editors',
	],
	long_description=long_description,
	long_description_content_type='text/markdown',
	keywords='terminal text-editor',
	url='https://akashnag.github.io/ash',
	author='Akash Nag',
	author_email='nag.akash.cs@gmail.com',
	license='MIT',
	install_requires=[
		'chardet>=3.0.4',
		'Pygments>=2.7.4',
		'pyperclip>=1.8.0',
		'Send2Trash>=1.5.0',
		'GitPython>=3.1.7',
		'Cython>=0.29.21'
	],
    packages=['ash', 'ash.core', 'ash.utils', 'ash.formatting', 'ash.gui'],
    package_dir = { 'ash': 'src/ash', 'ash.core': 'src/ash/core', 'ash.utils': 'src/ash/utils', 'ash.formatting': 'src/ash/formatting', 'ash.gui': 'src/ash/gui'},
	package_data={'ash.core':['screen.pyx']},
	include_package_data=True,
    entry_points = {'console_scripts': ['ash = ash.ash_main:run']},
    data_files=[('docs', ['README.md', 'KEYBINDINGS.md', 'LICENSE.md', 'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md']),
    			('assets', [
								'assets/banner.png', 'assets/ash-default.png', 'assets/bmc-button.png',
								'assets/ss1.png', 'assets/ss2.png', 'assets/ss3.png', 'assets/ss4.png', 
								'assets/ss5.png', 'assets/ss6.png', 'assets/ss7.png', 'assets/ss8.png',
								'assets/ss9.png', 'assets/ss10.png', 'assets/ss11.png', 'assets/ss12.png',
								'assets/ss13.png', 'assets/ss14.png', 'assets/ss15.png', 'assets/ss16.png',
								'assets/ss17.png', 'assets/ss18.png', 'assets/ss19.png', 'assets/ss20.png'
							]
				)]
)