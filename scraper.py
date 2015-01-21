import requests
from lxml import html
import dataset
from itertools import count
from urlparse import urljoin
from datetime import datetime


BASE_URL = 'http://www.rigzone.com/data/results.asp?sortField=&sortDir=1&P=%s&Rig_Name=&RWD_Max=-1&RWD_Min=-1&Region_ID=-1&Rig_Type_ID=-1&Manager_ID=-1&Rig_Status_ID=-1&Operator_ID=-1'
engine = dataset.connect('sqlite:///data.sqlite')
rz_table = engine['data']


def parse_rig(url):
    url = urljoin(BASE_URL, url)
    res = requests.get(url)
    doc = html.fromstring(res.content)
    
    data = {'url': url, 'updated': datetime.utcnow()}
    for table in doc.findall('.//table//table'):
        for row in table.findall('.//tr'):
            cols = row.findall('./td')
            if len(cols) != 2:
                continue
            header, value = cols
            header = header.text_content().strip()
            header = header.replace(':', '').strip().lower().replace(' ', '_')
            value = value.text_content().strip()
            data[header] = value
    print data
    rz_table.upsert(data, ['url'])



def list_rigs():
    for i in count(1):
        url = BASE_URL % i
        res = requests.get(url)
        if not 'results.asp' in res.url:
            break
        doc = html.fromstring(res.content)
        for a in doc.findall('.//table//a'):
            if 'offshore_drilling_rigs' in a.get('href'):
                parse_rig(a.get('href'))

if __name__ == '__main__':
    list_rigs()
