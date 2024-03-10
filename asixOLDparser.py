import xml.etree.ElementTree as ET
import asixObject
from pyvis.network import Network
import re
import sys
import os.path
import pandas

ASCIart="""  
   ____ _____ _____                            
  / ___| ____|_   _|                           
 | |  _|  _|   | |                             
 | |_| | |___  | |                             
  \____|_____| |_|    _   _ _   _ _____ _      
  / ___| | | |  / \  | \ | | \ | | ____| |     
 | |   | |_| | / _ \ |  \| |  \| |  _| | |     
 | |___|  _  |/ ___ \| |\  | |\  | |___| |___  
  \____|_|_|_/_/_ _\_\_| \_|_| \_|_____|_____| 
 |_ _| \ | |  ___/ _ \                         
  | ||  \| | |_ | | | |                        
  | || |\  |  _|| |_| |                        
 |___|_| \_|_|   \___/     """

xmlFile=""
asixStations=[]

'''FIND COM port number'''
def findCOMnumber(text)->str|None:
    COMPort=re.search('(Port=([0-9]+))|(port=([0-9]+))|(port=COM([0-9]+)|(COM[0-9]+))',text) # Find COM Port from Params
    if COMPort: 
        COMPortStr=COMPort.group()
        if(COMPortStr):
            onlyNumber=re.search('[0-9]+',COMPortStr)
            if onlyNumber.group():
                return onlyNumber.group()
            return COMPortStr
        else:
            return ""

'''FIND IPv4 Addres'''
def findIPaddress(text)->str|None: 
    IPAddr=re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',text) # Find IPAddress Port from Params
    if IPAddr: 
        IPAddrStr=IPAddr.group()
        return IPAddrStr
    else:
        return ""


def readRecurse(child):
    """Read all document step by step/child by child..."""
    #find variants because computers are in this tag
    variants=child.findall('variant')
    for variant in variants:

        #Check if is it a computer
        isComputer=variant.get('type')
        #Get computer name
        computerName=variant.get('name')
        if isComputer=='computer':
            if computerName:
                print(f"Odnaleziono komputer: {computerName}")
                
                #Create new station:
                tmpStation=asixObject.asixStation()
                tmpStation.name=computerName
            channelList=[] #create temporary channel array for this station/computer
            #Look for the channels:
                
            sections=variant.findall('section') #Channels are in section
            if sections:
                for section in sections:    #search the channels section in computer
                    if section.get('name')=="channels": 
                        channels=section.findall('channel') #list all channels into iterable
                        if channels:
                            #print("\t with channels: ")
                            print('Ładowanie kanałów')
                            for channel in channels:        #play witch each channel
                                channelName=channel.get('name') #get channel name
                                tmpChannel=asixObject.asixChannel() #create channel

                                if channelName:
                                    #print(f"\t\t{channelName}")
                                    #print('.')
                                    tmpChannel.name=channelName #assign channel name
                                channelDriver=channel.get('driver') #get channel driver
                                if channelDriver:
                                    #print(f"\t\t\t Driver: {channelDriver}")
                                    tmpChannel.driver=channelDriver #assign channel driver
                                channelParams=channel.get('parameters')
                                if channelParams:
                                    tmpChannel.parameters=channelParams
                                    
                                    IPv4addr=findIPaddress(channelParams)
                                    if IPv4addr:
                                        tmpChannel.IPv4=IPv4addr
                                    else:
                                        COMnumber=findCOMnumber(channelParams)
                                        if COMnumber:
                                            tmpChannel.COMnumber=COMnumber


                                channelList.append(tmpChannel)  #append station channel list
                                
                tmpStation.channels=channelList
                asixStations.append(tmpStation) #Append global station list
                tmpStation=None
    #go deep, to child of a child
    for obj in child:
        readRecurse(obj)





def generateDiagramPyVis():
    # Tworzenie obiektu grafu
    graph = Network(select_menu=True,filter_menu=True)


    devices=[]

    #ADD NODES:
    for station in asixStations:
        #devices.append(station.name)
        graph.add_node(station.name,shape='image',image='img\Comp_img.png')
        for channel in station.channels:
            #Add Node if not exists already
            if not channel.name in devices:
                devices.append(channel.name)
                graph.add_node(channel.name,shape='image',image='img/PLC_img.png',title=channel.parameters)

    #ADD EDGES
    for station in asixStations:
        for channel in station.channels:
            #Add edge if not Network driver
            #if channel.driver!="network":
            if channel.driver=="network":
                graph.add_edge(station.name,channel.name,label=f"""{channel.driver}""",color="#353b48")
            elif len(channel.IPv4)>7:
                graph.add_edge(station.name,channel.name,label=f"""{channel.driver}""",color="#e1b12c")
            elif len(channel.COMnumber)>1:
                graph.add_edge(station.name,channel.name,label=f"""{channel.driver}""",color="#273c75")
            else:
                graph.add_edge(station.name,channel.name,label=f"""{channel.driver}""",color="#44bd32")
    #Show adjust buttons
    graph.force_atlas_2based()
    graph.show_buttons()

    # Save graph to file
    graph.show('asixConnections.html',notebook=False)


def exportToFile(fileName="sampleFile"):
    df=pandas.DataFrame()
    for station in asixStations:    #prepare pandas dataframe to export
        df=pandas.concat([df,pandas.DataFrame(station.to_dict())])  

    #print(df)
    df.to_excel(f"{fileName}.xlsx") #save to excel file

def printAsixStations():
    #print in console
    print("_____LISTA________")
    for asixStation in asixStations:
        print(asixStation)


def main():

    print(ASCIart)
    print("Ładowanie pliku xml")
    if len(sys.argv)>1:
        xmlFile=sys.argv[1]
        print(xmlFile)
        if os.path.isfile(xmlFile):
            xmlData=ET.parse(xmlFile)
            root=xmlData.getroot()
            #read all xml starting from main root and fill station array
            readRecurse(root)
            print("END")
        else:
            print(f"Problem z odczytaniem podanego pliku: {sys.argv[1]}")
            sys.exit()
    else:
        print('''Nie podano pliku wejściowego.
              Użycie:
              ./asixOLDparser.exe nazwa_pliku.xml
              lub:
              python asixOLDparser.py nazwa_pliku.xml''')
        sys.exit()

    

    runProgram=True
    while(runProgram):
        choice = input("""
1: Wyświetl dane odczytane z pliku.
2: Wygeneruj diagram pyvis
3: Eksport danych do pliku XML
4: Zakończ     
Wybór: """)
        
        if choice=="1":
            printAsixStations()
        elif choice=="2":
            generateDiagramPyVis()
        elif choice=="3":
            excelFile=input("Podaj proszę nazwę pliku wyjściowego bez rozszerzenia .xlsx: ")
            exportToFile(excelFile)
        elif choice=="4":
            sys.exit()



if __name__=="__main__":
    main()






