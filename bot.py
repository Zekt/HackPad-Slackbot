import oauth2
import time
import requests
import json
import html2text
import re

SITE = ""
padID = ""
email = ""
hackpadKey = ""
hackpadSecret = ""

slackURL = ""

api_method = "https://"+SITE+".hackpad.com/api/1.0/pad/"+padID+"/revisions"


params = {
    'oauth_version': "1.0",
    'oauth_nonce': oauth2.generate_nonce(),
    'oauth_timestamp': int(time.time()),
    'email': email,
    'padId': padID
}

comsumer = oauth2.Consumer(key=hackpadKey, secret=hackpadSecret)
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
        
        requests.post(slackURL, data=json.dumps(payload))
        lastTimeStamp = timeStamp
    else:
        serial = False
