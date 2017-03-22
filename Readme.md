# FritzVoiceMail

A small script to crawl and convert voice-mail messages from a [FRITZ!Box](https://avm.de/produkte/fritzbox/) and deploy them to [Amazon Alexa](https://www.amazon.com/alexa). 

Specifically, when executed the script `crawl.sh` sends a SOAP request to the FRITZ!Box (using cURL to avoid any SOAP libraries for Python). When the result shows new voice-mail messages, these are downloaded and converted to MP3 (using [LAME](http://lame.sourceforge.net/) on CLI), such that they can be fed into the [Flash Briefing Skill](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/flash-briefing-skill-api-feed-reference) as RSS feed. 

The RSS feed is provided at `http://<host>/feed.rss` through [Python BaseHTTPServer](https://docs.python.org/2/library/basehttpserver.html) in `server.py`, which should be run on a machine that has local access to the FRITZ!box (through `https://fritz.box`).
