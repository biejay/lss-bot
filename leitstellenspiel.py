#Alles

#Falls ein Fehler mit Selenium auftritt:
#pip install selenium
#pip install urllib3
#get https://raw.githubusercontent.com/LSS-Manager/lss-manager-v3/master/modules/lss-missionHelper/missions.de_DE.json
#u'ü' = Sperrm\u00fcllbrand



#Mac:
#brew cask install chromedriver
#install selenium via browser, unpack, install

import configparser
import getpass 
from selenium import webdriver
import re
import random
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pickle
import os.path
from os import path
import os
import stat
import time
import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import json 
aufgaben_file="aufgaben.lss"
vehicles_file="vehicles.lss"   
  
  
  

 
    

def settings():
    global username
    global password
    global browser_used
    config_file='lss_settings.ini'
    config = configparser.ConfigParser()
    if (path.exists(config_file)):
     
        config.read(config_file)
        username   = config['DEFAULT']['username'] 
        password = config['DEFAULT']['password']    
        browser_used = config['DEFAULT']['browser'] 
        if (username=="" or password=="" or browser_used!="chrome" and browser_used!="firefox"):
            print("Fehler beim Einlesen der Einstellungen. Bitte überprüfe den Inhalt der Einstellunsdatei:",config_file)
            quit()
        print("Dein Benutzername:",username)
        print("Dein Browser:",browser_used)
    else: 
        print("1. Setup vor dem Start:")
        username=input("Wie lautet deine E-Mail oder Spielername:") 
        password = getpass.getpass("Passwort:") 
        if (username=="" or password==""):
            print("Fehler bei der Eingabe. Beende...")
            quit()
        browser_used=input("Welcher Browser benutzt du? (chrome/firefox) [Standard=chrome]") 
        if (browser_used==""): browser_used="chrome"
        if (browser_used!="chrome" and browser_used!="firefox"):
            print("Ungültige Eingabe:",browser_used,"Beende...")
            quit()
        print("Speichere Einstellungen. Diese können später in folgender Datei angepasst werden:",config_file)
        config['DEFAULT']['username'] = username    
        config['DEFAULT']['password'] = password   
        config['DEFAULT']['browser'] = browser_used 
        with open(config_file, 'w') as configfile:    # save
            config.write(configfile)  
  
def personal_einstellen(driver):
    page=driver.get("https://www.leitstellenspiel.de/api/buildings")   
    if (browser_used=="chrome"):
        pre = driver.find_element_by_tag_name("pre").text
    if (browser_used=="firefox"):     
        pre=driver.find_element_by_id('json').text
    data = json.loads(pre)
    for i in data:
        if(str(i['building_type'])=="7"):
            print(datetime.now().strftime("%H:%M:%S"),"  ","Leitstelle",(30-len(i['caption']))*" "," ( 0 ) : Skippe Leitstelle")           
            continue 
        driver.get("https://www.leitstellenspiel.de/buildings/"+str(i['id']))
        inhalt=str(driver.page_source)
        angestellte=inhalt[inhalt.find("Personal:")+43:inhalt.find("Angestellte")-1]
        driver.get("https://www.leitstellenspiel.de/buildings/"+str(i['id'])+'/hire')  
        inhalt=str(driver.page_source)
        print(datetime.now().strftime("%H:%M:%S"),"  ",i['caption'],(30-len(i['caption']))*" ","(",angestellte,") : ",end="")
        if ("Die Einstellungsphase läuft noch" in inhalt):
            start=inhalt.find("Die Einstellungsphase läuft noch")
            print(datetime.now().strftime("%H:%M:%S"),"  ",inhalt[start:start+40])
            continue
        driver.get("https://www.leitstellenspiel.de//buildings/"+str(i['id'])+"/hire_do/3")
        time.sleep(2)
        temp=driver.find_element_by_xpath("//div[contains(@class, 'alert fade in alert-success ')]")
        temp=temp.text.split("\n")
        print(datetime.now().strftime("%H:%M:%S"),"  ",temp[1])
        
def get_credits(driver,zeitraum):
    if (zeitraum>30):
        return "Fehler, Zeitraum zu groß! Wähle weniger als 30 Tage!"
    max_pages=100    
    w, h = 3, 20*max_pages  #6 Items in x 'reihen' Reihen       
    credit = [[0 for x in range(w)] for y in range(h)] 
    x=-1
    max_pages=max_pages+1
    for page in range(1,max_pages):
        print(datetime.now().strftime("%H:%M:%S"),"  ","Seite",page,"/",max_pages-1)
        x=x-1
        url=" https://www.leitstellenspiel.de/credits?page="+str(page)
        driver.get(url)     
        inhalt = str(driver.page_source)
        if ("Bisher besteht noch kein Eintrag." in inhalt):
        	return "Fehler, zu wenig Einträge vorhanden! Zeitraum (aktuell: ",zeitraum,"Tage) verkleinern?"   
        table = driver.find_elements_by_tag_name('table')          
        for tables in table:         
          for row in tables.find_elements_by_xpath(".//tr"):
            x=x+1 
            y=-1    
            for td in row.find_elements_by_xpath(".//td"):
                y=y+1
                td=td.text  
                if (y==0):
                    td=td.replace(".","")
                credit[x][y]=td
                if (y==2):
                    datetime_str = str(credit[x][y])                    
                    englisch=['January', 'Feburary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
                    deutsch=['Januar','Februar','März','April','Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
                    for date in range(0,len(englisch)):
                         datetime_str=datetime_str.replace(deutsch[date],englisch[date])
                    year = time.strftime("%Y")   
                    datetime_str=datetime_str.replace("Uhr",year)
                    datetime_object = datetime.strptime(datetime_str, '%d. %B, %H:%M %Y')
                    #print(datetime.now().strftime("%H:%M:%S"),"  ",x,credit[x][1],datetime_object.strftime("%d.%m.%Y %H:%M"))
                    if ((datetime.now() - datetime_object).days>zeitraum-1):
                        credit=credit[:x]
                        print(datetime.now().strftime("%H:%M:%S"),"  ",len(credit),"abgeschlossene Missionen in letzten",zeitraum,"Tagen gefunden!" )
                        return credit                   
    return "Fehler, konnte nicht alle Missionen der letzten",zeitraum,"Tage abrufen (letztes Datum: "+datetime_str+"). Zeitraum verkleinern!?"

def credit_calc(credit,zeitraum):
    all_creds=0
    verbands_missions=0
    single_missions=0
    single_creds=0
    verbands_creds=0
    for x in range(0,len(credit)):    
      
        all_creds=all_creds+int(credit[x][0])        
        if ("[Verband]" in credit[x][1]):
            verbands_creds=verbands_creds+int(credit[x][0])
            verbands_missions+=1
        else:
            single_creds=single_creds+int(credit[x][0])           
            single_missions+=1  
    print(datetime.now().strftime("%H:%M:%S"),"  ","Missionsstatistiken",zeitraum,"Tag(e)")        
    print(datetime.now().strftime("%H:%M:%S"),"  ","Alle Missionen    (",len(credit),"):",all_creds,"Credits -> Entspricht Ø",round(all_creds/len(credit)),"pro Mission")
    print(datetime.now().strftime("%H:%M:%S"),"  ","Verbandsmissionen (",verbands_missions,"):",verbands_creds," Credits -> Entspricht Ø",round(verbands_creds/verbands_missions),"pro Mission")
    print(datetime.now().strftime("%H:%M:%S"),"  ","Single-Missionen  (",single_missions,"):",single_creds," Credits -> Entspricht Ø",round(single_creds/single_missions),"pro Mission")
    
def call_aufgaben(driver): 
    global aufgaben    
    #1.1 Öffne Github und rufe Aufgaben sowie benötigte Fahrzeuge ab
    if (path.exists(aufgaben_file) and (time.time()-os.path.getmtime(aufgaben_file))/3600 < 72):
        with open (aufgaben_file, 'rb') as fp:
            aufgaben = pickle.load(fp)  
        print(datetime.now().strftime("%H:%M:%S"),"  ","Datei:",aufgaben_file,"gefunden, lese verfügbare Aufgaben ein...")
        print(datetime.now().strftime("%H:%M:%S"),"  ",len(aufgaben),"verschiedene Aufgaben gefunden!")    
    else:   
        try:
            if((time.time()-os.path.getmtime(aufgaben_file))/3600> 72):
                print(datetime.now().strftime("%H:%M:%S"),"  ","Datei:",aufgaben_file,"seit über 72h nicht mehr geupdatet. Hole aktuelle Daten online...")
        except:
            print(datetime.now().strftime("%H:%M:%S"),"  ","Datei:",aufgaben_file,"nicht gefunden. Rufe Daten online ab...")
        print ("#1.1 Öffne Wiki und rufe Aufgaben sowie benötigte Fahrzeuge ab...")
        url="https://raw.githubusercontent.com/LSS-Manager/lss-manager-v3/master/modules/lss-missionHelper/missions.de_DE.json"
        driver.get(url)
        if (browser_used=="chrome"):
            pre = driver.find_element_by_tag_name("pre").text
        if (browser_used=="firefox"):     
                pre=driver.find_element_by_id('json').text
        data = json.loads(pre)
        x=0
        reihen=len(data)
        w, h = 3, reihen  #6 Items in x 'reihen' Reihen       
        aufgaben = [[0 for x in range(w)] for y in range(h)] 
        for i in data: 
            aufgaben[x][0]=data[str(i)]['name']
            aufgaben[x][1]=data[str(i)]['average_credits']
            aufgaben[x][2]=data[str(i)]['requirements']
            x+=1
        print(datetime.now().strftime("%H:%M:%S"),"  ",reihen,"verschiedene Aufgaben gefunden! --> Speichere in",aufgaben_file) 
        with open(aufgaben_file, 'wb') as fp:
            pickle.dump(aufgaben, fp)
def call_cars(driver):
     global vehicles
     if (path.exists(vehicles_file) and (time.time()-os.path.getmtime(vehicles_file))/3600 < 72):
        with open (vehicles_file, 'rb') as fp:
            vehicles = pickle.load(fp)  
        print(datetime.now().strftime("%H:%M:%S"),"  ","Datei:",vehicles_file,"gefunden, lese verfügbare Aufgaben ein...")
        print(datetime.now().strftime("%H:%M:%S"),"  ",len(vehicles),"verschiedene Fahrzeuge gefunden!")      
     else:   
        try:
            if((time.time()-os.path.getmtime(vehicles_file))/3600> 72):
                print(datetime.now().strftime("%H:%M:%S"),"  ","Datei:",vehicles_file,"seit über 72h nicht mehr geupdatet. Hole aktuelle Daten online...")
        except:
            print(datetime.now().strftime("%H:%M:%S"),"  ","Datei:",vehicles_file,"nicht gefunden. Rufe Daten online ab...")
        print(datetime.now().strftime("%H:%M:%S"),"  ","#1.2 Öffne Wiki und rufe Fahrzeugtypen ab ")
        #1.2 Öffne Wiki und rufe Fahrzeugtypen ab       
        url = 'https://wiki.leitstellenspiel.de/index.php?title=Fahrzeug_%C3%9Cbersicht'     
        try: 
            print(datetime.now().strftime("%H:%M:%S"),"  ","try")
            driver.get(url)
            table = driver.find_elements_by_tag_name('table')
        except: 
            print(datetime.now().strftime("%H:%M:%S"),"  ","except")
           # global driver
            driver.get(url)
            table = driver.find_elements_by_tag_name('table')
        x=-2
        reihen=0
        for tables in table: 
           reihen=reihen+len(tables.find_elements_by_xpath(".//tr"))
        vehicles = [0 for y in range(0,reihen)] 
        for tables in table: 
          for row in tables.find_elements_by_xpath(".//tr"):
            x=x+1 
            y=-1    
            for td in row.find_elements_by_xpath(".//td"):
               y=y+1
               td=td.text              
               td=td.replace("\n","+")   
               td=td.replace(" ","")        
               if (y ==0):        
                  vehicles[x]=td
          print(datetime.now().strftime("%H:%M:%S"),"  ",round(x/reihen*100),"%...",end="")        
        print(datetime.now().strftime("%H:%M:%S"),"  ",reihen,"verschiedene Fahrzeuge gefunden! --> Speichere in",vehicles_file) 
        with open(vehicles_file, 'wb') as fp:
            pickle.dump(vehicles, fp)
def login(driver):
    #2 Einloggen
    print(datetime.now().strftime("%H:%M:%S"),"  ","#2 Einloggen")
    #options = webdriver.ChromeOptions()
    #options.add_argument("headless")
    #driver = webdriver.Chrome(options=options)
    url="https://www.leitstellenspiel.de/users/sign_in"
    try: 
        driver.get(url)
    except: 
        #global driver
        if (browser_used=="chrome"):
            driver=webdriver.Chrome()
        else:
            driver=webdriver.Firefox()
        driver.get(url)    
    inhalt = str(driver.page_source)
    if ("Du bist bereits angemeldet." in inhalt):
        return
    usernamefield = driver.find_element_by_id("user_email")
    passwordfield = driver.find_element_by_id("user_password")
    usernamefield.send_keys(username)
    passwordfield.send_keys(password)
    driver.find_element_by_name("commit").click()
def call_cur_missions(driver):
    #3 Aktuelle Missionen abrufen   
    print(datetime.now().strftime("%H:%M:%S"),"  ","#3 Aktuelle Missionen abrufen")
    global missions
    global mission_id
    global mission_alliance
    global mission_missing
    driver.get("https://www.leitstellenspiel.de/")
    time.sleep(2)
    inhalt = str(driver.page_source)
    temp=[m.start() for m in re.finditer('missionMarkerAdd', inhalt)]
    print (datetime.now().strftime("%H:%M:%S"),"  ","Gefundene Missionen:",str((len(temp))))
    missions=["NONE"]*len(temp)
    mission_id=["NONE"]*len(temp)
    mission_alliance=["NONE"]*len(temp)
    mission_missing=["NONE"]*len(temp)
    for i in range(0,len(temp)):
           if (i<len(temp)-1):
               cur_inhalt=inhalt[temp[i]:temp[i+1]]   
           else:
                cur_inhalt=inhalt[temp[i]:len(inhalt)]
           start=cur_inhalt.find('"caption"')
           end=cur_inhalt.find('"',start+11)
           missions[i]=cur_inhalt[start+11:end]
          
           start=cur_inhalt.find('"id"')
           end=cur_inhalt.find('"',start+5)  
           mission_id[i]=cur_inhalt[start+5:end-1]
        
           start=cur_inhalt.find('"alliance_id"')
           end=cur_inhalt.find('"',start+13)       
           mission_alliance[i]=cur_inhalt[start+14:end-1]    
           if (mission_alliance[i]=="null"):
              mission_alliance[i]=0
           else:
              mission_alliance[i]=1
                            
           start=cur_inhalt.find('"missing_text"')
           end=cur_inhalt.find('"',start+16)  
           mission_missing[i]=cur_inhalt[start+16:end]      
           if (mission_missing[i]=="ull,"):
              mission_missing[i]=0
           else:
              cur_inhalt=mission_missing[i]
              start=cur_inhalt.find(":")
              end=cur_inhalt.find(".")
              mission_missing[i]= cur_inhalt[start+2:end]
                   
           #print(datetime.now().strftime("%H:%M:%S"),"  ",i+1,missions[i],"ID:",mission_id[i],"Allianz:",mission_alliance[i],"Missing:",mission_missing[i]) 
           row=-1 
           for r in aufgaben:
             row=row+1   
             if (str(r[0]) in missions[i]):
                 break
           #print ("-->Gefunden:",aufgaben[row][0],"-Dafür benötigt:",aufgaben[row][1])
           #print ("-->Credits:",aufgaben[row][2])
         #  if (mission_alliance[i]==0):
         #     print(datetime.now().strftime("%H:%M:%S"),"  ",i+1,missions[i],"Credits:",aufgaben[row][2])
def alertt(driver):    
     try:
        WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' +
                                       'confirmation popup to appear.')
        alert = driver.switch_to.alert    
        print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,alert.text)
        alert.accept()
       # print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,"Fahrzeug nicht verfügbar")
     except TimeoutException:
        return    
def alarmieren(driver):
    global needed
    #5 Fahrzeuge vor Ort / Auf Anfahrt  
    print(datetime.now().strftime("%H:%M:%S"),"  ","#5 Alarmieren")
    for i in range(0,len(missions)):     
      string=str(i+1)+" / "+str(len(missions))       
      printtstart=(len(string)+1)*" "
      print(datetime.now().strftime("%H:%M:%S"),"  ",i+1, "/",str(len(missions))," ",end="")
      additional=0
      if (mission_alliance[i]==0): 
        url="https://www.leitstellenspiel.de/missions/"+mission_id[i]
        driver.get(url)
        time.sleep(3)
        source=str(driver.page_source)
        if ("Der Einsatz wurde erfolgreich abgeschlossen." in str(driver.page_source)):
            print(missions[i],"...Skippe abgeschlossenen Einsatz",)
            continue
        if ("Beginn in:" in source):
            start=source.find("missionCountdown(")            
            end=source[start:].find(",")
            restzeit=source[start+17:start+end]     
            restzeit=int(restzeit)/60           
            if (restzeit>15):
                print(missions[i],"...Skippe Mission, Beginn erst in",round(restzeit),"Minuten")
                continue
        lf_da=0
        dlk_da=0
        elw_da=0
        rw_da=0
        manpower_da=0
        row=-1
        for r in aufgaben:
                 row=row+1   
                 if (str(r[0]) in missions[i]):
                     break                 
        if (row+1==len(aufgaben)):
           print(missions[i],"- Credits: unbekannt")
        else:         
           print(missions[i],"( Ø",aufgaben[row][1],"Credits )")
        try:
            vorort=1
            find= driver.find_element_by_id('mission_vehicle_at_mission')         
            for row in find.find_elements_by_xpath(".//tr"):
              x=0  
              for cell in row.find_elements_by_xpath(".//td"):
                value=""
                if (x==1):
                  value=cell.text    
                if ("LF" in value):
                    lf_da+=1
                if ("DLK" in  value):
                    dlk_da+=1    
                if ("ELW" in value):
                    elw_da+=1 
                if ("RW" in  value):
                    rw_da+=1  
                if (x==3):
                    value=cell.text         
                    manpower_da=manpower_da+ int(value)
                x+=1            
        except:
            vorort=0
            print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,"Keine Fahrzeuge vor Ort")         
        lf_an=0
        dlk_an=0
        elw_an=0
        rw_an=0
        manpower_an=0
        try: 
            find= driver.find_element_by_id('mission_vehicle_driving')
            ankommend=1
            for row in find.find_elements_by_xpath(".//tr"):
              x=0  
              for cell in row.find_elements_by_xpath(".//td"):
                value=""  
                if (x==1):
                    value=cell.text   
                for auto in fahrzeuge_abk:                    
                   if(auto in value):
                     fahrzeuge_an[fahrzeuge_abk.index(auto)]=+1             
                if (x==4):
                    value=cell.text         
                    manpower_an=manpower_an+ int(value)
                x+=1   
        #    print(datetime.now().strftime("%H:%M:%S"),"  ","Auf Anfahrt:")    
        #    print(datetime.now().strftime("%H:%M:%S"),"  ","LF:"+str(lf_an))
        #    print(datetime.now().strftime("%H:%M:%S"),"  ","DLK:"+str(dlk_an))
        #    print(datetime.now().strftime("%H:%M:%S"),"  ","ELW:"+str(elw_an))
        #    print(datetime.now().strftime("%H:%M:%S"),"  ","RW:"+str(rw_an))   
        #    print(datetime.now().strftime("%H:%M:%S"),"  ","Manpower:"+str(manpower_an))
        except:
            print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,"Keine Fahrzeuge auf Anfahrt")
            ankommend=0
        if ("Wir benötigen noch min." not in str(driver.page_source) and "Zusätzlich benötigte Fahrzeuge:" not in str(driver.page_source) and "missionCountdown(" in source and vorort==1 or "Wir benötigen noch min." not in str(driver.page_source) and "Zusätzlich benötigte Fahrzeuge:" not in str(driver.page_source) and ankommend==1 and "missionCountdown(" in source):
            start=source.find("missionCountdown(")
            #restzeit=source[start+17:]
            end=source[start:].find(",")
            restzeit=source[start+17:start+end]     
            restzeit=int(restzeit)/60
            print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,"...Skippe Mission, alle Fahrzeuge vor Ort. Restzeit:",round(restzeit),"Minute(n)")
            continue      
        row=-1
        for r in aufgaben:
                 row=row+1   
                 if (str(r[0]) in missions[i]):
                     break    
                    
        if ("Zusätzlich benötigte Fahrzeuge:" in str(driver.page_source)):
            additional=1
            source=str(driver.page_source)
            start=source.find("Zusätzlich benötigte Fahrzeuge:")        
            end=source[start:].find(".")          
            needed=source[start+31:start+end]            
            if (source[start+end-1:start+end+8]=="l. Wasser"):
                 start=source.find("Zusätzlich benötigte Fahrzeuge:")                
                 end=source[start+42:].find(".")  
                 needed=source[start+47:start+42+end]
                 print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,"Was mit Wasser und needed:",needed)  
                 if (lf_an==0 and ankommend==0):   
                     print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,"Schicke 1 LF als Mannschaftsverstärkung")
                     driver.find_element_by_xpath('//*[@title="1 LF"]').click()      
                     ankommend=1
                     alertt(driver)
            #print(datetime.now().strftime("%H:%M:%S"),"  ",needed)   
            if (ankommend==0):
              #  print(datetime.now().strftime("%H:%M:%S"),"  ",needed)
                if ("(" in needed):
                    temp=needed.split(")")
                    needed=""
                    for j in temp:
                        if ("(" in j):
                          #  print(datetime.now().strftime("%H:%M:%S"),"  ",j)
                            end=j.find("(")
                            if (j[len(j)-1:len(j)]==" "):
                                needed=needed+j[:end]
                            else:
                                needed=needed+j[:end-1]
                        else:
                            needed=needed+j
                   # print(datetime.now().strftime("%H:%M:%S"),"  ",needed)    
                if ("," in needed):
                    needed=needed.split(",")                
                    for auto in needed:
                      # print(datetime.now().strftime("%H:%M:%S"),"  ",auto)
                      # print ("Auto:",auto[3:],"-",auto[1:2],"Mal rufen")
                       for h in range(0,int(auto[1:2])):                       
                         call='//*[@title="1 '+auto[3:]+'"]'   
                        # print(datetime.now().strftime("%H:%M:%S"),"  ","call:",call)
                         driver.find_element_by_xpath(call).click()                       
                         alertt(driver)                
                else:
                    #print ("Auto:",needed[3:],"-1 Mal rufen")
                    for h in range(0,int(needed[1:2])):                       
                         call='//*[@title="1 '+needed[3:]+'"]'   
                       #  print(datetime.now().strftime("%H:%M:%S"),"  ","call:",call)
                         driver.find_element_by_xpath(call).click()                       
                         alertt(driver)
            else:
                print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,"Es sind bereits Fahrzeuge auf Anfahrt, warte ab und schicke keine weiteren.")
                #continue
            #for auto in fahrzeuge_abk:
            #    if (auto in needed):
            #        needed = needed[::-1]                  
            #        needed=needed[needed.find(auto[::-1]):]                    
            #        if (" redo " in needed):
            #            needed=needed[10:] 
             #       else:    
             #           needed=needed[3:]
             #       anzahl_needed=int(needed[needed.find(" ")+1:needed.find(" ")+2])     
             #     #  print(datetime.now().strftime("%H:%M:%S"),"  ","anzahl needed:",anzahl_needed,"auto:",auto,"anzahl ankommend:",fahrzeuge_an[fahrzeuge_abk.index(auto)])  
             #       for x in range (0,anzahl_needed-fahrzeuge_an[fahrzeuge_abk.index(auto)]):                        
             #         call='//*[@title="1 '+fahrzeuge_abk[fahrzeuge_abk.index(auto)+1]+'"]'    
             #        # print(datetime.now().strftime("%H:%M:%S"),"  ",call)
             #         driver.find_element_by_xpath(call).click()                       
             #         alertt(driver)                  
        else:            
          #  lf_need=0
          #  dlk_need=0
          #  rw_need=0
          #  elw_need=0
          #  needed=str(aufgaben[row][1])    
          #  if (row+1==len(aufgaben)):
          #      print ("  Unbekanntes Einsatzstichwort")
          #      needed ="1x Löschfahrzeug"            
          #  for auto in fahrzeuge_abk:
          #      if (auto in needed):
          #          needed = needed[::-1]
          #          needed=needed[needed.find(auto[::-1]):]
          #          anzahl_needed=int(needed[needed.find(" x")+2:needed.find(" x")+3]) 
          #          #print(datetime.now().strftime("%H:%M:%S"),"  ","anzahl needed:",anzahl_needed,"auto:",auto,"anzahl ankommend:",fahrzeuge_an[fahrzeuge_abk.index(auto)])  
          #          for x in range (0,anzahl_needed):                        
          #            call='//*[@title="1 '+fahrzeuge_abk[fahrzeuge_abk.index(auto)+1]+'"]'                      
          #            driver.find_element_by_xpath(call).click()                       
          #            alertt(driver)
            if ("Wir benötigen noch min." in str(driver.page_source) and lf_an==0 and ankommend==0):
                additional=1 
                print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,"Schicke 1 LF als Mannschaftsverstärkung")               
                driver.find_element_by_xpath('//*[@title="1 LF"]').click()                
                alertt(driver)  
      
       # print(datetime.now().strftime("%H:%M:%S"),"  ","")
       # print(datetime.now().strftime("%H:%M:%S"),"  ","Differenz:")
       # print(datetime.now().strftime("%H:%M:%S"),"  ","LF benötigt:",str(lf_need-lf_da-lf_an))    
       # print(datetime.now().strftime("%H:%M:%S"),"  ","DLK benötigt:",str(dlk_need-dlk_da-dlk_an))  
       # print(datetime.now().strftime("%H:%M:%S"),"  ","RW benötigt:",str(rw_need-rw_da-rw_an))  
       # print(datetime.now().strftime("%H:%M:%S"),"  ","ELW benötigt:",str(elw_need-elw_da-elw_an))  
        if (additional == 0 and vorort==0 and ankommend==0):              
             print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,"Schicke 1 LF als Vorhut")               
             driver.find_element_by_xpath('//*[@title="1 LF"]').click()                
             alertt(driver)  
        if (additional == 18236123):
            try: 
             if (lf_need-lf_da-lf_an>0):
              for x in range (0,lf_need-lf_da-lf_an):
                  driver.find_element_by_xpath('//*[@title="1 LF"]').click()
                  # alert = driver.switch_to.alert
                  #alert.accept()
                  time.sleep(random.randint(1, 4))
             if (elw_need-elw_da-elw_an>0):
              for x in range (0,elw_need-elw_da-elw_an):
                  driver.find_element_by_xpath('//*[@title="1 ELW"]').click()
                  # alert = driver.switch_to.alert
                  #alert.accept()
                  time.sleep(random.randint(1, 4))
             if (dlk_need-dlk_da-dlk_an>0):
              for x in range (0,dlk_need-dlk_da-dlk_an):
                  driver.find_element_by_xpath('//*[@title="1 DLK"]').click()
                 # alert = driver.switch_to.alert
                  time.sleep(random.randint(1, 4))
             if (rw_need-rw_da-rw_an>0):
              for x in range (0,rw_need-rw_da-rw_an):
                  driver.find_element_by_xpath('//*[@title="1 RW"]').click()
                 # alert = driver.switch_to.alert
                  time.sleep(random.randint(1, 4))
            except:
             alertt(driver)                    
            
        try: 
            element = driver.find_element_by_name("commit")
            driver.execute_script("arguments[0].click();", element)
            #if (additional == 0):
            #     print (lf_need-lf_da-lf_an,"LF,", elw_need-elw_da-elw_an,"ELW,",dlk_need-dlk_da-dlk_an,"DLK,",rw_need-rw_da-rw_an,"RW zu Mission",missions[i],"geschickt!")
            #if (additional == 1):
            #     print ("Benötigte Verstärkung geschickt:", lf_need,"LF,", elw_need,"ELW,",dlk_need,"DLK,",rw_need,"RW zu Mission",missions[i],"geschickt!")
            time.sleep(2)
            temp=driver.find_element_by_xpath("//div[contains(@class, 'alert fade in alert-success ')]")
            temp=temp.text.split("\n")
            print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,temp[1])
            time.sleep(random.randint(2, 8))
        except:
            alertt(driver)
      else:
        row=-1
        for r in aufgaben:
                 row=row+1   
                 if (str(r[0]) in missions[i]):
                     break                          
        if (row+1==len(aufgaben)):
           print(missions[i],"...Skippe Verbandsmission, unbekannte Aufgabe")   
        else:   
           credits=aufgaben[row][1]
           #print(datetime.now().strftime("%H:%M:%S"),"  ","credits:",credits)
          # try: 
          #      credits=credits.replace(".","")
          # except:
          #      credits=credits
          # try: 
           #     credits=credits.replace("ca","")
           #except:
           #     credits=credits
           #if ("Ø" in credits):
           #     start=credits.find("Ø")
           #     credits=credits[start+1:]
           #if ("Credits" in credits):
           #     start=credits.find("Credits")
           #     credits=credits[:start]  
                
          # if ("-" in credits):
          #      start=credits.find("-")
          #      credits=credits[start+2:]  
           #print(datetime.now().strftime("%H:%M:%S"),"  ","neue credits:",credits)       
           try:
                credits=int(credits)
           except:
                print(missions[i],"...Skippe Verbandsmission, unklare Credits (",credits,")")
                continue
           if (credits+1>creditgrenze):
                url="https://www.leitstellenspiel.de/missions/"+mission_id[i]
                driver.get(url)
                time.sleep(3)
                source=str(driver.page_source)
                if ("Rückalarmieren" in source):
                     print(missions[i],"...Skippe Verbandsmission ( Ø",aufgaben[row][1],"Credits ). Bereits Fahrzeug(e) vor Ort.")
                else:
                    if ("Beginn in:" in source):
                        start=source.find("missionCountdown(")            
                        end=source[start:].find(",")
                        restzeit=source[start+17:start+end]     
                        restzeit=int(restzeit)/60           
                        if (restzeit>15):
                            print(missions[i],"...Skippe Mission, Beginn erst in",round(restzeit),"Minuten")
                            continue
                    print(missions[i],"( Ø",aufgaben[row][1],"Credits )")         
                    print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,"Schicke 1 LF zur Verbandsmission")   
                    try:        
                        driver.find_element_by_xpath('//*[@title="1 LF"]').click()                
                        alertt(driver)         
                        element = driver.find_element_by_name("commit")
                        alertt(driver)
                        driver.execute_script("arguments[0].click();", element)       
                        alertt(driver)
                        time.sleep(2)
                        temp=driver.find_element_by_xpath("//div[contains(@class, 'alert fade in alert-success ')]")
                        temp=temp.text.split("\n")
                        print(datetime.now().strftime("%H:%M:%S"),"  ",printtstart,temp[1])
                        time.sleep(random.randint(2, 8))
                    except:
                        alertt(driver)
           else:           
                print(missions[i],"...Skippe Verbandsmission, Ø",aufgaben[row][1],"Credits ist unter Creditgrenze von",str(creditgrenze),")")
        
def globaling(hidden):
    if (hidden=="ja"):
        print(datetime.now().strftime("%H:%M:%S"),"  ","Starte versteckt")
        if (browser_used=="chrome"):
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            options.add_argument("disable-gpu")
            driver = webdriver.Chrome(options=options)       
        else:
            options = Options()
            options.add_argument("disable-gpu")
            options.headless = True
            driver = webdriver.Firefox(options=options)    
    else:
         if (browser_used=="chrome"):
            driver=webdriver.Chrome()     
         else:
           driver=webdriver.Firefox()  
    return driver
def get_status(driverc):
    try:
        driverc.get("www.google.de")
        return "Alive"
    except:
        return "Dead"
    
fahrzeuge_abk=["Löschfahrzeug","LF","Drehleiter","DLK","Rüstwagen","RW","ELW 1","ELW 1", "Einsatzleitwagen 2","ELW 2","GW-Öl","GW-ÖL"]    
fahrzeuge_an=[0]*len(fahrzeuge_abk)
printtstart="       "

settings()


hidden=input("Browser versteckt starten? (ja/nein) [Standard=nein]: ") 

print("Was willst du tun?")
print("1 Bot starten")
print("2 Personal einstellen")
print("3 Creditstatistik abrufen")
auswahl=input("1, 2 oder 3:")




if (auswahl=="2"):
    browser=globaling(hidden)        
    login(browser)
    personal_einstellen(browser)
    browser.quit() 
    quit()
if (auswahl=="3"):
    creds_zeitraum=input("Wie viele Tage? [Standard=1]: ")     
    if (creds_zeitraum==""): 
        creds_zeitraum=1
    else:
        try:
            creds_zeitraum=int(creds_zeitraum)
        except:
            print("Ungültiges Format, nur Zahlen erlaubt! (",creds_zeitraum,")")
            quit()
    browser=globaling(hidden)        
    login(browser)
    credit=get_credits(browser,creds_zeitraum)
    if ("Fehler" in credit):
        print(datetime.now().strftime("%H:%M:%S"),"  ",credit)
    else:
       credit_calc(credit,creds_zeitraum)  
    browser.quit() 
    quit()
    
if (auswahl=="1"):   
    durchgaenge=input("Wie viele Durchgänge sollen laufen [Standard=1]: ") 
    if durchgaenge == "":
            durchgaenge=1
    else:
            durchgaenge=int(durchgaenge)
    creditgrenze=2500
    browser=globaling(hidden)
    try: aufgaben
    except:  call_aufgaben(browser)       
    try: vehicles
    except:  call_cars(browser)
    #try: driver.get("www.google.de")
    #except: driver=webdriver.Chrome()    
    login(browser)    
    for i in range(0,durchgaenge):
        print (datetime.now().strftime("%H:%M:%S"),"  ","Durchgang",i+1,"/",durchgaenge)
        call_cur_missions(browser)
        alarmieren(browser)
        if (i+1<durchgaenge):
            rand=random.randint(40,80)
            print(datetime.now().strftime("%H:%M:%S"),"  ","Noch",rand,"Sekunden...")
            time.sleep(rand)
            rand=random.randint(40,80)
            print(datetime.now().strftime("%H:%M:%S"),"  ","Noch",rand,"Sekunden...")
            time.sleep(rand)
    print(datetime.now().strftime("%H:%M:%S"),"  ","Ende")    
    browser.quit() 
    quit()


print(datetime.now().strftime("%H:%M:%S"),"  ",auswahl,"ist keine gültige Möglichkeit. Beende...")
