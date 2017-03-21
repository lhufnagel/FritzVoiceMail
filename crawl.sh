#!/bin/bash

curl -X POST -H "Content-Type: text/xml" \
    -H "SOAPAction: \"urn:dslforum-org:service:X_AVM-DE_TAM:1#GetMessageList\"" \
    --data-binary @request0.xml \
    --anyauth \
    --user user:pwd \
    http://fritz.box:49000/upnp/control/x_tam > response.xml
