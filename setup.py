from setuptools import setup

setup(name='minerrestarter',
      version='0.0.0',
      description='Restarts your miner (stak-xmr)',
      url='http://github.com/jav/minerrestarter',
      author='Javier Ubillos',
      author_email='javier@ubillos.orgcom',
      license='GPL3',
      packages=['minerrestarter'],
      install_requires=[
          'mock',
      ],
      zip_safe=False)
