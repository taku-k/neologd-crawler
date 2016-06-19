import sys
import threading
import redis
import urlparse, urllib, sys
from crawl import *
from results import *

try:
    from mesos.native import MesosExecutorDriver, MesosSchedulerDriver
    from mesos.interface import Executor, Scheduler
    from mesos.interface import mesos_pb2
except ImportError:
    from mesos import Executor, MesosExecutorDriver, MesosSchedulerDriver, Scheduler
    import mesos_pb2

VISITED_LINKS_KEY = "NEologd-NE:visited-links"

class URLCrawlExecutor(Executor):
    def __init__(self, redis_host='localhost', port=6379):
        super(URLCrawlExecutor, self).__init__()

        self.redis_host = redis_host
        self.port = port

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
            print("Running URL crawl task %s" % task.task_id.value)

            conn = redis.Redis(connection_pool=self.conn_pool)

            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_RUNNING
            driver.sendStatusUpdate(update)

            url = task.data

            try:
                links = url_crawl(url)
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
            except NotAnyFetchException:
                error_msg = "Could not fetch any links from html"
                update = mesos_pb2.TaskStatus()
                update.task_id.value = task.task_id.value
                update.state = mesos_pb2.TASK_FINISHED
                update.message = error_msg

                driver.sendStatusUpdate(update)
                print error_msg
                return

            # print("Get these links {}".format(links))

            selected_links = []
            for link in links:
                if not conn.hexists(VISITED_LINKS_KEY, link):
                    selected_links.append(link)

            res = UrlCrawlResult(
                task.task_id.value,
                url,
                links
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
        driver = MesosExecutorDriver(URLCrawlExecutor(redis_host, int(port)))
    else:
        driver = MesosExecutorDriver(URLCrawlExecutor())
    sys.exit(0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1)