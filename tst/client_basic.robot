*** Settings ***

Library         HttpCtrl.Client
Library         HttpCtrl.Server
Library         HttpCtrl.Json

Library         Collections
Library         DateTime
Library         OperatingSystem


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


Bind Client to Address and Port
    [Teardown]  Stop Server
    Initialize Client   127.0.0.1   8000   127.0.0.1   8001
    Start Server        127.0.0.1   8000

    ${connection}=   Send HTTP Request Async   POST   /post   Post Message

    ${response}=   Get Async Response   ${connection}   1
    Should Be Equal   ${response}   ${None}

    Wait For Request

    ${source address}=   Get Request Source Address
    ${source port}=      Get Request Source Port
    ${source port as integer}=   Get Request Source Port As Integer

    Should Be Equal   ${source address}   127.0.0.1
    Should Be Equal   ${source port}      8001
    Should Be Equal   ${source port as integer}   ${8001}


Bind Client to Address Only
    [Teardown]  Stop Server
    Initialize Client   127.0.0.1   8000   127.0.0.1
    Start Server        127.0.0.1   8000

    ${connection}=   Send HTTP Request Async   POST   /post   Post Message

    ${response}=   Get Async Response   ${connection}   1
    Should Be Equal   ${response}   ${None}

    Wait For Request

    ${source address}=   Get Request Source Address

    Should Be Equal   ${source address}   127.0.0.1


Read Response Body to File
    [Teardown]  Stop Server
    Initialize Client   www.httpbin.org

    ${body content}=   Set Variable   Sync Response Body in File
    ${filename}=       Set Variable   sync_resp_body.txt

    Send HTTP Request   POST   /post   ${body content}   resp_body_to_file=${filename}

    ${response status}=   Get Response Status
    Should Be Equal   ${response status}   ${200}

    File Should Exist          ${filename}
    File Should Not Be Empty   ${filename}

    ${response body}=   Get Response Body
    ${data node}=       Get Json Value From String   ${response body}   data
    Should Be Equal     ${data node}   ${body content}

    Remove File   ${filename}


Read Response Body with PNG to File
    [Teardown]  Stop Server
    Initialize Client   www.httpbin.org

    ${filename}=       Set Variable   random_image.png

    Send HTTP Request   GET   /image/png   resp_body_to_file=${filename}

    ${response status}=   Get Response Status
    Should Be Equal   ${response status}   ${200}

    File Should Exist          ${filename}
    File Should Not Be Empty   ${filename}

    Remove File   ${filename}


Read Response Body with PNG to RAM
    [Teardown]  Stop Server
    Initialize Client   www.httpbin.org

    ${filename}=       Set Variable   random_image.png

    Send HTTP Request   GET   /image/png

    ${response status}=   Get Response Status
    ${response body}=     Get Response Body

    Should Not Be Equal   ${response body}     ${None}
    Should Be Equal       ${response status}   ${200}


Read Response Body to File Async
    [Teardown]  Stop Server
    Initialize Client   127.0.0.1   8000
    Start Server        127.0.0.1   8000

    ${body content}=   Set Variable   Async Response Body in File
    ${filename}=       Set Variable   async_resp_body.txt

    ${connection}=   Send HTTP Request Async   GET   /get   resp_body_to_file=${filename}

    Wait For Request
    
    Reply By   200   ${body content}

    ${response}=   Get Async Response   ${connection}   1

    File Should Exist          ${filename}
    File Should Not Be Empty   ${filename}

    Should Not Be Equal   ${response}   ${None}
    ${body}=       Get Body From Response      ${response}

    Should Be Equal   ${body content}   ${body}

    Remove File   ${filename}
