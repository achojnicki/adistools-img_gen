from adisconfig import adisconfig
from log import Log

from flask import Flask, request, Response
from uuid import uuid4
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from user_agents import parse
from random import randint

class img_gen:
    project_name='adistools-img_gen'
    def __init__(self):
        self._config=adisconfig('/opt/adistools/configs/adistools-img_gen.yaml')
        self._log=Log(
            parent=self,
            backends=['rabbitmq_emitter'],
            debug=self._config.log.debug,
            rabbitmq_host=self._config.rabbitmq.host,
            rabbitmq_port=self._config.rabbitmq.port,
            rabbitmq_user=self._config.rabbitmq.user,
            rabbitmq_passwd=self._config.rabbitmq.password,
        ) 

        self._font_text=ImageFont.truetype('Monaco.ttf', 30)
        self._terminal_img=Image.open('terminal.png')



    def gen_img(self, time, user_agent, ip_addr):
        user_agent=parse(user_agent)
        buffer=BytesIO()

        img=self._terminal_img.copy()
        draw=ImageDraw.Draw(img)
        
        draw.text((465,750), f'"{ip_addr}",', font=self._font_text, fill=(191, 189, 0))
        img.save(buffer, "png")
        buffer.seek(0)        
        return buffer.read()

img_gen=img_gen()
application=Flask(__name__)

@application.route("/")
def img():
    time=datetime.now()
    user_agent=str(request.user_agent)
    if request.headers.getlist("X-Forwarded-For"):
        remote_addr=request.headers.getlist("X-Forwarded-For")[0]
    else:
        remote_addr=str(request.remote_addr)
    
    img=img_gen.gen_img(time, user_agent, remote_addr)

    return Response(
    	img,
        mimetype='image/png',
    )
