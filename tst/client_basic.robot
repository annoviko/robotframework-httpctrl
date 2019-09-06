*** Settings ***

Library         HttpCtrl.Client
Library         HttpCtrl.Server


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
