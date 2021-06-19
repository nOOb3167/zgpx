from setuptools import setup
from setuptools import find_packages

setup(name='zgpx', version='1.0', description='', author='', author_email='', url='',
    packages = find_packages(where = 'src'),
    package_dir = {'' : 'src'},
    include_package_data = True,
    setup_requires = ['setuptools_scm'],
    use_scm_version = True
)
