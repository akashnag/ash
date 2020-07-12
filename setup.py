from setuptools import setup, find_packages
setup(
	name="ash",
    version="0.1.0-dev",
	description='A modern terminal text-editor',
	classifiers=[
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 3.8',
	'Topic :: Text Editor',
	],
	keywords='terminal text-editor',
	url='https://github.com/akashnag/ash',
	author='Akash Nag',
	author_email='nag.akash.cs@gmail.com',
	license='MIT',    
    packages=['ash', 'ash.core', 'ash.utils', 'ash.formatting', 'ash.gui'],
    package_dir = { 'ash': 'src/ash', 'ash.core': 'src/ash/core', 'ash.utils': 'src/ash/utils', 'ash.formatting': 'src/ash/formatting', 'ash.gui': 'src/ash/gui'},
    entry_points = {'console_scripts': ['ash = ash.ash_main:run']},
    data_files=[('docs', ['README.md', 'KEYBINDINGS.md', 'LICENSE.md']),
    			('assets', ['assets/banner.png', 'assets/ash-default.png', 'assets/ss1.png', 'assets/ss2.png', 'assets/ss3.png', 'assets/ss4.png', 'assets/ss5.png'])]
)
