"""Setup tool for this module"""
from numpy.distutils.misc_util import Configuration


def configuration(parent_package='', top_path=None):
    config = Configuration('kbest_assignment', parent_package, top_path)
    config.add_subpackage('lsap')
    config.make_config_py()
    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
