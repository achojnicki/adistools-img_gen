from adistools.adisconfig import adisconfig
from adistools.log import Log

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

        self._font_header=ImageFont.truetype('Comic Sans MS Bold.ttf', 30)
        self._font_text=ImageFont.truetype('Comic Sans MS Bold.ttf', 15)
        self._miku_img=Image.open('miku.png')



    def gen_img(self, time, user_agent, ip_addr):
        user_agent=parse(user_agent)
        buffer=BytesIO()

        img=Image.new(mode="RGBA", size=(1000, 563), color='white')
        draw=ImageDraw.Draw(img)
        draw.rectangle([(0,0),img.size], fill = (randint(0,255),randint(0,255),randint(0,255)))
        img.alpha_composite(self._miku_img)
        draw.text((10,10), "Welcome", font=self._font_header, fill="black")
        
        draw.text((10,80), f"Your IP Address is: {ip_addr}", font=self._font_text, fill="black")
        draw.text((10,100), f"Your browser is {user_agent.browser.family}({user_agent.browser.version_string})", font=self._font_text, fill="black")
        draw.text((10,120), f"Your operating system is {user_agent.os.family} version {user_agent.os.version_string}", font=self._font_text, fill="black")
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
