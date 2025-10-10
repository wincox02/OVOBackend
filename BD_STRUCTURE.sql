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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

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
  CONSTRAINT `FK_aptitudcarrera_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.backup
CREATE TABLE IF NOT EXISTS `backup` (
  `fechaBackup` datetime DEFAULT NULL,
  `directorio` varchar(50) DEFAULT NULL,
  `tamano` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.carrera
CREATE TABLE IF NOT EXISTS `carrera` (
  `idCarrera` int(11) NOT NULL AUTO_INCREMENT,
  `fechaFin` datetime DEFAULT NULL,
  `nombreCarrera` varchar(50) DEFAULT NULL,
  `idTipoCarrera` int(11) DEFAULT NULL,
  PRIMARY KEY (`idCarrera`),
  KEY `FK_carrera_tipocarrera` (`idTipoCarrera`),
  CONSTRAINT `FK_carrera_tipocarrera` FOREIGN KEY (`idTipoCarrera`) REFERENCES `tipocarrera` (`idTipoCarrera`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.carrerainstitucion
CREATE TABLE IF NOT EXISTS `carrerainstitucion` (
  `idCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
  `idEstadoCarreraInstitucion` int(11) NOT NULL,
  `idCarrera` int(11) DEFAULT NULL,
  `idModalidadCarreraInstitucion` int(11) NOT NULL,
  `idInstitucion` int(11) DEFAULT NULL,
  `cantidadMaterias` int(11) NOT NULL,
  `duracionCarrera` decimal(20,2) NOT NULL,
  `fechaFin` datetime DEFAULT NULL,
  `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
  `horasCursado` int(11) NOT NULL,
  `observaciones` varchar(500) NOT NULL,
  `nombreCarrera` varchar(50) NOT NULL,
  `tituloCarrera` varchar(50) NOT NULL,
  `montoCuota` decimal(20,2) NOT NULL,
  PRIMARY KEY (`idCarreraInstitucion`),
  KEY `FK_carrerainstitucion_estadocarrerainstitucion` (`idEstadoCarreraInstitucion`),
  KEY `FK_carrerainstitucion_carrera` (`idCarrera`),
  KEY `FK_carrerainstitucion_modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`),
  KEY `FK_carrerainstitucion_institucion` (`idInstitucion`),
  CONSTRAINT `FK_carrerainstitucion_carrera` FOREIGN KEY (`idCarrera`) REFERENCES `carrera` (`idCarrera`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `FK_carrerainstitucion_estadocarrerainstitucion` FOREIGN KEY (`idEstadoCarreraInstitucion`) REFERENCES `estadocarrerainstitucion` (`idEstadoCarreraInstitucion`) ON UPDATE CASCADE,
  CONSTRAINT `FK_carrerainstitucion_institucion` FOREIGN KEY (`idInstitucion`) REFERENCES `institucion` (`idInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_carrerainstitucion_modalidadcarrerainstitucion` FOREIGN KEY (`idModalidadCarreraInstitucion`) REFERENCES `modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.categoriapermiso
CREATE TABLE IF NOT EXISTS `categoriapermiso` (
  `idCategoriaPermiso` int(11) NOT NULL AUTO_INCREMENT,
  `nombreCategoriaPermiso` varchar(50) NOT NULL,
  PRIMARY KEY (`idCategoriaPermiso`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.configuracionbackup
CREATE TABLE IF NOT EXISTS `configuracionbackup` (
  `frecuencia` varchar(50) DEFAULT NULL,
  `horaEjecucion` time DEFAULT NULL,
  `cantidadBackupConservar` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.estadoacceso
CREATE TABLE IF NOT EXISTS `estadoacceso` (
  `idEstadoAcceso` int(11) NOT NULL AUTO_INCREMENT,
  `nombreEstadoAcceso` varchar(50) DEFAULT NULL,
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idEstadoAcceso`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.estadocarrerainstitucion
CREATE TABLE IF NOT EXISTS `estadocarrerainstitucion` (
  `idEstadoCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
  `nombreEstadoCarreraInstitucion` varchar(50) DEFAULT NULL,
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idEstadoCarreraInstitucion`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.estadoinstitucion
CREATE TABLE IF NOT EXISTS `estadoinstitucion` (
  `idEstadoInstitucion` int(11) NOT NULL AUTO_INCREMENT,
  `nombreEstadoInstitucion` varchar(50) DEFAULT NULL,
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idEstadoInstitucion`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.estadotest
CREATE TABLE IF NOT EXISTS `estadotest` (
  `idEstadoTest` int(11) NOT NULL AUTO_INCREMENT,
  `nombreEstadoTest` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`idEstadoTest`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.estadousuario
CREATE TABLE IF NOT EXISTS `estadousuario` (
  `idEstadoUsuario` int(11) NOT NULL AUTO_INCREMENT,
  `nombreEstadoUsuario` varchar(50) DEFAULT NULL,
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idEstadoUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.genero
CREATE TABLE IF NOT EXISTS `genero` (
  `idGenero` int(11) NOT NULL AUTO_INCREMENT,
  `nombreGenero` varchar(50) NOT NULL,
  PRIMARY KEY (`idGenero`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.grupo
CREATE TABLE IF NOT EXISTS `grupo` (
  `idGrupo` int(11) NOT NULL AUTO_INCREMENT,
  `nombreGrupo` varchar(50) DEFAULT NULL,
  `fechaFin` datetime DEFAULT NULL,
  `descripcion` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idGrupo`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

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

-- La exportación de datos fue deseleccionada.

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
  CONSTRAINT `FK_historialacceso_estadoacceso` FOREIGN KEY (`idEstadoAcceso`) REFERENCES `estadoacceso` (`idEstadoAcceso`) ON UPDATE CASCADE,
  CONSTRAINT `FK_historialacceso_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=272 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.institucion
CREATE TABLE IF NOT EXISTS `institucion` (
  `idInstitucion` int(11) NOT NULL AUTO_INCREMENT,
  `idTipoInstitucion` int(11) NOT NULL,
  `idLocalidad` int(11) DEFAULT NULL,
  `idUsuario` int(11) DEFAULT NULL,
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
  PRIMARY KEY (`idInstitucion`),
  KEY `FK_institucion_tipoinstitucion` (`idTipoInstitucion`),
  KEY `FK_institucion_localidad` (`idLocalidad`),
  KEY `FK_institucion_usuario` (`idUsuario`),
  CONSTRAINT `FK_institucion_localidad` FOREIGN KEY (`idLocalidad`) REFERENCES `localidad` (`idLocalidad`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `FK_institucion_tipoinstitucion` FOREIGN KEY (`idTipoInstitucion`) REFERENCES `tipoinstitucion` (`idTipoInstitucion`) ON UPDATE CASCADE,
  CONSTRAINT `FK_institucion_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

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

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.localidad
CREATE TABLE IF NOT EXISTS `localidad` (
  `idLocalidad` int(11) NOT NULL AUTO_INCREMENT,
  `nombreLocalidad` varchar(50) NOT NULL,
  `idProvincia` int(11) NOT NULL,
  PRIMARY KEY (`idLocalidad`),
  KEY `FK_localidad_provincia` (`idProvincia`),
  CONSTRAINT `FK_localidad_provincia` FOREIGN KEY (`idProvincia`) REFERENCES `provincia` (`idProvincia`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3981 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.modalidadcarrerainstitucion
CREATE TABLE IF NOT EXISTS `modalidadcarrerainstitucion` (
  `idModalidadCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
  `nombreModalidad` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idModalidadCarreraInstitucion`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.pais
CREATE TABLE IF NOT EXISTS `pais` (
  `idPais` int(11) NOT NULL AUTO_INCREMENT,
  `nombrePais` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idPais`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.permiso
CREATE TABLE IF NOT EXISTS `permiso` (
  `idPermiso` int(11) NOT NULL AUTO_INCREMENT,
  `idCategoriaPermiso` int(11) DEFAULT NULL,
  `nombrePermiso` varchar(50) DEFAULT NULL,
  `descripcion` varchar(500) DEFAULT NULL,
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idPermiso`),
  KEY `FK_permiso_categoriapermiso` (`idCategoriaPermiso`),
  CONSTRAINT `FK_permiso_categoriapermiso` FOREIGN KEY (`idCategoriaPermiso`) REFERENCES `categoriapermiso` (`idCategoriaPermiso`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

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
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.preguntafrecuente
CREATE TABLE IF NOT EXISTS `preguntafrecuente` (
  `idPreguntaFrecuente` int(11) NOT NULL AUTO_INCREMENT,
  `idCarreraInstitucion` int(11) NOT NULL,
  `fechaFin` datetime DEFAULT NULL,
  `nombrePregunta` varchar(50) NOT NULL,
  `respuesta` varchar(50) NOT NULL,
  PRIMARY KEY (`idPreguntaFrecuente`),
  KEY `FK_preguntafrecuente_carrerainstitucion` (`idCarreraInstitucion`),
  CONSTRAINT `FK_preguntafrecuente_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.provincia
CREATE TABLE IF NOT EXISTS `provincia` (
  `idProvincia` int(11) NOT NULL AUTO_INCREMENT,
  `nombreProvincia` varchar(50) NOT NULL,
  `idPais` int(11) NOT NULL,
  PRIMARY KEY (`idProvincia`),
  KEY `FK_provincia_pais` (`idPais`),
  CONSTRAINT `FK_provincia_pais` FOREIGN KEY (`idPais`) REFERENCES `pais` (`idPais`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=394 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.test
CREATE TABLE IF NOT EXISTS `test` (
  `idResultadoCuestionario` int(11) NOT NULL AUTO_INCREMENT,
  `idEstadoTest` int(11) DEFAULT NULL,
  `idUsuario` int(11) NOT NULL,
  `fechaResultadoCuestionario` datetime NOT NULL DEFAULT current_timestamp(),
  `idChatIA` varchar(50) NOT NULL,
  `HistorialPreguntas` longtext DEFAULT NULL,
  PRIMARY KEY (`idResultadoCuestionario`),
  KEY `FK_test_usuario` (`idUsuario`),
  KEY `FK_test_estadotest` (`idEstadoTest`),
  CONSTRAINT `FK_test_estadotest` FOREIGN KEY (`idEstadoTest`) REFERENCES `estadotest` (`idEstadoTest`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_test_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

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

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.testcarrerainstitucion
CREATE TABLE IF NOT EXISTS `testcarrerainstitucion` (
  `afinidadCarrera` double DEFAULT NULL,
  `idTest` int(11) DEFAULT NULL,
  `idCarreraInstitucion` int(11) DEFAULT NULL,
  KEY `FK_testcarrerainstitucion_test` (`idTest`),
  KEY `FK_testcarrerainstitucion_carrerainstitucion` (`idCarreraInstitucion`),
  CONSTRAINT `FK_testcarrerainstitucion_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON UPDATE CASCADE,
  CONSTRAINT `FK_testcarrerainstitucion_test` FOREIGN KEY (`idTest`) REFERENCES `test` (`idResultadoCuestionario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.tipoaccion
CREATE TABLE IF NOT EXISTS `tipoaccion` (
  `idTipoAccion` int(11) NOT NULL AUTO_INCREMENT,
  `nombreTipoAccion` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idTipoAccion`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.tipocarrera
CREATE TABLE IF NOT EXISTS `tipocarrera` (
  `idTipoCarrera` int(11) NOT NULL AUTO_INCREMENT,
  `nombreTipoCarrera` varchar(50) DEFAULT NULL,
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idTipoCarrera`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.tipoinstitucion
CREATE TABLE IF NOT EXISTS `tipoinstitucion` (
  `idTipoInstitucion` int(11) NOT NULL AUTO_INCREMENT,
  `nombreTipoInstitucion` varchar(50) DEFAULT NULL,
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idTipoInstitucion`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

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
  `idLocalidad` int(11) DEFAULT NULL,
  PRIMARY KEY (`idUsuario`),
  KEY `FK_usuario_genero` (`idGenero`),
  KEY `FK_usuario_localidad` (`idLocalidad`),
  CONSTRAINT `FK_usuario_genero` FOREIGN KEY (`idGenero`) REFERENCES `genero` (`idGenero`) ON UPDATE CASCADE,
  CONSTRAINT `FK_usuario_localidad` FOREIGN KEY (`idLocalidad`) REFERENCES `localidad` (`idLocalidad`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.usuarioestado
CREATE TABLE IF NOT EXISTS `usuarioestado` (
  `idUsuarioEstado` int(11) NOT NULL AUTO_INCREMENT,
  `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
  `fechaFin` datetime DEFAULT NULL,
  `idEstadoUsuario` int(11) NOT NULL,
  `idUsuario` int(11) NOT NULL,
  PRIMARY KEY (`idUsuarioEstado`),
  KEY `FK_usuarioestado_estadousuario` (`idEstadoUsuario`),
  KEY `FK_usuarioestado_usuario` (`idUsuario`),
  CONSTRAINT `FK_usuarioestado_estadousuario` FOREIGN KEY (`idEstadoUsuario`) REFERENCES `estadousuario` (`idEstadoUsuario`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_usuarioestado_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

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
  CONSTRAINT `FK_usuariogrupo_grupo` FOREIGN KEY (`idGrupo`) REFERENCES `grupo` (`idGrupo`) ON UPDATE CASCADE,
  CONSTRAINT `FK_usuariogrupo_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla ovo.usuariopermiso
CREATE TABLE IF NOT EXISTS `usuariopermiso` (
  `idUsuarioPermiso` int(11) NOT NULL AUTO_INCREMENT,
  `idUsuario` int(11) NOT NULL,
  `idPermiso` int(11) NOT NULL,
  `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
  `fechaFin` datetime DEFAULT NULL,
  PRIMARY KEY (`idUsuarioPermiso`),
  KEY `FK_usuariopermiso_permiso` (`idPermiso`),
  KEY `FK_usuariopermiso_usuario` (`idUsuario`),
  CONSTRAINT `FK_usuariopermiso_permiso` FOREIGN KEY (`idPermiso`) REFERENCES `permiso` (`idPermiso`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_usuariopermiso_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
