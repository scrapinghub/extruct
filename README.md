Extruct
=======

Extruct = Extrct structure from web pages. It's a Web REST API that extract microdata formats from any given URL, or a set of URLS

Methods supported
=================

    /extruct/<URL>
    method = GET


    /extruct/batch
    method = POST
    params:
        urls - a list of URLs separted by newlines
        urlsfile - a file with one URL per line

    
