package taku_k

import java.io.File

import com.google.protobuf.ByteString
import org.apache.mesos.Protos

import scala.collection.JavaConversions._
import scala.collection.JavaConverters._

/**
  * Created by taku on 2016/06/18.
  */
trait Utils {

  def seedURL(): String
  def redisHost(): String
  def redisPort(): String

  val TASK_CPUS = 0.3
  val TASK_MEM = 64.0

  lazy val seedURLHost: String = new java.net.URI(seedURL).getHost

  protected[this] val uris: Seq[Protos.CommandInfo.URI] =
    Seq(
      "python/url_crawl_executor.py",
      "python/crawl.py",
      "python/results.py",
      "python/extract.py",
      "python/extract_executor.py"
    ).map {
        file =>
          Protos.CommandInfo.URI.newBuilder
            .setValue(new File("/home/vagrant/hostfiles", file).getAbsolutePath)
            .setExtract(false)
            .build
      }

  lazy val urlCrawlExecutor: Protos.ExecutorInfo = {
    val command = Protos.CommandInfo.newBuilder
      .setValue("python url_crawl_executor.py")
      .addAllUris(uris.asJava)
    Protos.ExecutorInfo.newBuilder
      .setExecutorId(Protos.ExecutorID.newBuilder.setValue("url-crawl-executor"))
      .setName("URLCrawler")
      .setCommand(command)
      .build
  }

  lazy val extractExecutor: Protos.ExecutorInfo = {
    val command = Protos.CommandInfo.newBuilder
      .setValue(s"python extract_executor.py $redisHost $redisPort")
      .addAllUris(uris.asJava)
    Protos.ExecutorInfo.newBuilder
      .setExecutorId(Protos.ExecutorID.newBuilder.setValue("extract-executor"))
      .setName("Extract")
      .setCommand(command)
      .build
  }

  def makeTaskPrototype(id: String, offer: Protos.Offer): Protos.TaskInfo =
    Protos.TaskInfo.newBuilder
      .setTaskId(Protos.TaskID.newBuilder.setValue(id))
      .setName("")
      .setSlaveId((offer.getSlaveId))
      .addAllResources(
        Seq(
          scalarResource("cpus", TASK_CPUS),
          scalarResource("mem", TASK_MEM)
        ).asJava
      )
      .build

  protected def scalarResource(name: String, value: Double): Protos.Resource =
    Protos.Resource.newBuilder
      .setType(Protos.Value.Type.SCALAR)
      .setName(name)
      .setScalar(Protos.Value.Scalar.newBuilder.setValue(value))
      .build

  def makeURLCrawlTask(
    id: String,
    url: String,
    offer: Protos.Offer): Protos.TaskInfo =
    makeTaskPrototype(id, offer).toBuilder
      .setName(s"url_crawl_$id")
      .setExecutor(urlCrawlExecutor)
      .setData(ByteString.copyFromUtf8(url))
      .build

  def makeExtractTask(
    id: String,
    url: String,
    offer: Protos.Offer): Protos.TaskInfo =
    makeTaskPrototype(id, offer).toBuilder
      .setName(s"extract_$id")
      .setExecutor(extractExecutor)
      .setData(ByteString.copyFromUtf8(url))
      .build

  def validateURL(url: String): Boolean =
    try {
      new java.net.URI(url).getHost == seedURLHost
    }
    catch {
      case e: Exception =>
        false
    }

  def getMaxTasks(
    offer: Protos.Offer,
    cpusPerTask: Double = TASK_CPUS,
    memPerTask: Double = TASK_MEM): Int = {

    var count = 0
    var cpus = 0.0
    var mem = 0.0

    for (resource <- offer.getResourcesList) {
      resource.getName match {
        case "cpus" => cpus = resource.getScalar.getValue
        case "mem"  => mem = resource.getScalar.getValue
        case _      => ()
      }
    }

    while (cpus >= cpusPerTask && mem >= memPerTask) {
      count = count + 1
      cpus = cpus - cpusPerTask
      mem = mem - memPerTask
    }

    count
  }
}
