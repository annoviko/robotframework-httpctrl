*** Settings ***

Library         DateTime
Library         String
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


Reply by Bytes Body
    [Teardown]  Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    ${connection}=   Send HTTP Request Async   POST   /post   Post Message

    ${response}=   Get Async Response   ${connection}   1
    Should Be Equal   ${response}   ${None}

    ${body bytes}=   Evaluate   bytes((0x0a, 0x12, 0x0a))
    Wait For Request
    Reply By   200   ${body bytes}

    ${response}=   Get Async Response   ${connection}   1
    ${response body}=   Get Body From Response   ${response}
    ${response body bytes}=   Encode String To Bytes   ${response body}   UTF-8

    Should Be Equal   ${response body bytes}   ${body bytes}


Set Signle Stub And One Call
    [Teardown]   Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    Set Stub Reply   POST   /api/v1/post   200   Post Message

    Check Stub Statistic          POST   /api/v1/post   ${0}
    Send Request and Check Stub   POST   /api/v1/post   ${200}   Post Message   ${1}


Set Single Stub And Four Calls
    [Teardown]   Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    Set Stub Reply   POST   /api/v1/post   200   Post Message

    Check Stub Statistic          POST   /api/v1/post   ${0}

    FOR    ${index}    IN RANGE    1    5
        Send Request and Check Stub   POST   /api/v1/post   ${200}   Post Message   ${index}
    END


Set Two Stubs And Five Calls Consequentially
    [Teardown]   Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    Set Stub Reply   POST   /api/v1/post   202   Post Message
    Set Stub Reply   GET    /api/v1/get    201   Get Message

    Check Stub Statistic          POST   /api/v1/post   ${0}
    Check Stub Statistic          GET    /api/v1/get    ${0}

    FOR    ${index}    IN RANGE    1    6
        Send Request and Check Stub   POST   /api/v1/post   ${202}   Post Message   ${index}
        Check Stub Statistic          GET    /api/v1/get    ${0}
    END

    FOR    ${index}    IN RANGE    1    6
        Check Stub Statistic          POST   /api/v1/post   ${5}
        Send Request and Check Stub   GET    /api/v1/get    ${201}   Get Message    ${index}
    END


Set Two Stubs And Seven Calls Simultaneously
    [Teardown]   Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    Set Stub Reply   POST   /api/v1/post   202   Post Message
    Set Stub Reply   GET    /api/v1/get    201   Get Message

    Check Stub Statistic          POST   /api/v1/post   ${0}
    Check Stub Statistic          GET    /api/v1/get    ${0}

    FOR    ${index}    IN RANGE    1    8
        Send Request and Check Stub   POST   /api/v1/post   ${202}   Post Message   ${index}
        Send Request and Check Stub   GET    /api/v1/get    ${201}   Get Message    ${index}
    END


*** Keywords ***

Send Request and Check Stub
    [Arguments]   ${stub method}   ${stub url}   ${expected status}   ${expected body}   ${expected count}

    Send HTTP Request   ${stub method}   ${stub url}

    ${status}=     Get Response Status
    ${body}=       Get Response Body

    Should Be Equal   ${status}   ${expected status}
    Should Be Equal   ${body}     ${expected body}

    ${count}=      Get Stub Count   ${stub method}   ${stub url}

    Should Be Equal   ${count}   ${expected count}


Check Stub Statistic
    [Arguments]   ${stub method}   ${stub url}   ${expected count}

    ${count}=      Get Stub Count   ${stub method}   ${stub url}

    Should Be Equal   ${count}   ${expected count}
