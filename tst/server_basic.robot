*** Settings ***

Library         HttpCtrl.Server


*** Test Cases ***

Start Stop Server
    Start Server   127.0.0.1   8000
    Stop Server


Double Server Start
    Start Server   127.0.0.1   8000
    Start Server   127.0.0.1   8001
    Stop Server