class HtmlTemplate():
    st_html= ""
    async def insert_token(token):
        st_html= f"""
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=
                            , initial-scale=1.0">
                            <title>Document</title>
                        </head>
                        <body>
                            <p> From Papic Nation through HTML </p>
                            <p>Click this link below to reset pin: 
                                <div id="token">{token}</div>
                                <br>
                                https://slni.org
                            </p>
                        </body>
                        </html>
            """
        return st_html