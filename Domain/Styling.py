def apply_css(html_string: str):
    html_string = html_string.replace('<table',
                                      "<table style='font-size:14px;border-collapse:collapse;text-align:center;'")
    html_string = html_string.replace('<th',
                                      '<th style="background:#AFCDE7;color:white;padding:10px 20px;border-style:solid;border-width:0 1px 1px 0;border-color:white;text-align:left;"')
    html_string = html_string.replace('<td',
                                      '<td style="border-style:solid;border-width:0 1px 1px 0;border-color:white;background:#D8E6F3;"')
    return html_string
