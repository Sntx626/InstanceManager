import datetime
import json
import os
import shutil
import subprocess
import threading
import tkinter as tk

from bin import threads


def updateConfigVar(dictKey : str, var):
        config = json.load(open('usr/config.json'))
        config[dictKey] = var
        json.dump(config, open("usr/config.json", "w"), indent=2)

def backupFolders(self):
    self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: Backing up folders...!\n")
    config = json.load(open('usr/config.json'))
    backupFolderName = str(datetime.datetime.now().strftime("%d-%b-%Y_%Hh%Mm%Ss"))
    backupFolderPath = f"{self.workingDirectory}\\usr\\backups\\{backupFolderName}"
    try:
        os.mkdir(backupFolderPath)
        metadata = {}
        for folder in config["directories to backup"]:
            metadata[str(os.path.basename(folder))] = os.path.normpath(folder)
            shutil.copytree(os.path.normpath(folder), os.path.join(backupFolderPath, str(os.path.basename(folder))))
        config["lastBackupOk"] = True
        config["latestBackup"] = os.path.normpath(backupFolderPath)
        json.dump(config, open("usr/config.json", "w"), indent=2)
        json.dump(metadata, open(f"{os.path.join(backupFolderPath, 'metadata.json')}", "w"), indent=2)
        self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: Backed up folders.\n")
        self.consoleText.see(tk.END)
    except Exception as e:
        self.updateStatus("red")
        self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: There was an error backing up your folders.\n{e}\n")
        self.consoleText.see(tk.END)
        config["lastBackupOk"] = False
        json.dump(config, open("usr/config.json", "w"), indent=2)
    
def performUpdate(self, join=False):
    config = json.load(open('usr/config.json'))
    if not config["lastBackupOk"]:
        self.updateStatus("red")
        self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: Could not update. Reason: The last Backup couldnot be confirmed!\n")
        self.consoleText.see(tk.END)
    else:
        self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: Initiating Update...\n")
        self.consoleText.see(tk.END)
        try:
            if self.Instance.poll() is None:
                self.stop()
        except:
            pass
        self.bypassRestart = True
        self.Instance = subprocess.Popen(json.load(open('usr/config.json'))['update command'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        watcherThread = threading.Thread(target=threads.instanceWatcher, args=[self])
        watcherThread.start()
        consoleThread = threading.Thread(target=threads.updateConsole, args=[self])
        consoleThread.start()
        if join:
            watcherThread.join()
    
def loadBackupFolders(self):
    self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: Restoring files from Backup...\n")
    self.consoleText.see(tk.END)
    config = json.load(open('usr/config.json'))
    if not config["lastBackupOk"]:
        self.updateStatus("red")
        self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: Could not update. Reason: The last Backup couldnot be confirmed!\n")
        self.consoleText.see(tk.END)
    else:
        metadata = json.load(open(f"{os.path.join(config['latestBackup'], 'metadata.json')}"))
        for folder in metadata:
            shutil.copytree(os.path.join(config['latestBackup'], folder), os.path.normpath(metadata[folder]), dirs_exist_ok=True)
        self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: Restored all data from Backup.!\n")
        self.consoleText.see(tk.END)

def update(self):
    backupFolders(self)
    performUpdate(self, True)
    loadBackupFolders(self)
