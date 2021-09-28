|Build Status Linux| |PyPi|

HttpCtrl library for Robot Framework
====================================

**RobotFramework-HttpCtrl** is a library for Robot Framework that provides HTTP/HTTPS client and HTTP server (IPv4 and IPv6) services
to make REST API testing easy.

**Version**: 0.1.x

**Author**: Andrei Novikov

**License**: GNU General Public License

**Documentation**: https://annoviko.github.io/robotframework-httpctrl/


Request Feature
===============

New features are implemented by request that can be created here using issues [`Press Me to Create a Feature Request`_]. Please, do not hesitate to create feature requests.

.. _Press Me to Create a Feature Request: https://github.com/annoviko/robotframework-httpctrl/issues/new?assignees=&labels=&template=feature_request.md&title=


Bug Reporting
=============

Please, do not hesitate to report about bugs using issues here [`Press Me to Report a Bug`_].

.. _Press Me to Report a Bug: https://github.com/annoviko/robotframework-httpctrl/issues/new?assignees=&labels=bug&template=bug_report.md&title=


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


Send POST request and extract required information from response:

.. code:: robotframework

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

.. code:: robotframework

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


.. |Build Status Linux| image:: https://github.com/annoviko/robotframework-httpctrl/actions/workflows/build-httpctrl.yml/badge.svg
   :target: https://github.com/annoviko/robotframework-httpctrl/actions
.. |PyPi| image:: https://badge.fury.io/py/robotframework-httpctrl.svg
   :target: https://badge.fury.io/py/robotframework-httpctrl