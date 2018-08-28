# -*- coding: utf-8 -*-
"""
    IncetOps.rqscheduler_worker
    ~~~~~~~~~~~~~~

    The working process of the RQ-Scheduler queue.

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

if __name__ == '__main__':
    import setproctitle
    from redis import from_url
    from config import GLOBAL, REDIS
    from rq_scheduler.scheduler import Scheduler
    setproctitle.setproctitle(GLOBAL['ProcessName'] + '.rqscheduler')
    scheduler = Scheduler(connection=from_url(REDIS), interval=1)
    scheduler.run()
