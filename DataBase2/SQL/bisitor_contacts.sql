-- MySQL dump 10.13  Distrib 5.7.25, for Linux (x86_64)
--
-- Host: localhost    Database: bisitor_contacts
-- ------------------------------------------------------
-- Server version	5.7.25-0ubuntu0.18.10.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `administrations`
--

DROP TABLE IF EXISTS `administrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `administrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `last_name` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `middle_name` varchar(50) DEFAULT NULL,
  `card_id` varchar(16) DEFAULT NULL,
  `contact_info_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `card_id` (`card_id`),
  KEY `contact_info_id` (`contact_info_id`),
  CONSTRAINT `administrations_ibfk_1` FOREIGN KEY (`contact_info_id`) REFERENCES `contacts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administrations`
--

LOCK TABLES `administrations` WRITE;
/*!40000 ALTER TABLE `administrations` DISABLE KEYS */;
/*!40000 ALTER TABLE `administrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth5`
--

DROP TABLE IF EXISTS `auth5`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth5` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `login` varchar(40) DEFAULT NULL,
  `password` varchar(40) DEFAULT NULL,
  `uid` varchar(40) DEFAULT NULL,
  `user_type` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `login` (`login`),
  UNIQUE KEY `uid` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth5`
--

LOCK TABLES `auth5` WRITE;
/*!40000 ALTER TABLE `auth5` DISABLE KEYS */;
INSERT INTO `auth5` VALUES (1,'2019-03-09 09:40:52','2019-03-09 09:40:52',0,NULL,'VAE','123456','4c0d240e43362d132e6c657d0ed8e17b',1,1),(2,'2019-01-03 00:44:00','2019-01-05 03:52:17',NULL,NULL,'IVAN','123456','4c0d240e4336dd132e6c657d0ed8e17b',1,2);
/*!40000 ALTER TABLE `auth5` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contacts`
--

DROP TABLE IF EXISTS `contacts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `contacts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `email` varchar(200) DEFAULT NULL,
  `auto` tinyint(1) DEFAULT NULL,
  `last_auto` datetime DEFAULT NULL,
  `interval_auto_hours` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contacts`
--

LOCK TABLES `contacts` WRITE;
/*!40000 ALTER TABLE `contacts` DISABLE KEYS */;
INSERT INTO `contacts` VALUES (1,'2019-03-07 18:22:51','2019-03-09 16:05:54',NULL,NULL,'merd888888@gmail.com',1,'2019-03-09 04:23:08',1);
/*!40000 ALTER TABLE `contacts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `data_views`
--

DROP TABLE IF EXISTS `data_views`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_views` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `abbreviation` varchar(16) DEFAULT NULL,
  `script_path` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_views`
--

LOCK TABLES `data_views` WRITE;
/*!40000 ALTER TABLE `data_views` DISABLE KEYS */;
INSERT INTO `data_views` VALUES (1,'Пропуски','Пропуски','OneListStudentsTotalLoss');
/*!40000 ALTER TABLE `data_views` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departments`
--

DROP TABLE IF EXISTS `departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `departments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `abbreviation` varchar(16) DEFAULT NULL,
  `faculty_id` int(11) NOT NULL,
  `contact_info_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `faculty_id` (`faculty_id`),
  KEY `contact_info_id` (`contact_info_id`),
  CONSTRAINT `departments_ibfk_1` FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`id`),
  CONSTRAINT `departments_ibfk_2` FOREIGN KEY (`contact_info_id`) REFERENCES `contacts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departments`
--

LOCK TABLES `departments` WRITE;
/*!40000 ALTER TABLE `departments` DISABLE KEYS */;
INSERT INTO `departments` VALUES (1,'Кафедра Безопасности Информационных Систем','ИС',1,NULL);
/*!40000 ALTER TABLE `departments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departments_professors`
--

DROP TABLE IF EXISTS `departments_professors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `departments_professors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `department_id` int(11) DEFAULT NULL,
  `professor_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `departments_professors_UK` (`department_id`,`professor_id`),
  KEY `professor_id` (`professor_id`),
  CONSTRAINT `departments_professors_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
  CONSTRAINT `departments_professors_ibfk_2` FOREIGN KEY (`professor_id`) REFERENCES `professors` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departments_professors`
--

LOCK TABLES `departments_professors` WRITE;
/*!40000 ALTER TABLE `departments_professors` DISABLE KEYS */;
INSERT INTO `departments_professors` VALUES (1,1,1);
/*!40000 ALTER TABLE `departments_professors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disciplines`
--

DROP TABLE IF EXISTS `disciplines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `disciplines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `abbreviation` varchar(16) DEFAULT NULL,
  `department_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `department_id` (`department_id`),
  CONSTRAINT `disciplines_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disciplines`
--

LOCK TABLES `disciplines` WRITE;
/*!40000 ALTER TABLE `disciplines` DISABLE KEYS */;
INSERT INTO `disciplines` VALUES (1,'2019-01-04 23:27:11','2019-01-10 16:31:40',0,NULL,'Разработка защищённых веб-приложений','РЗВП',1),(2,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,'Алгоритмизация и программирование','АиП',1),(3,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,'Основы информационных сетей','ОИС',1),(4,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,'Системы хранения данных','СХД',1),(5,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,'Архитектура информационных систем','АИС',1);
/*!40000 ALTER TABLE `disciplines` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `emails_views`
--

DROP TABLE IF EXISTS `emails_views`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `emails_views` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `contact_info_id` int(11) DEFAULT NULL,
  `data_view_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `contact_info_id` (`contact_info_id`),
  KEY `data_view_id` (`data_view_id`),
  CONSTRAINT `emails_views_ibfk_1` FOREIGN KEY (`contact_info_id`) REFERENCES `contacts` (`id`),
  CONSTRAINT `emails_views_ibfk_2` FOREIGN KEY (`data_view_id`) REFERENCES `data_views` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `emails_views`
--

LOCK TABLES `emails_views` WRITE;
/*!40000 ALTER TABLE `emails_views` DISABLE KEYS */;
INSERT INTO `emails_views` VALUES (1,'2019-03-07 18:25:07',NULL,NULL,NULL,1,1);
/*!40000 ALTER TABLE `emails_views` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculties`
--

DROP TABLE IF EXISTS `faculties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `faculties` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `abbreviation` varchar(16) DEFAULT NULL,
  `contact_info_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `contact_info_id` (`contact_info_id`),
  CONSTRAINT `faculties_ibfk_1` FOREIGN KEY (`contact_info_id`) REFERENCES `contacts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculties`
--

LOCK TABLES `faculties` WRITE;
/*!40000 ALTER TABLE `faculties` DISABLE KEYS */;
INSERT INTO `faculties` VALUES (1,'Факультет Информационных Систем и Технологий','ИСиТ',NULL),(2,'Факультет Фундаментальной подготовки','ФП',1);
/*!40000 ALTER TABLE `faculties` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty_administrations`
--

DROP TABLE IF EXISTS `faculty_administrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `faculty_administrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Faculty` int(11) DEFAULT NULL,
  `Administration` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `Faculty` (`Faculty`),
  KEY `Administration` (`Administration`),
  CONSTRAINT `faculty_administrations_ibfk_1` FOREIGN KEY (`Faculty`) REFERENCES `faculties` (`id`),
  CONSTRAINT `faculty_administrations_ibfk_2` FOREIGN KEY (`Administration`) REFERENCES `administrations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty_administrations`
--

LOCK TABLES `faculty_administrations` WRITE;
/*!40000 ALTER TABLE `faculty_administrations` DISABLE KEYS */;
/*!40000 ALTER TABLE `faculty_administrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `abbreviation` varchar(16) DEFAULT NULL,
  `faculty_id` int(11) DEFAULT NULL,
  `contact_info_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `faculty_id` (`faculty_id`),
  KEY `contact_info_id` (`contact_info_id`),
  CONSTRAINT `groups_ibfk_1` FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`id`),
  CONSTRAINT `groups_ibfk_2` FOREIGN KEY (`contact_info_id`) REFERENCES `contacts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'2019-01-04 23:27:17','2019-01-10 16:31:40',0,NULL,'ИСТ-621',NULL,1,NULL),(2,'2019-01-04 23:27:17','2019-01-10 16:31:40',0,NULL,'ИСТ-622',NULL,1,NULL),(3,'2019-01-04 23:27:17','2019-01-10 16:31:40',0,NULL,'ИСТ-632',NULL,1,NULL),(4,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,'ФП-81',NULL,2,NULL),(19,'2019-02-27 01:20:12','2019-02-27 01:20:12',0,NULL,'ФП-51',NULL,2,NULL);
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lessons`
--

DROP TABLE IF EXISTS `lessons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lessons` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `professor_id` int(11) NOT NULL,
  `discipline_id` int(11) NOT NULL,
  `type` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `completed` tinyint(1) NOT NULL,
  `room_id` varchar(40) NOT NULL,
  `semester_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lesson_UK` (`professor_id`,`date`),
  UNIQUE KEY `id` (`id`),
  KEY `discipline_id` (`discipline_id`),
  KEY `semester` (`semester_id`),
  CONSTRAINT `lessons_ibfk_1` FOREIGN KEY (`professor_id`) REFERENCES `professors` (`id`),
  CONSTRAINT `lessons_ibfk_2` FOREIGN KEY (`discipline_id`) REFERENCES `disciplines` (`id`),
  CONSTRAINT `lessons_ibfk_3` FOREIGN KEY (`semester_id`) REFERENCES `semesters` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=895 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lessons`
--

LOCK TABLES `lessons` WRITE;
/*!40000 ALTER TABLE `lessons` DISABLE KEYS */;
INSERT INTO `lessons` VALUES (1,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,1,'2018-09-13 13:00:00',1,'205',1),(2,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,1,'2018-09-27 13:00:00',1,'205',1),(3,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,1,'2018-10-11 13:00:00',1,'205',1),(4,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,1,'2018-10-25 13:00:00',1,'205',1),(5,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,1,'2018-11-07 13:00:00',1,'205',1),(6,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-11-22 13:00:00',0,'205',1),(7,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-12-06 13:00:00',0,'205',1),(8,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-12-20 13:00:00',0,'205',1),(9,'2019-01-04 23:28:02','2019-01-10 17:20:30',0,NULL,1,1,0,'2018-09-06 14:45:00',1,'511',1),(10,'2019-01-04 23:28:02','2019-01-10 17:20:30',0,NULL,1,1,0,'2018-09-13 14:45:00',1,'511',1),(11,'2019-01-04 23:28:02','2019-01-10 17:20:30',0,NULL,1,1,0,'2018-09-20 14:45:00',1,'511',1),(12,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,0,'2018-09-27 14:45:00',1,'511',1),(13,'2019-01-04 23:28:02','2019-01-10 17:20:30',0,NULL,1,1,0,'2018-10-04 14:45:00',1,'511',1),(14,'2019-01-04 23:28:02','2019-01-10 17:20:30',0,NULL,1,1,0,'2018-10-11 14:45:00',1,'511',1),(16,'2019-01-04 23:28:02','2019-01-10 17:20:30',0,NULL,1,1,0,'2018-10-25 14:45:00',1,'511',1),(17,'2019-01-04 23:28:02','2019-01-10 17:20:30',0,NULL,1,1,0,'2018-11-01 14:45:00',1,'511',1),(18,'2019-01-04 23:28:02','2019-01-10 17:20:30',0,NULL,1,1,0,'2018-11-08 14:45:00',1,'511',1),(19,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,0,'2018-11-15 14:45:00',0,'511',1),(20,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,0,'2018-11-22 14:45:00',0,'511',1),(21,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,0,'2018-11-29 14:45:00',0,'511',1),(22,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,0,'2018-12-06 14:45:00',0,'511',1),(23,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,0,'2018-12-13 14:45:00',0,'511',1),(24,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,0,'2018-12-20 14:45:00',0,'511',1),(25,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,0,'2018-12-27 14:45:00',0,'511',1),(26,'2019-01-04 23:28:02','2019-01-10 17:20:30',0,NULL,1,1,0,'2018-09-06 16:30:00',1,'511',1),(27,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,2,'2018-09-13 16:30:00',1,'205',1),(28,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-09-20 16:30:00',0,'205',1),(29,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,2,'2018-09-27 16:30:00',1,'205',1),(30,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,2,'2018-10-04 16:30:00',1,'205',1),(31,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,2,'2018-10-11 16:30:00',1,'205',1),(32,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,2,'2018-10-18 16:30:00',1,'205',1),(33,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,2,'2018-10-25 16:30:00',1,'205',1),(34,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,2,'2018-11-01 16:30:00',1,'205',1),(35,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,2,'2018-11-08 16:30:00',1,'205',1),(36,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-11-15 16:30:00',0,'205',1),(37,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-11-22 16:30:00',0,'205',1),(38,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-11-29 16:30:00',0,'205',1),(39,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-12-06 16:30:00',0,'205',1),(40,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-12-13 16:30:00',0,'205',1),(41,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-12-20 16:30:00',0,'205',1),(42,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-12-27 16:30:00',0,'205',1),(43,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,1,'2018-09-22 16:30:00',1,'205',1),(44,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,2,'2018-09-18 16:30:00',1,'205',1),(45,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,1,'2018-09-05 09:00:00',1,'203',1),(46,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,1,'2018-09-19 09:00:00',1,'203',1),(47,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,1,'2018-10-03 09:00:00',1,'203',1),(48,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,1,'2018-10-17 09:00:00',1,'203',1),(49,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,1,'2018-10-31 09:00:00',1,'203',1),(50,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-11-14 09:00:00',0,'203',1),(51,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-11-28 09:00:00',0,'203',1),(52,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-12-12 09:00:00',0,'203',1),(53,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-12-26 09:00:00',0,'203',1),(54,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,2,'2018-09-12 13:00:00',1,'203',1),(56,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,2,'2018-10-10 13:00:00',1,'203',1),(57,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,2,'2018-10-24 13:00:00',1,'203',1),(58,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,2,'2018-11-06 13:00:00',1,'203',1),(59,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-11-21 13:00:00',0,'203',1),(60,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-12-05 13:00:00',0,'203',1),(61,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-12-19 13:00:00',0,'203',1),(62,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,2,'2018-09-12 14:45:00',1,'203',1),(64,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,2,'2018-10-10 14:45:00',1,'203',1),(65,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,2,'2018-10-24 14:45:00',1,'203',1),(66,'2019-01-04 23:28:02','2019-01-10 17:20:23',0,NULL,1,1,2,'2018-11-07 14:45:00',1,'203',1),(67,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-11-21 14:45:00',0,'203',1),(68,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-12-05 14:45:00',0,'203',1),(69,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-12-19 14:45:00',0,'203',1),(88,'2019-01-04 23:28:02','2019-01-10 17:20:20',0,NULL,1,1,1,'2018-09-22 13:00:00',1,'205',1),(89,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,2,'2018-09-05 10:45:00',1,'203',1),(90,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,2,'2018-09-12 10:45:00',1,'203',1),(91,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,2,'2018-09-19 10:45:00',1,'203',1),(92,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,2,'2018-09-26 10:45:00',1,'203',1),(93,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,2,'2018-10-03 10:45:00',1,'203',1),(94,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,2,'2018-10-10 10:45:00',1,'203',1),(95,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,2,'2018-10-17 10:45:00',1,'203',1),(96,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,2,'2018-10-24 10:45:00',1,'203',1),(97,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-10-31 10:45:00',0,'203',1),(98,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,2,'2018-11-07 10:45:00',1,'203',1),(99,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-11-14 10:45:00',0,'203',1),(100,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-11-21 10:45:00',0,'203',1),(101,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-11-28 10:45:00',0,'203',1),(102,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-12-05 10:45:00',0,'203',1),(103,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-12-12 10:45:00',0,'203',1),(104,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,2,'2018-12-19 10:45:00',0,'203',1),(105,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-12-26 10:45:00',0,'203',1),(106,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,1,'2018-09-05 13:00:00',1,'203',1),(107,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,1,'2018-09-19 13:00:00',1,'203',1),(108,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,1,'2018-10-03 13:00:00',1,'203',1),(109,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,1,'2018-10-17 13:00:00',1,'203',1),(110,'2019-01-04 23:28:02','2019-01-10 17:20:26',0,NULL,1,1,1,'2018-10-31 13:00:00',1,'203',1),(111,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-11-14 13:00:00',0,'203',1),(112,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-11-28 13:00:00',0,'203',1),(113,'2019-01-04 23:28:02','2019-01-10 16:31:40',0,NULL,1,1,1,'2018-12-12 13:00:00',0,'203',1),(114,'2019-01-04 23:28:02','2019-01-06 16:32:01',0,NULL,1,1,1,'2018-12-26 13:00:00',0,'203',1),(115,'2019-02-14 19:41:46','2019-02-19 22:21:42',0,NULL,1,2,2,'2019-04-10 16:30:00',0,'',2),(116,'2019-02-14 19:41:46','2019-02-19 22:21:50',0,NULL,1,2,2,'2019-05-08 16:30:00',0,'',2),(117,'2019-02-14 19:41:46','2019-02-19 22:22:01',0,NULL,1,2,2,'2019-06-05 16:30:00',0,'',2),(118,'2019-02-14 19:41:46','2019-02-19 22:21:17',0,NULL,1,2,2,'2019-02-20 16:30:00',0,'',2),(119,'2019-02-14 19:41:46','2019-02-19 22:21:59',0,NULL,1,2,2,'2019-05-29 16:30:00',0,'',2),(120,'2019-02-14 19:41:46','2019-02-19 22:21:53',0,NULL,1,2,2,'2019-05-15 16:30:00',0,'',2),(121,'2019-02-14 19:41:46','2019-02-19 22:21:21',0,NULL,1,2,2,'2019-03-20 16:30:00',0,'',2),(122,'2019-02-14 19:41:46','2019-02-19 22:21:56',0,NULL,1,2,2,'2019-05-22 16:30:00',0,'',2),(123,'2019-02-14 19:41:46','2019-02-19 22:21:09',0,NULL,1,2,2,'2019-03-06 16:30:00',0,'',2),(124,'2019-02-14 19:41:46','2019-02-19 22:21:34',0,NULL,1,2,2,'2019-03-27 16:30:00',0,'',2),(125,'2019-02-14 19:41:46','2019-02-19 22:21:45',0,NULL,1,2,2,'2019-04-17 16:30:00',0,'',2),(126,'2019-02-14 19:41:46','2019-02-19 22:21:38',0,NULL,1,2,2,'2019-04-03 16:30:00',0,'',2),(127,'2019-02-14 19:41:46','2019-02-19 22:21:04',0,NULL,1,2,2,'2019-03-13 16:30:00',0,'',2),(128,'2019-02-14 19:41:46','2019-02-19 22:21:48',0,NULL,1,2,2,'2019-04-24 16:30:00',0,'',2),(129,'2019-02-14 19:41:46','2019-02-19 22:21:13',0,NULL,1,2,2,'2019-02-27 16:30:00',0,'',2);
/*!40000 ALTER TABLE `lessons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lessons_groups`
--

DROP TABLE IF EXISTS `lessons_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lessons_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `lesson_id` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `lesson_groups_UK` (`lesson_id`,`group_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `lessons_groups_ibfk_1` FOREIGN KEY (`lesson_id`) REFERENCES `lessons` (`id`),
  CONSTRAINT `lessons_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=676 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lessons_groups`
--

LOCK TABLES `lessons_groups` WRITE;
/*!40000 ALTER TABLE `lessons_groups` DISABLE KEYS */;
INSERT INTO `lessons_groups` VALUES (1,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,42,1),(2,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,25,1),(3,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,25,2),(4,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,25,3),(5,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,114,3),(6,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,105,3),(7,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,53,2),(8,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,41,1),(9,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,24,1),(10,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,24,2),(11,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,24,3),(12,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,23,1),(13,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,23,2),(14,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,23,3),(15,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,22,1),(16,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,22,2),(17,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,22,3),(18,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,21,1),(19,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,21,2),(20,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,21,3),(21,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,20,1),(22,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,20,2),(23,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,20,3),(24,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,19,1),(25,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,19,2),(26,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,19,3),(27,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,18,1),(28,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,18,2),(29,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,18,3),(30,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,17,1),(31,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,17,2),(32,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,17,3),(33,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,16,1),(34,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,16,2),(35,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,16,3),(39,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,14,1),(40,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,14,2),(41,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,14,3),(42,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,13,1),(43,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,13,2),(44,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,13,3),(45,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,12,1),(46,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,12,2),(47,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,12,3),(48,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,11,1),(49,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,11,2),(50,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,11,3),(51,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,10,1),(52,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,10,2),(53,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,10,3),(54,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,9,1),(55,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,9,2),(56,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,9,3),(57,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,26,1),(58,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,26,2),(59,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,26,3),(60,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,1,1),(61,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,2,1),(62,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,3,1),(63,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,4,1),(64,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,5,1),(65,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,6,1),(66,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,7,1),(67,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,8,1),(68,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,43,1),(69,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,45,2),(70,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,46,2),(71,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,47,2),(72,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,48,2),(73,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,49,2),(74,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,50,2),(75,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,51,2),(76,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,52,2),(77,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,88,1),(78,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,106,3),(79,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,107,3),(80,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,108,3),(81,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,109,3),(82,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,110,3),(83,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,111,3),(84,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,112,3),(86,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,89,3),(87,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,90,3),(88,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,91,3),(89,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,92,3),(90,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,93,3),(91,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,94,3),(92,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,95,3),(93,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,96,3),(94,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,97,3),(95,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,98,3),(96,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,99,3),(97,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,100,3),(98,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,101,3),(99,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,102,3),(100,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,103,3),(101,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,104,3),(102,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,54,2),(104,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,56,2),(105,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,57,2),(106,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,58,2),(107,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,59,2),(108,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,60,2),(109,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,61,2),(110,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,62,2),(112,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,64,2),(113,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,65,2),(114,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,66,2),(115,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,67,2),(116,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,68,2),(117,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,69,2),(118,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,27,1),(119,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,28,1),(120,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,29,1),(121,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,30,1),(122,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,31,1),(123,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,32,1),(124,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,33,1),(125,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,34,1),(126,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,35,1),(127,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,36,1),(128,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,37,1),(129,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,38,1),(130,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,39,1),(131,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,40,1),(132,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,44,1),(133,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,122,4),(134,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,128,4),(135,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,123,4),(136,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,121,4),(137,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,117,4),(138,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,116,4),(139,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,118,4),(140,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,120,4),(141,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,126,4),(142,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,127,4),(143,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,115,4),(144,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,124,4),(145,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,119,4),(146,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,125,4),(147,'2019-02-14 19:41:46','2019-02-14 19:41:46',0,NULL,129,4),(675,'2019-01-04 23:28:04','2019-01-10 16:31:40',0,NULL,113,3);
/*!40000 ALTER TABLE `lessons_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parents`
--

DROP TABLE IF EXISTS `parents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `parents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `last_name` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `middle_name` varchar(50) DEFAULT NULL,
  `card_id` varchar(16) DEFAULT NULL,
  `contact_info_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `card_id` (`card_id`),
  KEY `contact_info_id` (`contact_info_id`),
  CONSTRAINT `parents_ibfk_1` FOREIGN KEY (`contact_info_id`) REFERENCES `contacts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parents`
--

LOCK TABLES `parents` WRITE;
/*!40000 ALTER TABLE `parents` DISABLE KEYS */;
/*!40000 ALTER TABLE `parents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professors`
--

DROP TABLE IF EXISTS `professors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `professors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `last_name` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `middle_name` varchar(50) DEFAULT NULL,
  `card_id` varchar(16) DEFAULT NULL,
  `_last_update_in` datetime DEFAULT NULL,
  `_last_update_out` datetime DEFAULT NULL,
  `contact_info_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `card_id` (`card_id`),
  KEY `contact_info_id` (`contact_info_id`),
  CONSTRAINT `professors_ibfk_1` FOREIGN KEY (`contact_info_id`) REFERENCES `contacts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professors`
--

LOCK TABLES `professors` WRITE;
/*!40000 ALTER TABLE `professors` DISABLE KEYS */;
INSERT INTO `professors` VALUES (1,'2019-01-04 23:15:54','2019-01-10 05:13:07',0,NULL,'Евстигнеев','Валерий','Александрович',NULL,NULL,'2008-01-01 00:00:00',NULL),(2,'2019-01-04 23:15:54','2019-01-10 05:13:07',0,NULL,'Иванов','Иван','Иванович',NULL,NULL,'2008-01-01 00:00:00',NULL);
/*!40000 ALTER TABLE `professors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `semesters`
--

DROP TABLE IF EXISTS `semesters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `semesters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `start_date` datetime NOT NULL,
  `first_week_index` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `start_date` (`start_date`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semesters`
--

LOCK TABLES `semesters` WRITE;
/*!40000 ALTER TABLE `semesters` DISABLE KEYS */;
INSERT INTO `semesters` VALUES (1,'2018-09-01 00:00:00',0),(2,'2019-02-11 00:00:00',0),(3,'2016-09-01 00:00:00',1);
/*!40000 ALTER TABLE `semesters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `students` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `last_name` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `middle_name` varchar(50) DEFAULT NULL,
  `card_id` varchar(16) DEFAULT NULL,
  `contact_info_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `card_id` (`card_id`),
  KEY `contact_info_id` (`contact_info_id`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`contact_info_id`) REFERENCES `contacts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=214 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (1,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Бабицкий','Евгений','Михайлович',NULL,NULL),(2,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Гетманова','Мария','Дмитриевна',NULL,NULL),(3,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Головина','Изабелла','Алексеевна',NULL,NULL),(4,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Данилова','Наталья','Александровна',NULL,NULL),(5,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Захаревич','Павел','Андреевич',NULL,NULL),(6,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Иванова','Диана','Евгеньевна',NULL,NULL),(7,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Иванова','Октябрина','Валерьевна',NULL,NULL),(8,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Лещев','Николай','Станиславович',NULL,NULL),(9,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Липкович','Денис','Вячеславович',NULL,NULL),(10,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Митусов','Алексей','Дмитриевич',NULL,NULL),(11,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Плахтюков','Дмитрий','Сергеевич',NULL,NULL),(12,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Поморцев','Данила','Аркадьевич',NULL,NULL),(13,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Савельева','Наталия','Андреевна',NULL,NULL),(14,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Смирнов','Никита','Сергеевич',NULL,NULL),(15,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Цветков','Илья','Александрович',NULL,NULL),(16,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Чепчугова','Нина','Алексеевна',NULL,NULL),(17,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Чуев','Денис','Сергеевич',NULL,NULL),(18,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Шеремет','Владимир','Александрович',NULL,NULL),(19,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Шерстобитова','Софья','Викторовна',NULL,NULL),(20,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Щербак','Владимир','Игоревич',NULL,NULL),(21,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Яковлев','Максим','Евгеньевич',NULL,NULL),(22,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Анчишкина','Лидия','Сергеевна',NULL,NULL),(23,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Атаманчук','Леонтий','Сергеевич',NULL,NULL),(24,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Баев','Вадим','Дмитриевич',NULL,NULL),(25,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Галицына','Полина','Сергеевна',NULL,NULL),(26,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Гончар','Илья','Олегович',NULL,NULL),(27,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Горячева','Анна','Станиславовна',NULL,NULL),(28,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Гуляков','Ярослав','Андреевич',NULL,NULL),(29,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Жук','Дарья','Васильевна',NULL,NULL),(30,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Жуков','Семен','Павлович',NULL,NULL),(31,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Игнатьева','Анастасия','Алексеевна',NULL,NULL),(32,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Ким','Данил','',NULL,NULL),(33,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Кокарев','Денис','Андреевич',NULL,NULL),(34,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Колесников','Иван','Сергеевич',NULL,NULL),(35,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Кревлев','Максим','Дмитриевич',NULL,NULL),(36,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Лебедева','Анастасия','Павловна',NULL,NULL),(37,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Лобазова','Ульяна','Павловна',NULL,NULL),(38,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Луканина','Анна','Васильевна',NULL,NULL),(39,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Нагорнов','Роман','Андреевич',NULL,NULL),(40,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Николаев','Валерий','Александрович',NULL,NULL),(41,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Орлова','Вероника','Алексеевна',NULL,NULL),(42,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Худайберенов','Максим','Батырович',NULL,NULL),(43,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Шунько','Анастасия','Константиновна',NULL,NULL),(44,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Алексеев','Андрей','Анатольевич',NULL,NULL),(45,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Андрусович','Никита','Витальевич',NULL,NULL),(46,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Базуева','Анастасия','Олеговна',NULL,NULL),(47,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Деменева','Дарья','Александровна',NULL,NULL),(48,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Друзенко','Виктория','Валерьевна',NULL,NULL),(49,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Егоренко','Дмитрий','Александрович',NULL,NULL),(50,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Зубин','Роман','Александрович',NULL,NULL),(51,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Кирпиченко','Дарья','Сергеевна',NULL,NULL),(52,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Козлов','Олег','Валерьевич',NULL,NULL),(53,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Корчик','Андрей','Викторович',NULL,NULL),(54,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Ксенофонтова','Алевтина','Дмитриевна',NULL,NULL),(55,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Лымаренко','Александра','Руслановна',NULL,NULL),(56,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Машков','Никита','Антонович',NULL,NULL),(57,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Могильный','Владислав','Анатольевич',NULL,NULL),(58,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Поленичкина','Елизавета','Дмитриевна',NULL,NULL),(59,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Фирсанова','Анастасия','Александровна',NULL,NULL),(60,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Хайдари','Джонатан','',NULL,NULL),(61,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Шаронов','Никита','Максимович',NULL,NULL),(63,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Андреев','Дмитрий','Алексеевич',NULL,NULL),(64,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Церенов','Мингиян','Олегович',NULL,NULL),(65,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Шумилова','Светлана','Игоревна',NULL,NULL),(66,'2019-01-04 23:27:52','2019-01-31 17:25:13',0,NULL,'Шур','Павел','Александрович',NULL,NULL),(67,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Мельников','Павел','Сергеевич',NULL,NULL),(68,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Зеленская','Надежда','Игоревна',NULL,NULL),(69,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Илларионов','Александр','Михайлович',NULL,NULL),(70,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Кудряшова','Светлана','Андреевна',NULL,NULL),(71,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Котышевский','Юрий','Сергеевич',NULL,NULL),(72,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Гулин','Андрей','Игоревич',NULL,NULL),(73,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Мокшин','Егор','Витальевич',NULL,NULL),(74,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Петровская','Полина','Эдуардовна',NULL,NULL),(75,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Герасимов','Глеб','Юрьевич',NULL,NULL),(76,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Бондарев','Михаил','Михайлович',NULL,NULL),(77,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Овчинников','Владислав','Алексеевич',NULL,NULL),(78,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Ефимов','Вадим','Андреевич',NULL,NULL),(79,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Колесник','Антон','Павлович',NULL,NULL),(80,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Рожко','Дмитрий','Алексеевич',NULL,NULL),(81,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Жолоб','Максим','Эдуардович',NULL,NULL),(82,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Богданов','Максим','Алексеевич',NULL,NULL),(83,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Алиев','Владислав','Русланович',NULL,NULL),(84,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Румянцева','Софья','Константиновна',NULL,NULL),(85,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Сауленко','Евгений','Павлович',NULL,NULL),(86,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Жикин','Сергей','Александрович',NULL,NULL),(87,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Киселев','Антон','Михайлович',NULL,NULL),(88,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Тимкина','Екатерина','Алексеевна',NULL,NULL),(89,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Смотров','Владислав','Юрьевич',NULL,NULL),(90,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Гиниятуллин','Александр','Эдуардович',NULL,NULL),(91,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Книгиницкий','Егор','Игоревич',NULL,NULL),(92,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Вдовиченко','Егор','Викторович',NULL,NULL),(93,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Терновая','Анастасия','Константиновна',NULL,NULL),(94,'2019-02-14 20:18:03','2019-02-14 20:18:03',0,NULL,'Вихров','Семен','Евгеньевич',NULL,NULL),(195,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Акум','Ахмад','',NULL,NULL),(196,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Амонов','Жасурбек','Назирович',NULL,NULL),(197,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Байрамов','Нарыман','Бахрамжанивич',NULL,NULL),(198,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Ващенко','Святослав','Дмитриевич',NULL,NULL),(199,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Жауад','Саад','',NULL,NULL),(200,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Гафоров','Рустамджон','Абдусатторович',NULL,NULL),(201,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Зориков','Антон','Станиславович',NULL,NULL),(202,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Зуева','Екатерина','Дмитриевна',NULL,NULL),(203,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Коновалова','Елизавета','Александровна',NULL,NULL),(204,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Ларьков','Евгений','Юрьевич',NULL,NULL),(205,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Леонтьев','Александр','Сергеевич',NULL,NULL),(206,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Летамба','Валтер','Аликс',NULL,NULL),(207,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Мугу','Лилия','Рашидовна',NULL,NULL),(208,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Музаффаров','Хасан','Джалолович',NULL,NULL),(209,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Подольская','Мария','Олеговна',NULL,NULL),(210,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Рожков','Анатолий','Максимович',NULL,NULL),(211,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Синичкин','Александр','Александрович',NULL,NULL),(212,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Хайдар','Фаузи','Нассер',NULL,NULL),(213,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,'Цыганков','Григорий','Антонович',NULL,NULL);
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students_groups`
--

DROP TABLE IF EXISTS `students_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `students_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `student_id` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `students_groups_UK` (`student_id`,`group_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `students_groups_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `students_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=214 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students_groups`
--

LOCK TABLES `students_groups` WRITE;
/*!40000 ALTER TABLE `students_groups` DISABLE KEYS */;
INSERT INTO `students_groups` VALUES (1,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,63,1),(2,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,1,1),(3,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,2,1),(4,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,3,1),(5,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,4,1),(6,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,5,1),(7,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,6,1),(8,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,7,1),(9,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,8,1),(10,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,9,1),(11,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,10,1),(12,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,11,1),(13,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,12,1),(14,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,13,1),(15,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,14,1),(16,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,15,1),(17,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,16,1),(18,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,17,1),(19,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,18,1),(20,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,19,1),(21,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,20,1),(22,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,21,2),(23,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,22,2),(24,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,23,2),(25,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,24,2),(26,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,25,2),(27,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,26,2),(28,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,27,2),(29,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,28,2),(30,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,29,2),(31,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,30,2),(32,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,31,2),(33,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,32,2),(34,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,33,2),(35,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,34,2),(36,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,35,2),(37,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,36,2),(38,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,37,2),(39,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,38,2),(40,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,39,2),(41,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,40,2),(42,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,41,2),(43,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,42,2),(44,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,43,2),(45,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,44,3),(46,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,45,3),(47,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,46,3),(48,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,47,3),(49,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,48,3),(50,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,49,3),(51,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,50,3),(52,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,51,3),(53,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,52,3),(54,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,53,3),(55,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,54,3),(56,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,55,3),(57,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,56,3),(58,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,57,3),(59,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,58,3),(60,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,59,3),(61,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,60,3),(62,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,61,3),(64,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,64,2),(65,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,65,3),(66,'2019-01-04 23:28:07','2019-01-10 16:31:40',0,NULL,66,3),(67,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,88,4),(68,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,83,4),(69,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,69,4),(70,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,77,4),(71,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,73,4),(72,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,74,4),(73,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,86,4),(74,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,67,4),(75,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,75,4),(76,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,91,4),(77,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,82,4),(78,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,89,4),(79,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,87,4),(80,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,71,4),(81,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,90,4),(82,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,81,4),(83,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,84,4),(84,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,72,4),(85,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,80,4),(86,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,76,4),(87,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,70,4),(88,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,93,4),(89,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,94,4),(90,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,79,4),(91,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,68,4),(92,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,85,4),(93,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,78,4),(94,'2019-02-14 20:26:02','2019-02-14 20:26:02',0,NULL,92,4),(195,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,195,19),(196,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,196,19),(197,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,197,19),(198,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,198,19),(199,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,199,19),(200,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,200,19),(201,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,201,19),(202,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,202,19),(203,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,203,19),(204,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,204,19),(205,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,205,19),(206,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,206,19),(207,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,207,19),(208,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,208,19),(209,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,209,19),(210,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,210,19),(211,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,211,19),(212,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,212,19),(213,'2019-02-27 01:20:27','2019-02-27 01:20:27',0,NULL,213,19);
/*!40000 ALTER TABLE `students_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students_parents`
--

DROP TABLE IF EXISTS `students_parents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `students_parents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `student_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `student_parent_UK` (`parent_id`,`student_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `students_parents_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `parents` (`id`),
  CONSTRAINT `students_parents_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students_parents`
--

LOCK TABLES `students_parents` WRITE;
/*!40000 ALTER TABLE `students_parents` DISABLE KEYS */;
/*!40000 ALTER TABLE `students_parents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `visitations`
--

DROP TABLE IF EXISTS `visitations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_created` datetime DEFAULT NULL,
  `_updated` datetime DEFAULT NULL,
  `_is_deleted` tinyint(1) DEFAULT NULL,
  `_deleted` datetime DEFAULT NULL,
  `student_id` int(11) DEFAULT NULL,
  `lesson_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `visitation_UK` (`student_id`,`lesson_id`),
  KEY `lesson_id` (`lesson_id`),
  CONSTRAINT `visitations_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `visitations_ibfk_2` FOREIGN KEY (`lesson_id`) REFERENCES `lessons` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18136 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `visitations`
--

LOCK TABLES `visitations` WRITE;
/*!40000 ALTER TABLE `visitations` DISABLE KEYS */;
INSERT INTO `visitations` VALUES (17079,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,22,11),(17080,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,47,96),(17081,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,91),(17082,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,14,16),(17083,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,51,108),(17084,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,108),(17085,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,46),(17086,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,92),(17087,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,8,13),(17088,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,22,14),(17089,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,22,26),(17090,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,6,17),(17091,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,12,88),(17092,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,88),(17093,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,26,10),(17094,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,48),(17095,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,17,12),(17096,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,16,44),(17097,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,66,11),(17098,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,60,110),(17099,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,4),(17100,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,18,26),(17101,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,58),(17102,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,48,10),(17103,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,13,18),(17104,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,11,17),(17105,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,30,58),(17106,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,33,58),(17107,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,39,47),(17108,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,29),(17109,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,33),(17110,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,55,92),(17111,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,40,58),(17112,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,20,29),(17113,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,13,17),(17114,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,25,64),(17115,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,59,26),(17116,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,59,18),(17117,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,52,12),(17118,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,1),(17119,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,98),(17120,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,39,18),(17121,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,34,16),(17122,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,41,58),(17123,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,5,33),(17124,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,48),(17125,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,5),(17126,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,109),(17127,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,57),(17128,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,48),(17129,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,108),(17130,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,33,46),(17131,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,89),(17132,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,25,46),(17133,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,50,9),(17134,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,17,14),(17135,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,1,13),(17136,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,2),(17137,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,88),(17138,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,60,11),(17139,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,8,2),(17140,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,35,9),(17141,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,1,18),(17142,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,28,18),(17143,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,106),(17144,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,56),(17145,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,33,56),(17146,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,18,17),(17147,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,55,98),(17148,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,14,26),(17149,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,45,109),(17150,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,44,10),(17151,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,33,54),(17152,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,90),(17153,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,20,17),(17154,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,58),(17155,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,55,13),(17156,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,33,47),(17157,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,59,108),(17158,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,27),(17159,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,49,13),(17160,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,3,27),(17161,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,38,62),(17162,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,43),(17163,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,32,10),(17164,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,39,62),(17165,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,107),(17166,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,40,18),(17167,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,66,9),(17168,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,30,66),(17169,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,56),(17170,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,41,12),(17171,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,42,26),(17172,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,6,12),(17173,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,41,65),(17174,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,43),(17175,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,40,12),(17176,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,46,89),(17177,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,28,17),(17178,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,35),(17179,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,35),(17180,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,31,64),(17181,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,57,10),(17182,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,6,11),(17183,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,3,1),(17184,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,10,29),(17185,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,98),(17186,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,12,18),(17187,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,7,18),(17188,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,30),(17189,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,60,108),(17190,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,66,26),(17191,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,47,89),(17192,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,2),(17193,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,47,11),(17194,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,1),(17195,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,37,62),(17196,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,53,12),(17197,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,54,10),(17198,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,9,5),(17199,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,64),(17200,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,93),(17201,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,93),(17202,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,15,17),(17203,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,32),(17204,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,90),(17205,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,27,58),(17206,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,109),(17207,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,89),(17208,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,30),(17209,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,33,64),(17210,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,47,94),(17211,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,47),(17212,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,40,46),(17213,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,25,10),(17214,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,39,65),(17215,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,1,11),(17216,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,5,88),(17217,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,19,26),(17218,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,53,16),(17219,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,32),(17220,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,3),(17221,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,91),(17222,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,4,18),(17223,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,60,95),(17224,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,35,12),(17225,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,8,1),(17226,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,60,14),(17227,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,60,98),(17228,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,10,31),(17229,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,3,9),(17230,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,43,45),(17231,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,41,17),(17232,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,96),(17233,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,20,88),(17234,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,60,17),(17235,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,53,17),(17236,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,57,9),(17237,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,46),(17238,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,45),(17239,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,50,18),(17240,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,20,30),(17241,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,93),(17242,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,20,43),(17243,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,13,11),(17244,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,29),(17245,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,18,12),(17246,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,3),(17247,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,27),(17248,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,4),(17249,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,35,65),(17250,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,35,13),(17251,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,12,11),(17252,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,60,94),(17253,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,3,13),(17254,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,7,9),(17255,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,6,10),(17256,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,64,64),(17257,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,10,27),(17258,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,106),(17259,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,34,18),(17260,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,51,17),(17261,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,65,12),(17262,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,16,2),(17263,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,59,92),(17264,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,91),(17265,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,108),(17266,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,98),(17267,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,98),(17268,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,58),(17269,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,55,17),(17270,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,9,1),(17271,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,48,14),(17272,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,91),(17273,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,90),(17274,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,44),(17275,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,20,10),(17276,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,95),(17277,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,35,47),(17278,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,13,16),(17279,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,40,9),(17280,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,57,18),(17281,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,10,3),(17282,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,92),(17283,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,9,2),(17284,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,27,14),(17285,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,35,45),(17286,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,60,16),(17287,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,9,10),(17288,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,8,16),(17289,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,1,14),(17290,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,51,95),(17291,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,34),(17292,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,25,16),(17293,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,42,16),(17294,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,110),(17295,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,4),(17296,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,95),(17297,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,47,9),(17298,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,17,29),(17299,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,45),(17300,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,30),(17301,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,54,17),(17302,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,32),(17303,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,47),(17304,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,19,10),(17305,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,11,16),(17306,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,48,12),(17307,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,44,95),(17308,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,33,45),(17309,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,88),(17310,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,37,45),(17311,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,66,14),(17312,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,44),(17313,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,9,44),(17314,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,44),(17315,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,35),(17316,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,4,11),(17317,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,94),(17318,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,65),(17319,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,2),(17320,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,89),(17321,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,18,11),(17322,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,3),(17323,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,1),(17324,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,56),(17325,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,16,27),(17326,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,47,92),(17327,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,20,12),(17328,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,10,1),(17329,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,92),(17330,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,33,18),(17331,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,96),(17332,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,20,1),(17333,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,29),(17334,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,98),(17335,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,32),(17336,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,12),(17337,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,46,92),(17338,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,93),(17339,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,2),(17340,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,44),(17341,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,43,10),(17342,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,61,107),(17343,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,32,57),(17344,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,65),(17345,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,106),(17346,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,25,62),(17347,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,109),(17348,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,42,9),(17349,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,11,9),(17350,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,11,11),(17351,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,11,10),(17352,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,9,43),(17353,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,41,46),(17354,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,12,10),(17355,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,55,18),(17356,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,40,57),(17357,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,94),(17358,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,40,49),(17359,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,91),(17360,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,27,45),(17361,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,2),(17362,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,98),(17363,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,12,30),(17364,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,95),(17365,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,40,66),(17366,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,92),(17367,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,48,13),(17368,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,88),(17369,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,3,88),(17370,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,91),(17371,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,59,9),(17372,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,47,17),(17373,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,31,46),(17374,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,38,16),(17375,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,59,10),(17376,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,8,29),(17377,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,96),(17378,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,43,62),(17379,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,15,9),(17380,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,58,14),(17381,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,54),(17382,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,3,10),(17383,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,62),(17384,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,66),(17385,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,108),(17386,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,36,47),(17387,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,18,13),(17388,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,4),(17389,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,89),(17390,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,108),(17391,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,108),(17392,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,7,12),(17393,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,94),(17394,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,23,48),(17395,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,36,11),(17396,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,65,9),(17397,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,59,109),(17398,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,24,26),(17399,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,62),(17400,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,11,18),(17401,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,62),(17402,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,13,14),(17403,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,55,94),(17404,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,16,43),(17405,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,66),(17406,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,30),(17407,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,38,18),(17408,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,58,13),(17409,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,10,5),(17410,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,88),(17411,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,89),(17412,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,95),(17413,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,65,17),(17414,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,7,13),(17415,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,60,93),(17416,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,107),(17417,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,45,106),(17418,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,12),(17419,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,19,2),(17420,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,14,11),(17421,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,52,10),(17422,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,50,13),(17423,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,45,107),(17424,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,41,66),(17425,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,5,43),(17426,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,3,11),(17427,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,34),(17428,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,6,16),(17429,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,47),(17430,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,51,107),(17431,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,58),(17432,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,54,16),(17433,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,42,10),(17434,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,46,106),(17435,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,24,14),(17436,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,19,32),(17437,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,9,18),(17438,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,52,18),(17439,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,13,13),(17440,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,6,14),(17441,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,39,58),(17442,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,34),(17443,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,12,14),(17444,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,51,12),(17445,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,59,90),(17446,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,28,26),(17447,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,9,12),(17448,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,16,9),(17449,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,96),(17450,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,92),(17451,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,106),(17452,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,2),(17453,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,107),(17454,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,44,106),(17455,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,49),(17456,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,18,9),(17457,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,60,107),(17458,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,4,10),(17459,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,27,64),(17460,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,32),(17461,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,32,12),(17462,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,1),(17463,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,9,88),(17464,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,66),(17465,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,53,13),(17466,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,93),(17467,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,5,2),(17468,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,14,17),(17469,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,4,12),(17470,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,57,11),(17471,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,17,9),(17472,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,25,65),(17473,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,43,47),(17474,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,37,54),(17475,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,8,26),(17476,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,35),(17477,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,3,30),(17478,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,64,65),(17479,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,43),(17480,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,59,91),(17481,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,59,110),(17482,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,107),(17483,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,98),(17484,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,38,45),(17485,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,42,14),(17486,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,91),(17487,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,5),(17488,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,65,14),(17489,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,8,30),(17490,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,31),(17491,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,27,12),(17492,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,27,26),(17493,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,8,27),(17494,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,31,45),(17495,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,43,57),(17496,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,19,13),(17497,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,59,89),(17498,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,48),(17499,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,59,93),(17500,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,47),(17501,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,40,54),(17502,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,46,90),(17503,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,54,9),(17504,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,36,10),(17505,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,33,62),(17506,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,1),(17507,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,48,16),(17508,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,90),(17509,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,47,110),(17510,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,47,90),(17511,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,44,109),(17512,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,58,9),(17513,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,23,54),(17514,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,45,95),(17515,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,30),(17516,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,3,33),(17517,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,57,16),(17518,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,47,10),(17519,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,11,12),(17520,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,98),(17521,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,32,58),(17522,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,30,62),(17523,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,46,95),(17524,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,33,66),(17525,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,59,14),(17526,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,40,56),(17527,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,25,54),(17528,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,29),(17529,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,55,107),(17530,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,12),(17531,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,2),(17532,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,109),(17533,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,12,44),(17534,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,40,16),(17535,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,42,11),(17536,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,60,96),(17537,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,52,9),(17538,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,47,18),(17539,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,51,13),(17540,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,110),(17541,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,64,57),(17542,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,4,14),(17543,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,55,96),(17544,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,55,95),(17545,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,15,10),(17546,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,45,14),(17547,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,91),(17548,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,39,66),(17549,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,31,49),(17550,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,98),(17551,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,51,94),(17552,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,96),(17553,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,27),(17554,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,17,2),(17555,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,59,16),(17556,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,59,106),(17557,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,45),(17558,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,54,26),(17559,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,15,18),(17560,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,9,34),(17561,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,59,17),(17562,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,16,14),(17563,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,13,9),(17564,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,1),(17565,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,44),(17566,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,41,16),(17567,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,4),(17568,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,25,26),(17569,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,52,13),(17570,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,48,17),(17571,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,90),(17572,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,4),(17573,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,32),(17574,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,41,57),(17575,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,19,44),(17576,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,9,27),(17577,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,51,14),(17578,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,49,18),(17579,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,34),(17580,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,9,11),(17581,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,92),(17582,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,53,11),(17583,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,36,14),(17584,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,57,13),(17585,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,44),(17586,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,98),(17587,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,27,9),(17588,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,92),(17589,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,57),(17590,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,3,18),(17591,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,25,56),(17592,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,3,44),(17593,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,3,32),(17594,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,47,93),(17595,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,43),(17596,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,35,10),(17597,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,59,95),(17598,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,7,10),(17599,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,27),(17600,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,37,16),(17601,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,106),(17602,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,94),(17603,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,90),(17604,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,1,17),(17605,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,24,16),(17606,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,61,91),(17607,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,35,11),(17608,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,23,62),(17609,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,106),(17610,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,107),(17611,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,66,13),(17612,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,2),(17613,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,46,9),(17614,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,8,18),(17615,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,15,12),(17616,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,47,12),(17617,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,49),(17618,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,57,12),(17619,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,55,14),(17620,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,43),(17621,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,95),(17622,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,44),(17623,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,94),(17624,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,43,54),(17625,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,5,3),(17626,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,66,17),(17627,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,3,43),(17628,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,54,18),(17629,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,9,16),(17630,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,91),(17631,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,32,26),(17632,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,5,13),(17633,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,6,13),(17634,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,52,11),(17635,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,27,66),(17636,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,20,32),(17637,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,51,93),(17638,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,45,11),(17639,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,56,18),(17640,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,110),(17641,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,41,64),(17642,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,47),(17643,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,65,16),(17644,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,1),(17645,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,45,12),(17646,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,45,10),(17647,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,3),(17648,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,10,12),(17649,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,9,3),(17650,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,49,12),(17651,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,20,9),(17652,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,20,27),(17653,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,45,89),(17654,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,53,26),(17655,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,58,11),(17656,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,3),(17657,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,41,13),(17658,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,57,14),(17659,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,30),(17660,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,60,109),(17661,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,55,93),(17662,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,110),(17663,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,18,18),(17664,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,56,16),(17665,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,49,14),(17666,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,44,92),(17667,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,65,26),(17668,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,91),(17669,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,1),(17670,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,57),(17671,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,33),(17672,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,54,12),(17673,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,43,58),(17674,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,94),(17675,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,19,12),(17676,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,89),(17677,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,44,91),(17678,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,52,17),(17679,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,51,109),(17680,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,23,47),(17681,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,65,10),(17682,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,22,10),(17683,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,110),(17684,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,19,27),(17685,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,30),(17686,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,36,54),(17687,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,40,26),(17688,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,64),(17689,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,27),(17690,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,20,14),(17691,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,41,14),(17692,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,33,16),(17693,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,55,108),(17694,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,29),(17695,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,28,11),(17696,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,107),(17697,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,37,66),(17698,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,8,33),(17699,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,25,9),(17700,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,35,26),(17701,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,19,30),(17702,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,107),(17703,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,34),(17704,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,93),(17705,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,20,3),(17706,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,95),(17707,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,34),(17708,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,5,14),(17709,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,9,31),(17710,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,20,26),(17711,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,30,54),(17712,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,47,107),(17713,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,66,12),(17714,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,94),(17715,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,43),(17716,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,4),(17717,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,106),(17718,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,93),(17719,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,55,109),(17720,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,42,17),(17721,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,31),(17722,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,1,12),(17723,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,12,32),(17724,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,94),(17725,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,110),(17726,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,57,26),(17727,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,20,44),(17728,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,18,10),(17729,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,32),(17730,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,89),(17731,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,24,13),(17732,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,12,13),(17733,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,44,11),(17734,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,46,91),(17735,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,10,10),(17736,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,32,47),(17737,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,40,11),(17738,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,65),(17739,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,29),(17740,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,56,13),(17741,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,17,26),(17742,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,38,54),(17743,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,66,10),(17744,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,12,35),(17745,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,57,17),(17746,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,14,10),(17747,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,41,18),(17748,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,15,26),(17749,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,32,18),(17750,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,46,109),(17751,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,53,9),(17752,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,39,54),(17753,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,88),(17754,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,48,9),(17755,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,24,9),(17756,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,52,14),(17757,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,16,3),(17758,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,40,62),(17759,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,57),(17760,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,60,18),(17761,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,51,110),(17762,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,65),(17763,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,60,12),(17764,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,89),(17765,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,29),(17766,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,43),(17767,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,66),(17768,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,14,14),(17769,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,19,29),(17770,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,51,11),(17771,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,1,16),(17772,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,31,54),(17773,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,3),(17774,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,45,92),(17775,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,16,11),(17776,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,25,57),(17777,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,56,11),(17778,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,90),(17779,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,5),(17780,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,44,90),(17781,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,56,14),(17782,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,54),(17783,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,96),(17784,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,107),(17785,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,36,16),(17786,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,66,16),(17787,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,96),(17788,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,34,11),(17789,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,5),(17790,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,89),(17791,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,48,18),(17792,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,10,18),(17793,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,48,11),(17794,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,49,17),(17795,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,4,16),(17796,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,109),(17797,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,1,10),(17798,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,26,45),(17799,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,41,56),(17800,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,15,13),(17801,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,12,26),(17802,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,60,91),(17803,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,55,90),(17804,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,24,10),(17805,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,15,14),(17806,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,47,106),(17807,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,34),(17808,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,55,16),(17809,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,16,12),(17810,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,12,3),(17811,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,19,1),(17812,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,50,12),(17813,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,10,11),(17814,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,66),(17815,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,50,16),(17816,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,57),(17817,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,27,47),(17818,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,95),(17819,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,36,46),(17820,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,44,89),(17821,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,43),(17822,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,23,45),(17823,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,5),(17824,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,9,14),(17825,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,54),(17826,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,13,12),(17827,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,95),(17828,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,94),(17829,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,91),(17830,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,20,13),(17831,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,12,1),(17832,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,30,49),(17833,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,27),(17834,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,90),(17835,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,10,2),(17836,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,5,1),(17837,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,36,62),(17838,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,22,13),(17839,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,20,2),(17840,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,3,4),(17841,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,94),(17842,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,47,91),(17843,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,5,29),(17844,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,1,27),(17845,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,64),(17846,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,88),(17847,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,59,11),(17848,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,92),(17849,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,92),(17850,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,16,34),(17851,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,95),(17852,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,55,12),(17853,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,43,46),(17854,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,107),(17855,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,40,14),(17856,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,110),(17857,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,7,26),(17858,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,35),(17859,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,48,26),(17860,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,50,17),(17861,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,64,56),(17862,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,8,32),(17863,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,110),(17864,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,32,65),(17865,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,19,88),(17866,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,45,90),(17867,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,16,10),(17868,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,19,18),(17869,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,49,11),(17870,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,28,13),(17871,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,43,16),(17872,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,109),(17873,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,12),(17874,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,66,93),(17875,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,8,10),(17876,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,20,34),(17877,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,11,26),(17878,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,45),(17879,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,59,107),(17880,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,110),(17881,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,12,9),(17882,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,14,12),(17883,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,47,26),(17884,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,19,16),(17885,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,18,16),(17886,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,58,12),(17887,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,8,9),(17888,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,3,26),(17889,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,5,44),(17890,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,27,16),(17891,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,32,66),(17892,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,44,107),(17893,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,31),(17894,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,93),(17895,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,56,95),(17896,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,108),(17897,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,106),(17898,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,5,27),(17899,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,90),(17900,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,31,62),(17901,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,33),(17902,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,62),(17903,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,32,48),(17904,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,14,9),(17905,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,3,35),(17906,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,41,48),(17907,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,54,110),(17908,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,52,26),(17909,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,27),(17910,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,110),(17911,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,90),(17912,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,64,66),(17913,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,7,16),(17914,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,36,56),(17915,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,56),(17916,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,9,29),(17917,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,56,12),(17918,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,8,12),(17919,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,36,57),(17920,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,58,26),(17921,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,39,12),(17922,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,93),(17923,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,1),(17924,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,14,13),(17925,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,27,56),(17926,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,65),(17927,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,60,92),(17928,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,107),(17929,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,43,65),(17930,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,38,12),(17931,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,58,16),(17932,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,51,16),(17933,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,96),(17934,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,35,17),(17935,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,37,58),(17936,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,33),(17937,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,44,14),(17938,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,12,27),(17939,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,43,66),(17940,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,28,16),(17941,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,92),(17942,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,18,30),(17943,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,7,17),(17944,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,58,106),(17945,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,35,18),(17946,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,28,10),(17947,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,32),(17948,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,38,10),(17949,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,50,26),(17950,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,33,14),(17951,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,59,12),(17952,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,45,91),(17953,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,51,92),(17954,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,107),(17955,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,36,18),(17956,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,53,14),(17957,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,15,27),(17958,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,61,93),(17959,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,36,65),(17960,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,5,16),(17961,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,11,13),(17962,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,5,11),(17963,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,32,9),(17964,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,42,58),(17965,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,1,9),(17966,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,5,12),(17967,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,4,88),(17968,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,20,11),(17969,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,109),(17970,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,50,109),(17971,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,49,96),(17972,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,60,13),(17973,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,40,47),(17974,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,41,11),(17975,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,3),(17976,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,38,64),(17977,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,40,65),(17978,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,50,11),(17979,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,46,26),(17980,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,31),(17981,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,3,5),(17982,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,93),(17983,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,35),(17984,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,49),(17985,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,92),(17986,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,15,11),(17987,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,35,66),(17988,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,24,64),(17989,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,4,13),(17990,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,50,10),(17991,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,31,12),(17992,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,28,9),(17993,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,95),(17994,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,3,16),(17995,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,56),(17996,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,13,10),(17997,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,52,108),(17998,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,23,49),(17999,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,109),(18000,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,38,26),(18001,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,38,9),(18002,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,12,5),(18003,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,48,108),(18004,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,12,43),(18005,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,35,54),(18006,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,30,9),(18007,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,35,57),(18008,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,7,43),(18009,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,31),(18010,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,51,18),(18011,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,49),(18012,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,11,14),(18013,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,14,2),(18014,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,10,43),(18015,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,7,11),(18016,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,16,1),(18017,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,5,10),(18018,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,65,90),(18019,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,15,16),(18020,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,34,12),(18021,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,49,16),(18022,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,51,96),(18023,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,51,91),(18024,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,27,13),(18025,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,22,9),(18026,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,43,18),(18027,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,35,62),(18028,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,52,16),(18029,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,42,13),(18030,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,7,14),(18031,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,39,56),(18032,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,28,46),(18033,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,38,56),(18034,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,57,94),(18035,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,58,17),(18036,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,28,14),(18037,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,55,11),(18038,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,22,16),(18039,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,6,33),(18040,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,39,57),(18041,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,19,9),(18042,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,8,44),(18043,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,4),(18044,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,19,33),(18045,'2019-01-10 17:20:26','2019-01-10 17:20:26',0,NULL,53,96),(18046,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,13,29),(18047,'2019-01-10 17:20:30','2019-01-10 17:20:30',0,NULL,44,12),(18048,'2019-01-10 17:20:20','2019-01-10 17:20:20',0,NULL,11,29),(18049,'2019-01-10 17:20:23','2019-01-10 17:20:23',0,NULL,22,62);
/*!40000 ALTER TABLE `visitations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'bisitor_contacts'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-03-09 16:22:14
