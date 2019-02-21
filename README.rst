HttpCtrl library for Robot Framework
====================================

**HttpCtrl** is a library for Robot Framework that provides HTTP/HTTPS client and server services.

**Version**: 0.0

**License**: GNU General Public License


Dependencies
============

**Python version**: >=3.4 (32, 64-bit)


Examples
========

Send POST request to HTTP server and check for negative response from it (403 Forbidden is expected).

.. code:: robot-framework

    *** Settings ***

    Library         Collections
    Library         OperatingSystem
    Library         HttpCtrl.Client

    Test Setup      Start HTTP Client

    *** Test Cases ***
    Start Task With Negative Expectation
        ${request body}=   Get File   data/start_task_json
        ${url}=            http://192.168.55.78:8080/server_api/v1/task

        Set Request Header    Content-Type   application/json-rpc
        Send HTTP Request     POST   ${url}   ${request body}

        ${response status}=   Get Response Status
        ${expected status}=   Convert To Integer   403
        Should Be Equal   ${response status}   ${expected status}

    *** Keywords ***
    Start HTTP Client
        Initialize Client   192.168.55.77   8000
