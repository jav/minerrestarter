from setuptools import setup
import py2exe

setup(name='minerrestarter',
      version='0.0.0',
      description='Restarts your miner (stak-xmr)',
      url='http://github.com/jav/minerrestarter',
      author='Javier Ubillos',
      author_email='javier@ubillos.org',
      license='GPL3',
      options = {"py2exe": {"packages": ["encodings"]}},
      uac_execution_info= "requireAdministrator",
      install_requires=[
          'psutil'
      ],
      tests_requires=[
          'mock',
          'nose'
      ],
      console=['minerrestarter.py'],
      zip_safe=False)
