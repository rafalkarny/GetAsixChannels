

class asixStation:
    name="stationName"
    channels=[]


    def __init__(self,name="stationName",channels=[]):
        self.name=name
        self.channels=channels
        

    def __str__(self) -> str:
        stringFormat=f'''_________________________________________
        {self.name} :
        '''
        for channel in self.channels:
            stringFormat+=f"\n{str(channel)}"

        return stringFormat
    
    def to_dict(self):
        channelsListOfDict=[]
        for channel in self.channels:
            channelDictObj=channel.to_dict()
            channelDictObj["Nazwa_stacji"]=self.name
            channelsListOfDict.append(channelDictObj)
        return channelsListOfDict


class asixChannel:
    name=""
    driver=""
    parameters=""
    active=True
    IPv4=""
    COMnumber=""

    def __init__(self,name="channelName",driver="undefined",parameters="",active=True,IPv4="",COMnumber=""):
        self.name=name
        self.driver=driver
        self.parameters=parameters
        self.active=active
        self.IPv4=IPv4
        self.COMnumber=COMnumber

    def __str__(self) -> str:
        stringFormat=f'''
        Channel name: {self.name}
        \tDriver: {self.driver}
        \tParameters: {self.parameters}
        \tActive: {str(self.active)}
        \tIPv4: {self.IPv4}
        \tCOM port: {self.COMnumber}
        '''
        return stringFormat
    
    def to_dict(self):
        return {
            'Nazwa': self.name,
            'Drajwer': self.driver,
            'Parametry':self.parameters,
            'IP': self.IPv4,
            'COM': self.COMnumber
        }

class diagramObj:
    name=""
    channelList=[]

    def __init__(self,name, channelList):
        self.name=name
        self.channelList=channelList


class asixEdge:
    to=""
    source=""
    label=""

    def __init__(self,to="to",source="source",label="label") -> None:
        self.to=to
        self.source=source
        self.label=label