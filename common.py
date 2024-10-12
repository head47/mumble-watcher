import os
from pathlib import Path

CONFIG_FILE = (Path(os.path.dirname(os.path.realpath(__file__))) / "config.json").resolve()
CERT_FILE = (Path(os.path.dirname(os.path.realpath(__file__))) / "cert.pem").resolve()
KEY_FILE = (Path(os.path.dirname(os.path.realpath(__file__))) / "key.pem").resolve()
