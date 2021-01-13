*** Settings ***

Library         HttpCtrl.Client
Library         HttpCtrl.Server

Library         Collections
Library         DateTime

*** Test Cases ***

Send Request Without Reply
    [Teardown]  Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    Send HTTP Request Async   POST   /post   Hello Server!

    Wait For Request

    ${message}=   Get Request Body
    Should Be Equal   ${message}   Hello Server!

    ${status}=   Get Response Status
    ${body}=     Get Response Body

    Should Be Equal   ${status}   ${None}
    Should Be Equal   ${body}     ${None}


Wait Request During 2 Seconds
    [Teardown]  Stop Server
    Start Server        127.0.0.1   8000

    ${start time}=     Get Current Date
    Run Keyword And Expect Error   *   Wait For Request   2
    ${end time}=       Get Current Date
    ${duration}=       Subtract Date From Date   ${end time}   ${start time}
    Should Be Equal As Numbers   ${2}   ${duration}   precision=1


Receive No Async Responses
    [Teardown]  Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    ${connection 1}=   Send HTTP Request Async   POST   /post   Post Message
    ${connection 2}=   Send HTTP Request Async   PUT    /put    Put Message

    ${response}=   Get Async Response   ${connection 1}
    Should Be Equal   ${response}   ${None}

    ${response}=   Get Async Response   ${connection 2}
    Should Be Equal   ${response}   ${None}


Receive Async For One Connection
    [Teardown]  Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    ${connection 1}=   Send HTTP Request Async   POST   /post   Post Message

    ${response}=   Get Async Response   ${connection 1}   1
    Should Be Equal   ${response}   ${None}

    Wait For Request
    Reply By   200   Post Response

    ${response}=   Get Async Response   ${connection 1}   1
    Should Not Be Equal   ${response}   ${None}


Receive Async For One Connection IPv6
    [Teardown]  Stop Server
    Initialize Client   0000:0000:0000:0000:0000:0000:0000:0001   42001
    Start Server        0000:0000:0000:0000:0000:0000:0000:0001   42001

    ${connection 1}=   Send HTTP Request Async   POST   /post   Post Message

    ${response}=   Get Async Response   ${connection 1}   1
    Should Be Equal   ${response}   ${None}

    Wait For Request
    Reply By   200   Post Response

    ${response}=   Get Async Response   ${connection 1}   1
    Should Not Be Equal   ${response}   ${None}


Receive Async Responses
    [Teardown]  Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    ${connection 1}=   Send HTTP Request Async   POST   /post   Post Message
    ${connection 2}=   Send HTTP Request Async   PUT    /put    Put Message

    Wait For Request
    Set Reply Header   Header-Key   Header-Value
    Reply By   200   Post Response

    Wait For Request
    Set Reply Header   Another-Key   Another-Value
    Reply by   201   Put Response

    ${response}=   Get Async Response   ${connection 1}   1
    Should Not Be Equal   ${response}   ${None}
    ${status}=     Get Status From Response    ${response}
    ${body}=       Get Body From Response      ${response}
    ${headers}=    Get Headers From Response   ${response}
    Should Be Equal   ${status}   ${200}
    Should Be Equal   ${body}     Post Response
    Dictionary Should Contain Item   ${headers}   Header-Key   Header-Value

    ${response}=   Get Async Response   ${connection 2}   1
    Should Not Be Equal   ${response}   ${None}
    ${status}=     Get Status From Response    ${response}
    ${body}=       Get Body From Response      ${response}
    ${headers}=    Get Headers From Response   ${response}
    Should Be Equal   ${status}   ${201}
    Should Be Equal   ${body}     Put Response
    Dictionary Should Contain Item   ${headers}   Another-Key   Another-Value

    ${response}=   Get Async Response   ${connection 1}
    Should Be Equal   ${response}   ${None}

    ${response}=   Get Async Response   ${connection 2}
    Should Be Equal   ${response}   ${None}


Receive Only One Async Response
    [Teardown]  Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    ${connection 1}=   Send HTTP Request Async   POST   /post   Post Message
    Sleep   200ms
    ${connection 2}=   Send HTTP Request Async   PUT    /put    Put Message

    Wait And Ignore Request

    Wait For Request
    Set Reply Header   Another-Key   Another-Value
    Reply by   201   Put Response

    ${response}=   Get Async Response   ${connection 1}   1
    Should Be Equal   ${response}   ${None}

    ${response}=   Get Async Response   ${connection 2}   1
    Should Not Be Equal   ${response}   ${None}
    ${status}=     Get Status From Response    ${response}
    ${body}=       Get Body From Response      ${response}
    ${headers}=    Get Headers From Response   ${response}
    Should Be Equal   ${status}   ${201}
    Should Be Equal   ${body}     Put Response
    Dictionary Should Contain Item   ${headers}   Another-Key   Another-Value

    ${response}=   Get Async Response   ${connection 1}
    Should Be Equal   ${response}   ${None}

    ${response}=   Get Async Response   ${connection 2}
    Should Be Equal   ${response}   ${None}
