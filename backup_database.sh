#!/bin/bash
#
# backup_database.sh - Script de backup automático para base de datos MariaDB
#
# Uso:
#   1. Dar permisos de ejecución: chmod +x backup_database.sh
#   2. Ejecutar: sudo ./backup_database.sh
#   3. Opcional: Agregar a crontab para ejecución automática
#      Ejemplo (diario a las 2 AM): 0 2 * * * /ruta/a/backup_database.sh
#
# Requisitos:
#   - MariaDB/MySQL instalado
#   - Acceso root a la base de datos (vía sudo)
#   - Permisos de escritura en /var/bdbackup/
#

# Configuración de la base de datos
DB_HOST="localhost"
DB_PORT="3306"
DB_USER="ovo"
DB_PASS="1234"
DB_NAME="ovo"

# Configuración de backup
BACKUP_DIR="/var/bdbackup"       # Directorio donde se guardarán los backups
TIMESTAMP=$(date +"%d-%m-%Y--%H-%M-%S")  # Formato: dd-mm-yyyy--hh-mm-ss
BACKUP_FILE="${BACKUP_DIR}/${TIMESTAMP}.sql"
BACKUP_FILENAME="${TIMESTAMP}.sql"

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar que el script se ejecute como root
if [ "$EUID" -ne 0 ]; then 
    log_error "Este script debe ejecutarse con permisos de root (sudo)"
    exit 1
fi

# Crear directorio de backup si no existe
if [ ! -d "$BACKUP_DIR" ]; then
    log_info "Creando directorio de backup: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    if [ $? -ne 0 ]; then
        log_error "No se pudo crear el directorio $BACKUP_DIR"
        exit 1
    fi
fi

# Verificar que MariaDB/MySQL esté disponible
if ! command -v mysqldump &> /dev/null; then
    log_error "mysqldump no está instalado o no está en el PATH"
    exit 1
fi

if ! command -v mysql &> /dev/null; then
    log_error "mysql no está instalado o no está en el PATH"
    exit 1
fi

# Realizar el backup
log_info "Iniciando backup de la base de datos '$DB_NAME'..."
log_info "Archivo de destino: $BACKUP_FILE"

# Ejecutar mysqldump con todas las opciones necesarias
# --single-transaction: Para tablas InnoDB sin bloquear
# --routines: Incluye stored procedures y funciones
# --triggers: Incluye triggers
# --events: Incluye eventos programados
# --databases: Incluye CREATE DATABASE
mysqldump -h"$DB_HOST" \
          -P"$DB_PORT" \
          -u"$DB_USER" \
          -p"$DB_PASS" \
          --single-transaction \
          --routines \
          --triggers \
          --events \
          --databases "$DB_NAME" > "$BACKUP_FILE" 2>&1

# Verificar si el backup fue exitoso
if [ $? -eq 0 ]; then
    # Obtener tamaño del archivo en bytes
    FILE_SIZE_BYTES=$(stat -c%s "$BACKUP_FILE" 2>/dev/null || stat -f%z "$BACKUP_FILE" 2>/dev/null)
    FILE_SIZE_HUMAN=$(du -h "$BACKUP_FILE" | cut -f1)
    
    log_info "✓ Backup completado exitosamente"
    log_info "  Tamaño: $FILE_SIZE_HUMAN"
    log_info "  Ubicación: $BACKUP_FILE"
    
    # Registrar el backup en la base de datos
    log_info "Registrando backup en la base de datos..."
    mysql -h"$DB_HOST" \
          -P"$DB_PORT" \
          -u"$DB_USER" \
          -p"$DB_PASS" \
          "$DB_NAME" \
          -e "INSERT INTO backup (fechaBackup, directorio, tamano) VALUES (NOW(), '$BACKUP_FILENAME', $FILE_SIZE_BYTES);" 2>&1
    
    if [ $? -eq 0 ]; then
        log_info "✓ Backup registrado en la base de datos"
    else
        log_warning "⚠ No se pudo registrar el backup en la base de datos, pero el archivo fue creado"
    fi
    
    # Opcional: Comprimir el backup para ahorrar espacio
    # log_info "Comprimiendo backup..."
    # gzip "$BACKUP_FILE"
    # log_info "✓ Backup comprimido: ${BACKUP_FILE}.gz"
    
    # Eliminar backups antiguos según configuración
    # Consultar cantidadBackupConservar de la tabla configuracionbackup
    log_info "Verificando configuración de límite de backups..."
    CANTIDAD_CONSERVAR=$(mysql -h"$DB_HOST" \
                              -P"$DB_PORT" \
                              -u"$DB_USER" \
                              -p"$DB_PASS" \
                              "$DB_NAME" \
                              -sN \
                              -e "SELECT cantidadBackupConservar FROM configuracionbackup LIMIT 1;" 2>/dev/null)
    
    if [ -z "$CANTIDAD_CONSERVAR" ]; then
        log_warning "⚠ No se encontró configuración de límite de backups"
    elif [ "$CANTIDAD_CONSERVAR" -le 0 ]; then
        log_info "  Límite de backups desactivado (valor: $CANTIDAD_CONSERVAR)"
    else
        log_info "  Límite configurado: conservar últimos $CANTIDAD_CONSERVAR backups"
        
        # Contar cuántos backups hay actualmente en la base de datos
        TOTAL_BACKUPS=$(mysql -h"$DB_HOST" \
                             -P"$DB_PORT" \
                             -u"$DB_USER" \
                             -p"$DB_PASS" \
                             "$DB_NAME" \
                             -sN \
                             -e "SELECT COUNT(*) FROM backup;" 2>/dev/null)
        
        log_info "  Total de backups registrados: $TOTAL_BACKUPS"
        
        if [ "$TOTAL_BACKUPS" -gt "$CANTIDAD_CONSERVAR" ]; then
            BACKUPS_A_ELIMINAR=$((TOTAL_BACKUPS - CANTIDAD_CONSERVAR))
            log_info "  Eliminando $BACKUPS_A_ELIMINAR backup(s) antiguo(s)..."
            
            # Obtener los IDs y directorios de los backups a eliminar (los más antiguos)
            BACKUPS_ANTIGUOS=$(mysql -h"$DB_HOST" \
                                    -P"$DB_PORT" \
                                    -u"$DB_USER" \
                                    -p"$DB_PASS" \
                                    "$DB_NAME" \
                                    -sN \
                                    -e "SELECT idBackup, directorio FROM backup ORDER BY fechaBackup ASC LIMIT $BACKUPS_A_ELIMINAR;" 2>/dev/null)
            
            if [ -n "$BACKUPS_ANTIGUOS" ]; then
                ELIMINADOS=0
                echo "$BACKUPS_ANTIGUOS" | while IFS=$'\t' read -r id_backup directorio_backup; do
                    # Eliminar archivo físico
                    if [ -f "$BACKUP_DIR/$directorio_backup" ]; then
                        if rm -f "$BACKUP_DIR/$directorio_backup" 2>/dev/null; then
                            log_info "    ✓ Archivo eliminado: $directorio_backup"
                        else
                            log_warning "    ⚠ No se pudo eliminar archivo: $directorio_backup"
                        fi
                    else
                        log_warning "    ⚠ Archivo no encontrado: $directorio_backup"
                    fi
                    
                    # Eliminar registro de la base de datos
                    mysql -h"$DB_HOST" \
                          -P"$DB_PORT" \
                          -u"$DB_USER" \
                          -p"$DB_PASS" \
                          "$DB_NAME" \
                          -e "DELETE FROM backup WHERE idBackup = $id_backup;" 2>&1
                    
                    if [ $? -eq 0 ]; then
                        log_info "    ✓ Registro eliminado de BD: ID $id_backup"
                        ELIMINADOS=$((ELIMINADOS + 1))
                    else
                        log_warning "    ⚠ No se pudo eliminar registro de BD: ID $id_backup"
                    fi
                done
                log_info "✓ Limpieza completada: $ELIMINADOS backup(s) eliminado(s)"
            else
                log_warning "  No se encontraron backups para eliminar"
            fi
        else
            log_info "  No es necesario eliminar backups (dentro del límite)"
        fi
        
        # Verificar archivos huérfanos (archivos físicos sin registro en BD)
        log_info "Verificando archivos huérfanos en $BACKUP_DIR..."
        ARCHIVOS_HUERFANOS=0
        
        for archivo in "$BACKUP_DIR"/*.sql; do
            if [ -f "$archivo" ]; then
                NOMBRE_ARCHIVO=$(basename "$archivo")
                
                # Verificar si existe en la base de datos
                EXISTE_EN_BD=$(mysql -h"$DB_HOST" \
                                    -P"$DB_PORT" \
                                    -u"$DB_USER" \
                                    -p"$DB_PASS" \
                                    "$DB_NAME" \
                                    -sN \
                                    -e "SELECT COUNT(*) FROM backup WHERE directorio = '$NOMBRE_ARCHIVO';" 2>/dev/null)
                
                if [ "$EXISTE_EN_BD" -eq 0 ]; then
                    log_warning "  Archivo huérfano encontrado: $NOMBRE_ARCHIVO"
                    if rm -f "$archivo" 2>/dev/null; then
                        log_info "    ✓ Archivo huérfano eliminado"
                        ARCHIVOS_HUERFANOS=$((ARCHIVOS_HUERFANOS + 1))
                    else
                        log_warning "    ⚠ No se pudo eliminar archivo huérfano"
                    fi
                fi
            fi
        done
        
        if [ $ARCHIVOS_HUERFANOS -eq 0 ]; then
            log_info "  No se encontraron archivos huérfanos"
        else
            log_info "✓ $ARCHIVOS_HUERFANOS archivo(s) huérfano(s) eliminado(s)"
        fi
    fi
    
    exit 0
else
    log_error "Falló el backup de la base de datos"
    log_error "Revisa los permisos y la conexión a MariaDB"
    
    # Eliminar archivo de backup incompleto si existe
    if [ -f "$BACKUP_FILE" ]; then
        rm "$BACKUP_FILE"
    fi
    
    exit 1
fi
