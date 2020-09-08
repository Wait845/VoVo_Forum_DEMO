import time
import shutil
import os
from PIL import Image
import requests
import random




class image():
    def __init__(self):

        self.project_location = "{}/".format(os.getcwd())

        print("image初始化， project_location:{}".format(self.project_location))

    def save_avatar(self, url_link, user_id):
        if len(url_link) == 0 or url_link is None:
            return "ISA001"
        if len(user_id) == 0 or user_id is None:
            return "ISA002"
        
        if url_link[0:4] != "http":     # 改链接为相对路径，转换为绝对路径
            url_link = "http://127.0.0.1" + url_link
        # 下载图片到临时文件夹
        img_request = requests.get(url_link)
        if img_request.status_code == 200:
            # 随机生成一个临时文件名
            img_name = str(int(time.time())) + "_" + str(random.randint(0, 1000))
            try:
                img_location = self.project_location + "static/images/"
                with open(img_location + "temp/{}.png".format(img_name), "wb") as img_file:    # 因为图片用二进制保存，所以使用WB
                    img_file.write(img_request.content)
                img = Image.open(img_location + "temp/{}.png".format(img_name))
                img = self.__cut_avatar(img)

                # 判断文件是否存在
                if os.path.isfile(img_location + "avatar/{}.png".format(user_id)):
                    from_addr = img_location + "avatar/{}.png".format(user_id)
                    to_addr = img_location + "avatar_old/{}_{}.png".format(user_id, str(int(time.time())))
                    shutil.copyfile(from_addr, to_addr)
                    os.remove(img_location + "avatar/{}.png".format(user_id))
                img.save(img_location + "avatar/{}.png".format(user_id))
                return "ISA006"

            except:
                # 文件错误
                print("保存文件错误")
                return "ISA003"

        else:
            # 获取图片失败
            print("获取图片失败")
            return "ISA004"

    def save_file(self, path):
        try:
            file_name = str(int(time.time())) + "_" + str(random.randint(0, 1000))
            img_location = self.project_location + "static/images/"
            img = Image.open(path)
            img = self.__cut_avatar(img)
            img.save(img_location + "temp/{}.png".format(file_name))
            return file_name
        except:
            return "ISF001"

    
    def __cut_avatar(self, img):
        img_width, img_length = img.size

        # 如果文件大小合法，则返回
        if img_width == img_length == 100:
            return img

        # 如果x边更小则以x边计算比例
        if img_width <= img_length:
            rate = img_width / 100
            img_width = 100
            img_length = round(img_length / rate)
        # 如果y边更小则以y边计算比例
        elif img_width > img_length:
            rate = img_length / 100
            img_length = 100
            img_width = round(img_width / rate)

        # 按计算好的像素进行resize
        img = img.resize((img_width, img_length), Image.ANTIALIAS)
        x = (img_width - 100) / 2   # 等同于 img_width / 2 - 50
        y = (img_length - 100) / 2  # 等同于 img_length / 2 - 50
        # 从中间裁剪出一个100*100的正方形
        img = img.crop((x, y, 100 + x, 100 + y))
        return img

