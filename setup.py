from setuptools import setup, find_packages

setup(
    name='geeksw',
    version='0.1',
    description='The geeks analysis framework',
    long_description='A cmssw inspired analysis framework in Python.',
    url='http://github.com/guitargeek/geeksw',
    author='Jonas Rembser',
    author_email='jonas.rembser@cern.ch',
    license='MIT',
    packages=find_packages(),
    entry_points = {
        'console_scripts': ['geekRun=geeksw.geekRun:__main__'],
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=[
   'numpy',
   'argparse',
    ]
)
