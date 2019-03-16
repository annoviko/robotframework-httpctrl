*** Settings ***

Library         HttpCtrl.Client
Library         HttpCtrl.Json


*** Test Cases ***

Send HTTP POST Request
    Initialize Client   www.httpbin.org

    ${body}=   Set Variable   { "message": "Hello World!" }
    Send HTTP Request   POST   /post   ${body}

    ${response status}=   Get Response Status
    ${response body}=     Get Response Body

    ${expected status}=   Convert To Integer   200
    Should Be Equal   ${response status}   ${expected status}

    ${message}=    Get Json Value From String   ${response body}   data
    Should Be Equal   ${message}   ${body}


Send HTTPS PATCH Request
    Initialize Client   www.httpbin.org

    ${body}=   Set Variable   { "volume": 77, "mute": false }
    Send HTTPS Request   PATCH   /patch   ${body}

    ${response status}=   Get Response Status
    ${response body}=     Get Response Body

    ${expected status}=   Convert To Integer   200
    Should Be Equal   ${response status}   ${expected status}

    ${volume}=   Get Json Value From String   ${response body}   json/volume
    Should Be Equal   ${volume}   ${77}

    ${mute}=   Get Json Value From String   ${response body}   json/mute
    Should Be Equal   ${mute}   ${False}


Send HTTP GET Request
    Initialize Client   www.httpbin.org

    Send HTTPS Request   GET   /get
    ${response status}=   Get Response Status

    Should Be Equal   ${response status}   ${200}


Send HTTP PUT Request
    Initialize Client   www.httpbin.org

    ${body}=   Set Variable   { "message": "Welcome!" }
    Send HTTPS Request   PUT   /put   ${body}

    ${response status}=   Get Response Status
    ${response body}=     Get Response Body

    Should Be Equal   ${response status}   ${200}
    ${data}=   Get Json Value From String   ${response body}   data
    Should Be Equal   ${data}   ${body}


Send HTTP DELETE Request
    Initialize Client   www.httpbin.org

    ${body}=   Set Variable   { "file": "file1.txt" }
    Send HTTPS Request   DELETE   /delete   ${body}

    ${response status}=   Get Response Status
    Should Be Equal   ${response status}   ${200}
