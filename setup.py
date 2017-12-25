from setuptools import setup
import py2exe

setup(name='minerrestarter',
      version='0.0.0',
      description='Restarts your miner (stak-xmr)',
      url='http://github.com/jav/minerrestarter',
      author='Javier Ubillos',
      author_email='javier@ubillos.org',
      license='GPL3',
      packages=['minerrestarter'],
      install_requires=[
          'mock',
      ],
      console=['minerrestarter'],
      zip_safe=False)
