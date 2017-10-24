from __future__ import print_function
import os

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/drive.file'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store, flags) \
            if flags else tools.run(flow, store)
DRIVE = build('drive', 'v2', http=creds.authorize(Http()))

FILES = (
    ('hello.txt', False),
    ('hello.txt', True),
)

for filename, convert in FILES:
    metadata = {'title': filename}
    res = DRIVE.files().insert(convert=convert, body=metadata,
            media_body=filename, fields='mimeType,exportLinks').execute()
    if res:
        print('Uploaded "%s" (%s)' % (filename, res['mimeType']))

if res:
    MIMETYPE = 'application/pdf'
    res, data = DRIVE._http.request(res['exportLinks'][MIMETYPE])
    if data:
        fn = '%s.pdf' % os.path.splitext(filename)[0]
        with open(fn, 'wb') as fh:
            fh.write(data)
        print('Downloaded "%s" (%s)' % (fn, MIMETYPE))

API_KEY = AIzaSyCzKjtPleu5tRGzOEYb0klqm48-blIISJw
#!/usr/bin/env python
