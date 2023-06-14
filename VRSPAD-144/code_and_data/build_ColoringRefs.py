# from numpy.distutils.core import setup, Extension

# module1 = Extension('ColoringRefs',
#                     sources = ['ColoringRefs.c'])

# setup (name = 'ColoringRefs',
#        version = '1.0',
#        description = 'This is a demo package',
#        ext_modules = [module1])

from setuptools import setup, Extension

ext_modules = [
    Extension('ColoringRefs', sources = ['ColoringRefs.c'], include_dirs=['C:/Users/William/AppData/Local/Programs/Python/Python310/Lib/site-packages/numpy/core/include']),
]

setup(
    name = 'ColoringRefs',
    ext_modules = ext_modules
)