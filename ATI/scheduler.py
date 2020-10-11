#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import queue
from concurrent.futures import ThreadPoolExecutor
from common.config import getConfig
from ATI.Testing import Testing


class Schedule(object):
    def __init__(self):
        self.thread_pool_size = max(1, int(getConfig('ATIThreadPoolSize'))) + 1
        self.tasks = queue.Queue()
        self.executor = ThreadPoolExecutor(self.thread_pool_size)

        self.run()

    @property
    def task(self):
        return None

    @task.setter
    def task(self, value):
        self.tasks.put((Testing, value))

    def worker(self):
        while True:
            func, param = self.tasks.get()
            func(param)
            self.tasks.task_done()

    def run(self):
        for i in range(self.thread_pool_size):
            self.executor.submit(self.worker)
