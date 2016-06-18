package taku_k

/**
  * Created by taku on 2016/06/19.
  */

import play.api.libs.json._

case class UrlCrawlResult(taskId: String, url: String, links: Seq[String])

case class ExtractResult(taskId: String, url: String, word: String, yomi: String)

trait ResultProtocol {
  implicit val urlCrawlResultFormat = Json.format[UrlCrawlResult]
  implicit val extractResultFormat = Json.format[ExtractResult]
}
