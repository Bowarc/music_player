from os import path as osPath

# from Utils.Util_Methods import ResourcePath as RezPth


class ResourcePath():
    def __init__(self):
        pass

    def GetImage(self, ImageName):
        BasePath = osPath.abspath(".")
        RelativePath = 'App\\Src\\Images\\' + ImageName

        return osPath.join(BasePath, RelativePath)

    def GetQss(self, FileName):
        BasePath = osPath.abspath(".")
        RelativePath = 'App\\Src\\Qss\\' + FileName

        return osPath.join(BasePath, RelativePath)

    def GetMusic(self, MusicName):
        pass
