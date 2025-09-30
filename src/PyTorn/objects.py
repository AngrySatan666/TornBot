import os
import shutil
import subprocess
import random, string
import yaml
import socket
import time
import pwd
import grp

_dir = os.path.dirname(os.path.abspath(__file__))

class User:
    def __init__(self):
        self.root = os.path.join(_dir, 'data', 'user', 'users.json')
