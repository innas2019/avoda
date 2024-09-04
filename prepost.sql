
CREATE TABLE `preposts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(40) CHARACTER SET utf8mb4 DEFAULT NULL,
  `text` varchar(500) DEFAULT NULL,
  `place` varchar(40) NOT NULL,
  `created` datetime DEFAULT NULL,
  `contacts` varchar(100) CHARACTER SET utf8mb4 DEFAULT NULL,
  `result` int(11) DEFAULT NULL,
  `name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4;

