package taku_k

import taku_k.scheduler.NeologdCrawlerScheduler
//import taku_k.executor.NeologdCrawlerExecutor

import com.typesafe.config.{ Config, ConfigFactory }
import org.apache.mesos.{ MesosSchedulerDriver }
import org.apache.mesos.Protos.{ FrameworkInfo, FrameworkID }
import scala.concurrent.Future
import scala.concurrent.duration._
import scala.concurrent.ExecutionContext.Implicits.global

object NeologdCrawler extends Logging {

  val defaultSettings = ConfigFactory.parseString("""
    mesos {
      master = "127.0.1.1:5050"
    }
    redis {
      host = "localhost"
      port = "6379"
    }
  """)

  val config = ConfigFactory.load.getConfig("taku_k").withFallback(defaultSettings)

  val normalizedName = "neologd-crawler"
  val failoverTimeout = 600000 // in milliseconds (10 minutes)
  val mesosMaster = config.getString("mesos.master")
  val redisHost = config.getString("redis.host")
  val redisPort = config.getString("redis.port")

  val frameworkId = FrameworkID.newBuilder.setValue(normalizedName)

  val frameworkInfo = FrameworkInfo.newBuilder()
    .setName(normalizedName)
    .setFailoverTimeout(failoverTimeout)
    .setUser("") // let Mesos assign the user
    .setCheckpoint(false)
    .build

  val scheduler = new NeologdCrawlerScheduler("http://www.what-myhome.net")

  val driver = new MesosSchedulerDriver(
    scheduler,
    frameworkInfo,
    mesosMaster
  )

  // Execution entry point
  def main(args: Array[String]): Unit = {
    log.info("Start framework [{}]!", normalizedName)
    log.info(mesosMaster)
    Future { driver.run }

    log.info("Please push [Ctrl-C] if you would stop this framework.")
    var pool = true
    sys addShutdownHook {
      log.info("Shutdown hook caught.")
      scheduler.shutdown(5.minutes) {
        driver.stop()
        pool = false
        Thread.sleep(5000)
      }
    }

    while (pool) {
      Thread.sleep(1000)
    }

  }

}
