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
  `nombreAptitud` varchar(50) DEFAULT NULL,
  `descripcion` varchar(50) DEFAULT NULL,
  `fechaAlta` datetime NOT NULL DEFAULT current_timestamp(),
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
  `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
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
  `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.estadoacceso: ~2 rows (aproximadamente)
INSERT INTO `estadoacceso` (`idEstadoAcceso`, `nombreEstadoAcceso`, `fechaFin`) VALUES
	(1, 'Exitoso', NULL),
	(2, 'Fallido', NULL),
	(3, 'Fallido Google', NULL);

-- Volcando estructura para tabla ovo.estadocarrerainstitucion
CREATE TABLE IF NOT EXISTS `estadocarrerainstitucion` (
  `idEstadoCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
  `nombreEstadoCarreraInstitucion` varchar(50) DEFAULT NULL,
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idEstadoCarreraInstitucion`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.estadocarrerainstitucion: ~2 rows (aproximadamente)
INSERT INTO `estadocarrerainstitucion` (`idEstadoCarreraInstitucion`, `nombreEstadoCarreraInstitucion`, `fechaFin`) VALUES
	(1, 'Activa', NULL),
	(2, 'Inactiva', NULL),
	(3, 'Cerrada', NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.estadousuario: ~2 rows (aproximadamente)
INSERT INTO `estadousuario` (`idEstadoUsuario`, `nombreEstadoUsuario`, `fechaFin`) VALUES
	(1, 'Activo', NULL),
	(2, 'Suspendido', NULL),
	(3, 'Baja', NULL);

-- Volcando estructura para tabla ovo.genero
CREATE TABLE IF NOT EXISTS `genero` (
  `idGenero` int(11) NOT NULL AUTO_INCREMENT,
  `nombreGenero` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idGenero`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.genero: ~0 rows (aproximadamente)
INSERT INTO `genero` (`idGenero`, `nombreGenero`) VALUES
	(1, 'Masculino');

-- Volcando estructura para tabla ovo.grupo
CREATE TABLE IF NOT EXISTS `grupo` (
  `idGrupo` int(11) NOT NULL AUTO_INCREMENT,
  `nombreGrupo` varchar(50) DEFAULT NULL,
  `fechaFin` datetime DEFAULT NULL,
  `descripcion` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idGrupo`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.grupo: ~3 rows (aproximadamente)
INSERT INTO `grupo` (`idGrupo`, `nombreGrupo`, `fechaFin`, `descripcion`) VALUES
	(1, 'Administrador', '2035-08-25 18:54:47', 'Todos los permisos'),
	(2, 'Moderador', '3000-08-25 19:07:43', NULL),
	(3, 'Estudiante', NULL, NULL),
	(4, 'Institucion', NULL, NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.historialabm: ~1 rows (aproximadamente)
INSERT INTO `historialabm` (`idHistorialABM`, `idUsuario`, `fechaHistorial`, `idTipoAccion`, `idModalidadCarreraInstitucion`, `idLocalidad`, `idGrupo`, `idProvincia`, `idPermiso`, `idAptitud`, `idPermisoGrupo`, `idCarrera`, `idEstadoAcceso`, `idGenero`, `idEstadoCarreraInstitucion`, `idEstadoUsuario`, `idPais`, `idTipoInstitucion`, `idTipoCarrera`) VALUES
	(1, 1, '2025-08-31 18:31:20', 1, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- Volcando estructura para tabla ovo.historialacceso
CREATE TABLE IF NOT EXISTS `historialacceso` (
  `idHistorial` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL DEFAULT current_timestamp(),
  `ipAcceso` varchar(50) DEFAULT NULL,
  `navegador` varchar(50) DEFAULT NULL,
  `idEstadoAcceso` int(11) DEFAULT NULL,
  `idUsuario` int(11) DEFAULT NULL,
  PRIMARY KEY (`idHistorial`),
  KEY `FK_historialacceso_estadoacceso` (`idEstadoAcceso`),
  KEY `FK_historialacceso_usuario` (`idUsuario`),
  CONSTRAINT `FK_historialacceso_estadoacceso` FOREIGN KEY (`idEstadoAcceso`) REFERENCES `estadoacceso` (`idEstadoAcceso`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_historialacceso_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.historialacceso: ~1 rows (aproximadamente)
INSERT INTO `historialacceso` (`idHistorial`, `fecha`, `ipAcceso`, `navegador`, `idEstadoAcceso`, `idUsuario`) VALUES
	(1, '2025-08-31 18:18:39', '1.1.1.1', 'dasd', 1, 1);

-- Volcando estructura para tabla ovo.institucion
CREATE TABLE IF NOT EXISTS `institucion` (
  `idInstitucion` int(11) NOT NULL AUTO_INCREMENT,
  `anioFundacion` int(11) DEFAULT NULL,
  `codigoPostal` int(11) DEFAULT NULL,
  `nombreInstitucion` varchar(50) DEFAULT NULL,
  `CUIT` int(11) DEFAULT NULL,
  `direccion` varchar(50) DEFAULT NULL,
  `fechaAlta` datetime NOT NULL DEFAULT current_timestamp(),
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
  `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
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
  `fechaAlta` datetime NOT NULL DEFAULT current_timestamp(),
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.localidad: ~1 rows (aproximadamente)
INSERT INTO `localidad` (`idLocalidad`, `nombreLocalidad`, `idProvincia`) VALUES
	(1, 'Mendoza', 1);

-- Volcando estructura para tabla ovo.modalidadcarrerainstitucion
CREATE TABLE IF NOT EXISTS `modalidadcarrerainstitucion` (
  `idModalidadCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
  `nombreModalidad` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idModalidadCarreraInstitucion`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.modalidadcarrerainstitucion: ~2 rows (aproximadamente)
INSERT INTO `modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`, `nombreModalidad`) VALUES
	(1, 'Presencial'),
	(2, 'Virtual'),
	(3, 'Hibrida');

-- Volcando estructura para tabla ovo.pais
CREATE TABLE IF NOT EXISTS `pais` (
  `idPais` int(11) NOT NULL AUTO_INCREMENT,
  `nombrePais` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idPais`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.pais: ~0 rows (aproximadamente)
INSERT INTO `pais` (`idPais`, `nombrePais`) VALUES
	(1, 'Argentina');

-- Volcando estructura para tabla ovo.permiso
CREATE TABLE IF NOT EXISTS `permiso` (
  `idPermiso` int(11) NOT NULL AUTO_INCREMENT,
  `nombrePermiso` varchar(50) DEFAULT NULL,
  `descripcion` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`idPermiso`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.permiso: ~2 rows (aproximadamente)
INSERT INTO `permiso` (`idPermiso`, `nombrePermiso`, `descripcion`) VALUES
	(1, 'ADMIN_PANEL', 'Obtener Grupos y permisos. Asignar permisos a usuarios'),
	(2, 'NO_SE', 'Por grupo moderador');

-- Volcando estructura para tabla ovo.permisogrupo
CREATE TABLE IF NOT EXISTS `permisogrupo` (
  `idPermisoGrupo` int(11) NOT NULL AUTO_INCREMENT,
  `idGrupo` int(11) DEFAULT NULL,
  `idPermiso` int(11) DEFAULT NULL,
  `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idPermisoGrupo`),
  KEY `FK_permisogrupo_grupo` (`idGrupo`),
  KEY `FK_permisogrupo_permiso` (`idPermiso`),
  CONSTRAINT `FK_permisogrupo_grupo` FOREIGN KEY (`idGrupo`) REFERENCES `grupo` (`idGrupo`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_permisogrupo_permiso` FOREIGN KEY (`idPermiso`) REFERENCES `permiso` (`idPermiso`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.permisogrupo: ~2 rows (aproximadamente)
INSERT INTO `permisogrupo` (`idPermisoGrupo`, `idGrupo`, `idPermiso`, `fechaInicio`, `fechaFin`) VALUES
	(1, 1, 1, '2025-08-25 18:55:15', NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.provincia: ~0 rows (aproximadamente)
INSERT INTO `provincia` (`idProvincia`, `nombreProvincia`, `idPais`) VALUES
	(1, 'Mendoza', 1);

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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.tipoaccion: ~0 rows (aproximadamente)
INSERT INTO `tipoaccion` (`idTipoAccion`, `nombreTipoAccion`) VALUES
	(1, 'CREACION');

-- Volcando estructura para tabla ovo.tipocarrera
CREATE TABLE IF NOT EXISTS `tipocarrera` (
  `idTipoCarrera` int(11) NOT NULL AUTO_INCREMENT,
  `nombreTipoCarrera` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idTipoCarrera`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.tipocarrera: ~9 rows (aproximadamente)
INSERT INTO `tipocarrera` (`idTipoCarrera`, `nombreTipoCarrera`) VALUES
	(1, 'Licenciatura'),
	(2, 'Tecnicatura'),
	(3, 'Profesorado'),
	(4, 'Ingenieria'),
	(5, 'Doctorado'),
	(6, 'Maestria'),
	(7, 'Diplomatura'),
	(8, 'Formacion Profesional'),
	(9, 'Curso Superior'),
	(10, 'Certificacion Tecnica');

-- Volcando estructura para tabla ovo.tipoinstitucion
CREATE TABLE IF NOT EXISTS `tipoinstitucion` (
  `idTipoInstitucion` int(11) NOT NULL AUTO_INCREMENT,
  `nombreTipoInstitucion` varchar(50) DEFAULT NULL,
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idTipoInstitucion`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.tipoinstitucion: ~2 rows (aproximadamente)
INSERT INTO `tipoinstitucion` (`idTipoInstitucion`, `nombreTipoInstitucion`, `fechaFin`) VALUES
	(1, 'Universitaria', NULL),
	(2, 'Instituto tecnico', NULL),
	(3, 'Centro de formacion', NULL);

-- Volcando estructura para tabla ovo.usuario
CREATE TABLE IF NOT EXISTS `usuario` (
  `idUsuario` int(11) NOT NULL AUTO_INCREMENT,
  `mail` varchar(50) DEFAULT NULL,
  `dni` int(11) DEFAULT NULL,
  `apellido` varchar(50) DEFAULT NULL,
  `nombre` varchar(50) DEFAULT NULL,
  `contrasena` varchar(50) DEFAULT NULL,
  `vencimientoContrasena` datetime DEFAULT NULL,
  `fechaNac` date DEFAULT NULL,
  `idGenero` int(11) DEFAULT NULL,
  `idLocalidad` int(11) DEFAULT NULL,
  PRIMARY KEY (`idUsuario`),
  KEY `FK_usuario_genero` (`idGenero`),
  KEY `FK_usuario_localidad` (`idLocalidad`),
  CONSTRAINT `FK_usuario_genero` FOREIGN KEY (`idGenero`) REFERENCES `genero` (`idGenero`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_usuario_localidad` FOREIGN KEY (`idLocalidad`) REFERENCES `localidad` (`idLocalidad`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.usuario: ~1 rows (aproximadamente)
INSERT INTO `usuario` (`idUsuario`, `mail`, `dni`, `apellido`, `nombre`, `contrasena`, `vencimientoContrasena`, `fechaNac`, `idGenero`, `idLocalidad`) VALUES
	(1, 'm1718c@gmail.com', 12345678, 'Bufarini', 'Ignacio', 'HnSZzlwAdcOCybWVlw7mGwLX5OwjARun2/LnHUpBn2I=', '2026-08-19 17:36:29', '2000-05-15', 1, 1),
	(2, 'ana@example.com', NULL, NULL, 'Ana', '7s0ftvL9WCz6AT2uHOuszsh0nZy5C/fBFyZldg+rgNU=', NULL, NULL, NULL, NULL);

-- Volcando estructura para tabla ovo.usuarioestado
CREATE TABLE IF NOT EXISTS `usuarioestado` (
  `idUsuarioEstado` int(11) NOT NULL AUTO_INCREMENT,
  `fechaFin` datetime DEFAULT NULL,
  `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
  `idEstadoUsuario` int(11) DEFAULT NULL,
  `idUsuario` int(11) DEFAULT NULL,
  PRIMARY KEY (`idUsuarioEstado`),
  KEY `FK_usuarioestado_estadousuario` (`idEstadoUsuario`),
  KEY `FK_usuarioestado_usuario` (`idUsuario`),
  CONSTRAINT `FK_usuarioestado_estadousuario` FOREIGN KEY (`idEstadoUsuario`) REFERENCES `estadousuario` (`idEstadoUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_usuarioestado_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.usuarioestado: ~1 rows (aproximadamente)
INSERT INTO `usuarioestado` (`idUsuarioEstado`, `fechaFin`, `fechaInicio`, `idEstadoUsuario`, `idUsuario`) VALUES
	(1, NULL, '2025-09-01 19:22:43', 1, 1);

-- Volcando estructura para tabla ovo.usuariogrupo
CREATE TABLE IF NOT EXISTS `usuariogrupo` (
  `idUsuarioGrupo` int(11) NOT NULL AUTO_INCREMENT,
  `idUsuario` int(11) DEFAULT NULL,
  `idGrupo` int(11) DEFAULT NULL,
  `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idUsuarioGrupo`),
  KEY `FK_usuariogrupo_usuario` (`idUsuario`),
  KEY `FK_usuariogrupo_grupo` (`idGrupo`),
  CONSTRAINT `FK_usuariogrupo_grupo` FOREIGN KEY (`idGrupo`) REFERENCES `grupo` (`idGrupo`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_usuariogrupo_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.usuariogrupo: ~2 rows (aproximadamente)
INSERT INTO `usuariogrupo` (`idUsuarioGrupo`, `idUsuario`, `idGrupo`, `fechaInicio`, `fechaFin`) VALUES
	(6, 1, 2, '2025-08-25 19:15:20', NULL),
	(7, 1, 1, '2025-08-25 19:22:53', NULL);

-- Volcando estructura para tabla ovo.usuariopermiso
CREATE TABLE IF NOT EXISTS `usuariopermiso` (
  `idUsuarioPermiso` int(11) NOT NULL AUTO_INCREMENT,
  `idPermiso` int(11) DEFAULT NULL,
  `idUsuario` int(11) DEFAULT NULL,
  `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idUsuarioPermiso`),
  KEY `FK_usuariopermiso_permiso` (`idPermiso`),
  KEY `FK_usuariopermiso_usuario` (`idUsuario`),
  CONSTRAINT `FK_usuariopermiso_permiso` FOREIGN KEY (`idPermiso`) REFERENCES `permiso` (`idPermiso`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_usuariopermiso_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla ovo.usuariopermiso: ~1 rows (aproximadamente)
INSERT INTO `usuariopermiso` (`idUsuarioPermiso`, `idPermiso`, `idUsuario`, `fechaInicio`, `fechaFin`) VALUES
	(1, 1, 1, '2025-08-25 18:52:49', NULL),
	(2, 2, 1, '2025-08-26 12:10:25', '2025-08-26 17:24:08');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
