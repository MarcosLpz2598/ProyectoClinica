USE clinica;
CREATE TABLE Usuarios (id int NOT NULL AUTO_INCREMENT, nombre varchar(15), apellidoPaterno varchar(20), apellidoMaterno varchar(20),
correo varchar(50), password varchar(10), userName varchar(20), PRIMARY KEY (id));

CREATE TABLE pacientes (id int NOT NULL AUTO_INCREMENT, nombre varchar(45), apellidoPaterno varchar(40), apellidoMaterno varchar(40),
edad int, direccion varchar(50), fechaNacimiento date, telefono varchar(20), correo varchar(40), PRIMARY KEY (id));

CREATE TABLE doctores (id int NOT NULL AUTO_INCREMENT, nombre varchar(45), apellidoPaterno varchar(40), apellidoMaterno varchar(40),
especialidad varchar(40), correo varchar(40), telefono varchar(20), PRIMARY KEY (id));

CREATE TABLE citas (id int NOT NULL AUTO_INCREMENT, nombre varchar(45), telefono varchar(20), email varchar(40), sintomas varchar(100), fecha date,
departamento varchar(40), genero varchar(20), hora time,  PRIMARY KEY (id));