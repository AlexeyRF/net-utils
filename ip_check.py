import requests
def get_ip():
    try:
        import stun
        _, ip, _ = stun.get_ip_info(stun_host='stun.l.google.com', stun_port=19302)
        return ip
    except: pass
    services = [
        'https://api.ipify.org',
        'https://checkip.amazonaws.com',
        'https://ipinfo.io/ip',
        'https://ifconfig.me/ip',
    ]
    for service in services:
        try:
            response = requests.get(service, timeout=3)
            if response.status_code == 200:
                ip = response.text.strip()
                return ip
        except: continue
    return None
