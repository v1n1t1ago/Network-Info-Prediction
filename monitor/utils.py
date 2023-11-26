from django.conf import settings

def humanize_network(speed):
    speed_mbps = speed / 1_000_000
    if speed_mbps>1:
         return f"{speed_mbps} Mbps" 
    return f"{speed / 1_000} Kbps"

     
def ignore_keys(d, keys):
    return {k: d[k] for k in d.keys() - keys}
