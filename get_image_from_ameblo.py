# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import sys
import datetime
import time
from bs4 import BeautifulSoup


async def get_page(ameblo_id, target_date):
    url = "http://ameblo.jp/{0}/imagelist-{1}.html"\
              .format(ameblo_id, target_date)
    res = await aiohttp.request('GET', url)
    body = await res.read()
    res.close()
    soup = BeautifulSoup(body, 'html.parser')
    img_url_list = []
    is_empty = True
    for i in soup.find_all('img'):
        if 'stat.ameba.jp' in i.get('src'):
            img_url_list.append('http:' + i.get('src'))
            is_empty = False
    if is_empty is True:
        pass
    else:
        tasks = [asyncio.ensure_future(preserve_image(url, ameblo_id,
                                                      target_date, index))
                 for index, url in enumerate(img_url_list)]
        await asyncio.wait(tasks)


async def preserve_image(url, ameblo_id, target_date, index):
    print("getting {} ...".format(url))
    resp = await aiohttp.request('GET', url)
    data = await resp.read()
    resp.close()
    with open("./{0}/{0}_{1}_{2:03d}.{3}"
              .format(ameblo_id, target_date, index, url[-3::]), "wb") \
            as f:
        f.write(data)

if __name__ == '__main__':
    argv = sys.argv
    argc = len(sys.argv)
    if argc == 2 or argc == 3:
        if '-h' in argv:
            print("Usage: {0} ameblo_id start_month_of_blog".format(argv[0]))
        else:
            # target Ameba Blog ID
            ameblo_id = argv[1]
            import os
            if os.path.exists(ameblo_id) is not True:
                os.mkdir(ameblo_id)
            # start date of blog
            start = argv[2]
            d = datetime.datetime.strptime(start, '%Y-%m')
            start_year = d.year
            start_month = d.month
            # year and month of today
            today = datetime.date.today()
            today_year = today.year
            today_month = today.month
            month_list = []
            # date validation
            # TODO
            while(not (today_month < d.month and today_year == d.year)):
                cur = d.strftime('%Y%m')
                month_list.append(cur)
                d = datetime.date.\
                    fromtimestamp(time.mktime((d.year, d.month + 1,
                                               1, 0, 0, 0, 0, 0, 0)))
            # asyncio event loop
            tasks = [asyncio.ensure_future(get_page(ameblo_id, target))
                     for target in month_list]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tasks))
            loop.close()
    else:
        print("Usage: {0} ameblo_id".format(argv[0]))
