*** Settings ***

Library         HttpCtrl.Json


*** Test Cases ***

Write And Read Json Value
    ${json template}=   Catenate
     ...   {
     ...      "id": "200"
     ...   }

    ${json message}=   Set Json Value In String   ${json template}   id   300
    ${id}=   Get Json Value From String   ${json message}   id

    Should Be Equal   300   ${id}


Write And Read Json Nesting Value
    ${json template}=   Catenate
    ...   {
    ...      "book": {
    ...         "title": "St Petersburg: A Cultural History",
    ...         "author": "Solomon Volkov",
    ...         "price": 0,
    ...         "currency": ""
    ...      }
    ...   }

    ${catalog}=   Set Json Value In String   ${json template}   book/price   ${500}
    ${catalog}=   Set Json Value In String   ${catalog}   book/currency   RUB

    ${title}=   Get Json Value From String   ${catalog}   book/title
    ${price}=   Get Json Value From String   ${catalog}   book/price
    ${currency}=   Get Json Value From String   ${catalog}   book/currency

    Should Be Equal   St Petersburg: A Cultural History   ${title}
    Should Be Equal   ${500}   ${price}
    Should Be Equal   ${currency}   RUB


Write And Read Json Integer Value
    ${json template}=   Catenate
    ...   {
    ...      "integer":   1703
    ...   }

    ${json message}=   Set Json Value In String   ${json template}   integer   ${1812}
    ${value}=   Get Json Value From String   ${json message}   integer

    Should Be Equal   ${1812}   ${value}


Write And Read Json Array Value
    ${json template}=   Catenate
    ...   {
    ...      "array": [
    ...         "red", "green", "blue", "yellow"
    ...      ]
    ...   }

    ${colors}=   Set Json Value In String   ${json template}   array/3   white

    ${red}=     Get Json Value From String   ${colors}   array/0
    ${green}=   Get Json Value From String   ${colors}   array/1
    ${blue}=    Get Json Value From String   ${colors}   array/2
    ${white}=   Get Json Value From String   ${colors}   array/3

    Should Be Equal   red     ${red}
    Should Be Equal   green   ${green}
    Should Be Equal   blue    ${blue}
    Should Be Equal   white   ${white}


Write And Read Json Array Netsting Value
    ${json template}=   Catenate
    ...   {
    ...      "array": [
    ...         { "color": "red" },
    ...         { "color": "green" },
    ...         { "color": "white" }
    ...      ]
    ...   }

    ${colors}=   Set Json Value In String   ${json template}   array/2/color   blue

    ${red}=     Get Json Value From String   ${colors}   array/0/color
    ${green}=   Get Json Value From String   ${colors}   array/1/color
    ${blue}=    Get Json Value From String   ${colors}   array/2/color

    Should Be Equal   red     ${red}
    Should Be Equal   green   ${green}
    Should Be Equal   blue    ${blue}
