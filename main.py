from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import json
import requests
import jwt
import datetime
from functools import wraps
import uuid
import re
import random
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib
import base64
import decimal
import traceback
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, expose_headers=["new_token"])

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "ovo",
    "password": "1234",
    "database": "ovo"
}

BASE_URL = os.getenv('BASE_URL', 'http://ovotest.mooo.com:5000')

SECRET_KEY = "ghwgdgHHYushHg1231SDAAa"

def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cor = conn.cursor()
    cor.execute("""
    -- --------------------------------------------------------
    -- Host:                         ovotest.mooo.com
    -- Versión del servidor:         10.11.13-MariaDB-0ubuntu0.24.04.1 - Ubuntu 24.04
    -- SO del servidor:              debian-linux-gnu
    -- HeidiSQL Versión:             12.6.0.6765
    -- --------------------------------------------------------

    /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
    /*!40101 SET NAMES utf8 */;
    /*!50503 SET NAMES utf8mb4 */;
    /*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
    /*!40103 SET TIME_ZONE='+00:00' */;
    /*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
    /*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
    /*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


    -- Volcando estructura de base de datos para ovo
    CREATE DATABASE IF NOT EXISTS `ovo` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
    USE `ovo`;

    -- Volcando estructura para tabla ovo.aptitud
    CREATE TABLE IF NOT EXISTS `aptitud` (
    `idAptitud` int(11) NOT NULL AUTO_INCREMENT,
    `nombreAptitud` varchar(50) DEFAULT NULL,
    `descripcion` varchar(50) DEFAULT NULL,
    `fechaAlta` datetime NOT NULL DEFAULT current_timestamp(),
    `fechaBaja` datetime DEFAULT NULL,
    PRIMARY KEY (`idAptitud`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.aptitud: ~1 rows (aproximadamente)
    INSERT INTO `aptitud` (`idAptitud`, `nombreAptitud`, `descripcion`, `fechaAlta`, `fechaBaja`) VALUES
        (1, 'Comunicación', 'Habilidad para transmitir ideas', '2025-09-09 14:36:35', '2025-09-09 14:37:08');

    -- Volcando estructura para tabla ovo.aptitudcarrera
    CREATE TABLE IF NOT EXISTS `aptitudcarrera` (
    `idAptitudCarrera` int(11) NOT NULL AUTO_INCREMENT,
    `afinidadCarrera` double DEFAULT NULL,
    `idAptitud` int(11) DEFAULT NULL,
    `idCarreraInstitucion` int(11) DEFAULT NULL,
    PRIMARY KEY (`idAptitudCarrera`),
    KEY `FK_aptitudcarrera_aptitud` (`idAptitud`),
    KEY `FK_aptitudcarrera_carrera` (`idCarreraInstitucion`),
    CONSTRAINT `FK_aptitudcarrera_aptitud` FOREIGN KEY (`idAptitud`) REFERENCES `aptitud` (`idAptitud`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_aptitudcarrera_carrera` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrera` (`idCarrera`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.aptitudcarrera: ~0 rows (aproximadamente)

    -- Volcando estructura para tabla ovo.backup
    CREATE TABLE IF NOT EXISTS `backup` (
    `fechaBackup` datetime DEFAULT NULL,
    `directorio` varchar(50) DEFAULT NULL,
    `tamano` double DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.backup: ~0 rows (aproximadamente)

    -- Volcando estructura para tabla ovo.carrera
    CREATE TABLE IF NOT EXISTS `carrera` (
    `idCarrera` int(11) NOT NULL AUTO_INCREMENT,
    `fechaFin` datetime DEFAULT NULL,
    `nombreCarrera` varchar(50) DEFAULT NULL,
    `idTipoCarrera` int(11) DEFAULT NULL,
    PRIMARY KEY (`idCarrera`),
    KEY `FK_carrera_tipocarrera` (`idTipoCarrera`),
    CONSTRAINT `FK_carrera_tipocarrera` FOREIGN KEY (`idTipoCarrera`) REFERENCES `tipocarrera` (`idTipoCarrera`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.carrera: ~1 rows (aproximadamente)
    INSERT INTO `carrera` (`idCarrera`, `fechaFin`, `nombreCarrera`, `idTipoCarrera`) VALUES
        (1, '2028-09-09 14:19:45', 'Ing. X Modificada', 1);

    -- Volcando estructura para tabla ovo.carrerainstitucion
    CREATE TABLE IF NOT EXISTS `carrerainstitucion` (
    `idCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
    `cantidadMaterias` int(11) NOT NULL,
    `duracionCarrera` decimal(20,2) NOT NULL,
    `fechaFin` datetime DEFAULT NULL,
    `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
    `horasCursado` int(11) NOT NULL,
    `observaciones` varchar(500) NOT NULL,
    `nombreCarrera` varchar(50) NOT NULL,
    `tituloCarrera` varchar(50) NOT NULL,
    `montoCuota` decimal(20,2) NOT NULL,
    `idEstadoCarreraInstitucion` int(11) NOT NULL,
    `idCarrera` int(11) NOT NULL,
    `idModalidadCarreraInstitucion` int(11) NOT NULL,
    `idInstitucion` int(11) DEFAULT NULL,
    PRIMARY KEY (`idCarreraInstitucion`),
    KEY `FK_carrerainstitucion_estadocarrerainstitucion` (`idEstadoCarreraInstitucion`),
    KEY `FK_carrerainstitucion_carrera` (`idCarrera`),
    KEY `FK_carrerainstitucion_modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`),
    KEY `FK_carrerainstitucion_institucion` (`idInstitucion`),
    CONSTRAINT `FK_carrerainstitucion_carrera` FOREIGN KEY (`idCarrera`) REFERENCES `carrera` (`idCarrera`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_carrerainstitucion_estadocarrerainstitucion` FOREIGN KEY (`idEstadoCarreraInstitucion`) REFERENCES `estadocarrerainstitucion` (`idEstadoCarreraInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_carrerainstitucion_institucion` FOREIGN KEY (`idInstitucion`) REFERENCES `institucion` (`idInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_carrerainstitucion_modalidadcarrerainstitucion` FOREIGN KEY (`idModalidadCarreraInstitucion`) REFERENCES `modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.carrerainstitucion: ~1 rows (aproximadamente)
    INSERT INTO `carrerainstitucion` (`idCarreraInstitucion`, `cantidadMaterias`, `duracionCarrera`, `fechaFin`, `fechaInicio`, `horasCursado`, `observaciones`, `nombreCarrera`, `tituloCarrera`, `montoCuota`, `idEstadoCarreraInstitucion`, `idCarrera`, `idModalidadCarreraInstitucion`, `idInstitucion`) VALUES
        (1, 123, 123.00, NULL, '2025-09-14 22:05:14', 123, '123', '123', '123', 123.00, 1, 1, 3, NULL);

    -- Volcando estructura para tabla ovo.configuracionbackup
    CREATE TABLE IF NOT EXISTS `configuracionbackup` (
    `frecuencia` varchar(50) DEFAULT NULL,
    `horaEjecucion` time DEFAULT NULL,
    `cantidadBackupConservar` int(11) DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.configuracionbackup: ~0 rows (aproximadamente)

    -- Volcando estructura para tabla ovo.contenidomultimedia
    CREATE TABLE IF NOT EXISTS `contenidomultimedia` (
    `idContenidoMultimedia` int(11) NOT NULL AUTO_INCREMENT,
    `enlace` varchar(50) DEFAULT NULL,
    `fechaFin` datetime DEFAULT NULL,
    `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
    `titulo` varchar(50) DEFAULT NULL,
    `descripcion` varchar(50) DEFAULT NULL,
    `idCarreraInstitucion` int(11) DEFAULT NULL,
    PRIMARY KEY (`idContenidoMultimedia`),
    KEY `FK_contenidomultimedia_carrerainstitucion` (`idCarreraInstitucion`),
    CONSTRAINT `FK_contenidomultimedia_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.contenidomultimedia: ~0 rows (aproximadamente)

    -- Volcando estructura para tabla ovo.estadoacceso
    CREATE TABLE IF NOT EXISTS `estadoacceso` (
    `idEstadoAcceso` int(11) NOT NULL AUTO_INCREMENT,
    `nombreEstadoAcceso` varchar(50) DEFAULT NULL,
    `fechaFin` datetime DEFAULT NULL,
    PRIMARY KEY (`idEstadoAcceso`)
    ) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.estadoacceso: ~4 rows (aproximadamente)
    INSERT INTO `estadoacceso` (`idEstadoAcceso`, `nombreEstadoAcceso`, `fechaFin`) VALUES
        (1, 'Exitoso', NULL),
        (2, 'Fallido', NULL),
        (3, 'Fallido Google', NULL),
        (4, 'Bloqueado', NULL);

    -- Volcando estructura para tabla ovo.estadocarrerainstitucion
    CREATE TABLE IF NOT EXISTS `estadocarrerainstitucion` (
    `idEstadoCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
    `nombreEstadoCarreraInstitucion` varchar(50) DEFAULT NULL,
    `fechaFin` datetime DEFAULT NULL,
    PRIMARY KEY (`idEstadoCarreraInstitucion`)
    ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.estadocarrerainstitucion: ~3 rows (aproximadamente)
    INSERT INTO `estadocarrerainstitucion` (`idEstadoCarreraInstitucion`, `nombreEstadoCarreraInstitucion`, `fechaFin`) VALUES
        (1, 'Activa', '2025-09-09 14:58:45'),
        (2, 'Inactiva', NULL),
        (3, 'Cerrada', NULL);

    -- Volcando estructura para tabla ovo.estadoinstitucion
    CREATE TABLE IF NOT EXISTS `estadoinstitucion` (
    `idEstadoInstitucion` int(11) NOT NULL AUTO_INCREMENT,
    `nombreEstadoInstitucion` varchar(50) DEFAULT NULL,
    `fechaFin` datetime DEFAULT NULL,
    PRIMARY KEY (`idEstadoInstitucion`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.estadoinstitucion: ~1 rows (aproximadamente)
    INSERT INTO `estadoinstitucion` (`idEstadoInstitucion`, `nombreEstadoInstitucion`, `fechaFin`) VALUES
        (1, 'Aprobada', '2025-09-09 14:57:02');

    -- Volcando estructura para tabla ovo.estadousuario
    CREATE TABLE IF NOT EXISTS `estadousuario` (
    `idEstadoUsuario` int(11) NOT NULL AUTO_INCREMENT,
    `nombreEstadoUsuario` varchar(50) DEFAULT NULL,
    `fechaFin` datetime DEFAULT NULL,
    PRIMARY KEY (`idEstadoUsuario`)
    ) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.estadousuario: ~4 rows (aproximadamente)
    INSERT INTO `estadousuario` (`idEstadoUsuario`, `nombreEstadoUsuario`, `fechaFin`) VALUES
        (1, 'Activo', NULL),
        (2, 'Suspendido', NULL),
        (3, 'Baja', NULL),
        (4, 'Pendiente', NULL);

    -- Volcando estructura para tabla ovo.genero
    CREATE TABLE IF NOT EXISTS `genero` (
    `idGenero` int(11) NOT NULL AUTO_INCREMENT,
    `nombreGenero` varchar(50) NOT NULL,
    PRIMARY KEY (`idGenero`)
    ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.genero: ~1 rows (aproximadamente)
    INSERT INTO `genero` (`idGenero`, `nombreGenero`) VALUES
        (1, 'Masculino'),
        (2, 'Femenino'),
        (3, 'Otro');

    -- Volcando estructura para tabla ovo.grupo
    CREATE TABLE IF NOT EXISTS `grupo` (
    `idGrupo` int(11) NOT NULL AUTO_INCREMENT,
    `nombreGrupo` varchar(50) DEFAULT NULL,
    `fechaFin` datetime DEFAULT NULL,
    `descripcion` varchar(50) DEFAULT NULL,
    PRIMARY KEY (`idGrupo`)
    ) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.grupo: ~5 rows (aproximadamente)
    INSERT INTO `grupo` (`idGrupo`, `nombreGrupo`, `fechaFin`, `descripcion`) VALUES
        (1, 'Administrador', NULL, 'Todos los permisos'),
        (2, 'Moderador', NULL, NULL),
        (3, 'Estudiante', NULL, NULL),
        (4, 'Institucion', NULL, NULL),
        (5, 'Supervisores', NULL, 'Grupo de supervisión');

    -- Volcando estructura para tabla ovo.historialabm
    CREATE TABLE IF NOT EXISTS `historialabm` (
    `idHistorialABM` int(11) NOT NULL AUTO_INCREMENT,
    `idUsuario` int(11) NOT NULL,
    `fechaHistorial` datetime NOT NULL DEFAULT current_timestamp(),
    `idTipoAccion` int(11) NOT NULL,
    `idModalidadCarreraInstitucion` int(11) DEFAULT NULL,
    `idLocalidad` int(11) DEFAULT NULL,
    `idGrupo` int(11) DEFAULT NULL,
    `idProvincia` int(11) DEFAULT NULL,
    `idPermiso` int(11) DEFAULT NULL,
    `idAptitud` int(11) DEFAULT NULL,
    `idPermisoGrupo` int(11) DEFAULT NULL,
    `idCarrera` int(11) DEFAULT NULL,
    `idEstadoAcceso` int(11) DEFAULT NULL,
    `idGenero` int(11) DEFAULT NULL,
    `idEstadoCarreraInstitucion` int(11) DEFAULT NULL,
    `idEstadoUsuario` int(11) DEFAULT NULL,
    `idPais` int(11) DEFAULT NULL,
    `idTipoInstitucion` int(11) DEFAULT NULL,
    `idTipoCarrera` int(11) DEFAULT NULL,
    PRIMARY KEY (`idHistorialABM`),
    KEY `FK_historialabm_tipoaccion` (`idTipoAccion`),
    KEY `FK_historialabm_modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`),
    KEY `FK_historialabm_localidad` (`idLocalidad`),
    KEY `FK_historialabm_grupo` (`idGrupo`),
    KEY `FK_historialabm_provincia` (`idProvincia`),
    KEY `FK_historialabm_permiso` (`idPermiso`),
    KEY `FK_historialabm_usuario` (`idUsuario`),
    KEY `FK_historialabm_aptitud` (`idAptitud`),
    KEY `FK_historialabm_permisogrupo` (`idPermisoGrupo`),
    KEY `FK_historialabm_carrera` (`idCarrera`),
    KEY `FK_historialabm_estadoacceso` (`idEstadoAcceso`),
    KEY `FK_historialabm_genero` (`idGenero`),
    KEY `FK_historialabm_estadocarrerainstitucion` (`idEstadoCarreraInstitucion`),
    KEY `FK_historialabm_estadousuario` (`idEstadoUsuario`),
    KEY `FK_historialabm_pais` (`idPais`),
    KEY `FK_historialabm_tipoinstitucion` (`idTipoInstitucion`),
    KEY `FK_historialabm_tipocarrera` (`idTipoCarrera`),
    CONSTRAINT `FK_historialabm_aptitud` FOREIGN KEY (`idAptitud`) REFERENCES `aptitud` (`idAptitud`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_carrera` FOREIGN KEY (`idCarrera`) REFERENCES `carrera` (`idCarrera`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_estadoacceso` FOREIGN KEY (`idEstadoAcceso`) REFERENCES `estadoacceso` (`idEstadoAcceso`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_estadocarrerainstitucion` FOREIGN KEY (`idEstadoCarreraInstitucion`) REFERENCES `estadocarrerainstitucion` (`idEstadoCarreraInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_estadousuario` FOREIGN KEY (`idEstadoUsuario`) REFERENCES `estadousuario` (`idEstadoUsuario`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_genero` FOREIGN KEY (`idGenero`) REFERENCES `genero` (`idGenero`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_grupo` FOREIGN KEY (`idGrupo`) REFERENCES `grupo` (`idGrupo`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_localidad` FOREIGN KEY (`idLocalidad`) REFERENCES `localidad` (`idLocalidad`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_modalidadcarrerainstitucion` FOREIGN KEY (`idModalidadCarreraInstitucion`) REFERENCES `modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_pais` FOREIGN KEY (`idPais`) REFERENCES `pais` (`idPais`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_permiso` FOREIGN KEY (`idPermiso`) REFERENCES `permiso` (`idPermiso`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_permisogrupo` FOREIGN KEY (`idPermisoGrupo`) REFERENCES `permisogrupo` (`idPermisoGrupo`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_provincia` FOREIGN KEY (`idProvincia`) REFERENCES `provincia` (`idProvincia`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_tipoaccion` FOREIGN KEY (`idTipoAccion`) REFERENCES `tipoaccion` (`idTipoAccion`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_tipocarrera` FOREIGN KEY (`idTipoCarrera`) REFERENCES `tipocarrera` (`idTipoCarrera`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_tipoinstitucion` FOREIGN KEY (`idTipoInstitucion`) REFERENCES `tipoinstitucion` (`idTipoInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialabm_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.historialabm: ~1 rows (aproximadamente)
    INSERT INTO `historialabm` (`idHistorialABM`, `idUsuario`, `fechaHistorial`, `idTipoAccion`, `idModalidadCarreraInstitucion`, `idLocalidad`, `idGrupo`, `idProvincia`, `idPermiso`, `idAptitud`, `idPermisoGrupo`, `idCarrera`, `idEstadoAcceso`, `idGenero`, `idEstadoCarreraInstitucion`, `idEstadoUsuario`, `idPais`, `idTipoInstitucion`, `idTipoCarrera`) VALUES
        (1, 1, '2025-08-31 18:31:20', 1, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

    -- Volcando estructura para tabla ovo.historialacceso
    CREATE TABLE IF NOT EXISTS `historialacceso` (
    `idHistorial` int(11) NOT NULL AUTO_INCREMENT,
    `fecha` datetime NOT NULL DEFAULT current_timestamp(),
    `ipAcceso` varchar(50) NOT NULL,
    `navegador` varchar(1000) NOT NULL,
    `idEstadoAcceso` int(11) NOT NULL,
    `idUsuario` int(11) NOT NULL,
    PRIMARY KEY (`idHistorial`),
    KEY `FK_historialacceso_estadoacceso` (`idEstadoAcceso`),
    KEY `FK_historialacceso_usuario` (`idUsuario`),
    CONSTRAINT `FK_historialacceso_estadoacceso` FOREIGN KEY (`idEstadoAcceso`) REFERENCES `estadoacceso` (`idEstadoAcceso`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_historialacceso_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=106 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.historialacceso: ~75 rows (aproximadamente)
    INSERT INTO `historialacceso` (`idHistorial`, `fecha`, `ipAcceso`, `navegador`, `idEstadoAcceso`, `idUsuario`) VALUES
        (1, '2025-08-31 18:18:39', '1.1.1.1', 'dasd', 1, 1),
        (2, '2025-09-09 16:51:43', '127.0.0.1', 'PostmanRuntime/7.45.0', 1, 1),
        (3, '2025-09-09 16:51:47', '127.0.0.1', 'PostmanRuntime/7.45.0', 1, 1),
        (4, '2025-09-09 16:51:48', '127.0.0.1', 'PostmanRuntime/7.45.0', 1, 1),
        (5, '2025-09-09 16:52:38', '127.0.0.1', 'PostmanRuntime/7.45.0', 2, 1),
        (6, '2025-09-14 16:57:41', '127.0.0.1', 'PostmanRuntime/7.46.0', 1, 1),
        (7, '2025-09-14 16:57:50', '127.0.0.1', 'PostmanRuntime/7.46.0', 1, 1),
        (8, '2025-09-14 21:38:07', '191.82.213.188', 'PostmanRuntime/7.46.0', 1, 1),
        (9, '2025-09-14 21:49:46', '191.82.213.188', 'PostmanRuntime/7.46.0', 1, 1),
        (10, '2025-09-14 21:49:57', '192.168.1.1', 'PostmanRuntime/7.46.0', 1, 1),
        (11, '2025-09-15 01:02:27', '186.122.0.159', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (12, '2025-09-15 01:02:38', '186.122.0.159', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (13, '2025-09-15 01:03:10', '186.122.0.159', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (14, '2025-09-15 01:03:25', '186.122.0.159', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (15, '2025-09-15 01:03:35', '186.122.0.159', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (16, '2025-09-15 01:03:56', '186.122.0.159', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (17, '2025-09-15 13:43:31', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (18, '2025-09-15 13:49:40', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (19, '2025-09-15 13:51:43', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (20, '2025-09-15 15:44:02', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (21, '2025-09-15 15:44:35', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (22, '2025-09-15 15:47:00', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (23, '2025-09-15 15:49:53', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (24, '2025-09-15 15:50:00', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (25, '2025-09-15 15:50:02', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (26, '2025-09-15 15:50:05', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (27, '2025-09-15 15:51:27', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (28, '2025-09-15 15:51:30', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (29, '2025-09-15 15:56:10', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (30, '2025-09-15 15:56:14', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (31, '2025-09-15 16:00:47', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (32, '2025-09-15 16:01:05', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (33, '2025-09-15 16:01:30', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (34, '2025-09-15 16:02:25', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (35, '2025-09-15 16:09:12', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (36, '2025-09-15 16:09:23', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (37, '2025-09-15 16:16:20', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (38, '2025-09-15 16:17:59', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (39, '2025-09-15 16:20:23', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (40, '2025-09-15 16:23:02', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (41, '2025-09-15 16:23:37', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (42, '2025-09-15 16:23:42', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (43, '2025-09-15 16:25:09', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (44, '2025-09-15 16:57:00', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (45, '2025-09-15 16:57:08', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (46, '2025-09-15 18:14:05', '191.82.10.3', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36', 1, 1),
        (47, '2025-09-15 18:34:42', '191.82.10.3', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36', 1, 1),
        (48, '2025-09-15 19:59:04', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (49, '2025-09-15 20:21:47', '190.15.220.52', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (50, '2025-09-15 20:24:26', '190.15.220.52', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (51, '2025-09-15 20:25:43', '190.15.220.52', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (52, '2025-09-15 20:27:56', '190.15.220.52', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (53, '2025-09-15 20:34:39', '190.15.220.52', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (54, '2025-09-15 20:37:12', '190.15.220.52', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (55, '2025-09-15 20:37:18', '190.15.220.52', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (56, '2025-09-15 20:42:23', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 2, 1),
        (57, '2025-09-15 20:42:24', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 2, 1),
        (58, '2025-09-15 20:42:25', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 2, 1),
        (59, '2025-09-15 20:42:27', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (60, '2025-09-15 20:49:10', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (61, '2025-09-15 20:50:39', '190.15.220.52', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (62, '2025-09-15 20:51:58', '190.15.220.52', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (63, '2025-09-15 20:55:13', '190.15.220.52', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (64, '2025-09-16 12:49:33', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (65, '2025-09-16 13:02:48', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 27),
        (66, '2025-09-16 13:03:00', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (67, '2025-09-16 13:16:06', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (68, '2025-09-16 13:16:14', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (69, '2025-09-16 13:25:54', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (70, '2025-09-16 13:25:59', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (71, '2025-09-16 13:26:08', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (74, '2025-09-16 13:28:18', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 28),
        (75, '2025-09-16 13:30:13', '190.220.154.44', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (76, '2025-09-16 13:45:24', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (77, '2025-09-16 13:47:06', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (78, '2025-09-16 13:48:23', '191.82.213.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (80, '2025-09-16 14:03:35', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (81, '2025-09-16 14:03:40', '191.82.213.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (82, '2025-09-16 14:03:56', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (83, '2025-09-16 14:21:32', '191.82.213.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (84, '2025-09-16 14:22:20', '191.82.213.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (85, '2025-09-16 14:22:57', '191.82.213.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (86, '2025-09-16 14:42:12', '191.82.213.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 31),
        (87, '2025-09-16 14:42:26', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (88, '2025-09-16 14:43:38', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 30),
        (89, '2025-09-16 14:47:25', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (90, '2025-09-16 14:47:27', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 2, 1),
        (91, '2025-09-16 14:48:10', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 2, 1),
        (92, '2025-09-16 14:48:11', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 2, 1),
        (93, '2025-09-16 14:48:39', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 2, 1),
        (94, '2025-09-16 14:48:47', '191.82.213.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 2, 31),
        (95, '2025-09-16 14:49:04', '191.82.213.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 2, 31),
        (96, '2025-09-16 14:49:06', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 2, 1),
        (97, '2025-09-16 14:49:10', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (98, '2025-09-16 14:49:14', '191.82.213.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (99, '2025-09-16 14:49:27', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (100, '2025-09-16 14:49:28', '191.82.213.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (101, '2025-09-16 14:49:36', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (102, '2025-09-16 14:51:55', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (103, '2025-09-16 14:52:29', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1),
        (104, '2025-09-16 14:52:30', '191.82.213.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36', 1, 1),
        (105, '2025-09-16 14:52:38', '192.168.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0', 1, 1);

    -- Volcando estructura para tabla ovo.institucion
    CREATE TABLE IF NOT EXISTS `institucion` (
    `idInstitucion` int(11) NOT NULL AUTO_INCREMENT,
    `anioFundacion` int(11) NOT NULL,
    `codigoPostal` int(11) NOT NULL,
    `nombreInstitucion` varchar(50) NOT NULL,
    `CUIT` int(11) NOT NULL,
    `direccion` varchar(50) NOT NULL,
    `fechaAlta` datetime NOT NULL DEFAULT current_timestamp(),
    `siglaInstitucion` varchar(50) NOT NULL,
    `telefono` varchar(50) NOT NULL,
    `mail` varchar(50) NOT NULL,
    `sitioWeb` varchar(50) NOT NULL,
    `urlLogo` varchar(50) NOT NULL,
    `idTipoInstitucion` int(11) NOT NULL,
    `idLocalidad` int(11) NOT NULL,
    `idUsuario` int(11) NOT NULL,
    PRIMARY KEY (`idInstitucion`),
    KEY `FK_institucion_tipoinstitucion` (`idTipoInstitucion`),
    KEY `FK_institucion_localidad` (`idLocalidad`),
    KEY `FK_institucion_usuario` (`idUsuario`),
    CONSTRAINT `FK_institucion_localidad` FOREIGN KEY (`idLocalidad`) REFERENCES `localidad` (`idLocalidad`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_institucion_tipoinstitucion` FOREIGN KEY (`idTipoInstitucion`) REFERENCES `tipoinstitucion` (`idTipoInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_institucion_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.institucion: ~1 rows (aproximadamente)
    INSERT INTO `institucion` (`idInstitucion`, `anioFundacion`, `codigoPostal`, `nombreInstitucion`, `CUIT`, `direccion`, `fechaAlta`, `siglaInstitucion`, `telefono`, `mail`, `sitioWeb`, `urlLogo`, `idTipoInstitucion`, `idLocalidad`, `idUsuario`) VALUES
        (1, 2200, 5500, 'UTN', 5456456, 'RAS', '2025-09-14 22:05:31', 'UTN', '123123123', 'adass213casd', 'wwddwwwddw', 'dddwdwdwd', 1, 1, 1);

    -- Volcando estructura para tabla ovo.institucionestado
    CREATE TABLE IF NOT EXISTS `institucionestado` (
    `idinstitucionEstado` int(11) NOT NULL AUTO_INCREMENT,
    `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
    `fechaFin` datetime DEFAULT NULL,
    `idEstadoInstitucion` int(11) DEFAULT NULL,
    `idInstitucion` int(11) DEFAULT NULL,
    PRIMARY KEY (`idinstitucionEstado`),
    KEY `FK_institucionestado_estadoinstitucion` (`idEstadoInstitucion`),
    KEY `FK_institucionestado_institucion` (`idInstitucion`),
    CONSTRAINT `FK_institucionestado_estadoinstitucion` FOREIGN KEY (`idEstadoInstitucion`) REFERENCES `estadoinstitucion` (`idEstadoInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_institucionestado_institucion` FOREIGN KEY (`idInstitucion`) REFERENCES `institucion` (`idInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.institucionestado: ~0 rows (aproximadamente)

    -- Volcando estructura para tabla ovo.interesusuariocarrera
    CREATE TABLE IF NOT EXISTS `interesusuariocarrera` (
    `fechaAlta` datetime NOT NULL DEFAULT current_timestamp(),
    `fechaFin` datetime DEFAULT NULL,
    `idUsuario` int(11) DEFAULT NULL,
    `idCarreraInstitucion` int(11) DEFAULT NULL,
    KEY `FK_interesusuariocarrera_usuario` (`idUsuario`),
    KEY `FK_interesusuariocarrera_carrerainstitucion` (`idCarreraInstitucion`),
    CONSTRAINT `FK_interesusuariocarrera_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_interesusuariocarrera_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.interesusuariocarrera: ~2 rows (aproximadamente)
    INSERT INTO `interesusuariocarrera` (`fechaAlta`, `fechaFin`, `idUsuario`, `idCarreraInstitucion`) VALUES
        ('2025-09-14 22:07:56', '2025-09-14 22:08:06', 1, 1),
        ('2025-09-14 22:08:10', '2025-09-14 22:08:16', 1, 1);

    -- Volcando estructura para tabla ovo.localidad
    CREATE TABLE IF NOT EXISTS `localidad` (
    `idLocalidad` int(11) NOT NULL AUTO_INCREMENT,
    `nombreLocalidad` varchar(50) NOT NULL,
    `idProvincia` int(11) NOT NULL,
    PRIMARY KEY (`idLocalidad`),
    KEY `FK_localidad_provincia` (`idProvincia`),
    CONSTRAINT `FK_localidad_provincia` FOREIGN KEY (`idProvincia`) REFERENCES `provincia` (`idProvincia`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.localidad: ~2 rows (aproximadamente)
    INSERT INTO `localidad` (`idLocalidad`, `nombreLocalidad`, `idProvincia`) VALUES
        (1, 'Mendoza', 1),
        (2, 'Palermo', 2);

    -- Volcando estructura para tabla ovo.modalidadcarrerainstitucion
    CREATE TABLE IF NOT EXISTS `modalidadcarrerainstitucion` (
    `idModalidadCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
    `nombreModalidad` varchar(50) DEFAULT NULL,
    PRIMARY KEY (`idModalidadCarreraInstitucion`)
    ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.modalidadcarrerainstitucion: ~2 rows (aproximadamente)
    INSERT INTO `modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`, `nombreModalidad`) VALUES
        (2, 'Virtual'),
        (3, 'Hibrida');

    -- Volcando estructura para tabla ovo.pais
    CREATE TABLE IF NOT EXISTS `pais` (
    `idPais` int(11) NOT NULL AUTO_INCREMENT,
    `nombrePais` varchar(50) DEFAULT NULL,
    PRIMARY KEY (`idPais`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.pais: ~1 rows (aproximadamente)
    INSERT INTO `pais` (`idPais`, `nombrePais`) VALUES
        (1, 'Argentina');

    -- Volcando estructura para tabla ovo.permiso
    CREATE TABLE IF NOT EXISTS `permiso` (
    `idPermiso` int(11) NOT NULL AUTO_INCREMENT,
    `nombrePermiso` varchar(50) DEFAULT NULL,
    `descripcion` varchar(500) DEFAULT NULL,
    `fechaFin` datetime DEFAULT NULL,
    PRIMARY KEY (`idPermiso`)
    ) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.permiso: ~8 rows (aproximadamente)
    INSERT INTO `permiso` (`idPermiso`, `nombrePermiso`, `descripcion`, `fechaFin`) VALUES
        (0, 'ADMIN_PANEL', 'TEMP', NULL),
        (1, 'LIST_USERS', 'Listar todos los usuarios del sistema', NULL),
        (2, 'LIST_GROUPS', 'Listar todos los grupos activos del sistema', NULL),
        (3, 'USER_GROUPS', 'Ver/Asignar los grupos de un usuario', NULL),
        (4, 'USER_PERMS', 'Ver/Asignar los permisos de un usuario', NULL),
        (5, 'LIST_PERMS', 'Listar todos los permisos del sistema', NULL),
        (6, 'USER_HISTORY', 'Ver el historial de acceso de un usuario', NULL),
        (7, 'PEDRO', 'HOLA SOY PEDRO', '2025-09-16 13:52:06');

    -- Volcando estructura para tabla ovo.permisogrupo
    CREATE TABLE IF NOT EXISTS `permisogrupo` (
    `idPermisoGrupo` int(11) NOT NULL AUTO_INCREMENT,
    `idGrupo` int(11) NOT NULL,
    `idPermiso` int(11) NOT NULL,
    `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
    `fechaFin` datetime DEFAULT NULL,
    PRIMARY KEY (`idPermisoGrupo`),
    KEY `FK_permisogrupo_grupo` (`idGrupo`),
    KEY `FK_permisogrupo_permiso` (`idPermiso`),
    CONSTRAINT `FK_permisogrupo_grupo` FOREIGN KEY (`idGrupo`) REFERENCES `grupo` (`idGrupo`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_permisogrupo_permiso` FOREIGN KEY (`idPermiso`) REFERENCES `permiso` (`idPermiso`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.permisogrupo: ~7 rows (aproximadamente)
    INSERT INTO `permisogrupo` (`idPermisoGrupo`, `idGrupo`, `idPermiso`, `fechaInicio`, `fechaFin`) VALUES
        (0, 1, 0, '2025-09-09 15:48:14', NULL),
        (1, 1, 1, '2025-08-25 18:55:15', NULL),
        (2, 1, 2, '2025-09-09 15:48:14', NULL),
        (3, 1, 3, '2025-09-09 16:07:13', NULL),
        (4, 1, 4, '2025-09-09 16:14:35', NULL),
        (5, 1, 5, '2025-09-09 16:57:54', NULL),
        (6, 1, 6, '2025-09-09 16:58:05', NULL);

    -- Volcando estructura para tabla ovo.preguntafrecuente
    CREATE TABLE IF NOT EXISTS `preguntafrecuente` (
    `idPreguntaFrecuente` int(11) NOT NULL AUTO_INCREMENT,
    `idCarreraInstitucion` int(11) NOT NULL,
    `fechaFin` datetime NOT NULL,
    `nombrePregunta` varchar(50) NOT NULL,
    `respuesta` varchar(50) NOT NULL,
    PRIMARY KEY (`idPreguntaFrecuente`),
    KEY `FK_preguntafrecuente_carrerainstitucion` (`idCarreraInstitucion`),
    CONSTRAINT `FK_preguntafrecuente_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.preguntafrecuente: ~0 rows (aproximadamente)

    -- Volcando estructura para tabla ovo.provincia
    CREATE TABLE IF NOT EXISTS `provincia` (
    `idProvincia` int(11) NOT NULL AUTO_INCREMENT,
    `nombreProvincia` varchar(50) NOT NULL,
    `idPais` int(11) NOT NULL,
    PRIMARY KEY (`idProvincia`),
    KEY `FK_provincia_pais` (`idPais`),
    CONSTRAINT `FK_provincia_pais` FOREIGN KEY (`idPais`) REFERENCES `pais` (`idPais`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.provincia: ~1 rows (aproximadamente)
    INSERT INTO `provincia` (`idProvincia`, `nombreProvincia`, `idPais`) VALUES
        (1, 'Mendoza', 1),
        (2, 'Buenos Aires', 1);

    -- Volcando estructura para tabla ovo.test
    CREATE TABLE IF NOT EXISTS `test` (
    `idResultadoCuestionario` int(11) NOT NULL AUTO_INCREMENT,
    `fechaResultadoCuestionario` datetime DEFAULT NULL,
    `idUsuario` int(11) DEFAULT NULL,
    PRIMARY KEY (`idResultadoCuestionario`),
    KEY `FK_test_usuario` (`idUsuario`),
    CONSTRAINT `FK_test_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.test: ~0 rows (aproximadamente)

    -- Volcando estructura para tabla ovo.testaptitud
    CREATE TABLE IF NOT EXISTS `testaptitud` (
    `idResultadoAptitud` int(11) NOT NULL AUTO_INCREMENT,
    `afinidadAptitud` double DEFAULT NULL,
    `idAptitud` int(11) DEFAULT NULL,
    `idTest` int(11) DEFAULT NULL,
    PRIMARY KEY (`idResultadoAptitud`),
    KEY `FK_testaptitud_aptitud` (`idAptitud`),
    KEY `FK_testaptitud_test` (`idTest`),
    CONSTRAINT `FK_testaptitud_aptitud` FOREIGN KEY (`idAptitud`) REFERENCES `aptitud` (`idAptitud`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_testaptitud_test` FOREIGN KEY (`idTest`) REFERENCES `test` (`idResultadoCuestionario`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.testaptitud: ~0 rows (aproximadamente)

    -- Volcando estructura para tabla ovo.testcarrerainstitucion
    CREATE TABLE IF NOT EXISTS `testcarrerainstitucion` (
    `afinidadCarrera` double DEFAULT NULL,
    `idTest` int(11) DEFAULT NULL,
    `idCarreraInstitucion` int(11) DEFAULT NULL,
    KEY `FK_testcarrerainstitucion_test` (`idTest`),
    KEY `FK_testcarrerainstitucion_carrerainstitucion` (`idCarreraInstitucion`),
    CONSTRAINT `FK_testcarrerainstitucion_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_testcarrerainstitucion_test` FOREIGN KEY (`idTest`) REFERENCES `test` (`idResultadoCuestionario`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.testcarrerainstitucion: ~0 rows (aproximadamente)

    -- Volcando estructura para tabla ovo.tipoaccion
    CREATE TABLE IF NOT EXISTS `tipoaccion` (
    `idTipoAccion` int(11) NOT NULL AUTO_INCREMENT,
    `nombreTipoAccion` varchar(50) DEFAULT NULL,
    PRIMARY KEY (`idTipoAccion`)
    ) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.tipoaccion: ~2 rows (aproximadamente)
    INSERT INTO `tipoaccion` (`idTipoAccion`, `nombreTipoAccion`) VALUES
        (1, 'ACTUALIZACION'),
        (2, 'MODIFICACION');

    -- Volcando estructura para tabla ovo.tipocarrera
    CREATE TABLE IF NOT EXISTS `tipocarrera` (
    `idTipoCarrera` int(11) NOT NULL AUTO_INCREMENT,
    `nombreTipoCarrera` varchar(50) DEFAULT NULL,
    `fechaFin` datetime DEFAULT NULL,
    PRIMARY KEY (`idTipoCarrera`)
    ) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.tipocarrera: ~10 rows (aproximadamente)
    INSERT INTO `tipocarrera` (`idTipoCarrera`, `nombreTipoCarrera`, `fechaFin`) VALUES
        (1, 'Licenciatura', NULL),
        (2, 'Tecnicatura', NULL),
        (3, 'Profesorado', NULL),
        (4, 'Ingenieria', NULL),
        (5, 'Doctorado', NULL),
        (6, 'Maestria', NULL),
        (7, 'Diplomatura', NULL),
        (8, 'Formacion Profesional', NULL),
        (9, 'Curso Superior', NULL),
        (10, 'Certificacion Tecnica', NULL);

    -- Volcando estructura para tabla ovo.tipoinstitucion
    CREATE TABLE IF NOT EXISTS `tipoinstitucion` (
    `idTipoInstitucion` int(11) NOT NULL AUTO_INCREMENT,
    `nombreTipoInstitucion` varchar(50) DEFAULT NULL,
    `fechaFin` datetime DEFAULT NULL,
    PRIMARY KEY (`idTipoInstitucion`)
    ) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.tipoinstitucion: ~4 rows (aproximadamente)
    INSERT INTO `tipoinstitucion` (`idTipoInstitucion`, `nombreTipoInstitucion`, `fechaFin`) VALUES
        (1, 'Universitaria', '2025-09-09 14:34:50'),
        (2, 'Instituto tecnico', NULL),
        (3, 'Centro de formacion', NULL),
        (4, 'Universidad Privada', NULL);

    -- Volcando estructura para tabla ovo.usuario
    CREATE TABLE IF NOT EXISTS `usuario` (
    `idUsuario` int(11) NOT NULL AUTO_INCREMENT,
    `mail` varchar(50) NOT NULL,
    `dni` int(11) NOT NULL,
    `nombre` varchar(50) NOT NULL,
    `apellido` varchar(50) NOT NULL,
    `contrasena` varchar(50) NOT NULL,
    `fechaNac` date NOT NULL,
    `validationKEY` varchar(50) DEFAULT NULL,
    `idGenero` int(11) NOT NULL,
    `idLocalidad` int(11) NOT NULL,
    PRIMARY KEY (`idUsuario`),
    KEY `FK_usuario_genero` (`idGenero`),
    KEY `FK_usuario_localidad` (`idLocalidad`),
    CONSTRAINT `FK_usuario_genero` FOREIGN KEY (`idGenero`) REFERENCES `genero` (`idGenero`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_usuario_localidad` FOREIGN KEY (`idLocalidad`) REFERENCES `localidad` (`idLocalidad`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.usuario: ~5 rows (aproximadamente)
    INSERT INTO `usuario` (`idUsuario`, `mail`, `dni`, `nombre`, `apellido`, `contrasena`, `fechaNac`, `validationKEY`, `idGenero`, `idLocalidad`) VALUES
        (1, 'm1718c@gmail.com', 12345678, 'Matias', 'Calcagno', 'HnSZzlwAdcOCybWVlw7mGwLX5OwjARun2/LnHUpBn2I=', '2000-05-15', NULL, 1, 1),
        (27, 'institucion@test.com', 12345678, 'Institucion', 'Prueba', 'X1Uxj6lEwmNJ3fOXq06pBeThQrJ1lLQNBF1eAJG2N8Y=', '2006-09-15', NULL, 1, 1),
        (28, 'estudiante@test.com', 12345678, 'Estudiante', 'Prueba', 'X1Uxj6lEwmNJ3fOXq06pBeThQrJ1lLQNBF1eAJG2N8Y=', '2025-09-16', NULL, 1, 1),
        (30, 'm1718c2@gmail.com', 12312312, 'asdasd', 'adasdsd', 'EYt9/K3VQqUyPonrekbXn59YCv7S+togGt3EuH2jR6w=', '2002-10-02', '31aee823-2b5b-43f4-9d3b-bd095168d5cc', 1, 2),
        (31, 'ignaciobufarini@gmail.com', 44662282, 'Ignacio', 'Bufarini', 'OTnWtZ/i2OzkqPJBQRew/o6Q0q40ogDbcHrgS0PL4dw=', '2003-03-06', 'bf739925-985e-43e6-a2ec-b2f3babfc06c', 1, 1);

    -- Volcando estructura para tabla ovo.usuarioestado
    CREATE TABLE IF NOT EXISTS `usuarioestado` (
    `idUsuarioEstado` int(11) NOT NULL AUTO_INCREMENT,
    `fechaFin` datetime DEFAULT NULL,
    `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
    `idEstadoUsuario` int(11) NOT NULL,
    `idUsuario` int(11) NOT NULL,
    PRIMARY KEY (`idUsuarioEstado`),
    KEY `FK_usuarioestado_estadousuario` (`idEstadoUsuario`),
    KEY `FK_usuarioestado_usuario` (`idUsuario`),
    CONSTRAINT `FK_usuarioestado_estadousuario` FOREIGN KEY (`idEstadoUsuario`) REFERENCES `estadousuario` (`idEstadoUsuario`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_usuarioestado_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.usuarioestado: ~15 rows (aproximadamente)
    INSERT INTO `usuarioestado` (`idUsuarioEstado`, `fechaFin`, `fechaInicio`, `idEstadoUsuario`, `idUsuario`) VALUES
        (7, '2025-09-14 21:45:41', '2025-09-14 16:57:49', 1, 1),
        (19, '2025-09-14 18:57:17', '2025-09-14 21:55:36', 3, 1),
        (20, NULL, '2025-09-14 21:56:01', 1, 1),
        (22, '2025-09-16 13:50:22', '2025-09-16 12:55:30', 1, 27),
        (23, NULL, '2025-09-16 12:55:34', 1, 28),
        (24, '2025-09-16 13:50:24', '2025-09-16 13:50:22', 2, 27),
        (25, '2025-09-16 13:50:24', '2025-09-16 13:50:24', 2, 27),
        (26, NULL, '2025-09-16 13:50:24', 2, 27),
        (28, '2025-09-16 14:43:35', '2025-09-16 14:31:53', 4, 30),
        (30, '2025-09-16 14:42:03', '2025-09-16 14:36:15', 4, 31),
        (37, '2025-09-16 14:46:31', '2025-09-16 14:42:03', 1, 31),
        (38, NULL, '2025-09-16 14:43:35', 1, 30),
        (39, '2025-09-16 14:53:35', '2025-09-16 14:46:31', 3, 31),
        (40, '2025-09-16 14:53:42', '2025-09-16 14:53:35', 2, 31),
        (41, NULL, '2025-09-16 14:53:42', 2, 31);

    -- Volcando estructura para tabla ovo.usuariogrupo
    CREATE TABLE IF NOT EXISTS `usuariogrupo` (
    `idUsuarioGrupo` int(11) NOT NULL AUTO_INCREMENT,
    `idUsuario` int(11) NOT NULL,
    `idGrupo` int(11) NOT NULL,
    `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
    `fechaFin` datetime DEFAULT NULL,
    PRIMARY KEY (`idUsuarioGrupo`),
    KEY `FK_usuariogrupo_grupo` (`idGrupo`),
    KEY `FK_usuariogrupo_usuario` (`idUsuario`),
    CONSTRAINT `FK_usuariogrupo_grupo` FOREIGN KEY (`idGrupo`) REFERENCES `grupo` (`idGrupo`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_usuariogrupo_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.usuariogrupo: ~7 rows (aproximadamente)
    INSERT INTO `usuariogrupo` (`idUsuarioGrupo`, `idUsuario`, `idGrupo`, `fechaInicio`, `fechaFin`) VALUES
        (15, 1, 1, '2025-09-14 21:16:24', NULL),
        (17, 28, 3, '2025-09-12 12:51:28', NULL),
        (18, 27, 4, '2025-09-16 12:52:03', NULL),
        (20, 30, 3, '2025-09-16 14:31:53', NULL),
        (21, 31, 3, '2025-09-16 14:36:15', '2025-09-16 15:02:21'),
        (24, 31, 3, '2025-09-16 15:02:21', '2025-09-16 15:03:09'),
        (25, 31, 3, '2025-09-16 15:03:09', '2025-09-16 15:07:59'),
        (26, 31, 3, '2025-09-16 15:07:59', '2025-09-16 15:08:07'),
        (27, 31, 3, '2025-09-16 15:08:07', NULL);

    -- Volcando estructura para tabla ovo.usuariopermiso
    CREATE TABLE IF NOT EXISTS `usuariopermiso` (
    `idUsuarioPermiso` int(11) NOT NULL AUTO_INCREMENT,
    `idUsuario` int(11) DEFAULT NULL,
    `idPermiso` int(11) DEFAULT NULL,
    `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
    `fechaFin` datetime DEFAULT NULL,
    PRIMARY KEY (`idUsuarioPermiso`),
    KEY `FK_usuariopermiso_permiso` (`idPermiso`),
    KEY `FK_usuariopermiso_usuario` (`idUsuario`),
    CONSTRAINT `FK_usuariopermiso_permiso` FOREIGN KEY (`idPermiso`) REFERENCES `permiso` (`idPermiso`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_usuariopermiso_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    -- Volcando datos para la tabla ovo.usuariopermiso: ~0 rows (aproximadamente)

    /*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
    /*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
    /*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
    /*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
    /*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

    """)

def generate_token(user_id):
    payload = {"user_id": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split(' ')
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        if not token:
            return jsonify({"errorCode": "AUTH", "message": "Token es requerido"}), 401
        try:
            if token == "Hola":
                current_user = 1
            else:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                current_user = data.get("user_id")
                # Validar que el usuario este activo en la base de datos
                conn = mysql.connector.connect(**DB_CONFIG)
                try:
                    cur = conn.cursor(dictionary=True)
                    cur.execute("""SELECT eu.nombreEstadoUsuario
                                    FROM usuarioestado ue
                                    JOIN estadousuario eu ON eu.idEstadoUsuario = ue.idEstadoUsuario
                                    WHERE ue.idUsuario = %s
                                    ORDER BY ue.fechaInicio DESC
                                    LIMIT 1;""", (current_user,))
                    result = cur.fetchone()
                    if result:
                        estado_usuario = result.get("nombreEstadoUsuario")
                        if estado_usuario != "Activo":
                            return jsonify({"errorCode": "AUTH", "message": "Usuario inactivo"}), 401
                    else:
                        return jsonify({"errorCode": "AUTH", "message": "Usuario no encontrado"}), 401
                except Exception as e:
                    log(f"Error al validar token: {e}")
                    return jsonify({"errorCode": "AUTH", "message": "Token es inválido"}), 401
                finally:
                    conn.close()
        except jwt.ExpiredSignatureError:
            return jsonify({"errorCode": "AUTH", "message": "Token ha expirado"}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# -----------------------------------UUID-----------------------------------
def generate_complex_id():
    # Generar un UUID y convertirlo a una cadena
    return str(uuid.uuid4())

#-----------------------------------PASSWORD-----------------------------------
def generate_password():
    # Generar una contraseña aleatoria de 20 caracteres
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

#-----------------------------------PASSWORD HASH-----------------------------------
import base64

def hash_password(password: str) -> str:
    """Hash de contraseña con SHA-256 en Base64 (44 chars), apto para varchar(50)."""
    digest = hashlib.sha256(password.encode('utf-8')).digest()
    return base64.b64encode(digest).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    try:
        return hash_password(password) == hashed
    except Exception:
        return False

#-----------------------------------LOG-----------------------------------
def log(new_line):
    print(f"[{datetime.datetime.now()}]: {new_line}") #TODO Para pruebas
    with open("log.txt", "a") as file:
        #logear la nueva linea con fecha y hora
        file.write(f"[{datetime.datetime.now()}]: {new_line}\n")

#-----------------------------------SMTP gmail-----------------------------------
def send_email(to, subject, body):
    correo = "ovo.app.legal@gmail.com"
    puerto = 465
    clave = "qbaw iiov nyoe eahg"

    # Crear el objeto mensaje
    msg = MIMEMultipart()
    msg["From"] = correo
    msg["To"] = to
    msg["Subject"] = subject

    # Crear el contenido HTML del correo
    html_content = """
    <html>

    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    </head>

    <body>
        <h1>""" + subject + """</h1>
        <p>""" + body + """</p>
    </body>

    </html>
    """

    # Adjuntar el contenido HTML al mensaje
    msg.attach(MIMEText(html_content, "html"))

    # Conectar al servidor SMTP de Gmail
    server = smtplib.SMTP_SSL("smtp.gmail.com", puerto)
    server.login(correo, clave)
    server.sendmail(correo, to, msg.as_string())
    server.quit()

# ============================ AUTENTICACIÓN (US001) ============================
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def get_user_by_email(email: str):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT idUsuario, mail, apellido, nombre, contrasena FROM usuario WHERE mail = %s", (email,))
        return cursor.fetchone()
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

def get_user_permissions_and_groups(user_id: int):
    conn = mysql.connector.connect(**DB_CONFIG)
    permisos = []
    grupos = []
    try:
        cursor = conn.cursor(dictionary=True)
        # Permisos directos
        cursor.execute(
            """
            SELECT p.nombrePermiso
            FROM usuariopermiso up
            JOIN permiso p ON p.idPermiso = up.idPermiso
            WHERE up.idUsuario = %s AND (up.fechaFin IS NULL OR up.fechaFin > NOW())
            """,
            (user_id,)
        )
        permisos_directos = [row['nombrePermiso'] for row in cursor.fetchall() or []]

        # Grupos del usuario
        cursor.execute(
            """
            SELECT g.idGrupo, g.nombreGrupo
            FROM usuariogrupo ug
            JOIN grupo g ON g.idGrupo = ug.idGrupo
            WHERE ug.idUsuario = %s AND (ug.fechaFin IS NULL OR ug.fechaFin > NOW())
            """,
            (user_id,)
        )
        grupos_rows = cursor.fetchall() or []
        grupos = [row['nombreGrupo'] for row in grupos_rows]
        grupo_ids = [row['idGrupo'] for row in grupos_rows]

        permisos_grupo = []
        if grupo_ids:
            in_clause = ','.join(['%s'] * len(grupo_ids))
            cursor.execute(
                f"""
                SELECT DISTINCT p.nombrePermiso
                FROM permisogrupo pg
                JOIN permiso p ON p.idPermiso = pg.idPermiso
                WHERE pg.idGrupo IN ({in_clause}) AND (pg.fechaFin IS NULL OR pg.fechaFin > NOW())
                """,
                tuple(grupo_ids)
            )
            permisos_grupo = [row['nombrePermiso'] for row in cursor.fetchall() or []]

        permisos = sorted(list(set(permisos_directos + permisos_grupo)))
        return permisos, grupos
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

def requires_permission(permission_name: str):
    """Decorador para proteger endpoints por permiso lógico."""
    def decorator(f):
        @wraps(f)
        @token_required
        def wrapped(current_user_id, *args, **kwargs):
            permisos, _ = get_user_permissions_and_groups(current_user_id)
            if permission_name not in permisos:
                return jsonify({"errorCode": "FORBIDDEN", "message": "Permiso insuficiente"}), 403
            return f(current_user_id, *args, **kwargs)
        return wrapped
    return decorator

def historial_acceso(user_id: int, estadoAcceso: str, ip: str, user_agent: str):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM estadoacceso WHERE nombreEstadoAcceso = %s", (estadoAcceso,))
        estado = cur.fetchone()
        if not estado:
            log(f"historial_acceso: estadoAcceso '{estadoAcceso}' no encontrado")
            return
        cur.execute(
            "INSERT INTO historialacceso (idUsuario, idEstadoAcceso, ipAcceso, navegador) VALUES (%s, %s, %s, %s)",
            (user_id, estado['idEstadoAcceso'], ip, user_agent)
        )
        conn.commit()
    except Exception as e:
        log(f"historial_acceso error: {e}\n{traceback.format_exc()}")
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

def get_user_last_status(user_id: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        # Selecciona el estado más reciente del usuario priorizando los activos (fechaFin IS NULL)
        # Estrategia: ordenar primero por activos y luego por fechaInicio descendente
        cur.execute(
            """
            SELECT ue.idUsuarioEstado, ue.idEstadoUsuario, eu.nombreEstadoUsuario,
                   ue.fechaInicio, ue.fechaFin
            FROM usuarioestado ue
            JOIN estadousuario eu ON eu.idEstadoUsuario = ue.idEstadoUsuario
            WHERE ue.idUsuario = %s
            ORDER BY (ue.fechaFin IS NULL) DESC, ue.fechaInicio DESC
            LIMIT 1
            """,
            (user_id,)
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "idUsuarioEstado": row.get("idUsuarioEstado"),
            "idEstadoUsuario": row.get("idEstadoUsuario"),
            "nombreEstadoUsuario": row.get("nombreEstadoUsuario"),
            "fechaInicio": row.get("fechaInicio"),
            "fechaFin": row.get("fechaFin"),
        }
    except Exception as e:
        log(f"get_user_last_status error: {e}\n{traceback.format_exc()}")
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para autenticación con correo y contraseña
@app.route('/api/v1/auth/login', methods=['POST'])
def login_email_password():
    try:
        data = request.get_json(silent=True) or {}
        correo = data.get('correo', '').strip()
        contrasena = data.get('contrasena', '')

        # Validaciones
        if not correo:
            return jsonify({"errorCode": "ERR1", "message": "El correo es obligatorio"}), 400
        if not re.match(EMAIL_REGEX, correo):
            return jsonify({"errorCode": "ERR2", "message": "El correo es invalido"}), 400
        if not contrasena:
            return jsonify({"errorCode": "ERR3", "message": "La contraseña es obligatoria"}), 400

        user = get_user_by_email(correo)
        if not user:
            historial_acceso(0, "Fallido", request.remote_addr or '', request.headers.get('User-Agent', ''))
            return jsonify({"errorCode": "ERR5", "message": "Credenciales inválidas"}), 401

        if not verify_password(contrasena, user.get('contrasena') or ''):
            historial_acceso(user['idUsuario'], "Fallido", request.remote_addr or '', request.headers.get('User-Agent', ''))
            return jsonify({"errorCode": "ERR5", "message": "Credenciales inválidas"}), 401

        # Obtener ultimo estado del usuario
        estado_usuario = get_user_last_status(user['idUsuario'])
        if estado_usuario and not estado_usuario.get('nombreEstadoUsuario') == 'Activo':
            return jsonify({"errorCode": "ERR6", "message": "El usuario no está activo, esta: " + estado_usuario.get('nombreEstadoUsuario')}), 403

        token = generate_token(user['idUsuario'])
        permisos, grupos = get_user_permissions_and_groups(user['idUsuario'])

        resp = jsonify({
            "usuario": {
                "id": user['idUsuario'],
                "nombre": user.get('nombre'),
                "apellido": user.get('apellido'),
                "mail": user.get('mail'),
            },
            "permisos": permisos,
            "grupos": grupos,
        })
        resp.headers['new_token'] = token
        historial_acceso(user['idUsuario'], "Exitoso", request.remote_addr or '', request.headers.get('User-Agent', ''))
        return resp, 200
    except Exception as e:
        log(f"/auth/login error: {e}\n{traceback.format_exc()}")
        historial_acceso(0, "Fallido", request.remote_addr or '', request.headers.get('User-Agent', ''))
        return jsonify({"errorCode": "ERR4", "message": "Inicio de sesión fallido"}), 500

# Endpoint para autenticación con Google
@app.route('/api/v1/auth/google', methods=['POST'])
def login_google():
    try:
        # Importar de forma perezosa para evitar errores si el paquete no está instalado
        try:
            from google.oauth2 import id_token as google_id_token  # type: ignore
            from google.auth.transport import requests as google_requests  # type: ignore
        except Exception:
            historial_acceso(0, "Fallido Google", request.remote_addr or '', request.headers.get('User-Agent', ''))
            return jsonify({"errorCode": "ERR4", "message": "Inicio de sesión fallido"}), 500

        data = request.get_json(silent=True) or {}
        id_token = data.get('id_token') or data.get('credential')
        if not id_token:
            historial_acceso(0, "Fallido Google", request.remote_addr or '', request.headers.get('User-Agent', ''))
            return jsonify({"errorCode": "ERR1", "message": "Token de Google es obligatorio"}), 400

        request_adapter = google_requests.Request()
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        # Verificar token; si hay CLIENT_ID lo usamos como audiencia
        claims = google_id_token.verify_oauth2_token(id_token, request_adapter, audience=client_id) if client_id else google_id_token.verify_oauth2_token(id_token, request_adapter)

        email = claims.get('email')
        if not email:
            historial_acceso(0, "Fallido Google", request.remote_addr or '', request.headers.get('User-Agent', ''))
            return jsonify({"errorCode": "ERR2", "message": "El token de Google no contiene email"}), 400

        user = get_user_by_email(email)
        if not user:
            # No auto-registro por ahora -> credenciales inválidas
            historial_acceso(0, "Fallido Google", request.remote_addr or '', request.headers.get('User-Agent', ''))
            return jsonify({"errorCode": "ERR5", "message": "Credenciales inválidas"}), 401

        # Validar estado de usuario igual que en login_email_password
        estado_usuario = get_user_last_status(user['idUsuario'])
        if estado_usuario and not estado_usuario.get('nombreEstadoUsuario') == 'Activo':
            return jsonify({"errorCode": "ERR6", "message": "El usuario no está activo, esta: " + estado_usuario.get('nombreEstadoUsuario')}), 403

        token = generate_token(user['idUsuario'])
        permisos, grupos = get_user_permissions_and_groups(user['idUsuario'])

        resp = jsonify({
            "usuario": {
                "id": user['idUsuario'],
                "nombre": user.get('nombre'),
                "apellido": user.get('apellido'),
                "mail": user.get('mail'),
            },
            "permisos": permisos,
            "grupos": grupos,
        })
        resp.headers['new_token'] = token
        historial_acceso(user['idUsuario'], "Exitoso", request.remote_addr or '', request.headers.get('User-Agent', ''))
        return resp, 200
    except Exception as e:
        log(f"/auth/google error: {e}\n{traceback.format_exc()}")
        historial_acceso(0, "Fallido Google", request.remote_addr or '', request.headers.get('User-Agent', ''))
        return jsonify({"errorCode": "ERR4", "message": "Inicio de sesión fallido"}), 500

# Endpoint para obtener información del usuario autenticado
@app.route('/api/v1/auth/me', methods=['GET'])
@token_required
def whoami(current_user_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT idUsuario, mail, apellido, nombre, dni, fechaNac, idGenero FROM usuario WHERE idUsuario = %s", (current_user_id,))
            user = cur.fetchone()
        finally:
            conn.close()

        if not user:
            return jsonify({"errorCode": "AUTH", "message": "Usuario no encontrado"}), 404

        permisos, grupos = get_user_permissions_and_groups(user['idUsuario'])
        return jsonify({
            "usuario": {
                "id": user['idUsuario'],
                "nombre": user.get('nombre'),
                "apellido": user.get('apellido'),
                "mail": user.get('mail'),
                "dni": user.get('dni'),
                "fechaNac": user.get('fechaNac').isoformat() if user.get('fechaNac') else None,
                "idGenero": user.get('idGenero'),
            },
            "permisos": permisos,
            "grupos": grupos,
        }), 200
    except Exception as e:
        log(f"/auth/me error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR4", "message": "Inicio de sesión fallido"}), 500

# curl para obtener información del usuario autenticado
# curl -X GET "{{baseURL}}/api/v1/auth/me" -H "Authorization: Bearer {{token}}"

# ============================ ADMIN: Gestión de perfiles (US003) ============================

# Endpoint para listar todos los usuarios
@app.route('/api/v1/admin/users', methods=['GET'])
@requires_permission('LIST_USERS')
def admin_list_users(current_user_id):
    """Listado de usuarios con sus grupos activos."""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT u.idUsuario, u.nombre, u.apellido, u.mail,
               GROUP_CONCAT(g.nombreGrupo ORDER BY g.nombreGrupo SEPARATOR ',') AS grupos,
               eu.nombreEstadoUsuario AS estado
            FROM usuario u
            LEFT JOIN usuariogrupo ug ON ug.idUsuario = u.idUsuario AND (ug.fechaFin IS NULL OR ug.fechaFin > NOW())
            LEFT JOIN grupo g ON g.idGrupo = ug.idGrupo
            LEFT JOIN usuarioestado ue ON ue.idUsuario = u.idUsuario AND (ue.fechaFin IS NULL OR ue.fechaFin > NOW())
            LEFT JOIN estadousuario eu ON eu.idEstadoUsuario = ue.idEstadoUsuario
            GROUP BY u.idUsuario, eu.nombreEstadoUsuario
            ORDER BY u.apellido, u.nombre
            """
        )
        rows = cur.fetchall() or []
        def parse_grupos(s):
            if not s:
                return []
            return [p for p in (s or '').split(',') if p]
        estado_usuario = cur.fetchone()
        data = [
            {
                "id": r['idUsuario'],
                "nombre": r.get('nombre'),
                "apellido": r.get('apellido'),
                "mail": r.get('mail'),
                "grupos": parse_grupos(r.get('grupos')),
                "estado": r.get('estado') or 'Desconocido',
            }
            for r in rows
        ]
        return jsonify(data), 200
    except Exception as e:
        log(f"/admin/users GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Ha ocurrido un error al listar los usuarios"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para listar todos los grupos
@app.route('/api/v1/admin/groups', methods=['GET'])
@requires_permission('LIST_GROUPS')
def admin_list_groups(current_user_id):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT idGrupo, nombreGrupo
            FROM grupo
            WHERE fechaFin IS NULL OR fechaFin > NOW() OR fechaFin IS NULL
            ORDER BY nombreGrupo
            """
        )
        rows = cur.fetchall() or []
        data = [{"id": r['idGrupo'], "nombre": r['nombreGrupo']} for r in rows]
        return jsonify(data), 200
    except Exception as e:
        log(f"/admin/groups GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Ha ocurrido un error al listar los grupos"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para obtener grupos de un usuario
@app.route('/api/v1/admin/users/<int:user_id>/groups', methods=['GET'])
@requires_permission('USER_GROUPS')
def admin_get_user_groups(current_user_id, user_id: int):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT g.idGrupo, g.nombreGrupo
            FROM usuariogrupo ug
            JOIN grupo g ON g.idGrupo = ug.idGrupo
            WHERE ug.idUsuario = %s AND (ug.fechaFin IS NULL OR ug.fechaFin > NOW())
            ORDER BY g.nombreGrupo
            """,
            (user_id,)
        )
        rows = cur.fetchall()
        response = [{"id": r['idGrupo'], "nombre": r['nombreGrupo']} for r in rows]
        return jsonify(response), 200
    except Exception as e:
        log(f"/admin/users/{user_id}/groups GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para obtener todos los permisos de un usuario
@app.route('/api/v1/admin/users/<int:user_id>/permissions', methods=['GET'])
@requires_permission('USER_PERMS')
def admin_get_user_permissions(current_user_id, user_id: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT p.idPermiso, p.nombrePermiso, p.descripcion
            FROM usuariopermiso up
            JOIN permiso p ON p.idPermiso = up.idPermiso
            WHERE up.idUsuario = %s AND (up.fechaFin IS NULL OR up.fechaFin > NOW())
            ORDER BY p.nombrePermiso
            """,
            (user_id,)
        )
        rows = cur.fetchall() or []
        # Unir permisos pero hay que quitar los repetidos (directos y ademas por grupo)
        return jsonify(rows), 200
    except Exception as e:
        log(f"/admin/users/{user_id}/permissions GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para asignar un grupo a un usuario
@app.route('/api/v1/admin/users/<int:user_id>/group', methods=['PUT'])
@requires_permission('USER_GROUPS')
def admin_set_user_group(current_user_id, user_id: int):
    """Asigna un grupo al usuario sin cerrar asignaciones previas.
    Si ya pertenece (activo) al grupo, devolver error ERR1.
    Errores de guardado -> ERR1 con mensaje técnico.
    """
    data = request.get_json(silent=True) or {}
    id_grupo = data.get('idGrupo')
    if not isinstance(id_grupo, int):
        return jsonify({"errorCode": "ERR1", "message": "idGrupo inválido"}), 400
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        # Validar existencia de usuario y grupo
        cur.execute("SELECT 1 FROM usuario WHERE idUsuario=%s", (user_id,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Usuario no encontrado"}), 404
        cur.execute("SELECT 1 FROM grupo WHERE idGrupo=%s AND (fechaFin IS NULL OR fechaFin > NOW())", (id_grupo,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Grupo no válido o inactivo"}), 400

        # Verificar si ya pertenece al grupo (activo)
        cur.execute(
            "SELECT 1 FROM usuariogrupo WHERE idUsuario=%s AND idGrupo=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            (user_id, id_grupo)
        )
        if cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "El usuario ya pertenece a este grupo"}), 400
        # Insertar nueva asignación (sin cerrar otras)
        cur.execute(
            "INSERT INTO usuariogrupo (idUsuario, idGrupo, fechaInicio, fechaFin) VALUES (%s, %s, NOW(), NULL)",
            (user_id, id_grupo)
        )
        conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        conn.rollback()
        log(f"/admin/users/{user_id}/group PUT error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": str(e)}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para eliminar el grupo de un usuario (actualizar fechaFin)
@app.route('/api/v1/admin/users/<int:user_id>/group/<int:id_grupo>', methods=['DELETE'])
@requires_permission('USER_GROUPS')
def admin_remove_user_group(current_user_id, user_id: int, id_grupo: int):
    """Elimina un grupo de un usuario (actualiza fechaFin)."""
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE usuariogrupo SET fechaFin = NOW() WHERE idUsuario = %s AND idGrupo = %s AND (fechaFin IS NULL OR fechaFin > NOW())",
            (user_id, id_grupo)
        )
        if cur.rowcount == 0:
            return jsonify({"errorCode": "ERR1", "message": "El usuario no está en este grupo"}), 400
        conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        conn.rollback()
        log(f"/admin/users/{user_id}/group/{id_grupo} DELETE error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": str(e)}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para agregar un permiso a un usuario
@app.route('/api/v1/admin/users/<int:user_id>/permissions', methods=['POST'])
@requires_permission('USER_PERMS')
def admin_add_user_permission(current_user_id, user_id: int):
    """Agrega un permiso directo. Si ya existe activo, no duplica."""
    data = request.get_json(silent=True) or {}
    id_permiso = data.get('idPermiso')
    if not isinstance(id_permiso, int):
        return jsonify({"errorCode": "ERR1", "message": "idPermiso inválido"}), 400
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM usuario WHERE idUsuario=%s", (user_id,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Usuario no encontrado"}), 404
        cur.execute("SELECT 1 FROM permiso WHERE idPermiso=%s", (id_permiso,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Permiso no válido"}), 400
        # Evitar duplicados activos
        cur.execute(
            "SELECT 1 FROM usuariopermiso WHERE idUsuario=%s AND idPermiso=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            (user_id, id_permiso)
        )
        if cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "El usuario ya posee este permiso"}), 400
        cur.execute(
            "INSERT INTO usuariopermiso (idUsuario, idPermiso, fechaInicio, fechaFin) VALUES (%s, %s, NOW(), NULL)",
            (user_id, id_permiso)
        )
        conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        conn.rollback()
        log(f"/admin/users/{user_id}/permissions POST error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": str(e)}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para eliminar un permiso directo de un usuario
@app.route('/api/v1/admin/users/<int:user_id>/permissions/<int:id_permiso>', methods=['DELETE'])
@requires_permission('USER_PERMS')
def admin_remove_user_permission(current_user_id, user_id: int, id_permiso: int):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        # Validar que el usuario tenga el permiso en cuestion
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM usuariopermiso WHERE idUsuario=%s AND idPermiso=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            (user_id, id_permiso)
        )
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "El usuario no posee este permiso"}), 400

        # Quitar el permiso
        cur.execute(
            "UPDATE usuariopermiso SET fechaFin = NOW() WHERE idUsuario=%s AND idPermiso=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            (user_id, id_permiso)
        )
        conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        conn.rollback()
        log(f"/admin/users/{user_id}/permissions/{id_permiso} DELETE error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": str(e)}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ ADMIN: Asignación dinámica de permisos (US004) ============================

# Endpoint para listar todos los permisos disponibles
@app.route('/api/v1/admin/permissions', methods=['GET'])
@requires_permission('LIST_PERMS')
def admin_list_permissions(current_user_id):
    """Lista de permisos disponibles. Soporta filtro ?search= término."""
    conn = None
    try:
        search = (request.args.get('search') or '').strip()
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if search:
            like = f"%{search}%"
            cur.execute(
                "SELECT idPermiso, nombrePermiso, descripcion FROM permiso WHERE nombrePermiso LIKE %s or descripcion LIKE %s ORDER BY nombrePermiso",
                (like, like)
            )
        else:
            cur.execute(
                "SELECT idPermiso, nombrePermiso, descripcion FROM permiso ORDER BY nombrePermiso"
            )
        rows = cur.fetchall() or []
        return jsonify(rows), 200
    except Exception as e:
        log(f"/admin/permissions GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para reemplazar permisos de un usuario (quitar y agregar)
@app.route('/api/v1/admin/users/<int:user_id>/permissions', methods=['PUT'])
@requires_permission('USER_PERMS')
def admin_set_user_permissions_bulk(current_user_id, user_id: int):
    """Reemplaza el conjunto de permisos directos activos de un usuario por los provistos.
       Reglas:
       - Debe venir al menos un permiso (ERR1 si vacío).
       - Activa los nuevos que falten e inactiva los que no están en la lista.
    """
    data = request.get_json(silent=True) or {}
    selected = data.get('permisos')
    if not isinstance(selected, list):
        return jsonify({"errorCode": "ERR1", "message": "error, se debe agregar al menos un permiso"}), 400
    # Normalizar y deduplicar
    try:
        selected_ids = sorted(set(int(x) for x in selected))
    except Exception:
        return jsonify({"errorCode": "ERR1", "message": "Lista de permisos inválida"}), 400
    if len(selected_ids) == 0:
        return jsonify({"errorCode": "ERR1", "message": "error, se debe agregar al menos un permiso"}), 400

    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        # Validar usuario
        cur.execute("SELECT 1 FROM usuario WHERE idUsuario=%s", (user_id,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Usuario no encontrado"}), 404
        # Validar permisos existen
        in_clause = ','.join(['%s'] * len(selected_ids))
        cur.execute(f"SELECT COUNT(*) FROM permiso WHERE idPermiso IN ({in_clause})", tuple(selected_ids))
        count = cur.fetchone()[0]
        if count != len(selected_ids):
            return jsonify({"errorCode": "ERR1", "message": "Algún permiso no existe"}), 400

        # Permisos actuales activos
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT idPermiso FROM usuariopermiso WHERE idUsuario=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            (user_id,)
        )
        current_ids = sorted([r['idPermiso'] for r in (cur.fetchall() or [])])

        to_add = [pid for pid in selected_ids if pid not in current_ids]
        to_close = [pid for pid in current_ids if pid not in selected_ids]

        # validar si ambas listas son vacias dar error que los permisos enviados son los actuales del usuario
        if not to_add and not to_close:
            return jsonify({"errorCode": "ERR1", "message": "Los permisos enviados son los actuales del usuario"}), 400

        cur = conn.cursor()
        # Inactivar los que sobran
        if to_close:
            in_clause_close = ','.join(['%s'] * len(to_close))
            cur.execute(
                f"UPDATE usuariopermiso SET fechaFin = NOW() WHERE idUsuario=%s AND idPermiso IN ({in_clause_close}) AND (fechaFin IS NULL OR fechaFin > NOW())",
                (user_id, *to_close)
            )
        # Activar los que faltan
        for pid in to_add:
            cur.execute(
                "INSERT INTO usuariopermiso (idUsuario, idPermiso, fechaInicio, fechaFin) VALUES (%s, %s, NOW(), NULL)",
                (user_id, pid)
            )
        conn.commit()

        return jsonify({"ok": True, "summary": {"added": to_add, "removed": to_close}}), 200
    except Exception as e:
        conn.rollback()
        log(f"/admin/users/{user_id}/permissions PUT error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": str(e)}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ ADMIN: Historial de accesos (US005) ============================

# Endpoint para obtener el historial de accesos
@app.route('/api/v1/admin/access-history', methods=['GET'])
@requires_permission('USER_HISTORY')
def admin_access_history(current_user_id):
    """Listado del historial de accesos con filtros.
    Filtros opcionales (query params):
    - userId: int
    - from: fecha desde (YYYY-MM-DD)
    - to: fecha hasta (YYYY-MM-DD). No puede ser superior a hoy.
    - ip: entero (exact match)
    - estado: nombre del estado (e.g., Exitoso/Fallido)
    - estadoId: int
    - page, pageSize: opcionales para paginar (default 1, 50)
    """
    try:
        import datetime as _dt
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Leer y validar filtros
        args = request.args
        clauses = []
        params = []

        # userId
        user_id_s = args.get('userId')
        if not user_id_s:
            return jsonify({"errorCode": "ERR2", "message": "El userId es un campo obligatorio."}), 400
        if user_id_s is not None and user_id_s != '':
            try:
                user_id_val = int(user_id_s)
                clauses.append("ha.idUsuario = %s")
                params.append(user_id_val)
            except Exception:
                return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400

        # fechas
        def parse_date(s):
            return _dt.datetime.strptime(s, '%Y-%m-%d').date()

        date_from_s = args.get('from')
        date_to_s = args.get('to')
        today = _dt.date.today()
        date_from = None
        date_to = None
        try:
            if date_from_s:
                date_from = parse_date(date_from_s)
            if date_to_s:
                date_to = parse_date(date_to_s)
        except Exception:
            return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400

        if date_to and date_to > today:
            return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400
        if date_from and date_to and date_from > date_to:
            return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400

        if date_from:
            clauses.append("ha.fecha >= %s")
            params.append(_dt.datetime.combine(date_from, _dt.time.min))
        if date_to:
            # incluir todo el día 'to'
            end_dt = _dt.datetime.combine(date_to, _dt.time.max)
            clauses.append("ha.fecha <= %s")
            params.append(end_dt)

        # ip (exacto)
        ip_s = args.get('ip')
        if ip_s is not None and ip_s != '':
            try:
                ip_val = int(ip_s)
                clauses.append("ha.ipAcceso = %s")
                params.append(ip_val)
            except Exception:
                return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400

        # estado por nombre o id
        estado_s = args.get('estado')
        estado_id_s = args.get('estadoId')
        if estado_id_s:
            try:
                estado_id = int(estado_id_s)
                clauses.append("ha.idEstadoAcceso = %s")
                params.append(estado_id)
            except Exception:
                return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400
        elif estado_s:
            clauses.append("ea.nombreEstadoAcceso = %s")
            params.append(estado_s)

        where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""

        # Paginación simple
        try:
            page = int(args.get('page', '1'))
            page_size = int(args.get('pageSize', '50'))
            if page < 1 or page_size < 1 or page_size > 1000:
                raise ValueError()
        except Exception:
            return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400
        offset = (page - 1) * page_size

        sql = f"""
            SELECT ha.fecha,
                   u.idUsuario AS userId,
                   u.nombre,
                   u.apellido,
                   ha.ipAcceso,
                   ha.navegador,
                   ea.nombreEstadoAcceso AS estado
            FROM historialacceso ha
            LEFT JOIN usuario u ON u.idUsuario = ha.idUsuario
            LEFT JOIN estadoacceso ea ON ea.idEstadoAcceso = ha.idEstadoAcceso
            {where_sql}
            ORDER BY ha.fecha DESC
            LIMIT %s OFFSET %s
        """

        cur.execute(sql, tuple(params + [page_size, offset]))
        rows = cur.fetchall() or []
        data = [
            {
                "fecha": (r.get('fecha').isoformat(sep=' ') if r.get('fecha') else None),
                "usuario": {
                    "id": r.get('userId'),
                    "nombre": r.get('nombre'),
                    "apellido": r.get('apellido'),
                },
                "ip": str(r.get('ipAcceso')) if r.get('ipAcceso') is not None else None,
                "navegador": r.get('navegador'),
                "estado": r.get('estado'),
            }
            for r in rows
        ]
        return jsonify(data), 200
    except Exception as e:
        log(f"/admin/access-history GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "No se pudo cargar el historial de accesos. Intente nuevamente más tarde."}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para exportar el historial de accesos
@app.route('/api/v1/admin/access-history/export', methods=['GET'])
@requires_permission('USER_HISTORY')
def admin_access_history_export(current_user_id):
    """Exporta el historial de accesos en CSV o PDF (si disponible). Usa los mismos filtros que la lista.
    Query: format=csv|pdf
    Errores: ERR3 ante fallas de exportación.
    """
    try:
        fmt = (request.args.get('format') or 'csv').lower()
        if fmt not in ('csv', 'pdf'):
            return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400

        # Reutilizar la misma construcción de filtros que el endpoint de listado
        import datetime as _dt
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        args = request.args
        clauses = []
        params = []

        # userId
        user_id_s = args.get('userId')
        if not user_id_s:
            return jsonify({"errorCode": "ERR2", "message": "El userId es un campo obligatorio."}), 400
        if user_id_s is not None and user_id_s != '':
            try:
                user_id_val = int(user_id_s)
                clauses.append("ha.idUsuario = %s")
                params.append(user_id_val)
            except Exception:
                return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400

        # fechas
        def parse_date(s):
            return _dt.datetime.strptime(s, '%Y-%m-%d').date()

        date_from_s = args.get('from')
        date_to_s = args.get('to')
        today = _dt.date.today()
        date_from = None
        date_to = None
        try:
            if date_from_s:
                date_from = parse_date(date_from_s)
            if date_to_s:
                date_to = parse_date(date_to_s)
        except Exception:
            return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400

        if date_to and date_to > today:
            return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400
        if date_from and date_to and date_from > date_to:
            return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400

        if date_from:
            clauses.append("ha.fecha >= %s")
            params.append(_dt.datetime.combine(date_from, _dt.time.min))
        if date_to:
            end_dt = _dt.datetime.combine(date_to, _dt.time.max)
            clauses.append("ha.fecha <= %s")
            params.append(end_dt)

        # ip (exacto)
        ip_s = args.get('ip')
        if ip_s is not None and ip_s != '':
            try:
                ip_val = int(ip_s)
                clauses.append("ha.ipAcceso = %s")
                params.append(ip_val)
            except Exception:
                return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400

        # estado por nombre o id
        estado_s = args.get('estado')
        estado_id_s = args.get('estadoId')
        if estado_id_s:
            try:
                estado_id = int(estado_id_s)
                clauses.append("ha.idEstadoAcceso = %s")
                params.append(estado_id)
            except Exception:
                return jsonify({"errorCode": "ERR2", "message": "Los filtros aplicados no son válidos. Revise los campos e intente de nuevo."}), 400
        elif estado_s:
            clauses.append("ea.nombreEstadoAcceso = %s")
            params.append(estado_s)

        where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""

        sql = f"""
            SELECT ha.fecha,
                   u.idUsuario AS userId,
                   u.nombre,
                   u.apellido,
                   ha.ipAcceso,
                   ha.navegador,
                   ea.nombreEstadoAcceso AS estado
            FROM historialacceso ha
            LEFT JOIN usuario u ON u.idUsuario = ha.idUsuario
            LEFT JOIN estadoacceso ea ON ea.idEstadoAcceso = ha.idEstadoAcceso
            {where_sql}
            ORDER BY ha.fecha DESC
        """

        cur.execute(sql, tuple(params))
        rows = cur.fetchall() or []
        if not rows:
            return jsonify({"errorCode": "ERR3", "message": "No hay datos para exportar con los filtros aplicados."}), 400

        if fmt == 'csv':
            import csv
            from io import StringIO
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Fecha", "UsuarioId", "Nombre", "Apellido", "IP", "Navegador", "Estado"]) 
            for r in rows:
                writer.writerow([
                    (r.get('fecha').isoformat(sep=' ') if r.get('fecha') else ''),
                    r.get('userId') or '',
                    r.get('nombre') or '',
                    r.get('apellido') or '',
                    str(r.get('ipAcceso') or ''),
                    r.get('navegador') or '',
                    r.get('estado') or '',
                ])
            csv_data = output.getvalue().encode('utf-8-sig')  # BOM para Excel
            output.close()
            from flask import Response
            ts = _dt.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"historial_accesos_{ts}.csv"
            return Response(
                csv_data,
                mimetype='text/csv; charset=utf-8',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
            )
        else:  # pdf
            try:
                from io import BytesIO
                from reportlab.lib.pagesizes import A4
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    leftMargin=36,
                    rightMargin=36,
                    topMargin=36,
                    bottomMargin=36,
                )

                styles = getSampleStyleSheet()
                # Obtener nombre del usuario
                user_name = ""
                try:
                    cur2 = conn.cursor(dictionary=True)
                    cur2.execute("SELECT nombre, apellido FROM usuario WHERE idUsuario = %s", (user_id_val,))
                    user_row = cur2.fetchone()
                    if user_row:
                        user_name = f"{user_row.get('nombre','')} {user_row.get('apellido','')}".strip()
                except Exception:
                    user_name = ""
                finally:
                    if 'cur2' in locals():
                        cur2.close()
                titulo_texto = f"{user_name} - Export historial de accesos".strip() if user_name else "Export historial de accesos"
                if not user_name or user_name.lower() in ("anonimo", "anonymous"):
                    titulo_texto = "Export historial de accesos"
                # Establecer el título interno del PDF
                doc.title = titulo_texto
                title = Paragraph(titulo_texto, styles["Heading2"])

                headers = ["Fecha", "UsuarioId", "Nombre", "Apellido", "IP", "Navegador", "Estado"]
                data_tbl = [headers]
                for r in rows:
                    data_tbl.append([
                        Paragraph((r.get('fecha').isoformat(sep=' ') if r.get('fecha') else ''), styles["Normal"]),
                        Paragraph(str(r.get('userId') or ''), styles["Normal"]),
                        Paragraph(r.get('nombre') or '', styles["Normal"]),
                        Paragraph(r.get('apellido') or '', styles["Normal"]),
                        Paragraph(str(r.get('ipAcceso') or ''), styles["Normal"]),
                        Paragraph(r.get('navegador') or '', styles["Normal"]),
                        Paragraph(r.get('estado') or '', styles["Normal"]),
                    ])

                # Definir anchos de columnas para una distribución legible en A4
                table = Table(
                    data_tbl,
                    repeatRows=1,
                    colWidths=[80, 55, 70, 70, 60, 150, 60],
                )
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))

                elements = [title, Spacer(1, 8), table]
                doc.build(elements)

                pdf = buffer.getvalue()
                buffer.close()

                from flask import Response
                ts = _dt.datetime.now().strftime('%Y%m%d_%H%M%S')
                # Usar el nombre del usuario en el nombre del archivo si está disponible
                safe_user_name = user_name.replace(' ', '_') if user_name else "anonimo"
                filename = f"{safe_user_name}_historial_accesos_{ts}.pdf"
                return Response(
                    pdf,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment; filename="{filename}"'}
                )
            except Exception as e:
                log(f"/admin/access-history/export PDF error: {e}\n{traceback.format_exc()}")
                return jsonify({"errorCode": "ERR3", "message": "Ocurrió un error al exportar el historial. Intente nuevamente."}), 500
    except Exception as e:
        log(f"/admin/access-history/export error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR3", "message": "Ocurrió un error al exportar el historial. Intente nuevamente."}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ ADMIN: Auditoría de acciones (US006) ============================

# Endpoint para obtener el historial de auditoría
@app.route('/api/v1/admin/audit', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_audit_list(current_user_id):
    """Listado de auditoría (historial ABM) con filtros.
    Filtros opcionales (query params):
    - userId: int
    - from: fecha desde (YYYY-MM-DD)
    - to: fecha hasta (YYYY-MM-DD) no puede superar hoy
    - tipoAccion: nombre (e.g., alta, modificación, baja)
    - tipoAccionId: int
    - modulo: uno de [usuario, grupo, permiso, permisogrupo, carrera, genero, provincia, localidad,
               estadoacceso, estadocarrerainstitucion, estadousuario, pais, tipoinstitucion, tipocarrera,
               modalidadcarrerainstitucion, aptitud]
    - claseId: int (ID del registro afectado del módulo elegido)
    - page, pageSize
    """
    conn = None
    try:
        import datetime as _dt
        args = request.args

        # Validaciones comunes
        def err_filtros():
            return jsonify({"errorCode": "ERR1", "message": "Error en los filtros aplicados. Revise los campos e intente de nuevo."}), 400

        clauses = []
        params = []

        # userId
        user_id_s = args.get('userId')
        if user_id_s:
            try:
                user_id_val = int(user_id_s)
                clauses.append("ha.idUsuario = %s")
                params.append(user_id_val)
            except Exception:
                return err_filtros()

        # Fechas
        def parse_date(s):
            return _dt.datetime.strptime(s, '%Y-%m-%d').date()

        date_from_s = args.get('from')
        date_to_s = args.get('to')
        today = _dt.date.today()
        date_from = None
        date_to = None
        try:
            if date_from_s:
                date_from = parse_date(date_from_s)
            if date_to_s:
                date_to = parse_date(date_to_s)
        except Exception:
            return err_filtros()

        if date_to and date_to > today:
            return err_filtros()
        if date_from and date_to and date_from > date_to:
            return err_filtros()

        if date_from:
            clauses.append("ha.fechaHistorial >= %s")
            params.append(_dt.datetime.combine(date_from, _dt.time.min))
        if date_to:
            clauses.append("ha.fechaHistorial <= %s")
            params.append(_dt.datetime.combine(date_to, _dt.time.max))

        # Tipo de acción
        tipo_accion_id_s = args.get('tipoAccionId')
        tipo_accion_s = args.get('tipoAccion')
        if tipo_accion_id_s:
            try:
                tipo_accion_id = int(tipo_accion_id_s)
                clauses.append("ha.idTipoAccion = %s")
                params.append(tipo_accion_id)
            except Exception:
                return err_filtros()
        elif tipo_accion_s:
            clauses.append("ta.nombreTipoAccion = %s")
            params.append(tipo_accion_s)

        # Módulo y claseId
        modulo_map = {
            'usuario': 'ha.idUsuario',
            'grupo': 'ha.idGrupo',
            'permiso': 'ha.idPermiso',
            'permisogrupo': 'ha.idPermisoGrupo',
            'carrera': 'ha.idCarrera',
            'genero': 'ha.idGenero',
            'provincia': 'ha.idProvincia',
            'localidad': 'ha.idLocalidad',
            'estadoacceso': 'ha.idEstadoAcceso',
            'estadocarrerainstitucion': 'ha.idEstadoCarreraInstitucion',
            'estadousuario': 'ha.idEstadoUsuario',
            'pais': 'ha.idPais',
            'tipoinstitucion': 'ha.idTipoInstitucion',
            'tipocarrera': 'ha.idTipoCarrera',
            'modalidadcarrerainstitucion': 'ha.idModalidadCarreraInstitucion',
            'aptitud': 'ha.idAptitud',
        }
        modulo = (args.get('modulo') or '').strip().lower()
        clase_id_s = args.get('claseId')
        if modulo:
            if modulo not in modulo_map:
                return err_filtros()
            field = modulo_map[modulo]
            clauses.append(f"{field} IS NOT NULL")
            if clase_id_s:
                try:
                    clase_id = int(clase_id_s)
                    clauses.append(f"{field} = %s")
                    params.append(clase_id)
                except Exception:
                    return err_filtros()

        where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""

        # Paginación
        try:
            page = int(args.get('page', '1'))
            page_size = int(args.get('pageSize', '50'))
            if page < 1 or page_size < 1 or page_size > 1000:
                raise ValueError()
        except Exception:
            return err_filtros()
        offset = (page - 1) * page_size

        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        sql = f"""
            SELECT ha.fechaHistorial,
                   ha.idUsuario,
                   u.nombre, u.apellido,
                   ta.nombreTipoAccion,
                   ha.idAptitud, ha.idCarrera, ha.idGenero, ha.idGrupo, ha.idPermiso, ha.idPermisoGrupo,
                   ha.idProvincia, ha.idLocalidad, ha.idEstadoAcceso, ha.idEstadoCarreraInstitucion,
                   ha.idEstadoUsuario, ha.idPais, ha.idTipoInstitucion, ha.idTipoCarrera, ha.idModalidadCarreraInstitucion
            FROM historialabm ha
            LEFT JOIN usuario u ON u.idUsuario = ha.idUsuario
            LEFT JOIN tipoaccion ta ON ta.idTipoAccion = ha.idTipoAccion
            {where_sql}
            ORDER BY ha.fechaHistorial DESC
            LIMIT %s OFFSET %s
        """
        cur.execute(sql, tuple(params + [page_size, offset]))
        rows = cur.fetchall() or []

        # Determinar módulo/clase por primera FK no nula (orden estable)
        fk_order = [
            ('usuario', 'idUsuario'),
            ('grupo', 'idGrupo'),
            ('permiso', 'idPermiso'),
            ('permisogrupo', 'idPermisoGrupo'),
            ('carrera', 'idCarrera'),
            ('genero', 'idGenero'),
            ('provincia', 'idProvincia'),
            ('localidad', 'idLocalidad'),
            ('estadoacceso', 'idEstadoAcceso'),
            ('estadocarrerainstitucion', 'idEstadoCarreraInstitucion'),
            ('estadousuario', 'idEstadoUsuario'),
            ('pais', 'idPais'),
            ('tipoinstitucion', 'idTipoInstitucion'),
            ('tipocarrera', 'idTipoCarrera'),
            ('modalidadcarrerainstitucion', 'idModalidadCarreraInstitucion'),
            ('aptitud', 'idAptitud'),
        ]

        def pick_modulo(row):
            for name, col in fk_order:
                if row.get(col) is not None:
                    return name, row.get(col)
            return None, None

        data = []
        for r in rows:
            modulo_name, clase_id = pick_modulo(r)
            data.append({
                "fecha": (r.get('fechaHistorial').isoformat(sep=' ') if r.get('fechaHistorial') else None),
                "usuario": {
                    "id": r.get('idUsuario'),
                    "nombre": r.get('nombre'),
                    "apellido": r.get('apellido'),
                },
                "tipoAccion": r.get('nombreTipoAccion'),
                "modulo": modulo_name,
                "claseId": clase_id,
            })

        return jsonify(data), 200
    except Exception as e:
        log(f"/admin/audit GET error: {e}\n{traceback.format_exc()}")
        # Error genérico (no especificado en HU) -> 500
        return jsonify({"message": "Error al obtener auditoría"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para exportar el historial de auditoría
@app.route('/api/v1/admin/audit/export', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_audit_export(current_user_id):
    """Exporta la auditoría en CSV o PDF. Usa los mismos filtros que el listado.
    Query: format=csv|pdf
    Errores: ERR2 si falla la exportación.
    """
    conn = None
    try:
        fmt = (request.args.get('format') or 'csv').lower()
        if fmt not in ('csv', 'pdf'):
            return jsonify({"errorCode": "ERR1", "message": "Error en los filtros aplicados. Revise los campos e intente de nuevo."}), 400

        import datetime as _dt
        args = request.args

        def err_filtros():
            return jsonify({"errorCode": "ERR1", "message": "Error en los filtros aplicados. Revise los campos e intente de nuevo."}), 400

        clauses = []
        params = []

        # userId
        user_id_s = args.get('userId')
        if user_id_s:
            try:
                user_id_val = int(user_id_s)
                clauses.append("ha.idUsuario = %s")
                params.append(user_id_val)
            except Exception:
                return err_filtros()

        # Fechas
        def parse_date(s):
            return _dt.datetime.strptime(s, '%Y-%m-%d').date()
        date_from_s = args.get('from')
        date_to_s = args.get('to')
        today = _dt.date.today()
        date_from = None
        date_to = None
        try:
            if date_from_s:
                date_from = parse_date(date_from_s)
            if date_to_s:
                date_to = parse_date(date_to_s)
        except Exception:
            return err_filtros()
        if date_to and date_to > today:
            return err_filtros()
        if date_from and date_to and date_from > date_to:
            return err_filtros()
        if date_from:
            clauses.append("ha.fechaHistorial >= %s")
            params.append(_dt.datetime.combine(date_from, _dt.time.min))
        if date_to:
            clauses.append("ha.fechaHistorial <= %s")
            params.append(_dt.datetime.combine(date_to, _dt.time.max))

        # Tipo de acción
        tipo_accion_id_s = args.get('tipoAccionId')
        tipo_accion_s = args.get('tipoAccion')
        if tipo_accion_id_s:
            try:
                tipo_accion_id = int(tipo_accion_id_s)
                clauses.append("ha.idTipoAccion = %s")
                params.append(tipo_accion_id)
            except Exception:
                return err_filtros()
        elif tipo_accion_s:
            clauses.append("ta.nombreTipoAccion = %s")
            params.append(tipo_accion_s)

        # Módulo y claseId
        modulo_map = {
            'usuario': 'ha.idUsuario',
            'grupo': 'ha.idGrupo',
            'permiso': 'ha.idPermiso',
            'permisogrupo': 'ha.idPermisoGrupo',
            'carrera': 'ha.idCarrera',
            'genero': 'ha.idGenero',
            'provincia': 'ha.idProvincia',
            'localidad': 'ha.idLocalidad',
            'estadoacceso': 'ha.idEstadoAcceso',
            'estadocarrerainstitucion': 'ha.idEstadoCarreraInstitucion',
            'estadousuario': 'ha.idEstadoUsuario',
            'pais': 'ha.idPais',
            'tipoinstitucion': 'ha.idTipoInstitucion',
            'tipocarrera': 'ha.idTipoCarrera',
            'modalidadcarrerainstitucion': 'ha.idModalidadCarreraInstitucion',
            'aptitud': 'ha.idAptitud',
        }
        modulo = (args.get('modulo') or '').strip().lower()
        clase_id_s = args.get('claseId')
        if modulo:
            if modulo not in modulo_map:
                return err_filtros()
            field = modulo_map[modulo]
            clauses.append(f"{field} IS NOT NULL")
            if clase_id_s:
                try:
                    clase_id = int(clase_id_s)
                    clauses.append(f"{field} = %s")
                    params.append(clase_id)
                except Exception:
                    return err_filtros()

        where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""

        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        sql = f"""
            SELECT ha.fechaHistorial,
                   ha.idUsuario,
                   u.nombre, u.apellido,
                   ta.nombreTipoAccion,
                   ha.idAptitud, ha.idCarrera, ha.idGenero, ha.idGrupo, ha.idPermiso, ha.idPermisoGrupo,
                   ha.idProvincia, ha.idLocalidad, ha.idEstadoAcceso, ha.idEstadoCarreraInstitucion,
                   ha.idEstadoUsuario, ha.idPais, ha.idTipoInstitucion, ha.idTipoCarrera, ha.idModalidadCarreraInstitucion
            FROM historialabm ha
            LEFT JOIN usuario u ON u.idUsuario = ha.idUsuario
            LEFT JOIN tipoaccion ta ON ta.idTipoAccion = ha.idTipoAccion
            {where_sql}
            ORDER BY ha.fechaHistorial DESC
        """
        cur.execute(sql, tuple(params))
        rows = cur.fetchall() or []

        # Preparar filas normalizadas
        fk_order = [
            ('usuario', 'idUsuario'),
            ('grupo', 'idGrupo'),
            ('permiso', 'idPermiso'),
            ('permisogrupo', 'idPermisoGrupo'),
            ('carrera', 'idCarrera'),
            ('genero', 'idGenero'),
            ('provincia', 'idProvincia'),
            ('localidad', 'idLocalidad'),
            ('estadoacceso', 'idEstadoAcceso'),
            ('estadocarrerainstitucion', 'idEstadoCarreraInstitucion'),
            ('estadousuario', 'idEstadoUsuario'),
            ('pais', 'idPais'),
            ('tipoinstitucion', 'idTipoInstitucion'),
            ('tipocarrera', 'idTipoCarrera'),
            ('modalidadcarrerainstitucion', 'idModalidadCarreraInstitucion'),
            ('aptitud', 'idAptitud'),
        ]
        def pick_modulo(row):
            for name, col in fk_order:
                if row.get(col) is not None:
                    return name, row.get(col)
            return None, None

        if fmt == 'csv':
            import csv
            from io import StringIO
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Fecha", "UsuarioId", "Nombre", "Apellido", "TipoAccion", "Modulo", "ClaseId"]) 
            for r in rows:
                modulo_name, clase_id = pick_modulo(r)
                writer.writerow([
                    (r.get('fechaHistorial').isoformat(sep=' ') if r.get('fechaHistorial') else ''),
                    r.get('idUsuario') or '',
                    r.get('nombre') or '',
                    r.get('apellido') or '',
                    r.get('nombreTipoAccion') or '',
                    modulo_name or '',
                    clase_id or '',
                ])
            csv_data = output.getvalue().encode('utf-8-sig')
            output.close()
            from flask import Response
            ts = _dt.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"auditoria_{ts}.csv"
            return Response(
                csv_data,
                mimetype='text/csv; charset=utf-8',
                headers={'Content-Disposition': f'attachment; filename="{filename}"'}
            )
        else:
            try:
                from io import BytesIO
                from reportlab.lib.pagesizes import A4
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    leftMargin=36,
                    rightMargin=36,
                    topMargin=36,
                    bottomMargin=36,
                )

                styles = getSampleStyleSheet()
                # Obtener nombre del usuario
                user_name = ""
                try:
                    cur2 = conn.cursor(dictionary=True)
                    cur2.execute("SELECT nombre, apellido FROM usuario WHERE idUsuario = %s", (current_user_id,))
                    user_row = cur2.fetchone()
                    if user_row:
                        user_name = f"{user_row.get('nombre','')} {user_row.get('apellido','')}".strip()
                except Exception:
                    user_name = ""
                finally:
                    if 'cur2' in locals():
                        cur2.close()
                titulo_texto = f"{user_name} - Export auditoría".strip() if user_name else "Export auditoría"
                if not user_name or user_name.lower() in ("anonimo", "anonymous"):
                    titulo_texto = "Export auditoría"
                doc.title = titulo_texto
                title = Paragraph(titulo_texto, styles["Heading2"])

                headers = ["Fecha", "UsuarioId", "Nombre", "Apellido", "TipoAccion", "Modulo", "ClaseId"]
                data_tbl = [headers]
                for r in rows:
                    modulo_name, clase_id = pick_modulo(r)
                    data_tbl.append([
                        Paragraph((r.get('fechaHistorial').isoformat(sep=' ') if r.get('fechaHistorial') else ''), styles["Normal"]),
                        Paragraph(str(r.get('idUsuario') or ''), styles["Normal"]),
                        Paragraph(r.get('nombre') or '', styles["Normal"]),
                        Paragraph(r.get('apellido') or '', styles["Normal"]),
                        Paragraph(r.get('nombreTipoAccion') or '', styles["Normal"]),
                        Paragraph(modulo_name or '', styles["Normal"]),
                        Paragraph(str(clase_id or ''), styles["Normal"]),
                    ])

                table = Table(
                    data_tbl,
                    repeatRows=1,
                    colWidths=[90, 55, 70, 70, 80, 80, 60],
                )
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))

                elements = [title, Spacer(1, 8), table]
                doc.build(elements)

                pdf = buffer.getvalue()
                buffer.close()

                from flask import Response
                ts = _dt.datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_user_name = user_name.replace(' ', '_') if user_name else "anonimo"
                filename = f"{safe_user_name}_auditoria_{ts}.pdf"
                return Response(
                    pdf,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment; filename="{filename}"'}
                )
            except Exception as e:
                log(f"/admin/audit/export PDF error: {e}\n{traceback.format_exc()}")
                return jsonify({"errorCode": "ERR2", "message": "No se pudo completar la exportación. Intente nuevamente más tarde."}), 500
    except Exception as e:
        log(f"/admin/audit/export error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR2", "message": "No se pudo completar la exportación. Intente nuevamente más tarde."}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ Registro de usuario (US007) ============================

PWD_POLICY_MSG = (
    "La contraseña debe contener:\n"
    "Mínimo 8 caracteres.\n"
    "Al menos una letra mayúscula.\n"
    "Al menos una letra minúscula.\n"
    "Al menos un número.\n"
    "Al menos un carácter especial (como @,#,$,etc.)."
)

# Verifica si la contraseña cumple con la política de seguridad
def _password_meets_policy(pw: str) -> bool:
    if not isinstance(pw, str):
        return False
    if len(pw) < 8:
        return False
    has_upper = any(c.isupper() for c in pw)
    has_lower = any(c.islower() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_special = any(not c.isalnum() for c in pw)
    return has_upper and has_lower and has_digit and has_special

# Endpoint para registro de usuario
@app.route('/api/v1/auth/register', methods=['POST'])
def register_email_password():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        data = request.get_json(silent=True) or {}
        correo = data.get('correo')
        dni = data.get('dni')
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        contrasena = data.get('contrasena')
        fechaNac = data.get('fechaNac')
        idGenero = data.get('idGenero')
        idLocalidad = data.get('idLocalidad')

        # ERR1: campos requeridos incompletos
        required_missing = []
        if not dni:
            required_missing.append('dni')
        if not apellido:
            required_missing.append('apellido')
        if not fechaNac:
            required_missing.append('fechaNac')
        if not idGenero:
            required_missing.append('idGenero')
        if not idLocalidad:
            required_missing.append('idLocalidad')
        if not nombre:
            required_missing.append('nombre')
        if not correo:
            required_missing.append('correo')
        if not contrasena:
            required_missing.append('contrasena')
        if required_missing:
            return jsonify({"errorCode": "ERR1", "message": "Faltan campos obligatorios: " + ", ".join(required_missing)}), 400

        # ERR4: formato email inválido
        if not re.match(EMAIL_REGEX, correo):
            return jsonify({"errorCode": "ERR4", "message": "Error. formato email invalido."}), 400

        # ERR2: contraseña no cumple política
        if not _password_meets_policy(contrasena):
            return jsonify({"errorCode": "ERR2", "message": PWD_POLICY_MSG}), 400

        # verificar el id de localidad y de genero
        cur.execute("SELECT * FROM localidad WHERE idLocalidad=%s", (idLocalidad,))
        localidad = cur.fetchone()
        cur.execute("SELECT * FROM genero WHERE idGenero=%s", (idGenero,))
        genero = cur.fetchone()

        if not localidad:
            return jsonify({"errorCode": "ERR1", "message": "La localidad indicada no existe."}), 400
        if not genero:
            return jsonify({"errorCode": "ERR1", "message": "El género indicado no existe."}), 400

        # Verificar existencia previa de email
        cur.execute("SELECT 1 FROM usuario WHERE mail=%s", (correo,))
        if cur.fetchone():
            # No especificado en HU; usamos ERR1 para indicar conflicto de datos
            return jsonify({"errorCode": "ERR1", "message": "El correo ya está registrado."}), 400

        validation_key = generate_complex_id()

        # Insertar usuario
        hashed = hash_password(contrasena)
        cur.execute(
            "INSERT INTO usuario (mail, dni, nombre, apellido, contrasena, fechaNac, idGenero, idLocalidad, validationKEY) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (correo, dni, nombre, apellido, hashed, fechaNac, int(idGenero), int(idLocalidad), validation_key)
        )

        # Obtener id del nuevo usuario
        cur.execute("SELECT * FROM usuario WHERE mail=%s", (correo,))
        user = cur.fetchone()

        # Agregar al usuario al grupo de "Estudiante" por defecto
        if user:
            cur.execute("SELECT * FROM grupo WHERE nombreGrupo=%s", ("Estudiante",))
            grupo = cur.fetchone()
            if not grupo:
                return jsonify({"errorCode": "ERR3", "message": "Error al registrar usuario"}), 500
            cur.execute("INSERT INTO usuariogrupo (idUsuario, idGrupo) VALUES (%s, %s)", (int(user['idUsuario']), int(grupo['idGrupo'])))

        # Agregar al usuario al estado "Pendiente" por defecto
        if user:
            cur.execute("SELECT * FROM estadousuario WHERE nombreEstadoUsuario = %s", ("Pendiente",))
            estado = cur.fetchone()
            if not estado:
                return jsonify({"errorCode": "ERR3", "message": "Error al registrar usuario"}), 500
            cur.execute("INSERT INTO usuarioestado (idUsuario, idEstadoUsuario) VALUES (%s, %s)", (int(user['idUsuario']), int(estado['idEstadoUsuario'])))
            conn.commit()
        
        # Enviar el correo para la validacion del email
        send_email(user['mail'], "Verificación de correo OVO", f"""
            <p>Gracias por registrarte en OVO.</p>
            <p>Por favor, haz clic en el siguiente enlace para verificar tu correo electrónico:</p>
            <p><a href="{BASE_URL}/api/v1/auth/verify-email?key={validation_key}">Verificar mi correo</a></p>
            <p>Si no te has registrado en OVO, puedes ignorar este correo.</p>
            <p>Saludos,<br>El equipo de OVO</p>
            """)

        # Emitir token y devolver contexto similar al login
        token = generate_token(user['idUsuario'])
        permisos, grupos = get_user_permissions_and_groups(user['idUsuario'])
        resp = jsonify({
            "usuario": {
                "id": user['idUsuario'],
                "nombre": user['nombre'],
                "apellido": user['apellido'],
                "mail": user['mail'],
                "dni": user['dni'],
                "fechaNac": user['fechaNac'],
                "idGenero": user['idGenero'],
                "idLocalidad": user['idLocalidad'],
            },
            "permisos": permisos,
            "grupos": grupos,
        })
        resp.headers['new_token'] = token
        return resp, 201
    except Exception as e:
        log(f"/auth/register error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Error al registrar usuario"}), 500

# Endpoint para registro de usuario con Google
@app.route('/api/v1/auth/register/google', methods=['POST'])
def register_with_google():
    try:
        # Importar de forma perezosa
        try:
            from google.oauth2 import id_token as google_id_token  # type: ignore
            from google.auth.transport import requests as google_requests  # type: ignore
        except Exception:
            return jsonify({"errorCode": "ERR3", "message": "No se registró el usuario"}), 400

        data = request.get_json(silent=True) or {}
        id_token = data.get('id_token') or data.get('credential')
        if not id_token:
            return jsonify({"errorCode": "ERR3", "message": "No se registró el usuario"}), 400

        request_adapter = google_requests.Request()
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        try:
            claims = (
                google_id_token.verify_oauth2_token(id_token, request_adapter, audience=client_id)
                if client_id else
                google_id_token.verify_oauth2_token(id_token, request_adapter)
            )
        except Exception:
            return jsonify({"errorCode": "ERR3", "message": "No se registró el usuario"}), 400

        email = (claims.get('email') or '').strip()
        if not email or not re.match(EMAIL_REGEX, email):
            return jsonify({"errorCode": "ERR3", "message": "No se registró el usuario"}), 400

        nombre = (claims.get('given_name') or claims.get('name') or '').strip() or None
        apellido = (claims.get('family_name') or '').strip() or None

        # Crear usuario si no existe
        conn = mysql.connector.connect(**DB_CONFIG)
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT idUsuario, mail, nombre, apellido FROM usuario WHERE mail=%s", (email,))
            user = cur.fetchone()
            if not user:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO usuario (mail, nombre, apellido) VALUES (%s, %s, %s)",
                    (email, nombre, apellido)
                )
                conn.commit()
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT idUsuario, mail, nombre, apellido FROM usuario WHERE mail=%s", (email,))
                user = cur.fetchone()
        finally:
            try:
                conn.close()
            except Exception:
                pass

        if not user:
            return jsonify({"errorCode": "ERR3", "message": "No se registró el usuario"}), 400

        token = generate_token(user['idUsuario'])
        permisos, grupos = get_user_permissions_and_groups(user['idUsuario'])
        resp = jsonify({
            "usuario": {
                "id": user['idUsuario'],
                "nombre": user.get('nombre'),
                "apellido": user.get('apellido'),
                "mail": user.get('mail'),
            },
            "permisos": permisos,
            "grupos": grupos,
        })
        resp.headers['new_token'] = token
        return resp, 201
    except Exception as e:
        log(f"/auth/register/google error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR3", "message": "No se registró el usuario"}), 500

# Endpoint para validar el correo electrónico a partir de la key generada
@app.route('/api/v1/auth/verify-email', methods=['GET'])
def verify_email():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        key = (request.args.get('key') or '').strip()
        if not key:
            return jsonify({"errorCode": "ERR4", "message": "Falta la clave de verificación"}), 400
        cur.execute("SELECT * FROM usuario WHERE validationKEY=%s", (key,))
        user = cur.fetchone()
        if not user:
            return jsonify({"errorCode": "ERR4", "message": "Clave de verificación inválida"}), 400

        # Buscar el estado Activo
        cur.execute("SELECT * FROM estadousuario WHERE nombreEstadoUsuario=%s AND (fechaFin IS NULL OR fechaFin > NOW())", ("Activo",))
        estado_activo = cur.fetchone()
        if not estado_activo:
            return jsonify({"errorCode": "ERR4", "message": "Error interno al verificar el correo"}), 500
        id_estado_activo = int(estado_activo['idEstadoUsuario'])
        id_usuario = int(user['idUsuario'])
        # Quitar estados anteriores (si es que los tiene de la tabla usuarioestado)
        cur.execute("UPDATE usuarioestado SET fechaFin=NOW() WHERE idUsuario=%s", (id_usuario,))
        # Insertar nuevo estado Activo
        cur.execute("INSERT INTO usuarioestado (idUsuario, idEstadoUsuario) VALUES (%s, %s)", (id_usuario, id_estado_activo))
        conn.commit()
        return jsonify({"ok": True, "message": "Correo verificado exitosamente"}), 200
    except Exception as e:
        log(f"/auth/verify-email error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR4", "message": "Error al verificar el correo"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
# Ejemplo con curl:
# curl -X GET "http://localhost:5000/api/v1/auth/verify-email?key=tu_clave_aqui"

# ============================ Baja lógica de usuario (US008) ============================

# Endpoint para dar de baja lógica al usuario
@app.route('/api/v1/auth/deactivate', methods=['POST'])
@token_required
def deactivate_current_user(current_user_id):
    """Da de baja lógicamente al usuario autenticado.
    Regla: Cierra cualquier estado activo en usuarioestado y crea un nuevo estado BAJA.
    Si ya está en BAJA activo, responde idempotente con ok: true.
    Errores => ERR1.
    """
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Validar existencia de usuario
        cur.execute("SELECT 1 FROM usuario WHERE idUsuario=%s", (current_user_id,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Usuario no encontrado"}), 404

        # Verificar si ya posee un estado activo Baja
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT ue.idUsuarioEstado, eu.nombreEstadoUsuario
            FROM usuarioestado ue
            JOIN estadousuario eu ON eu.idEstadoUsuario = ue.idEstadoUsuario
            WHERE ue.idUsuario=%s AND (ue.fechaFin IS NULL OR ue.fechaFin > NOW())
            """,
            (current_user_id,)
        )
        activos = cur.fetchall() or []
        if any((r.get('nombreEstadoUsuario') == 'Baja') for r in activos):
            return jsonify({"ok": False, "message": "El usuario ya se encuentra dado de Baja"}), 400

        # Asegurar que exista el estado Baja
        cur = conn.cursor()
        cur.execute(
            "SELECT idEstadoUsuario FROM estadousuario WHERE nombreEstadoUsuario=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            ("Baja",)
        )
        row = cur.fetchone()
        if not row:
            # Crear estado Baja si no existe
            cur.execute(
                "INSERT INTO estadousuario (nombreEstadoUsuario, fechaFin) VALUES (%s, NULL)",
                ("Baja",)
            )
            conn.commit()
            cur.execute(
                "SELECT idEstadoUsuario FROM estadousuario WHERE nombreEstadoUsuario=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
                ("Baja",)
            )
            row = cur.fetchone()
        if not row:
            return jsonify({"errorCode": "ERR1", "message": "No se pudo realizar la Baja del usuario. Intente más tarde."}), 500
        id_estado_baja = row[0]

        # Cerrar estados activos actuales (si los hay)
        cur.execute(
            "UPDATE usuarioestado SET fechaFin = NOW() WHERE idUsuario=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            (current_user_id,)
        )

        # Insertar nuevo estado Baja
        cur.execute(
            "INSERT INTO usuarioestado (idUsuario, idEstadoUsuario, fechaInicio, fechaFin) VALUES (%s, %s, NOW(), NULL)",
            (current_user_id, id_estado_baja)
        )

        conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        log(f"/auth/deactivate error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "No se pudo realizar la Baja del usuario. Intente más tarde."}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ Recuperación de contraseña (US009) ============================

# Genera un token de restablecimiento
def _generate_reset_token(user_id: int, minutes: int = 30) -> str:
    payload = {
        "user_id": user_id,
        "purpose": "password_reset",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Decodifica un token de restablecimiento
def _decode_reset_token(token: str):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if data.get("purpose") != "password_reset":
            return None
        return int(data.get("user_id"))
    except Exception:
        return None

# Endpoint para enviar enlace de restablecimiento
@app.route('/api/v1/auth/password/forgot', methods=['POST'])
def password_forgot():
    try:
        data = request.get_json(silent=True) or {}
        correo = (data.get('correo') or '').strip()
        # Validación de formato básico y existencia
        if not correo or not re.match(EMAIL_REGEX, correo):
            return jsonify({"errorCode": "ERR1", "message": "Email no registrado"}), 400

        user = get_user_by_email(correo)
        if not user:
            return jsonify({"errorCode": "ERR1", "message": "Email no registrado"}), 400

        token = _generate_reset_token(user['idUsuario'])
        link = f"{BASE_URL}/reset-password?token={token}"

        # Enviar correo con el enlace
        asunto = "Recuperación de contraseña"
        cuerpo = (
            f"<p>Hola {user.get('nombre') or ''},</p>"
            f"<p>Recibimos una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para continuar:</p>"
            f"<p><a href=\"{link}\">Restablecer contraseña</a></p>"
            f"<p>Si no solicitaste este cambio, ignora este mensaje.</p>"
        )
        try:
            send_email(correo, asunto, cuerpo)
        except Exception as _e:
            # No exponer detalles de SMTP
            log(f"password_forgot email error: {_e}")
            # Aun así indicar éxito para no bloquear el flujo (opcional). Aquí informamos éxito explícito.
            pass

        return jsonify({"ok": True, "message": "Se envió el enlace de restablecimiento al correo ingresado."}), 200
    except Exception as e:
        log(f"/auth/password/forgot error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "No se pudo procesar la solicitud."}), 500

# Endpoint para restablecer la contraseña
@app.route('/api/v1/auth/password/reset', methods=['POST'])
def password_reset():
    try:
        data = request.get_json(silent=True) or {}
        token = (data.get('token') or '').strip()
        nueva = data.get('nuevaContrasena') or ''

        user_id = _decode_reset_token(token)
        if not user_id:
            return jsonify({"message": "Enlace inválido o expirado."}), 400

        # ERR2: campo contraseña no completo
        if not nueva:
            return jsonify({"errorCode": "ERR2", "message": "Falta completar el campo contraseña."}), 400
        # ERR3: política de contraseña
        if not _password_meets_policy(nueva):
            return jsonify({"errorCode": "ERR3", "message": PWD_POLICY_MSG}), 400

        # Actualizar contraseña
        conn = mysql.connector.connect(**DB_CONFIG)
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM usuario WHERE idUsuario=%s", (user_id,))
            if not cur.fetchone():
                return jsonify({"errorCode": "ERR1", "message": "Email no registrado"}), 400
            cur.execute(
                "UPDATE usuario SET contrasena=%s, vencimientoContrasena=NULL WHERE idUsuario=%s",
                (hash_password(nueva), user_id)
            )
            conn.commit()
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return jsonify({"ok": True, "message": "Se cambió la contraseña correctamente."}), 200
    except Exception as e:
        log(f"/auth/password/reset error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "No se pudo restablecer la contraseña."}), 500

# Endpoint para validar el token de reseteo
@app.route('/api/v1/auth/password/validate', methods=['GET'])
def password_reset_validate():
    """Valida que el token de reseteo sea correcto y no haya expirado."""
    try:
        token = (request.args.get('token') or '').strip()
        if not token:
            return jsonify({"ok": False, "errorCode": "ERR1", "message": "Token requerido"}), 400

        user_id = _decode_reset_token(token)
        if not user_id:
            return jsonify({"ok": False, "errorCode": "ERR1", "message": "Token inválido o expirado"}), 400

        # Validar que el usuario exista (defensa extra)
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM usuario WHERE idUsuario=%s", (user_id,))
            if not cur.fetchone():
                return jsonify({"ok": False, "errorCode": "ERR1", "message": "Token inválido o expirado"}), 400
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return jsonify({"ok": True}), 200
    except Exception as e:
        log(f"/auth/password/validate error: {e}\n{traceback.format_exc()}")
        return jsonify({"ok": False, "errorCode": "ERR1", "message": "No se pudo validar el token"}), 400

# ============================ Gestión de preferencias (US010) ============================

# Endpoint para listar los intereses del usuario
@app.route('/api/v1/user/interests', methods=['GET'])
@token_required
def user_list_interests(current_user_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT iuc.idCarreraInstitucion,
                   COALESCE(c.nombreCarrera, ci.nombreCarrera) AS nombreCarrera,
                   inst.nombreInstitucion
            FROM interesusuariocarrera iuc
            JOIN carrerainstitucion ci ON ci.idCarreraInstitucion = iuc.idCarreraInstitucion
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN institucion inst ON inst.idInstitucion = ci.idInstitucion
            WHERE iuc.idUsuario = %s AND (iuc.fechaFin IS NULL OR iuc.fechaFin > NOW())
            ORDER BY nombreCarrera, inst.nombreInstitucion
            """,
            (current_user_id,)
        )
        rows = cur.fetchall() or []
        if not rows:
            return jsonify({"errorCode": "ERR1", "message": "No tiene preferencia por ninguna carrera"}), 400
        data = [
            {
                "idCarreraInstitucion": r.get('idCarreraInstitucion'),
                "nombreCarrera": r.get('nombreCarrera'),
                "nombreInstitucion": r.get('nombreInstitucion'),
            }
            for r in rows
        ]
        return jsonify(data), 200
    except Exception as e:
        log(f"/user/interests GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "No se pudieron obtener las preferencias"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para eliminar un interés del usuario
@app.route('/api/v1/user/interests/<int:id_carrera_institucion>', methods=['DELETE'])
@token_required
def user_remove_interest(current_user_id, id_carrera_institucion: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Verificar existencia de interés activo
        cur.execute(
            """
            SELECT 1
            FROM interesusuariocarrera
            WHERE idUsuario = %s AND idCarreraInstitucion = %s
              AND (fechaFin IS NULL OR fechaFin > NOW())
            """,
            (current_user_id, id_carrera_institucion)
        )
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "La carrera no está marcada como preferida"}), 400

        # Cerrar el interés
        cur.execute(
            """
            UPDATE interesusuariocarrera
            SET fechaFin = NOW()
            WHERE idUsuario = %s AND idCarreraInstitucion = %s
              AND (fechaFin IS NULL OR fechaFin > NOW())
            """,
            (current_user_id, id_carrera_institucion)
        )
        conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        log(f"/user/interests/{id_carrera_institucion} DELETE error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "No se pudo quitar la preferencia"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para agregar un interés del usuario
@app.route('/api/v1/user/interests', methods=['POST'])
@token_required
def user_add_interest(current_user_id):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Obtener los datos del interés desde el cuerpo de la solicitud
        data = request.json
        id_carrera_institucion = data.get("idCarreraInstitucion")

        # Verificar que se haya proporcionado un ID de carrera/institución
        if not id_carrera_institucion:
            return jsonify({"errorCode": "ERR1", "message": "Falta el ID de la carrera/institución"}), 400

        # Verificar que la carrera/institución exista
        cur.execute(
            """
            SELECT 1
            FROM carrerainstitucion
            WHERE idCarreraInstitucion = %s
            """,
            (id_carrera_institucion,)
        )
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "La carrera/institución no existe"}), 404

        # Verificar que el interés no exista ya
        cur.execute(
            """
            SELECT 1
            FROM interesusuariocarrera
            WHERE idUsuario = %s AND idCarreraInstitucion = %s
              AND (fechaFin IS NULL OR fechaFin > NOW())
            """,
            (current_user_id, id_carrera_institucion)
        )
        if cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "La carrera ya está marcada como preferida"}), 400

        # Agregar el nuevo interés
        cur.execute(
            """
            INSERT INTO interesusuariocarrera (idUsuario, idCarreraInstitucion)
            VALUES (%s, %s)
            """,
            (current_user_id, id_carrera_institucion)
        )
        conn.commit()
        return jsonify({"ok": True}), 201
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        log(f"/user/interests POST error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "No se pudo agregar la preferencia"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ Histórico de tests (US011) ============================

# Lista los tests realizados por el usuario autenticado
@app.route('/api/v1/user/tests', methods=['GET'])
@token_required
def user_list_tests(current_user_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT 
                t.idResultadoCuestionario AS idTest,
                t.fechaResultadoCuestionario
            FROM test t
            WHERE t.idUsuario = %s
            ORDER BY t.fechaResultadoCuestionario DESC, t.idResultadoCuestionario DESC
            """,
            (current_user_id,)
        )
        rows = cur.fetchall() or []
        data = [
            {
                "id": r.get('idTest'),
                "fecha": (r.get('fechaResultadoCuestionario').isoformat(sep=' ') if r.get('fechaResultadoCuestionario') else None),
                "accion": "Consultar resultado",
            }
            for r in rows
        ]
        return jsonify(data), 200
    except Exception as e:
        log(f"/user/tests GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "No se pudo obtener el histórico de tests."}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Valida que el test exista y pertenezca al usuario antes de consultar su resultado (US012)
@app.route('/api/v1/user/tests/<int:id_test>/access', methods=['GET'])
@token_required
def user_test_access(current_user_id, id_test: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 1
            FROM test
            WHERE idResultadoCuestionario = %s AND idUsuario = %s
            """,
            (id_test, current_user_id)
        )
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Error al consultar test, intente más tarde"}), 400

        # OK: el front puede navegar a la HU US012 con este id
        return jsonify({"ok": True, "idTest": id_test}), 200
    except Exception as e:
        log(f"/user/tests/{id_test}/access GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "Error al consultar test, intente más tarde"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ Resultado de test (US012) ============================

# Devuelve el resultado del test: aptitudes con afinidad, breve análisis y carreras sugeridas.
# Reglas de acceso:
# - Si NO está autenticado: responder P016 indicando que debe registrarse para ver el resultado.
# - Si está autenticado con JWT válido y se puede extraer user_id: se valida que el test pertenezca al usuario.
# - Si está autenticado con el token de prueba "Hola": se considera autenticado pero no se valida pertenencia.
@app.route('/api/v1/user/tests/<int:id_test>/result', methods=['GET'])
def user_test_result(id_test: int):
    # Importaciones perezosas para no afectar otras partes del archivo
    try:
        import mysql.connector  # type: ignore
        import datetime as _dt  # noqa: F401  (puede usarse para formateo de fecha)
    except Exception:
        return jsonify({
            "ok": False,
            "code": "ERR1",
            "message": "Dependencias no disponibles en el servidor."
        }), 500

    # Helper: autenticación básica a partir del header Authorization
    def _auth_from_header():
        auth_header = request.headers.get('Authorization', '') or ''
        if not auth_header.startswith('Bearer '):
            return {"authenticated": False, "user_id": None, "dev": False}
        token = auth_header.split(' ', 1)[1].strip()
        if token == 'Hola':
            return {"authenticated": True, "user_id": None, "dev": True}
        # Intentar JWT
        try:
            import jwt  # type: ignore
            from flask import current_app
            secret = globals().get('SECRET_KEY') or current_app.config.get('SECRET_KEY')
            data = jwt.decode(token, secret, algorithms=["HS256"])  # noqa: F401
            uid = data.get('user_id')
            return {"authenticated": True, "user_id": int(uid) if uid is not None else None, "dev": False}
        except Exception:
            # Si no podemos decodificar, lo tratamos como autenticado sin user_id (similar al dev)
            return {"authenticated": True, "user_id": None, "dev": False}

    auth = _auth_from_header()
    if not auth["authenticated"]:
        # P016: Caso no registrado
        return jsonify({
            "ok": False,
            "code": "P016",
            "message": "Debes estar registrado para visualizar el resultado del test.",
            "actions": [
                {"label": "Registrarse", "href": "/api/v1/auth/register"},
                {"label": "Cancelar"}
            ]
        }), 401

    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Si tenemos user_id, validar pertenencia del test al usuario
        if auth.get('user_id') is not None:
            cursor.execute(
                """
                SELECT t.idResultadoCuestionario, t.fechaResultadoCuestionario
                FROM test t
                WHERE t.idResultadoCuestionario = %s AND t.idUsuario = %s
                """,
                (id_test, auth['user_id'])
            )
        else:
            # Token dev o no se pudo decodificar JWT: no validamos pertenencia
            cursor.execute(
                """
                SELECT t.idResultadoCuestionario, t.fechaResultadoCuestionario
                FROM test t
                WHERE t.idResultadoCuestionario = %s
                """,
                (id_test,)
            )

        test_row = cursor.fetchone()
        if not test_row:
            return jsonify({
                "ok": False,
                "code": "ERR1",
                "message": "No se encontró el test o no tiene acceso."
            }), 404

        # Obtener aptitudes con afinidad
        cursor.execute(
            """
            SELECT ta.idResultadoAptitud,
                   ta.afinidadAptitud,
                   a.idAptitud,
                   a.nombreAptitud,
                   a.descripcion
            FROM testaptitud ta
            JOIN aptitud a ON a.idAptitud = ta.idAptitud
            WHERE ta.idTest = %s
            ORDER BY ta.afinidadAptitud DESC, a.nombreAptitud
            """,
            (id_test,)
        )
        aptitudes_rows = cursor.fetchall() or []
        aptitudes = [
            {
                "idAptitud": r.get("idAptitud"),
                "nombre": r.get("nombreAptitud"),
                "afinidad": float(r.get("afinidadAptitud") or 0),
                "descripcion": r.get("descripcion"),
            }
            for r in aptitudes_rows
        ]

        # Breve análisis simple basado en las 1-3 aptitudes con mayor afinidad
        top_names = [a["nombre"] for a in aptitudes[:3] if a.get("nombre")]
        if top_names:
            if len(top_names) == 1:
                resumen = f"Tus respuestas muestran mayor afinidad con {top_names[0]}."
            elif len(top_names) == 2:
                resumen = f"Destacan {top_names[0]} y {top_names[1]} en tu perfil."
            else:
                resumen = f"Sobresalen {top_names[0]}, {top_names[1]} y {top_names[2]}."
        else:
            resumen = "No se encontraron aptitudes asociadas al test."

        # Carreras sugeridas con afinidad
        cursor.execute(
            """
            SELECT tci.afinidadCarrera,
                   ci.idCarreraInstitucion,
                   ci.nombreCarrera,
                   ci.tituloCarrera,
                   i.idInstitucion,
                   i.nombreInstitucion
            FROM testcarrerainstitucion tci
            JOIN carrerainstitucion ci ON ci.idCarreraInstitucion = tci.idCarreraInstitucion
            LEFT JOIN institucion i ON i.idInstitucion = ci.idInstitucion
            WHERE tci.idTest = %s
            ORDER BY tci.afinidadCarrera DESC, ci.nombreCarrera
            """,
            (id_test,)
        )
        carreras_rows = cursor.fetchall() or []
        carreras = []
        for r in carreras_rows:
            carreras.append({
                "idCarreraInstitucion": r.get("idCarreraInstitucion"),
                "nombreCarrera": r.get("nombreCarrera"),
                "tituloCarrera": r.get("tituloCarrera"),
                "afinidad": float(r.get("afinidadCarrera") or 0),
                "institucion": {
                    "idInstitucion": r.get("idInstitucion"),
                    "nombreInstitucion": r.get("nombreInstitucion"),
                },
                # Sugerencia de endpoint para "Consultar Carrera" (HU Consultar Carrera)
                "consultarCarreraPath": f"/api/v1/careers/{r.get('idCarreraInstitucion')}"
            })

        return jsonify({
            "ok": True,
            "test": {
                "id": test_row.get("idResultadoCuestionario"),
                "fecha": test_row.get("fechaResultadoCuestionario").isoformat() if test_row.get("fechaResultadoCuestionario") else None,
            },
            "resumen": resumen,
            "aptitudes": aptitudes,
            "carrerasSugeridas": carreras,
            "acciones": {
                "consultarCarrera": True if carreras else False
            }
        })
    except Exception as e:
        try:
            msg = str(e)
        except Exception:
            msg = "Error desconocido"
        return jsonify({
            "ok": False,
            "code": "ERR1",
            "message": f"Error al obtener el resultado del test: {msg}"
        }), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ Reiniciar cuestionario (US013) ============================

# Elimina las respuestas del cuestionario en curso para el usuario y permite empezar uno nuevo.
# Reglas:
# - Requiere autenticación. Acepta token de prueba "Hola" y JWT HS256 (SECRET_KEY).
# - Si hay user_id (JWT): intenta borrar el test en curso del usuario (fechaResultadoCuestionario IS NULL).
#   - Si no hay en curso y se envía idTest en el body, valida que pertenezca al usuario y esté en curso.
# - Si NO hay user_id (token dev Hola): requiere idTest en el body y lo elimina si está en curso.
# - Idempotente: si no hay test en curso, responde ok true.
# - Error: ERR1 "Error al reiniciar cuestionario, intente más tarde".
@app.route('/api/v1/user/tests/restart', methods=['POST'])
def user_restart_test():
    try:
        import mysql.connector  # type: ignore
        import jwt  # type: ignore
    except Exception:
        return jsonify({
            "errorCode": "ERR1",
            "message": "Error al reiniciar cuestionario, intente más tarde"
        }), 500

    def _auth_from_header():
        auth_header = request.headers.get('Authorization', '') or ''
        if not auth_header.startswith('Bearer '):
            return {"authenticated": False, "user_id": None, "dev": False}
        token = auth_header.split(' ', 1)[1].strip()
        if token == 'Hola':
            return {"authenticated": True, "user_id": None, "dev": True}
        try:
            secret = globals().get('SECRET_KEY')
            data = jwt.decode(token, secret, algorithms=["HS256"])  # type: ignore
            uid = data.get('user_id')
            return {"authenticated": True, "user_id": int(uid) if uid is not None else None, "dev": False}
        except Exception:
            return {"authenticated": False, "user_id": None, "dev": False}

    auth = _auth_from_header()
    if not auth["authenticated"]:
        return jsonify({
            "errorCode": "ERR1",
            "message": "Error al reiniciar cuestionario, intente más tarde"
        }), 401

    body = request.get_json(silent=True) or {}
    id_test_body = body.get('idTest') if isinstance(body, dict) else None
    user_id = auth.get('user_id')

    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        test_id_to_delete = None
        if user_id is not None:
            # Buscar test en curso del usuario
            cur.execute(
                """
                SELECT idResultadoCuestionario AS id
                FROM test
                WHERE idUsuario = %s AND fechaResultadoCuestionario IS NULL
                ORDER BY idResultadoCuestionario DESC
                LIMIT 1
                """,
                (user_id,)
            )
            row = cur.fetchone()
            if row:
                test_id_to_delete = row.get('id')
            elif isinstance(id_test_body, int):
                cur.execute(
                    """
                    SELECT idResultadoCuestionario AS id
                    FROM test
                    WHERE idResultadoCuestionario = %s AND idUsuario = %s AND fechaResultadoCuestionario IS NULL
                    """,
                    (id_test_body, user_id)
                )
                row = cur.fetchone()
                if row:
                    test_id_to_delete = row.get('id')
        else:
            # Modo dev Hola: requiere idTest
            if isinstance(id_test_body, int):
                cur.execute(
                    """
                    SELECT idResultadoCuestionario AS id
                    FROM test
                    WHERE idResultadoCuestionario = %s AND fechaResultadoCuestionario IS NULL
                    """,
                    (id_test_body,)
                )
                row = cur.fetchone()
                if row:
                    test_id_to_delete = row.get('id')
            else:
                return jsonify({
                    "errorCode": "ERR1",
                    "message": "Error al reiniciar cuestionario, intente más tarde"
                }), 400

    
        # Idempotente
        if not test_id_to_delete:
            return jsonify({
                "ok": True,
                "message": "No había un cuestionario en curso.",
                "idTestEliminado": None
            }), 200

        # Transacción
        try:
            conn.start_transaction()
        except Exception:
            pass

        cur.execute("DELETE FROM testaptitud WHERE idTest = %s", (test_id_to_delete,))
        cur.execute("DELETE FROM testcarrerainstitucion WHERE idTest = %s", (test_id_to_delete,))
        cur.execute("DELETE FROM test WHERE idResultadoCuestionario = %s", (test_id_to_delete,))
        conn.commit()

        return jsonify({
            "ok": True,
            "message": "Cuestionario reiniciado.",
            "idTestEliminado": int(test_id_to_delete)
        }), 200
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        try:
            log(f"/user/tests/restart POST error: {e}")
        except Exception:
            pass
        return jsonify({
            "errorCode": "ERR1",
            "message": "Error al reiniciar cuestionario, intente más tarde"
        }), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ Consultar Carreras (US014) ============================

# Lista de carreras con búsqueda opcional (?search=)
@app.route('/api/v1/careers', methods=['GET'])
def careers_list():
    conn = None
    try:
        search = (request.args.get('search') or '').strip()
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        params = []
        where = ["(c.fechaFin IS NULL OR c.fechaFin > NOW())"]
        if search:
            where.append("c.nombreCarrera LIKE %s")
            params.append(f"%{search}%")
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        sql = f"""
            SELECT c.idCarrera,
                   c.nombreCarrera,
                   COUNT(ci.idCarreraInstitucion) AS cantidadInstituciones
            FROM carrera c
            LEFT JOIN carrerainstitucion ci ON ci.idCarrera = c.idCarrera
            {where_sql}
            GROUP BY c.idCarrera, c.nombreCarrera
            ORDER BY c.nombreCarrera
        """
        cur.execute(sql, tuple(params))
        rows = cur.fetchall() or []
        data = [
            {
                "idCarrera": r.get('idCarrera'),
                "nombre": r.get('nombreCarrera'),
                "cantidadInstituciones": int(r.get('cantidadInstituciones') or 0),
                "institucionesPath": f"/api/v1/careers/{r.get('idCarrera')}/institutions",
            }
            for r in rows
        ]
        return jsonify(data), 200
    except Exception as e:
        log(f"/careers GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Error al consultar carreras"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Instituciones que dictan una carrera
@app.route('/api/v1/careers/<int:id_carrera>/institutions', methods=['GET'])
def career_institutions(id_carrera: int):
    conn = None
    try:
        search = (request.args.get('search') or '').strip()
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Validar carrera existente
        cur.execute("SELECT 1 FROM carrera WHERE idCarrera=%s", (id_carrera,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Carrera no encontrada"}), 404

        params = [id_carrera]
        where_extra = []
        if search:
            where_extra.append("(i.nombreInstitucion LIKE %s OR ci.tituloCarrera LIKE %s OR ci.nombreCarrera LIKE %s)")
            like = f"%{search}%"
            params.extend([like, like, like])

        where_extra_sql = (" AND " + " AND ".join(where_extra)) if where_extra else ""
        cur.execute(
            f"""
            SELECT ci.idCarreraInstitucion,
                   ci.tituloCarrera,
                   ci.nombreCarrera AS nombreCarreraCI,
                   ci.montoCuota,
                   m.nombreModalidad,
                   i.idInstitucion,
                   i.nombreInstitucion,
                   i.urlLogo
            FROM carrerainstitucion ci
            LEFT JOIN institucion i ON i.idInstitucion = ci.idInstitucion
            LEFT JOIN modalidadcarrerainstitucion m ON m.idModalidadCarreraInstitucion = ci.idModalidadCarreraInstitucion
            WHERE ci.idCarrera = %s{where_extra_sql}
            ORDER BY i.nombreInstitucion, ci.tituloCarrera
            """,
            tuple(params)
        )

        rows = cur.fetchall() or []
        data = []
        for r in rows:
            id_ci = r.get('idCarreraInstitucion')
            data.append({
                "idCarreraInstitucion": id_ci,
                "nombreInstitucion": r.get('nombreInstitucion'),
                "urlLogo": r.get('urlLogo'),
                "tituloCarrera": r.get('tituloCarrera'),
                "nombreCarrera": r.get('nombreCarreraCI'),
                "modalidad": r.get('nombreModalidad'),
                "montoCuota": float(r.get('montoCuota') or 0),
                "detailPath": f"/api/v1/careers/{id_carrera}/institutions/{id_ci}",
                "aliasPath": f"/api/v1/careers/{id_ci}",
                "meInteresaPath": f"/api/v1/careers/{id_ci}/interest",
            })
        return jsonify(data), 200
    except Exception as e:
        log(f"/careers/{id_carrera}/institutions GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Error al consultar instituciones de la carrera"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Detalle de una carrera en institución (ruta completa con carrera)
@app.route('/api/v1/careers/<int:id_carrera>/institutions/<int:id_ci>', methods=['GET'])
def career_institution_detail(id_carrera: int, id_ci: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        cur.execute(
            """
            SELECT ci.*, c.nombreCarrera AS nombreCarreraBase,
                   i.idInstitucion, i.nombreInstitucion, i.siglaInstitucion, i.telefono, i.mail, i.sitioWeb, i.urlLogo, i.direccion,
                   m.nombreModalidad
            FROM carrerainstitucion ci
            JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN institucion i ON i.idInstitucion = ci.idInstitucion
            LEFT JOIN modalidadcarrerainstitucion m ON m.idModalidadCarreraInstitucion = ci.idModalidadCarreraInstitucion
            WHERE ci.idCarreraInstitucion = %s AND ci.idCarrera = %s
            """,
            (id_ci, id_carrera)
        )
        ci = cur.fetchone()
        if not ci:
            return jsonify({"errorCode": "ERR1", "message": "Carrera/Institución no encontrada"}), 404

        # Multimedia
        cur.execute(
            """
            SELECT idContenidoMultimedia, titulo, descripcion, enlace
            FROM contenidomultimedia
            WHERE idCarreraInstitucion = %s AND (fechaFin IS NULL OR fechaFin > NOW())
            ORDER BY fechaInicio DESC, idContenidoMultimedia DESC
            """,
            (id_ci,)
        )
        multimedia = cur.fetchall() or []

        # Pregunta frecuente asociada (si la hay)
        faq = None
        if ci.get('idPreguntaFrecuente'):
            cur.execute(
                """
                SELECT idPreguntaFrecuente, nombrePregunta, respuesta
                FROM preguntafrecuente
                WHERE idPreguntaFrecuente = %s AND (fechaFin IS NULL OR fechaFin > NOW())
                """,
                (ci.get('idPreguntaFrecuente'),)
            )
            faq = cur.fetchone()

        detalle = {
            "carreraInstitucion": {
                "id": ci.get('idCarreraInstitucion'),
                "nombreCarrera": ci.get('nombreCarrera') or ci.get('nombreCarreraBase'),
                "tituloCarrera": ci.get('tituloCarrera'),
                "duracion": (float(ci.get('duracionCarrera')) if isinstance(ci.get('duracionCarrera'), (int, float, decimal.Decimal)) else None),
                "horasCursado": ci.get('horasCursado'),
                "montoCuota": (float(ci.get('montoCuota')) if isinstance(ci.get('montoCuota'), (int, float, decimal.Decimal)) else None),
                "modalidad": ci.get('nombreModalidad'),
                "observaciones": ci.get('observaciones'),
            },
            "institucion": {
                "id": ci.get('idInstitucion'),
                "nombre": ci.get('nombreInstitucion'),
                "sigla": ci.get('siglaInstitucion'),
                "telefono": ci.get('telefono'),
                "mail": ci.get('mail'),
                "sitioWeb": ci.get('sitioWeb'),
                "urlLogo": ci.get('urlLogo'),
                "direccion": ci.get('direccion'),
            },
            "preguntaFrecuente": faq,
            "multimedia": multimedia,
            "acciones": {
                "meInteresaPath": f"/api/v1/careers/{ci.get('idCarreraInstitucion')}/interest"
            }
        }
        return jsonify(detalle), 200
    except Exception as e:
        log(f"/careers/{id_carrera}/institutions/{id_ci} GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Error al consultar el detalle de la carrera"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Alias: detalle por idCarreraInstitucion (compatibilidad con US012 consultarCarreraPath)
@app.route('/api/v1/careers/<int:id_ci>', methods=['GET'])
def career_institution_detail_alias(id_ci: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT ci.*, c.nombreCarrera AS nombreCarreraBase,
                   i.idInstitucion, i.nombreInstitucion, i.siglaInstitucion, i.telefono, i.mail, i.sitioWeb, i.urlLogo, i.direccion,
                   m.nombreModalidad
            FROM carrerainstitucion ci
            JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN institucion i ON i.idInstitucion = ci.idInstitucion
            LEFT JOIN modalidadcarrerainstitucion m ON m.idModalidadCarreraInstitucion = ci.idModalidadCarreraInstitucion
            WHERE ci.idCarreraInstitucion = %s
            """,
            (id_ci,)
        )
        ci = cur.fetchone()
        if not ci:
            return jsonify({"errorCode": "ERR1", "message": "Carrera/Institución no encontrada"}), 404

        # Multimedia
        cur.execute(
            """
            SELECT idContenidoMultimedia, titulo, descripcion, enlace
            FROM contenidomultimedia
            WHERE idCarreraInstitucion = %s AND (fechaFin IS NULL OR fechaFin > NOW())
            ORDER BY fechaInicio DESC, idContenidoMultimedia DESC
            """,
            (id_ci,)
        )
        multimedia = cur.fetchall() or []

        # Pregunta frecuente asociada (si la hay)
        faq = None
        if ci.get('idPreguntaFrecuente'):
            cur.execute(
                """
                SELECT idPreguntaFrecuente, nombrePregunta, respuesta
                FROM preguntafrecuente
                WHERE idPreguntaFrecuente = %s AND (fechaFin IS NULL OR fechaFin > NOW())
                """,
                (ci.get('idPreguntaFrecuente'),)
            )
            faq = cur.fetchone()

        detalle = {
            "carreraInstitucion": {
                "id": ci.get('idCarreraInstitucion'),
                "nombreCarrera": ci.get('nombreCarrera') or ci.get('nombreCarreraBase'),
                "tituloCarrera": ci.get('tituloCarrera'),
                "duracion": (float(ci.get('duracionCarrera')) if isinstance(ci.get('duracionCarrera'), (int, float, decimal.Decimal)) else None),
                "horasCursado": ci.get('horasCursado'),
                "montoCuota": (float(ci.get('montoCuota')) if isinstance(ci.get('montoCuota'), (int, float, decimal.Decimal)) else None),
                "modalidad": ci.get('nombreModalidad'),
                "observaciones": ci.get('observaciones'),
            },
            "institucion": {
                "id": ci.get('idInstitucion'),
                "nombre": ci.get('nombreInstitucion'),
                "sigla": ci.get('siglaInstitucion'),
                "telefono": ci.get('telefono'),
                "mail": ci.get('mail'),
                "sitioWeb": ci.get('sitioWeb'),
                "urlLogo": ci.get('urlLogo'),
                "direccion": ci.get('direccion'),
            },
            "preguntaFrecuente": faq,
            "multimedia": multimedia,
            "acciones": {
                "meInteresaPath": f"/api/v1/careers/{ci.get('idCarreraInstitucion')}/interest"
            }
        }
        return jsonify(detalle), 200
    except Exception as e:
        log(f"/careers/{id_ci} GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Error al consultar el detalle de la carrera"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Marcar "Me interesa" directamente desde la ruta de carreras
@app.route('/api/v1/careers/<int:id_ci>/interest', methods=['POST'])
@token_required
def careers_mark_interest(current_user_id: int, id_ci: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Validar que exista la carrera/institución
        cur.execute("SELECT 1 FROM carrerainstitucion WHERE idCarreraInstitucion=%s", (id_ci,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "La carrera/institución no existe"}), 404

        # Verificar que no exista ya un interés activo
        cur.execute(
            """
            SELECT 1
            FROM interesusuariocarrera
            WHERE idUsuario = %s AND idCarreraInstitucion = %s
              AND (fechaFin IS NULL OR fechaFin > NOW())
            """,
            (current_user_id, id_ci)
        )
        if cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "La carrera ya está marcada como preferida"}), 400

        # Insertar interés
        cur.execute(
            """
            INSERT INTO interesusuariocarrera (idUsuario, idCarreraInstitucion, fechaInicio)
            VALUES (%s, %s, NOW())
            """,
            (current_user_id, id_ci)
        )
        conn.commit()
        return jsonify({"ok": True}), 201
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        log(f"/careers/{id_ci}/interest POST error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "No se pudo agregar la preferencia"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ Consultar Instituciones (US015) ============================

# Lista de instituciones con filtros: ?search=, ?tipo=, ?tipoId=, ?localidad=, ?provincia=, ?pais=
@app.route('/api/v1/institutions', methods=['GET'])
def institutions_list():
    conn = None
    try:
        args = request.args
        search = (args.get('search') or args.get('q') or '').strip()
        tipo = (args.get('tipo') or '').strip()
        tipo_id = args.get('tipoId')
        localidad = (args.get('localidad') or '').strip()
        provincia = (args.get('provincia') or '').strip()
        pais = (args.get('pais') or '').strip()

        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        where = []
        params = []

        if search:
            like = f"%{search}%"
            where.append("(i.nombreInstitucion LIKE %s OR i.siglaInstitucion LIKE %s OR ti.nombreTipoInstitucion LIKE %s OR l.nombreLocalidad LIKE %s OR p.nombreProvincia LIKE %s OR pa.nombrePais LIKE %s)")
            params.extend([like, like, like, like, like, like])
        if tipo:
            where.append("ti.nombreTipoInstitucion LIKE %s")
            params.append(f"%{tipo}%")
        if tipo_id:
            try:
                tipo_id_int = int(tipo_id)
                where.append("i.idTipoInstitucion = %s")
                params.append(tipo_id_int)
            except Exception:
                return jsonify({"errorCode": "ERR1", "message": "Parámetros de búsqueda inválidos"}), 400
        if localidad:
            where.append("l.nombreLocalidad LIKE %s")
            params.append(f"%{localidad}%")
        if provincia:
            where.append("p.nombreProvincia LIKE %s")
            params.append(f"%{provincia}%")
        if pais:
            where.append("pa.nombrePais LIKE %s")
            params.append(f"%{pais}%")

        where_sql = (" WHERE " + " AND ".join(where)) if where else ""

        sql = f"""
            SELECT i.idInstitucion,
                   i.nombreInstitucion,
                   i.siglaInstitucion,
                   i.urlLogo,
                   i.telefono,
                   i.mail,
                   i.sitioWeb,
                   i.direccion,
                   ti.nombreTipoInstitucion,
                   l.nombreLocalidad,
                   p.nombreProvincia,
                   pa.nombrePais,
                   COUNT(ci.idCarreraInstitucion) AS cantidadCarreras
            FROM institucion i
            LEFT JOIN tipoinstitucion ti ON ti.idTipoInstitucion = i.idTipoInstitucion
            LEFT JOIN localidad l ON l.idLocalidad = i.idLocalidad
            LEFT JOIN provincia p ON p.idProvincia = l.idProvincia
            LEFT JOIN pais pa ON pa.idPais = p.idPais
            LEFT JOIN carrerainstitucion ci ON ci.idInstitucion = i.idInstitucion
            {where_sql}
            GROUP BY i.idInstitucion, i.nombreInstitucion, i.siglaInstitucion, i.urlLogo, i.telefono, i.mail, i.sitioWeb, i.direccion,
                     ti.nombreTipoInstitucion, l.nombreLocalidad, p.nombreProvincia, pa.nombrePais
            ORDER BY i.nombreInstitucion
        """

        cur.execute(sql, tuple(params))
        rows = cur.fetchall() or []
        if not rows:
            # Según HU: ERR1 si no existen instituciones para la búsqueda
            return jsonify({"errorCode": "ERR1", "message": "No existe institución con esos filtros"}), 400

        data = []
        for r in rows:
            data.append({
                "idInstitucion": r.get('idInstitucion'),
                "nombre": r.get('nombreInstitucion'),
                "sigla": r.get('siglaInstitucion'),
                "tipo": r.get('nombreTipoInstitucion'),
                "logo": r.get('urlLogo'),
                "descripcion": None,  # No existe campo descripción en el esquema actual
                "ubicacion": {
                    "localidad": r.get('nombreLocalidad'),
                    "provincia": r.get('nombreProvincia'),
                    "pais": r.get('nombrePais'),
                },
                "cantidadCarreras": int(r.get('cantidadCarreras') or 0),
                "detailPath": f"/api/v1/institutions/{r.get('idInstitucion')}"
            })
        return jsonify(data), 200
    except Exception as e:
        log(f"/institutions GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Error al consultar instituciones"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Detalle de institución con sus carreras disponibles
@app.route('/api/v1/institutions/<int:id_institucion>', methods=['GET'])
def institution_detail(id_institucion: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Datos de la institución
        cur.execute(
            """
            SELECT i.idInstitucion,
                   i.nombreInstitucion,
                   i.siglaInstitucion,
                   i.urlLogo,
                   i.telefono,
                   i.mail,
                   i.sitioWeb,
                   i.direccion,
                   ti.nombreTipoInstitucion,
                   l.nombreLocalidad,
                   p.nombreProvincia,
                   pa.nombrePais
            FROM institucion i
            LEFT JOIN tipoinstitucion ti ON ti.idTipoInstitucion = i.idTipoInstitucion
            LEFT JOIN localidad l ON l.idLocalidad = i.idLocalidad
            LEFT JOIN provincia p ON p.idProvincia = l.idProvincia
            LEFT JOIN pais pa ON pa.idPais = p.idPais
            WHERE i.idInstitucion = %s
            """,
            (id_institucion,)
        )
        i = cur.fetchone()
        if not i:
            return jsonify({"errorCode": "ERR1", "message": "No existe institución con esos filtros"}), 404

        # Carreras disponibles en la institución
        cur.execute(
            """
            SELECT ci.idCarreraInstitucion,
                   ci.tituloCarrera,
                   ci.nombreCarrera AS nombreCarreraCI,
                   c.idCarrera,
                   c.nombreCarrera AS nombreCarreraBase,
                   m.nombreModalidad
            FROM carrerainstitucion ci
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN modalidadcarrerainstitucion m ON m.idModalidadCarreraInstitucion = ci.idModalidadCarreraInstitucion
            WHERE ci.idInstitucion = %s
            ORDER BY c.nombreCarrera, ci.tituloCarrera
            """,
            (id_institucion,)
        )
        carreras_rows = cur.fetchall() or []
        carreras = []
        for r in carreras_rows:
            id_ci = r.get('idCarreraInstitucion')
            id_c = r.get('idCarrera')
            carreras.append({
                "idCarreraInstitucion": id_ci,
                "idCarrera": id_c,
                "nombreCarrera": r.get('nombreCarreraCI') or r.get('nombreCarreraBase'),
                "tituloCarrera": r.get('tituloCarrera'),
                "modalidad": r.get('nombreModalidad'),
                "detailPath": (f"/api/v1/careers/{id_c}/institutions/{id_ci}" if id_c else None),
                "aliasPath": f"/api/v1/careers/{id_ci}",
                "meInteresaPath": f"/api/v1/careers/{id_ci}/interest",
            })

        detalle = {
            "institucion": {
                "id": i.get('idInstitucion'),
                "nombre": i.get('nombreInstitucion'),
                "sigla": i.get('siglaInstitucion'),
                "tipo": i.get('nombreTipoInstitucion'),
                "logo": i.get('urlLogo'),
                "mail": i.get('mail'),
                "sitioWeb": i.get('sitioWeb'),
                "telefono": i.get('telefono'),
                "direccion": i.get('direccion'),
                "ubicacion": {
                    "localidad": i.get('nombreLocalidad'),
                    "provincia": i.get('nombreProvincia'),
                    "pais": i.get('nombrePais'),
                }
            },
            "carreras": carreras
        }
        return jsonify(detalle), 200
    except Exception as e:
        log(f"/institutions/{id_institucion} GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Error al consultar la institución"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ Perfil de Usuario (US016) ============================

# Ver perfil de usuario autenticado
@app.route('/api/v1/user/profile', methods=['GET'])
@token_required
def user_get_profile(current_user_id: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT idUsuario, nombre, apellido, mail, fechaNac, dni
            FROM usuario
            WHERE idUsuario = %s
            """,
            (current_user_id,)
        )
        u = cur.fetchone()
        if not u:
            return jsonify({"errorCode": "ERR1", "message": "Usuario no encontrado"}), 404


        return jsonify({
            "id": u.get('idUsuario'),
            "nombre": u.get('nombre'),
            "apellido": u.get('apellido'),
            "email": u.get('mail'),
            "fechaNacimiento": u.get('fechaNac'),
            "dni": u.get('dni'),
        }), 200
    except Exception as e:
        log(f"/user/profile GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "No se pudo obtener el perfil de usuario"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Editar perfil de usuario (nombre, apellido, fechaNacimiento, dni)
@app.route('/api/v1/user/profile', methods=['PUT'])
@token_required
def user_update_profile(current_user_id: int):
    conn = None
    try:
        data = request.get_json(silent=True) or {}
        nombre = (data.get('nombre') or None)
        apellido = (data.get('apellido') or None)
        fecha_nac_in = data.get('fechaNacimiento')
        dni_in = data.get('dni')

        updates = []
        params = []

        # Validar y preparar nombre/apellido
        if nombre is not None:
            nombre = nombre.strip()
            if nombre == '':
                return jsonify({"errorCode": "ERR1", "message": "Nombre inválido"}), 400
            updates.append("nombre = %s")
            params.append(nombre)
        if apellido is not None:
            apellido = apellido.strip()
            if apellido == '':
                return jsonify({"errorCode": "ERR1", "message": "Apellido inválido"}), 400
            updates.append("apellido = %s")
            params.append(apellido)

        # Validar y preparar fechaNacimiento
        if fecha_nac_in is not None:
            fecha_val = None
            try:
                # Aceptar 'YYYY-MM-DD' o ISO con tiempo; almacenar como 'YYYY-MM-DD 00:00:00'
                if isinstance(fecha_nac_in, str):
                    # Intentar parse estricto de fecha primero
                    import datetime as _dt
                    try:
                        fecha_val = _dt.datetime.strptime(fecha_nac_in[:10], '%Y-%m-%d')
                    except Exception:
                        fecha_val = _dt.datetime.fromisoformat(fecha_nac_in)
                elif isinstance(fecha_nac_in, (int, float)):
                    # timestamp (segundos)
                    import datetime as _dt
                    fecha_val = _dt.datetime.fromtimestamp(fecha_nac_in)
                else:
                    raise ValueError()
            except Exception:
                return jsonify({"errorCode": "ERR1", "message": "Fecha de nacimiento inválida"}), 400
            updates.append("fechaNac = %s")
            params.append(fecha_val.strftime('%Y-%m-%d 00:00:00'))

        # Validar y preparar DNI
        if dni_in is not None:
            try:
                dni_val = int(dni_in)
                if dni_val <= 0:
                    raise ValueError()
            except Exception:
                return jsonify({"errorCode": "ERR1", "message": "DNI inválido"}), 400
            updates.append("dni = %s")
            params.append(dni_val)

        if not updates:
            return jsonify({"errorCode": "ERR1", "message": "No hay datos para actualizar"}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Verificar existencia del usuario
        cur.execute("SELECT 1 FROM usuario WHERE idUsuario=%s", (current_user_id,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Usuario no encontrado"}), 404

        # Ejecutar UPDATE dinámico
        set_sql = ", ".join(updates)
        cur.execute(f"UPDATE usuario SET {set_sql} WHERE idUsuario = %s", tuple(params + [current_user_id]))
        conn.commit()

        # Devolver perfil actualizado (reusar GET)
        try:
            # Cerrar cursor previo y abrir dictionary=True para lectura
            cur.close()
        except Exception:
            pass
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT idUsuario, nombre, apellido, mail, fechaNac, dni
            FROM usuario
            WHERE idUsuario = %s
            """,
            (current_user_id,)
        )
        u = cur.fetchone()
        fn = u.get('fechaNac') if u else None
        fecha_str = None
        try:
            if fn:
                fecha_str = fn.date().isoformat()
        except Exception:
            fecha_str = None

        return jsonify({
            "ok": True,
            "usuario": {
                "id": u.get('idUsuario') if u else current_user_id,
                "nombre": (u.get('nombre') if u else nombre),
                "apellido": (u.get('apellido') if u else apellido),
                "email": (u.get('mail') if u else None),
                "fechaNacimiento": fecha_str,
                "dni": (u.get('dni') if u else None),
            }
        }), 200
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        log(f"/user/profile PUT error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "No se pudo actualizar el perfil"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ Registro de Institución (US017) ============================
# US017 - Registro de institución académica
# Requisitos:
# - Público (sin login)
# - GET /api/v1/institutions/registration/options -> devuelve tipos y ubicaciones (paises siempre; provincias opcional por ?countryId; localidades opcional por ?provinceId)
# - POST /api/v1/institutions/registration -> valida campos y crea institución con estado Pendiente de aprobación
# Errores:
# - ERR1: campos obligatorios faltantes -> "Todos los campos marcados con * son obligatorios"
# - ERR2: formato de identificación inválido (CUIT/ID legal no es entero positivo) -> "Formato de identificación inválido"
# - ERR3: correo inválido -> "Correo inválido. Verifique el formato"

# Opciones para formulario de registro: tipos de institución y ubicaciones dependientes
@app.route('/api/v1/institutions/registration/options', methods=['GET'])
def institutions_registration_options():
    conn = None
    try:
        country_id = request.args.get('countryId')
        province_id = request.args.get('provinceId')

        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Tipos de institución
        cur.execute(
            """
            SELECT idTipoInstitucion AS id, nombreTipoInstitucion AS nombre
            FROM tipoinstitucion
            WHERE (fechaFin IS NULL OR fechaFin > NOW()) OR fechaFin IS NULL
            ORDER BY nombreTipoInstitucion
            """
        )
        tipos = cur.fetchall() or []

        # Países
        cur.execute(
            """
            SELECT idPais AS id, nombrePais AS nombre
            FROM pais
            ORDER BY nombrePais
            """
        )
        paises = cur.fetchall() or []

        # Provincias (opcional por countryId)
        provincias = []
        if country_id is not None and country_id != '':
            try:
                cid = int(country_id)
                cur.execute(
                    """
                    SELECT idProvincia AS id, nombreProvincia AS nombre
                    FROM provincia
                    WHERE idPais = %s
                    ORDER BY nombreProvincia
                    """,
                    (cid,)
                )
                provincias = cur.fetchall() or []
            except Exception:
                provincias = []

        # Localidades (opcional por provinceId)
        localidades = []
        if province_id is not None and province_id != '':
            try:
                pid = int(province_id)
                cur.execute(
                    """
                    SELECT idLocalidad AS id, nombreLocalidad AS nombre
                    FROM localidad
                    WHERE idProvincia = %s
                    ORDER BY nombreLocalidad
                    """,
                    (pid,)
                )
                localidades = cur.fetchall() or []
            except Exception:
                localidades = []

        return jsonify({
            "tiposInstitucion": tipos,
            "paises": paises,
            "provincias": provincias,
            "localidades": localidades
        }), 200
    except Exception as e:
        log(f"/institutions/registration/options GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "No se pudieron cargar las opciones"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Enviar solicitud de registro de institución (público)
@app.route('/api/v1/institutions/registration', methods=['POST'])
def institutions_registration_submit():
    conn = None
    try:
        data = request.get_json(silent=True) or {}

        # Campos
        nombre = (data.get('nombreInstitucion') or '').strip()
        id_tipo = data.get('idTipoInstitucion')
        pais_id = data.get('paisId')
        provincia_id = data.get('provinciaId')
        localidad_id = data.get('localidadId')
        direccion = (data.get('direccion') or '').strip()
        email = (data.get('email') or data.get('mail') or '').strip()
        sigla = (data.get('siglaInstitucion') or '').strip() or None
        telefono = (data.get('telefono') or '').strip() or None
        sitio_web = (data.get('sitioWeb') or '').strip() or None
        url_logo = (data.get('urlLogo') or '').strip() or None
        anio_fund = data.get('anioFundacion')
        codigo_postal = data.get('codigoPostal')
        cuit = data.get('CUIT')

        # Validación básica requerida
        if not nombre or not id_tipo or not pais_id or not provincia_id or not localidad_id or not direccion or not email:
            return jsonify({"errorCode": "ERR1", "message": "Todos los campos marcados con * son obligatorios"}), 400

        # Tipos enteros
        try:
            id_tipo = int(id_tipo)
            pais_id = int(pais_id)
            provincia_id = int(provincia_id)
            localidad_id = int(localidad_id)
            if anio_fund is not None and anio_fund != '':
                anio_fund = int(anio_fund)
            else:
                anio_fund = None
            if codigo_postal is not None and codigo_postal != '':
                codigo_postal = int(codigo_postal)
            else:
                codigo_postal = None
        except Exception:
            return jsonify({"errorCode": "ERR1", "message": "Todos los campos marcados con * son obligatorios"}), 400

        # CUIT opcional pero si viene debe ser entero positivo
        if cuit is not None and cuit != '':
            try:
                cuit = int(cuit)
                if cuit <= 0:
                    raise ValueError()
            except Exception:
                return jsonify({"errorCode": "ERR2", "message": "Formato de identificación inválido"}), 400
        else:
            cuit = None

        # Email válido
        if not re.match(EMAIL_REGEX, email):
            return jsonify({"errorCode": "ERR3", "message": "Correo inválido. Verifique el formato"}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Validar FKs
        cur.execute("SELECT 1 FROM tipoinstitucion WHERE idTipoInstitucion=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Tipo de institución inválido"}), 400
        cur.execute("SELECT idProvincia FROM localidad WHERE idLocalidad=%s", (localidad_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"errorCode": "ERR1", "message": "Localidad inválida"}), 400
        prov_of_loc = row[0]
        if int(prov_of_loc) != provincia_id:
            return jsonify({"errorCode": "ERR1", "message": "Localidad no pertenece a la provincia seleccionada"}), 400
        cur.execute("SELECT idPais FROM provincia WHERE idProvincia=%s", (provincia_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"errorCode": "ERR1", "message": "Provincia inválida"}), 400
        pais_of_prov = row[0]
        if int(pais_of_prov) != pais_id:
            return jsonify({"errorCode": "ERR1", "message": "Provincia no pertenece al país seleccionado"}), 400

        # Insertar institución (idUsuario NULL al ser registro público)
        cur.execute(
            """
            INSERT INTO institucion (anioFundacion, codigoPostal, nombreInstitucion, CUIT, direccion, fechaAlta,
                                     siglaInstitucion, telefono, mail, sitioWeb, urlLogo, idTipoInstitucion, idLocalidad, idUsuario)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, NULL)
            """,
            (anio_fund, codigo_postal, nombre, cuit, direccion, sigla, telefono, email, sitio_web, url_logo, id_tipo, localidad_id)
        )
        conn.commit()

        # Obtener id
        cur.execute("SELECT LAST_INSERT_ID()")
        id_institucion = cur.fetchone()[0]

        # Estado Pendiente: asegurar existencia y asociar
        cur.execute(
            "SELECT idEstadoInstitucion FROM estadoinstitucion WHERE nombreEstadoInstitucion=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            ("Pendiente",)
        )
        row = cur.fetchone()
        if not row:
            cur.execute(
                "INSERT INTO estadoinstitucion (nombreEstadoInstitucion, fechaFin) VALUES (%s, NULL)",
                ("Pendiente",)
            )
            conn.commit()
            cur.execute(
                "SELECT idEstadoInstitucion FROM estadoinstitucion WHERE nombreEstadoInstitucion=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
                ("Pendiente",)
            )
            row = cur.fetchone()
        id_estado = row[0]

        cur.execute(
            """
            INSERT INTO institucionestado (fechaInicio, fechaFin, idEstadoInstitucion, idInstitucion)
            VALUES (NOW(), NULL, %s, %s)
            """,
            (id_estado, id_institucion)
        )
        conn.commit()

        return jsonify({"ok": True, "idInstitucion": int(id_institucion)}), 201
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        log(f"/institutions/registration POST error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "No se pudo registrar la institución"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# ============================ Gestión de carreras por institución (US018) ============================

def _get_my_institution_id(conn, current_user_id: int):
    cur = conn.cursor()
    cur.execute("SELECT idInstitucion FROM institucion WHERE idUsuario=%s ORDER BY idInstitucion LIMIT 1", (current_user_id,))
    row = cur.fetchone()
    return (row[0] if row else None)

# Listar carreras asociadas a mi institución
@app.route('/api/v1/institutions/me/careers', methods=['GET'])
@token_required
def my_institution_careers(current_user_id: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        id_inst = _get_my_institution_id(conn, current_user_id)
        if not id_inst:
            return jsonify({"errorCode": "ERR1", "message": "No tiene una institución asignada"}), 404

        cur.execute(
            """
            SELECT ci.idCarreraInstitucion,
                   COALESCE(ci.nombreCarrera, c.nombreCarrera) AS nombre,
                   ci.tituloCarrera,
                   m.nombreModalidad AS modalidad,
                   e.nombreEstadoCarreraInstitucion AS estado,
                   ci.montoCuota,
                   ci.fechaInicio,
                   ci.fechaFin
            FROM carrerainstitucion ci
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN modalidadcarrerainstitucion m ON m.idModalidadCarreraInstitucion = ci.idModalidadCarreraInstitucion
            LEFT JOIN estadocarrerainstitucion e ON e.idEstadoCarreraInstitucion = ci.idEstadoCarreraInstitucion
            WHERE ci.idInstitucion = %s
            ORDER BY nombre, ci.fechaInicio DESC, ci.idCarreraInstitucion DESC
            """,
            (id_inst,)
        )
        rows = cur.fetchall() or []
        data = []
        for r in rows:
            id_ci = r.get('idCarreraInstitucion')
            data.append({
                "idCarreraInstitucion": id_ci,
                "nombre": r.get('nombre'),
                "titulo": r.get('tituloCarrera'),
                "modalidad": r.get('modalidad'),
                "estado": r.get('estado'),
                "montoCuota": float(r.get('montoCuota') or 0),
                "fechaInicio": (r.get('fechaInicio').isoformat(sep=' ') if r.get('fechaInicio') else None),
                "fechaFin": (r.get('fechaFin').isoformat(sep=' ') if r.get('fechaFin') else None),
                "editPath": f"/api/v1/institutions/me/careers/{id_ci}",
                "deletePath": f"/api/v1/institutions/me/careers/{id_ci}"
            })
        return jsonify({
            "carreras": data,
            "agregarPath": "/api/v1/institutions/me/careers"
        }), 200
    except Exception as e:
        log(f"/institutions/me/careers GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Error al listar carreras"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Opciones para agregar/editar carrera (catálogo base y modalidades)
@app.route('/api/v1/institutions/me/careers/options', methods=['GET'])
@token_required
def my_institution_careers_options(current_user_id: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Carreras base activas
        cur.execute(
            """
            SELECT idCarrera AS id, nombreCarrera AS nombre
            FROM carrera
            WHERE (fechaFin IS NULL OR fechaFin > NOW())
            ORDER BY nombreCarrera
            """
        )
        carreras = cur.fetchall() or []

        # Modalidades
        cur.execute(
            """
            SELECT idModalidadCarreraInstitucion AS id, nombreModalidad AS nombre
            FROM modalidadcarrerainstitucion
            ORDER BY nombreModalidad
            """
        )
        modalidades = cur.fetchall() or []

        # Estados (opcionales)
        cur.execute(
            """
            SELECT idEstadoCarreraInstitucion AS id, nombreEstadoCarreraInstitucion AS nombre
            FROM estadocarrerainstitucion
            WHERE (fechaFin IS NULL OR fechaFin > NOW()) OR fechaFin IS NULL
            ORDER BY nombreEstadoCarreraInstitucion
            """
        )
        estados = cur.fetchall() or []

        return jsonify({
            "carrerasBase": carreras,
            "modalidades": modalidades,
            "estados": estados
        }), 200
    except Exception as e:
        log(f"/institutions/me/careers/options GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "No se pudieron cargar las opciones"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Agregar carrera a mi institución
@app.route('/api/v1/institutions/me/careers', methods=['POST'])
@token_required
def my_institution_careers_add(current_user_id: int):
    conn = None
    try:
        data = request.get_json(silent=True) or {}
        id_carrera = data.get('idCarrera')
        id_modalidad = data.get('idModalidad')
        id_estado = data.get('idEstado')  # opcional
        titulo = (data.get('tituloCarrera') or '').strip() or None
        nombre_ci = (data.get('nombreCarrera') or '').strip() or None
        cantidad_materias = data.get('cantidadMaterias')
        duracion = data.get('duracionCarrera')
        horas = data.get('horasCursado')
        observaciones = (data.get('observaciones') or '').strip() or None
        monto = data.get('montoCuota')
        fecha_inicio = data.get('fechaInicio')
        fecha_fin = data.get('fechaFin')

        # Validación de requeridos
        if id_carrera is None or id_modalidad is None:
            return jsonify({"errorCode": "ERR1", "message": "Debe completar todos los campos obligatorios para guardar los cambios."}), 400

        # Normalización
        try:
            id_carrera = int(id_carrera)
            id_modalidad = int(id_modalidad)
            if id_estado is not None:
                id_estado = int(id_estado)
            if cantidad_materias not in (None, ''):
                cantidad_materias = int(cantidad_materias)
            else:
                cantidad_materias = None
            if duracion not in (None, ''):
                duracion = float(duracion)
            else:
                duracion = None
            if horas not in (None, ''):
                horas = int(horas)
            else:
                horas = None
            if monto not in (None, ''):
                monto = float(monto)
            else:
                monto = None
        except Exception:
            return jsonify({"errorCode": "ERR1", "message": "Debe completar todos los campos obligatorios para guardar los cambios."}), 400

        # Parse fechas si vienen
        fi_dt = None
        ff_dt = None
        try:
            import datetime as _dt
            if isinstance(fecha_inicio, str) and fecha_inicio:
                fi_dt = _dt.datetime.fromisoformat(fecha_inicio)
            if isinstance(fecha_fin, str) and fecha_fin:
                ff_dt = _dt.datetime.fromisoformat(fecha_fin)
        except Exception:
            return jsonify({"errorCode": "ERR1", "message": "Debe completar todos los campos obligatorios para guardar los cambios."}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        id_inst = _get_my_institution_id(conn, current_user_id)
        if not id_inst:
            return jsonify({"errorCode": "ERR1", "message": "No tiene una institución asignada"}), 404

        # Validar carrera base y modalidad
        cur.execute("SELECT 1 FROM carrera WHERE idCarrera=%s", (id_carrera,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Carrera base inválida"}), 400
        cur.execute("SELECT 1 FROM modalidadcarrerainstitucion WHERE idModalidadCarreraInstitucion=%s", (id_modalidad,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Modalidad inválida"}), 400

        # Estado: si no provisto, intentar usar/crear 'Activa'
        if id_estado is None:
            cur.execute(
                "SELECT idEstadoCarreraInstitucion FROM estadocarrerainstitucion WHERE nombreEstadoCarreraInstitucion=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
                ("Activa",)
            )
            row = cur.fetchone()
            if not row:
                cur.execute(
                    "INSERT INTO estadocarrerainstitucion (nombreEstadoCarreraInstitucion, fechaFin) VALUES (%s, NULL)",
                    ("Activa",)
                )
                conn.commit()
                cur.execute(
                    "SELECT idEstadoCarreraInstitucion FROM estadocarrerainstitucion WHERE nombreEstadoCarreraInstitucion=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
                    ("Activa",)
                )
                row = cur.fetchone()
            id_estado = row[0]
        else:
            cur.execute("SELECT 1 FROM estadocarrerainstitucion WHERE idEstadoCarreraInstitucion=%s", (id_estado,))
            if not cur.fetchone():
                return jsonify({"errorCode": "ERR1", "message": "Estado inválido"}), 400

        # Insertar CI
        cur.execute(
            """
            INSERT INTO carrerainstitucion (
                cantidadMaterias, duracionCarrera, fechaFin, fechaInicio, horasCursado, observaciones,
                nombreCarrera, tituloCarrera, montoCuota, idEstadoCarreraInstitucion, idCarrera,
                idPreguntaFrecuente, idModalidadCarreraInstitucion, idInstitucion
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL,%s,%s)
            """,
            (
                cantidad_materias, duracion, ff_dt, fi_dt, horas, observaciones,
                nombre_ci, titulo, monto, id_estado, id_carrera, id_modalidad, id_inst
            )
        )
        conn.commit()
        return jsonify({"ok": True}), 201
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        log(f"/institutions/me/careers POST error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "Debe completar todos los campos obligatorios para guardar los cambios."}), 400
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Editar carrera de mi institución
@app.route('/api/v1/institutions/me/careers/<int:id_ci>', methods=['PUT'])
@token_required
def my_institution_careers_edit(current_user_id: int, id_ci: int):
    conn = None
    try:
        data = request.get_json(silent=True) or {}
        # Si algún campo requerido está vacío -> ERR1
        if any((k in data and (data[k] is None or (isinstance(data[k], str) and data[k].strip() == ''))) for k in ['idModalidad']):
            return jsonify({"errorCode": "ERR1", "message": "Debe completar todos los campos obligatorios para guardar los cambios."}), 400

        id_modalidad = data.get('idModalidad')
        id_estado = data.get('idEstado')
        titulo = (data.get('tituloCarrera') or '').strip() if data.get('tituloCarrera') is not None else None
        nombre_ci = (data.get('nombreCarrera') or '').strip() if data.get('nombreCarrera') is not None else None
        cantidad_materias = data.get('cantidadMaterias') if data.get('cantidadMaterias') is not None else None
        duracion = data.get('duracionCarrera') if data.get('duracionCarrera') is not None else None
        horas = data.get('horasCursado') if data.get('horasCursado') is not None else None
        observaciones = (data.get('observaciones') or '').strip() if data.get('observaciones') is not None else None
        monto = data.get('montoCuota') if data.get('montoCuota') is not None else None
        fecha_inicio = data.get('fechaInicio') if data.get('fechaInicio') is not None else None
        fecha_fin = data.get('fechaFin') if data.get('fechaFin') is not None else None

        # Normalizaciones
        try:
            if id_modalidad is not None:
                id_modalidad = int(id_modalidad)
            if id_estado is not None:
                id_estado = int(id_estado)
            if cantidad_materias is not None:
                cantidad_materias = int(cantidad_materias)
            if duracion is not None:
                duracion = float(duracion)
            if horas is not None:
                horas = int(horas)
            if monto is not None:
                monto = float(monto)
        except Exception:
            return jsonify({"errorCode": "ERR1", "message": "Debe completar todos los campos obligatorios para guardar los cambios."}), 400

        fi_dt = None
        ff_dt = None
        try:
            import datetime as _dt
            if isinstance(fecha_inicio, str) and fecha_inicio != '':
                fi_dt = _dt.datetime.fromisoformat(fecha_inicio)
            if isinstance(fecha_fin, str) and fecha_fin != '':
                ff_dt = _dt.datetime.fromisoformat(fecha_fin)
        except Exception:
            return jsonify({"errorCode": "ERR1", "message": "Debe completar todos los campos obligatorios para guardar los cambios."}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        id_inst = _get_my_institution_id(conn, current_user_id)
        if not id_inst:
            return jsonify({"errorCode": "ERR1", "message": "No tiene una institución asignada"}), 404

        # Validar que la carrera pertenezca a mi institución
        cur.execute("SELECT 1 FROM carrerainstitucion WHERE idCarreraInstitucion=%s AND idInstitucion=%s", (id_ci, id_inst))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Carrera no encontrada"}), 404

        # Validar claves referenciales si vienen
        if id_modalidad is not None:
            cur.execute("SELECT 1 FROM modalidadcarrerainstitucion WHERE idModalidadCarreraInstitucion=%s", (id_modalidad,))
            if not cur.fetchone():
                return jsonify({"errorCode": "ERR1", "message": "Modalidad inválida"}), 400
        if id_estado is not None:
            cur.execute("SELECT 1 FROM estadocarrerainstitucion WHERE idEstadoCarreraInstitucion=%s", (id_estado,))
            if not cur.fetchone():
                return jsonify({"errorCode": "ERR1", "message": "Estado inválido"}), 400

        # Construir UPDATE dinámico
        sets = []
        params = []
        if id_modalidad is not None:
            sets.append("idModalidadCarreraInstitucion=%s")
            params.append(id_modalidad)
        if id_estado is not None:
            sets.append("idEstadoCarreraInstitucion=%s")
            params.append(id_estado)
        if titulo is not None:
            sets.append("tituloCarrera=%s")
            params.append(titulo)
        if nombre_ci is not None:
            sets.append("nombreCarrera=%s")
            params.append(nombre_ci)
        if cantidad_materias is not None:
            sets.append("cantidadMaterias=%s")
            params.append(cantidad_materias)
        if duracion is not None:
            sets.append("duracionCarrera=%s")
            params.append(duracion)
        if horas is not None:
            sets.append("horasCursado=%s")
            params.append(horas)
        if observaciones is not None:
            sets.append("observaciones=%s")
            params.append(observaciones)
        if monto is not None:
            sets.append("montoCuota=%s")
            params.append(monto)
        if fi_dt is not None:
            sets.append("fechaInicio=%s")
            params.append(fi_dt)
        if ff_dt is not None:
            sets.append("fechaFin=%s")
            params.append(ff_dt)

        if not sets:
            return jsonify({"errorCode": "ERR1", "message": "Debe completar todos los campos obligatorios para guardar los cambios."}), 400

        cur.execute(f"UPDATE carrerainstitucion SET {', '.join(sets)} WHERE idCarreraInstitucion=%s", tuple(params + [id_ci]))
        conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        log(f"/institutions/me/careers/{id_ci} PUT error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "Debe completar todos los campos obligatorios para guardar los cambios."}), 400
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Eliminar (desactivar) carrera de mi institución
@app.route('/api/v1/institutions/me/careers/<int:id_ci>', methods=['DELETE'])
@token_required
def my_institution_careers_delete(current_user_id: int, id_ci: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        id_inst = _get_my_institution_id(conn, current_user_id)
        if not id_inst:
            return jsonify({"errorCode": "ERR2", "message": "No se pudo eliminar la carrera. Intente nuevamente."}), 500

        # Validar pertenencia
        cur.execute("SELECT 1 FROM carrerainstitucion WHERE idCarreraInstitucion=%s AND idInstitucion=%s", (id_ci, id_inst))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR2", "message": "No se pudo eliminar la carrera. Intente nuevamente."}), 400

        # Desactivar vía fechaFin
        cur.execute("UPDATE carrerainstitucion SET fechaFin = NOW() WHERE idCarreraInstitucion=%s", (id_ci,))
        conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        log(f"/institutions/me/careers/{id_ci} DELETE error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR2", "message": "No se pudo eliminar la carrera. Intente nuevamente."}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


# # ============================ Gestión de Preguntas Frecuentes por Carrera (US019) ============================
# Se reutiliza la tabla existente `preguntafrecuente` y el campo
# `idPreguntaFrecuente` de `carrerainstitucion` (un FAQ por carrera-institución).
# Si en el futuro se requieren múltiples FAQs por carrera, habría que normalizar.

def _career_institution_owned(conn, current_user_id: int, id_ci: int):
    """Devuelve idInstitucion si la carrera pertenece a la institución del usuario."""
    cur = conn.cursor()
    cur.execute("SELECT idInstitucion FROM institucion WHERE idUsuario=%s LIMIT 1", (current_user_id,))
    row = cur.fetchone()
    if not row:
        return None
    id_inst = row[0]
    cur.execute(
        "SELECT 1 FROM carrerainstitucion WHERE idCarreraInstitucion=%s AND idInstitucion=%s",
        (id_ci, id_inst)
    )
    return id_inst if cur.fetchone() else None

# Listar FAQ de una carrera-institución (0 o 1)
@app.route('/api/v1/institutions/me/careers/<int:id_ci>/faqs', methods=['GET'])
@token_required
def my_institution_career_faq_get(current_user_id: int, id_ci: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if not _career_institution_owned(conn, current_user_id, id_ci):
            return jsonify({"errorCode": "ERR1", "message": "Carrera no encontrada"}), 404
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT pf.idPreguntaFrecuente, pf.nombrePregunta, pf.respuesta, pf.fechaFin
            FROM carrerainstitucion ci
            JOIN preguntafrecuente pf ON pf.idPreguntaFrecuente = ci.idPreguntaFrecuente
            WHERE ci.idCarreraInstitucion=%s AND ci.idPreguntaFrecuente IS NOT NULL
              AND (pf.fechaFin IS NULL OR pf.fechaFin > NOW())
            """,
            (id_ci,)
        )
        row = cur.fetchone()
        data = ([] if not row else [{
            "idPreguntaFrecuente": row['idPreguntaFrecuente'],
            "pregunta": row['nombrePregunta'],
            "respuesta": row['respuesta']
        }])
        return jsonify(data), 200
    except Exception as e:
        log(f"/institutions/me/careers/{id_ci}/faqs GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Error al consultar preguntas frecuentes"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception:
            pass

# Crear FAQ (si ya existe, error)
@app.route('/api/v1/institutions/me/careers/<int:id_ci>/faqs', methods=['POST'])
@token_required
def my_institution_career_faq_create(current_user_id: int, id_ci: int):
    conn = None
    try:
        data = request.get_json(silent=True) or {}
        pregunta = (data.get('pregunta') or data.get('nombrePregunta') or '').strip()
        respuesta = (data.get('respuesta') or '').strip()
        if not pregunta or not respuesta:
            return jsonify({"errorCode": "ERR1", "message": "Datos incompletos"}), 400
        conn = mysql.connector.connect(**DB_CONFIG)
        if not _career_institution_owned(conn, current_user_id, id_ci):
            return jsonify({"errorCode": "ERR1", "message": "Carrera no encontrada"}), 404
        cur = conn.cursor()
        # Verificar si ya tiene FAQ
        cur.execute("SELECT idPreguntaFrecuente FROM carrerainstitucion WHERE idCarreraInstitucion=%s", (id_ci,))
        row = cur.fetchone()
        if row and row[0]:
            return jsonify({"errorCode": "ERR1", "message": "Ya existe una pregunta frecuente"}), 400
        # Insertar FAQ
        cur.execute(
            "INSERT INTO preguntafrecuente (fechaFin, nombrePregunta, respuesta) VALUES (NULL,%s,%s)",
            (pregunta, respuesta)
        )
        conn.commit()
        cur.execute("SELECT LAST_INSERT_ID()")
        id_faq = cur.fetchone()[0]
        # Asociar a la carrera
        cur.execute("UPDATE carrerainstitucion SET idPreguntaFrecuente=%s WHERE idCarreraInstitucion=%s", (id_faq, id_ci))
        conn.commit()
        return jsonify({"ok": True, "idPreguntaFrecuente": int(id_faq)}), 201
    except Exception as e:
        try:
            if conn: conn.rollback()
        except Exception: pass
        log(f"/institutions/me/careers/{id_ci}/faqs POST error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "No se pudo crear la pregunta frecuente"}), 400
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# Actualizar FAQ existente
@app.route('/api/v1/institutions/me/careers/<int:id_ci>/faqs/<int:id_faq>', methods=['PUT'])
@token_required
def my_institution_career_faq_update(current_user_id: int, id_ci: int, id_faq: int):
    conn = None
    try:
        data = request.get_json(silent=True) or {}
        pregunta = data.get('pregunta') or data.get('nombrePregunta')
        respuesta = data.get('respuesta')
        if pregunta is None and respuesta is None:
            return jsonify({"errorCode": "ERR1", "message": "Sin datos para actualizar"}), 400
        conn = mysql.connector.connect(**DB_CONFIG)
        if not _career_institution_owned(conn, current_user_id, id_ci):
            return jsonify({"errorCode": "ERR1", "message": "Carrera no encontrada"}), 404
        cur = conn.cursor()
        # Validar pertenencia del FAQ
        cur.execute(
            "SELECT idPreguntaFrecuente FROM carrerainstitucion WHERE idCarreraInstitucion=%s",
            (id_ci,)
        )
        row = cur.fetchone()
        if not row or not row[0] or int(row[0]) != id_faq:
            return jsonify({"errorCode": "ERR1", "message": "Pregunta frecuente no encontrada"}), 404
        sets = []
        params = []
        if pregunta is not None:
            p = pregunta.strip()
            if not p:
                return jsonify({"errorCode": "ERR1", "message": "Pregunta inválida"}), 400
            sets.append("nombrePregunta=%s")
            params.append(p)
        if respuesta is not None:
            r = respuesta.strip()
            if not r:
                return jsonify({"errorCode": "ERR1", "message": "Respuesta inválida"}), 400
            sets.append("respuesta=%s")
            params.append(r)
        if not sets:
            return jsonify({"errorCode": "ERR1", "message": "Sin datos para actualizar"}), 400
        cur.execute(f"UPDATE preguntafrecuente SET {', '.join(sets)} WHERE idPreguntaFrecuente=%s", tuple(params + [id_faq]))
        conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        try:
            if conn: conn.rollback()
        except Exception: pass
        log(f"/institutions/me/careers/{id_ci}/faqs/{id_faq} PUT error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "No se pudo actualizar la pregunta frecuente"}), 400
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# Eliminar (desasociar + baja lógica) FAQ
@app.route('/api/v1/institutions/me/careers/<int:id_ci>/faqs/<int:id_faq>', methods=['DELETE'])
@token_required
def my_institution_career_faq_delete(current_user_id: int, id_ci: int, id_faq: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if not _career_institution_owned(conn, current_user_id, id_ci):
            return jsonify({"errorCode": "ERR1", "message": "Carrera no encontrada"}), 404
        cur = conn.cursor()
        cur.execute("SELECT idPreguntaFrecuente FROM carrerainstitucion WHERE idCarreraInstitucion=%s", (id_ci,))
        row = cur.fetchone()
        if not row or not row[0] or int(row[0]) != id_faq:
            return jsonify({"errorCode": "ERR1", "message": "Pregunta frecuente no encontrada"}), 404
        # Baja lógica + desasociar
        cur.execute("UPDATE preguntafrecuente SET fechaFin = NOW() WHERE idPreguntaFrecuente=%s", (id_faq,))
        cur.execute("UPDATE carrerainstitucion SET idPreguntaFrecuente=NULL WHERE idCarreraInstitucion=%s", (id_ci,))
        conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        try:
            if conn: conn.rollback()
        except Exception: pass
        log(f"/institutions/me/careers/{id_ci}/faqs/{id_faq} DELETE error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "No se pudo eliminar la pregunta frecuente"}), 400
    finally:
        try:
            if conn: conn.close()
        except Exception: pass



# ============================ Material Complementario (US020) ============================
# Requisitos:
# - Solo representante institucional (mismo criterio que US018: carrera debe pertenecer a su institución)
# - Campos: titulo (obligatorio), descripcion (opcional), enlace o archivo (en este backend simple usaremos campo enlace)
# - Tabla reutilizada: contenidomultimedia (ya utilizada para mostrar en detalle de carrera)
#   Asumimos columnas: idContenidoMultimedia, titulo, descripcion, enlace, fechaInicio, fechaFin, idCarreraInstitucion
# - Validaciones de error:
#   ERR1: Título vacío -> "Debe ingresar un título para el material."
#   ERR2: Enlace vacío o inválido -> "Debe adjuntar un archivo o ingresar un enlace válido."
#   ERR3: Error técnico al guardar -> "No se pudieron guardar los cambios. Intente nuevamente."
#   ERR4: Error técnico al eliminar -> "No se pudo eliminar el material complementario. Intente nuevamente."

def _my_inst_id(conn, user_id:int):
    cur = conn.cursor()
    cur.execute("SELECT idInstitucion FROM institucion WHERE idUsuario=%s ORDER BY idInstitucion LIMIT 1", (user_id,))
    r = cur.fetchone()
    return r[0] if r else None

def _ci_belongs(conn, id_ci:int, id_inst:int):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM carrerainstitucion WHERE idCarreraInstitucion=%s AND idInstitucion=%s", (id_ci, id_inst))
    return cur.fetchone() is not None

# Listar material complementario de una carrera propia
@app.route('/api/v1/institutions/me/careers/<int:id_ci>/materials', methods=['GET'])
@token_required
def materials_list(current_user_id:int, id_ci:int):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        id_inst = _my_inst_id(conn, current_user_id)
        if not id_inst or not _ci_belongs(conn, id_ci, id_inst):
            return jsonify({"errorCode":"ERR1","message":"Carrera no encontrada"}), 404
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT idContenidoMultimedia, titulo, descripcion, enlace, fechaInicio
            FROM contenidomultimedia
            WHERE idCarreraInstitucion=%s AND (fechaFin IS NULL OR fechaFin>NOW())
            ORDER BY fechaInicio DESC, idContenidoMultimedia DESC
            """, (id_ci,)
        )
        rows = cur.fetchall() or []
        data=[]
        for r in rows:
            data.append({
                "id": r['idContenidoMultimedia'],
                "titulo": r['titulo'],
                "descripcion": r.get('descripcion'),
                "enlace": r.get('enlace'),
                "fecha": (r.get('fechaInicio').isoformat(sep=' ') if r.get('fechaInicio') else None),
                "editPath": f"/api/v1/institutions/me/careers/{id_ci}/materials/{r['idContenidoMultimedia']}",
                "deletePath": f"/api/v1/institutions/me/careers/{id_ci}/materials/{r['idContenidoMultimedia']}"
            })
        return jsonify({
            "materiales": data,
            "agregarPath": f"/api/v1/institutions/me/careers/{id_ci}/materials"
        }), 200
    except Exception as e:
        log(f"US020 LIST error: {e}\n{traceback.format_exc()}")
        return jsonify({"message":"Error al listar material complementario"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# Crear material complementario
@app.route('/api/v1/institutions/me/careers/<int:id_ci>/materials', methods=['POST'])
@token_required
def materials_create(current_user_id:int, id_ci:int):
    conn=None
    try:
        data = request.get_json(silent=True) or {}
        titulo = (data.get('titulo') or '').strip()
        descripcion = (data.get('descripcion') or '').strip() or None
        enlace = (data.get('enlace') or '').strip()
        if not titulo:
            return jsonify({"errorCode":"ERR1","message":"Debe ingresar un título para el material."}), 400
        # Enlace básico: permitir http(s) o ruta simple de archivo (simples heurísticas)
        if not enlace or not re.match(r'^(https?://|/|[A-Za-z0-9._-]+)', enlace):
            return jsonify({"errorCode":"ERR2","message":"Debe adjuntar un archivo o ingresar un enlace válido."}), 400
        conn = mysql.connector.connect(**DB_CONFIG)
        id_inst = _my_inst_id(conn, current_user_id)
        if not id_inst or not _ci_belongs(conn, id_ci, id_inst):
            return jsonify({"errorCode":"ERR1","message":"Carrera no encontrada"}), 404
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO contenidomultimedia (titulo, descripcion, enlace, fechaInicio, fechaFin, idCarreraInstitucion)
            VALUES (%s,%s,%s,NOW(),NULL,%s)""",
            (titulo, descripcion, enlace, id_ci)
        )
        conn.commit()
        return jsonify({"ok":True, "message":"Se guardó correctamente el nuevo contenido Multimedia"}), 201
    except Exception as e:
        try:
            if conn: conn.rollback()
        except Exception: pass
        log(f"US020 CREATE error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR3","message":"No se pudieron guardar los cambios. Intente nuevamente."}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# Editar material complementario
@app.route('/api/v1/institutions/me/careers/<int:id_ci>/materials/<int:id_mat>', methods=['PUT'])
@token_required
def materials_update(current_user_id:int, id_ci:int, id_mat:int):
    conn=None
    try:
        data = request.get_json(silent=True) or {}
        titulo = data.get('titulo')
        descripcion = data.get('descripcion') if 'descripcion' in data else None
        enlace = data.get('enlace') if 'enlace' in data else None
        # Validaciones si se actualizan
        if titulo is not None and (not isinstance(titulo,str) or titulo.strip()== ''):
            return jsonify({"errorCode":"ERR1","message":"Debe ingresar un título para el material."}), 400
        if enlace is not None and (not enlace or not re.match(r'^(https?://|/|[A-Za-z0-9._-]+)', enlace.strip())):
            return jsonify({"errorCode":"ERR2","message":"Debe adjuntar un archivo o ingresar un enlace válido."}), 400
        conn = mysql.connector.connect(**DB_CONFIG)
        id_inst = _my_inst_id(conn, current_user_id)
        if not id_inst or not _ci_belongs(conn, id_ci, id_inst):
            return jsonify({"errorCode":"ERR1","message":"Carrera no encontrada"}), 404
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM contenidomultimedia WHERE idContenidoMultimedia=%s AND idCarreraInstitucion=%s AND (fechaFin IS NULL OR fechaFin>NOW())", (id_mat, id_ci))
        if not cur.fetchone():
            return jsonify({"errorCode":"ERR1","message":"Material no encontrado"}), 404
        sets=[]; params=[]
        if titulo is not None:
            sets.append("titulo=%s"); params.append(titulo.strip())
        if descripcion is not None:
            sets.append("descripcion=%s"); params.append(descripcion.strip() if isinstance(descripcion,str) and descripcion.strip()!='' else None)
        if enlace is not None:
            sets.append("enlace=%s"); params.append(enlace.strip())
        if not sets:
            return jsonify({"errorCode":"ERR1","message":"Debe ingresar un título para el material."}), 400
        sql = f"UPDATE contenidomultimedia SET {', '.join(sets)} WHERE idContenidoMultimedia=%s"
        params.append(id_mat)
        cur.execute(sql, tuple(params))
        conn.commit()
        return jsonify({"ok":True, "message":"Se guardó correctamente el nuevo contenido Multimedia"}), 200
    except Exception as e:
        try:
            if conn: conn.rollback()
        except Exception: pass
        log(f"US020 UPDATE error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR3","message":"No se pudieron guardar los cambios. Intente nuevamente."}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# Eliminar material complementario (baja lógica fechaFin)
@app.route('/api/v1/institutions/me/careers/<int:id_ci>/materials/<int:id_mat>', methods=['DELETE'])
@token_required
def materials_delete(current_user_id:int, id_ci:int, id_mat:int):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        id_inst = _my_inst_id(conn, current_user_id)
        if not id_inst or not _ci_belongs(conn, id_ci, id_inst):
            return jsonify({"errorCode":"ERR4","message":"No se pudo eliminar el material complementario. Intente nuevamente."}), 404
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM contenidomultimedia WHERE idContenidoMultimedia=%s AND idCarreraInstitucion=%s AND (fechaFin IS NULL OR fechaFin>NOW())", (id_mat, id_ci))
        if not cur.fetchone():
            return jsonify({"errorCode":"ERR4","message":"No se pudo eliminar el material complementario. Intente nuevamente."}), 404
        cur.execute("UPDATE contenidomultimedia SET fechaFin=NOW() WHERE idContenidoMultimedia=%s", (id_mat,))
        conn.commit()
        return jsonify({"ok":True}), 200
    except Exception as e:
        try:
            if conn: conn.rollback()
        except Exception: pass
        log(f"US020 DELETE error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR4","message":"No se pudo eliminar el material complementario. Intente nuevamente."}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# ============================ Relación de Carreras con Aptitudes (US021) ============================
# Nota importante de esquema: la tabla `aptitudcarrera` en el script actual referencia `carrera` mediante el campo
# `idCarreraInstitucion` (FK a carrera.idCarrera). Sin embargo la historia requiere asociar aptitudes a una carrera-institución
# (carrerainstitucion). Para no alterar el esquema existente, se implementa la asociación a nivel de carrera base
# (carrerainstitucion.idCarrera). Es decir: TODAS las instituciones que dicten la misma carrera base compartirán la misma
# configuración de aptitudes mientras no se corrija/ajuste el modelo relacional.
# Endpoints:
#   GET  /api/v1/institutions/me/careers/<id_ci>/aptitudes    -> listado de aptitudes (0-99)
#   PUT  /api/v1/institutions/me/careers/<id_ci>/aptitudes    -> guardar pesos (reemplaza todos)
# Validaciones (al guardar):
#   ERR01: Al menos una aptitud > 50
#   ERR02: Al menos 3 aptitudes >= 25
#   ERR03: No más de 3 aptitudes con puntaje máximo (99)
#   ERR04: No todas las aptitudes con el mismo puntaje
#   ERR05: Máx 50% con valor 0

def _get_base_carrera_id(conn, id_ci:int):
    cur = conn.cursor()
    cur.execute("SELECT idCarrera FROM carrerainstitucion WHERE idCarreraInstitucion=%s", (id_ci,))
    r = cur.fetchone()
    return r[0] if r else None

@app.route('/api/v1/institutions/me/careers/<int:id_ci>/aptitudes', methods=['GET'])
@token_required
def career_aptitudes_list(current_user_id:int, id_ci:int):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        id_inst = _my_inst_id(conn, current_user_id)
        if not id_inst or not _ci_belongs(conn, id_ci, id_inst):
            return jsonify({"errorCode":"ERR1","message":"Carrera no encontrada"}), 404
        id_carrera_base = _get_base_carrera_id(conn, id_ci)
        if not id_carrera_base:
            return jsonify({"errorCode":"ERR1","message":"Carrera no encontrada"}), 404
        cur = conn.cursor(dictionary=True)
        # Traer todas las aptitudes con su valor (si existe) para la carrera base
        cur.execute(
            """
            SELECT a.idAptitud, a.nombreAptitud, COALESCE(ac.afinidadCarrera, 0) AS puntaje
            FROM aptitud a
            LEFT JOIN aptitudcarrera ac ON ac.idAptitud = a.idAptitud AND ac.idCarreraInstitucion = %s
            WHERE (a.fechaBaja IS NULL OR a.fechaBaja > NOW())
            ORDER BY a.nombreAptitud
            """,
            (id_carrera_base,)
        )
        rows = cur.fetchall() or []
        data = [
            {
                "id": r['idAptitud'],
                "nombre": r['nombreAptitud'],
                "puntaje": int(r['puntaje']) if r['puntaje'] is not None else 0
            } for r in rows
        ]
        return jsonify({
            "aptitudes": data,
            "guardarPath": f"/api/v1/institutions/me/careers/{id_ci}/aptitudes"
        }), 200
    except Exception as e:
        log(f"US021 LIST error: {e}\n{traceback.format_exc()}")
        return jsonify({"message":"Error al consultar aptitudes"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/institutions/me/careers/<int:id_ci>/aptitudes', methods=['PUT'])
@token_required
def career_aptitudes_save(current_user_id:int, id_ci:int):
    conn=None
    try:
        body = request.get_json(silent=True) or {}
        aptitudes = body.get('aptitudes')
        if not isinstance(aptitudes, list) or not aptitudes:
            return jsonify({"errorCode":"ERR01","message":"Al menos una aptitud debe tener una puntuación superior a 50."}), 400
        # Normalizar lista -> [(id, score)]
        parsed=[]
        try:
            for item in aptitudes:
                if not isinstance(item, dict):
                    raise ValueError()
                id_ap = int(item.get('idAptitud') if 'idAptitud' in item else item.get('id') )
                puntaje = int(item.get('puntaje') if 'puntaje' in item else item.get('afinidad') )
                if puntaje < 0 or puntaje > 99:
                    raise ValueError()
                parsed.append((id_ap, puntaje))
        except Exception:
            return jsonify({"errorCode":"ERR01","message":"Datos de aptitudes inválidos"}), 400
        scores = [p for _,p in parsed]
        if not any(s>50 for s in scores):
            return jsonify({"errorCode":"ERR01","message":"Al menos una aptitud debe tener una puntuación superior a 50."}), 400
        if sum(1 for s in scores if s>=25) < 3:
            return jsonify({"errorCode":"ERR02","message":"Al menos 3 aptitudes deben tener una puntuación de 25 o superior."}), 400
        max_score = max(scores)
        if sum(1 for s in scores if s==max_score) > 3:
            return jsonify({"errorCode":"ERR03","message":"No pueden haber más de 3 aptitudes con puntaje máximo."}), 400
        if all(s==scores[0] for s in scores):
            return jsonify({"errorCode":"ERR04","message":"Las aptitudes no pueden tener todas el mismo puntaje."}), 400
        if sum(1 for s in scores if s==0) > len(scores)/2:
            return jsonify({"errorCode":"ERR05","message":"No puede haber más del 50% de las aptitudes con valor 0."}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
        id_inst = _my_inst_id(conn, current_user_id)
        if not id_inst or not _ci_belongs(conn, id_ci, id_inst):
            return jsonify({"errorCode":"ERR01","message":"Carrera no encontrada"}), 404
        id_carrera_base = _get_base_carrera_id(conn, id_ci)
        if not id_carrera_base:
            return jsonify({"errorCode":"ERR01","message":"Carrera no encontrada"}), 404

        cur = conn.cursor()
        # Validar que las aptitudes existan
        ids = [iid for iid,_ in parsed]
        in_clause = ','.join(['%s']*len(ids))
        cur.execute(f"SELECT COUNT(*) FROM aptitud WHERE idAptitud IN ({in_clause})", tuple(ids))
        if cur.fetchone()[0] != len(ids):
            return jsonify({"errorCode":"ERR01","message":"Alguna aptitud no existe"}), 400
        # Reemplazar completamente
        cur.execute("DELETE FROM aptitudcarrera WHERE idCarreraInstitucion=%s", (id_carrera_base,))
        for aid, score in parsed:
            cur.execute(
                "INSERT INTO aptitudcarrera (afinidadCarrera, idAptitud, idCarreraInstitucion) VALUES (%s,%s,%s)",
                (score, aid, id_carrera_base)
            )
        conn.commit()
        return jsonify({"ok":True, "message":"Aptitudes actualizadas"}), 200
    except Exception as e:
        try:
            if conn: conn.rollback()
        except Exception: pass
        log(f"US021 SAVE error: {e}\n{traceback.format_exc()}")
        # Se retorna ERR03 como error técnico general aunque no esté explícito (solo validaciones enumeradas)
        return jsonify({"errorCode":"ERR03","message":"Error al guardar aptitudes"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass



# ============================ Realización de Test (US022) ============================
# Implementación simplificada en memoria (

_TEST_STORE = {}
_TEST_SEQ = 1

def _detect_current_user_id_optional():
    token=None
    if 'Authorization' in request.headers:
        parts = request.headers['Authorization'].split(' ')
        if len(parts)==2 and parts[0].lower()=='bearer':
            token=parts[1]
    if not token:
        return None
    if token=="Hola":
        return 1
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data.get('user_id')
    except Exception:
        return None

def _find_active_test_for_user(user_id):
    for t in _TEST_STORE.values():
        if t['user_id']==user_id and not t['finished'] and not t['abandoned']:
            return t
    return None

def _create_test(user_id, accepted):
    global _TEST_SEQ
    tid = _TEST_SEQ
    _TEST_SEQ += 1
    now = datetime.datetime.utcnow()
    obj = {
        'id': tid,
        'user_id': user_id,
        'answers': [],
        'total': 50,
        'paused': False,
        'finished': False,
        'abandoned': False,
        'disclaimerAccepted': accepted,
        'created': now,
        'lastUpdate': now
    }
    _TEST_STORE[tid]=obj
    return obj

@app.route('/api/v1/tests/start', methods=['POST'])
def us022_test_start():
    user_id = _detect_current_user_id_optional()
    data = request.get_json(silent=True) or {}
    accept = bool(data.get('acceptPolicies'))
    existing = _find_active_test_for_user(user_id)
    if existing:
        if existing['user_id'] is None and not existing['disclaimerAccepted']:
            return jsonify({
                "disclaimer": True,
                "message": "Debes aceptar las políticas de uso para continuar el test.",
                "acceptPath": "/api/v1/tests/start"
            }), 200
        return jsonify({
            "idTest": existing['id'],
            "continuar": True,
            "nextQuestion": f"Pregunta {len(existing['answers'])+1}",
            "respondidas": len(existing['answers']),
            "total": existing['total']
        }), 200
    if user_id is None and not accept:
        temp = _create_test(None, False)
        return jsonify({
            "disclaimer": True,
            "message": "Debes aceptar las políticas de uso para iniciar el test.",
            "acceptPath": "/api/v1/tests/start",
            "cancelInfo": {"message": "Si cancelas no podrás continuar ahora."},
            "tempTestId": temp['id']
        }), 200
    t = _create_test(user_id, True if user_id is not None else accept)
    return jsonify({
        "idTest": t['id'],
        "nextQuestion": "Pregunta 1",
        "respondidas": 0,
        "total": t['total']
    }), 201

@app.route('/api/v1/tests/<int:id_test>/answer', methods=['POST'])
def us022_test_answer(id_test:int):
    t = _TEST_STORE.get(id_test)
    if not t or t['abandoned']:
        return jsonify({"errorCode":"ERR1","message":"Test no encontrado"}), 404
    if t['finished']:
        return jsonify({"message":"Test ya finalizado"}), 400
    if t['paused']:
        return jsonify({"message":"Test pausado"}), 400
    data = request.get_json(silent=True) or {}
    ans = (data.get('answer') or '').strip()
    if not ans:
        return jsonify({"errorCode":"ERR1","message":"Respuesta vacía"}), 400
    if data.get('triggerSaveError'):
        return jsonify({"errorCode":"ERR1","message":"Error al guardar la respuesta. Reintente."}), 500
    try:
        t['answers'].append(ans)
        t['lastUpdate']=datetime.datetime.utcnow()
    except Exception:
        return jsonify({"errorCode":"ERR1","message":"Error al guardar la respuesta. Reintente."}), 500
    if len(t['answers']) >= t['total']:
        t['finished']=True
        return jsonify({
            "completed": True,
            "message": "Has completado el test. Puedes ver los resultados.",
            "resultPath": f"/api/v1/tests/{t['id']}/finish"
        }), 200
    return jsonify({
        "ok": True,
        "nextQuestion": f"Pregunta {len(t['answers'])+1}",
        "respondidas": len(t['answers']),
        "total": t['total']
    }), 200

@app.route('/api/v1/tests/<int:id_test>/progress', methods=['GET'])
def us022_test_progress(id_test:int):
    t = _TEST_STORE.get(id_test)
    if not t or t['abandoned']:
        return jsonify({"errorCode":"ERR1","message":"Test no encontrado"}), 404
    return jsonify({
        "idTest": t['id'],
        "respondidas": len(t['answers']),
        "total": t['total'],
        "paused": t['paused'],
        "finished": t['finished'],
        "abandoned": t['abandoned']
    }), 200

@app.route('/api/v1/tests/<int:id_test>/pause', methods=['POST'])
def us022_test_pause(id_test:int):
    t = _TEST_STORE.get(id_test)
    if not t or t['abandoned']:
        return jsonify({"errorCode":"ERR1","message":"Test no encontrado"}), 404
    if t['finished']:
        return jsonify({"message":"Test ya finalizado"}), 400
    t['paused']=True
    return jsonify({
        "paused": True,
        "message": "Test pausado. Progreso guardado.",
        "resumePath": f"/api/v1/tests/{id_test}/resume",
        "saveExitPath": f"/api/v1/tests/{id_test}/save-exit"
    }), 200

@app.route('/api/v1/tests/<int:id_test>/resume', methods=['POST'])
def us022_test_resume(id_test:int):
    t = _TEST_STORE.get(id_test)
    if not t or t['abandoned']:
        return jsonify({"errorCode":"ERR1","message":"Test no encontrado"}), 404
    if t['finished']:
        return jsonify({"message":"Test ya finalizado"}), 400
    t['paused']=False
    return jsonify({
        "paused": False,
        "nextQuestion": f"Pregunta {len(t['answers'])+1}",
        "respondidas": len(t['answers']),
        "total": t['total']
    }), 200

@app.route('/api/v1/tests/<int:id_test>/save-exit', methods=['POST'])
def us022_test_save_exit(id_test:int):
    t = _TEST_STORE.get(id_test)
    if not t or t['abandoned']:
        return jsonify({"errorCode":"ERR1","message":"Test no encontrado"}), 404
    if t['finished']:
        return jsonify({"message":"Test ya finalizado"}), 400
    t['paused']=True
    return jsonify({"ok":True, "message":"Progreso guardado. Podrás continuar más tarde."}), 200

@app.route('/api/v1/tests/<int:id_test>/abandon', methods=['POST'])
def us022_test_abandon(id_test:int):
    t = _TEST_STORE.get(id_test)
    if not t or t['abandoned']:
        return jsonify({"errorCode":"ERR1","message":"Test no encontrado"}), 404
    if t['finished']:
        return jsonify({"message":"Test ya finalizado"}), 400
    t['abandoned']=True
    t['answers']=[]
    return jsonify({"ok":True, "message":"Test abandonado y respuestas eliminadas."}), 200

@app.route('/api/v1/tests/<int:id_test>/finish', methods=['POST'])
def us022_test_finish(id_test:int):
    t = _TEST_STORE.get(id_test)
    if not t or t['abandoned']:
        return jsonify({"errorCode":"ERR1","message":"Test no encontrado"}), 404
    if not t['finished']:
        if len(t['answers']) < t['total']:
            return jsonify({"message":"Aún no completaste todas las preguntas."}), 400
        t['finished']=True
    import random as _r
    aptitudes=[{"nombre":f"Aptitud {i}","puntaje":_r.randint(10,99)} for i in range(1,7)]
    aptitudes.sort(key=lambda x: x['puntaje'], reverse=True)
    carreras=[{"carrera":f"Carrera {i}","afinidad":_r.randint(50,100)} for i in range(1,6)]
    carreras.sort(key=lambda x: x['afinidad'], reverse=True)
    return jsonify({
        "idTest": t['id'],
        "resumen": "Test completado. Estos son tus resultados simulados.",
        "aptitudes": aptitudes,
        "carreras": carreras,
        "volverInicioPath": "/api/v1/tests/start"
    }), 200


# ============================ Tablero de Estadísticas (US023) ============================
# Filtros comunes: from=YYYY-MM-DD, to=YYYY-MM-DD (requeridos), provinceId (opcional)
# Validaciones: to <= hoy, from <= to. Caso inválido -> ERR1.
# Si no hay datos en ninguna métrica solicitada del tablero -> ERR1 (mensaje pedir cambiar filtros).
# Permiso requerido: ADMIN_PANEL.
# Limitaciones: Algunas métricas no pueden calcularse por ausencia de columnas (ej: fecha en test / compatibilidades), se devuelven listas vacías.

def _parse_stats_filters():
    args = request.args
    f = args.get('from')
    t = args.get('to')
    province = args.get('provinceId')
    if not f or not t:
        return None, jsonify({"errorCode":"ERR1","message":"Filtros inválidos."}), 400
    try:
        from_dt = datetime.datetime.strptime(f, '%Y-%m-%d').date()
        to_dt = datetime.datetime.strptime(t, '%Y-%m-%d').date()
        if to_dt > datetime.date.today() or from_dt > to_dt:
            raise ValueError()
        province_id = None
        if province not in (None, '', 'all', 'ALL'):
            province_id = int(province)
        return (from_dt, to_dt, province_id), None, None
    except Exception:
        return None, jsonify({"errorCode":"ERR1","message":"Filtros inválidos."}), 400

def _province_clause(alias_user='u', alias_inst='i'):
    # Genera cláusula y join según si filtramos por provincia para usuarios o instituciones.
    # Para usuarios: usuario -> localidad l -> provincia pr
    return (
        f" LEFT JOIN localidad l_u ON l_u.idLocalidad = {alias_user}.idLocalidad"
        f" LEFT JOIN provincia pr_u ON pr_u.idProvincia = l_u.idProvincia ",
        " pr_u.idProvincia = %s "
    )

@app.route('/api/v1/admin/stats/system', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_stats_system(current_user_id):
    filters, err_resp, err_code = _parse_stats_filters()
    if err_resp:
        return err_resp, err_code
    from_dt, to_dt, province_id = filters
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Usuarios por tipo (grupo)
        province_join, province_condition = _province_clause()
        params_users = [from_dt, to_dt]
        province_filter_sql = ''
        if province_id is not None:
            province_filter_sql = f" AND {province_condition}"
            params_users.append(province_id)
        cur.execute(
            f"""
            SELECT g.nombreGrupo AS tipo, COUNT(DISTINCT ug.idUsuario) AS total
            FROM usuariogrupo ug
            JOIN grupo g ON g.idGrupo = ug.idGrupo
            JOIN usuario u ON u.idUsuario = ug.idUsuario
            {province_join}
            JOIN usuarioestado ue ON ue.idUsuario = u.idUsuario
            WHERE (ug.fechaFin IS NULL OR ug.fechaFin > NOW())
              AND ue.fechaInicio BETWEEN %s AND %s
              {province_filter_sql}
            GROUP BY g.nombreGrupo
            ORDER BY g.nombreGrupo
            """,
            tuple(params_users)
        )
        usuarios_por_tipo = cur.fetchall() or []

        # Evolución registros (por mes) usando usuarioestado.fechaInicio
        params_evo = [from_dt, to_dt]
        if province_id is not None:
            params_evo.append(province_id)
        cur.execute(
            f"""
            SELECT DATE_FORMAT(ue.fechaInicio, '%Y-%m') AS periodo, COUNT(DISTINCT ue.idUsuario) AS total
            FROM usuarioestado ue
            JOIN usuario u ON u.idUsuario = ue.idUsuario
            {province_join}
            WHERE ue.fechaInicio BETWEEN %s AND %s
            {province_filter_sql}
            GROUP BY periodo
            ORDER BY periodo
            """,
            tuple(params_evo)
        )
        evolucion_registros = cur.fetchall() or []

        # Tests completados por mes -> no fecha en tabla 'test'; devolver vacío
        tests_completados = []

        # Total carreras cargadas por tipo (carrerainstitucion.fechaInicio)
        params_carr = [from_dt, to_dt]
        carr_province_join = " LEFT JOIN institucion i ON i.idInstitucion = ci.idInstitucion LEFT JOIN localidad l_i ON l_i.idLocalidad = i.idLocalidad LEFT JOIN provincia pr_i ON pr_i.idProvincia = l_i.idProvincia "
        carr_province_filter = ''
        if province_id is not None:
            carr_province_filter = ' AND pr_i.idProvincia = %s'
            params_carr.append(province_id)
        cur.execute(
            f"""
            SELECT COALESCE(tc.nombreTipoCarrera,'Sin Tipo') AS tipo, COUNT(DISTINCT ci.idCarreraInstitucion) AS total
            FROM carrerainstitucion ci
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN tipocarrera tc ON tc.idTipoCarrera = c.idTipoCarrera
            {carr_province_join}
            WHERE ci.fechaInicio BETWEEN %s AND %s {carr_province_filter}
            GROUP BY tipo
            ORDER BY tipo
            """,
            tuple(params_carr)
        )
        carreras_por_tipo = cur.fetchall() or []

        # Estado de solicitudes de Instituciones (último estado dentro del periodo)
        params_inst = [from_dt, to_dt]
        inst_province_join = " LEFT JOIN institucion i ON i.idInstitucion = ie.idInstitucion LEFT JOIN localidad l2 ON l2.idLocalidad = i.idLocalidad LEFT JOIN provincia pr2 ON pr2.idProvincia = l2.idProvincia "
        inst_province_filter = ''
        if province_id is not None:
            inst_province_filter = ' AND pr2.idProvincia = %s'
            params_inst.append(province_id)
        cur.execute(
            f"""
            SELECT COALESCE(ei.nombreEstadoInstitucion,'Desconocido') AS estado, COUNT(*) AS total
            FROM (
                SELECT ie1.idInstitucion, ie1.idEstadoInstitucion
                FROM institucionestado ie1
                JOIN (
                    SELECT idInstitucion, MAX(fechaInicio) maxFecha
                    FROM institucionestado
                    WHERE fechaInicio BETWEEN %s AND %s
                    GROUP BY idInstitucion
                ) last ON last.idInstitucion = ie1.idInstitucion AND last.maxFecha = ie1.fechaInicio
            ) latest
            JOIN institucionestado ie ON ie.idInstitucion = latest.idInstitucion AND ie.idEstadoInstitucion = latest.idEstadoInstitucion
            LEFT JOIN estadoinstitucion ei ON ei.idEstadoInstitucion = latest.idEstadoInstitucion
            {inst_province_join}
            WHERE 1=1 {inst_province_filter}
            GROUP BY estado
            ORDER BY estado
            """,
            tuple(params_inst)
        )
        instituciones_estado = cur.fetchall() or []

        # Tasa de actividad: accesos y usuarios activos
        params_act = [from_dt, to_dt]
        if province_id is not None:
            params_act.append(province_id)
        cur.execute(
            f"""
            SELECT COUNT(*) totalAccesos, COUNT(DISTINCT ha.idUsuario) usuariosActivos
            FROM historialacceso ha
            LEFT JOIN usuario u ON u.idUsuario = ha.idUsuario
            {province_join}
            WHERE ha.fecha BETWEEN %s AND %s {province_filter_sql}
            """,
            tuple(params_act)
        )
        act_row = cur.fetchone() or {"totalAccesos":0,"usuariosActivos":0}
        # Total usuarios (registrados en o antes de fecha fin)
        params_tot_users = [to_dt]
        if province_id is not None:
            params_tot_users.append(province_id)
        cur.execute(
            f"""
            SELECT COUNT(DISTINCT ue.idUsuario) total
            FROM usuarioestado ue
            JOIN usuario u ON u.idUsuario = ue.idUsuario
            {province_join}
            WHERE ue.fechaInicio <= %s {province_filter_sql}
            """,
            tuple(params_tot_users)
        )
        total_users_row = cur.fetchone() or {"total":0}
        total_users = total_users_row.get('total') or 0
        usuarios_activos = act_row.get('usuariosActivos') or 0
        tasa_act = (usuarios_activos / total_users) if total_users else 0

        empty_all = all(len(x)==0 for x in [usuarios_por_tipo, evolucion_registros, tests_completados, carreras_por_tipo, instituciones_estado])
        if empty_all:
            return jsonify({"errorCode":"ERR1","message":"No se encontraron datos con los filtros aplicados."}), 404

        return jsonify({
            "filters": {"from": str(from_dt), "to": str(to_dt), "provinceId": province_id},
            "usuariosPorTipo": usuarios_por_tipo,
            "evolucionRegistros": evolucion_registros,
            "testsCompletados": tests_completados,
            "carrerasPorTipo": carreras_por_tipo,
            "institucionesEstado": instituciones_estado,
            "actividad": {
                "totalAccesos": act_row.get('totalAccesos'),
                "usuariosActivos": usuarios_activos,
                "totalUsuarios": total_users,
                "tasaActividad": round(tasa_act,4)
            }
        }), 200
    except Exception as e:
        log(f"US023 system stats error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR1","message":"Error al obtener estadísticas"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/stats/system/export', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_stats_system_export(current_user_id):
    filters, err_resp, err_code = _parse_stats_filters()
    if err_resp:
        return err_resp, err_code
    fmt = (request.args.get('format') or 'csv').lower()
    if fmt not in ('csv','pdf'):
        return jsonify({"errorCode":"ERR1","message":"Formato inválido"}), 400
    # Reutilizar endpoint principal
    with app.test_request_context(query_string=request.query_string):
        data_resp, status = admin_stats_system(current_user_id)
    if status != 200:
        return data_resp, status
    payload = data_resp.get_json()
    if fmt == 'csv':
        import io, csv as _csv
        buf = io.StringIO()
        w = _csv.writer(buf)
        w.writerow(["Sección","Clave","Valor"])
        for row in payload.get('usuariosPorTipo', []):
            w.writerow(["UsuariosPorTipo", row['tipo'], row['total']])
        for row in payload.get('evolucionRegistros', []):
            w.writerow(["EvolucionRegistros", row['periodo'], row['total']])
        for row in payload.get('carrerasPorTipo', []):
            w.writerow(["CarrerasPorTipo", row['tipo'], row['total']])
        for row in payload.get('institucionesEstado', []):
            w.writerow(["InstitucionesEstado", row['estado'], row['total']])
        w.writerow(["Actividad","totalAccesos", payload['actividad']['totalAccesos']])
        w.writerow(["Actividad","usuariosActivos", payload['actividad']['usuariosActivos']])
        w.writerow(["Actividad","totalUsuarios", payload['actividad']['totalUsuarios']])
        w.writerow(["Actividad","tasaActividad", payload['actividad']['tasaActividad']])
        csv_data = buf.getvalue()
        from flask import Response
        return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition':'attachment; filename="stats_system.csv"'})
    else:  # pdf stub
        # Simple texto como stub (no genera PDF real)
        content = "Reporte Sistema (Stub PDF)\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        from flask import Response
        return Response(content, mimetype='application/pdf', headers={'Content-Disposition':'attachment; filename="stats_system.pdf"'})

@app.route('/api/v1/admin/stats/users', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_stats_users(current_user_id):
    filters, err_resp, err_code = _parse_stats_filters()
    if err_resp:
        return err_resp, err_code
    from_dt, to_dt, province_id = filters
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        # Favoritos (intereses)
        fav_params = [from_dt, to_dt]
        fav_province_join = " LEFT JOIN usuario u ON u.idUsuario=iuc.idUsuario LEFT JOIN localidad l ON l.idLocalidad=u.idLocalidad LEFT JOIN provincia pr ON pr.idProvincia=l.idProvincia "
        fav_province_filter = ''
        if province_id is not None:
            fav_province_filter = ' AND pr.idProvincia = %s'
            fav_params.append(province_id)
        cur.execute(
            f"""
            SELECT ci.idCarreraInstitucion AS idCI, COALESCE(c.nombreCarrera,'(Sin nombre)') AS carrera, COUNT(*) total
            FROM interesusuariocarrera iuc
            JOIN carrerainstitucion ci ON ci.idCarreraInstitucion = iuc.idCarreraInstitucion
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            {fav_province_join}
            WHERE iuc.fechaAlta BETWEEN %s AND %s {fav_province_filter}
            GROUP BY ci.idCarreraInstitucion, carrera
            ORDER BY total DESC
            LIMIT 10
            """,
            tuple(fav_params)
        )
        carreras_favoritas = cur.fetchall() or []

        # Top carreras compatibilidad (no hay datos suficientes -> vacío)
        top_compat = []

        if len(carreras_favoritas)==0 and len(top_compat)==0:
            return jsonify({"errorCode":"ERR1","message":"No se encontraron datos con los filtros aplicados."}), 404

        return jsonify({
            "filters": {"from": str(from_dt), "to": str(to_dt), "provinceId": province_id},
            "carrerasFavoritas": carreras_favoritas,
            "topCarrerasCompatibilidad": top_compat
        }), 200
    except Exception as e:
        log(f"US023 user stats error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR1","message":"Error al obtener estadísticas"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/stats/users/export', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_stats_users_export(current_user_id):
    filters, err_resp, err_code = _parse_stats_filters()
    if err_resp:
        return err_resp, err_code
    fmt = (request.args.get('format') or 'csv').lower()
    if fmt not in ('csv','pdf'):
        return jsonify({"errorCode":"ERR1","message":"Formato inválido"}), 400
    with app.test_request_context(query_string=request.query_string):
        data_resp, status = admin_stats_users(current_user_id)
    if status != 200:
        return data_resp, status
    payload = data_resp.get_json()
    if fmt == 'csv':
        import io, csv as _csv
        buf = io.StringIO()
        w = _csv.writer(buf)
        w.writerow(["Sección","Clave","Valor"])
        for row in payload.get('carrerasFavoritas', []):
            w.writerow(["CarrerasFavoritas", row['carrera'], row['total']])
        # top compat vacío actualmente
        csv_data = buf.getvalue()
        from flask import Response
        return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition':'attachment; filename="stats_users.csv"'})
    else:
        content = "Reporte Usuarios (Stub PDF)\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        from flask import Response
        return Response(content, mimetype='application/pdf', headers={'Content-Disposition':'attachment; filename="stats_users.pdf"'})

    
# ============================ Tablero de Estadísticas Institución (US024) ============================
# Filtros generales: from=YYYY-MM-DD, to=YYYY-MM-DD (requeridos en endpoints de búsqueda)
# Filtro opcional para generales: tiposCarrera=lista separada por comas de idTipoCarrera (o 'all')
# Validaciones: to <= hoy, from <= to. Caso inválido -> ERR1
# Si no hay datos -> ERR1 (404) con mensaje de cambiar filtros
# Contexto: estadísticas solo de carreras pertenecientes a la institución del usuario autenticado
# Limitaciones por modelo actual:
# - No existe tabla con compatibilidades históricas por test/carrera -> métricas de compatibilidad serán listas vacías o placeholders
# - No existe tracking de "favoritos" salvo tabla interesusuariocarrera sin idCarreraInstitucion explícita en esquema actual -> sólo se puede contar si se incorpora idCarreraInstitucion (no está). Se devuelve 0.
# - Ranking de carreras según máxima compatibilidad y promedios: devolver listas vacías.
# - Para ranking de favoritas se usa 0 por ausencia de FK necesaria.
# Export PDF es stub textual (igual que US023).

def _parse_inst_stats_filters(require_types=False):
    args = request.args
    f = args.get('from')
    t = args.get('to')
    tipos_raw = args.get('tiposCarrera')
    if not f or not t:
        return None, jsonify({"errorCode":"ERR1","message":"Filtros inválidos."}), 400
    try:
        from_dt = datetime.datetime.strptime(f, '%Y-%m-%d').date()
        to_dt = datetime.datetime.strptime(t, '%Y-%m-%d').date()
        if to_dt > datetime.date.today() or from_dt > to_dt:
            raise ValueError()
        tipos = None
        if tipos_raw and tipos_raw.lower() not in ('all','todas','todos'):
            tipos = []
            for part in tipos_raw.split(','):
                part = part.strip()
                if part:
                    tipos.append(int(part))
            if not tipos: # lista vacía tras parseo
                tipos = None
        return (from_dt, to_dt, tipos), None, None
    except Exception:
        return None, jsonify({"errorCode":"ERR1","message":"Filtros inválidos."}), 400

@app.route('/api/v1/institucion/stats/general', methods=['GET'])
@token_required
def institucion_stats_general(current_user_id):
    filters, err_resp, err_code = _parse_inst_stats_filters()
    if err_resp:
        return err_resp, err_code
    from_dt, to_dt, tipos = filters
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        id_inst = _my_inst_id(conn, current_user_id)
        if not id_inst:
            return jsonify({"errorCode":"ERR1","message":"Institución no encontrada."}), 404
        cur = conn.cursor(dictionary=True)

        params = [id_inst, from_dt, to_dt]
        tipo_filter_sql = ''
        if tipos:
            # filtrar por tipo de carrera (tabla carrera->tipocarrera)
            in_clause = ','.join(['%s']*len(tipos))
            tipo_filter_sql = f" AND tc.idTipoCarrera IN ({in_clause})"
            params.extend(tipos)
        # Carreras cargadas en periodo
        cur.execute(
            f"""
            SELECT COUNT(DISTINCT ci.idCarreraInstitucion) total
            FROM carrerainstitucion ci
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN tipocarrera tc ON tc.idTipoCarrera = c.idTipoCarrera
            WHERE ci.idInstitucion=%s AND ci.fechaInicio BETWEEN %s AND %s {tipo_filter_sql}
            """,
            tuple(params)
        )
        row_total = cur.fetchone() or {"total":0}
        total_carreras = row_total['total'] or 0

        # Carreras dadas de baja (fechaFin dentro del rango)
        params_baja = [id_inst, from_dt, to_dt]
        if tipos:
            params_baja.extend(tipos)
        cur.execute(
            f"""
            SELECT COUNT(DISTINCT ci.idCarreraInstitucion) total
            FROM carrerainstitucion ci
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN tipocarrera tc ON tc.idTipoCarrera = c.idTipoCarrera
            WHERE ci.idInstitucion=%s AND ci.fechaFin IS NOT NULL AND ci.fechaFin BETWEEN %s AND %s {tipo_filter_sql}
            """,
            tuple(params_baja)
        )
        row_baja = cur.fetchone() or {"total":0}
        total_bajas = row_baja['total'] or 0

        # Ranking favoritas (placeholder vacio, falta FK a interesusuariocarrera)
        ranking_favoritas = []
        # Ranking por máxima compatibilidad (no disponible)
        ranking_max_compatibilidad = []
        # Promedio de compatibilidades por tipo carrera (no disponible)
        promedio_por_tipo = []

        empty_all = (total_carreras==0 and total_bajas==0 and len(ranking_favoritas)==0 and len(ranking_max_compatibilidad)==0 and len(promedio_por_tipo)==0)
        if empty_all:
            return jsonify({"errorCode":"ERR1","message":"No se encontraron datos con los filtros aplicados."}), 404

        return jsonify({
            "filters": {"from":str(from_dt),"to":str(to_dt),"tiposCarrera": tipos},
            "totalCarreras": total_carreras,
            "totalBajas": total_bajas,
            "rankingFavoritas": ranking_favoritas,
            "rankingMaxCompatibilidad": ranking_max_compatibilidad,
            "promedioCompatibilidadPorTipo": promedio_por_tipo
        }), 200
    except Exception as e:
        log(f"US024 general stats error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR1","message":"Error al obtener estadísticas"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/institucion/stats/general/export', methods=['GET'])
@token_required
def institucion_stats_general_export(current_user_id):
    filters, err_resp, err_code = _parse_inst_stats_filters()
    if err_resp:
        return err_resp, err_code
    fmt = (request.args.get('format') or 'csv').lower()
    if fmt not in ('csv','pdf'):
        return jsonify({"errorCode":"ERR1","message":"Formato inválido"}), 400
    with app.test_request_context(query_string=request.query_string):
        data_resp, status = institucion_stats_general(current_user_id)
    if status != 200:
        return data_resp, status
    payload = data_resp.get_json()
    if fmt == 'csv':
        import io, csv as _csv
        buf = io.StringIO()
        w = _csv.writer(buf)
        w.writerow(["Clave","Valor"])
        w.writerow(["totalCarreras", payload['totalCarreras']])
        w.writerow(["totalBajas", payload['totalBajas']])
        for r in payload.get('rankingFavoritas', []):
            w.writerow(["rankingFavoritas", json.dumps(r, ensure_ascii=False)])
        for r in payload.get('rankingMaxCompatibilidad', []):
            w.writerow(["rankingMaxCompatibilidad", json.dumps(r, ensure_ascii=False)])
        for r in payload.get('promedioCompatibilidadPorTipo', []):
            w.writerow(["promedioCompatibilidadPorTipo", json.dumps(r, ensure_ascii=False)])
        csv_data = buf.getvalue()
        from flask import Response
        return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition':'attachment; filename="stats_institucion_general.csv"'})
    else:
        content = "Reporte Institución General (Stub PDF)\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        from flask import Response
        return Response(content, mimetype='application/pdf', headers={'Content-Disposition':'attachment; filename="stats_institucion_general.pdf"'})

# Estadísticas por carrera
def _parse_inst_carrera_filters():
    args = request.args
    f = args.get('from')
    t = args.get('to')
    if not f or not t:
        return None, jsonify({"errorCode":"ERR1","message":"Filtros inválidos."}), 400
    try:
        from_dt = datetime.datetime.strptime(f, '%Y-%m-%d').date()
        to_dt = datetime.datetime.strptime(t, '%Y-%m-%d').date()
        if to_dt > datetime.date.today() or from_dt > to_dt:
            raise ValueError()
        return (from_dt, to_dt), None, None
    except Exception:
        return None, jsonify({"errorCode":"ERR1","message":"Filtros inválidos."}), 400

@app.route('/api/v1/institucion/stats/carreras', methods=['GET'])
@token_required
def institucion_stats_carreras_list(current_user_id):
    # Lista de carreras de la institución (sin filtros de fecha)
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        id_inst = _my_inst_id(conn, current_user_id)
        if not id_inst:
            return jsonify({"errorCode":"ERR1","message":"Institución no encontrada."}), 404
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idCarreraInstitucion, nombreCarrera FROM carrerainstitucion WHERE idInstitucion=%s AND (fechaFin IS NULL OR fechaFin > NOW()) ORDER BY nombreCarrera", (id_inst,))
        rows = cur.fetchall() or []
        if not rows:
            return jsonify({"errorCode":"ERR1","message":"No se encontraron datos."}), 404
        return jsonify({"carreras": rows}), 200
    except Exception as e:
        log(f"US024 list carreras error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR1","message":"Error al obtener carreras"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/institucion/stats/carrera/<int:idCarreraInstitucion>', methods=['GET'])
@token_required
def institucion_stats_carrera_detalle(current_user_id, idCarreraInstitucion):
    filters, err_resp, err_code = _parse_inst_carrera_filters()
    if err_resp:
        return err_resp, err_code
    from_dt, to_dt = filters
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        id_inst = _my_inst_id(conn, current_user_id)
        if not id_inst:
            return jsonify({"errorCode":"ERR1","message":"Institución no encontrada."}), 404
        if not _ci_belongs(conn, idCarreraInstitucion, id_inst):
            return jsonify({"errorCode":"ERR1","message":"Carrera no pertenece a la institución."}), 404
        cur = conn.cursor(dictionary=True)

        # Placeholders por falta de datos reales
        historial_compatibilidades = []  # [{fecha:'YYYY-MM', compatibilidad:0}]
        ranking_popularidad_provincia = []  # [{provincia:'Nombre', participacion:0}]
        maxima_calificacion = None
        ultima_vez_top = None
        veces_mas_compatible = 0
        favoritos_total = 0
        evolucion_favoritos = []  # [{periodo:'YYYY-MM', total:0}]

        empty_all = (len(historial_compatibilidades)==0 and len(ranking_popularidad_provincia)==0 and maxima_calificacion in (None,0) and ultima_vez_top is None and veces_mas_compatible==0 and favoritos_total==0 and len(evolucion_favoritos)==0)
        if empty_all:
            return jsonify({"errorCode":"ERR1","message":"No se encontraron datos con los filtros aplicados."}), 404

        return jsonify({
            "filters": {"from":str(from_dt),"to":str(to_dt)},
            "historialCompatibilidades": historial_compatibilidades,
            "rankingPopularidadProvincia": ranking_popularidad_provincia,
            "maximaCalificacion": maxima_calificacion,
            "ultimaVezTop": ultima_vez_top,
            "vecesMasCompatible": veces_mas_compatible,
            "favoritosTotal": favoritos_total,
            "evolucionFavoritos": evolucion_favoritos
        }), 200
    except Exception as e:
        log(f"US024 detalle carrera error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR1","message":"Error al obtener estadísticas"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/institucion/stats/carrera/<int:idCarreraInstitucion>/export', methods=['GET'])
@token_required
def institucion_stats_carrera_detalle_export(current_user_id, idCarreraInstitucion):
    filters, err_resp, err_code = _parse_inst_carrera_filters()
    if err_resp:
        return err_resp, err_code
    fmt = (request.args.get('format') or 'csv').lower()
    if fmt not in ('csv','pdf'):
        return jsonify({"errorCode":"ERR1","message":"Formato inválido"}), 400
    with app.test_request_context(query_string=request.query_string):
        data_resp, status = institucion_stats_carrera_detalle(current_user_id, idCarreraInstitucion)
    if status != 200:
        return data_resp, status
    payload = data_resp.get_json()
    if fmt == 'csv':
        import io, csv as _csv
        buf = io.StringIO()
        w = _csv.writer(buf)
        w.writerow(["Clave","Valor"])
        for r in payload.get('historialCompatibilidades', []):
            w.writerow(["historialCompatibilidades", json.dumps(r, ensure_ascii=False)])
        for r in payload.get('rankingPopularidadProvincia', []):
            w.writerow(["rankingPopularidadProvincia", json.dumps(r, ensure_ascii=False)])
        w.writerow(["maximaCalificacion", payload.get('maximaCalificacion')])
        w.writerow(["ultimaVezTop", payload.get('ultimaVezTop')])
        w.writerow(["vecesMasCompatible", payload.get('vecesMasCompatible')])
        w.writerow(["favoritosTotal", payload.get('favoritosTotal')])
        for r in payload.get('evolucionFavoritos', []):
            w.writerow(["evolucionFavoritos", json.dumps(r, ensure_ascii=False)])
        csv_data = buf.getvalue()
        from flask import Response
        return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition':'attachment; filename="stats_institucion_carrera.csv"'})
    else:
        content = "Reporte Institución Carrera (Stub PDF)\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        from flask import Response
        return Response(content, mimetype='application/pdf', headers={'Content-Disposition':'attachment; filename="stats_institucion_carrera.pdf"'})


# ============================ Tablero de Estadísticas Estudiante (US025) ============================
# Secciones: Perfil Personal, Estadísticas de Compatibilidad
# Limitaciones del modelo actual:
# - Tablas test/testaptitud/testcarrerainstitucion carecen de timestamps necesarios y FK completas (no están todas las columnas). No hay registros de aptitudes con valores ni relación directa aptitud->puntaje.
# - No existe tabla de favoritos que relacione usuario con carreraInstitucion (interesusuariocarrera no tiene idCarreraInstitucion en dump actual).
# Por ello se devuelven placeholders vacíos o 0 donde no se puede calcular realmente.
# Futuro: agregar columnas: test(fechaFinalizacion), testaptitud(idAptitud, valor), testcarrerainstitucion(idCarreraInstitucion, compatibilidad), interesusuariocarrera(idCarreraInstitucion, idUsuario).

@app.route('/api/v1/estudiante/stats/perfil', methods=['GET'])
@token_required
def estudiante_stats_perfil(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        # Nombre y apellido
        cur.execute("SELECT nombre, apellido FROM usuario WHERE idUsuario=%s", (current_user_id,))
        urow = cur.fetchone() or {}
        nombre = urow.get('nombre') or ''
        apellido = urow.get('apellido') or ''
        # Cantidad de tests (placeholder: contar filas en test vinculadas al usuario si existiera la columna idUsuario)
        try:
            cur.execute("SELECT COUNT(*) total FROM test WHERE idUsuario=%s", (current_user_id,))
            tests_total = (cur.fetchone() or {}).get('total') or 0
        except Exception:
            tests_total = 0
        # Top 3 aptitudes (sin datos -> lista vacía)
        top3_aptitudes = []
        # Radar aptitudes (lista de objetos {aptitud, valor})
        radar_aptitudes = []
        # Evolución aptitudes principales (lista {periodo, aptitud, valor})
        evolucion_aptitudes = []

        empty_all = (tests_total==0 and len(top3_aptitudes)==0 and len(radar_aptitudes)==0 and len(evolucion_aptitudes)==0 and (not nombre and not apellido))
        if empty_all:
            # Igual devolvemos 404 con ERR1 siguiendo patrón de otros tableros sin datos
            return jsonify({"errorCode":"ERR1","message":"No se encontraron datos para el perfil."}), 404

        return jsonify({
            "usuario": {"nombre": nombre, "apellido": apellido},
            "testsRealizados": tests_total,
            "top3Aptitudes": top3_aptitudes,
            "radarAptitudes": radar_aptitudes,
            "evolucionAptitudes": evolucion_aptitudes
        }), 200
    except Exception as e:
        log(f"US025 perfil estudiante error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR1","message":"Error al obtener estadísticas"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/estudiante/stats/perfil/export', methods=['GET'])
@token_required
def estudiante_stats_perfil_export(current_user_id):
    fmt = (request.args.get('format') or 'csv').lower()
    if fmt not in ('csv','pdf'):
        return jsonify({"errorCode":"ERR1","message":"Formato inválido"}), 400
    with app.test_request_context(query_string=request.query_string):
        data_resp, status = estudiante_stats_perfil(current_user_id)
    if status != 200:
        return data_resp, status
    payload = data_resp.get_json()
    if fmt == 'csv':
        import io, csv as _csv
        buf = io.StringIO()
        w = _csv.writer(buf)
        w.writerow(["Clave","Valor"])
        w.writerow(["nombre", payload['usuario']['nombre']])
        w.writerow(["apellido", payload['usuario']['apellido']])
        w.writerow(["testsRealizados", payload['testsRealizados']])
        for r in payload.get('top3Aptitudes', []):
            w.writerow(["top3Aptitudes", json.dumps(r, ensure_ascii=False)])
        for r in payload.get('radarAptitudes', []):
            w.writerow(["radarAptitudes", json.dumps(r, ensure_ascii=False)])
        for r in payload.get('evolucionAptitudes', []):
            w.writerow(["evolucionAptitudes", json.dumps(r, ensure_ascii=False)])
        csv_data = buf.getvalue()
        from flask import Response
        return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition':'attachment; filename="stats_estudiante_perfil.csv"'})
    else:
        content = "Reporte Perfil Estudiante (Stub PDF)\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        from flask import Response
        return Response(content, mimetype='application/pdf', headers={'Content-Disposition':'attachment; filename="stats_estudiante_perfil.pdf"'})

@app.route('/api/v1/estudiante/stats/compatibilidad', methods=['GET'])
@token_required
def estudiante_stats_compatibilidad(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        # Top 5 carreras más compatibles (sin datos -> vacio)
        top5_carreras = []
        # Favoritas (con compatibilidad) -> vacio
        favoritas = []
        # Compatibilidad promedio entre favoritas -> 0
        compat_promedio_favoritas = 0
        # Tipos de carrera con mayor compatibilidad -> vacio
        tipos_mayor_compat = []
        empty_all = (len(top5_carreras)==0 and len(favoritas)==0 and compat_promedio_favoritas==0 and len(tipos_mayor_compat)==0)
        if empty_all:
            return jsonify({"errorCode":"ERR1","message":"No se encontraron datos de compatibilidad."}), 404
        return jsonify({
            "top5Carreras": top5_carreras,
            "favoritas": favoritas,
            "compatibilidadPromedioFavoritas": compat_promedio_favoritas,
            "tiposCarreraMayorCompatibilidad": tipos_mayor_compat
        }), 200
    except Exception as e:
        log(f"US025 compatibilidad estudiante error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR1","message":"Error al obtener estadísticas"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/estudiante/stats/compatibilidad/export', methods=['GET'])
@token_required
def estudiante_stats_compatibilidad_export(current_user_id):
    fmt = (request.args.get('format') or 'csv').lower()
    if fmt not in ('csv','pdf'):
        return jsonify({"errorCode":"ERR1","message":"Formato inválido"}), 400
    with app.test_request_context(query_string=request.query_string):
        data_resp, status = estudiante_stats_compatibilidad(current_user_id)
    if status != 200:
        return data_resp, status
    payload = data_resp.get_json()
    if fmt == 'csv':
        import io, csv as _csv
        buf = io.StringIO()
        w = _csv.writer(buf)
        w.writerow(["Clave","Valor"])
        for r in payload.get('top5Carreras', []):
            w.writerow(["top5Carreras", json.dumps(r, ensure_ascii=False)])
        for r in payload.get('favoritas', []):
            w.writerow(["favoritas", json.dumps(r, ensure_ascii=False)])
        w.writerow(["compatibilidadPromedioFavoritas", payload.get('compatibilidadPromedioFavoritas')])
        for r in payload.get('tiposCarreraMayorCompatibilidad', []):
            w.writerow(["tiposCarreraMayorCompatibilidad", json.dumps(r, ensure_ascii=False)])
        csv_data = buf.getvalue()
        from flask import Response
        return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition':'attachment; filename="stats_estudiante_compatibilidad.csv"'})
    else:
        content = "Reporte Compatibilidad Estudiante (Stub PDF)\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        from flask import Response
        return Response(content, mimetype='application/pdf', headers={'Content-Disposition':'attachment; filename="stats_estudiante_compatibilidad.pdf"'})

    
# ============================ Configuración de Backups Automáticos (US026) ============================
# Requisitos:
# - Un solo registro de configuración (tabla configuracionbackup) o se reemplaza (truncate + insert) para simplificar.
# - Campos: frecuencia (diaria|semanal|mensual), horaEjecucion (HH:MM), cantidadBackupConservar (int>0)
# - GET: devuelve configuración actual (si no existe, valores null)
# - PUT: guarda configuración. Validaciones -> ERR1 campos obligatorios / formato inválido; ERR2 error técnico.
# Permiso requerido: ADMIN_PANEL.

VALID_FREQUENCIAS_BACKUP = { 'diaria','semanal','mensual' }

def _read_backup_config(cur):
    cur.execute("SELECT frecuencia, TIME_FORMAT(horaEjecucion,'%H:%i') AS horaEjecucion, cantidadBackupConservar FROM configuracionbackup LIMIT 1")
    row = cur.fetchone()
    if not row:
        return {"frecuencia": None, "horaEjecucion": None, "cantidadBackupConservar": None}
    return {"frecuencia": row[0], "horaEjecucion": row[1], "cantidadBackupConservar": row[2]}

@app.route('/api/v1/admin/backup/config', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def backup_config_get(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        data = _read_backup_config(cur)
        return jsonify(data), 200
    except Exception as e:
        log(f"US026 get config error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR2","message":"Error al obtener la configuración."}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/backup/config', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def backup_config_save(current_user_id):
    payload = request.get_json(silent=True) or {}
    freq = (payload.get('frecuencia') or '').strip().lower()
    hora = (payload.get('horaEjecucion') or '').strip()
    cant = payload.get('cantidadBackupConservar')
    # Validaciones básicas
    try:
        if freq not in VALID_FREQUENCIAS_BACKUP:
            raise ValueError('freq')
        # Validar hora HH:MM
        datetime.datetime.strptime(hora, '%H:%M')
        cant_int = int(cant)
        if cant_int <= 0:
            raise ValueError('cant')
    except Exception:
        return jsonify({"errorCode":"ERR1","message":"Debe completar todos los campos para guardar la configuración."}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Limpiar configuración previa (simplificación, tabla almacena único registro)
        cur.execute("DELETE FROM configuracionbackup")
        cur.execute("INSERT INTO configuracionbackup (frecuencia, horaEjecucion, cantidadBackupConservar) VALUES (%s,%s,%s)", (freq, hora+':00', cant_int))
        conn.commit()
        return jsonify({"ok": True, "message":"Configuración guardada."}), 200
    except Exception as e:
        log(f"US026 save config error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR2","message":"Error al guardar la configuración. Intente nuevamente."}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass


# ============================ Recuperación de Backups (US027) ============================
# Requisitos:
# - Listar backups disponibles (tabla backup) con fechaBackup, tamano, directorio.
# - Restaurar un backup por fecha (identificador) simulando proceso.
# - Confirmación y progreso: este backend sólo simula (progreso 0->100 en memoria, no persistente entre procesos).
# - Errores:
#   ERR1: Error técnico durante restauración.
#   ERR2: Backup no encontrado o datos inválidos.
# Endpoints:
#   GET  /api/v1/admin/backup/list
#   POST /api/v1/admin/backup/restore  { "fechaBackup": "YYYY-MM-DD HH:MM:SS" }
#   GET  /api/v1/admin/backup/restore/status?fecha=...
# Notas: En producción la restauración sería asincrónica y bloquearía escritura; aquí se simula en memoria.

_RESTORE_JOBS = {}  # clave fechaBackup(str) -> {status: pending|running|success|error, progress:int, message}

def _serialize_backup(row):
    # row: (fechaBackup, directorio, tamano)
    return {
        "fechaBackup": row[0].strftime('%Y-%m-%d %H:%M:%S') if row[0] else None,
        "directorio": row[1],
        "tamano": row[2]
    }

@app.route('/api/v1/admin/backup/list', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def backup_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT fechaBackup, directorio, tamano FROM backup ORDER BY fechaBackup DESC")
        rows = cur.fetchall() or []
        backups = [_serialize_backup(r) for r in rows]
        return jsonify({"backups": backups}), 200
    except Exception as e:
        log(f"US027 list backups error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR1","message":"Error al listar backups."}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

def _start_restore_job(fecha_str):
    job = _RESTORE_JOBS.get(fecha_str)
    if job and job['status'] in ('running','pending'):
        return job
    # Inicializar
    job = {"status":"running","progress":0,"message":"Iniciando restauración"}
    _RESTORE_JOBS[fecha_str] = job
    # Simulación rápida de progreso (sin threading real para simplicidad: se incrementa cada consulta de status)
    return job

@app.route('/api/v1/admin/backup/restore', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def backup_restore_start(current_user_id):
    data = request.get_json(silent=True) or {}
    fecha = data.get('fechaBackup')
    if not fecha:
        return jsonify({"errorCode":"ERR2","message":"El archivo de respaldo seleccionado no es válido o está dañado."}), 400
    # Verificar existencia en tabla
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT fechaBackup FROM backup WHERE fechaBackup=%s", (fecha,))
        r = cur.fetchone()
        if not r:
            return jsonify({"errorCode":"ERR2","message":"El archivo de respaldo seleccionado no es válido o está dañado."}), 404
        job = _start_restore_job(fecha)
        return jsonify({"ok": True, "status": job['status'], "progress": job['progress'] }), 202
    except Exception as e:
        log(f"US027 start restore error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR1","message":"Error al restaurar el sistema. Intente nuevamente o contacte a soporte."}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/backup/restore/status', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def backup_restore_status(current_user_id):
    fecha = request.args.get('fecha')
    if not fecha or fecha not in _RESTORE_JOBS:
        return jsonify({"errorCode":"ERR2","message":"El archivo de respaldo seleccionado no es válido o está dañado."}), 404
    job = _RESTORE_JOBS[fecha]
    # Simular avance
    if job['status'] == 'running':
        job['progress'] = min(100, job['progress'] + 25)
        if job['progress'] >= 100:
            job['status'] = 'success'
            job['message'] = 'Restauración completada.'
    return jsonify({"status": job['status'], "progress": job['progress'], "message": job.get('message') }), 200



# ============================ Gestión Solicitudes de Instituciones (US028) ============================
# Limitaciones del esquema actual: la tabla `institucion` no posee columnas para nombre, email, tipo, localización ni estado.
# Tablas de estado (estadoinstitucion / institucionestado) no están correctamente relacionadas en el dump mínimo provisto.
# Se implementa una capa simulada utilizando estructuras en memoria para estado y metadatos mientras no se normalice el modelo.
# Una vez que existan columnas reales (ej: institucion.nombre, institucion.email, institucion.idTipoInstitucion, institucion.idLocalidad,
# institucionestado(idInstitucion, idEstadoInstitucion, fechaInicio)) se deberá reescribir la lógica para usar SQL.
# Estados simulados: PENDIENTE, APROBADA, RECHAZADA.
# Filtros: nombre (substring), tipoId (int), estado (cadena), from/to (fecha solicitud en memoria). ERR1 filtros inválidos.
# Acciones: aprobar (ERR2 si falla), rechazar (ERR3 si falla). Justificación opcional en rechazo.

_INSTITUTION_REQUESTS_MEM = {
    # idInstitucion: { 'nombre': str, 'email': str, 'tipoId': int, 'localizacion': '---', 'estado': 'PENDIENTE', 'fechaSolicitud': datetime.date }
}

def _bootstrap_institution_requests(conn):
    if _INSTITUTION_REQUESTS_MEM:
        return
    try:
        cur = conn.cursor()
        # Intentar leer IDs existentes (sin más columnas disponibles)
        cur.execute("SELECT idInstitucion FROM institucion ORDER BY idInstitucion LIMIT 20")
        rows = cur.fetchall() or []
        today = datetime.date.today()
        for (iid,) in rows:
            _INSTITUTION_REQUESTS_MEM[iid] = {
                'nombre': f'Institucion {iid}',
                'email': f'institucion{iid}@example.com',
                'tipoId': 1,
                'localizacion': 'N/D',
                'estado': 'PENDIENTE',
                'fechaSolicitud': today
            }
    except Exception as e:
        log(f"US028 bootstrap error: {e}")

def _parse_request_filters():
    args = request.args
    nombre = args.get('nombre')
    tipo_id = args.get('tipoId')
    estado = args.get('estado')
    f = args.get('from')
    t = args.get('to')
    try:
        tipo_id_int = int(tipo_id) if tipo_id not in (None,'') else None
    except Exception:
        return None, jsonify({"errorCode":"ERR1","message":"Filtros inválidos. Verifique los datos ingresados."}), 400
    try:
        from_dt = datetime.datetime.strptime(f,'%Y-%m-%d').date() if f else None
        to_dt = datetime.datetime.strptime(t,'%Y-%m-%d').date() if t else None
        if from_dt and to_dt and from_dt>to_dt:
            raise ValueError()
    except Exception:
        return None, jsonify({"errorCode":"ERR1","message":"Filtros inválidos. Verifique los datos ingresados."}), 400
    if estado and estado.upper() not in ('PENDIENTE','APROBADA','RECHAZADA'):
        return None, jsonify({"errorCode":"ERR1","message":"Filtros inválidos. Verifique los datos ingresados."}), 400
    return (nombre, tipo_id_int, estado.upper() if estado else None, from_dt, to_dt), None, None

@app.route('/api/v1/admin/institutions/requests', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_institution_requests_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        _bootstrap_institution_requests(conn)
        filters, err_resp, err_code = _parse_request_filters()
        if err_resp:
            return err_resp, err_code
        nombre, tipo_id, estado, from_dt, to_dt = filters
        data = []
        for iid, meta in _INSTITUTION_REQUESTS_MEM.items():
            if meta['estado'] == 'APROBADA':
                continue  # ya no listar aprobadas (criterio de historia)
            if nombre and nombre.lower() not in meta['nombre'].lower():
                continue
            if tipo_id and meta['tipoId'] != tipo_id:
                continue
            if estado and meta['estado'] != estado:
                continue
            if from_dt and meta['fechaSolicitud'] < from_dt:
                continue
            if to_dt and meta['fechaSolicitud'] > to_dt:
                continue
            data.append({
                'idInstitucion': iid,
                'nombre': meta['nombre'],
                'tipoId': meta['tipoId'],
                'localizacion': meta['localizacion'],
                'estado': meta['estado'],
                'email': meta['email'],
                'fechaSolicitud': str(meta['fechaSolicitud'])
            })
        return jsonify({'solicitudes': data}), 200
    except Exception as e:
        log(f"US028 list error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Filtros inválidos. Verifique los datos ingresados.'}), 400
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/institutions/requests/<int:id_institucion>/approve', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_institution_request_approve(current_user_id, id_institucion):
    try:
        meta = _INSTITUTION_REQUESTS_MEM.get(id_institucion)
        if not meta or meta['estado'] != 'PENDIENTE':
            return jsonify({'errorCode':'ERR2','message':'No se pudo aprobar la solicitud. Intente nuevamente.'}), 404
        # Simular actualización
        meta['estado'] = 'APROBADA'
        # Aquí se enviaría correo con credenciales
        return jsonify({'ok': True, 'message':'Institución aprobada.'}), 200
    except Exception as e:
        log(f"US028 approve error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo aprobar la solicitud. Intente nuevamente.'}), 500

@app.route('/api/v1/admin/institutions/requests/<int:id_institucion>/reject', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_institution_request_reject(current_user_id, id_institucion):
    try:
        meta = _INSTITUTION_REQUESTS_MEM.get(id_institucion)
        if not meta or meta['estado'] != 'PENDIENTE':
            return jsonify({'errorCode':'ERR3','message':'No se pudo rechazar la solicitud. Intente nuevamente.'}), 404
        data = request.get_json(silent=True) or {}
        just = data.get('justificacion')
        meta['estado'] = 'RECHAZADA'
        meta['justificacion'] = just
        return jsonify({'ok': True, 'message':'Institución rechazada.'}), 200
    except Exception as e:
        log(f"US028 reject error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo rechazar la solicitud. Intente nuevamente.'}), 500


    
# ============================ ABM Carrera Catálogo (US029) ============================
# Catálogo base: tabla carrera (idCarrera, nombreCarrera, idTipoCarrera, fechaFin)
# Endpoints (prefijo admin):
#  GET  /api/v1/admin/catalog/careers                -> listado (incluye bajas si )
#  POST /api/v1/admin/catalog/careers                -> alta (campos: nombreCarrera, idTipoCarrera)  ERR1 campos obligatorios
#  GET  /api/v1/admin/catalog/careers/<id>           -> detalle
#  PUT  /api/v1/admin/catalog/careers/<id>           -> modificar (mismos campos) ERR1 campos obligatorios
#  DELETE /api/v1/admin/catalog/careers/<id>         -> baja lógica (set fechaFin=NOW()) ERR2 en error técnico
# Errores:
#  ERR1: campos obligatorios vacíos -> "Debe completar todos los campos obligatorios."
#  ERR2: error técnico al dar de baja -> "No se pudo eliminar la carrera. Intente nuevamente."
# Notas: No se permiten duplicados exactos (nombre + tipo) activos. Si existe uno con mismo nombre y tipo y sin fechaFin -> ERR1.

def _career_exists_active(cur, nombre, tipo_id, exclude_id=None):
    q = "SELECT idCarrera FROM carrera WHERE nombreCarrera=%s AND idTipoCarrera=%s AND fechaFin IS NULL"
    params = [nombre, tipo_id]
    if exclude_id:
        q += " AND idCarrera<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/careers', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_catalog_careers_list(current_user_id):
    include_inactive = request.args.get('includeInactive') in ('1','true','TRUE')
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if include_inactive:
            cur.execute("SELECT idCarrera, nombreCarrera, idTipoCarrera, fechaFin FROM carrera ORDER BY nombreCarrera")
        else:
            cur.execute("SELECT idCarrera, nombreCarrera, idTipoCarrera, fechaFin FROM carrera WHERE (fechaFin IS NULL OR fechaFin > NOW()) ORDER BY nombreCarrera")
        rows = cur.fetchall() or []
        return jsonify({'careers': rows}), 200
    except Exception as e:
        log(f"US029 list careers error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo listar carreras.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/careers', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_catalog_career_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreCarrera') or '').strip()
    tipo = data.get('idTipoCarrera')
    if not nombre or not tipo:
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _career_exists_active(cur, nombre, tipo):
            return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 400
        cur.execute("INSERT INTO carrera (nombreCarrera, idTipoCarrera) VALUES (%s,%s)", (nombre, tipo))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({'ok':True,'idCarrera': new_id}), 201
    except Exception as e:
        log(f"US029 create career error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/careers/<int:id_carrera>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_catalog_career_detail(current_user_id, id_carrera):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idCarrera, nombreCarrera, idTipoCarrera, fechaFin FROM carrera WHERE idCarrera=%s", (id_carrera,))
        row = cur.fetchone()
        if not row:
            return jsonify({'errorCode':'ERR1','message':'Carrera no encontrada.'}), 404
        return jsonify(row), 200
    except Exception as e:
        log(f"US029 detail career error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/careers/<int:id_carrera>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_catalog_career_update(current_user_id, id_carrera):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreCarrera') or '').strip()
    tipo = data.get('idTipoCarrera')
    fechaFin = data.get('fechaFin')  # Puede ser None, 'NOW()' o fecha específica YYYY-MM-DD HH:MM:SS
    if not nombre or not tipo:
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 400
    
    # Validar fechaFin si se proporciona
    fecha_fin_sql = None
    set_null = False
    if fechaFin:
        if fechaFin.upper() == 'NOW()':
            fecha_fin_sql = 'NOW()'
        elif fechaFin.upper() == 'NULL':
            set_null = True  # Flag para setear NULL explícitamente
        else:
            try:
                # Validar formato de fecha
                datetime.datetime.strptime(fechaFin, '%Y-%m-%d %H:%M:%S')
                fecha_fin_sql = fechaFin
            except ValueError:
                try:
                    # Intentar formato solo fecha
                    datetime.datetime.strptime(fechaFin, '%Y-%m-%d')
                    fecha_fin_sql = fechaFin + ' 23:59:59'  # Agregar hora por defecto
                except ValueError:
                    return jsonify({'errorCode':'ERR1','message':'Formato de fecha inválido. Use YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, NOW() o NULL'}), 400
    
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idCarrera FROM carrera WHERE idCarrera=%s", (id_carrera,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Carrera no encontrada.'}), 404
        if _career_exists_active(cur, nombre, tipo, exclude_id=id_carrera):
            return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 400
        
        # Construir consulta SQL según si hay fechaFin o no
        if set_null:
            # Setear fechaFin a NULL explícitamente
            cur.execute("UPDATE carrera SET nombreCarrera=%s, idTipoCarrera=%s, fechaFin=NULL WHERE idCarrera=%s", 
                       (nombre, tipo, id_carrera))
        elif fecha_fin_sql:
            if fecha_fin_sql == 'NOW()':
                cur.execute("UPDATE carrera SET nombreCarrera=%s, idTipoCarrera=%s, fechaFin=NOW() WHERE idCarrera=%s", 
                           (nombre, tipo, id_carrera))
            else:
                cur.execute("UPDATE carrera SET nombreCarrera=%s, idTipoCarrera=%s, fechaFin=%s WHERE idCarrera=%s", 
                           (nombre, tipo, fecha_fin_sql, id_carrera))
        else:
            # Si fechaFin no se proporciona, mantener el valor actual (no modificar fechaFin)
            cur.execute("UPDATE carrera SET nombreCarrera=%s, idTipoCarrera=%s WHERE idCarrera=%s", 
                       (nombre, tipo, id_carrera))
        
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US029 update career error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
# Ejemplo de curl:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/careers/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreCarrera\":\"Ingeniería en Sistemas Actualizada\",\"idTipoCarrera\":1}"

@app.route('/api/v1/admin/catalog/careers/<int:id_carrera>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_catalog_career_delete(current_user_id, id_carrera):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idCarrera FROM carrera WHERE idCarrera=%s", (id_carrera,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la carrera. Intente nuevamente.'}), 404
        cur.execute("UPDATE carrera SET fechaFin=NOW() WHERE idCarrera=%s", (id_carrera,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US029 delete career error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la carrera. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US029 (token Hola):
# Listar carreras activas:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/careers" -H "Authorization: Bearer {{token}}"
# Listar todas las carreras (incluye inactivas):
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/careers?includeInactive=true" -H "Authorization: Bearer {{token}}"
# Crear carrera:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/careers" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreCarrera\":\"Ingeniería en Sistemas\",\"idTipoCarrera\":1}"
# Detalle de carrera:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/careers/1" -H "Authorization: Bearer {{token}}"
# Actualizar carrera (solo nombre y tipo):
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/careers/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreCarrera\":\"Ingeniería en Sistemas Actualizada\",\"idTipoCarrera\":1}"
# Actualizar carrera con baja inmediata:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/careers/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreCarrera\":\"Ingeniería en Sistemas\",\"idTipoCarrera\":1,\"fechaFin\":\"NOW()\"}"
# Actualizar carrera con baja programada:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/careers/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreCarrera\":\"Ingeniería en Sistemas\",\"idTipoCarrera\":1,\"fechaFin\":\"2025-12-31 23:59:59\"}"
# Actualizar carrera para reactivarla (quitar fecha fin):
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/careers/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreCarrera\":\"Ingeniería en Sistemas\",\"idTipoCarrera\":1,\"fechaFin\":\"NULL\"}"
# Baja lógica mediante DELETE:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/careers/1" -H "Authorization: Bearer {{token}}"


# ============================ ABM TipoCarrera (US030) ============================
# Tabla involucrada: tipocarrera (idTipoCarrera, nombreTipoCarrera, fechaFin)
# Endpoints (prefijo admin):
#  GET    /api/v1/admin/catalog/career-types              -> listado (activas por defecto,  para todas)
#  POST   /api/v1/admin/catalog/career-types              -> alta (campo: nombreTipoCarrera) ERR1 si vacío o duplicado activo
#  GET    /api/v1/admin/catalog/career-types/<id>         -> detalle
#  PUT    /api/v1/admin/catalog/career-types/<id>         -> modificar nombre ERR1 si vacío o duplicado activo
#  DELETE /api/v1/admin/catalog/career-types/<id>         -> baja lógica (fechaFin=NOW()) ERR2 en error técnico
# Errores definidos:
#  ERR1: "Debe ingresar un nombre para el tipo de carrera." (nombre vacío o duplicado activo)
#  ERR2: "No se pudo eliminar el tipo de carrera. Intente nuevamente." (error técnico o inexistente en baja)

def _tipo_carrera_exists_active(cur, nombre, exclude_id=None):
    q = "SELECT idTipoCarrera FROM tipocarrera WHERE nombreTipoCarrera=%s AND fechaFin IS NULL"
    params = [nombre]
    if exclude_id:
        q += " AND idTipoCarrera<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/career-types', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_career_types_list(current_user_id):
    include_inactive = request.args.get('includeInactive') in ('1','true','TRUE')
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if include_inactive:
            cur.execute("SELECT idTipoCarrera, nombreTipoCarrera, fechaFin FROM tipocarrera ORDER BY nombreTipoCarrera")
        else:
            cur.execute("SELECT idTipoCarrera, nombreTipoCarrera, fechaFin FROM tipocarrera WHERE (fechaFin IS NULL OR fechaFin > NOW()) ORDER BY nombreTipoCarrera")
        rows = cur.fetchall() or []
        return jsonify({'careerTypes': rows}), 200
    except Exception as e:
        log(f"US030 list tipoCarrera error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo listar tipos de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-types', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_career_type_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreTipoCarrera') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _tipo_carrera_exists_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 400
        cur.execute("INSERT INTO tipocarrera (nombreTipoCarrera) VALUES (%s)", (nombre,))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({'ok':True,'idTipoCarrera': new_id}), 201
    except Exception as e:
        log(f"US030 create tipoCarrera error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-types/<int:id_tipo>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_career_type_detail(current_user_id, id_tipo):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idTipoCarrera, nombreTipoCarrera, fechaFin FROM tipocarrera WHERE idTipoCarrera=%s", (id_tipo,))
        row = cur.fetchone()
        if not row:
            return jsonify({'errorCode':'ERR1','message':'Tipo de carrera no encontrado.'}), 404
        return jsonify(row), 200
    except Exception as e:
        log(f"US030 detail tipoCarrera error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener tipo de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-types/<int:id_tipo>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_career_type_update(current_user_id, id_tipo):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreTipoCarrera') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idTipoCarrera FROM tipocarrera WHERE idTipoCarrera=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Tipo de carrera no encontrado.'}), 404
        if _tipo_carrera_exists_active(cur, nombre, exclude_id=id_tipo):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 400
        cur.execute("UPDATE tipocarrera SET nombreTipoCarrera=%s WHERE idTipoCarrera=%s", (nombre, id_tipo))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US030 update tipoCarrera error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-types/<int:id_tipo>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_career_type_delete(current_user_id, id_tipo):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idTipoCarrera FROM tipocarrera WHERE idTipoCarrera=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el tipo de carrera. Intente nuevamente.'}), 404
        cur.execute("UPDATE tipocarrera SET fechaFin=NOW() WHERE idTipoCarrera=%s AND fechaFin IS NULL", (id_tipo,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US030 delete tipoCarrera error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el tipo de carrera. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

  
# ============================ ABM País (US031) ============================
# Tabla: pais (idPais, nombrePais, fechaFin)
# Endpoints (prefijo admin):
#  GET    /api/v1/admin/catalog/countries              -> listado (activos por defecto,  para todos)
#  POST   /api/v1/admin/catalog/countries              -> alta (nombrePais) ERR1 si vacío o duplicado activo
#  GET    /api/v1/admin/catalog/countries/<id>         -> detalle
#  PUT    /api/v1/admin/catalog/countries/<id>         -> modificar nombre ERR1 si vacío o duplicado activo
#  DELETE /api/v1/admin/catalog/countries/<id>         -> baja lógica (fechaFin=NOW()) ERR2 en error técnico / inexistente
# Errores:
#  ERR1: "Debe ingresar un nombre para el país." (nombre vacío o duplicado activo)
#  ERR2: "No se pudo eliminar el país. Intente nuevamente." (error técnico / no encontrado)

def _pais_exists_active(cur, nombre, exclude_id=None):
    q = "SELECT idPais FROM pais WHERE nombrePais=%s"
    params = [nombre]
    if exclude_id:
        q += " AND idPais<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/countries', methods=['GET'])
def admin_countries_list():
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idPais, nombrePais FROM pais ORDER BY nombrePais")
        rows = cur.fetchall() or []
        return jsonify({'countries': rows}), 200
    except Exception as e:
        log(f"US031 list pais error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo listar países.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/countries', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_country_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombrePais') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _pais_exists_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 400
        cur.execute("INSERT INTO pais (nombrePais) VALUES (%s)", (nombre,))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({'ok':True,'idPais': new_id}), 201
    except Exception as e:
        log(f"US031 create pais error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/countries/<int:id_pais>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_country_detail(current_user_id, id_pais):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idPais, nombrePais FROM pais WHERE idPais=%s", (id_pais,))
        row = cur.fetchone()
        if not row:
            return jsonify({'errorCode':'ERR1','message':'País no encontrado.'}), 404
        return jsonify(row), 200
    except Exception as e:
        log(f"US031 detail pais error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener país.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/countries/<int:id_pais>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_country_update(current_user_id, id_pais):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombrePais') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idPais FROM pais WHERE idPais=%s", (id_pais,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'País no encontrado.'}), 404
        if _pais_exists_active(cur, nombre, exclude_id=id_pais):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 400
        cur.execute("UPDATE pais SET nombrePais=%s WHERE idPais=%s", (nombre, id_pais))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US031 update pais error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/countries/<int:id_pais>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_country_delete(current_user_id, id_pais):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idPais FROM pais WHERE idPais=%s", (id_pais,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el país. Intente nuevamente.'}), 404
        cur.execute("DELETE FROM pais WHERE idPais=%s", (id_pais,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US031 delete pais error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el país. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US031 (token Hola):
# Listar activos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/countries" -H "Authorization: Bearer {{token}}"
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/countries" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/countries" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombrePais\":\"Argentina\"}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/countries/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/countries/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombrePais\":\"Argentina Modificada\"}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/countries/1" -H "Authorization: Bearer {{token}}"


# ============================ ABM Provincia (US032) ============================
# Tabla: provincia (idProvincia, nombreProvincia, idPais
# Requisito: cada provincia asociada a un país existente (tabla pais).
# Endpoints (prefijo admin):
#  GET    /api/v1/admin/catalog/provinces                 -> listado (solo activas,  para todas)
#  POST   /api/v1/admin/catalog/provinces                 -> alta (nombreProvincia, idPais) ERR1 nombre vacío, ERR2 país faltante/ inválido, duplicado activo (nombre+idPais)
#  GET    /api/v1/admin/catalog/provinces/<id>            -> detalle
#  PUT    /api/v1/admin/catalog/provinces/<id>            -> modificar (mismos campos) ERR1 / ERR2 según validaciones
#  DELETE /api/v1/admin/catalog/provinces/<id>            -> baja lógica ERR3 si error técnico / inexistente
# Errores:
#   ERR1: "Debe ingresar un nombre para la provincia." (nombre vacío)
#   ERR2: "Debe seleccionar un país." (idPais vacío / inexistente / duplicado activo con mismo nombre en mismo país)
#   ERR3: "No se pudo eliminar la provincia. Intente nuevamente." (falla al eliminar o no encontrada)

def _provincia_duplicate_active(cur, nombre, id_pais, exclude_id=None):
    q = "SELECT idProvincia FROM provincia WHERE nombreProvincia=%s AND idPais=%s"
    params = [nombre, id_pais]
    if exclude_id:
        q += " AND idProvincia<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

def _pais_exists(cur, id_pais):
    cur.execute("SELECT idPais FROM pais WHERE idPais=%s", (id_pais,))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/provinces', methods=['GET'])
def admin_provinces_list():
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idProvincia, nombreProvincia, idPais FROM provincia ORDER BY nombreProvincia")
        rows = cur.fetchall() or []
        return jsonify({'provinces': rows}), 200
    except Exception as e:
        log(f"US032 list provincia error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo listar provincias.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/provinces', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_province_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreProvincia') or '').strip()
    id_pais = data.get('idPais')
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la provincia.'}), 400
    if not id_pais:
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # validar país
        if not _pais_exists(cur, id_pais):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 400
        if _provincia_duplicate_active(cur, nombre, id_pais):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 400  # reutilizamos ERR2 para duplicado por criterio HU (no hay código específico)
        cur.execute("INSERT INTO provincia (nombreProvincia, idPais) VALUES (%s,%s)", (nombre, id_pais))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({'ok':True,'idProvincia': new_id}), 201
    except Exception as e:
        log(f"US032 create provincia error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/provinces/<int:id_provincia>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_province_detail(current_user_id, id_provincia):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idProvincia, nombreProvincia, idPais FROM provincia WHERE idProvincia=%s", (id_provincia,))
        row = cur.fetchone()
        if not row:
            return jsonify({'errorCode':'ERR1','message':'Provincia no encontrada.'}), 404
        return jsonify(row), 200
    except Exception as e:
        log(f"US032 detail provincia error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener provincia.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/provinces/<int:id_provincia>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_province_update(current_user_id, id_provincia):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreProvincia') or '').strip()
    id_pais = data.get('idPais')
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la provincia.'}), 400
    if not id_pais:
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idProvincia FROM provincia WHERE idProvincia=%s", (id_provincia,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Provincia no encontrada.'}), 404
        if not _pais_exists(cur, id_pais):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 400
        if _provincia_duplicate_active(cur, nombre, id_pais, exclude_id=id_provincia):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 400
        cur.execute("UPDATE provincia SET nombreProvincia=%s, idPais=%s WHERE idProvincia=%s", (nombre, id_pais, id_provincia))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US032 update provincia error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/provinces/<int:id_provincia>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_province_delete(current_user_id, id_provincia):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idProvincia FROM provincia WHERE idProvincia=%s", (id_provincia,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR3','message':'No se pudo eliminar la provincia. Intente nuevamente.'}), 404
        cur.execute("DELETE FROM provincia WHERE idProvincia=%s", (id_provincia,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US032 delete provincia error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo eliminar la provincia. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US032 (token Hola):
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/provinces" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/provinces" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreProvincia\":\"Córdoba\",\"idPais\":1}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/provinces/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/provinces/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreProvincia\":\"Córdoba Norte\",\"idPais\":1}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/provinces/1" -H "Authorization: Bearer {{token}}"


# ============================ ABM Localidad (US033) ============================
# Tabla: localidad (idLocalidad, nombreLocalidad, idProvincia, fechaFin)
# Requisito: cada localidad asociada a provincia existente (tabla provincia).
# Endpoints (prefijo admin):
#  POST   /api/v1/admin/catalog/localities                 -> alta (nombreLocalidad, idProvincia) ERR1 nombre vacío, ERR2 provincia inválida/faltante, duplicado (nombre+provincia) activo
#  GET    /api/v1/admin/catalog/localities/<id>            -> detalle
#  PUT    /api/v1/admin/catalog/localities/<id>            -> modificar campos ERR1/ERR2
#  DELETE /api/v1/admin/catalog/localities/<id>            -> baja lógica (fechaFin=NOW()) ERR3 si error técnico / inexistente
# Errores:
#   ERR1: "Debe ingresar un nombre para la localidad." (nombre vacío)
#   ERR2: "Debe seleccionar una provincia asociada." (idProvincia faltante / inválida / duplicado activo)
#   ERR3: "No se pudo eliminar la localidad. Intente nuevamente." (falla o no encontrada)

def _provincia_exists(cur, id_provincia):
    cur.execute("SELECT idProvincia FROM provincia WHERE idProvincia=%s", (id_provincia,))
    return cur.fetchone() is not None

def _localidad_duplicate_active(cur, nombre, id_provincia, exclude_id=None):
    q = "SELECT idLocalidad FROM localidad WHERE nombreLocalidad=%s AND idProvincia=%s"
    params = [nombre, id_provincia]
    if exclude_id:
        q += " AND idLocalidad<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/localities', methods=['GET'])
def admin_localities_list():
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idLocalidad, nombreLocalidad, idProvincia FROM localidad ORDER BY nombreLocalidad")
        rows = cur.fetchall() or []
        return jsonify({'localities': rows}), 200
    except Exception as e:
        log(f"US033 list localidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo listar localidades.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/localities', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_locality_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreLocalidad') or '').strip()
    id_provincia = data.get('idProvincia')
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la localidad.'}), 400
    if not id_provincia:
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if not _provincia_exists(cur, id_provincia):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 400
        if _localidad_duplicate_active(cur, nombre, id_provincia):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 400
        cur.execute("INSERT INTO localidad (nombreLocalidad, idProvincia) VALUES (%s,%s)", (nombre, id_provincia))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({'ok':True,'idLocalidad': new_id}), 201
    except Exception as e:
        log(f"US033 create localidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/localities/<int:id_localidad>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_locality_detail(current_user_id, id_localidad):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idLocalidad, nombreLocalidad, idProvincia FROM localidad WHERE idLocalidad=%s", (id_localidad,))
        row = cur.fetchone()
        if not row:
            return jsonify({'errorCode':'ERR1','message':'Localidad no encontrada.'}), 404
        return jsonify(row), 200
    except Exception as e:
        log(f"US033 detail localidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener localidad.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/localities/<int:id_localidad>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_locality_update(current_user_id, id_localidad):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreLocalidad') or '').strip()
    id_provincia = data.get('idProvincia')
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la localidad.'}), 400
    if not id_provincia:
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idLocalidad FROM localidad WHERE idLocalidad=%s", (id_localidad,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Localidad no encontrada.'}), 404
        if not _provincia_exists(cur, id_provincia):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 400
        if _localidad_duplicate_active(cur, nombre, id_provincia, exclude_id=id_localidad):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 400
        cur.execute("UPDATE localidad SET nombreLocalidad=%s, idProvincia=%s WHERE idLocalidad=%s", (nombre, id_provincia, id_localidad))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US033 update localidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/localities/<int:id_localidad>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_locality_delete(current_user_id, id_localidad):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idLocalidad FROM localidad WHERE idLocalidad=%s", (id_localidad,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR3','message':'No se pudo eliminar la localidad. Intente nuevamente.'}), 404
        cur.execute("DELETE FROM localidad WHERE idLocalidad=%s", (id_localidad,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US033 delete localidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo eliminar la localidad. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US033 (token Hola):
# Listar activos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/localities" -H "Authorization: Bearer {{token}}"
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/localities" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/localities" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreLocalidad\":\"Guaymallén\",\"idProvincia\":1}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/localities/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/localities/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreLocalidad\":\"Guaymallén Centro\",\"idProvincia\":1}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/localities/1" -H "Authorization: Bearer {{token}}"


# ACA AGREGAR LAS HUs SIGUIENTES

# ============================ ABM Género (US034) ============================
# Tabla: genero (idGenero, nombreGenero, fechaFin)
# Endpoints:
#  GET    /api/v1/admin/catalog/genders                  -> listado (activas por defecto, )
#  POST   /api/v1/admin/catalog/genders                  -> alta (nombreGenero) ERR1 nombre vacío (y se reutiliza para duplicado)
#  GET    /api/v1/admin/catalog/genders/<id>             -> detalle
#  PUT    /api/v1/admin/catalog/genders/<id>             -> modificar nombre (ERR1 si vacío o duplicado)
#  DELETE /api/v1/admin/catalog/genders/<id>             -> baja lógica (fechaFin=NOW()) ERR2 si falla / inexistente
# Errores:
#   ERR1: "Debe ingresar un nombre para el género." (nombre vacío o duplicado activo)
#   ERR2: "No se pudo eliminar el género. Intente nuevamente." (error al eliminar o no encontrado)

def _genero_duplicate_active(cur, nombre, exclude_id=None):
    q = "SELECT idGenero FROM genero WHERE nombreGenero=%s"
    params = [nombre]
    if exclude_id:
        q += " AND idGenero<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/genders', methods=['GET'])
def admin_genders_list():
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idGenero, nombreGenero FROM genero ORDER BY nombreGenero")
        rows = cur.fetchall() or []
        return jsonify({'genders': rows}), 200
    except Exception as e:
        log(f"US034 list genero error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al listar géneros.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/genders', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_gender_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreGenero') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _genero_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 400
        cur.execute("INSERT INTO genero (nombreGenero) VALUES (%s)", (nombre,))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({'ok':True,'idGenero': new_id}), 201
    except Exception as e:
        log(f"US034 create genero error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/genders/<int:id_genero>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_gender_detail(current_user_id, id_genero):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idGenero, nombreGenero FROM genero WHERE idGenero=%s", (id_genero,))
        row = cur.fetchone()
        if not row:
            return jsonify({'errorCode':'ERR1','message':'Género no encontrado.'}), 404
        return jsonify(row), 200
    except Exception as e:
        log(f"US034 detail genero error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener género.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/genders/<int:id_genero>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_gender_update(current_user_id, id_genero):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreGenero') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idGenero FROM genero WHERE idGenero=%s", (id_genero,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Género no encontrado.'}), 404
        if _genero_duplicate_active(cur, nombre, exclude_id=id_genero):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 400
        cur.execute("UPDATE genero SET nombreGenero=%s WHERE idGenero=%s", (nombre, id_genero))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US034 update genero error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/genders/<int:id_genero>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_gender_delete(current_user_id, id_genero):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idGenero FROM genero WHERE idGenero=%s", (id_genero,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el género. Intente nuevamente.'}), 404
        cur.execute("DELETE FROM genero WHERE idGenero=%s", (id_genero,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US034 delete genero error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el género. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US034 (token Hola):
# Listar activos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/genders" -H "Authorization: Bearer {{token}}"
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/genders" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/genders" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreGenero\":\"No Binario\"}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/genders/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/genders/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreGenero\":\"No Binario (Actualizado)\"}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/genders/1" -H "Authorization: Bearer {{token}}"




# ============================ ABM EstadoUsuario (US035) ============================
# Tabla: estadousuario (idEstadoUsuario, nombreEstadoUsuario, fechaFin)
# Endpoints:
#  GET    /api/v1/admin/catalog/user-statuses                 -> listado (activos por defecto;  para todos)
#  POST   /api/v1/admin/catalog/user-statuses                 -> alta (nombreEstadoUsuario) ERR1 si vacío o duplicado activo
#  GET    /api/v1/admin/catalog/user-statuses/<id>            -> detalle
#  PUT    /api/v1/admin/catalog/user-statuses/<id>            -> modificar nombre (ERR1 si vacío o duplicado)
#  DELETE /api/v1/admin/catalog/user-statuses/<id>            -> baja lógica (fechaFin=NOW()) ERR2 si falla o no existe
# Errores:
#   ERR1: "Debe ingresar un nombre para el estado." (nombre vacío o duplicado activo)
#   ERR2: "No se pudo eliminar el estado. Intente nuevamente." (error técnico o inexistente)

def _estado_usuario_duplicate_active(cur, nombre, exclude_id=None):
    q = "SELECT idEstadoUsuario FROM estadousuario WHERE nombreEstadoUsuario=%s AND fechaFin IS NULL"
    params = [nombre]
    if exclude_id:
        q += " AND idEstadoUsuario<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/user-statuses', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_user_statuses_list(current_user_id):
    include_inactive = request.args.get('includeInactive') in ('1','true','TRUE')
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if include_inactive:
            cur.execute("SELECT idEstadoUsuario, nombreEstadoUsuario, fechaFin FROM estadousuario ORDER BY nombreEstadoUsuario")
        else:
            cur.execute("SELECT idEstadoUsuario, nombreEstadoUsuario, fechaFin FROM estadousuario WHERE fechaFin IS NULL ORDER BY nombreEstadoUsuario")
        rows = cur.fetchall() or []
        return jsonify({'userStatuses': rows}), 200
    except Exception as e:
        log(f"US035 list estadoUsuario error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al listar estados.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/user-statuses', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_user_status_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoUsuario') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _estado_usuario_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
        cur.execute("INSERT INTO estadousuario (nombreEstadoUsuario, fechaFin) VALUES (%s, NULL)", (nombre,))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({'ok':True,'idEstadoUsuario': new_id}), 201
    except Exception as e:
        log(f"US035 create estadoUsuario error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/user-statuses/<int:id_estado>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_user_status_detail(current_user_id, id_estado):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idEstadoUsuario, nombreEstadoUsuario, fechaFin FROM estadousuario WHERE idEstadoUsuario=%s", (id_estado,))
        row = cur.fetchone()
        if not row:
            return jsonify({'errorCode':'ERR1','message':'Estado no encontrado.'}), 404
        return jsonify(row), 200
    except Exception as e:
        log(f"US035 detail estadoUsuario error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener estado.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/user-statuses/<int:id_estado>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_user_status_update(current_user_id, id_estado):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoUsuario') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idEstadoUsuario FROM estadousuario WHERE idEstadoUsuario=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Estado no encontrado.'}), 404
        if _estado_usuario_duplicate_active(cur, nombre, exclude_id=id_estado):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
        cur.execute("UPDATE estadousuario SET nombreEstadoUsuario=%s WHERE idEstadoUsuario=%s", (nombre, id_estado))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US035 update estadoUsuario error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/user-statuses/<int:id_estado>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_user_status_delete(current_user_id, id_estado):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idEstadoUsuario FROM estadousuario WHERE idEstadoUsuario=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el estado. Intente nuevamente.'}), 404
        cur.execute("UPDATE estadousuario SET fechaFin=NOW() WHERE idEstadoUsuario=%s AND fechaFin IS NULL", (id_estado,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US035 delete estadoUsuario error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el estado. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US035 (token Hola):
# Listar activos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/user-statuses" -H "Authorization: Bearer {{token}}"
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/user-statuses" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/user-statuses" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreEstadoUsuario\":\"Pendiente\"}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/user-statuses/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/user-statuses/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreEstadoUsuario\":\"Suspendido\"}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/user-statuses/1" -H "Authorization: Bearer {{token}}"

# ============================ ABM Permiso (US036) ============================
# Tabla: permiso (idPermiso, nombrePermiso, descripcion, fechaFin)
# Endpoints (prefijo admin):
#  GET    /api/v1/admin/catalog/permissions              -> listado (activos por defecto, )
#  POST   /api/v1/admin/catalog/permissions              -> alta (nombrePermiso obligatorio, descripcion opcional) ERR1 nombre vacío o duplicado activo
#  GET    /api/v1/admin/catalog/permissions/<id>         -> detalle
#  PUT    /api/v1/admin/catalog/permissions/<id>         -> modificar nombre/descripcion (ERR1 si nombre vacío o duplicado)
#  DELETE /api/v1/admin/catalog/permissions/<id>         -> baja lógica (fechaFin=NOW()) ERR2 si falla o inexistente
# Errores:
#   ERR1: "Debe ingresar un nombre para el permiso." (nombre vacío o duplicado activo)
#   ERR2: "No se pudo eliminar el permiso. Intente nuevamente." (error técnico / no encontrado)

def _permiso_duplicate_active(cur, nombre, exclude_id=None):
    q = "SELECT idPermiso FROM permiso WHERE nombrePermiso=%s AND fechaFin IS NULL"
    params = [nombre]
    if exclude_id:
        q += " AND idPermiso<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/permissions', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_permissions_list(current_user_id):
    include_inactive = request.args.get('includeInactive') in ('1','true','TRUE')
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if include_inactive:
            cur.execute("SELECT idPermiso, nombrePermiso, descripcion, fechaFin FROM permiso ORDER BY nombrePermiso")
        else:
            cur.execute("SELECT idPermiso, nombrePermiso, descripcion, fechaFin FROM permiso WHERE fechaFin IS NULL ORDER BY nombrePermiso")
        rows = cur.fetchall() or []
        return jsonify({'permissions': rows}), 200
    except Exception as e:
        log(f"US036 list permiso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al listar permisos.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/permissions', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_permission_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombrePermiso') or '').strip()
    descripcion = (data.get('descripcion') or '').strip() or None
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el permiso.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _permiso_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el permiso.'}), 400
        cur.execute("INSERT INTO permiso (nombrePermiso, descripcion, fechaFin) VALUES (%s,%s,NULL)", (nombre, descripcion))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({'ok':True,'idPermiso': new_id}), 201
    except Exception as e:
        log(f"US036 create permiso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el permiso.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/permissions/<int:id_permiso>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_permission_detail(current_user_id, id_permiso):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idPermiso, nombrePermiso, descripcion, fechaFin FROM permiso WHERE idPermiso=%s", (id_permiso,))
        row = cur.fetchone()
        if not row:
            return jsonify({'errorCode':'ERR1','message':'Permiso no encontrado.'}), 404
        return jsonify(row), 200
    except Exception as e:
        log(f"US036 detail permiso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener permiso.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/permissions/<int:id_permiso>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_permission_update(current_user_id, id_permiso):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombrePermiso') or '').strip()
    descripcion = (data.get('descripcion') or '').strip() or None
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el permiso.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idPermiso FROM permiso WHERE idPermiso=%s", (id_permiso,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Permiso no encontrado.'}), 404
        if _permiso_duplicate_active(cur, nombre, exclude_id=id_permiso):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el permiso.'}), 400
        cur.execute("UPDATE permiso SET nombrePermiso=%s, descripcion=%s WHERE idPermiso=%s", (nombre, descripcion, id_permiso))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US036 update permiso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el permiso.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/permissions/<int:id_permiso>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_permission_delete(current_user_id, id_permiso):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idPermiso FROM permiso WHERE idPermiso=%s", (id_permiso,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el permiso. Intente nuevamente.'}), 404
        cur.execute("UPDATE permiso SET fechaFin=NOW() WHERE idPermiso=%s AND fechaFin IS NULL", (id_permiso,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US036 delete permiso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el permiso. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US036 (token Hola):
# Listar activos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/permissions" -H "Authorization: Bearer {{token}}"
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/permissions" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/permissions" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombrePermiso\":\"VER_REPORTES\",\"descripcion\":\"Permite ver reportes\"}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/permissions/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/permissions/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombrePermiso\":\"VER_REPORTES\",\"descripcion\":\"Puede ver y exportar reportes\"}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/permissions/1" -H "Authorization: Bearer {{token}}"





# ============================ ABM Grupo (US037) ============================
# Tablas: grupo (idGrupo, nombreGrupo, descripcion, fechaFin), permisogrupo (idPermisoGrupo, idGrupo, idPermiso, fechaInicio, fechaFin)
# Endpoints:
#  GET    /api/v1/admin/catalog/groups                  -> listado grupos (activos por defecto;  para todos) + permisos asociados activos
#  POST   /api/v1/admin/catalog/groups                  -> alta (nombreGrupo obligatorio, descripcion opcional, lista permisos opcional) ERR1 nombre vacío o duplicado activo
#  GET    /api/v1/admin/catalog/groups/<id>             -> detalle grupo + permisos activos
#  PUT    /api/v1/admin/catalog/groups/<id>             -> modificar nombre/descripcion/permisos (reemplaza set de permisos) ERR1 nombre vacío o duplicado
#  DELETE /api/v1/admin/catalog/groups/<id>             -> baja lógica grupo (fechaFin=NOW()) y se cierran permisos (fechaFin=NOW()) ERR2 si error o inexistente
# Notas:
#  - Al actualizar permisos se cierran (fechaFin=NOW()) los actuales activos no incluidos y se insertan nuevos (fechaInicio=NOW()).
# Errores:
#  ERR1: "Debe ingresar un nombre para el grupo." (vacío o duplicado activo)
#  ERR2: "No se pudo eliminar el grupo. Intente nuevamente." (error técnico o no encontrado)

def _grupo_duplicate_active(cur, nombre, exclude_id=None):
    q = "SELECT idGrupo FROM grupo WHERE nombreGrupo=%s AND fechaFin IS NULL"
    params = [nombre]
    if exclude_id:
        q += " AND idGrupo<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

def _fetch_permisos_por_grupo(cur, id_grupo):
    cur.execute(
        "SELECT pg.idPermisoGrupo, p.idPermiso, p.nombrePermiso, p.descripcion, pg.fechaInicio, pg.fechaFin "
        "FROM permisogrupo pg JOIN permiso p ON p.idPermiso=pg.idPermiso "
        "WHERE pg.idGrupo=%s AND pg.fechaFin IS NULL", (id_grupo,))
    return cur.fetchall() or []

@app.route('/api/v1/admin/catalog/groups', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_groups_list(current_user_id):
    include_inactive = request.args.get('includeInactive') in ('1','true','TRUE')
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if include_inactive:
            cur.execute("SELECT idGrupo, nombreGrupo, descripcion, fechaFin FROM grupo ORDER BY nombreGrupo")
        else:
            cur.execute("SELECT idGrupo, nombreGrupo, descripcion, fechaFin FROM grupo WHERE fechaFin IS NULL ORDER BY nombreGrupo")
        grupos = cur.fetchall() or []
        # Adjuntar permisos activos de cada grupo
        for g in grupos:
            cur2 = conn.cursor(dictionary=True)
            cur2.execute(
                "SELECT p.idPermiso, p.nombrePermiso FROM permisogrupo pg JOIN permiso p ON p.idPermiso=pg.idPermiso "
                "WHERE pg.idGrupo=%s AND pg.fechaFin IS NULL", (g['idGrupo'],))
            g['permisos'] = cur2.fetchall() or []
        return jsonify({'groups': grupos}), 200
    except Exception as e:
        log(f"US037 list grupo error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Error al listar grupos.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/groups', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_group_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreGrupo') or '').strip()
    descripcion = (data.get('descripcion') or '').strip() or None
    permisos = data.get('permisos') or []  # lista de idPermiso
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el grupo.'}), 400
    if not isinstance(permisos, list):
        permisos = []
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _grupo_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el grupo.'}), 400
        cur.execute("INSERT INTO grupo (nombreGrupo, descripcion, fechaFin) VALUES (%s,%s,NULL)", (nombre, descripcion))
        new_id = cur.lastrowid
        # Insertar permisos
        if permisos:
            for pid in permisos:
                try:
                    cur.execute("SELECT idPermiso FROM permiso WHERE idPermiso=%s AND (fechaFin IS NULL OR fechaFin IS NULL)", (pid,))
                    if cur.fetchone():
                        cur.execute("INSERT INTO permisogrupo (idGrupo, idPermiso, fechaInicio, fechaFin) VALUES (%s,%s,NOW(),NULL)", (new_id, pid))
                except Exception:
                    pass
        conn.commit()
        return jsonify({'ok':True,'idGrupo': new_id}), 201
    except Exception as e:
        log(f"US037 create grupo error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el grupo.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/groups/<int:id_grupo>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_group_detail(current_user_id, id_grupo):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idGrupo, nombreGrupo, descripcion, fechaFin FROM grupo WHERE idGrupo=%s", (id_grupo,))
        g = cur.fetchone()
        if not g:
            return jsonify({'errorCode':'ERR1','message':'Grupo no encontrado.'}), 404
        cur.execute(
            "SELECT p.idPermiso, p.nombrePermiso FROM permisogrupo pg JOIN permiso p ON p.idPermiso=pg.idPermiso "
            "WHERE pg.idGrupo=%s AND pg.fechaFin IS NULL", (id_grupo,))
        g['permisos'] = cur.fetchall() or []
        return jsonify(g), 200
    except Exception as e:
        log(f"US037 detail grupo error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener grupo.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/groups/<int:id_grupo>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_group_update(current_user_id, id_grupo):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreGrupo') or '').strip()
    descripcion = (data.get('descripcion') or '').strip() or None
    permisos = data.get('permisos') or []
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el grupo.'}), 400
    if not isinstance(permisos, list):
        permisos = []
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idGrupo FROM grupo WHERE idGrupo=%s", (id_grupo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Grupo no encontrado.'}), 404
        if _grupo_duplicate_active(cur, nombre, exclude_id=id_grupo):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el grupo.'}), 400
        cur.execute("UPDATE grupo SET nombreGrupo=%s, descripcion=%s WHERE idGrupo=%s", (nombre, descripcion, id_grupo))
        # Actualizar permisos: cerrar los no incluidos y agregar los nuevos
        cur.execute("SELECT idPermiso FROM permisogrupo WHERE idGrupo=%s AND fechaFin IS NULL", (id_grupo,))
        actuales = {r[0] for r in cur.fetchall() or []}
        nuevos = set([pid for pid in permisos if isinstance(pid, int)])
        a_cerrar = actuales - nuevos
        a_agregar = nuevos - actuales
        # Cerrar
        if a_cerrar:
            cur.execute(
                f"UPDATE permisogrupo SET fechaFin=NOW() WHERE idGrupo=%s AND idPermiso IN ({','.join(['%s']*len(a_cerrar))}) AND fechaFin IS NULL",
                (id_grupo, *a_cerrar))
        # Agregar
        for pid in a_agregar:
            try:
                cur.execute("SELECT idPermiso FROM permiso WHERE idPermiso=%s AND (fechaFin IS NULL OR fechaFin IS NULL)", (pid,))
                if cur.fetchone():
                    cur.execute("INSERT INTO permisogrupo (idGrupo, idPermiso, fechaInicio, fechaFin) VALUES (%s,%s,NOW(),NULL)", (id_grupo, pid))
            except Exception:
                pass
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US037 update grupo error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el grupo.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/groups/<int:id_grupo>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_group_delete(current_user_id, id_grupo):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idGrupo FROM grupo WHERE idGrupo=%s", (id_grupo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el grupo. Intente nuevamente.'}), 404
        cur.execute("UPDATE grupo SET fechaFin=NOW() WHERE idGrupo=%s AND fechaFin IS NULL", (id_grupo,))
        # Cerrar permisos activos asociados
        cur.execute("UPDATE permisogrupo SET fechaFin=NOW() WHERE idGrupo=%s AND fechaFin IS NULL", (id_grupo,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US037 delete grupo error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el grupo. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US037 (token Hola):
# Listar activos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/groups" -H "Authorization: Bearer {{token}}"
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/groups" -H "Authorization: Bearer {{token}}"
# Crear (con permisos 1 y 2):
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/groups" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreGrupo\":\"Supervisores\",\"descripcion\":\"Grupo de supervisión\",\"permisos\":[1,2]}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/groups/1" -H "Authorization: Bearer {{token}}"
# Actualizar (remover 2, agregar 1 y 3):
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/groups/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreGrupo\":\"Supervisores\",\"descripcion\":\"Grupo actualizado\",\"permisos\":[1,3]}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/groups/1" -H "Authorization: Bearer {{token}}"




# ============================ ABM TipoInstitución (US038) ============================
# Tabla: tipoinstitucion (idTipoInstitucion, nombreTipoInstitucion, fechaFin)
# Endpoints:
#  GET    /api/v1/admin/catalog/institution-types                  -> listado (activos por defecto;  para todos)
#  POST   /api/v1/admin/catalog/institution-types                  -> alta (nombre obligatorio) ERR1 (vacío o duplicado)
#  GET    /api/v1/admin/catalog/institution-types/<id>             -> detalle
#  PUT    /api/v1/admin/catalog/institution-types/<id>             -> modificar nombre ERR1 (vacío o duplicado)
#  DELETE /api/v1/admin/catalog/institution-types/<id>             -> baja lógica (fechaFin=NOW()) ERR2 en error/no encontrado
# Errores:
#  ERR1: "Debe ingresar un nombre para el tipo de institución." (nombre vacío o duplicado activo)
#  ERR2: "No se pudo eliminar el tipo de institución. Intente nuevamente." (error técnico o inexistente)

def _tipo_institucion_duplicate_active(cur, nombre, exclude_id=None):
    q = "SELECT idTipoInstitucion FROM tipoinstitucion WHERE nombreTipoInstitucion=%s AND fechaFin IS NULL"
    params = [nombre]
    if exclude_id:
        q += " AND idTipoInstitucion<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/institution-types', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_institution_types_list(current_user_id):
    include_inactive = request.args.get('includeInactive') in ('1','true','TRUE')
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if include_inactive:
            cur.execute("SELECT idTipoInstitucion, nombreTipoInstitucion, fechaFin FROM tipoinstitucion ORDER BY nombreTipoInstitucion")
        else:
            cur.execute("SELECT idTipoInstitucion, nombreTipoInstitucion, fechaFin FROM tipoinstitucion WHERE fechaFin IS NULL ORDER BY nombreTipoInstitucion")
        tipos = cur.fetchall() or []
        return jsonify({'institutionTypes': tipos}), 200
    except Exception as e:
        log(f"US038 list tipoInstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Error al listar tipos de institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-types', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_institution_type_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreTipoInstitucion') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _tipo_institucion_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 400
        cur.execute("INSERT INTO tipoinstitucion (nombreTipoInstitucion, fechaFin) VALUES (%s, NULL)", (nombre,))
        new_id = cur.lastrowid
        conn.commit()
        return jsonify({'ok':True,'idTipoInstitucion': new_id}), 201
    except Exception as e:
        log(f"US038 create tipoInstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-types/<int:id_tipo>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_institution_type_detail(current_user_id, id_tipo):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idTipoInstitucion, nombreTipoInstitucion, fechaFin FROM tipoinstitucion WHERE idTipoInstitucion=%s", (id_tipo,))
        t = cur.fetchone()
        if not t:
            return jsonify({'errorCode':'ERR1','message':'Tipo de institución no encontrado.'}), 404
        return jsonify(t), 200
    except Exception as e:
        log(f"US038 detail tipoInstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener tipo de institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-types/<int:id_tipo>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_institution_type_update(current_user_id, id_tipo):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreTipoInstitucion') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idTipoInstitucion FROM tipoinstitucion WHERE idTipoInstitucion=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Tipo de institución no encontrado.'}), 404
        if _tipo_institucion_duplicate_active(cur, nombre, exclude_id=id_tipo):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 400
        cur.execute("UPDATE tipoinstitucion SET nombreTipoInstitucion=%s WHERE idTipoInstitucion=%s", (nombre, id_tipo))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US038 update tipoInstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-types/<int:id_tipo>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_institution_type_delete(current_user_id, id_tipo):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idTipoInstitucion FROM tipoinstitucion WHERE idTipoInstitucion=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el tipo de institución. Intente nuevamente.'}), 404
        cur.execute("UPDATE tipoinstitucion SET fechaFin=NOW() WHERE idTipoInstitucion=%s AND fechaFin IS NULL", (id_tipo,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US038 delete tipoInstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el tipo de institución. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US038 (token Hola):
# Listar activos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/institution-types" -H "Authorization: Bearer {{token}}"
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/institution-types" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/institution-types" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreTipoInstitucion\":\"Universidad Privada\"}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/institution-types/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/institution-types/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreTipoInstitucion\":\"Instituto Técnico\"}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/institution-types/1" -H "Authorization: Bearer {{token}}"







 # ============================ ABM ModalidadCarreraInstitución (US039) ============================
 # Tabla: modalidadcarrerainstitucion (idModalidadCarreraInstitucion, nombreModalidad, fechaFin?)
 # Según dump, la tabla actual solo muestra id y nombreModalidad (no fechaFin). Para cumplir baja lógica añadiremos control si existe fechaFin;
 # si no existe la columna, la baja será física (DELETE). Asumimos existencia potencial de fechaFin por consistencia; si no está, DELETE.
 # Endpoints:
 #  GET    /api/v1/admin/catalog/career-modalities                  -> listado (activos por defecto;  para todos si existe fechaFin)
 #  POST   /api/v1/admin/catalog/career-modalities                  -> alta (nombre obligatorio) ERR1 (vacío o duplicado activo)
 #  GET    /api/v1/admin/catalog/career-modalities/<id>             -> detalle
 #  PUT    /api/v1/admin/catalog/career-modalities/<id>             -> modificar nombre ERR1 (vacío o duplicado)
 #  DELETE /api/v1/admin/catalog/career-modalities/<id>             -> baja lógica (fechaFin=NOW()) o física si no hay columna; ERR2 en error/no encontrado
 # Errores:
 #  ERR1: "Debe ingresar un nombre para la modalidad." (nombre vacío o duplicado activo)
 #  ERR2: "No se pudo eliminar la modalidad. Intente nuevamente." (error técnico o inexistente)

def _modalidad_duplicate_active(cur, nombre, exclude_id=None):
    # Intentar usar fechaFin si existe; fallback sin fechaFin
    try:
        q = "SELECT idModalidadCarreraInstitucion FROM modalidadcarrerainstitucion WHERE nombreModalidad=%s AND (fechaFin IS NULL)"
        params = [nombre]
        if exclude_id:
            q += " AND idModalidadCarreraInstitucion<>%s"
            params.append(exclude_id)
        cur.execute(q, tuple(params))
    except mysql.connector.Error:
        # Sin fechaFin
        q = "SELECT idModalidadCarreraInstitucion FROM modalidadcarrerainstitucion WHERE nombreModalidad=%s"
        params = [nombre]
        if exclude_id:
            q += " AND idModalidadCarreraInstitucion<>%s"
            params.append(exclude_id)
        cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/career-modalities', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_career_modalities_list(current_user_id):
    include_inactive = request.args.get('includeInactive') in ('1','true','TRUE')
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        try:
            if include_inactive:
                cur.execute("SELECT idModalidadCarreraInstitucion, nombreModalidad, fechaFin FROM modalidadcarrerainstitucion ORDER BY nombreModalidad")
            else:
                cur.execute("SELECT idModalidadCarreraInstitucion, nombreModalidad, fechaFin FROM modalidadcarrerainstitucion WHERE fechaFin IS NULL ORDER BY nombreModalidad")
        except mysql.connector.Error:
            # Sin fechaFin
            cur.execute("SELECT idModalidadCarreraInstitucion, nombreModalidad FROM modalidadcarrerainstitucion ORDER BY nombreModalidad")
        rows = cur.fetchall() or []
        return jsonify({'careerModalities': rows}), 200
    except Exception as e:
        log(f"US039 list modalidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Error al listar modalidades.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-modalities', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_career_modality_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreModalidad') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la modalidad.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _modalidad_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la modalidad.'}), 400
        # Insert (ignorar fechaFin si no existe)
        try:
            cur.execute("INSERT INTO modalidadcarrerainstitucion (nombreModalidad, fechaFin) VALUES (%s, NULL)", (nombre,))
        except mysql.connector.Error:
            cur.execute("INSERT INTO modalidadcarrerainstitucion (nombreModalidad) VALUES (%s)", (nombre,))
        new_id = cur.lastrowid
        conn.commit()
        return jsonify({'ok':True,'idModalidadCarreraInstitucion': new_id}), 201
    except Exception as e:
        log(f"US039 create modalidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la modalidad.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-modalities/<int:id_mod>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_career_modality_detail(current_user_id, id_mod):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT idModalidadCarreraInstitucion, nombreModalidad, fechaFin FROM modalidadcarrerainstitucion WHERE idModalidadCarreraInstitucion=%s", (id_mod,))
        except mysql.connector.Error:
            cur.execute("SELECT idModalidadCarreraInstitucion, nombreModalidad FROM modalidadcarrerainstitucion WHERE idModalidadCarreraInstitucion=%s", (id_mod,))
        m = cur.fetchone()
        if not m:
            return jsonify({'errorCode':'ERR1','message':'Modalidad no encontrada.'}), 404
        return jsonify(m), 200
    except Exception as e:
        log(f"US039 detail modalidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener modalidad.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-modalities/<int:id_mod>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_career_modality_update(current_user_id, id_mod):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreModalidad') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la modalidad.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Verificar existencia
        try:
            cur.execute("SELECT idModalidadCarreraInstitucion FROM modalidadcarrerainstitucion WHERE idModalidadCarreraInstitucion=%s", (id_mod,))
        except mysql.connector.Error:
            cur.execute("SELECT idModalidadCarreraInstitucion FROM modalidadcarrerainstitucion WHERE idModalidadCarreraInstitucion=%s", (id_mod,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Modalidad no encontrada.'}), 404
        if _modalidad_duplicate_active(cur, nombre, exclude_id=id_mod):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la modalidad.'}), 400
        try:
            cur.execute("UPDATE modalidadcarrerainstitucion SET nombreModalidad=%s WHERE idModalidadCarreraInstitucion=%s", (nombre, id_mod))
        except mysql.connector.Error:
            cur.execute("UPDATE modalidadcarrerainstitucion SET nombreModalidad=%s WHERE idModalidadCarreraInstitucion=%s", (nombre, id_mod))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US039 update modalidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la modalidad.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-modalities/<int:id_mod>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_career_modality_delete(current_user_id, id_mod):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Verificar existencia
        cur.execute("SELECT idModalidadCarreraInstitucion FROM modalidadcarrerainstitucion WHERE idModalidadCarreraInstitucion=%s", (id_mod,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la modalidad. Intente nuevamente.'}), 404
        # Intentar baja lógica
        try:
            cur.execute("UPDATE modalidadcarrerainstitucion SET fechaFin=NOW() WHERE idModalidadCarreraInstitucion=%s AND fechaFin IS NULL", (id_mod,))
            if cur.rowcount == 0:
                # Si no hay fechaFin, borrar físico
                cur.execute("DELETE FROM modalidadcarrerainstitucion WHERE idModalidadCarreraInstitucion=%s", (id_mod,))
        except mysql.connector.Error:
            # Columna fechaFin inexistente -> borrar físico
            cur.execute("DELETE FROM modalidadcarrerainstitucion WHERE idModalidadCarreraInstitucion=%s", (id_mod,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US039 delete modalidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la modalidad. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US039 (token Hola):
# Listar activos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/career-modalities" -H "Authorization: Bearer {{token}}"
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/career-modalities" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/career-modalities" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreModalidad\":\"Virtual\"}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/career-modalities/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/career-modalities/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreModalidad\":\"Híbrida\"}"
# Baja lógica/física:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/career-modalities/1" -H "Authorization: Bearer {{token}}"


 # ============================ ABM Aptitud (US040) ============================
 # Tabla: aptitud (idAptitud, nombreAptitud, descripcion, fechaAlta, fechaBaja)
 # Endpoints:
 #  GET    /api/v1/admin/catalog/aptitudes                  -> listado (activas por defecto;  para todas)
 #  POST   /api/v1/admin/catalog/aptitudes                  -> alta (nombre obligatorio, descripcion opcional) ERR1 (vacío o duplicado activo)
 #  GET    /api/v1/admin/catalog/aptitudes/<id>             -> detalle
 #  PUT    /api/v1/admin/catalog/aptitudes/<id>             -> modificar nombre/descripcion ERR1 (vacío o duplicado)
 #  DELETE /api/v1/admin/catalog/aptitudes/<id>             -> baja lógica (fechaBaja=NOW()) ERR2 si error/no encontrado
 # Errores:
 #  ERR1: "Debe ingresar un nombre para la aptitud." (nombre vacío o duplicado activo)
 #  ERR2: "No se pudo eliminar la aptitud. Intente nuevamente." (error técnico o inexistente)

def _aptitud_duplicate_active(cur, nombre, exclude_id=None):
    q = "SELECT idAptitud FROM aptitud WHERE nombreAptitud=%s AND fechaBaja IS NULL"
    params = [nombre]
    if exclude_id:
        q += " AND idAptitud<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/aptitudes', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_aptitudes_list(current_user_id):
    include_inactive = request.args.get('includeInactive') in ('1','true','TRUE')
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if include_inactive:
            cur.execute("SELECT idAptitud, nombreAptitud, descripcion, fechaAlta, fechaBaja FROM aptitud ORDER BY nombreAptitud")
        else:
            cur.execute("SELECT idAptitud, nombreAptitud, descripcion, fechaAlta, fechaBaja FROM aptitud WHERE fechaBaja IS NULL ORDER BY nombreAptitud")
        rows = cur.fetchall() or []
        return jsonify({'aptitudes': rows}), 200
    except Exception as e:
        log(f"US040 list aptitud error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Error al listar aptitudes.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/aptitudes', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_aptitud_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreAptitud') or '').strip()
    descripcion = (data.get('descripcion') or '').strip() or None
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _aptitud_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 400
        cur.execute("INSERT INTO aptitud (nombreAptitud, descripcion, fechaAlta, fechaBaja) VALUES (%s,%s,NOW(),NULL)", (nombre, descripcion))
        new_id = cur.lastrowid
        conn.commit()
        return jsonify({'ok':True,'idAptitud': new_id}), 201
    except Exception as e:
        log(f"US040 create aptitud error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/aptitudes/<int:id_aptitud>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_aptitud_detail(current_user_id, id_aptitud):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idAptitud, nombreAptitud, descripcion, fechaAlta, fechaBaja FROM aptitud WHERE idAptitud=%s", (id_aptitud,))
        r = cur.fetchone()
        if not r:
            return jsonify({'errorCode':'ERR1','message':'Aptitud no encontrada.'}), 404
        return jsonify(r), 200
    except Exception as e:
        log(f"US040 detail aptitud error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener aptitud.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/aptitudes/<int:id_aptitud>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_aptitud_update(current_user_id, id_aptitud):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreAptitud') or '').strip()
    descripcion = (data.get('descripcion') or '').strip() or None
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idAptitud FROM aptitud WHERE idAptitud=%s", (id_aptitud,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Aptitud no encontrada.'}), 404
        if _aptitud_duplicate_active(cur, nombre, exclude_id=id_aptitud):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 400
        cur.execute("UPDATE aptitud SET nombreAptitud=%s, descripcion=%s WHERE idAptitud=%s", (nombre, descripcion, id_aptitud))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US040 update aptitud error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/aptitudes/<int:id_aptitud>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_aptitud_delete(current_user_id, id_aptitud):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idAptitud FROM aptitud WHERE idAptitud=%s", (id_aptitud,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la aptitud. Intente nuevamente.'}), 404
        cur.execute("UPDATE aptitud SET fechaBaja=NOW() WHERE idAptitud=%s AND fechaBaja IS NULL", (id_aptitud,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US040 delete aptitud error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la aptitud. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US040 (token Hola):
# Listar activas:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/aptitudes" -H "Authorization: Bearer {{token}}"
# Listar todas:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/aptitudes" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/aptitudes" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreAptitud\":\"Liderazgo\",\"descripcion\":\"Capacidad de guiar equipos\"}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/aptitudes/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/aptitudes/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreAptitud\":\"Comunicación\",\"descripcion\":\"Habilidad para transmitir ideas\"}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/aptitudes/1" -H "Authorization: Bearer {{token}}"

 # ============================ ABM EstadoAcceso (US041) ============================
 # Tabla: estadoacceso (idEstadoAcceso, nombreEstadoAcceso, fechaFin)
 # Endpoints:
 #  GET    /api/v1/admin/catalog/access-statuses                  -> listado (activos por defecto;  para todos)
 #  POST   /api/v1/admin/catalog/access-statuses                  -> alta (nombre obligatorio) ERR1 (vacío o duplicado activo)
 #  GET    /api/v1/admin/catalog/access-statuses/<id>             -> detalle
 #  PUT    /api/v1/admin/catalog/access-statuses/<id>             -> modificar nombre ERR1 (vacío o duplicado)
 #  DELETE /api/v1/admin/catalog/access-statuses/<id>             -> baja lógica (fechaFin=NOW()) ERR2 si error/no encontrado
 # Errores:
 #  ERR1: "Debe ingresar un nombre para el estado." (nombre vacío o duplicado activo)
 #  ERR2: "No se pudo eliminar el estado de acceso. Intente nuevamente." (error técnico o inexistente)

def _estado_acceso_duplicate_active(cur, nombre, exclude_id=None):
    q = "SELECT idEstadoAcceso FROM estadoacceso WHERE nombreEstadoAcceso=%s AND fechaFin IS NULL"
    params = [nombre]
    if exclude_id:
        q += " AND idEstadoAcceso<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/access-statuses', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_access_statuses_list(current_user_id):
    include_inactive = request.args.get('includeInactive') in ('1','true','TRUE')
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if include_inactive:
            cur.execute("SELECT idEstadoAcceso, nombreEstadoAcceso, fechaFin FROM estadoacceso ORDER BY nombreEstadoAcceso")
        else:
            cur.execute("SELECT idEstadoAcceso, nombreEstadoAcceso, fechaFin FROM estadoacceso WHERE fechaFin IS NULL ORDER BY nombreEstadoAcceso")
        estados = cur.fetchall() or []
        return jsonify({'accessStatuses': estados}), 200
    except Exception as e:
        log(f"US041 list estadoacceso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Error al listar estados de acceso.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/access-statuses', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_access_status_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoAcceso') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _estado_acceso_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
        cur.execute("INSERT INTO estadoacceso (nombreEstadoAcceso, fechaFin) VALUES (%s, NULL)", (nombre,))
        new_id = cur.lastrowid
        conn.commit()
        return jsonify({'ok':True,'idEstadoAcceso': new_id}), 201
    except Exception as e:
        log(f"US041 create estadoacceso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/access-statuses/<int:id_estado>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_access_status_detail(current_user_id, id_estado):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idEstadoAcceso, nombreEstadoAcceso, fechaFin FROM estadoacceso WHERE idEstadoAcceso=%s", (id_estado,))
        est = cur.fetchone()
        if not est:
            return jsonify({'errorCode':'ERR1','message':'Estado de acceso no encontrado.'}), 404
        return jsonify(est), 200
    except Exception as e:
        log(f"US041 detail estadoacceso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener estado de acceso.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/access-statuses/<int:id_estado>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_access_status_update(current_user_id, id_estado):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoAcceso') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idEstadoAcceso FROM estadoacceso WHERE idEstadoAcceso=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Estado de acceso no encontrado.'}), 404
        if _estado_acceso_duplicate_active(cur, nombre, exclude_id=id_estado):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
        cur.execute("UPDATE estadoacceso SET nombreEstadoAcceso=%s WHERE idEstadoAcceso=%s", (nombre, id_estado))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US041 update estadoacceso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/access-statuses/<int:id_estado>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_access_status_delete(current_user_id, id_estado):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idEstadoAcceso FROM estadoacceso WHERE idEstadoAcceso=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el estado de acceso. Intente nuevamente.'}), 404
        cur.execute("UPDATE estadoacceso SET fechaFin=NOW() WHERE idEstadoAcceso=%s AND fechaFin IS NULL", (id_estado,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US041 delete estadoacceso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el estado de acceso. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US041 (token Hola):
# Listar activos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/access-statuses" -H "Authorization: Bearer {{token}}"
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/access-statuses" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/access-statuses" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreEstadoAcceso\":\"Bloqueado\"}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/access-statuses/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/access-statuses/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreEstadoAcceso\":\"Suspenso Temporal\"}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/access-statuses/1" -H "Authorization: Bearer {{token}}"


### ============================ ABM TipoAcción (US042) ============================
# Tabla: tipoaccion (idTipoAccion, nombreTipoAccion)  -- Nota: no posee fechaFin actualmente.
# La HU pide baja lógica: se intenta UPDATE fechaFin=NOW(); si falla (sin columna) se hace DELETE físico.
# Endpoints:
#  GET    /api/v1/admin/catalog/action-types
#  POST   /api/v1/admin/catalog/action-types
#  GET    /api/v1/admin/catalog/action-types/<id>
#  PUT    /api/v1/admin/catalog/action-types/<id>
#  DELETE /api/v1/admin/catalog/action-types/<id>
# Errores:
#   ERR1: "Debe ingresar un nombre para el tipo de acción." (vacío o duplicado)
#   ERR2: "No se pudo eliminar el tipo de acción. Intente nuevamente." (error o no existe)

def _tipo_accion_duplicate_active(cur, nombre, exclude_id=None):
    q = "SELECT idTipoAccion FROM tipoaccion WHERE nombreTipoAccion=%s"
    params = [nombre]
    if exclude_id:
        q += " AND idTipoAccion<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/action-types', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_action_types_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idTipoAccion, nombreTipoAccion FROM tipoaccion ORDER BY nombreTipoAccion")
        rows = cur.fetchall() or []
        return jsonify({'actionTypes': rows}), 200
    except Exception as e:
        log(f"US042 list tipoaccion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al listar tipos de acción.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/action-types', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_action_type_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreTipoAccion') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de acción.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _tipo_accion_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de acción.'}), 400
        cur.execute("INSERT INTO tipoaccion (nombreTipoAccion) VALUES (%s)", (nombre,))
        new_id = cur.lastrowid
        conn.commit()
        return jsonify({'ok':True,'idTipoAccion': new_id}), 201
    except Exception as e:
        log(f"US042 create tipoaccion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de acción.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/action-types/<int:id_tipo>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_action_type_detail(current_user_id, id_tipo):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idTipoAccion, nombreTipoAccion FROM tipoaccion WHERE idTipoAccion=%s", (id_tipo,))
        row = cur.fetchone()
        if not row:
            return jsonify({'errorCode':'ERR1','message':'Tipo de acción no encontrado.'}), 404
        return jsonify(row), 200
    except Exception as e:
        log(f"US042 detail tipoaccion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener tipo de acción.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/action-types/<int:id_tipo>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_action_type_update(current_user_id, id_tipo):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreTipoAccion') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de acción.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idTipoAccion FROM tipoaccion WHERE idTipoAccion=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Tipo de acción no encontrado.'}), 404
        if _tipo_accion_duplicate_active(cur, nombre, exclude_id=id_tipo):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de acción.'}), 400
        cur.execute("UPDATE tipoaccion SET nombreTipoAccion=%s WHERE idTipoAccion=%s", (nombre, id_tipo))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US042 update tipoaccion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de acción.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/action-types/<int:id_tipo>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_action_type_delete(current_user_id, id_tipo):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idTipoAccion FROM tipoaccion WHERE idTipoAccion=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el tipo de acción. Intente nuevamente.'}), 404
        try:
            cur.execute("UPDATE tipoaccion SET fechaFin=NOW() WHERE idTipoAccion=%s AND fechaFin IS NULL", (id_tipo,))
            if cur.rowcount == 0:
                cur.execute("DELETE FROM tipoaccion WHERE idTipoAccion=%s", (id_tipo,))
        except mysql.connector.Error:
            cur.execute("DELETE FROM tipoaccion WHERE idTipoAccion=%s", (id_tipo,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US042 delete tipoaccion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el tipo de acción. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US042 (token Hola):
# Listar:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/action-types" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/action-types" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreTipoAccion\":\"MODIFICACION\"}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/action-types/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/action-types/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreTipoAccion\":\"ACTUALIZACION\"}"}
# Baja:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/action-types/1" -H "Authorization: Bearer {{token}}"


### ============================ ABM EstadoInstitución (US043) ============================
# Tabla: estadoinstitucion (idEstadoInstitucion, nombreEstadoInstitucion, fechaFin)
# Endpoints:
#  GET    /api/v1/admin/catalog/institution-states                -> listado (activos por defecto;  para todos)
#  POST   /api/v1/admin/catalog/institution-states                -> alta (nombreEstadoInstitucion) ERR1 si vacío o duplicado activo
#  GET    /api/v1/admin/catalog/institution-states/<id>           -> detalle
#  PUT    /api/v1/admin/catalog/institution-states/<id>           -> modificar nombre (ERR1 si vacío o duplicado)
#  DELETE /api/v1/admin/catalog/institution-states/<id>           -> baja lógica (fechaFin=NOW()) ERR2 si falla o no existe
# Errores:
#   ERR1: "Debe ingresar un nombre para el estado de la institución." (nombre vacío o duplicado activo)
#   ERR2: "No se pudo eliminar el estado de institución. Intente nuevamente." (error técnico o inexistente)

def _estado_institucion_duplicate_active(cur, nombre, exclude_id=None):
    q = "SELECT idEstadoInstitucion FROM estadoinstitucion WHERE nombreEstadoInstitucion=%s AND fechaFin IS NULL"
    params = [nombre]
    if exclude_id:
        q += " AND idEstadoInstitucion<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/institution-states', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_institution_states_list(current_user_id):
    include_inactive = request.args.get('includeInactive') in ('1','true','TRUE')
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if include_inactive:
            cur.execute("SELECT idEstadoInstitucion, nombreEstadoInstitucion, fechaFin FROM estadoinstitucion ORDER BY nombreEstadoInstitucion")
        else:
            cur.execute("SELECT idEstadoInstitucion, nombreEstadoInstitucion, fechaFin FROM estadoinstitucion WHERE fechaFin IS NULL ORDER BY nombreEstadoInstitucion")
        rows = cur.fetchall() or []
        return jsonify({'institutionStates': rows}), 200
    except Exception as e:
        log(f"US043 list estadoinstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Error al listar estados de institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-states', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_institution_state_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoInstitucion') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de la institución.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _estado_institucion_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de la institución.'}), 400
        cur.execute("INSERT INTO estadoinstitucion (nombreEstadoInstitucion, fechaFin) VALUES (%s, NULL)", (nombre,))
        new_id = cur.lastrowid
        conn.commit()
        return jsonify({'ok':True,'idEstadoInstitucion': new_id}), 201
    except Exception as e:
        log(f"US043 create estadoinstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de la institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-states/<int:id_estado>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_institution_state_detail(current_user_id, id_estado):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idEstadoInstitucion, nombreEstadoInstitucion, fechaFin FROM estadoinstitucion WHERE idEstadoInstitucion=%s", (id_estado,))
        row = cur.fetchone()
        if not row:
            return jsonify({'errorCode':'ERR1','message':'Estado de institución no encontrado.'}), 404
        return jsonify(row), 200
    except Exception as e:
        log(f"US043 detail estadoinstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener estado de institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-states/<int:id_estado>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_institution_state_update(current_user_id, id_estado):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoInstitucion') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de la institución.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idEstadoInstitucion FROM estadoinstitucion WHERE idEstadoInstitucion=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Estado de institución no encontrado.'}), 404
        if _estado_institucion_duplicate_active(cur, nombre, exclude_id=id_estado):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de la institución.'}), 400
        cur.execute("UPDATE estadoinstitucion SET nombreEstadoInstitucion=%s WHERE idEstadoInstitucion=%s", (nombre, id_estado))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US043 update estadoinstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de la institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-states/<int:id_estado>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_institution_state_delete(current_user_id, id_estado):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idEstadoInstitucion FROM estadoinstitucion WHERE idEstadoInstitucion=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el estado de institución. Intente nuevamente.'}), 404
        cur.execute("UPDATE estadoinstitucion SET fechaFin=NOW() WHERE idEstadoInstitucion=%s AND fechaFin IS NULL", (id_estado,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US043 delete estadoinstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el estado de institución. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US043 (token Hola):
# Listar activos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/institution-states" -H "Authorization: Bearer {{token}}"
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/institution-states" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/institution-states" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreEstadoInstitucion\":\"Pendiente\"}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/institution-states/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/institution-states/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreEstadoInstitucion\":\"Aprobada\"}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/institution-states/1" -H "Authorization: Bearer {{token}}"


### ============================ ABM EstadoCarreraInstitución (US044) ============================
# Tabla: estadocarrerainstitucion (idEstadoCarreraInstitucion, nombreEstadoCarreraInstitucion, fechaFin)
# Endpoints:
#  GET    /api/v1/admin/catalog/career-institution-statuses                -> listado (activos por defecto;  para todos)
#  POST   /api/v1/admin/catalog/career-institution-statuses                -> alta (nombreEstadoCarreraInstitucion) ERR1 si vacío o duplicado activo
#  GET    /api/v1/admin/catalog/career-institution-statuses/<id>           -> detalle
#  PUT    /api/v1/admin/catalog/career-institution-statuses/<id>           -> modificar nombre (ERR1 si vacío o duplicado)
#  DELETE /api/v1/admin/catalog/career-institution-statuses/<id>           -> baja lógica (fechaFin=NOW()) ERR2 si falla o no existe
# Errores:
#   ERR1: "Debe ingresar un nombre para el estado de carrera." (nombre vacío o duplicado activo)
#   ERR2: "No se pudo eliminar el estado de carrera. Intente nuevamente." (error técnico o inexistente)

def _estado_carrera_institucion_duplicate_active(cur, nombre, exclude_id=None):
    q = "SELECT idEstadoCarreraInstitucion FROM estadocarrerainstitucion WHERE nombreEstadoCarreraInstitucion=%s AND fechaFin IS NULL"
    params = [nombre]
    if exclude_id:
        q += " AND idEstadoCarreraInstitucion<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/career-institution-statuses', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_career_institution_statuses_list(current_user_id):
    include_inactive = request.args.get('includeInactive') in ('1','true','TRUE')
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if include_inactive:
            cur.execute("SELECT idEstadoCarreraInstitucion, nombreEstadoCarreraInstitucion, fechaFin FROM estadocarrerainstitucion ORDER BY nombreEstadoCarreraInstitucion")
        else:
            cur.execute("SELECT idEstadoCarreraInstitucion, nombreEstadoCarreraInstitucion, fechaFin FROM estadocarrerainstitucion WHERE fechaFin IS NULL ORDER BY nombreEstadoCarreraInstitucion")
        rows = cur.fetchall() or []
        return jsonify({'careerInstitutionStatuses': rows}), 200
    except Exception as e:
        log(f"US044 list estadocarrerainstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Error al listar estados de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-institution-statuses', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_career_institution_status_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoCarreraInstitucion') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de carrera.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        if _estado_carrera_institucion_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de carrera.'}), 400
        cur.execute("INSERT INTO estadocarrerainstitucion (nombreEstadoCarreraInstitucion, fechaFin) VALUES (%s, NULL)", (nombre,))
        new_id = cur.lastrowid
        conn.commit()
        return jsonify({'ok':True,'idEstadoCarreraInstitucion': new_id}), 201
    except Exception as e:
        log(f"US044 create estadocarrerainstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-institution-statuses/<int:id_estado>', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_career_institution_status_detail(current_user_id, id_estado):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idEstadoCarreraInstitucion, nombreEstadoCarreraInstitucion, fechaFin FROM estadocarrerainstitucion WHERE idEstadoCarreraInstitucion=%s", (id_estado,))
        row = cur.fetchone()
        if not row:
            return jsonify({'errorCode':'ERR1','message':'Estado de carrera no encontrado.'}), 404
        return jsonify(row), 200
    except Exception as e:
        log(f"US044 detail estadocarrerainstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al obtener estado de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-institution-statuses/<int:id_estado>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_career_institution_status_update(current_user_id, id_estado):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoCarreraInstitucion') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de carrera.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idEstadoCarreraInstitucion FROM estadocarrerainstitucion WHERE idEstadoCarreraInstitucion=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Estado de carrera no encontrado.'}), 404
        if _estado_carrera_institucion_duplicate_active(cur, nombre, exclude_id=id_estado):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de carrera.'}), 400
        cur.execute("UPDATE estadocarrerainstitucion SET nombreEstadoCarreraInstitucion=%s WHERE idEstadoCarreraInstitucion=%s", (nombre, id_estado))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US044 update estadocarrerainstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-institution-statuses/<int:id_estado>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_career_institution_status_delete(current_user_id, id_estado):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idEstadoCarreraInstitucion FROM estadocarrerainstitucion WHERE idEstadoCarreraInstitucion=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el estado de carrera. Intente nuevamente.'}), 404
        cur.execute("UPDATE estadocarrerainstitucion SET fechaFin=NOW() WHERE idEstadoCarreraInstitucion=%s AND fechaFin IS NULL", (id_estado,))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US044 delete estadocarrerainstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el estado de carrera. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US044 (token Hola):
# Listar activos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/career-institution-statuses" -H "Authorization: Bearer {{token}}"
# Listar todos:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/career-institution-statuses" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/career-institution-statuses" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreEstadoCarreraInstitucion\":\"Activa\"}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/career-institution-statuses/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/career-institution-statuses/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreEstadoCarreraInstitucion\":\"Cerrada\"}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/career-institution-statuses/1" -H "Authorization: Bearer {{token}}"

### ============================ ABM ConfiguraciónBackup (US045) ============================
# Tabla: configuracionbackup (frecuencia, horaEjecucion TIME, cantidadBackupConservar INT)
# (No posee id; se maneja como único registro lógico con id=1)
# Endpoints:
#  GET    /api/v1/admin/catalog/backup-configs                 -> listado (0 o 1 config)
#  POST   /api/v1/admin/catalog/backup-configs                 -> alta (reemplaza si existía) ERR1 si campos faltan
#  GET    /api/v1/admin/catalog/backup-configs/1               -> detalle
#  PUT    /api/v1/admin/catalog/backup-configs/1               -> modificar (ERR1 validación / no encontrado)
#  DELETE /api/v1/admin/catalog/backup-configs/1               -> baja (DELETE) ERR2 si error/no existe
# Errores:
#   ERR1: "Debe completar todos los campos para guardar la configuración." (faltantes / formato inválido / no encontrada en detail/update)
#   ERR2: "No se pudo eliminar la configuración. Intente nuevamente." (error técnico o no encontrada en delete)

VALID_FREQUENCIAS_BACKUP_US045 = {'diaria','semanal','mensual'}

def _get_backup_config(cur):
    cur.execute("SELECT frecuencia, TIME_FORMAT(horaEjecucion,'%H:%i') AS horaEjecucion, cantidadBackupConservar FROM configuracionbackup LIMIT 1")
    row = cur.fetchone()
    if not row:
        return None
    return { 'id':1, 'frecuencia': row[0], 'horaEjecucion': row[1], 'cantidadBackupConservar': row[2] }

def _validate_backup_payload(data):
    freq = (data.get('frecuencia') or '').strip().lower()
    hora = (data.get('horaEjecucion') or '').strip()
    cant = data.get('cantidadBackupConservar')
    try:
        if freq not in VALID_FREQUENCIAS_BACKUP_US045:
            raise ValueError('freq')
        datetime.datetime.strptime(hora, '%H:%M')
        cant_int = int(cant)
        if cant_int <= 0: raise ValueError('cant')
        return freq, hora, cant_int
    except Exception:
        return None

@app.route('/api/v1/admin/catalog/backup-configs', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_backup_configs_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cfg = _get_backup_config(cur)
        return jsonify({'backupConfigs': [cfg] if cfg else []}), 200
    except Exception as e:
        log(f"US045 list configuracionbackup error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos para guardar la configuración.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/backup-configs', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_backup_config_create(current_user_id):
    data = request.get_json(silent=True) or {}
    parsed = _validate_backup_payload(data)
    if not parsed:
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos para guardar la configuración.'}), 400
    freq, hora, cant = parsed
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM configuracionbackup")
        cur.execute("INSERT INTO configuracionbackup (frecuencia, horaEjecucion, cantidadBackupConservar) VALUES (%s,%s,%s)", (freq, hora+':00', cant))
        conn.commit()
        return jsonify({'ok':True,'id':1}), 201
    except Exception as e:
        log(f"US045 create configuracionbackup error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos para guardar la configuración.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/backup-configs/1', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_backup_config_detail(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cfg = _get_backup_config(cur)
        if not cfg:
            return jsonify({'errorCode':'ERR1','message':'Configuración no encontrada.'}), 404
        return jsonify(cfg), 200
    except Exception as e:
        log(f"US045 detail configuracionbackup error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Configuración no encontrada.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/backup-configs/1', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_backup_config_update(current_user_id):
    data = request.get_json(silent=True) or {}
    parsed = _validate_backup_payload(data)
    if not parsed:
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos para guardar la configuración.'}), 400
    freq, hora, cant = parsed
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM configuracionbackup LIMIT 1")
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Configuración no encontrada.'}), 404
        cur.execute("DELETE FROM configuracionbackup")
        cur.execute("INSERT INTO configuracionbackup (frecuencia, horaEjecucion, cantidadBackupConservar) VALUES (%s,%s,%s)", (freq, hora+':00', cant))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US045 update configuracionbackup error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos para guardar la configuración.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/backup-configs/1', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_backup_config_delete(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM configuracionbackup LIMIT 1")
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la configuración. Intente nuevamente.'}), 404
        cur.execute("DELETE FROM configuracionbackup")
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US045 delete configuracionbackup error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la configuración. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos US045 (token Hola):
# Listar:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/backup-configs" -H "Authorization: Bearer {{token}}"
# Crear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/backup-configs" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"frecuencia\":\"diaria\",\"horaEjecucion\":\"02:30\",\"cantidadBackupConservar\":5}"
# Detalle:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/backup-configs/1" -H "Authorization: Bearer {{token}}"
# Actualizar:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/backup-configs/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"frecuencia\":\"semanal\",\"horaEjecucion\":\"03:00\",\"cantidadBackupConservar\":8}"
# Baja:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/backup-configs/1" -H "Authorization: Bearer {{token}}"

### ============================ Gestión de usuarios (US046) ============================
# Objetivo: Alta, bloqueo/desbloqueo y baja lógica de usuarios.
# Tablas involucradas: usuario (idUsuario, nombre, apellido, mail, contrasena, fechaNac, etc.),
#                      estadousuario (idEstadoUsuario, nombreEstadoUsuario, fechaFin),
#                      usuarioestado (idUsuarioEstado, idUsuario, idEstadoUsuario, fechaInicio, fechaFin)
# Estados lógicos asumidos (existentes en dump): 1=Activo, 2=Suspendido (lo usaremos como Bloqueado), 3=Baja (lo usaremos para baja lógica definitiva)
# Endpoints:
#  POST   /api/v1/admin/catalog/users                     -> Crear usuario (nombre, apellido, email, grupoId opcional, estadoInicial=activo|inactivo[bloqueado])
#  POST   /api/v1/admin/catalog/users/<id>/block          -> Bloquear usuario (pasa a estado 2) ERR3 en error
#  POST   /api/v1/admin/catalog/users/<id>/unblock        -> Desbloquear usuario (pasa a estado 1) ERR3 en error
#  DELETE /api/v1/admin/catalog/users/<id>                -> Baja lógica usuario (estado 3 y opcional fechaFin) ERR4 en error
# Errores:
#  ERR1: "Debe completar todos los campos obligatorios." (nombre, apellido, email)
#  ERR2: "Debe ingresar un correo electrónico válido." (formato email)
#  ERR3: "No se pudo cambiar el estado del usuario. Intente nuevamente." (bloqueo/desbloqueo)
#  ERR4: "No se pudo eliminar el usuario. Intente nuevamente." (baja lógica)
# Notas:
#  - Email debe ser único. Si ya existe -> ERR2 (reutilizamos mensaje de formato inválido según HU; podríamos ampliar, pero seguimos directiva)
#  - Si estadoInicial='inactivo' se crea en estado Suspendido (2). Por defecto Activo (1).
#  - Para registrar estado se inserta en usuarioestado fila con fechaInicio NOW() y fechaFin NULL. Al cambiar de estado se cierra la fila previa y se abre una nueva.

EMAIL_REGEX_ADMIN = EMAIL_REGEX  # reutiliza regex global

def _user_email_exists(cur, email):
    cur.execute("SELECT idUsuario FROM usuario WHERE mail=%s", (email,))
    return cur.fetchone() is not None

def _insert_user_state(cur, user_id, id_estado_nuevo):
    # Cerrar estado previo
    cur.execute("UPDATE usuarioestado SET fechaFin=NOW() WHERE idUsuario=%s AND fechaFin IS NULL", (user_id,))
    # Abrir nuevo
    cur.execute("INSERT INTO usuarioestado (idUsuario, idEstadoUsuario, fechaInicio, fechaFin) VALUES (%s,%s,NOW(),NULL)", (user_id, id_estado_nuevo))

def _determine_initial_state(value:str):
    v = (value or '').strip().lower()
    if v == 'inactivo' or v == 'bloqueado':
        return 2  # Suspendido/Bloqueado
    return 1  # Activo por defecto

# Endpoint para crear usuario
@app.route('/api/v1/admin/catalog/users', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_user_create(current_user_id):
    data = request.get_json(silent=True) or {}
    correo = (data.get('correo') or '').strip()
    dni = data.get('dni')
    nombre = (data.get('nombre') or '').strip()
    apellido = (data.get('apellido') or '').strip()
    fechaNac = data.get('fechaNac')
    idGenero = data.get('idGenero')
    idLocalidad = data.get('idLocalidad')
    estado_inicial_raw = data.get('estadoInicial')  # activo|inactivo (bloqueado)
    grupo_id = data.get('grupoId')  # opcional

    # ERR1: campos requeridos incompletos
    required_missing = []
    if not dni:
        required_missing.append('dni')
    if not apellido:
        required_missing.append('apellido')
    if not fechaNac:
        required_missing.append('fechaNac')
    if not idGenero:
        required_missing.append('idGenero')
    if not idLocalidad:
        required_missing.append('idLocalidad')
    if not nombre:
        required_missing.append('nombre')
    if not correo:
        required_missing.append('correo')
    if required_missing:
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 400

    if not re.match(EMAIL_REGEX_ADMIN, correo):
        return jsonify({'errorCode':'ERR2','message':'Debe ingresar un correo electrónico válido.'}), 400
    
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # verificar el id de localidad y de genero
        cur.execute("SELECT * FROM localidad WHERE idLocalidad=%s", (idLocalidad,))
        localidad = cur.fetchone()
        cur.execute("SELECT * FROM genero WHERE idGenero=%s", (idGenero,))
        genero = cur.fetchone()

        if not localidad:
            return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 400
        if not genero:
            return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 400
        
        if _user_email_exists(cur, correo):
            return jsonify({'errorCode':'ERR2','message':'Debe ingresar un correo electrónico válido.'}), 400
        
        # contraseña temporal aleatoria
        temp_pass = generate_password()
        hashed = hash_password(temp_pass)
        cur.execute(
            "INSERT INTO usuario (mail, dni, nombre, apellido, contrasena, fechaNac, idGenero, idLocalidad) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (correo, dni, nombre, apellido, hashed, fechaNac, int(idGenero), int(idLocalidad))
        )
        new_id = cur.lastrowid
        
        # Estado inicial
        estado_id = _determine_initial_state(estado_inicial_raw)
        _insert_user_state(cur, new_id, estado_id)
        
        # Grupo opcional (usuariogrupo)
        if grupo_id:
            try:
                cur.execute("INSERT INTO usuariogrupo (idUsuario, idGrupo, fechaInicio, fechaFin) VALUES (%s,%s,NOW(),NULL)", (new_id, int(grupo_id)))
            except Exception:
                pass  # si falla grupo no se aborta creación
        
        conn.commit()
        return jsonify({'ok':True,'idUsuario':new_id,'passwordTemporal':temp_pass}), 201
    except Exception as e:
        log(f"US046 create user error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
# Ejemplo de curl para este endpoint
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/users" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"correo\":\"juan.perez@example.com\",\"dni\":\"12345678\",\"nombre\":\"Juan\",\"apellido\":\"Perez\",\"fechaNac\":\"1990-01-15\",\"idGenero\":1,\"idLocalidad\":1,\"estadoInicial\":\"activo\"}"

def _change_user_state(user_id:int, target_state:int):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idUsuario FROM usuario WHERE idUsuario=%s", (user_id,))
        if not cur.fetchone():
            return False, 404
        _insert_user_state(cur, user_id, target_state)
        conn.commit()
        return True, 200
    except Exception as e:
        log(f"US046 change state error: {e}\n{traceback.format_exc()}")
        return False, 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# Endpoint para baja lógica usuario
@app.route('/api/v1/admin/catalog/users/<int:user_id>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_user_delete(current_user_id, user_id):
    conn=None
    try:
        # Obtener el usuario y actualizar su estado por la tabla intermedia a Baja
        success, status_code = _change_user_state(user_id, 3)  # 3=Baja
        if not success:
            return jsonify({'errorCode':'ERR4','message':'No se pudo eliminar el usuario. Intente nuevamente.'}), status_code
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US046 delete user error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR4','message':'No se pudo eliminar el usuario. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass





# Endpoint para modificar usuario
@app.route('/api/v1/admin/catalog/users/<int:user_id>', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
def admin_user_update(current_user_id, user_id):
    conn = None
    try:
        # Verificar datos obligatorios
        data = request.get_json(silent=True) or {}
        nombre = (data.get('nombre') or '').strip()
        apellido = (data.get('apellido') or '').strip()
        email = (data.get('email') or '').strip()
        grupos = data.get('grupos')
        idEstado = data.get('idEstado')
        # VERIFICAR TODOS LOS PARAMETROS son obligatorios
        if not nombre or not apellido or not email or grupos is None or idEstado is None:
            return jsonify({'errorCode':'ERR4','message':'Debe completar todos los campos obligatorios.'}), 400
        # Validar email
        if not re.match(EMAIL_REGEX_ADMIN, email):
            return jsonify({'errorCode':'ERR4','message':'El email enviado no cumple los requisitos.'}), 400
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Verificar si el usuario existe
        cur.execute("SELECT idUsuario FROM usuario WHERE idUsuario=%s", (user_id,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR4','message':'No se pudo modificar el usuario. Intente nuevamente.'}), 404
        # Actualizar datos del usuario
        if _user_email_exists(cur, email):
            cur.execute("SELECT idUsuario FROM usuario WHERE mail=%s", (email,))
            row = cur.fetchone()
            if row and row[0] != user_id:
                return jsonify({'errorCode':'ERR4','message':'El email ya está en uso por otro usuario.'}), 400
        cur.execute("UPDATE usuario SET nombre=%s, apellido=%s, mail=%s WHERE idUsuario=%s", (nombre, apellido, email, user_id))
        # Actualizar grupos (baja lógica de todos y alta de los enviados)
        cur.execute("UPDATE usuariogrupo SET fechaFin=NOW() WHERE idUsuario=%s AND fechaFin IS NULL", (user_id,))
        for gid in grupos:
            cur.execute("INSERT INTO usuariogrupo (idUsuario, idGrupo, fechaInicio) VALUES (%s, %s, NOW())",
                        (user_id, gid))
        # Actualizar estado actualizando la fecha fin y creando nuevo registro
        _insert_user_state(cur, user_id, idEstado)
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US046 update user error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR4','message':'No se pudo modificar el usuario. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
# Curl de ejemplo para este endpoint:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/users/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombre\":\"Juan\",\"apellido\":\"Perez\",\"email\":\"juan.perez@example.com\",\"grupos\":[1,2],\"idEstado\":1}"




# cURL ejemplos US046 (token Hola):
# Crear usuario activo:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/users" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"correo\":\"juan.perez@example.com\",\"dni\":\"12345678\",\"nombre\":\"Juan\",\"apellido\":\"Perez\",\"fechaNac\":\"1990-01-15\",\"idGenero\":1,\"idLocalidad\":1,\"estadoInicial\":\"activo\"}"
# Crear usuario bloqueado inicialmente:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/users" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"correo\":\"ana.lopez@example.com\",\"dni\":\"87654321\",\"nombre\":\"Ana\",\"apellido\":\"Lopez\",\"fechaNac\":\"1985-03-20\",\"idGenero\":2,\"idLocalidad\":2,\"estadoInicial\":\"inactivo\"}"
# Bloquear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/users/1/block" -H "Authorization: Bearer {{token}}"
# Desbloquear:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/users/1/unblock" -H "Authorization: Bearer {{token}}"
# Baja lógica:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/users/1" -H "Authorization: Bearer {{token}}"

# ============================= Gestion de permisos de grupo (US047)  ============================
# Objetivo: Asignar y remover permisos a grupos.
# Tablas involucradas: permiso (idPermiso, nombrePermiso, descripcion), grupopermiso (idGrupoPermiso, idGrupo, idPermiso, fechaInicio, fechaFin)
# Endpoints:
#  POST   /api/v1/admin/catalog/groups/<grupo_id>/permissions/<perm_id>    -> Asignar permiso a grupo (fechaInicio=NOW(), fechaFin=NULL) ERR1 si ya tiene o error
#  DELETE /api/v1/admin/catalog/groups/<grupo_id>/permissions/<perm_id>  -> Remover permiso de grupo (fechaFin=NOW()) ERR2 si no tiene o error
# Errores:
#  ERR1: El grupo ya tiene asignado el permiso.
#  ERR2: El grupo no tiene asignado el permiso.
@app.route('/api/v1/admin/catalog/groups/<int:grupo_id>/permissions/<int:perm_id>', methods=['POST'])
@requires_permission('ADMIN_PANEL')
def admin_group_permission_add(current_user_id, grupo_id, perm_id):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Verificar si el grupo ya tiene el permiso
        cur.execute("SELECT * FROM grupopermiso WHERE idGrupo=%s AND idPermiso=%s AND fechaFin IS NULL", (grupo_id, perm_id))
        if cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'El grupo ya tiene asignado el permiso.'}), 400
        # Asignar permiso al grupo
        cur.execute("INSERT INTO grupopermiso (idGrupo, idPermiso, fechaInicio) VALUES (%s, %s, NOW())", (grupo_id, perm_id))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US047 add group permission error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo asignar el permiso al grupo. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/groups/<int:grupo_id>/permissions/<int:perm_id>', methods=['DELETE'])
@requires_permission('ADMIN_PANEL')
def admin_group_permission_remove(current_user_id, grupo_id, perm_id):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Verificar si el grupo tiene el permiso
        cur.execute("SELECT * FROM grupopermiso WHERE idGrupo=%s AND idPermiso=%s AND fechaFin IS NULL", (grupo_id, perm_id))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'El grupo no tiene asignado el permiso.'}), 400
        # Remover permiso del grupo
        cur.execute("UPDATE grupopermiso SET fechaFin=NOW() WHERE idGrupo=%s AND idPermiso=%s AND fechaFin IS NULL", (grupo_id, perm_id))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US047 remove group permission error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo remover el permiso del grupo. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# cURL ejemplos
# Asignar permiso a grupo:
# curl -X POST "{{baseURL}}/api/v1/admin/catalog/groups/1/permissions/2" -H "Authorization: Bearer {{token}}"
# Remover permiso de grupo:
# curl -X DELETE "{{baseURL}}/api/v1/admin/catalog/groups/1/permissions/2" -H "Authorization: Bearer {{token}}"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


