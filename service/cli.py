#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import requests

url = 'http://127.0.0.1:8080/upload2'
files = {'ufile': open('../data/CS_H.inp', 'rb')}

r = requests.post(url, files=files)

print(r)
print(r.text)