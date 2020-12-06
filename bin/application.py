import json
import os
import threading
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox, ttk

from bin import methods, threads


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.workingDirectory = os.getcwd()
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.closeEvent)
        self.mainWindow()
        self.pack()
    
    def updateStatus(self, color : str):
        if color == "green":
            self.master.iconphoto(True, tk.PhotoImage(file='./rsc/green-icon.png'))
        elif color == "red":
            self.master.iconphoto(True, tk.PhotoImage(file='./rsc/red-icon.png'))
        elif color == "yellow":
            self.master.iconphoto(True, tk.PhotoImage(file='./rsc/yellow-icon.png'))
        else:
            self.master.iconphoto(True, tk.PhotoImage(file='./rsc/grey-icon.png'))
    
    def update(self, bypass=False):
        updateThread = threading.Thread(target=threads.update, args=[self, bypass])
        updateThread.start()

    def start(self):
        if self.autoUpdate.get():
            updateAndStartThread = threading.Thread(target=threads.updateAndStart, args=[self])
            updateAndStartThread.start()
        else:
            try:
                if not self.Instance.poll() is None:
                    startThread = threading.Thread(target=threads.start, args=[self])
                    startThread.start()
            except:
                startThread = threading.Thread(target=threads.start, args=[self])
                startThread.start()

    def stop(self):
        try:
            self.bypassRestart = True
            self.Instance.terminate()
            self.Instance.terminate()
        except:
            pass
    
    def forceStop(self):
        try:
            self.bypassRestart = True
            self.Instance.kill()
            self.Instance.kill()
        except:
            pass
    
    def forceRestart(self):
        try:
            if not self.Instance.poll() is None:
                self.start()
            else:
                self.bypassRestart = True
                self.Instance.kill()
                self.Instance.kill()
                self.start()
        except:
            self.start()
    
    def getCommand(self):
        dir = fd.askopenfilename()
        if dir == "":
            return
        config = json.load(open("usr/config.json"))
        config["command"] = [f"{os.path.normpath(dir)}"]
        json.dump(config, open("usr/config.json", "w"), indent=2)
        self.configLabelEntryVar.set(f"{json.load(open('usr/config.json'))['command']}")

    def setCommand(self, *args):
        list = self.configLabelEntryVar.get().strip('][').split(', ')
        for i in range(len(list)):
            list[i] = os.path.normpath(list[i].strip("'"))
        methods.updateConfigVar("command", list)
    
    def getUpdateCommand(self):
        dir = fd.askopenfilename()
        if dir == "":
            return
        config = json.load(open("usr/config.json"))
        config["update command"] = [f"{os.path.normpath(dir)}"]
        json.dump(config, open("usr/config.json", "w"), indent=2)
        self.updateLabelEntryVar.set(f"{json.load(open('usr/config.json'))['update command']}")

    def removeBackupFolder(self, label, dir):
        config = json.load(open("usr/config.json"))
        config["directories to backup"].remove(os.path.normpath(dir))
        json.dump(config, open("usr/config.json", "w"), indent=2)
        label.destroy()

    def setUpdateCommand(self, *args):
        list = self.updateLabelEntryVar.get().strip('][').split(', ')
        for i in range(len(list)):
            list[i] = os.path.normpath(list[i].strip("'"))
        methods.updateConfigVar("update command", list)
    
    def addFolderToBackup(self):
        dir = fd.askdirectory()
        if dir == "":
            return
        config = json.load(open("usr/config.json"))
        config["directories to backup"].append(os.path.normpath(dir))
        json.dump(config, open("usr/config.json", "w"), indent=2)
        backupLabel = tk.Label(self.configBackupLabelFrame, text=f"{os.path.normpath(dir)}")
        backupLabel.pack(fill=tk.X)
        backupLabelButtonRemove = tk.Button(backupLabel, text="Remove this dir", command= lambda: self.removeBackupFolder(backupLabel, dir))
        backupLabelButtonRemove.pack(side=tk.RIGHT)
    
    def loadBackupFolderLabel(self, dir):
        backupLabel = tk.Label(self.configBackupLabelFrame, text=f"{os.path.normpath(dir)}")
        backupLabel.pack(fill=tk.X)
        backupLabelButtonRemove = tk.Button(backupLabel, text="Remove this dir", command= lambda: self.removeBackupFolder(backupLabel, dir))
        backupLabelButtonRemove.pack(side=tk.RIGHT)

    ###### Application Windows ######

    def mainWindow(self):
        self.master.title("InstanceManager")
        self.updateStatus("grey")
        self.master.geometry("700x600")

        mainWindowFrame = tk.Frame(self.master)
        mainWindowFrame.pack(fill=tk.BOTH, expand=True)

        configLabelFrame = tk.LabelFrame(mainWindowFrame, text = "Config")
        configLabelFrame.pack(fill=tk.X, expand=True)

        configRunLabelFrame = tk.LabelFrame(configLabelFrame, text="Run Command")
        configRunLabelFrame.pack(fill=tk.X)

        self.configLabelText = tk.Label(configRunLabelFrame)
        self.configLabelText.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.configLabelEntryVar = tk.StringVar()
        self.configLabelEntryVar.set(f"{json.load(open('usr/config.json'))['command']}")
        self.configLabelEntryVar.trace_add("write", self.setCommand)
        configLabelEntry = tk.Entry(self.configLabelText, textvariable=self.configLabelEntryVar)
        configLabelEntry.pack(fill=tk.X)

        configButtonOpenCommand = tk.Button(configRunLabelFrame, text="Select .bat to run", command=self.getCommand)
        configButtonOpenCommand.pack(side=tk.RIGHT)

        configLabelOpenCommand = tk.Label(configRunLabelFrame, text="or")
        configLabelOpenCommand.pack(side=tk.RIGHT)

        configUpdateLabelFrame = tk.LabelFrame(configLabelFrame, text="Update Command")
        configUpdateLabelFrame.pack(fill=tk.X)

        self.updateLabel = tk.Label(configUpdateLabelFrame)
        self.updateLabel.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.updateLabelEntryVar = tk.StringVar()
        self.updateLabelEntryVar.set(f"{json.load(open('usr/config.json'))['update command']}")
        self.updateLabelEntryVar.trace_add("write", self.setUpdateCommand)
        updateLabelEntry = tk.Entry(self.updateLabel, textvariable=self.updateLabelEntryVar)
        updateLabelEntry.pack(fill=tk.X)

        updateButtonOpenCommand = tk.Button(configUpdateLabelFrame, text="Select .bat to run", command=self.getUpdateCommand)
        updateButtonOpenCommand.pack(side=tk.RIGHT)

        updateLabelOpenCommand = tk.Label(configUpdateLabelFrame, text="or")
        updateLabelOpenCommand.pack(side=tk.RIGHT)

        self.configBackupLabelFrame = tk.LabelFrame(configLabelFrame, text="Folder to Backup")
        self.configBackupLabelFrame.pack(fill=tk.X)

        configButtonOpenCommand = tk.Button(self.configBackupLabelFrame, text="Add directory to backup", command=self.addFolderToBackup)
        configButtonOpenCommand.pack(fill=tk.X)
        
        backupDirs = json.load(open("usr/config.json"))["directories to backup"]
        for dir in backupDirs:
            self.loadBackupFolderLabel(os.path.normpath(dir))

        executeLabelFrame = tk.LabelFrame(mainWindowFrame, text = "Execute")
        executeLabelFrame.pack(fill=tk.X, expand=True)

        executeUpdateLabelFrame = tk.LabelFrame(executeLabelFrame, text="Update")
        executeUpdateLabelFrame.pack(fill=tk.X)

        executeUpdateLabelTop = tk.Label(executeUpdateLabelFrame)
        executeUpdateLabelTop.pack(fill=tk.X)

        executeUpdateLabelTopText = tk.Label(executeUpdateLabelTop, text="Update Every Day at ")
        executeUpdateLabelTopText.pack(side=tk.LEFT)

        hours = list(range(24))
        self.hoursVar = tk.StringVar()
        self.hoursVar.set(json.load(open('usr/config.json'))['scheduledUpdateTimeHours'])
        self.hoursVar.trace_add("write", lambda *args: methods.updateConfigVar("scheduledUpdateTimeHours", self.hoursVar.get()))
        executeUpdateLabelTopDropDownHours = ttk.Combobox(executeUpdateLabelTop, values=hours, width=3, textvariable=self.hoursVar)
        executeUpdateLabelTopDropDownHours.pack(side=tk.LEFT)

        executeUpdateLabelTopCollumn = tk.Label(executeUpdateLabelTop, text=":")
        executeUpdateLabelTopCollumn.pack(side=tk.LEFT)

        minutes = list(range(60))
        self.minutesVar = tk.StringVar()
        self.minutesVar.set(json.load(open('usr/config.json'))['scheduledUpdateTimeMinutes'])
        self.minutesVar.trace_add("write", lambda *args: methods.updateConfigVar("scheduledUpdateTimeMinutes", self.minutesVar.get()))
        executeUpdateLabelTopDropDownMinutes = ttk.Combobox(executeUpdateLabelTop, values=minutes, width=3, textvariable=self.minutesVar)
        executeUpdateLabelTopDropDownMinutes.pack(side=tk.LEFT)

        executeUpdateLabelTopDot = tk.Label(executeUpdateLabelTop, text=". ")
        executeUpdateLabelTopDot.pack(side=tk.LEFT)

        self.scheduledUpdate = tk.BooleanVar()
        self.scheduledUpdate.set(json.load(open('usr/config.json'))['scheduledUpdate'])
        self.executeCheckbuttonScheduledUpdate = tk.Checkbutton(executeUpdateLabelTop, text ="Activate Scheduled Update?", variable=self.scheduledUpdate, onvalue=True, offvalue=False, command=lambda: methods.updateConfigVar("scheduledUpdate", self.scheduledUpdate.get()))
        self.executeCheckbuttonScheduledUpdate.pack(side=tk.LEFT)

        executeUpdateButtonBackup = tk.Button(executeUpdateLabelTop, text="Load Backup", command=lambda:methods.loadBackupFolders(self))
        executeUpdateButtonBackup.pack(side=tk.RIGHT)

        executeUpdateButtonBackup = tk.Button(executeUpdateLabelTop, text="Run Update Command", command=lambda:methods.performUpdate(self))
        executeUpdateButtonBackup.pack(side=tk.RIGHT)

        executeUpdateButtonBackup = tk.Button(executeUpdateLabelTop, text="Backup", command=lambda:methods.backupFolders(self))
        executeUpdateButtonBackup.pack(side=tk.RIGHT)

        executeUpdateLabelBottom = tk.Label(executeUpdateLabelFrame)
        executeUpdateLabelBottom.pack(fill=tk.X)

        executeUpdateButtonBackup = tk.Button(executeUpdateLabelBottom, text="Update", command=lambda:self.update(True))
        executeUpdateButtonBackup.pack(fill=tk.X)

        executeRunLabelFrame = tk.LabelFrame(executeLabelFrame, text="Run")
        executeRunLabelFrame.pack(fill=tk.X)

        executeRunLabelTop = tk.Label(executeRunLabelFrame)
        executeRunLabelTop.pack(fill=tk.X)

        self.autoRestart = tk.BooleanVar()
        self.autoRestart.set(json.load(open('usr/config.json'))['autoRestart'])
        self.commandCheckbuttonRestart = tk.Checkbutton(executeRunLabelTop, text ="Auto Restart?", variable=self.autoRestart, onvalue=True, offvalue=False, command=lambda: methods.updateConfigVar("autoRestart", self.autoRestart.get()))
        self.commandCheckbuttonRestart.pack(side=tk.LEFT)

        self.autoUpdate = tk.BooleanVar()
        self.autoUpdate.set(json.load(open('usr/config.json'))['autoUpdate'])
        self.commandCheckbuttonUpdate = tk.Checkbutton(executeRunLabelTop, text ="Update on Start?", variable=self.autoUpdate, onvalue=True, offvalue=False, command=lambda: methods.updateConfigVar("autoUpdate", self.autoUpdate.get()))
        self.commandCheckbuttonUpdate.pack(side=tk.LEFT)
        
        self.bypassRestart = False
        executeRunButtonForceRestart = tk.Button(executeRunLabelTop, text="Force Restart", command=self.forceRestart)
        executeRunButtonForceRestart.pack(side=tk.RIGHT)

        executeRunButtonForceStop = tk.Button(executeRunLabelTop, text="Force Stop", command=self.forceStop)
        executeRunButtonForceStop.pack(side=tk.RIGHT)

        executeRunLabelBottom = tk.Label(executeRunLabelFrame)
        executeRunLabelBottom.pack(fill=tk.X)

        self.commandButtonToggle = tk.Button(executeRunLabelBottom, text ="Start", command=self.start)
        self.commandButtonToggle.pack(fill=tk.X)

        consoleLabelFrame = tk.LabelFrame(mainWindowFrame, text = "Output")
        consoleLabelFrame.pack(fill=tk.BOTH, expand=True)

        self.consoleText = tk.Text(consoleLabelFrame)
        self.consoleText.pack(fill=tk.BOTH, expand=True)

    def closeEvent(self):
        try:
            if self.Instance.poll() is None:
                if messagebox.askokcancel("Quit", "The Instance is still running.\nIt will continue running in the Backround.\nExit anyway?"):
                    self.stop()
                else:
                    return
        except:
            pass
        self.master.destroy()

def run():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
