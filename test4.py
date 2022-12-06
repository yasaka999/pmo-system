import re
def substr(keyword,str):
    result = re.findall('%s.*>(.+?)</%s' %(keyword,keyword) ,str)[0]
    return result

str = '<?xml version="1.0" encoding="utf-8"?><SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:impl="iptv" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header/><SOAP-ENV:Body><impl:ResultNotify><CSPID >cspid</CSPID><LSPID>lspid</LSPID><CorrelateID>correlateid</CorrelateID><CmdResult>0</CmdResult><ResultFileURL>ftp</ResultFileURL></impl:ResultNotify></SOAP-ENV:Body></SOAP-ENV:Envelope>'
cspid = substr('CSPID',str)
lspid = substr('LSPID',str)
correlateid = substr('CorrelateID',str)
print (cspid,lspid,correlateid)