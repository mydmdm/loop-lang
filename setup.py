from setuptools import setup, find_packages
setup(
    name = "loo",
    version = "0.1",
    packages = ['loo'],
    package_dir={'': 'src'},
    install_requires = ['anytree'],
)