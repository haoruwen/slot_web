-- slot db schema

CREATE DATABASE IF NOT EXISTS `db_slot`;
USE `db_slot`;

CREATE TABLE IF NOT EXISTS `tbl_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  -- md5 hash of password
  `passwd` text NOT NULL,
  `role` enum('user', 'administrator') NOT NULL,
  `points` int NOT NULL,
  `self_points` int NOT NULL,
  `is_first` BOOLEAN DEFAULT `TRUE`,
  `avatar_path` VARCHAR(255) DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE_INDEX` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `tbl_ip` (
    `id` int NOT NULL AUTO_INCREMENT,
    `ip_address` VARCHAR(50) NOT NULL,
    `attempts` int DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `ip_address_UNIQUE_INDEX` (`ip_address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `tbl_prize` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `stock` int NOT NULL,
    `is_first_tier` TINYINT(1) NOT NULL,
    `is_second_tier` TINYINT(1) NOT NULL,
    `is_third_tier` TINYINT(1) NOT NULL,
    `first_tier_prob` FLOAT NOT NULL,
    `second_tier_prob` FLOAT NOT NULL,
    `third_tier_prob` FLOAT NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name_UNIQUE_INDEX` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `tbl_records` (
    `id` int NOT NULL AUTO_INCREMENT,
    `from_id` int NOT NULL,
    `to_id` int NOT NULL,
    `prize_id` int NOT NULL,
    `tier` enum('first', 'second', 'third') NOT NULL,
    `create_time` datetime NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;