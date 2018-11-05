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
            self.dirBtn.append(wx.Button(self,wx.ID_ANY,'�ļ���·��',pos=(400,50+50*i),size=(90,20)))
            self.dirBtn[i].Bind(wx.EVT_BUTTON, lambda event,pos=i: self.openDir(event,pos))     
            self.pathShow.append(wx.StaticText(self,label='ѡ���ļ���',pos=(20,50+50*i),style=0,size=(350,20)))   #��ʾѡ����ļ�·��
            self.pathShow[i].SetBackgroundColour((0,0,0))      #�޸ı�����ɫ
            self.pathShow[i].SetForegroundColour((255,255,255))    #�޸�������ɫ
            self.path.append("")    #����·��������Ŀ¼����Ŀ¼������Ŀ¼��
        self.pathInput=wx.TextCtrl(self, style= wx.TE_MULTILINE , pos=(20,200) , size=(470,200))        #�ֶ������·��
        self.execute=wx.Button(self,wx.ID_ANY,'��ʼ',pos=(400,420),size=(90,20))
        self.execute.Bind(wx.EVT_BUTTON,self.OnExecute)
        self.toSearchDir=["\\setting","\\script","\\ui"]     #ֻ���������Ŀ¼�µĶ���
        #����Ŀ¼�ļ�Md5������Ŀ¼�ļ�Md5��������ļ�·����Ϊkey�����·��ָ\script\event\...֮�ࡣ��Ҫ�Ƿ���Ƚϣ���ֹ���ļ����ǿ��ǵ��ļ������ܻ�����
        self.srcMd5Infos={}
        self.workMd5Infos={}

    def openDir(self,e,i):
        tmpDirDlg=wx.DirDialog(self,'ѡ���ļ���') 
        if tmpDirDlg.ShowModal() == wx.ID_OK:
            DirPath=tmpDirDlg.GetPath()
            self.pathShow[i].SetLabelText(DirPath)
            self.path[i]=DirPath
        tmpDirDlg.Destroy()
    
    def OnExecute(self,event):
        if self.path[2]=="":
            wx.MessageBox('��ѡ��һ��Ŀ���ļ���','Tip',wx.OK | wx.ICON_INFORMATION)
            return
        if self.path[0]!="" and self.path[1]!="":
            self.ExecuteByCompare()
            return
        if self.pathInput.GetValue()!="":
            self.ExecuteByInput()
            return
        return

    def GetAllFilesMd5(self,rootDir,Md5Infos):      #��ȡĿ¼�������ļ���·������F:\1.txt  ��·��,����filespath��
        pathlist = os.listdir(rootDir)  #��ȡrootDir�����е�Ŀ¼���ļ�����
        for name in pathlist :
            pathI = os.path.join(rootDir,name)
            if os.path.isdir(pathI):
                self.GetAllFilesMd5(pathI,Md5Infos)
            elif os.path.isfile(pathI):
                if pathI.find(self.path[0])!=-1: 
                    Md5Infos[pathI.replace(self.path[0],'',1)]=GetFileMd5(pathI)
                if pathI.find(self.path[1])!=-1: 
                    Md5Infos[pathI.replace(self.path[1],'',1)]=GetFileMd5(pathI)     #������ø�һ�²�Ҫ���ַ���������á�

    def ExecuteByCompare(self):
        for needPath in self.toSearchDir:
            self.GetAllFilesMd5(self.path[0]+needPath,self.srcMd5Infos)
            self.GetAllFilesMd5(self.path[1]+needPath,self.workMd5Infos)
        #ɾ���ɵ�
        dstDir=self.path[2]+'\\gameres'
        if os.path.isdir(dstDir):
            shutil.rmtree(dstDir)
        for filePath,md5Value in self.workMd5Infos.items():
            if (filePath not in self.srcMd5Infos) or (self.srcMd5Infos[filePath]!=md5Value):     #������½����ļ����߸Ķ����ļ������Ƹ��ļ�������Ŀ¼
                #��ȡ�ļ�·��(\script\...��ʽ���Լ��ļ���)
                fileDir,fileName=os.path.split(filePath)
                #��ȡĿ���ļ�·��(��F:\script\test.lua)
                dstFilePath=dstDir+filePath
                srcFilePath=self.path[1]+filePath      #ע��Ҫ�ӹ���Ŀ¼������ȥ
                #��ȡĿ���ļ���·������Ҫ���ж��Ƿ�����Է��㴴��
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
            for needPath in self.toSearchDir:       #���\script  \setting  \ui�Ƿ���·���У�ȡ�����·��
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