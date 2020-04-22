import json
import os
import requests
import re
import time
import datetime
import argparse

def gethtml(url,ip): #定义获取url的函数
    #print(url)
    proxy = {
        'http': 'http://' + ip,
        'https': 'https://' + ip
    }
    try:
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',

        }
        t=requests.get(url,headers=header,proxies=proxy,timeout=10)
        print("     ",t.status_code)
        t.encoding="utf-8"
        t.raise_for_status()
        #print(t.text)
        return t.text
    except Exception as result:
        print('       err1 爬取失败 ',result)

        return ''



def getallIamgeUrl(number,style):
    print("--获取图片列表---")
    allimageurisset = set()
    path="./file/"+style+".txt"
    j=0
    while j < int(number/60)+1:

        time.sleep(3)
        #https://www.wikiart.org/en/paintings-by-style/ukiyo-e?select=featured&json=2&layout=new&page=2&resultType=masonry
        url = "https://www.wikiart.org/en/paintings-by-style/"+style+"?select=featured&json=2&layout=new&page="+str(j+1)+"&resultType=masonry"
        demo = gethtml(url)
        if demo != '':
            data = json.loads(demo)
            #print(data)
            inmagelist = []
            inmagelist = data.get("Paintings")
            print("step ",j+1," 图片数量 ",len(inmagelist)," url ",url)
            if len(inmagelist)>0:
                j = j+1
            for i in range(len(inmagelist)):
                t = inmagelist[i]
                allimageurisset.add(t["paintingUrl"])
        else:
            print(j+1," ",style," 没捕获图片列表,重新开始")



            #print(type(t))
            #print(t)
            #print(t["width"]," ",t["height"]," ",t["paintingUrl"])
    print("-------")

    allimageuri = list(allimageurisset)
    print("总作品数量 ",len(allimageuri))
    # 写之前，先检验文件是否存在，存在就删掉
    if len(allimageuri)>0:
        # 以写的方式打开文件，如果文件不存在，就会自动创建
        file_write_obj = open(path, 'a+',encoding='utf-8')
        for var in allimageuri:
            file_write_obj.writelines(str(var)+"\n")
            #file_write_obj.write('\n')
        file_write_obj.close()

def findminIndex(sizelist):
    index0 = 0
    for i in range(len(sizelist)):
        if  sizelist[i][1]>250 and sizelist[i][2]>250  :
            index0 = i
            break
    return index0
def findImgUrl(uri,dallip, dimgtime,tc):

    url = "https://www.wikiart.org"+uri
    print("     a.寻找图片链接 在",url)
    furltime = datetime.datetime.now()
    print("     ", furltime)
    allip = dallip
    ip = allip[int(tc%10)]
    tc = tc +1
    if (furltime- dimgtime).seconds>60:
        allip = getip()
        ip = allip[0]
        tc = 0
    html = gethtml(url,ip)
    str0 = r'ng-init="thumbnailSizesModel = {.*}'
    result = re.findall(str0,html)
    #soup =BeautifulSoup(html)
    if len(result)<1:
        print("         err2 ",uri," 没找到图片链接")
        return 0,0,0,0,allip,furltime,tc
    imgurlsstr = result[0].split("=")[-1].replace("&quot;",'"')
    data = json.loads(imgurlsstr)
    templist = data.get("ImageThumbnailsModel")[0]["Thumbnails"]

    sizelist = []
    for i in range(len(templist)):
        #一个图片 templist[i]
        sizelist.append((abs(int(templist[i]['Width'])*int(templist[i]['Height'])-250*250),int(templist[i]['Width']),int(templist[i]['Height'])))
        #print(i," ",int(templist[i]['Width'])*int(templist[i]['Height'])," ",templist[i]['Name']," ",templist[i])
    #print(sizelist)
    index0 = findminIndex(sizelist)
    imgurl = templist[index0]['Url']
    Width = templist[index0]['Width']
    Height = templist[index0]['Height']

    return 1,imgurl,Width,Height,allip,furltime,tc
    #print(imgurl)
    #print(index0, " ", int(templist[index0]['Width']) ," ", int(templist[index0]['Height']), " ", templist[index0]['Name'], " ", templist[index0])
    #print(sizelist)

def cleanUrl(url):

    str0 = r'&#\d*;'
    result = re.findall(str0,url)
    if len(result)==0:
        return url
    result = list(set(result))
    #print(result)
    newurl = ""
    for i0 in range(len(result)):

        #print("------%d----"%(i0))
        newurl = ""
        str0=result[i0]
        str1=chr(int(str0[2:-1]))
        #print(str0)
        #print(str1)
        templist=url.split(str0)
        newurl=templist[0]
        #print(templist)
        #print(len(templist))

        for j in range(1,len(templist)):
            newurl = newurl+str1+templist[j]
        url = newurl
    print("       newurl:",newurl)
    return newurl

def downloadImg(url,dir,imgname,allip0,furlTime,tc):

    #&#224;-1508.jpg!Portrait.jpg
    #url = url.replace("&#224;",'')
    newurl = cleanUrl(url)
    ip = allip0[tc%10]
    tc = tc+1
    allip = allip0
    dimgtime = datetime.datetime.now()
    if (dimgtime-furlTime).seconds >60:
        allip = getip()
        ip = allip[0]
        tc = 0
    print("     b.下载图片 url", newurl)
    print("     ", dimgtime)
    #time.sleep(3)
    path = dir+imgname
    try:
        if not os.path.exists(path):
            header = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',

            }
            proxy = {
                'http': 'http://' + ip,
                'https': 'https://' + ip
            }
            r = requests.get(newurl, headers=header,proxies=proxy,timeout=11)
            print("       请求的url",r.request.url)
            print("       状态码：",r.status_code)
            r.raise_for_status()
            with open(path,'wb') as f:
                f.write(r.content)
                f.close()
                print("       ",imgname+" 保存成功")
                return 2,allip,dimgtime,tc
        else:
            return 2,allip,dimgtime,tc
    except:
        print("         err3 下载图片失败")
        return 3,allip,dimgtime,tc

#python  05-artimage.py -style proto-renaissance -number 440
"""
401910 401691
python  05-artimage.py -style early-renaissance -number 1617 
python  05-artimage.py -style mannerism-late-renaissance -number 1523 
python  05-artimage.py -style northern-renaissance -number 2913 romanticism
python  05-artimage.py -style romanticism -number 3599 
python  05-artimage.py -style realism -number 3599 
python  05-artimage.py -style neoclassicism -number 3599 
python  05-artimage.py -style abstract-art -number 2058 #
python  05-artimage.py -style abstract-expressionism -number 3599
python  05-artimage.py -style expressionism -number 3599
python  05-artimage.py -style ukiyo-e -number 1740
undone----
python  05-artimage.py -style surrealism -number 3599
python  05-artimage.py -style post-impressionism -number 3599
python  05-artimage.py -style impressionism -number 3599
"""
def getip():
    targetUrl = "https://proxyapi.horocn.com/api/v2/proxies?order_id=ZRQI1664680338184184&num=20&format=json&line_separator=win&can_repeat=yes&user_token=1c6fd89a8e5fc0708b8b54a003aae8f2&loc_name=%E6%B1%9F%E8%8B%8F"
    resp = requests.get(targetUrl,timeout=3)
    allip = []
    demo = resp.text
    if demo != '':
        data = json.loads(demo)
        # print(data)
        inmagelist = []
        inmagelist = data.get("data")

        for i in range(len(inmagelist)):
            t = inmagelist[i]
            allip.append(t["host"] + ":" + t["port"])
    return allip
def main(args):
    style =args.style# "early-renaissance"
    number = args.number#1617
    print(style," ",number)
    imgdir="./img/"+style+"/"
    writepath = "./file/"+style+"-download.txt"
    readpath = "./file/" + style + ".txt"

    if not os.path.exists(imgdir):
        os.mkdir(imgdir)

    if not os.path.exists(readpath):
        getallIamgeUrl(number=number,style=style)
    # 以写的方式打开文件，如果文件不存在，就会自动创建

    file_obj_read = open(readpath,encoding='utf-8')
    all_lines = file_obj_read.readlines()
    dallip = getip()
    dimgtime = datetime.datetime.now()
    tc = 0
    j = 0
    while j>=0:
        imglist = os.listdir(imgdir)
        if len(imglist)==number or int(j/number)>10:
            break
        i= j%number
        line = all_lines[i]
        j= j+1
        line = line.strip('\n')
        #print(line)
        imgname = line.split("/")[-2]+"+"+line.split("/")[-1] + ".jpg"
        print("------{}: {}----".format(i+1,imgname))
        print("     ",datetime.datetime.now())
        if not os.path.exists(imgdir + imgname):
            #allip = getip()
            ip = ""
            ok,imgurl,Width,Height,allip1,furlTime,tc = findImgUrl(line,dallip, dimgtime,tc )
            if ok>0:
                line = line+"?W*H:"+str(Width)+"*"+str(Height)
                print("       ",imgurl)
                print("       ",line)
                fl, dallip, dimgtime,tc =downloadImg(url=imgurl, dir=imgdir,imgname=imgname,allip0=allip1,furlTime=furlTime,tc=tc)
                if  fl==2 and 1<2 :
                    with open(writepath, 'a+',encoding='utf-8') as file_write_obj:
                        file_write_obj.writelines(str(line) + "\n")



    file_obj_read.close()


parser = argparse.ArgumentParser(usage="it's usage tip.", description="help info.")
parser.add_argument("-style", type=str, required=True, help="图片风格.")
parser.add_argument("-number", type=int, required=True, help="图片数量")

args = parser.parse_args()
main(args)



#getallIamgeUrl(120,'high-renaissance1')