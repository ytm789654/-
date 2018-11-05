# coding=gbk
import os
import wx
import hashlib
import shutil

def GetFileMd5(filename):
    if not os.path.isfile(filename):
        print("No such file!")
        return
    myhash = hashlib.sha1()
    f = open(filename,'rb')
    b = f.read()
    myhash.update(b)
    f.close()
    return myhash.hexdigest()

class MainWindow(wx.Frame):
    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,title=title,size=(520,500))
        self.Show(True)
        self.dirBtn=[]
        self.pathShow=[]
        self.path=[]
        for i in range (0,3):
            self.dirBtn.append(wx.Button(self,wx.ID_ANY,'文件夹路径',pos=(400,50+50*i),size=(90,20)))
            self.dirBtn[i].Bind(wx.EVT_BUTTON, lambda event,pos=i: self.openDir(event,pos))     
            self.pathShow.append(wx.StaticText(self,label='选择文件夹',pos=(20,50+50*i),style=0,size=(350,20)))   #显示选择的文件路径
            self.pathShow[i].SetBackgroundColour((0,0,0))      #修改背景颜色
            self.pathShow[i].SetForegroundColour((255,255,255))    #修改字体颜色
            self.path.append("")    #三个路径，备份目录工作目录和生成目录。
        self.pathInput=wx.TextCtrl(self, style= wx.TE_MULTILINE , pos=(20,200) , size=(470,200))        #手动输入的路径
        self.execute=wx.Button(self,wx.ID_ANY,'开始',pos=(400,420),size=(90,20))
        self.execute.Bind(wx.EVT_BUTTON,self.OnExecute)
        self.toSearchDir=["\\setting","\\script","\\ui"]     #只检查这三个目录下的东西
        #备份目录文件Md5，工作目录文件Md5，以相对文件路径作为key，相对路径指\script\event\...之类。主要是方便比较，不止用文件名是考虑到文件名可能会重名
        self.srcMd5Infos={}
        self.workMd5Infos={}

    def openDir(self,e,i):
        tmpDirDlg=wx.DirDialog(self,'选择文件夹') 
        if tmpDirDlg.ShowModal() == wx.ID_OK:
            DirPath=tmpDirDlg.GetPath()
            self.pathShow[i].SetLabelText(DirPath)
            self.path[i]=DirPath
        tmpDirDlg.Destroy()
    
    def OnExecute(self,event):
        if self.path[2]=="":
            wx.MessageBox('请选择一个目标文件夹','Tip',wx.OK | wx.ICON_INFORMATION)
            return
        if self.path[0]!="" and self.path[1]!="":
            self.ExecuteByCompare()
            return
        if self.pathInput.GetValue()!="":
            self.ExecuteByInput()
            return
        return

    def GetAllFilesMd5(self,rootDir,Md5Infos):      #获取目录下所有文件的路径，如F:\1.txt  带路径,存在filespath中
        pathlist = os.listdir(rootDir)  #获取rootDir下所有的目录和文件名称
        for name in pathlist :
            pathI = os.path.join(rootDir,name)
            if os.path.isdir(pathI):
                self.GetAllFilesMd5(pathI,Md5Infos)
            elif os.path.isfile(pathI):
                if pathI.find(self.path[0])!=-1: 
                    Md5Infos[pathI.replace(self.path[0],'',1)]=GetFileMd5(pathI)
                if pathI.find(self.path[1])!=-1: 
                    Md5Infos[pathI.replace(self.path[1],'',1)]=GetFileMd5(pathI)     #这里最好改一下不要用字符串操作最好。

    def ExecuteByCompare(self):
        for needPath in self.toSearchDir:
            self.GetAllFilesMd5(self.path[0]+needPath,self.srcMd5Infos)
            self.GetAllFilesMd5(self.path[1]+needPath,self.workMd5Infos)
        #删除旧的
        dstDir=self.path[2]+'\\gameres'
        if os.path.isdir(dstDir):
            shutil.rmtree(dstDir)
        for filePath,md5Value in self.workMd5Infos.items():
            if (filePath not in self.srcMd5Infos) or (self.srcMd5Infos[filePath]!=md5Value):     #如果是新建的文件或者改动的文件，则复制该文件到包外目录
                #获取文件路径(\script\...格式，以及文件名)
                fileDir,fileName=os.path.split(filePath)
                #获取目的文件路径(如F:\script\test.lua)
                dstFilePath=dstDir+filePath
                srcFilePath=self.path[1]+filePath      #注意要从工作目录拷贝过去
                #获取目的文件夹路径，主要是判断是否存在以方便创建
                dstFileDir=dstDir+fileDir
                if os.path.exists(dstFileDir):
                    shutil.copyfile(srcFilePath,dstFilePath)
                else:
                    os.makedirs(dstFileDir)
                    shutil.copyfile(srcFilePath,dstFilePath)
        wx.MessageBox("OK!")
        return

    def ExecuteByInput(self):
        srcFilePaths = self.pathInput.GetValue().splitlines(False)
        for path in srcFilePaths:
            print(path)
        dstDir=self.path[2]+'\\gameres'
        if os.path.isdir(dstDir):
            shutil.rmtree(dstDir)
        for srcFilePath in srcFilePaths:                #srcPath= D:\script\event\xxxx.lua
            for needPath in self.toSearchDir:       #检查\script  \setting  \ui是否在路径中，取出相关路径
                pos = srcFilePath.find(needPath)
                if pos != -1:
                    filePath = srcFilePath[pos:]        #filePath = \script\event\xxxx.lua
                    fileDir,fileName = os.path.split(filePath)
                    dstFileDir = dstDir + fileDir   #F:\gameres\script\event\
                    dstFilePath = dstDir + filePath #F:\gameres\script\event\xxxx.lua
                    dstFileDir=dstDir+fileDir
                    if os.path.exists(dstFileDir):
                        shutil.copyfile(srcFilePath,dstFilePath)
                    else:
                        os.makedirs(dstFileDir)
                        shutil.copyfile(srcFilePath,dstFilePath)
                    break
        wx.MessageBox("OK!")
        return
app = wx.App(False)
frame = MainWindow(None," v1.0")
app.MainLoop()