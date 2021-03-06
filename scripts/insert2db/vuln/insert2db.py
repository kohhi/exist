#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import configparser
import inspect
import plugins
from plugins import *

## Django Setup
import django
import pymysql
pymysql.install_as_MySQLdb()
conffile = os.path.join(os.path.dirname(__file__), "../conf/insert2db.conf")
conf = configparser.SafeConfigParser()
conf.read(conffile)
sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from apps.vuln.models import Vuln
import django.utils.timezone as tzone
from django.db import IntegrityError

## Logger Setup
from logging.handlers import TimedRotatingFileHandler
from logging import getLogger, DEBUG, Formatter
logfilename = os.path.join(os.path.dirname(__file__), 'logs/insert2db.log')
logger = getLogger()
handler = TimedRotatingFileHandler(
    filename=logfilename,
    when="D",
    interval=1,
    backupCount=31,
)
handler.setFormatter(Formatter("%(asctime)s %(name)s %(funcName)s [%(levelname)s]: %(message)s"))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

DataDir = os.path.dirname(__file__) + '/data/'

def printQuery(q):
    print("==========")
    print(q.id)
    print(q.title)
    print(q.description)
    print(q.datetime)
    print(q.referrer)

def saveQuery(queries):
    res = []
    cnt = 0
    try:
        res = Vuln.objects.bulk_create(queries)
    except:
        for query in queries:
            try:
                query.save(force_insert=True)
                cnt += 1
            except IntegrityError:
                continue
            except Exception as e:
                logger.error("%s: %s", e, query)
                continue

    cnt += len(res)
    logger.info("%s queries were inserted", cnt)

if __name__ == '__main__':
    logger.info("%s start", __file__)

    modules = list(map(lambda x:x[0], inspect.getmembers(plugins, inspect.ismodule)))
    for module in modules:
        if module == 'glob' or module == 'os':
            continue
        try:
            queries = getattr(plugins, module).Tracker().parse()
        except Exception as e:
            logger.error(e)
        try:
            saveQuery(queries)
        except Exception as e:
            logger.error(e)

    logger.info("%s done", __file__)

