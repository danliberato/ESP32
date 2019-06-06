import network

class Connection:
    
    ap = network.WLAN(network.AP_IF)
    nic = network.WLAN(network.STA_IF)
    
    def __init__(self):
        pass
    
    def startWlanClient(self,name, psw):
        self.nic.active(True)
        self.nic.connect(name, psw)
        if self.nic.isconnected():
            print('Connected to Wi-Fi: ' + name + ' ('+self.nic.ifconfig()[0]+')')
    
    def stopWlanClient(self):
        self.nic.stop()
        
    def startAP(self,name, psw):
        self.ap.config(essid=name, authmode=4, password=psw)
        self.ap.active(True)
        
    def stopAP(self):
        self.ap.active(False)