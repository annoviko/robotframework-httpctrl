*** Settings ***

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
    Wait For No Requests   2
    Stop Server