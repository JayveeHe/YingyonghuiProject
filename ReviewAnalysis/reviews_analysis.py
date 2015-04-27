# coding=utf-8
from datetime import datetime
import json
import os
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
__author__ = 'ITTC-Jayvee'
project_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
data_path = '%s/data' % (project_path)

# project import
sys.path.append(project_path)
import Utils
from Utils.get_logger import logger, Timer


@Timer
def analysis(appinfo_connect, appname):
    appinfo = appinfo_connect.find_one({'app_name': appname})
    fout = open('%s/result.csv' % data_path, 'w')
    fout.write('date,content,version,nickname,phonetype\n')
    if appinfo is not None:
        comments = appinfo['comments']
        for comment in comments:
            date = comment['date']
            content = comment['comment']
            content = str(content).replace('\r','')
            version = comment['version']
            nickname = comment['nickname']
            phonetype = comment['phonetype']
            fout.write('%s,%s,%s,%s,%s\n' % (str(date), str(content).strip(), version, nickname, phonetype))
            # fout.write('%s\n' % (nickname))


if __name__ == '__main__':
    import pymongo

    db_address = json.loads(open('%s/conf/DB_Address.conf' % (project_path), 'r').read())['MongoDB_Address']
    conn = pymongo.MongoClient(host=db_address, port=27017)
    appinfo_connect = conn.AppChinaData.AppInfo
    analysis(appinfo_connect, '微信')
