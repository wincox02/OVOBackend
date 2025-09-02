from flask import Flask, request, jsonify, make_response, render_template_string
from flask_cors import CORS
import mysql.connector
import json
import requests
import hashlib
import decimal
import traceback
import os


# -----------------------------------JWT-----------------------------------
import jwt
import datetime
from functools import wraps
# -----------------------------------UUID-----------------------------------
import uuid
import re
#-----------------------------------PASSWORD-----------------------------------
import random
import string
#-----------------------------------SMTP gmail-----------------------------------
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#-----------------------------------Discord-----------------------------------

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, expose_headers=["new_token"])

# Configuración de MariaDB
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "ovo",
    "password": "1234",
    "database": "ovo"
}

def init_db():
    """Inicializa la base de datos MariaDB."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        -- --------------------------------------------------------
        -- Host:                         127.0.0.1
        -- Versión del servidor:         11.3.2-MariaDB - mariadb.org binary distribution
        -- SO del servidor:              Win64
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
        `fechaAlta` datetime DEFAULT NULL,
        `nombreAptitud` varchar(50) DEFAULT NULL,
        `descripcion` varchar(50) DEFAULT NULL,
        `fechaBaja` datetime DEFAULT NULL,
        PRIMARY KEY (`idAptitud`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.aptitud: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.aptitudcarrera
        CREATE TABLE IF NOT EXISTS `aptitudcarrera` (
        `idAptitudCarrera` int(11) NOT NULL AUTO_INCREMENT,
        `afinidadCarrera` double DEFAULT NULL,
        `idAptitud` int(11) DEFAULT NULL,
        `idCarreraInstitucion` int(11) DEFAULT NULL,
        PRIMARY KEY (`idAptitudCarrera`),
        KEY `FK_aptitudcarrera_aptitud` (`idAptitud`),
        KEY `FK_aptitudcarrera_carrera` (`idCarreraInstitucion`),
        CONSTRAINT `FK_aptitudcarrera_aptitud` FOREIGN KEY (`idAptitud`) REFERENCES `aptitud` (`idAptitud`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_aptitudcarrera_carrera` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrera` (`idCarrera`) ON DELETE NO ACTION ON UPDATE NO ACTION
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
        CONSTRAINT `FK_carrera_tipocarrera` FOREIGN KEY (`idTipoCarrera`) REFERENCES `tipocarrera` (`idTipoCarrera`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.carrera: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.carrerainstitucion
        CREATE TABLE IF NOT EXISTS `carrerainstitucion` (
        `idCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
        `cantidadMaterias` int(11) DEFAULT NULL,
        `duracionCarrera` decimal(20,2) DEFAULT NULL,
        `fechaFin` datetime DEFAULT NULL,
        `fechaInicio` datetime DEFAULT NULL,
        `horasCursado` int(11) DEFAULT NULL,
        `observaciones` varchar(500) DEFAULT NULL,
        `nombreCarrera` varchar(50) DEFAULT NULL,
        `tituloCarrera` varchar(50) DEFAULT NULL,
        `montoCuota` decimal(20,2) DEFAULT NULL,
        `idEstadoCarreraInstitucion` int(11) DEFAULT NULL,
        `idCarrera` int(11) DEFAULT NULL,
        `idPreguntaFrecuente` int(11) DEFAULT NULL,
        `idModalidadCarreraInstitucion` int(11) DEFAULT NULL,
        `idInstitucion` int(11) DEFAULT NULL,
        PRIMARY KEY (`idCarreraInstitucion`),
        KEY `FK_carrerainstitucion_estadocarrerainstitucion` (`idEstadoCarreraInstitucion`),
        KEY `FK_carrerainstitucion_carrera` (`idCarrera`),
        KEY `FK_carrerainstitucion_preguntafrecuente` (`idPreguntaFrecuente`),
        KEY `FK_carrerainstitucion_modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`),
        KEY `FK_carrerainstitucion_institucion` (`idInstitucion`),
        CONSTRAINT `FK_carrerainstitucion_carrera` FOREIGN KEY (`idCarrera`) REFERENCES `carrera` (`idCarrera`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_carrerainstitucion_estadocarrerainstitucion` FOREIGN KEY (`idEstadoCarreraInstitucion`) REFERENCES `estadocarrerainstitucion` (`idEstadoCarreraInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_carrerainstitucion_institucion` FOREIGN KEY (`idInstitucion`) REFERENCES `institucion` (`idInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_carrerainstitucion_modalidadcarrerainstitucion` FOREIGN KEY (`idModalidadCarreraInstitucion`) REFERENCES `modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_carrerainstitucion_preguntafrecuente` FOREIGN KEY (`idPreguntaFrecuente`) REFERENCES `preguntafrecuente` (`idPreguntaFrecuente`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.carrerainstitucion: ~0 rows (aproximadamente)

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
        `fechaInicio` datetime DEFAULT NULL,
        `titulo` varchar(50) DEFAULT NULL,
        `descripcion` varchar(50) DEFAULT NULL,
        `idCarreraInstitucion` int(11) DEFAULT NULL,
        PRIMARY KEY (`idContenidoMultimedia`),
        KEY `FK_contenidomultimedia_carrerainstitucion` (`idCarreraInstitucion`),
        CONSTRAINT `FK_contenidomultimedia_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.contenidomultimedia: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.estadoacceso
        CREATE TABLE IF NOT EXISTS `estadoacceso` (
        `idEstadoAcceso` int(11) NOT NULL AUTO_INCREMENT,
        `nombreEstadoAcceso` varchar(50) DEFAULT NULL,
        `fechaFin` datetime DEFAULT NULL,
        PRIMARY KEY (`idEstadoAcceso`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.estadoacceso: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.estadocarrerainstitucion
        CREATE TABLE IF NOT EXISTS `estadocarrerainstitucion` (
        `idEstadoCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
        `nombreEstadoCarreraInstitucion` varchar(50) DEFAULT NULL,
        `fechaFin` datetime DEFAULT NULL,
        PRIMARY KEY (`idEstadoCarreraInstitucion`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.estadocarrerainstitucion: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.estadoinstitucion
        CREATE TABLE IF NOT EXISTS `estadoinstitucion` (
        `idEstadoInstitucion` int(11) NOT NULL AUTO_INCREMENT,
        `nombreEstadoInstitucion` varchar(50) DEFAULT NULL,
        `fechaFin` datetime DEFAULT NULL,
        PRIMARY KEY (`idEstadoInstitucion`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.estadoinstitucion: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.estadousuario
        CREATE TABLE IF NOT EXISTS `estadousuario` (
        `idEstadoUsuario` int(11) NOT NULL AUTO_INCREMENT,
        `nombreEstadoUsuario` varchar(50) DEFAULT NULL,
        `fechaFin` datetime DEFAULT NULL,
        PRIMARY KEY (`idEstadoUsuario`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.estadousuario: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.genero
        CREATE TABLE IF NOT EXISTS `genero` (
        `idGenero` int(11) NOT NULL AUTO_INCREMENT,
        `nombreGenero` varchar(50) DEFAULT NULL,
        PRIMARY KEY (`idGenero`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.genero: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.grupo
        CREATE TABLE IF NOT EXISTS `grupo` (
        `idGrupo` int(11) NOT NULL AUTO_INCREMENT,
        `nombreGrupo` varchar(50) DEFAULT NULL,
        `fechaFin` datetime DEFAULT NULL,
        `descripcion` varchar(50) DEFAULT NULL,
        PRIMARY KEY (`idGrupo`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.grupo: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.historialabm
        CREATE TABLE IF NOT EXISTS `historialabm` (
        `idHistorialABM` int(11) NOT NULL AUTO_INCREMENT,
        `fechaHistorial` datetime DEFAULT NULL,
        `idTipoAccion` int(11) DEFAULT NULL,
        `idModalidadCarreraInstitucion` int(11) DEFAULT NULL,
        `idLocalidad` int(11) DEFAULT NULL,
        `idGrupo` int(11) DEFAULT NULL,
        `idProvincia` int(11) DEFAULT NULL,
        `idPermiso` int(11) DEFAULT NULL,
        `idUsuario` int(11) DEFAULT NULL,
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
        CONSTRAINT `FK_historialabm_aptitud` FOREIGN KEY (`idAptitud`) REFERENCES `aptitud` (`idAptitud`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_carrera` FOREIGN KEY (`idCarrera`) REFERENCES `carrera` (`idCarrera`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_estadoacceso` FOREIGN KEY (`idEstadoAcceso`) REFERENCES `estadoacceso` (`idEstadoAcceso`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_estadocarrerainstitucion` FOREIGN KEY (`idEstadoCarreraInstitucion`) REFERENCES `estadocarrerainstitucion` (`idEstadoCarreraInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_estadousuario` FOREIGN KEY (`idEstadoUsuario`) REFERENCES `estadousuario` (`idEstadoUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_genero` FOREIGN KEY (`idGenero`) REFERENCES `genero` (`idGenero`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_grupo` FOREIGN KEY (`idGrupo`) REFERENCES `grupo` (`idGrupo`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_localidad` FOREIGN KEY (`idLocalidad`) REFERENCES `localidad` (`idLocalidad`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_modalidadcarrerainstitucion` FOREIGN KEY (`idModalidadCarreraInstitucion`) REFERENCES `modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_pais` FOREIGN KEY (`idPais`) REFERENCES `pais` (`idPais`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_permiso` FOREIGN KEY (`idPermiso`) REFERENCES `permiso` (`idPermiso`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_permisogrupo` FOREIGN KEY (`idPermisoGrupo`) REFERENCES `permisogrupo` (`idPermisoGrupo`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_provincia` FOREIGN KEY (`idProvincia`) REFERENCES `provincia` (`idProvincia`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_tipoaccion` FOREIGN KEY (`idTipoAccion`) REFERENCES `tipoaccion` (`idTipoAccion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_tipocarrera` FOREIGN KEY (`idTipoCarrera`) REFERENCES `tipocarrera` (`idTipoCarrera`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_tipoinstitucion` FOREIGN KEY (`idTipoInstitucion`) REFERENCES `tipoinstitucion` (`idTipoInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialabm_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.historialabm: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.historialacceso
        CREATE TABLE IF NOT EXISTS `historialacceso` (
        `idHistorial` int(11) NOT NULL AUTO_INCREMENT,
        `fecha` datetime DEFAULT NULL,
        `ipAcceso` int(11) DEFAULT NULL,
        `navegador` varchar(50) DEFAULT NULL,
        `idEstadoAcceso` int(11) DEFAULT NULL,
        `idUsuario` int(11) DEFAULT NULL,
        PRIMARY KEY (`idHistorial`),
        KEY `FK_historialacceso_estadoacceso` (`idEstadoAcceso`),
        KEY `FK_historialacceso_usuario` (`idUsuario`),
        CONSTRAINT `FK_historialacceso_estadoacceso` FOREIGN KEY (`idEstadoAcceso`) REFERENCES `estadoacceso` (`idEstadoAcceso`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_historialacceso_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.historialacceso: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.institucion
        CREATE TABLE IF NOT EXISTS `institucion` (
        `idInstitucion` int(11) NOT NULL AUTO_INCREMENT,
        `anioFundacion` int(11) DEFAULT NULL,
        `codigoPostal` int(11) DEFAULT NULL,
        `nombreInstitucion` varchar(50) DEFAULT NULL,
        `CUIT` int(11) DEFAULT NULL,
        `direccion` varchar(50) DEFAULT NULL,
        `fechaAlta` datetime DEFAULT NULL,
        `siglaInstitucion` varchar(50) DEFAULT NULL,
        `telefono` varchar(50) DEFAULT NULL,
        `mail` varchar(50) DEFAULT NULL,
        `sitioWeb` varchar(50) DEFAULT NULL,
        `urlLogo` varchar(50) DEFAULT NULL,
        `idTipoInstitucion` int(11) DEFAULT NULL,
        `idLocalidad` int(11) DEFAULT NULL,
        `idUsuario` int(11) DEFAULT NULL,
        PRIMARY KEY (`idInstitucion`),
        KEY `FK_institucion_tipoinstitucion` (`idTipoInstitucion`),
        KEY `FK_institucion_localidad` (`idLocalidad`),
        KEY `FK_institucion_usuario` (`idUsuario`),
        CONSTRAINT `FK_institucion_localidad` FOREIGN KEY (`idLocalidad`) REFERENCES `localidad` (`idLocalidad`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_institucion_tipoinstitucion` FOREIGN KEY (`idTipoInstitucion`) REFERENCES `tipoinstitucion` (`idTipoInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_institucion_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.institucion: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.institucionestado
        CREATE TABLE IF NOT EXISTS `institucionestado` (
        `idinstitucionEstado` int(11) NOT NULL AUTO_INCREMENT,
        `fechaInicio` datetime DEFAULT NULL,
        `fechaFin` datetime DEFAULT NULL,
        `idEstadoInstitucion` int(11) DEFAULT NULL,
        `idInstitucion` int(11) DEFAULT NULL,
        PRIMARY KEY (`idinstitucionEstado`),
        KEY `FK_institucionestado_estadoinstitucion` (`idEstadoInstitucion`),
        KEY `FK_institucionestado_institucion` (`idInstitucion`),
        CONSTRAINT `FK_institucionestado_estadoinstitucion` FOREIGN KEY (`idEstadoInstitucion`) REFERENCES `estadoinstitucion` (`idEstadoInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_institucionestado_institucion` FOREIGN KEY (`idInstitucion`) REFERENCES `institucion` (`idInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.institucionestado: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.interesusuariocarrera
        CREATE TABLE IF NOT EXISTS `interesusuariocarrera` (
        `fechaAlta` datetime DEFAULT NULL,
        `fechaFin` datetime DEFAULT NULL,
        `idUsuario` int(11) DEFAULT NULL,
        `idCarreraInstitucion` int(11) DEFAULT NULL,
        KEY `FK_interesusuariocarrera_usuario` (`idUsuario`),
        KEY `FK_interesusuariocarrera_carrerainstitucion` (`idCarreraInstitucion`),
        CONSTRAINT `FK_interesusuariocarrera_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_interesusuariocarrera_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.interesusuariocarrera: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.localidad
        CREATE TABLE IF NOT EXISTS `localidad` (
        `idLocalidad` int(11) NOT NULL AUTO_INCREMENT,
        `nombreLocalidad` varchar(50) DEFAULT NULL,
        `idProvincia` int(11) DEFAULT NULL,
        PRIMARY KEY (`idLocalidad`),
        KEY `FK_localidad_provincia` (`idProvincia`),
        CONSTRAINT `FK_localidad_provincia` FOREIGN KEY (`idProvincia`) REFERENCES `provincia` (`idProvincia`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.localidad: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.modalidadcarrerainstitucion
        CREATE TABLE IF NOT EXISTS `modalidadcarrerainstitucion` (
        `idModalidadCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
        `nombreModalidad` varchar(50) DEFAULT NULL,
        PRIMARY KEY (`idModalidadCarreraInstitucion`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.modalidadcarrerainstitucion: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.pais
        CREATE TABLE IF NOT EXISTS `pais` (
        `idPais` int(11) NOT NULL AUTO_INCREMENT,
        `nombrePais` varchar(50) DEFAULT NULL,
        PRIMARY KEY (`idPais`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.pais: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.permiso
        CREATE TABLE IF NOT EXISTS `permiso` (
        `idPermiso` int(11) NOT NULL AUTO_INCREMENT,
        `nombrePermiso` varchar(50) DEFAULT NULL,
        `descripcion` varchar(50) DEFAULT NULL,
        PRIMARY KEY (`idPermiso`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.permiso: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.permisogrupo
        CREATE TABLE IF NOT EXISTS `permisogrupo` (
        `idPermisoGrupo` int(11) NOT NULL AUTO_INCREMENT,
        `fechaFin` datetime DEFAULT NULL,
        `fechaInicio` datetime DEFAULT NULL,
        `idGrupo` int(11) DEFAULT NULL,
        `idPermiso` int(11) DEFAULT NULL,
        PRIMARY KEY (`idPermisoGrupo`),
        KEY `FK_permisogrupo_grupo` (`idGrupo`),
        KEY `FK_permisogrupo_permiso` (`idPermiso`),
        CONSTRAINT `FK_permisogrupo_grupo` FOREIGN KEY (`idGrupo`) REFERENCES `grupo` (`idGrupo`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_permisogrupo_permiso` FOREIGN KEY (`idPermiso`) REFERENCES `permiso` (`idPermiso`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.permisogrupo: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.preguntafrecuente
        CREATE TABLE IF NOT EXISTS `preguntafrecuente` (
        `idPreguntaFrecuente` int(11) NOT NULL AUTO_INCREMENT,
        `fechaFin` datetime DEFAULT NULL,
        `nombrePregunta` varchar(50) DEFAULT NULL,
        `respuesta` varchar(50) DEFAULT NULL,
        PRIMARY KEY (`idPreguntaFrecuente`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.preguntafrecuente: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.provincia
        CREATE TABLE IF NOT EXISTS `provincia` (
        `idProvincia` int(11) NOT NULL AUTO_INCREMENT,
        `nombreProvincia` varchar(50) DEFAULT NULL,
        `idPais` int(11) DEFAULT NULL,
        PRIMARY KEY (`idProvincia`),
        KEY `FK_provincia_pais` (`idPais`),
        CONSTRAINT `FK_provincia_pais` FOREIGN KEY (`idPais`) REFERENCES `pais` (`idPais`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.provincia: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.test
        CREATE TABLE IF NOT EXISTS `test` (
        `idResultadoCuestionario` int(11) NOT NULL AUTO_INCREMENT,
        `fechaResultadoCuestionario` datetime DEFAULT NULL,
        `idUsuario` int(11) DEFAULT NULL,
        PRIMARY KEY (`idResultadoCuestionario`),
        KEY `FK_test_usuario` (`idUsuario`),
        CONSTRAINT `FK_test_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
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
        CONSTRAINT `FK_testaptitud_aptitud` FOREIGN KEY (`idAptitud`) REFERENCES `aptitud` (`idAptitud`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_testaptitud_test` FOREIGN KEY (`idTest`) REFERENCES `test` (`idResultadoCuestionario`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.testaptitud: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.testcarrerainstitucion
        CREATE TABLE IF NOT EXISTS `testcarrerainstitucion` (
        `afinidadCarrera` double DEFAULT NULL,
        `idTest` int(11) DEFAULT NULL,
        `idCarreraInstitucion` int(11) DEFAULT NULL,
        KEY `FK_testcarrerainstitucion_test` (`idTest`),
        KEY `FK_testcarrerainstitucion_carrerainstitucion` (`idCarreraInstitucion`),
        CONSTRAINT `FK_testcarrerainstitucion_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_testcarrerainstitucion_test` FOREIGN KEY (`idTest`) REFERENCES `test` (`idResultadoCuestionario`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.testcarrerainstitucion: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.tipoaccion
        CREATE TABLE IF NOT EXISTS `tipoaccion` (
        `idTipoAccion` int(11) NOT NULL AUTO_INCREMENT,
        `nombreTipoAccion` varchar(50) DEFAULT NULL,
        PRIMARY KEY (`idTipoAccion`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.tipoaccion: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.tipocarrera
        CREATE TABLE IF NOT EXISTS `tipocarrera` (
        `idTipoCarrera` int(11) NOT NULL AUTO_INCREMENT,
        `nombreTipoCarrera` varchar(50) DEFAULT NULL,
        PRIMARY KEY (`idTipoCarrera`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.tipocarrera: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.tipoinstitucion
        CREATE TABLE IF NOT EXISTS `tipoinstitucion` (
        `idTipoInstitucion` int(11) NOT NULL AUTO_INCREMENT,
        `nombreTipoInstitucion` varchar(50) DEFAULT NULL,
        PRIMARY KEY (`idTipoInstitucion`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.tipoinstitucion: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.usuario
        CREATE TABLE IF NOT EXISTS `usuario` (
        `idUsuario` int(11) NOT NULL AUTO_INCREMENT,
        `mail` varchar(50) DEFAULT NULL,
        `dni` int(11) DEFAULT NULL,
        `apellido` varchar(50) DEFAULT NULL,
        `nombre` varchar(50) DEFAULT NULL,
        `contrasena` varchar(50) DEFAULT NULL,
        `fechaNac` datetime DEFAULT NULL,
        `vencimientoContrasena` datetime DEFAULT NULL,
        `idGenero` int(11) DEFAULT NULL,
        `idLocalidad` int(11) DEFAULT NULL,
        PRIMARY KEY (`idUsuario`),
        KEY `FK_usuario_genero` (`idGenero`),
        KEY `FK_usuario_localidad` (`idLocalidad`),
        CONSTRAINT `FK_usuario_genero` FOREIGN KEY (`idGenero`) REFERENCES `genero` (`idGenero`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_usuario_localidad` FOREIGN KEY (`idLocalidad`) REFERENCES `localidad` (`idLocalidad`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.usuario: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.usuarioestado
        CREATE TABLE IF NOT EXISTS `usuarioestado` (
        `idUsuarioEstado` int(11) NOT NULL AUTO_INCREMENT,
        `fechaFin` datetime DEFAULT NULL,
        `fechaInicio` datetime DEFAULT NULL,
        `idEstadoUsuario` int(11) DEFAULT NULL,
        `idUsuario` int(11) DEFAULT NULL,
        PRIMARY KEY (`idUsuarioEstado`),
        KEY `FK_usuarioestado_estadousuario` (`idEstadoUsuario`),
        KEY `FK_usuarioestado_usuario` (`idUsuario`),
        CONSTRAINT `FK_usuarioestado_estadousuario` FOREIGN KEY (`idEstadoUsuario`) REFERENCES `estadousuario` (`idEstadoUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_usuarioestado_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.usuarioestado: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.usuariogrupo
        CREATE TABLE IF NOT EXISTS `usuariogrupo` (
        `idUsuarioGrupo` int(11) NOT NULL AUTO_INCREMENT,
        `idUsuario` int(11) DEFAULT NULL,
        `idGrupo` int(11) DEFAULT NULL,
        `fechaFin` datetime DEFAULT NULL,
        `fechaInicio` datetime DEFAULT NULL,
        PRIMARY KEY (`idUsuarioGrupo`),
        KEY `FK_usuariogrupo_usuario` (`idUsuario`),
        KEY `FK_usuariogrupo_grupo` (`idGrupo`),
        CONSTRAINT `FK_usuariogrupo_grupo` FOREIGN KEY (`idGrupo`) REFERENCES `grupo` (`idGrupo`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_usuariogrupo_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.usuariogrupo: ~0 rows (aproximadamente)

        -- Volcando estructura para tabla ovo.usuariopermiso
        CREATE TABLE IF NOT EXISTS `usuariopermiso` (
        `idUsuarioPermiso` int(11) NOT NULL AUTO_INCREMENT,
        `idPermiso` int(11) DEFAULT NULL,
        `idUsuario` int(11) DEFAULT NULL,
        `fechaFin` datetime DEFAULT NULL,
        `fechaInicio` datetime DEFAULT NULL,
        PRIMARY KEY (`idUsuarioPermiso`),
        KEY `FK_usuariopermiso_permiso` (`idPermiso`),
        KEY `FK_usuariopermiso_usuario` (`idUsuario`),
        CONSTRAINT `FK_usuariopermiso_permiso` FOREIGN KEY (`idPermiso`) REFERENCES `permiso` (`idPermiso`) ON DELETE NO ACTION ON UPDATE NO ACTION,
        CONSTRAINT `FK_usuariopermiso_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        -- Volcando datos para la tabla ovo.usuariopermiso: ~0 rows (aproximadamente)

        /*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
        /*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
        /*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
        /*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
        /*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
    """)
    conn.commit()
    conn.close()

# -----------------------------------JWT-----------------------------------
SECRET_KEY = "ghwgdgHHYushHg1231SDAAa"

# Función para generar un token JWT
def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Decorador para proteger rutas con autenticación JWT
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
                current_user = 1  # Usuario de prueba
            else:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                current_user = data.get("user_id")
        except Exception:
            return jsonify({"errorCode": "AUTH", "message": "Token es inválido"}), 401
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
    correo = "drifthostingvps@gmail.com"
    puerto = 465
    clave = "hwpz gask jgsd ulzj"

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

# Endpoint para probar el envío de correos
@app.route("/api/v1/email", methods=["POST"])
def send_test_email():
    try:
        data = request.json
        if "to" not in data or "subject" not in data or "mensaje" not in data:
            raise Exception("Faltan datos obligatorios")
        #verificar que to sea un correo
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, data["to"]):
            raise Exception("El correo electrónico no es válido")
        send_email(data["to"], data["subject"], f"<p>{data['mensaje']}</p>")
        return jsonify("Correo enviado correctamente"), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
            return jsonify({"errorCode": "ERR5", "message": "Credenciales inválidas"}), 401

        if not verify_password(contrasena, user.get('contrasena') or ''):
            return jsonify({"errorCode": "ERR5", "message": "Credenciales inválidas"}), 401

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
        return resp, 200
    except Exception as e:
        log(f"/auth/login error: {e}\n{traceback.format_exc()}")
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
            return jsonify({"errorCode": "ERR4", "message": "Inicio de sesión fallido"}), 500

        data = request.get_json(silent=True) or {}
        id_token = data.get('id_token') or data.get('credential')
        if not id_token:
            return jsonify({"errorCode": "ERR4", "message": "Inicio de sesión fallido"}), 400

        request_adapter = google_requests.Request()
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        # Verificar token; si hay CLIENT_ID lo usamos como audiencia
        claims = google_id_token.verify_oauth2_token(id_token, request_adapter, audience=client_id) if client_id else google_id_token.verify_oauth2_token(id_token, request_adapter)

        email = claims.get('email')
        if not email:
            return jsonify({"errorCode": "ERR4", "message": "Inicio de sesión fallido"}), 400

        user = get_user_by_email(email)
        if not user:
            # No auto-registro por ahora -> credenciales inválidas según criterios
            return jsonify({"errorCode": "ERR5", "message": "Credenciales inválidas"}), 401

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
        return resp, 200
    except Exception as e:
        log(f"/auth/google error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR4", "message": "Inicio de sesión fallido"}), 500

# Endpoint para obtener información del usuario autenticado
@app.route('/api/v1/auth/me', methods=['GET'])
@token_required
def whoami(current_user_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT idUsuario, mail, apellido, nombre FROM usuario WHERE idUsuario = %s", (current_user_id,))
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
            },
            "permisos": permisos,
            "grupos": grupos,
        }), 200
    except Exception as e:
        log(f"/auth/me error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR4", "message": "Inicio de sesión fallido"}), 500

# ============================ ADMIN: Gestión de perfiles (US003) ============================

# Endpoint para listar todos los usuarios
@app.route('/api/v1/admin/users', methods=['GET'])
@requires_permission('ADMIN_PANEL')
def admin_list_users(current_user_id):
    """Listado de usuarios con sus grupos activos."""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT u.idUsuario, u.nombre, u.apellido, u.mail,
                   GROUP_CONCAT(g.nombreGrupo ORDER BY g.nombreGrupo SEPARATOR ',') AS grupos
            FROM usuario u
            LEFT JOIN usuariogrupo ug ON ug.idUsuario = u.idUsuario AND (ug.fechaFin IS NULL OR ug.fechaFin > NOW())
            LEFT JOIN grupo g ON g.idGrupo = ug.idGrupo
            GROUP BY u.idUsuario
            ORDER BY u.apellido, u.nombre
            """
        )
        rows = cur.fetchall() or []
        def parse_grupos(s):
            if not s:
                return []
            return [p for p in (s or '').split(',') if p]
        data = [
            {
                "id": r['idUsuario'],
                "nombre": r.get('nombre'),
                "apellido": r.get('apellido'),
                "mail": r.get('mail'),
                "grupos": parse_grupos(r.get('grupos')),
            }
            for r in rows
        ]
        return jsonify(data), 200
    except Exception as e:
        log(f"/admin/users GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para listar todos los grupos
@app.route('/api/v1/admin/groups', methods=['GET'])
@requires_permission('ADMIN_PANEL')
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
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para obtener grupos de un usuario
@app.route('/api/v1/admin/users/<int:user_id>/groups', methods=['GET'])
@requires_permission('ADMIN_PANEL')
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

# Endpoint para asignar un grupo a un usuario
@app.route('/api/v1/admin/users/<int:user_id>/group', methods=['PUT'])
@requires_permission('ADMIN_PANEL')
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
@requires_permission('ADMIN_PANEL')
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

# Endpoint para obtener todos los permisos de un usuario
@app.route('/api/v1/admin/users/<int:user_id>/permissions', methods=['GET'])
@requires_permission('ADMIN_PANEL')
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
        # Obtener los permisos de los grupos a los cuales pertenece y no esta vencido
        cur.execute(
            """
            SELECT p.idPermiso, p.nombrePermiso, p.descripcion
            FROM permiso p
            JOIN permisogrupo pg ON pg.idPermiso = p.idPermiso
            WHERE pg.idGrupo IN (
                SELECT idGrupo
                FROM usuariogrupo
                WHERE idUsuario = %s AND (fechaFin IS NULL OR fechaFin > NOW())
            )
        """,
            (user_id,)
        )
        # Unir permisos pero hay que quitar los repetidos (directos y ademas por grupo)
        rows = {**{row['idPermiso']: row for row in rows}, **{row['idPermiso']: row for row in cur.fetchall() or []}}
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

# Endpoint para agregar un permiso a un usuario
@app.route('/api/v1/admin/users/<int:user_id>/permissions', methods=['POST'])
@requires_permission('ADMIN_PANEL')
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
@requires_permission('ADMIN_PANEL')
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
@requires_permission('ADMIN_PANEL')
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
@requires_permission('ADMIN_PANEL')
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
@requires_permission('ADMIN_PANEL')
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
@requires_permission('ADMIN_PANEL')
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
                title = Paragraph("Historial de accesos", styles["Heading2"])

                headers = ["Fecha", "UsuarioId", "Nombre", "Apellido", "IP", "Navegador", "Estado"]
                data_tbl = [headers]
                for r in rows:
                    data_tbl.append([
                        (r.get('fecha').isoformat(sep=' ') if r.get('fecha') else ''),
                        str(r.get('userId') or ''),
                        r.get('nombre') or '',
                        r.get('apellido') or '',
                        str(r.get('ipAcceso') or ''),
                        (r.get('navegador') or '')[:60],
                        r.get('estado') or '',
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
                filename = f"historial_accesos_{ts}.pdf"
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
                title = Paragraph("Auditoría del sistema", styles["Heading2"])

                headers = ["Fecha", "UsuarioId", "Nombre", "Apellido", "TipoAccion", "Modulo", "ClaseId"]
                data_tbl = [headers]
                for r in rows:
                    modulo_name, clase_id = pick_modulo(r)
                    data_tbl.append([
                        (r.get('fechaHistorial').isoformat(sep=' ') if r.get('fechaHistorial') else ''),
                        str(r.get('idUsuario') or ''),
                        r.get('nombre') or '',
                        r.get('apellido') or '',
                        r.get('nombreTipoAccion') or '',
                        modulo_name or '',
                        str(clase_id or ''),
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
                filename = f"auditoria_{ts}.pdf"
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
    try:
        data = request.get_json(silent=True) or {}
        nombre = (data.get('nombre') or '').strip()
        correo = (data.get('correo') or '').strip()
        contrasena = data.get('contrasena') or ''
        acepta_politicas = data.get('aceptaPoliticas')

        # ERR1: campos requeridos incompletos
        required_missing = []
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

        # Verificar existencia previa de email
        conn = mysql.connector.connect(**DB_CONFIG)
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM usuario WHERE mail=%s", (correo,))
            if cur.fetchone():
                # No especificado en HU; usamos ERR1 para indicar conflicto de datos
                return jsonify({"errorCode": "ERR1", "message": "El correo ya está registrado."}), 400

            # Insertar usuario
            hashed = hash_password(contrasena)
            cur.execute(
                "INSERT INTO usuario (mail, nombre, contrasena) VALUES (%s, %s, %s)",
                (correo, nombre, hashed)
            )
            conn.commit()

            # Obtener id del nuevo usuario
            cur.execute("SELECT idUsuario, mail, nombre, apellido FROM usuario WHERE mail=%s", (correo,))
            user = cur.fetchone()
        finally:
            try:
                conn.close()
            except Exception:
                pass

        # Emitir token y devolver contexto similar al login
        token = generate_token(user[0])
        permisos, grupos = get_user_permissions_and_groups(user[0])
        resp = jsonify({
            "usuario": {
                "id": user[0],
                "nombre": user[2],
                "apellido": user[3],
                "mail": user[1],
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
        frontend_base = os.getenv('FRONTEND_BASE_URL', 'http://localhost:3000')
        link = f"{frontend_base}/reset-password?token={token}"

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
            INSERT INTO interesusuariocarrera (idUsuario, idCarreraInstitucion, fechaInicio)
            VALUES (%s, %s, NOW())
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

        fn = u.get('fechaNac')
        fecha_str = None
        try:
            if fn:
                # fechaNac es datetime; devolver solo fecha
                fecha_str = fn.date().isoformat()
        except Exception:
            fecha_str = None

        return jsonify({
            "id": u.get('idUsuario'),
            "nombre": u.get('nombre'),
            "apellido": u.get('apellido'),
            "email": u.get('mail'),
            "fechaNacimiento": fecha_str,
            "dni": u.get('dni'),
            # "acciones": {
            #     "editar": {"method": "PUT", "path": "/api/v1/user/profile"},
            #     "listarCarrerasInteres": {"method": "GET", "path": "/api/v1/user/interests"},
            #     "verHistoricoTest": {"method": "GET", "path": "/api/v1/user/tests"},
            #     "bajaUsuario": {"method": "POST", "path": "/api/v1/auth/deactivate"}
            # }
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







if __name__ == "__main__":
    # Inicializar la base de datos
    # init_db()

    # Iniciar la aplicación Flask
    app.run(debug=True, host="127.0.0.1", port=8000)