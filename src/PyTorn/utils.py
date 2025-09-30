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
USERS = ['angry', 'cree', 'testuser']
PUBLIC_FOLDER = '/home/shared/Public'

def GenString(char=None, mult=None):
    """Generate a list of multiple random strings of specified length."""
    """Usage. str = GenString(char=3 mult=4) would give ['aks', 'ojd', 'mjo', 'jsp']"""
    """Usage. to see just one in the list str[2] would gie 'mjo' """
    strings = []
    if not isinstance(mult, int):
        mult = 1
    if not isinstance(char, int):
        char = random.choice(range(8, 16))
    for _ in range(mult):
        result = ''.join(random.choices(string.ascii_letters + string.digits, k=char))
        strings.append(result)
        return strings
