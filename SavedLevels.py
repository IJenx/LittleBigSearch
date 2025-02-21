import threading, os,shutil
import tkinter           as tk
from   tkinter           import Frame, ttk, Button
from   tkinter.constants import VERTICAL
from   PIL               import Image, ImageTk
from   functools         import partial
from   SFOParser         import LevelParser, ParserReturns
from   genericpath       import exists
import helpers.Utilities as helpers

class SavedLevels():
    def __init__(self,master, RPCS3Path, closeDelegate, savedLevels = []):
        super().__init__()
        
        #___ Delegates ______________________
        self.closeDelegate  = closeDelegate
        #____________________________________

        self.RPCS3Path = RPCS3Path
        #____________________________________
        self.scrollerCanvas  = tk.Canvas()
        self.scrollerFrame   = Frame()
        self.savedLevels     = savedLevels
        #____________________________________
        self.LevelParser     = LevelParser()
        #____________________________________

        self.window = tk.Toplevel(background= helpers.GlobalVars.BGColorLight)
        self.window.title("RPCS3 savedata levels")
        self.window.transient(master)
        
        self.canvas = tk.Canvas(master= self.window,
                                height = 100,
                                width  = 900 ,
                                bg=helpers.GlobalVars.BGColorLight, 
                                borderwidth=0,
                                highlightthickness=0)
        self.canvas.grid(columnspan=3)

        #____
        self.refreshButton = tk.Button(master        = self.window,
                                    text             ="Refresh",
                                    command          = lambda: self.refresh(),
                                    bg               = helpers.GlobalVars.logoBlue,
                                    activebackground = helpers.GlobalVars.logoBlue,
                                    fg = "white", height=1, width= 13, bd=0)
        self.refreshButton.grid(column=0, row=0)

        self.window.protocol("WM_DELETE_WINDOW", self.onClose)
        threadWork = threading.Thread(target= self.fetchSavedLevels, args= ()) 
        threadWork.start()


    # fetch levels from RPCS3 savedata _____________________________________________________
    
    def fetchSavedLevels(self):
        # this event will be called from background thread to use the main thread.
        self.window.bind("<<event1>>", self.showResult)
        self.LevelParser.fetchLevelsFrom(path=self.RPCS3Path, callBack= self.fetchCallBack)
    
    def fetchCallBack(self, response):
        if response == ParserReturns.noResult:
            # self.sendError("No result", "red")
            # No result = empty levels in RPCS3 so destroy the scroller frame.
            self.scrollerFrame.destroy()
            pass

        elif response == ParserReturns.noPath:
            # self.sendError("Please select a levels directory from the settings", "red")
            pass
        else:
            self.savedLevels = response
            # Calls showResult on the main thread.
            self.window.event_generate("<<event1>>")
    
    # Helper methods _______________________________________________________________________

    def _bound_to_mousewheel(self, event):
        self.scrollerCanvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _unbound_to_mousewheel(self, event):
        self.scrollerCanvas.unbind_all("<MouseWheel>")

    def _on_mouse_wheel(self, event):
        self.scrollerCanvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    # level managing _______________________________________________________________________
    
    def removeFolder(self, source):
        destination = self.RPCS3Path
        destDir = os.path.join(destination,os.path.basename(source))
        if exists(destDir) == True:
            # self.sendError("The Level folder was removed")
            shutil.rmtree(destDir)
            self.refresh()

    def refresh(self):
        threading.Thread(target= self.fetchSavedLevels, args= ()).start()

    # window closing protocol ______________________________________________________________
    def onClose(self):
        self.closeDelegate()
        self.window.destroy()

    def showResult(self, evt):
        # destroy the old scroll view
        self.scrollerFrame.destroy()
        
        if self.savedLevels == []:
            ### notification later here ## 
            return
        
        # build new one
        self.scrollFrame1 = Frame(self.window,
                                  highlightbackground = helpers.GlobalVars.BGColorDark,
                                  highlightcolor      = helpers.GlobalVars.BGColorDark)

        self.scrollFrame1.grid(columnspan=3, column=0)

        self.scrollerCanvas = tk.Canvas(self.scrollFrame1,
                                        bg=helpers.GlobalVars.BGColorDark,
                                        borderwidth=0,
                                        highlightthickness=0)

        self.scrollerCanvas.grid(row=0, column=0, ipadx= 250, ipady=150)

        myScrollBar = ttk.Scrollbar(self.scrollFrame1, 
                                    orient=VERTICAL,
                                    command=self.scrollerCanvas.yview)

        myScrollBar.grid(row=0, column=1, sticky='ns')
        self.scrollerCanvas.configure(yscrollcommand = myScrollBar.set, bg = helpers.GlobalVars.BGColorDark)

        self.scrollerCanvas.bind('<Configure>', lambda e: self.scrollerCanvas.configure(scrollregion= self.scrollerCanvas.bbox("all")))
        
        self.scrollerCanvas.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollerCanvas.bind('<Leave>', self._unbound_to_mousewheel)

        scrollFrame2 = Frame(self.scrollerCanvas, 
                            background          = helpers.GlobalVars.BGColorDark,
                            highlightbackground = helpers.GlobalVars.BGColorDark,
                            highlightcolor      = helpers.GlobalVars.BGColorDark)

        self.scrollerCanvas.create_window((0,0), window=scrollFrame2, anchor="nw")
        self.scrollerFrame = self.scrollFrame1

            # Loop and build level cells for the scrollable frame
        savedLevels = self.savedLevels
        
        for index, level in enumerate(savedLevels):

            labelText = f'{level.title}' 

            levellogo = Image.open(level.image)

            levelImage_resize = levellogo.resize(( 120, 75 ))
            levellogo = ImageTk.PhotoImage(levelImage_resize)

            levelImage_resize = tk.Label(scrollFrame2, 
                                        image=levellogo,
                                        bg=helpers.GlobalVars.BGColorDark)
            levelImage_resize.image = levellogo
            
            levelPath = f'...{level.path[-80:]}' if len(level.path) > 90 else level.path
            imagePadx = helpers.Utilities.getPadding(len(levelPath))
            levelImage_resize.grid(row = index, column=0, padx=imagePadx)
            
            levelInfoButton = Button(scrollFrame2,
                                    text    = labelText + "\n" + levelPath, anchor="e",
                                    bd      = 0, 
                                    command = partial(helpers.Utilities.openFile, level.path),
                                    cursor  = "hand2",
                                    bg      = helpers.GlobalVars.BGColorDark,
                                    activebackground = helpers.GlobalVars.logoBlue,
                                    fg               = "white",
                                    font             = ('Helvatical bold',10))
            levelInfoButton.grid(row = index, column=1 , padx= 20, pady=(0, 20))

            removeLevelButton = tk.Button(scrollFrame2,
                                         text             ="Remove",
                                         command          = partial(self.removeFolder, level.path),
                                         bg               = "red",
                                         activebackground = helpers.GlobalVars.logoBlue,
                                         fg               = "white",
                                         height           = 1,
                                         width            = 13,
                                         bd               = 0)
            removeLevelButton.grid(row = index, column=1, pady=(50, 0))
