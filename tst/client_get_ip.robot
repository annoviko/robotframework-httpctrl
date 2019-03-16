*** Settings ***

Library         HttpCtrl.Client
Library         HttpCtrl.Json


*** Test Cases ***

Get Origin Address
    Initialize Client   www.httpbin.org
    Send HTTP Request   GET   /ip

    ${response status}=   Get Response Status
    ${response body}=     Get Response Body

    ${expected status}=   Convert To Integer   200
    Should Be Equal   ${response status}   ${expected status}

    ${origin}=    Get Json Value From String   ${response body}   origin
    Should Not Be Empty   ${origin}


Get Origin Using Wrong URL
    Initialize Client   www.httpbin.org
    Send HTTP Request   GET   /some_wrong_url

    ${response status}=   Get Response Status

    ${expected status}=   Convert To Integer   404
    Should Be Equal   ${response status}   ${expected status}