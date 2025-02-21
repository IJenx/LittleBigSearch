import tkinter           as tk
import os, shutil,threading, ttkthemes
from   genericpath       import exists
from   tkinter           import Button, Frame, Widget, ttk
from   tkinter.constants import ANCHOR, VERTICAL
from   functools         import partial
from   PIL               import Image, ImageTk
from   SFOParser         import LevelParser, ParserReturns
from   Settings.Options  import Options
import helpers.Utilities as     helpers
from   SavedLevels       import SavedLevels
from   os                import path

class LittleBigSearchGUI():
    def __init__(self, master: tk.Tk, matchedLevels = []) -> None:
        
        self.archivePath = ''
        self.RPCS3Path   = ''
        self.stopSearchAnimation = False

        self.scrollerCanvas  = tk.Canvas()
        self.levelScroller   = Frame()
        
        self.levelParser     = LevelParser()
        self.matchedLevels   = matchedLevels
        
        self.settings = 0
        self.isDuplicatesAllowed = False
        self.includeDescription  = True

        self.savedLevels = 0
        
        
        self.master = master
        self.master.title("LittleBigSearch by @SackBiscuit v1.1.1")
        self.master.iconbitmap(default="images/icon.ico")
        self.master.configure(bg= helpers.GlobalVars.BGColorDark)

        ttkthemes.themed_style.ThemedStyle(theme="adapta")

        # _ UI _______________________

        self.canvas = tk.Canvas(master,
                                height = 150,
                                width  = 900 ,
                                bg=helpers.GlobalVars.BGColorLight, 
                                borderwidth=0,
                                highlightthickness=0)

        self.canvas.grid(columnspan=3, sticky="we")

        self.logo = Image.open('images/LBSearch.png')

        self.logoResize = self.logo.resize(( 500, 112 ))
        self.logo = ImageTk.PhotoImage(image= self.logoResize)

        self.logoLabel = tk.Label(image= self.logo, bg= helpers.GlobalVars.BGColorLight)
        self.logoLabel.image = self.logo
        self.logoLabel.grid(column=1, row=0)
        
        # ____ 
        
        self.settingButton = tk.Button(text             = "Settings",
                                       command          = lambda: self.openSettings(),
                                       bg               = helpers.GlobalVars.logoBlue, 
                                       activebackground = helpers.GlobalVars.logoBlue,
                                       fg               = "white",
                                       height           = 1, 
                                       width            = 13,
                                       bd               = 0)
        self.settingButton.grid(columnspan=3, column=0, row=1, pady=10, padx= (0,105))
        # ____
        self.SavedLevelsButton = tk.Button(text            = "Saved Levels",
                                          command          = lambda: self.openSavedLevels(),
                                          bg               = helpers.GlobalVars.logoBlue, 
                                          activebackground = helpers.GlobalVars.logoBlue,
                                          fg               = "white", 
                                          height           = 1,
                                          width            = 13,
                                          bd               = 0)
        self.SavedLevelsButton.grid(columnspan=3, column=0, row=1, pady=10, padx= (105,0))
        # ____ 
        searchLabel = tk.Label(text  = "The Search will look for level name, creator ID or any keyword in the level Description",
                               bg    = helpers.GlobalVars.BGColorDark,
                               fg    = "White",
                               font  = ('Helvatical bold',10))
        searchLabel.grid(columnspan=3, column=0, row=2)
        searchTextField = tk.Entry(bd= 0, font=15, bg="black", fg="white")
        searchTextField.grid(columnspan=3, row=3, column=0, ipadx= 250)

        searchButton = tk.Button(text             = "Search",
                                command           = lambda: threading.Thread(target= self.LBSsearch, args= (searchTextField.get(), self.archivePath)).start(),
                                bd                = 0,
                                bg                = helpers.GlobalVars.logoBlue, 
                                fg                = "white", 
                                activebackground  = helpers.GlobalVars.logoBlue,
                                height            = 1,
                                width             = 20)
        searchButton.grid(column=1, row=4, pady=10)


        self.errorText  = tk.StringVar()
        self.errorLabel = Button(textvariable    = self.errorText,
                                bd               = 0,
                                bg               = helpers.GlobalVars.BGColorDark,
                                activebackground = helpers.GlobalVars.logoBlue)
        self.errorText.set("")
        self.errorLabel.grid(column=1, row=5, ipadx=30)
        
        self.fetchSettingsFromJSON()
        
    # settings __________________________________________________________________________________________________________________________________________
    
    def fetchSettingCallBack(self, archive, RPCS3, dupsStatus, includeDescription):
        self.archivePath = archive
        self.RPCS3Path   = RPCS3
        self.isDuplicatesAllowed = dupsStatus
        self.includeDescription = includeDescription
    
    def fetchSettingsFromJSON(self):
        if path.exists("SavedSettings.json"):
            Options.getSettingsFromJSON(self.fetchSettingCallBack)
        else:
            print("No saved settings.")

    # search method _____________________________________________________________________________________________________________________________________

    def LBSsearch(self, term, path):
        if self.RPCS3Path.__contains__("/") == False:
            self.sendError("Please select an RPCS3 savedata folder from settings", "red")
            return

        self.sendError("Searching...")
        # this event will be called from background thread to use the main thread.
        self.master.bind("<<event1>>", self.showResult)
        self.levelParser.search(self.searchCallBack, term, path, includeDescription= self.includeDescription)
    
    def searchCallBack(self, response):
        if response == ParserReturns.noResult:
            self.sendError("No result", "red")

        elif response == ParserReturns.noPath:
            self.sendError("Please select a levels directory from the settings", "red")
        
        elif response == ParserReturns.wrongPath:
            self.sendError("Couldn't find the level archive directory", "red")
        
        else:
            self.matchedLevels = response
            # Calls showResult on the main thread.
            self.master.event_generate("<<event1>>")

    # Settings and settings Protocols ____________________________________________________________________________________________________________________

    #PROTOCOLS________________________
    def toggleDuplicatesProtocol(self):
        self.isDuplicatesAllowed = True if self.isDuplicatesAllowed == False else False

    def toggleIncludeDescriptionProtocol(self):
        self.includeDescription = True if self.includeDescription == False else False

    def settingsClosedProtocol(self):
        self.settings = 0

    def savedLevelClosedProtocol(self):
        self.savedLevels = 0

    def archivePathProtocol(self, path):
        self.archivePath = path
    
    def RPCS3PathProtocol(self, path):
        self.RPCS3Path = path

    # Saved levels _______________________________________________________________________________________________________________________________________

    def openSavedLevels(self):
        if self.RPCS3Path == '':
            self.sendError("Please select an RPCS3 savedata folder", "red")
            return

        if self.savedLevels == 0:
            self.savedLevels = SavedLevels(master        = self.master, 
                                           RPCS3Path     = self.RPCS3Path,
                                           closeDelegate = self.savedLevelClosedProtocol)
        else:
            self.savedLevels.window.lift()

    #_________________________________

    def openSettings(self):
        if self.settings == 0:
            self.settings = Options(closeDelegate              = self.settingsClosedProtocol,
                                    duplicatesDelegate         = self.toggleDuplicatesProtocol,
                                    includeDescriptionDelegate = self.toggleIncludeDescriptionProtocol,
                                    archiveDelegate            = self.archivePathProtocol,
                                    RPCS3Delegate              = self.RPCS3PathProtocol,
                                    currentArchivePath         = self.archivePath,
                                    currentRPCS3Path           = self.RPCS3Path,
                                    includeDescriptionStatus   = self.includeDescription,  
                                    duplicatesStatus           = self.isDuplicatesAllowed,
                                    master=self.master)
        else: 
            self.settings.window.lift()


    # Helper methods _____________________________________________________________________________________________________________________________________

    def moveFolder(self, source):
        destination = self.RPCS3Path
        destDir = os.path.join(destination,os.path.basename(source))
        if exists(destDir) == False:
            self.sendError("Level folder was added to RPCS3 savedata", "green")
            shutil.copytree(source, destDir)
        else:
            self.sendError("Level folder was removed from RPCS3 savedata")
            shutil.rmtree(destDir)
        
        # refresh Saved levels automatically
        if self.savedLevels != 0:
            self.savedLevels.refresh()

    def _bound_to_mousewheel(self, event):
        self.scrollerCanvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _unbound_to_mousewheel(self, event):
        self.scrollerCanvas.unbind_all("<MouseWheel>")

    def _on_mouse_wheel(self, event):
        self.sendError("")
        self.scrollerCanvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    def sendError(self, message = "", color = "white"):
        self.errorLabel.configure(fg=color)
        self.errorText.set(message)        

    # builds result scroller view _______________________________________________________________________________________________________________________________
    
    def showResult(self, evt):
        self.sendError("")
        # destroy the old scroll view
        self.levelScroller.destroy()
        
        # build new one
        self.mainFrame = Frame(self.master,
                               highlightbackground  = helpers.GlobalVars.BGColorDark,
                               highlightcolor       = helpers.GlobalVars.BGColorDark)

        self.mainFrame.grid(columnspan=3, column=0)

        self.scrollerCanvas = tk.Canvas(self.mainFrame,bg=helpers.GlobalVars.BGColorDark, borderwidth=0, highlightthickness=0)
        self.scrollerCanvas.grid(row=0, column=0, ipadx= 250, ipady=150)
        

        ScrollBar = ttk.Scrollbar(self.mainFrame, orient=VERTICAL, command=self.scrollerCanvas.yview)
        ScrollBar.grid(row=0, column=1, sticky='ns')
        

        self.scrollerCanvas.configure(yscrollcommand=ScrollBar.set, bg=helpers.GlobalVars.BGColorDark)
        self.scrollerCanvas.bind('<Configure>', lambda e: self.scrollerCanvas.configure(scrollregion= self.scrollerCanvas.bbox("all")))
        
        self.scrollerCanvas.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollerCanvas.bind('<Leave>', self._unbound_to_mousewheel)

        scrollerFrame = Frame(self.scrollerCanvas,
                             background          = helpers.GlobalVars.BGColorDark,
                             highlightbackground = helpers.GlobalVars.BGColorDark,
                             highlightcolor      = helpers.GlobalVars.BGColorDark)
        
        self.scrollerCanvas.create_window((0,0), window=scrollerFrame, anchor="nw")
        
        self.levelScroller = self.mainFrame
        
        matchedLevelsWithSettings = self.matchedLevels if self.isDuplicatesAllowed == True else set(self.matchedLevels)
            # Loop and build level cells for the scrollable frame
        for index, level in enumerate(matchedLevelsWithSettings):

            labelText = f'{level.title}'

            levellogo = Image.open(level.image)

            levelImage_resize = levellogo.resize(( 120, 75 ))
            levellogo = ImageTk.PhotoImage(levelImage_resize)

            levelImage_resize = tk.Label(scrollerFrame, image=levellogo, bg=helpers.GlobalVars.BGColorDark)
            levelImage_resize.image = levellogo

            levelPath = f'...{level.path[-80:]}' if len(level.path) > 90 else level.path  
            imagePadx = helpers.Utilities.getPadding(len(levelPath))
            levelImage_resize.grid(row = index, column=0, padx=imagePadx)
            
            levelInfoButton = Button(scrollerFrame,
                                    text             = labelText + "\n" + levelPath, anchor="e",
                                    bd               = 0, 
                                    command          = partial(self.moveFolder, level.path),
                                    cursor           = "hand2",
                                    bg               = helpers.GlobalVars.BGColorDark,
                                    activebackground = helpers.GlobalVars.logoBlue,
                                    fg               = "white",
                                    font             = ('Helvatical bold',10)) 
            levelInfoButton.grid(row = index, column=1)
            

    
root   = tk.Tk()
LBSGUI = LittleBigSearchGUI(master= root)
root.mainloop()

