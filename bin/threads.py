import datetime
import json
import subprocess
import threading
import time
import tkinter as tk

from bin import methods

# internal threads

def instanceWatcher(self):
    try:
        self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: Process started.\n")
        self.consoleText.see(tk.END)
        now = datetime.datetime.now()
        nextUpdate = datetime.datetime(int(now.strftime("%Y")),int(now.strftime("%m")), int(now.strftime("%d")), hour=int(self.hoursVar.get()), minute=int(self.minutesVar.get()))
        if nextUpdate < now:
            nextUpdate = nextUpdate + datetime.timedelta(days=1)
        self.updateStatus("green")
        while self.Instance.poll() is None:
            self.commandButtonToggle.configure(text="Stop", command=self.stop)
            if nextUpdate < datetime.datetime.now():
                if self.scheduledUpdate.get():
                    updateAndStartThread = threading.Thread(target=updateAndStart, args=[self])
                    updateAndStartThread.start()
                    break
                else:
                    nextUpdate = datetime.datetime(int(now.strftime("%Y")),int(now.strftime("%m")), int(now.strftime("%d")+1), hour=int(self.hoursVar.get()), minute=int(self.minutesVar.get()))
            else:
                now = datetime.datetime.now()
                nextUpdate = datetime.datetime(int(now.strftime("%Y")),int(now.strftime("%m")), int(now.strftime("%d")), hour=int(self.hoursVar.get()), minute=int(self.minutesVar.get()))
                if nextUpdate < now:
                    nextUpdate = nextUpdate + datetime.timedelta(days=1)
            time.sleep(0.5)
        if self.autoRestart.get() and not self.bypassRestart:
            self.updateStatus("yellow")
            self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: Process stopped.\n")
            self.consoleText.see(tk.END)
            self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: Restarting the Process after it terminated.\n")
            self.consoleText.see(tk.END)
            self.start()
            exit()
        else:
            self.bypassRestart = False
            self.updateStatus("yellow")
            self.consoleText.insert(tk.END, f"[{datetime.datetime.now()}]: Process stopped.\n")
            self.consoleText.see(tk.END)
            self.commandButtonToggle.configure(text="Start", command=self.start)
    except Exception as e:
        print(e)

def updateConsole(self):
    try:
        for line in iter(self.Instance.stdout.readline, ''):
            if not self.Instance.poll() is None:
                break
            self.consoleText.insert(tk.END, line.decode("utf-8"))
            self.consoleText.see(tk.END)
    except:
        pass

# external threads

def start(self):
    self.Instance = subprocess.Popen(json.load(open('usr/config.json'))['command'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    watcherThread = threading.Thread(target=instanceWatcher, args=[self])
    watcherThread.start()
    consoleThread = threading.Thread(target=updateConsole, args=[self])
    consoleThread.start()

def update(self, bypass=False):
    self.bypassRestart = bypass
    updateThread = threading.Thread(target=methods.update, args=[self])
    updateThread.start()

def updateAndStart(self):
    self.bypassRestart = True
    updateThread = threading.Thread(target=methods.update, args=[self])
    updateThread.start()
    updateThread.join()
    startThread = threading.Thread(target=start, args=[self])
    startThread.start()
