# -*- coding: utf-8 -*-
"""
    IncetOps.rq_worker
    ~~~~~~~~~~~~~~

    The working process of the RQ queue.

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

if __name__ == '__main__':
    import setproctitle
    from redis import from_url
    from config import GLOBAL, REDIS
    from rq import Worker, Queue, Connection
    listen = ['high', 'default', 'low']
    setproctitle.setproctitle(GLOBAL['ProcessName'] + '.rq')
    with Connection(from_url(REDIS)):
        worker = Worker(map(Queue, listen))
        worker.work()
