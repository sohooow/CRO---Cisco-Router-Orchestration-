-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: orchestration_routeur
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add user',1,'add_user'),(2,'Can change user',1,'change_user'),(3,'Can delete user',1,'delete_user'),(4,'Can view user',1,'view_user'),(5,'Can add router',2,'add_router'),(6,'Can change router',2,'change_router'),(7,'Can delete router',2,'delete_router'),(8,'Can view router',2,'view_router'),(9,'Can add log',3,'add_log'),(10,'Can change log',3,'change_log'),(11,'Can delete log',3,'delete_log'),(12,'Can view log',3,'view_log'),(13,'Can add interface',4,'add_interface'),(14,'Can change interface',4,'change_interface'),(15,'Can delete interface',4,'delete_interface'),(16,'Can view interface',4,'view_interface'),(17,'Can add log entry',5,'add_logentry'),(18,'Can change log entry',5,'change_logentry'),(19,'Can delete log entry',5,'delete_logentry'),(20,'Can view log entry',5,'view_logentry'),(21,'Can add permission',6,'add_permission'),(22,'Can change permission',6,'change_permission'),(23,'Can delete permission',6,'delete_permission'),(24,'Can view permission',6,'view_permission'),(25,'Can add group',7,'add_group'),(26,'Can change group',7,'change_group'),(27,'Can delete group',7,'delete_group'),(28,'Can view group',7,'view_group'),(29,'Can add content type',8,'add_contenttype'),(30,'Can change content type',8,'change_contenttype'),(31,'Can delete content type',8,'delete_contenttype'),(32,'Can view content type',8,'view_contenttype'),(33,'Can add session',9,'add_session'),(34,'Can change session',9,'change_session'),(35,'Can delete session',9,'delete_session'),(36,'Can view session',9,'view_session');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_orchestration_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_orchestration_user_id` FOREIGN KEY (`user_id`) REFERENCES `orchestration_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (5,'admin','logentry'),(7,'auth','group'),(6,'auth','permission'),(8,'contenttypes','contenttype'),(4,'orchestration','interface'),(3,'orchestration','log'),(2,'orchestration','router'),(1,'orchestration','user'),(9,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-06-24 07:49:17.884165'),(2,'contenttypes','0002_remove_content_type_name','2025-06-24 07:49:18.026560'),(3,'auth','0001_initial','2025-06-24 07:49:18.554052'),(4,'auth','0002_alter_permission_name_max_length','2025-06-24 07:49:18.677079'),(5,'auth','0003_alter_user_email_max_length','2025-06-24 07:49:18.692763'),(6,'auth','0004_alter_user_username_opts','2025-06-24 07:49:18.708246'),(7,'auth','0005_alter_user_last_login_null','2025-06-24 07:49:18.728998'),(8,'auth','0006_require_contenttypes_0002','2025-06-24 07:49:18.734661'),(9,'auth','0007_alter_validators_add_error_messages','2025-06-24 07:49:18.751403'),(10,'auth','0008_alter_user_username_max_length','2025-06-24 07:49:18.770383'),(11,'auth','0009_alter_user_last_name_max_length','2025-06-24 07:49:18.789114'),(12,'auth','0010_alter_group_name_max_length','2025-06-24 07:49:18.826393'),(13,'auth','0011_update_proxy_permissions','2025-06-24 07:49:18.845359'),(14,'auth','0012_alter_user_first_name_max_length','2025-06-24 07:49:18.862216'),(15,'orchestration','0001_initial','2025-06-24 07:49:19.557709'),(16,'admin','0001_initial','2025-06-24 07:49:19.969347'),(17,'admin','0002_logentry_remove_auto_add','2025-06-24 07:49:19.987274'),(18,'admin','0003_logentry_add_action_flag_choices','2025-06-24 07:49:20.012341'),(19,'orchestration','0002_remove_router_interface_name_and_more','2025-06-24 07:49:21.389369'),(20,'orchestration','0003_log_user_delete_configuration','2025-06-24 07:49:21.556489'),(21,'orchestration','0004_alter_interface_status_alter_interface_subnet_mask_and_more','2025-06-24 07:49:21.703586'),(22,'orchestration','0005_alter_user_role','2025-06-24 07:49:21.721978'),(23,'sessions','0001_initial','2025-06-24 07:49:21.820388');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orchestration_interface`
--

DROP TABLE IF EXISTS `orchestration_interface`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orchestration_interface` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `ip_address` char(39) NOT NULL,
  `subnet_mask` varchar(39) NOT NULL,
  `status` varchar(100) NOT NULL,
  `router_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `orchestration_interf_router_id_4473d569_fk_orchestra` (`router_id`),
  CONSTRAINT `orchestration_interf_router_id_4473d569_fk_orchestra` FOREIGN KEY (`router_id`) REFERENCES `orchestration_router` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orchestration_interface`
--

LOCK TABLES `orchestration_interface` WRITE;
/*!40000 ALTER TABLE `orchestration_interface` DISABLE KEYS */;
/*!40000 ALTER TABLE `orchestration_interface` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orchestration_log`
--

DROP TABLE IF EXISTS `orchestration_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orchestration_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(100) NOT NULL,
  `router_id` bigint NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `orchestration_log_router_id_8003aedf_fk_orchestration_router_id` (`router_id`),
  KEY `orchestration_log_user_id_612211c0_fk_orchestration_user_id` (`user_id`),
  CONSTRAINT `orchestration_log_router_id_8003aedf_fk_orchestration_router_id` FOREIGN KEY (`router_id`) REFERENCES `orchestration_router` (`id`),
  CONSTRAINT `orchestration_log_user_id_612211c0_fk_orchestration_user_id` FOREIGN KEY (`user_id`) REFERENCES `orchestration_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orchestration_log`
--

LOCK TABLES `orchestration_log` WRITE;
/*!40000 ALTER TABLE `orchestration_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `orchestration_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orchestration_router`
--

DROP TABLE IF EXISTS `orchestration_router`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orchestration_router` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `ip_address` char(39) NOT NULL,
  `device_type` varchar(100) NOT NULL,
  `hostname` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `orchestration_router_ip_address_57f8b717_uniq` (`ip_address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orchestration_router`
--

LOCK TABLES `orchestration_router` WRITE;
/*!40000 ALTER TABLE `orchestration_router` DISABLE KEYS */;
/*!40000 ALTER TABLE `orchestration_router` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orchestration_user`
--

DROP TABLE IF EXISTS `orchestration_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orchestration_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orchestration_user`
--

LOCK TABLES `orchestration_user` WRITE;
/*!40000 ALTER TABLE `orchestration_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `orchestration_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orchestration_user_groups`
--

DROP TABLE IF EXISTS `orchestration_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orchestration_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `orchestration_user_groups_user_id_group_id_20013916_uniq` (`user_id`,`group_id`),
  KEY `orchestration_user_groups_group_id_9d211f09_fk_auth_group_id` (`group_id`),
  CONSTRAINT `orchestration_user_g_user_id_be0a6645_fk_orchestra` FOREIGN KEY (`user_id`) REFERENCES `orchestration_user` (`id`),
  CONSTRAINT `orchestration_user_groups_group_id_9d211f09_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orchestration_user_groups`
--

LOCK TABLES `orchestration_user_groups` WRITE;
/*!40000 ALTER TABLE `orchestration_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `orchestration_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orchestration_user_user_permissions`
--

DROP TABLE IF EXISTS `orchestration_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orchestration_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `orchestration_user_user__user_id_permission_id_3b554e80_uniq` (`user_id`,`permission_id`),
  KEY `orchestration_user_u_permission_id_d9c14c95_fk_auth_perm` (`permission_id`),
  CONSTRAINT `orchestration_user_u_permission_id_d9c14c95_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `orchestration_user_u_user_id_24244a6a_fk_orchestra` FOREIGN KEY (`user_id`) REFERENCES `orchestration_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orchestration_user_user_permissions`
--

LOCK TABLES `orchestration_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `orchestration_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `orchestration_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-24  7:52:42
