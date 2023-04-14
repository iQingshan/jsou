import requests
from bs4 import BeautifulSoup
from Crypto.Util import number

"""
@author：青山(qingshan@88.com)
@time：2023-04-07
@explain：仅仅对江苏开放大学学习平台可以使用 使用的账号密码为统一身份认证账号密码
"""


header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

#解析加密
class RSAPublicKey:
    def __init__(self, n, e, chunk_size):
        self.n = n
        self.e = e
        self.chunk_size = chunk_size


def encrypted_string(key, s):
    a = [ord(c) for c in s]
    while len(a) % (key.chunk_size // 8) != 0:
        a.append(0)

    al = len(a)
    result = ""
    for i in range(0, al, key.chunk_size // 8):
        block = number.bytes_to_long(bytes(a[i:i + key.chunk_size // 8][::-1]))
        crypt = pow(block, key.e, key.n)
        text = hex(crypt)[2:]
        text = text.rjust(key.chunk_size // 4, '0')
        result += text

    return result

def rsa_encode(str):
    # 定义公钥模数和指数
    modulus = int(
        '008aed7e057fe8f14c73550b0e6467b023616ddc8fa91846d2613cdb7f7621e3cada4cd5d812d627af6b87727ade4e26d26208b7326815941492b2204c3167ab2d53df1e3a2c9153bdb7c8c2e968df97a5e7e01cc410f92c4c2c2fba529b3ee988ebc1fca99ff5119e036d732c368acf8beba01aa2fdafa45b21e4de4928d0d403',
        16)
    exponent = int('010001', 16)
    # 解析公钥并创建公钥对象
    pub_key = RSAPublicKey(modulus, exponent, 128)
    # 明文密码
    password = str
    # 加密明文密码
    encrypted_password = encrypted_string(pub_key, password)
    # print("加密后的密码为：", encrypted_password)
    return encrypted_password

def get_execution():
    session = requests.session()
    url = "https://ids3.jsou.cn/login?service=http%3A%2F%2Fxuexi.jsou.cn%2Fjxpt-web%2Fauth%2FidsLogin"
    res = session.get(url,headers=header)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text,"html.parser")
        execution = soup.findAll('input',{'name':'execution'})[0].get('value')
        return session,execution
    else:
        return "你的IP可能被屏蔽了！"

def login():
    print("=========使用统一身份认证的账号=========")
    print('==============开始登录==============')
    username = str(input("请输入账号："))
    password = str(input("请输入密码："))
    print("==============登录中！==============")
    session,execution = get_execution()
    url = "https://ids3.jsou.cn/login?service=http%3A%2F%2Fxuexi.jsou.cn%2Fjxpt-web%2Fauth%2FidsLogin"
    password = rsa_encode(password)
    if len(password) == 256:
        pass
    else:
        password = '0'+ password
    data = {
        "_eventId": "submit",
        "encrypted": "true",
        "execution": execution,
        "loginType": 1,
        "password": password,
        "submit": "登录",
        "username": username
    }
    # print(data)
    res = session.post(url,data=data,headers=header)
    if res.status_code == 200:
        getCourse(session)

#获取课程
def getCourse(s):
    print("==============你的课程：==============")
    url = 'http://xuexi.jsou.cn/jxpt-web/student/courseuser/getAllCurrentCourseByStudent'
    res = s.get(url,headers=header)
    # print(res.text)
    if res.status_code == 200:
        for i in res.json()['body']:
            courseVersionId = i['courseVersionId']
            courseName = i['courseName']
            teacherName = i['teacherName']
            xh = res.json()['body'].index(i) + 1
            print("["+ str(xh) +"]课程名称："+ courseName + "   【"+ teacherName +"】")
        choose = int(input("请输入课程序号：")) - 1
        courseVersionId = res.json()['body'][choose]['courseVersionId']
        getCell(s,courseVersionId)

#获取课件
def getCell(s,id):
    print("==============开始刷课==============")
    url = "http://xuexi.jsou.cn/jxpt-web/student/course/getAllActivity/" + id
    res = s.get(url, headers=header)
    if res.status_code == 200:
        # print(res.json())
        cells = []
        try:
            for i in res.json()['body']:
                for m in i['activitys']:
                    # print(m)
                    activityId = m['activityId']
                    name = m['activityName']
                    length = m['length']
                    type = m['type']
                    total = m['totalTime']
                    if length != None and length != "None":
                        if total == "None" or total == None:
                            pass
                        elif total > length:
                            print("==>课件:"+name+"[100%]")
                            continue
                    if type == '2' or type == '3' or type == '1':
                        data = {'type':type,'activityId':activityId,'name':name,'length':length}
                        cells.append(data)
            for cell in cells:
                heart(s,id,cell['activityId'],cell['length'],cell['type'],cell['name'])
            print("++++++++++++++++++++++++++++++++++++\n"+
                  "============本门课程已刷完！===========\n"+
                  "++++++++++++++++++++++++++++++++++++\n\n\n")
            next(s)
        except Exception as e:
            exit("没有课件哦")

#心跳保存进度
def heart(s,id,activityId,length,type,name):
    try:
        times = int(length/30) + 1
    except Exception as e:
        times = 1
    url = "http://xuexi.jsou.cn/jxpt-web/common/learningBehavior/heartbeat"
    data = {
        'playStatus': 'true',
        'isResourcePage': 'true',
        'courseVersionId': id,
        'activityId': activityId,
        'isStuLearningRecord': 2,
        'token': 'SpwPXGs2',
        'type': type
    }
    for i in range(0,times):
        res = s.post(url,data=data,headers=header)
        if res.status_code == 200:
            if res.json()['code'] == "SUCCESS":
                pass
            else:
                exit("error")
        else:
            exit("error")
    print("==>课件:"+name+"[已完成]")

def next(s):
    print("==============选择操作：==============")
    print("==============1.继续刷课==============")
    print("==============2.切换账号==============")
    print("==============3.退出程序==============")
    next_step = int(input('请选择：'))
    if next_step == 1:
        getCourse(s)
    elif next_step == 2:
        login()
    else:
        exit("退出成功")


if __name__ == '__main__':
    login()






