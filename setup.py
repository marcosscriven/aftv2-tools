from distutils.core import setup
import py2exe

setup(console=["root_aftv2.py"],
      options={"py2exe": {"packages": ["encodings"]}},
)
