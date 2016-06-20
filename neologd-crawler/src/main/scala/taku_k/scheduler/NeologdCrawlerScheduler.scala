package taku_k.scheduler

import java.io.File
import java.nio.charset.Charset

import taku_k._
import org.apache.mesos.{ Scheduler, SchedulerDriver }
import org.apache.mesos.Protos._
import java.util.{ List => JList }

import scala.concurrent.{ Await, Future }
import scala.concurrent.duration.Duration
import scala.util.Try
import org.apache.mesos.Protos

import scala.collection.JavaConversions._
import scala.collection.JavaConverters._
import scala.collection.mutable
import scala.concurrent.ExecutionContext.Implicits.global

class NeologdCrawlerScheduler(val home: String, val seedURL: String, val redisHost: String, val redisPort: String, val depth: Int)
    extends SchedulerSkelton
    with Utils
    with ResultProtocol {

  private[this] val crawlQueue = mutable.Queue[String](seedURL)
  private[this] val extractQueue = mutable.Queue[String]()
  private[this] val processedURLs = mutable.Set[String]()
  private[this] var tasksCreated = 0

  private[this] var crawlPoint = 1
  private[this] var prev = ""
  private[this] var extractPoint = 1

  override def resourceOffers(
    driver: SchedulerDriver,
    offers: JList[Offer]): Unit = {
    log.info("Scheduler.resourceOffers")
    // print and decline all received offers
    offers foreach { offer =>
      //      log.info(s"Gou resource offer $offer")

      val maxTasks = getMaxTasks(offer)
      log.info(s"we get $maxTasks")

      val tasks = mutable.Buffer[Protos.TaskInfo]()

      var numCrawlTask = (maxTasks * crawlPoint / (crawlPoint + extractPoint))
      var numExtractTask = (maxTasks * extractPoint / (crawlPoint + extractPoint))
      if (numCrawlTask == 0) {
        numCrawlTask = 1
        numExtractTask -= 1
      }
      log.info(s"numCrawlTask = $numCrawlTask, numExtractTask = $numExtractTask")

      0 until numCrawlTask foreach (_ => {
        if (crawlQueue.nonEmpty) {
          val url = crawlQueue.dequeue
          tasks += makeURLCrawlTask(s"$tasksCreated", url, offer)
          tasksCreated += 1
        }
      })
      0 until numExtractTask foreach (_ => {
        if (extractQueue.nonEmpty) {
          val url = extractQueue.dequeue
          tasks += makeExtractTask(s"$tasksCreated", url, offer)
          tasksCreated += 1
        }
      })

      if (tasks.nonEmpty)
        driver.launchTasks(Seq(offer.getId).asJava, tasks.asJava)
      else {
        log.warn("Maybe task is empty, so you should stop framework.")
        driver declineOffer offer.getId
      }
    }
  }

  override def frameworkMessage(
    driver: SchedulerDriver,
    executorId: ExecutorID,
    slaveId: SlaveID,
    data: Array[Byte]): Unit = {
    import play.api.libs.json._

    val jsonString = new String(data, Charset.forName("UTF-8"))

    executorId.getValue match {
      case id if id == urlCrawlExecutor.getExecutorId.getValue =>
        if (prev == "crawl") {
          extractPoint += 1
        }
        else {
          extractPoint = math.max(1, extractPoint - 1)
        }
        prev = "crawl"
        val result = Json.parse(jsonString).as[UrlCrawlResult]
        result.links.foreach { (link: String) =>
          {
            if (validateURL(link) && !processedURLs.contains(link)) {
              //              println(s"Enqueueing [$link]")
              processedURLs += link
              crawlQueue += link
              extractQueue += link
            }
          }
        }

      case id if id == extractExecutor.getExecutorId.getValue =>
        if (prev == "extract") {
          crawlPoint += 1
        }
        else {
          crawlPoint = math.max(1, crawlPoint - 1)
        }
        prev = "extract"
        val result = try {
          Json.parse(jsonString).as[ExtractResult]
        }
        catch {
          case _ => ""
        }
        log.info(s"Get word [$result]")
    }

  }

}