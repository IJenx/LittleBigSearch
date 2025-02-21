import os

class GlobalVars:
    BGColorDark   = "#1e1e1e"
    BGColorLight  = "#2f2f2f"
    logoBlue      = "#2cb4e8"


class Utilities:
    
    @staticmethod
    def openFile(path):
        try:
            path = os.path.realpath(path)
            os.startfile(path)
        except:
            print("Failed to open folder")
    
    #level info centre alignment. I hate tkinter
    @staticmethod
    def getPadding(charCount):
        padding = charCount - 155
        padding = abs(padding) + 25 if charCount < 60 else abs(padding)
        padding = abs(padding) - 10 if charCount > 85 else padding
        return (0, padding) 

        

