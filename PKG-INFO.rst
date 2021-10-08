HttpCtrl library for Robot Framework
====================================

**RobotFramework-HttpCtrl** is a library for Robot Framework that provides HTTP/HTTPS client and HTTP (IPv4 and IPv6) server services
to make REST API testing easy.

**License**: The 3-Clause BSD License

**Documentation**: https://annoviko.github.io/robotframework-httpctrl/


Dependencies
============

**Python version**: >=3.4


Installation
============

Installation using pip3 tool:

.. code:: bash

    $ pip3 install robotframework-httpctrl


Brief Overview of the Library Content
=====================================

**HttpCtrl** contains following general libraries:

- **HttpCtrl.Client** - provides API to work with HTTP/HTTPS client [`link client documentation`_].

- **HttpCtrl.Server** - provides API to work with HTTP server [`link server documentation`_].

- **HttpCtrl.Json** - provides API to work Json messages [`link json documentation`_].

.. _link client documentation: https://annoviko.github.io/robotframework-httpctrl/client.html
.. _link server documentation: https://annoviko.github.io/robotframework-httpctrl/server.html
.. _link json documentation: https://annoviko.github.io/robotframework-httpctrl/json.html


Examples
========

Send GET request to obtain origin IP address and check that is not empty:

.. code:: robotframework

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