import threading

import urlparse, urllib, sys
from crawl import *
from results import *
from extract import *
import redis
from url_crawl_executor import VISITED_LINKS_KEY

try:
    from mesos.native import MesosExecutorDriver, MesosSchedulerDriver
    from mesos.interface import Executor, Scheduler
    from mesos.interface import mesos_pb2
except ImportError:
    from mesos import Executor, MesosExecutorDriver, MesosSchedulerDriver, Scheduler
    import mesos_pb2


HASH_KEY = "NEologd-NE:dict"
NEW_HASH_KEY = "NEologd-NE:new-dict"

class ExtractExecutor(Executor):
    def __init__(self, redis_host='localhost', port=6379):
        super(ExtractExecutor, self).__init__()

        self.redis_host = redis_host
        self.port = port
        self.visited_redis = redis.StrictRedis(host="192.168.24.53", port=6379)

    def registered(self, driver, executorInfo, frameworkInfo, slaveInfo):
        print("CrawlExecutor registered")
        self.conn_pool = redis.ConnectionPool(host=self.redis_host, port=self.port)

    def reregistered(self, driver, slaveInfo):
        print("CrawlExecutor reregistered")
        self.conn_pool = None
        self.conn_pool = redis.ConnectionPool(host=self.redis_host, port=self.port)

    def disconnected(self, driver):
        print("CrawlExecutor disconnected")
        self.conn_pool = None

    def launchTask(self, driver, task):
        def run_task():
            print("Running word extract task %s" % task.task_id.value)

            conn = redis.Redis(connection_pool=self.conn_pool)

            # Update status to RUNNING
            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_RUNNING
            driver.sendStatusUpdate(update)

            # URL for extracting NE
            url = task.data

            try:
                word, yomi = selector(url)
            except CantReadException:
                error_msg = "Could not read resource at %s" % url
                update = mesos_pb2.TaskStatus()
                update.task_id.value = task.task_id.value
                update.state = mesos_pb2.TASK_FAILED
                update.message = error_msg
                update.data = url

                driver.sendStatusUpdate(update)
                print error_msg
                return
            except ExtractFailedException:
                self.visited_redis.hset(VISITED_LINKS_KEY, url, "VISITED")

                error_msg = "Could not extract from given URL [{}]".format(url)
                update = mesos_pb2.TaskStatus()
                update.task_id.value = task.task_id.value
                update.state = mesos_pb2.TASK_FINISHED
                update.message = error_msg

                driver.sendStatusUpdate(update)
                print(error_msg)
                return

            # print("Get these links {}".format(links))
            self.visited_redis.hset(VISITED_LINKS_KEY, url, "VISITED")
            if conn.hexists(HASH_KEY, word) or conn.hexists(NEW_HASH_KEY, word):
                msg = "Already registered this word %s" % word
                update = mesos_pb2.TaskStatus()
                update.task_id.value = task.task_id.value
                update.state = mesos_pb2.TASK_FINISHED
                update.message = msg
                driver.sendStatusUpdate(update)
                print(msg.encode('utf-8'))
                return
            else:
                conn.hset(NEW_HASH_KEY, word, yomi + "," + url)

            res = ExtractResult(
                task.task_id.value,
                url,
                word,
                yomi
            )
            message = repr(res)
            driver.sendFrameworkMessage(message)

            print("Sending status update...")
            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_FINISHED
            driver.sendStatusUpdate(update)
            print("Sent status update")
            return

        thread = threading.Thread(target=run_task)
        thread.start()

    def killTask(self, driver, taskId):
        self.shutdown(driver)

    def frameworkMessage(self, driver, message):
        print("Ignoring framework message: %s" % message)

    def shutdown(self, driver):
        print("Shutting down")
        sys.exit(0)

    def error(self, error, message):
        pass

if __name__ == "__main__":
    print("Starting Launching Executor (LE)")
    if len(sys.argv) == 3:
        redis_host, port = sys.argv[1:3]
        driver = MesosExecutorDriver(ExtractExecutor(redis_host, int(port)))
    else:
        driver = MesosExecutorDriver(ExtractExecutor())
    sys.exit(0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1)