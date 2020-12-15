import os
import subprocess
import threading


class Instance():
    """
    docstring
    """
    def __init__(self, instanceConfig):
        self.workingDirectory = os.getcwd()
        self.instanceConfig = instanceConfig
        self.isFirstRun = True
    
    pass
