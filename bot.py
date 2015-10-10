import oauth2
import time
import requests
import json
import html2text
import re
import sys

# Default configurations
settings = {
    "site": "ntuosc",
    "pad_id": "l0rem1psum",
    "email": "contact@ntuosc.org",
    "hackpad_key": "Sh1BAArrR",
    "hackpad_secret": "W0wMUchseCure",
    "slack_url": "https://example.slack.com/api/incoming/webhook/url",
}

try:
    with open('settings.json', 'r') as f:
        new_settings = json.load(f)
        settings.update(new_settings)
except IOError:
    print('You should create your configuration file first')
    sys.exit(1)

api_method = "https://{site}.hackpad.com/api/1.0/pad/{pad_id}/revisions".format(**settings)


params = {
    'oauth_version': "1.0",
    'oauth_nonce': oauth2.generate_nonce(),
    'oauth_timestamp': int(time.time()),
    'email': settings['email'],
    'padId': settings['pad_id'],
}

comsumer = oauth2.Consumer(key=settings['hackpad_key'], secret=settings['hackpad_secret'])
params['oauth_consumer_key'] = comsumer.key
r = oauth2.Request(method='GET', url=api_method, parameters=params)
signature_method = oauth2.SignatureMethod_HMAC_SHA1()
r.sign_request(signature_method, comsumer, None)

def repl(m):
    name = m.group(1)
    link = m.group(2)
    s = "<"+link+"|"+name+">"
    return s.replace('\n','')

lastTimeStamp = 0
serial = False
while True:
    time.sleep(60)
    res = requests.get(r.to_url())
    j = json.loads(res.text)
    timeStamp = j[0]['timestamp']
    if timeStamp != lastTimeStamp and not serial:
        serial = True
        md = html2text.html2text(j[0]['htmlDiff'])
        f = open('../public_html/hack.html', 'w')
        p = re.compile(r"\[(.+?)\]\((.+?)\)", re.DOTALL)
        md = re.sub(p, repl, md)
        md = md.replace(" * ",":ballot_box_with_check:")
        md = md.replace("\n", "", 1)
        f.write(md)
        
        payload = {
            "channel": "#administration",
            "username": "hackpadbot",
            "text": md,
            "mrkdwn": "true",
            "icon_url": j[0]['authorPics'][0]
        }
        
        requests.post(settings['slack_url'], data=json.dumps(payload))
        lastTimeStamp = timeStamp
    else:
        serial = False
