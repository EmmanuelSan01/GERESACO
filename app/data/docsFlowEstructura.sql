DROP DATABASE IF EXISTS geresaco;
CREATE DATABASE geresaco
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE geresaco;

CREATE TABLE user (
  nombre varchar(255) NOT NULL,
  contrasena_hash varchar(255) NOT NULL,
  rol enum('user','admin') NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  email varchar(255) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY ix_user_email (email)
) ENGINE=InnoDB;

CREATE TABLE room (
  nombre varchar(255) NOT NULL,
  sede enum('zona_franca','cajasan','bogota','cucuta','guatemala') NOT NULL,
  capacidad int NOT NULL,
  recursos varchar(255) NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE reservation (
  fecha date NOT NULL,
  hora_inicio time NOT NULL,
  hora_fin time NOT NULL,
  estado enum('pendiente','confirmada','cancelada') NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  usuario_id int NOT NULL,
  sala_id int NOT NULL,
  PRIMARY KEY (id),
  KEY ix_reservation_sala_id (sala_id),
  KEY ix_reservation_usuario_id (usuario_id),
  CONSTRAINT reservation_ibfk_1 FOREIGN KEY (usuario_id) REFERENCES user (id),
  CONSTRAINT reservation_ibfk_2 FOREIGN KEY (sala_id) REFERENCES room (id)
) ENGINE=InnoDB;