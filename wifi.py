"""
    upython-turnstile.wifi
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Description
    
    :copyright: (c) 2018 by Cooperativa de Trabajo BITSON Ltda..
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.com.ar>.
    :license: AGPL, see LICENSE for more details.
"""
# Standard lib imports
# Third-party imports
# BITSON imports


def connect_to(ssid='ThiagoBenjamin', password=None):
    from network import WLAN, STA_IF
    wlan = WLAN(STA_IF)
    if not wlan.isconnected():
        print('Connecting to {}'.format(ssid))
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
        print('Connected!')
        print('Network Config: {}'.format(wlan.ifconfig()))
