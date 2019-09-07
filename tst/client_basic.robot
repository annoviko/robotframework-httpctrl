*** Settings ***

Library         HttpCtrl.Client
Library         HttpCtrl.Server

Library         HttpCtrl.Client
Library         Collections

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

    ${response}=   Get Async Response   ${connection 1}
    Should Not Be Equal   ${response}   ${None}
    ${status}=     Get Status From Response    ${response}
    ${body}=       Get Body From Response      ${response}
    ${headers}=    Get Headers From Response   ${response}
    Should Be Equal   ${status}   ${200}
    Should Be Equal   ${body}     Post Response
    Dictionary Should Contain Item   ${headers}   Header-Key   Header-Value

    ${response}=   Get Async Response   ${connection 2}
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

    ${response}=   Get Async Response   ${connection 1}
    Should Be Equal   ${response}   ${None}

    ${response}=   Get Async Response   ${connection 2}
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
