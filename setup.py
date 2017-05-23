from setuptools import setup, find_packages

setup(
	name = "COSplay",
	version = "",
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
		'console_scripts' : ['COSplay = COSplay.cli:main']
	},
	scripts = ['scripts/grant_permissions_for_pyboard']
	)
