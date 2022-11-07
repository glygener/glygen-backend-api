import os,sys
from optparse import OptionParser
from setuptools import find_packages, setup


def main():

    mod = sys.argv[-2]
    ver = sys.argv[-1]
    sys.argv = sys.argv[0:-2]

    setup(
        name=mod,
        version=ver,
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'flask',
        ],
    )



if __name__ == '__main__':
    main()

