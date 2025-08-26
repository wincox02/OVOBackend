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


if __name__ == "__main__":
    # Inicializar la base de datos
    # init_db()

    # Iniciar la aplicación Flask
    app.run(debug=True, host="0.0.0.0", port=5000)
