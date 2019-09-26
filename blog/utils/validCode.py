import random
from PIL import Image,ImageFont,ImageDraw
import random
from io import BytesIO
def get_valid_code_img(request):
    #方式二
    # img = Image.new("RGB",(270,40),color=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
    # with open("validCode.png","wb") as f:
    #     img.save(f,"png")
    # with open("validCode.png","rb") as f:
    #     data = f.read()
    # return HttpResponse(data)
    def get_random_rgb():
        return (random.randint(0,255),random.randint(0,255),random.randint(0,255))

    img = Image.new("RGB",(270,40),color=get_random_rgb())
    draw = ImageDraw.Draw(img)
    my_font = ImageFont.truetype("static/font/delirium_sample.ttf",size=40)
    #自制验证码
    import string
    valid_code_str = ""
    for i in range(5):
        alp = string.ascii_uppercase+string.ascii_lowercase+string.digits
        distent_x = random.randint(i*40,i*40+10)
        distent_y = random.randint(0,10)
        word = random.choice(alp)
        draw.text((distent_x,distent_y),word,get_random_rgb(),font=my_font)
        valid_code_str += word
    print("验证码：",valid_code_str)
    # for i in range(5):
    #     random_num = str(random.randint(0,9))
    #     random_low_alpha = chr(random.randint(95,122))
    #     random_upper_alpha = chr(random.randint(65,90))
    #     word = random.choice([random_num, random_low_alpha,random_upper_alpha])
    #     draw.text((i*20+20,5),word,get_random_rgb(),font=my_font)
    request.session["valid_code_str"]=valid_code_str
    f = BytesIO()
    img.save(f,"png")
    return f.getvalue()