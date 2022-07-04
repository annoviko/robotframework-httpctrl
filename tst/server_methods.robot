*** Settings ***

Library         String

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
    ${body}=     Decode Bytes To String   ${body}   UTF-8

    Should Be Equal   ${method}   POST
    Should Be Equal   ${url}      /post
    Should Be Equal   ${body}     ${request body}


Receive And Reply To POST without Body
    Send HTTP Request Async   POST   /post

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body

    Should Be Equal   ${method}   POST
    Should Be Equal   ${url}      /post
    Should Be Equal   ${body}     ${None}


Receive And Reply To PUT
    ${request body}=   Set Variable   { "method": "PUT" }
    Send HTTP Request Async   PUT   /put   ${request body}

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body
    ${body}=     Decode Bytes To String   ${body}   UTF-8

    Should Be Equal   ${method}   PUT
    Should Be Equal   ${url}      /put
    Should Be Equal   ${body}     ${request body}


Receive And Reply To PUT without Body
    Send HTTP Request Async   PUT   /put

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body

    Should Be Equal   ${method}   PUT
    Should Be Equal   ${url}      /put
    Should Be Equal   ${body}     ${None}


Receive And Reply To PATCH
    ${request body}=   Set Variable   { "method": "PATCH" }
    Send HTTP Request Async   PATCH   /patch   ${request body}

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body
    ${body}=     Decode Bytes To String   ${body}   UTF-8

    Should Be Equal   ${method}   PATCH
    Should Be Equal   ${url}      /patch
    Should Be Equal   ${body}     ${request body}


Receive And Reply To PATCH without Body
    Send HTTP Request Async   PATCH   /patch

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body

    Should Be Equal   ${method}   PATCH
    Should Be Equal   ${url}      /patch
    Should Be Equal   ${body}     ${None}


Receive And Reply To GET
    Send HTTP Request Async   GET   /get

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url

    Should Be Equal   ${method}   GET
    Should Be Equal   ${url}      /get


Receive And Reply To GET with Body
    ${request body}=   Set Variable   { "method": "GET" }
    Send HTTP Request Async   GET   /get   ${request body}

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body
    ${body}=     Decode Bytes To String   ${body}   UTF-8

    Should Be Equal   ${method}   GET
    Should Be Equal   ${url}      /get
    Should Be Equal   ${body}     ${request body}


Receive And Reply To DELETE
    Send HTTP Request Async   DELETE   /delete

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url

    Should Be Equal   ${method}   DELETE
    Should Be Equal   ${url}      /delete


Receive And Reply To DELETE with Body
    ${request body}=   Set Variable   { "method": "DELETE" }
    Send HTTP Request Async   DELETE   /delete   ${request body}

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body
    ${body}=     Decode Bytes To String   ${body}   UTF-8

    Should Be Equal   ${method}   DELETE
    Should Be Equal   ${url}      /delete
    Should Be Equal   ${body}     ${request body}


Receive And Reply To HEAD
    Send HTTP Request Async   HEAD   /head

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url

    Should Be Equal   ${method}   HEAD
    Should Be Equal   ${url}      /head


Receive And Reply To HEAD with Body
    ${request body}=   Set Variable   { "method": "HEAD" }
    Send HTTP Request Async   HEAD   /head   ${request body}

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body
    ${body}=     Decode Bytes To String   ${body}   UTF-8

    Should Be Equal   ${method}   HEAD
    Should Be Equal   ${url}      /head
    Should Be Equal   ${body}     ${request body}


Receive And Reply To OPTIONS
    Send HTTP Request Async   OPTIONS   /options

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url

    Should Be Equal   ${method}   OPTIONS
    Should Be Equal   ${url}      /options


Receive And Reply To OPTIONS with Body
    ${request body}=   Set Variable   { "method": "OPTIONS" }
    Send HTTP Request Async   OPTIONS   /options   ${request body}

    Wait For Request
    Reply By   200

    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body
    ${body}=     Decode Bytes To String   ${body}   UTF-8

    Should Be Equal   ${method}   OPTIONS
    Should Be Equal   ${url}      /options
    Should Be Equal   ${body}     ${request body}


*** Keywords ***

Initialize HTTP Client And Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000


Terminate HTTP Server
    Stop Server