from setuptools import setup, find_packages

setup(
	name = "COSplay",
	version = "2.0.dev1",
	author = "Aymanns Florian",
	author_email = "faymanns@student.ethz.ch",
	description = "Stimulus delivery for fMRI experiments.",
	keywords = ["fMRI", "stimulus", "pyboard", "bruker"],
	url = "https://github.com/IBT-FMI/COSplay.git",
	install_requires = [],
	provides = ["cosplay"],
	packages = ["cosplay"],
	include_package_data = True,
	entry_points = {
		'console_scripts' : ['COSplay = cosplay.cli:main']
	},
	scripts = ['scripts/grant_permissions_for_pyboard']
	)
