|Build Status Linux|

HttpCtrl library for Robot Framework
====================================

**HttpCtrl** is a library for Robot Framework that provides HTTP/HTTPS client and HTTP server services to make
REST API testing easy.

**Version**: 0.1.0

**Author**: Andrei Novikov

**License**: GNU General Public License


Dependencies
============

**Python version**: >=3.4


Examples
========

Send GET request to obtain origin IP address and check that is not empty:

.. code:: robot-framework

    *** Settings ***

    Library         HttpCtrl.Client
    Library         HttpCtrl.Json

    *** Test Cases ***

    Get Origin Address
        Initialize Client   www.httpbin.org
        Send HTTP Request   GET   /ip

        ${response status}=   Get Response Status
        ${response body}=     Get Response Body

        ${expected status}=   Convert To Integer   200
        Should Be Equal   ${response status}   ${expected status}

        ${origin}=    Get Json Value From String   ${response body}   origin
        Should Not Be Empty   ${origin}


Send POST request and extract required information from response:

.. code:: robot-framework

    *** Settings ***

    Library         HttpCtrl.Client
    Library         HttpCtrl.Json

    *** Test Cases ***

    Send POST Request
        Initialize Client   www.httpbin.org

        ${body}=   Set Variable   { "message": "Hello World!" }
        Send HTTP Request   POST   /post   ${body}

        ${response status}=   Get Response Status
        ${response body}=     Get Response Body

        ${expected status}=   Convert To Integer   200
        Should Be Equal   ${response status}   ${expected status}

        ${message}=    Get Json Value From String   ${response body}   data
        Should Be Equal   ${message}   ${body}


Send PATCH request using HTTPS protocol:

.. code:: robot-framework

    *** Settings ***

    Library         HttpCtrl.Client
    Library         HttpCtrl.Json

    *** Test Cases ***

    Send HTTPS PATCH Request
        Initialize Client   www.httpbin.org

        ${body}=   Set Variable   { "volume": 77, "mute": false }
        Send HTTPS Request   PATCH   /patch   ${body}

        ${response status}=   Get Response Status
        ${response body}=     Get Response Body

        ${expected status}=   Convert To Integer   200
        Should Be Equal   ${response status}   ${expected status}

        ${volume}=   Get Json Value From String   ${response body}   json/volume
        Should Be Equal   ${volume}   ${77}

        ${mute}=   Get Json Value From String   ${response body}   json/mute
        Should Be Equal   ${mute}   ${False}


In this example HTTP client sends POST request to HTTP server. HTTP server receives it and checks incoming
request for correctness.

.. code:: robotframework

    *** Settings ***

    Library         HttpCtrl.Client
    Library         HttpCtrl.Server

    Test Setup       Initialize HTTP Client And Server
    Test Teardown    Terminate HTTP Server

    *** Test Cases ***

    Receive And Reply To POST
        ${request body}=   Set Variable   { "message": "Hello!" }
        Send HTTP Request Async   POST   /post   ${request body}

        Wait For Request
        Reply By   200

        ${method}=   Get Request Method
        ${url}=      Get Request Url
        ${body}=     Get Request Body

        Should Be Equal   ${method}   POST
        Should Be Equal   ${url}      /post
        Should Be Equal   ${body}     ${request body}

    *** Keywords ***

    Initialize HTTP Client And Server
        Initialize Client   127.0.0.1   8000
        Start Server        127.0.0.1   8000

    Terminate HTTP Server
        Stop Server


.. |Build Status Linux| image:: https://travis-ci.org/annoviko/robotframework-httpctrl.svg?branch=master
   :target: https://travis-ci.org/annoviko/https://travis-ci.org/annoviko/robotframework-httpctrl