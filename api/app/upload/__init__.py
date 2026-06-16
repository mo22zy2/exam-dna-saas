import logging
import os
import sys

logging.getLogger(__name__).addHandler(logging.NullHandler())

# Ensure libmagic DLL can be found on Windows (python-magic-bin installs it to magic/libmagic/)
if sys.platform == "win32":
    import site
    for _p in site.getsitepackages():
        _lib_dir = os.path.join(_p, "magic", "libmagic")
        if os.path.isfile(os.path.join(_lib_dir, "libmagic.dll")):
            os.environ["PATH"] = _lib_dir + os.pathsep + os.environ.get("PATH", "")
            break