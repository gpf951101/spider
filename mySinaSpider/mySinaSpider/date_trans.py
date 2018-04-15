#encoding=utf-8
import time 
import datetime
import re
import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 

nowtime = datetime.datetime.now()
year = nowtime.year

def getYesterday():
    today=datetime.date.today()
    oneday=datetime.timedelta(days=1)
    yesterday=today-oneday
    return yesterday

def transformDate(text):
	if u'月' in text:
		month = re.findall(u'(\d+)月',text)[0]
		day = re.findall(u'(\d+)日',text)[0]
		text = '{0}-{1}-{2}'.format(year, month, day)
	elif u'分钟' in text or u'小时' in text or u'刚刚' in text or u'今天' in text:
		text = '{0}-{1}-{2}'.format(year, nowtime.month, nowtime.day)
	elif u'昨天' in text:
		yDay = getYesterday();
		text = '{0}-{1}-{2}'.format(yDay.year, yDay.month, yDay.day)
	else:
		group = re.findall(u"(\d+)-(\d+)-(\d+)", text)
		text = '{0}-{1}-{2}'.format(group[0][0],group[0][1],group[0][2])
	return text

if __name__ == '__main__':
	test = transformDate(u'2017-12-19 19:01:40 ')
	print test