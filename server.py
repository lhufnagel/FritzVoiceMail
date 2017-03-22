#!/usr/bin/env python
"""
Very simple HTTP server in python.
Usage::
    ./server.py [<port>]
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer

from xml.dom import minidom
from urllib import urlopen
from datetime import datetime
import uuid
import sys, os
import ssl

def downloadMp3(path):
    #download and convert to mp3
    recording = path[19:]

    download = 'http://fritz.box/lua/photo.lua?sid=' + sid + '&myabfile=' + recording
    myfile =  urlopen(download)
    with open('temp.wav','wb') as output:
        output.write(myfile.read())

    os.system('lame -b 256 temp.wav ./'+ guid + '.mp3')

def printFeed(s):
    #print rss feed

    #get correct voicemail adress + session id from fritz.box
    os.system('./crawl.sh')
    xmldoc = minidom.parse('./response.xml')
    itemlist = xmldoc.getElementsByTagName('NewURL')

    response = '<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel><ttl>30</ttl>'

    if 0  == len(itemlist):
        response = response + '</channel></rss>'
        s.wfile.write(response)
        exit

    url = itemlist[0].childNodes[0].nodeValue
    sid = url[47:-11];

    #get list of messages for that voicemail
    dom = minidom.parse(urlopen(url))

    for message in dom.getElementsByTagName('Message'):
        #set name of caller
        fromName = 'Unknown'
        names = message.getElementsByTagName('Name')
        if len(names) > 0:
            fromName = names[0].childNodes[0].nodeValue
        else:
            #if name not known, user caller-number
            numbers = message.getElementsByTagName('Number')
            if len(numbers) > 0:
                fromName = numbers[0].childNodes[0].nodeValue

        timestamp = message.getElementsByTagName('Date')[0].childNodes[0].nodeValue
        datetime_object = datetime.strptime(timestamp, '%d.%m.%y %H:%M')
        
        guid = str(uuid.uuid5(uuid.NAMESPACE_URL, (timestamp+fromName).encode("ascii","ignore")))

        if not os.path.isfile("./"+ guid +".mp3"): 
            path = message.getElementsByTagName('Path')[0].childNodes[0].nodeValue
            downloadMp3(path)

        size = os.path.getsize("./"+ guid +".mp3")

        rss_item = '<item><guid>urn:uuid:' + guid + '</guid><title>Call from ' + \
            fromName + '</title><description> You have a voice message from ' + \
            fromName + ' on ' + datetime_object.ctime() +  \
            '</description><link>https://www.amazon.de</link><pubDate>' + \
            datetime_object.isoformat("T") + \
            '.0Z</pubDate><enclosure url="https://s3.eu-central-1.amazonaws.com/fritzvoice/' + guid + \
            '.mp3" length="' + str(size) + '" type="audio/mpeg" /></item>'

        response = response + rss_item

    response = response + '</channel></rss>'

    s.wfile.write(response)

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/rss+xml')
        self.end_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("Prost!")

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        if '/feed.rss' == self.path:
            self._set_headers()
            printFeed(self)
        elif len(self.path) > 5 and '.mp3' == self.path[-4:]:
            self.send_response(200)
            self.send_header('Content-type', 'audio/mpeg')
            self.end_headers()

            # todo sanitize path better!
            if not os.path.isfile('.' + self.path) or \
                    os.path.normpath(self.path) != self.path: 
                print "File not found!"
                f = open('./fail.mp3', 'rb')
                self.wfile.write(f.read())
            else:
                f = open('.' + self.path, 'rb')
                self.wfile.write(f.read())
            
        else:
            self.wfile.write("Nope!")


        
        
def run(server_class=HTTPServer, handler_class=S, port=1234):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    #httpd.socket = ssl.wrap_socket (httpd.socket, certfile='/pathto/server.crt', keyfile='/pathto/server.key', server_side=True)
    
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

