#!/bin/bash
#
# restore_database.sh - Script de restauración de base de datos MariaDB
#
# Uso:
#   1. Dar permisos de ejecución: chmod +x restore_database.sh
#   2. Ejecutar: sudo ./restore_database.sh <nombre_archivo_backup>
#      Ejemplo: sudo ./restore_database.sh 01-11-2025--14-30-00.sql
#
# Requisitos:
#   - MariaDB/MySQL instalado
#   - Acceso a la base de datos
#   - Permisos de lectura en /var/bdbackup/
#

# Configuración de la base de datos
DB_HOST="localhost"
DB_PORT="3306"
DB_USER="ovo"
DB_PASS="1234"
DB_NAME="ovo"

# Configuración de backup
BACKUP_DIR="/var/bdbackup"

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_question() {
    echo -e "${BLUE}[?]${NC} $1"
}

# Verificar que el script se ejecute como root
if [ "$EUID" -ne 0 ]; then 
    log_error "Este script debe ejecutarse con permisos de root (sudo)"
    exit 1
fi

# Verificar que se proporcione el nombre del archivo
if [ -z "$1" ]; then
    log_error "Uso: $0 <nombre_archivo_backup>"
    log_error "Ejemplo: $0 01-11-2025--14-30-00.sql"
    exit 1
fi

BACKUP_FILENAME="$1"
BACKUP_FILE="${BACKUP_DIR}/${BACKUP_FILENAME}"

# Verificar que el archivo de backup exista
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "El archivo de backup no existe: $BACKUP_FILE"
    log_error "Verifica que el nombre del archivo sea correcto"
    exit 1
fi

# Verificar que MariaDB/MySQL esté disponible
if ! command -v mysql &> /dev/null; then
    log_error "mysql no está instalado o no está en el PATH"
    exit 1
fi

# Obtener información del archivo
FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
FILE_DATE=$(stat -c%y "$BACKUP_FILE" 2>/dev/null | cut -d' ' -f1,2 || stat -f%Sm "$BACKUP_FILE" 2>/dev/null)

log_info "═══════════════════════════════════════════════════════"
log_info "  RESTAURACIÓN DE BASE DE DATOS"
log_info "═══════════════════════════════════════════════════════"
log_info "Archivo: $BACKUP_FILENAME"
log_info "Tamaño: $FILE_SIZE"
log_info "Fecha del backup: $FILE_DATE"
log_info "Base de datos: $DB_NAME"
log_info "═══════════════════════════════════════════════════════"
echo ""

# Confirmación del usuario
log_warning "⚠  ADVERTENCIA: Esta operación reemplazará TODOS los datos actuales"
log_warning "   de la base de datos '$DB_NAME' con los del backup."
echo ""
log_question "¿Está seguro que desea continuar? (escriba 'SI' para confirmar): "
read -r CONFIRMACION

if [ "$CONFIRMACION" != "SI" ]; then
    log_info "Restauración cancelada por el usuario"
    exit 0
fi

echo ""
log_info "Iniciando restauración de la base de datos..."

# Crear backup de seguridad antes de restaurar (opcional pero recomendado)
log_info "Creando backup de seguridad de la base de datos actual..."
SAFETY_BACKUP="${BACKUP_DIR}/pre-restore-$(date +"%d-%m-%Y--%H-%M-%S").sql"
mysqldump -h"$DB_HOST" \
          -P"$DB_PORT" \
          -u"$DB_USER" \
          -p"$DB_PASS" \
          --single-transaction \
          --routines \
          --triggers \
          --events \
          --databases "$DB_NAME" > "$SAFETY_BACKUP" 2>&1

if [ $? -eq 0 ]; then
    SAFETY_SIZE=$(du -h "$SAFETY_BACKUP" | cut -f1)
    log_info "✓ Backup de seguridad creado: $(basename $SAFETY_BACKUP) ($SAFETY_SIZE)"
else
    log_warning "⚠ No se pudo crear el backup de seguridad"
    log_question "¿Desea continuar sin backup de seguridad? (escriba 'SI' para confirmar): "
    read -r CONTINUE
    if [ "$CONTINUE" != "SI" ]; then
        log_info "Restauración cancelada"
        exit 0
    fi
fi

echo ""
log_info "Restaurando base de datos desde: $BACKUP_FILENAME"

# Ejecutar la restauración
mysql -h"$DB_HOST" \
      -P"$DB_PORT" \
      -u"$DB_USER" \
      -p"$DB_PASS" \
      "$DB_NAME" < "$BACKUP_FILE" 2>&1

# Verificar si la restauración fue exitosa
if [ $? -eq 0 ]; then
    echo ""
    log_info "════════════════════════════════════════════════════════"
    log_info "  ✓ RESTAURACIÓN COMPLETADA EXITOSAMENTE"
    log_info "════════════════════════════════════════════════════════"
    log_info "Base de datos: $DB_NAME"
    log_info "Archivo restaurado: $BACKUP_FILENAME"
    if [ -f "$SAFETY_BACKUP" ]; then
        log_info "Backup de seguridad: $(basename $SAFETY_BACKUP)"
    fi
    
    # Eliminar el archivo de backup restaurado
    log_info "Eliminando archivo de backup restaurado..."
    if rm -f "$BACKUP_FILE" 2>/dev/null; then
        log_info "✓ Archivo eliminado: $BACKUP_FILENAME"
    else
        log_warning "⚠ No se pudo eliminar el archivo: $BACKUP_FILENAME"
    fi
    
    log_info "════════════════════════════════════════════════════════"
    echo ""
    
    exit 0
else
    echo ""
    log_error "════════════════════════════════════════════════════════"
    log_error "  ✗ FALLÓ LA RESTAURACIÓN"
    log_error "════════════════════════════════════════════════════════"
    log_error "No se pudo restaurar la base de datos"
    log_error "Revisa los permisos y la conexión a MariaDB"
    
    if [ -f "$SAFETY_BACKUP" ]; then
        log_info ""
        log_info "Puedes restaurar el backup de seguridad con:"
        log_info "  $0 $(basename $SAFETY_BACKUP)"
    fi
    log_error "════════════════════════════════════════════════════════"
    echo ""
    
    exit 1
fi
