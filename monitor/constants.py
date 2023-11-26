import pywifi

PING_HOSTS = [
    '8.8.8.8', # Google 
    '208.67.222.222', # OpenDNS
    '172.66.40.38' # Hostgator
]

HOSTGATOR = '172.66.40.38'

INTERFACE_PADRAO = pywifi.PyWiFi().interfaces()[0]
INTERFACE_PADRAO.scan()
INTERFACE_GUID = INTERFACE_PADRAO._raw_obj.get('guid', '')