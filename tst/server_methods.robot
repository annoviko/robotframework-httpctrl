*** Settings ***

Library         HttpCtrl.Client
Library         HttpCtrl.Server

Test Setup       Initialize HTTP Client And Server
Test Teardown    Terminate HTTP Server


*** Test Cases ***

Receive And Reply To POST
    ${request body}=   Set Variable   { "method": "POST" }
    Send HTTP Request Async   POST   /post   ${request body}

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body

    Should Be Equal   ${method}   POST
    Should Be Equal   ${url}      /post
    Should Be Equal   ${body}     ${request body}


Receive And Reply To PUT
    ${request body}=   Set Variable   { "method": "PUT" }
    Send HTTP Request Async   PUT   /put   ${request body}

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body

    Should Be Equal   ${method}   PUT
    Should Be Equal   ${url}      /put
    Should Be Equal   ${body}     ${request body}


Receive And Reply To PATCH
    ${request body}=   Set Variable   { "method": "PATCH" }
    Send HTTP Request Async   PATCH   /patch   ${request body}

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body

    Should Be Equal   ${method}   PATCH
    Should Be Equal   ${url}      /patch
    Should Be Equal   ${body}     ${request body}


Receive And Reply To GET
    Send HTTP Request Async   GET   /get

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url

    Should Be Equal   ${method}   GET
    Should Be Equal   ${url}      /get


Receive And Reply To DELETE
    Send HTTP Request Async   DELETE   /delete

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url

    Should Be Equal   ${method}   DELETE
    Should Be Equal   ${url}      /delete


Receive And Reply To HEAD
    Send HTTP Request Async   HEAD   /head

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url

    Should Be Equal   ${method}   HEAD
    Should Be Equal   ${url}      /head


Receive And Reply To OPTIONS
    Send HTTP Request Async   OPTIONS   /options

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url

    Should Be Equal   ${method}   OPTIONS
    Should Be Equal   ${url}      /options


*** Keywords ***

Initialize HTTP Client And Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000


Terminate HTTP Server
    Stop Server