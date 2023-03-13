SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

DROP TABLE IF EXISTS `Account`;
CREATE TABLE `Account` (
  `id` int NOT NULL AUTO_INCREMENT,
  `firstName` varchar(128) NOT NULL,
  `lastName` varchar(128) NOT NULL,
  `email` varchar(128) NOT NULL,
  `password` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `Animal`;
CREATE TABLE `Animal` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `weight` float(32) NOT NULL,
  `length` float(32) NOT NULL,
  `height` float(32) NOT NULL,
  `gender` varchar(8) NOT NULL,
  `lifeStatus` varchar(8) NOT NULL,
  `chippingDateTime` datetime NOT NULL,
  `chipperId` int NOT NULL,
  `chippingLocationId` bigint NOT NULL,
  `deathDateTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `Animal_Type`;
CREATE TABLE `Animal_Type` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `type` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `Animal_Types_Array`;
CREATE TABLE `Animal_Types_Array` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `animal_id` bigint NOT NULL,
  `animal_type_id` bigint NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `Animal_Visited_Location`;
CREATE TABLE `Animal_Visited_Location` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `animalId` bigint NOT NULL,
  `locationPointId` bigint NOT NULL,
  `dateTimeOfVisitLocationPoint` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `Location_Point`;
CREATE TABLE `Location_Point` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `latitude` double NOT NULL,
  `longitude` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
