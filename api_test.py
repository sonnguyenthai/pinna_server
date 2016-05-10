# -*- coding: utf-8 -*-

import requests

def test_upload():
    data = {}
    data['genre'] = "2"
    data['mood'] = "1"
    data['author'] = "Linkin Park"
    data['duration'] = 120102
    data['artist'] = 'Linkin Park'
    data['name'] = 'khinh vu phi duong'
    data['hashtags'] = 'test5, test6'
    data['bpm'] = 128

    files = {'file': open('/Users/wisekey/Music/numb.mp3', 'rb')}

    headers = {}
    headers['PINNA_APPLICATION_ID'] = "abc"
    headers['PINNA_APPLICATION_KEY'] = "1234"
    headers['PINNA_AUTHENTICATED_TOKEN'] = "5ede18af159d597e7a785ddb0f8a55fc85f88522"

    url = "http://127.0.0.1:8000/api/music/upload"

    req = requests.post(url, data=data, headers=headers, files=files)
    print req.text
    print req.json().get('url')

def test_update_profile():
    headers = {}
    headers['PINNA_APPLICATION_ID'] = "abc"
    headers['PINNA_APPLICATION_KEY'] = "1234"
    headers['PINNA_AUTHENTICATED_TOKEN'] = "fa529f6c01d3145570ded19e4b5db82f81229e8f"

    data = {}
    data['firstname'] = "SOn"
    data['lastname'] = "Nguyen"

    files = {'photo': open('/Users/wisekey/Music/avatar.jpg', 'rb')}

    url = "http://127.0.0.1:8000/api/user/update"

    req = requests.put(url, data=data, headers=headers, files=files)
    print req.text

def test_get_profile():
    headers = {}
    headers['PINNA_APPLICATION_ID'] = "abc"
    headers['PINNA_APPLICATION_KEY'] = "1234"
    headers['PINNA_AUTHENTICATED_TOKEN'] = "fa529f6c01d3145570ded19e4b5db82f81229e8f"


    url = "http://127.0.0.1:8000/api/user/profile"

    req = requests.get(url,headers=headers)
    print req.text

def update_track():
    data = {}
    data['genre'] = "3"
    data['mood'] = "2"
    data['name'] = 'Numb Linkin-Park'
    data['hashtags'] = 'test1, test2, test3'
    data['bpm'] = 240


    headers = {}
    headers['PINNA_APPLICATION_ID'] = "abc"
    headers['PINNA_APPLICATION_KEY'] = "1234"
    headers['PINNA_AUTHENTICATED_TOKEN'] = "92203d8ad53870bb980cef6281305ed7a38ee786"

    url = "http://127.0.0.1:8000/api/music/3"

    req = requests.put(url,data=data, headers=headers)
    print req.text

def create_station():
    data = {}
    data['genre'] = "2"
    data['mood'] = "1"
    data['name'] = 'Station 12'
    data['hashtags'] = 'test2, test1, test3'
    data['bpm'] = "120, 600"

    files = {'photo': open('/Users/wisekey/Music/job_sample.png', 'rb')}

    headers = {}
    headers['PINNA_APPLICATION_ID'] = "abc"
    headers['PINNA_APPLICATION_KEY'] = "1234"
    headers['PINNA_AUTHENTICATED_TOKEN'] = "5a2e5cb1678df325818fad3b5c34e439a42f060a"

    url = "http://127.0.0.1:8000/api/music/station/create"
    url2 = "http://172.16.181.132:8080/api/music/station/create"
    req = requests.post(url,data=data,files=files, headers=headers)
    print req.text

def update_pr():
    data = {}
    data['display_name'] = 'THanh Quan'

    files = {'photo': open('/Users/wisekey/Music/avatar.jpg', 'rb')}

    headers = {}
    headers['PINNA_APPLICATION_ID'] = "abc"
    headers['PINNA_APPLICATION_KEY'] = "1234"
    headers['PINNA_AUTHENTICATED_TOKEN'] = "5a2e5cb1678df325818fad3b5c34e439a42f060a"

    url = "http://127.0.0.1:8000/api/user/update"
    url2 = "http://172.16.181.132:8080/api/user/update"
    req = requests.post(url,data=data,files=files, headers=headers)
    print req.text

#create_station()
#os.environ['DJANGO_SETTINGS_MODULE'] = 'evenresponse.settings'


PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4qSfI6gQ/T6YtGUSaQF4l7bUr+JFkAwACVCv9q33+2MfPYqnIcoWbdluULmjy9ieGOATYzT++pcPyeJz5kcLaGuxAQUsdxW6nsvkErtQAkXkXldsqWGBtCgdcR6czpOIhiqQ9jvXv7t+fYCoAXzjI2ShCSJvtVCG8k8r5WH1q/Vy+7tuwTmq+CvpEQoBKwHLPk7DflyOJPnPldLW9N8yjG+52fciew0899dycvw+yDxmiYh5t6qg/MX9hwzQ0QNjsQDcAOIathWgXSym/8dmVZ+umJwnwh6rf52albAZhK+ul3api/jeI4NxDn7OeSkIMrdh076A2WlbUS2c6mgr8QIDAQAB'
MSG = {"orderId":"12999763169054705758.1317948987830858","packageName":"com.pinna.onlineradio","productId":"pinna_purchase_coins","purchaseTime":1416280900660,"purchaseState":0,"developerPayload":"PINNA_WISEKEY_INAPP_PAYLOAD","purchaseToken":"fcnfdeadclfmdkhiphiefadg.AO-J1Oz0ZviakZhtNteItQCp9JNqvJK7PJpHsHCBbsdBk-9GPh5evsY1DP6cSj7Qaj-AYQuDV0uLHexmMQ-UBKcyQxyNDgIxg_kgLQoKevsk_GiozXhpHatvBYAB-qzkuwobkhNvSVL2"}

SIG = "rTWXL1n3D6nHqseF+xGz/mzDFryDey9NGQ9GWcSyqo9462+Sfq2MpeW0mZO86l3+YCJO4ZprSpIHjmSDbPNwCmwgSRqQaaVzJDvV4dNAL7YD+NGZSElPRTBQoxHNJPd7d/ir/y8ATK3dxdrYNd11jVdE/rvXZm6Oj9692eZcYaksyPx5KwRQGQK6iMvdHR10rDWDfmIH4zMN2o0sv3SHUzbRnoymwISOIrLyau9Tst0CSZKTYETeIVtvJem4nq3yvmvi0du5K9/3yMazd+ljHFKvHO8zgl+IUXfCq1YRy+8M2OhwAlbrAeb3A54ZI3KrAtbWwfmlU88o/tZLuZscxA=="

import base64
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

# Your base64 encoded public key from Google Play.
_PUBLIC_KEY_BASE64 = PUBLIC_KEY
# Key from Google Play is a X.509 subjectPublicKeyInfo DER SEQUENCE.
_PUBLIC_KEY = RSA.importKey(base64.standard_b64decode(_PUBLIC_KEY_BASE64))


def verify(signed_data, signature_base64):
    """Returns whether the given data was signed with the private key."""

    h = SHA.new()
    h.update(signed_data)
    # Scheme is RSASSA-PKCS1-v1_5.
    _PUBLIC_KEY = RSA.importKey(base64.standard_b64decode(_PUBLIC_KEY_BASE64))
    verifier = PKCS1_v1_5.new(_PUBLIC_KEY)
    # The signature is base64 encoded.
    signature = base64.standard_b64decode(signature_base64)
    return verifier.verify(h, signature)

msg = '{"orderId":"12999763169054705758.1317948987830858","packageName":"com.pinna.onlineradio","productId":"pinna_purchase_coins","purchaseTime":1416280900660,"purchaseState":0,"developerPayload":"PINNA_WISEKEY_INAPP_PAYLOAD","purchaseToken":"fcnfdeadclfmdkhiphiefadg.AO-J1Oz0ZviakZhtNteItQCp9JNqvJK7PJpHsHCBbsdBk-9GPh5evsY1DP6cSj7Qaj-AYQuDV0uLHexmMQ-UBKcyQxyNDgIxg_kgLQoKevsk_GiozXhpHatvBYAB-qzkuwobkhNvSVL2"}'

def test_add_coins():
    url = 'http://127.0.0.1:8000/api/user/add_coins'
    headers = {}
    headers['PINNA_APPLICATION_ID'] = "abc"
    headers['PINNA_APPLICATION_KEY'] = "1234"
    headers['PINNA_AUTHENTICATED_TOKEN'] = "589de62b2880fd35048f47a616ccf06450ac25d9"

    data = {}
    data['coins'] = 1000
    data['signature'] = SIG
    data['purchase_data'] = msg

    req = requests.post(url, data=data, headers=headers)
    print req.text

test_add_coins()