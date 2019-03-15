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

        ${origin}=    Get Json Value   ${response body}   origin
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

        ${message}=    Get Json Value   ${response body}   data
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

        ${volume}=   Get Json Value   ${response body}   json/volume
        Should Be Equal   ${volume}   ${77}

        ${mute}=   Get Json Value   ${response body}   json/mute
        Should Be Equal   ${mute}   ${False}