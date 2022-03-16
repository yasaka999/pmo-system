from mitmproxy import ctx, http
import json

class Modify:
    def request(self, flow):

        if flow.request.url.find("/group8/M00/48/00/wKgHkGHFhn-EWQuLAAAAABzPKmA696167241.zip") != -1  :
         ctx.log.info(flow.request.url)
         flow.request.url = "http://racknerd.homegw.ml:81/kindle.apk.zip"
         ctx.log.info("修改链接")

addons = [
    Modify()
]
