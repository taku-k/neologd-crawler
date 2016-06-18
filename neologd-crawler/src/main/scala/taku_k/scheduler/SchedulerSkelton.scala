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

class SchedulerSkelton
    extends Scheduler
    with Logging {

  protected[this] var tasksRunning = 0
  protected[this] var shuttingDown: Boolean = false

  def registered(
    driver: SchedulerDriver,
    frameworkId: FrameworkID,
    masterInfo: MasterInfo): Unit = {
    log.info("Scheduler.registered")
    log.info("FrameworkID:\n%s" format frameworkId)
    log.info("MasterInfo:\n%s" format masterInfo)
  }

  /**
    * Invoked when the scheduler re-registers with a newly elected Mesos master.
    * This is only called when the scheduler has previously been registered.
    * MasterInfo containing the updated information about the elected master
    * is provided as an argument.
    */
  def reregistered(
    driver: SchedulerDriver,
    masterInfo: MasterInfo): Unit = {
    log.info("Scheduler.reregistered")
    log.info("MasterInfo:\n%s" format masterInfo)
  }

  /**
    * Invoked when resources have been offered to this framework. A
    * single offer will only contain resources from a single slave.
    * Resources associated with an offer will not be re-offered to
    * _this_ framework until either (a) this framework has rejected
    * those resources or (b)
    * those resources have been rescinded.
    * Note that resources may be concurrently offered to more than one
    * framework at a time (depending on the allocator being used). In
    * that case, the first framework to launch tasks using those
    * resources will be able to use them while the other frameworks
    * will have those resources rescinded (or if a framework has
    * already launched tasks with those resources then those tasks will
    * fail with a TASK_LOST status and a message saying as much).
    */
  def resourceOffers(
    driver: SchedulerDriver,
    offers: JList[Offer]): Unit = {
    log.info("Scheduler.resourceOffers")
  }

  /**
    * Invoked when an offer is no longer valid (e.g., the slave was
    * lost or another framework used resources in the offer). If for
    * whatever reason an offer is never rescinded (e.g., dropped
    * message, failing over framework, etc.), a framwork that attempts
    * to launch tasks using an invalid offer will receive TASK_LOST
    * status updats for those tasks.
    */
  def offerRescinded(
    driver: SchedulerDriver,
    offerId: OfferID): Unit = {
    log.info("Scheduler.offerRescinded [%s]" format offerId.getValue)
  }

  /**
    * Invoked when the status of a task has changed (e.g., a slave is
    * lost and so the task is lost, a task finishes and an executor
    * sends a status update saying so, etc). Note that returning from
    * this callback _acknowledges_ receipt of this status update! If
    * for whatever reason the scheduler aborts during this callback (or
    * the process exits) another status update will be delivered (note,
    * however, that this is currently not true if the slave sending the
    * status update is lost/fails during that time).
    */
  def statusUpdate(
    driver: SchedulerDriver,
    status: TaskStatus): Unit = {
    import Protos.TaskState._

    //    log.info("Scheduler.statusUpdate:\n%s" format status)
    val state = status.getState
    val taskId = status.getTaskId.getValue
    val message = status.getMessage
    if (state == TASK_RUNNING)
      tasksRunning = tasksRunning + 1
    state match {
      case TASK_FINISHED =>
        tasksRunning = math.max(0, tasksRunning - 1)
      case TASK_FAILED =>
        tasksRunning = math.max(0, tasksRunning - 1)
        log.warn(s"Task [$taskId] is failed because $message")
      case TASK_KILLED =>
        tasksRunning = math.max(0, tasksRunning - 1)
      case TASK_LOST =>
        tasksRunning = math.max(0, tasksRunning - 1)
      case _ =>
        tasksRunning = tasksRunning
    }
  }

  /**
    * Invoked when an executor sends a message. These messages are best
    * effort; do not expect a framework message to be retransmitted in
    * any reliable fashion.
    */
  def frameworkMessage(
    driver: SchedulerDriver,
    executorId: ExecutorID,
    slaveId: SlaveID,
    data: Array[Byte]): Unit = {
    log.info("frameWorkMessage coming.")
  }

  /**
    * Invoked when the scheduler becomes "disconnected" from the master
    * (e.g., the master fails and another is taking over).
    */
  def disconnected(driver: SchedulerDriver): Unit = {
    log.info("Scheduler.disconnected")
  }

  /**
    * Invoked when a slave has been determined unreachable (e.g.,
    * machine failure, network partition). Most frameworks will need to
    * reschedule any tasks launched on this slave on a new slave.
    */
  def slaveLost(
    driver: SchedulerDriver,
    slaveId: SlaveID): Unit = {
    log.info("Scheduler.slaveLost: [%s]" format slaveId.getValue)
  }

  /**
    * Invoked when an executor has exited/terminated. Note that any
    * tasks running will have TASK_LOST status updates automagically
    * generated.
    */
  def executorLost(
    driver: SchedulerDriver,
    executorId: ExecutorID,
    slaveId: SlaveID,
    status: Int): Unit = {
    log.info("Scheduler.executorLost: [%s]" format executorId.getValue)
  }

  /**
    * Invoked when there is an unrecoverable error in the scheduler or
    * scheduler driver. The driver will be aborted BEFORE invoking this
    * callback.
    */
  def error(driver: SchedulerDriver, message: String): Unit = {
    log.info("Scheduler.error: [%s]" format message)
  }

  def waitForRunningTasks(): Unit = {
    while (tasksRunning > 0) {
      log.info(s"Shutting down but still have $tasksRunning tasks running.")
      Thread.sleep(3000)
    }
  }

  def shutdown[T](maxWait: Duration)(callback: => T): Unit = {
    log.info("Scheduler shutting down...")
    shuttingDown = true

    val f = Future { waitForRunningTasks() }
    Try { Await.ready(f, maxWait) }

    callback
  }
}
