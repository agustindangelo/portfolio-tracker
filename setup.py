from setuptools import setup
setup(
  name = 'portfolio-tracker',
  version = '0.1.0',
  packages = ['portfolio-tracker'],
  entry_points = {
      'console_scripts': [
          'pycli = pycli.__main__:main'
    ]
})