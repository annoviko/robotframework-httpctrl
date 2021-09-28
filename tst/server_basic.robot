*** Settings ***

Library         DateTime
Library         HttpCtrl.Client
Library         HttpCtrl.Server


*** Test Cases ***

Start Stop Server
    Start Server   127.0.0.1   8000
    Stop Server


Double Server Start
    Start Server   127.0.0.1   8000
    Start Server   127.0.0.1   8001
    Stop Server


Empty Queue after Server Stop
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    Send HTTP Request Async   POST   /post   Hello Server!
    Stop Server

    Start Server        127.0.0.1   8000
    ${start time}=   Get Current Date
    Wait For No Request   2
    ${end time}=     Get Current Date
    ${duration}=     Subtract Date From Date   ${end time}   ${start time}
    Should Be Equal As Numbers   ${2}   ${duration}   precision=1

    Stop Server


No Requests During 1 Second
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    ${start time}=   Get Current Date
    Wait For No Request   1
    ${end time}=     Get Current Date
    ${duration}=     Subtract Date From Date   ${end time}   ${start time}
    Should Be Equal As Numbers   1   ${duration}   precision=1

    Stop Server


Server Receives Two Messages at Once
    [Teardown]  Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    ${connection 1}=   Send HTTP Request Async   POST   /post   Message to Post
    ${connection 2}=   Send HTTP Request Async   PUT    /put    Message to Put

    Wait For Request
    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body
    Should Be Equal   ${method}   POST
    Should Be Equal   ${url}      /post
    Should Be Equal   ${body}     Message to Post
    Reply By          200

    Wait For Request
    ${method}=   Get Request Method
    ${url}=      Get Request Url
    ${body}=     Get Request Body
    Should Be Equal   ${method}   PUT
    Should Be Equal   ${url}      /put
    Should Be Equal   ${body}     Message to Put
    Reply By          201

    Sleep   200ms

    ${response 1}=   Get Async Response   ${connection 1}
    ${response 2}=   Get Async Response   ${connection 2}

    ${response status}=   Get Status From Response   ${response 1}
    ${expected status}=   Convert To Integer   200
    Should Be Equal   ${response status}   ${expected status}

    ${response status}=   Get Status From Response   ${response 2}
    ${expected status}=   Convert To Integer   201
    Should Be Equal   ${response status}   ${expected status}


Response Body
    [Teardown]  Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    ${connection}=   Send HTTP Request Async   POST   /post   Post Message

    ${response}=   Get Async Response   ${connection}   1
    Should Be Equal   ${response}   ${None}

    Wait For Request
    Reply By   200   Post Response

    ${response}=   Get Async Response   ${connection}   1
    ${response status}=   Get Status From Response   ${response}
    ${response reason}=   Get Reason From Response   ${response}

    Should Be Equal   ${response status}    ${200}
    Should Be Equal   ${response reason}    OK
