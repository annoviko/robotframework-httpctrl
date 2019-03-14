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

Send GET request to obtain origin IP address and check that is not empty.

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
