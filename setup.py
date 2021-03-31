from setuptools import setup

setup(name='waiter',
      version='0.1',
      description='ML deployment',
      packages=['waiter'],
      zip_safe=False,
      entry_points='''
        [console_scripts]
        waiter=waiter.waiter_runner:cli
      ''')
