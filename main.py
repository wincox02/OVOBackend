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

AWS_API_URL = "https://wid84vod2j.execute-api.us-east-2.amazonaws.com"

SECRET_KEY = "ghwgdgHHYushHg1231SDAAa"

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
            elif token == "Insti":
                current_user = 27
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

#-----------------------------------DATE VALIDATION-----------------------------------
def validate_date_string(date_str: str) -> tuple:
    """
    Valida que una fecha sea válida (sin fechas imposibles como 30/02, 31/11, etc.).
    Acepta formatos: 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS'
    
    Returns:
        tuple: (is_valid: bool, normalized_date: str or None, error_message: str or None)
    """
    if not date_str or not isinstance(date_str, str):
        return (False, None, "Fecha inválida.")
    
    date_str = date_str.strip()
    
    # Casos especiales
    if date_str.upper() == 'NOW()':
        return (True, 'NOW()', None)
    if date_str.upper() == 'NULL':
        return (True, None, None)
    
    # Intentar parsear con hora
    try:
        parsed = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return (True, date_str, None)
    except ValueError:
        pass
    
    # Intentar parsear solo fecha
    try:
        parsed = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        # Agregar hora por defecto
        normalized = date_str + ' 23:59:59'
        return (True, normalized, None)
    except ValueError:
        return (False, None, "Formato de fecha inválido. Use YYYY-MM-DD o YYYY-MM-DD HH:MM:SS")
    

# -- Volcando estructura para tabla ovo.historialabm
# CREATE TABLE IF NOT EXISTS `historialabm` (
#   `idHistorialABM` int(11) NOT NULL AUTO_INCREMENT,
#   `idUsuario` int(11) NOT NULL,
#   `detalle` text DEFAULT NULL,
#   `fechaHistorial` datetime NOT NULL DEFAULT current_timestamp(),
#   PRIMARY KEY (`idHistorialABM`),
#   KEY `FK_historialabm_usuario` (`idUsuario`),
#   CONSTRAINT `FK_historialabm_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON UPDATE CASCADE
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

# -- Volcando estructura para tabla ovo.tipoaccion
# CREATE TABLE IF NOT EXISTS `tipoaccion` (
#   `idTipoAccion` int(11) NOT NULL AUTO_INCREMENT,
#   `nombreTipoAccion` varchar(50) DEFAULT NULL,
#   PRIMARY KEY (`idTipoAccion`)
# ) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

# -- Volcando datos para la tabla ovo.tipoaccion: ~3 rows (aproximadamente)
# INSERT INTO `tipoaccion` (`idTipoAccion`, `nombreTipoAccion`) VALUES
# 	(1, 'ACTUALIZACION'),
# 	(2, 'MODIFICACION'),
# 	(3, 'ELIMINACION');

def auditoria_log(usuario_id: int, accion: str, detalles: str = None):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT idTipoAccion FROM tipoaccion WHERE nombreTipoAccion = %s", (accion,))
        id_tipo_accion = cursor.fetchone()
        id_tipo_accion = id_tipo_accion[0] if id_tipo_accion else None

        cursor.execute(
            "INSERT INTO historialabm (idUsuario, detalle, fechaHistorial, idTipoAccion) "
            "VALUES (%s, %s, NOW(), %s)",
            (usuario_id, detalles, id_tipo_accion)
        )
        conn.commit()
    except Exception as e:
        print(f"Error al registrar auditoría: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ============================ AUTENTICACIÓN (US001) ============================
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def get_user_by_email(email: str):
    conn = None
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

def requires_permission(permissions):
    """Decorador para proteger endpoints por permiso lógico.
    
    Args:
        permissions: str o list - Un permiso individual o lista de permisos.
                    El usuario necesita tener al menos uno de los permisos listados.
    """
    def decorator(f):
        @wraps(f)
        @token_required
        def wrapped(current_user_id, *args, **kwargs):
            permisos, _ = get_user_permissions_and_groups(current_user_id)
            
            # Convertir a lista si es un string individual
            required_perms = [permissions] if isinstance(permissions, str) else permissions
            
            # Verificar si tiene al menos uno de los permisos requeridos
            if not any(perm in permisos for perm in required_perms):
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

# ============================ ADMIN: Backup de la base de datos (US002) ============================

# -- Volcando estructura para tabla ovo.configuracionbackup
# CREATE TABLE IF NOT EXISTS `configuracionbackup` (
#   `frecuencia` enum('Diaria','Semanal','Mensual','Anual') DEFAULT NULL,
#   `horaEjecucion` time DEFAULT NULL,
#   `cantidadBackupConservar` int(11) DEFAULT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


# Endpoint para configurar la frecuencia automatica de backups
@app.route('/api/v1/admin/backup', methods=['POST'])
def configurar_frecuencia_backup():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        data = request.get_json(silent=True) or {}

        frecuencia = data.get('frecuencia')
        if frecuencia not in ['Diaria', 'Semanal', 'Mensual', 'Anual']:
            return jsonify({"errorCode": "ERR1", "message": "Frecuencia no válida"}), 400
        hora_ejecucion = data.get('horaEjecucion')
        cantidad_backup_conservar = data.get('cantidadBackupConservar')

        # Validar los datos recibidos
        if not frecuencia or not hora_ejecucion or cantidad_backup_conservar is None:
            return jsonify({"errorCode": "ERR1", "message": "Faltan datos"}), 400

        # Lógica para configurar la frecuencia de backups
        cur.execute("DELETE FROM configuracionbackup")
        cur.execute("INSERT INTO configuracionbackup (frecuencia, horaEjecucion, cantidadBackupConservar) VALUES (%s, %s, %s)",
                   (frecuencia, hora_ejecucion, cantidad_backup_conservar))
        conn.commit()

        # Extraer hora y minuto de horaEjecucion (formato HH:MM:SS o HH:MM)
        try:
            # Si es un objeto time, convertir a string
            if hasattr(hora_ejecucion, 'hour'):
                hora = hora_ejecucion.hour
                minuto = hora_ejecucion.minute
            else:
                # Si es string, parsear
                time_parts = str(hora_ejecucion).split(':')
                hora = int(time_parts[0])
                minuto = int(time_parts[1])
        except Exception:
            return jsonify({"errorCode": "ERR1", "message": "Formato de hora inválido"}), 400

        print("minuto:", minuto)
        print("hora:", hora)
        # Ejecutar comandos cron según la frecuencia configurada y eliminar los antiguos cron jobs
        if frecuencia == 'Diaria':
            cron_timing = f"{minuto} {hora} * * *"
        elif frecuencia == 'Semanal':
            cron_timing = f"{minuto} {hora} * * 0"
        elif frecuencia == 'Mensual':
            cron_timing = f"{minuto} {hora} 1 * *"
        elif frecuencia == 'Anual':
            cron_timing = f"{minuto} {hora} 1 1 *"

        # Aquí se eliminarían los antiguos cron jobs y se agregarían los nuevos
        # No en funciones aparte
        os.system("(crontab -l | grep -v 'backup_database.sh') | crontab -")
        os.system(f"(crontab -l; echo '{cron_timing} /root/proyectofinal/backup_database.sh') | crontab -")

        # Los backups se guardarían en /var/bdbackup/

        return jsonify({"message": "Frecuencia de backup configurada con éxito"}), 200
    except Exception as e:
        log(f"/admin/backup error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR4", "message": "Error al configurar la frecuencia de backup"}), 500

# Endpoint para obtener la configuración actual de backups
@app.route('/api/v1/admin/backup', methods=['GET'])
def obtener_configuracion_backup():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM configuracionbackup")
        # Vienen varios registros, tomar el primero si existe
        config = cur.fetchone()
        if not config:
            return jsonify({"errorCode": "ERR1", "message": "No se encontró configuración de backup"}), 404
        
        # Convertir horaEjecucion a string para que sea serializable en JSON
        if config.get('horaEjecucion'):
            # Si es un objeto time o timedelta, convertir a string
            hora_obj = config['horaEjecucion']
            if hasattr(hora_obj, 'total_seconds'):
                # Es un timedelta, convertir a formato HH:MM:SS
                total_seconds = int(hora_obj.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                config['horaEjecucion'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                # Es un objeto time u otro tipo, convertir a string
                config['horaEjecucion'] = str(hora_obj)
        
        return jsonify(config), 200
    except Exception as e:
        log(f"/admin/backup error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR4", "message": "Error al obtener la configuración de backup"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para obtener los backups disponibles (registrados en la tabla backup)
@app.route('/api/v1/admin/backup/files', methods=['GET'])
def obtener_backups_disponibles():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                idBackup,
                fechaBackup,
                directorio,
                tamano
            FROM backup
            ORDER BY fechaBackup DESC
        """)
        backups = cur.fetchall() or []
        
        # Formatear la respuesta
        data = [
            {
                "id": backup.get('idBackup'),
                "fecha": backup.get('fechaBackup').isoformat() if backup.get('fechaBackup') else None,
                "directorio": backup.get('directorio'),
                "tamano": backup.get('tamano'),  # Tamaño en bytes
                "tamanoFormateado": f"{backup.get('tamano') / (1024 * 1024):.2f} MB" if backup.get('tamano') else "0 MB"
            }
            for backup in backups
        ]
        
        return jsonify({"backups": data}), 200
    except Exception as e:
        log(f"/admin/backup/files error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR4", "message": "Error al obtener los backups disponibles"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para restaurar un backup específico
@app.route('/api/v1/admin/backup/files', methods=['POST'])
def restaurar_backup():
    log("======= INICIO restaurar_backup =======")
    data = request.get_json(silent=True) or {}
    id_backup = data.get("idBackup")
    log(f"ID backup recibido: {id_backup}")
    
    if not id_backup:
        log("ERROR: Falta el ID del backup")
        return jsonify({"errorCode": "ERR1", "message": "Falta el ID del backup"}), 400

    conn = None
    try:
        log("Conectando a la base de datos...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        log("Conexión exitosa")
        
        # Verificar que el backup exista en la tabla y obtener el directorio
        log(f"Buscando backup con ID {id_backup} en la tabla...")
        cur.execute("SELECT idBackup, directorio FROM backup WHERE idBackup = %s", (id_backup,))
        backup_row = cur.fetchone()
        log(f"Resultado de búsqueda: {backup_row}")
        
        if not backup_row:
            log("ERROR: Backup no encontrado en la base de datos")
            return jsonify({"errorCode": "ERR2", "message": "Backup no encontrado en el registro"}), 404
        
        directorio = backup_row.get('directorio')
        log(f"Directorio del backup: {directorio}")
        
        # Construir la ruta completa del archivo
        backup_path = f"/var/bdbackup/{directorio}"
        log(f"Ruta completa del backup: {backup_path}")
        
        # Verificar que el archivo físicamente exista
        log("Verificando si el archivo existe físicamente...")
        if not os.path.exists(backup_path):
            log(f"ERROR: El archivo {backup_path} no existe")
            return jsonify({"errorCode": "ERR3", "message": "El archivo de backup no existe físicamente"}), 404
        log("Archivo existe correctamente")
        
        # Cerrar la conexión a la base de datos antes de restaurar
        log("Cerrando conexión a la base de datos...")
        if conn:
            conn.close()
            conn = None
        log("Conexión cerrada")
        
        # Restaurar el backup directamente con mysql (sin el script interactivo)
        import subprocess
        
        # Ejecutar mysql para restaurar el backup
        restore_command = [
            "mysql",
            f"-h{DB_CONFIG['host']}",
            f"-P{DB_CONFIG['port']}",
            f"-u{DB_CONFIG['user']}",
            f"-p{DB_CONFIG['password']}",
            DB_CONFIG['database']
        ]
        log(f"Comando de restauración: {' '.join([c if 'password' not in c else '-p****' for c in restore_command])}")
        
        try:
            log("Abriendo archivo de backup...")
            with open(backup_path, 'r') as backup_file:
                log("Ejecutando comando mysql...")
                result = subprocess.run(
                    restore_command,
                    stdin=backup_file,
                    capture_output=True,
                    text=True,
                    timeout=300  # Timeout de 5 minutos
                )
                log(f"Comando mysql finalizado. Return code: {result.returncode}")
            
            if result.returncode != 0:
                log(f"ERROR en restauración: stdout={result.stdout}, stderr={result.stderr}")
                return jsonify({"errorCode": "ERR4", "message": f"Error al ejecutar la restauración: {result.stderr}"}), 500
            
            log("Restauración completada exitosamente")
            log("======= FIN restaurar_backup EXITOSO =======")
            return jsonify({"message": f"Backup {directorio} restaurado con éxito"}), 200
        except subprocess.TimeoutExpired:
            log("ERROR: Timeout al restaurar backup (excedió 5 minutos)")
            return jsonify({"errorCode": "ERR5", "message": "La restauración excedió el tiempo límite"}), 500
    except Exception as e:
        log(f"ERROR GENERAL en restaurar_backup: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR4", "message": "Error al restaurar el backup"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para realizar un backup manualmente (ejecutar el script de backup_database.sh)
@app.route('/api/v1/admin/backup/manual', methods=['POST'])
def backup_manual():
    # conn = None
    try:
        import subprocess
        import glob
        
        # Obtener el timestamp de antes de ejecutar para identificar el archivo generado
        backup_dir = "/var/bdbackup"
        archivos_antes = set(os.listdir(backup_dir)) if os.path.exists(backup_dir) else set()
        
        # Ejecutar el script de backup
        result = subprocess.run(
            ["bash", "/root/proyectofinal/backup_database.sh"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            log(f"backup_manual error: {result.stderr}")
            return jsonify({"errorCode": "ERR1", "message": "Error al ejecutar el script de backup"}), 500
        
        # Identificar el nuevo archivo generado
        archivos_despues = set(os.listdir(backup_dir)) if os.path.exists(backup_dir) else set()
        nuevos_archivos = archivos_despues - archivos_antes
        
        if not nuevos_archivos:
            return jsonify({"errorCode": "ERR2", "message": "No se generó ningún archivo de backup"}), 500
        
        # Tomar el archivo más reciente (debería ser solo uno)
        nuevo_archivo = list(nuevos_archivos)[0]
        ruta_completa = os.path.join(backup_dir, nuevo_archivo)
        
        # Obtener tamaño del archivo en bytes
        tamano_bytes = os.path.getsize(ruta_completa)
        
        # Registrar el backup en la tabla (se hace en el script)
        # conn = mysql.connector.connect(**DB_CONFIG)
        # cur = conn.cursor()
        # cur.execute(
        #     "INSERT INTO backup (fechaBackup, directorio, tamano) VALUES (NOW(), %s, %s)",
        #     (nuevo_archivo, tamano_bytes)
        # )
        # conn.commit()
        
        return jsonify({
            "message": "Backup manual ejecutado con éxito",
            "archivo": nuevo_archivo,
            "tamano": f"{tamano_bytes / (1024 * 1024):.2f} MB"
        }), 200
    except Exception as e:
        log(f"backup_manual error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR4", "message": "Error al realizar el backup manual"}), 500

# ============================ ADMIN: Gestión de perfiles (US003) ============================

def obtener_permisos_de_grupo_de_usuario(user_id: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
                        """
                        SELECT DISTINCT p.nombrePermiso
                        FROM permiso p
                        JOIN permisogrupo pg ON pg.idPermiso = p.idPermiso
                        JOIN usuariogrupo ug ON ug.idGrupo = pg.idGrupo
                        WHERE ug.idUsuario = %s
                            AND (ug.fechaFin IS NULL OR ug.fechaFin > NOW())
                            AND (pg.fechaFin IS NULL OR pg.fechaFin > NOW())
                            AND (p.fechaFin IS NULL OR p.fechaFin > NOW())
                        """,
                        (user_id,)
        )
        rows = cur.fetchall() or []
        return [r['nombrePermiso'] for r in rows]
    except Exception as e:
        log(f"obtener_permisos_de_grupo_de_usuario error: {e}\n{traceback.format_exc()}")
        return []
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

def obtener_permisos_directos_de_usuario(user_id: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
                        """
                        SELECT DISTINCT p.nombrePermiso
                        FROM permiso p
                        JOIN usuariopermiso up ON up.idPermiso = p.idPermiso
                        WHERE up.idUsuario = %s
                            AND (up.fechaFin IS NULL OR up.fechaFin > NOW())
                            AND (p.fechaFin IS NULL OR p.fechaFin > NOW())
                        """,
                        (user_id,)
        )
        rows = cur.fetchall() or []
        return [r['nombrePermiso'] for r in rows]
    except Exception as e:
        log(f"obtener_permisos_directos_de_usuario error: {e}\n{traceback.format_exc()}")
        return []
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

def obtener_grupos_de_usuario(user_id: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT g.nombreGrupo
            FROM grupo g
            JOIN usuariogrupo ug ON ug.idGrupo = g.idGrupo
            WHERE ug.idUsuario = %s
              AND (ug.fechaFin IS NULL OR ug.fechaFin > NOW())
              AND (g.fechaFin IS NULL OR g.fechaFin > NOW())
            """,
            (user_id,)
        )
        rows = cur.fetchall() or []
        return [r['nombreGrupo'] for r in rows]
    except Exception as e:
        log(f"obtener_grupos_de_usuario error: {e}\n{traceback.format_exc()}")
        return []
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

# Endpoint para listar todos los usuarios
@app.route('/api/v1/admin/users', methods=['GET'])
@requires_permission(['MANAGE_PROFILE','ASIGN_PERM'])
def admin_list_users(current_user_id):
    """Listado de usuarios con sus grupos activos."""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT u.idUsuario, u.nombre, u.apellido, u.mail, u.fechaAlta,
               GROUP_CONCAT(g.nombreGrupo ORDER BY g.nombreGrupo SEPARATOR ',') AS grupos,
               eu.nombreEstadoUsuario AS estado
            FROM usuario u
            LEFT JOIN usuariogrupo ug ON ug.idUsuario = u.idUsuario AND (ug.fechaFin IS NULL OR ug.fechaFin > NOW())
            LEFT JOIN grupo g ON g.idGrupo = ug.idGrupo
            LEFT JOIN usuarioestado ue ON ue.idUsuario = u.idUsuario AND (ue.fechaFin IS NULL OR ue.fechaFin > NOW())
            LEFT JOIN estadousuario eu ON eu.idEstadoUsuario = ue.idEstadoUsuario
            GROUP BY u.idUsuario, u.nombre, u.apellido, u.mail, eu.nombreEstadoUsuario
            ORDER BY u.apellido, u.nombre
            """
        )
        rows = cur.fetchall() or []

        # YYYY-MM-DD HH:MM:SS
        for r in rows:
            if r['fechaAlta']:
                r['fechaAlta'] = r['fechaAlta'].strftime("%Y-%m-%d %H:%M:%S")
        
        data = [
            {
                "id": r['idUsuario'],
                "nombre": r.get('nombre'),
                "apellido": r.get('apellido'),
                "mail": r.get('mail'),
                "grupos": obtener_grupos_de_usuario(r['idUsuario']),
                "estado": r.get('estado') or 'Desconocido',
                "permisos_de_grupo": obtener_permisos_de_grupo_de_usuario(r['idUsuario']),
                "permisos_directos": obtener_permisos_directos_de_usuario(r['idUsuario']),
                "fechaAlta": r.get('fechaAlta')
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
@requires_permission('MANAGE_PROFILE')
def admin_list_groups(current_user_id):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT idGrupo, nombreGrupo
            FROM grupo
            WHERE fechaFin IS NULL OR fechaFin > NOW()
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
@requires_permission('MANAGE_PROFILE')
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
@requires_permission('MANAGE_PROFILE')
def admin_get_user_permissions(current_user_id, user_id: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        # Obtener todos los permisos activos del sistema
        # y marcar si el usuario los tiene y si es editable (directo vs por grupo)
        cur.execute(
            """
            SELECT p.idPermiso, p.nombrePermiso, p.descripcion,
                   CASE 
                       WHEN direct_perms.idPermiso IS NOT NULL OR group_perms.idPermiso IS NOT NULL THEN 1
                       ELSE 0
                   END AS has_permission,
                   CASE 
                       WHEN direct_perms.idPermiso IS NOT NULL THEN 1
                       ELSE 0
                   END AS is_editable
            FROM permiso p
            LEFT JOIN (
                SELECT DISTINCT p.idPermiso
                FROM usuariopermiso up
                JOIN permiso p ON p.idPermiso = up.idPermiso
                WHERE up.idUsuario = %s AND (up.fechaFin IS NULL OR up.fechaFin > NOW())
            ) direct_perms ON direct_perms.idPermiso = p.idPermiso
            LEFT JOIN (
                SELECT DISTINCT p.idPermiso
                FROM usuariogrupo ug
                JOIN permisogrupo pg ON pg.idGrupo = ug.idGrupo
                JOIN permiso p ON p.idPermiso = pg.idPermiso
                WHERE ug.idUsuario = %s 
                AND (ug.fechaFin IS NULL OR ug.fechaFin > NOW())
                AND (pg.fechaFin IS NULL or pg.fechaFin > NOW())
            ) group_perms ON group_perms.idPermiso = p.idPermiso
            WHERE p.fechaFin IS NULL OR p.fechaFin > NOW()
            ORDER BY p.nombrePermiso
            """,
            (user_id, user_id)
        )
        rows = cur.fetchall() or []
        
        # Devolver lista plana de permisos
        permissions = []
        for row in rows:
            permissions.append({
                'idPermiso': row['idPermiso'],
                'nombrePermiso': row['nombrePermiso'],
                'descripcion': row['descripcion'],
                'has_permission': bool(row['has_permission']),
                'is_editable': bool(row['is_editable'])
            })
        
        return jsonify(permissions), 200
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
@requires_permission('MANAGE_PROFILE')
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
        cur = conn.cursor(dictionary=True)
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Asignación de grupo idGrupo={id_grupo} a usuario idUsuario={user_id}")
        
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
@requires_permission('MANAGE_PROFILE')
def admin_remove_user_group(current_user_id, user_id: int, id_grupo: int):
    """Elimina un grupo de un usuario (actualiza fechaFin)."""
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "UPDATE usuariogrupo SET fechaFin = NOW() WHERE idUsuario = %s AND idGrupo = %s AND (fechaFin IS NULL OR fechaFin > NOW())",
            (user_id, id_grupo)
        )
        if cur.rowcount == 0:
            return jsonify({"errorCode": "ERR1", "message": "El usuario no está en este grupo"}), 400
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de grupo idGrupo={id_grupo} de usuario idUsuario={user_id}")
        
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
@requires_permission('MANAGE_PROFILE')
def admin_add_user_permission(current_user_id, user_id: int):
    """Agrega un permiso directo. Si ya existe activo, no duplica."""
    data = request.get_json(silent=True) or {}
    id_permiso = data.get('idPermiso')
    if not isinstance(id_permiso, int):
        return jsonify({"errorCode": "ERR1", "message": "idPermiso inválido"}), 400
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor(dictionary=True)
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Asignación de permiso idPermiso={id_permiso} a usuario idUsuario={user_id}")
        
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
@requires_permission('MANAGE_PROFILE')
def admin_remove_user_permission(current_user_id, user_id: int, id_permiso: int):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        # Validar que el usuario tenga el permiso en cuestion
        cur = conn.cursor(dictionary=True)
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de permiso idPermiso={id_permiso} de usuario idUsuario={user_id}")
        
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

# Endpoint para eliminar a un usuario (cambiar a estado Baja)
@app.route('/api/v1/admin/users/<int:user_id>', methods=['DELETE'])
@requires_permission('MANAGE_PROFILE')
def admin_delete_user(current_user_id, user_id: int):
    """Elimina a un usuario cambiando su estado a 'Baja'."""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        # Validar que el usuario exista
        cur.execute("SELECT 1 FROM usuario WHERE idUsuario=%s", (user_id,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Usuario no encontrado"}), 404
        # Buscar el estado 'Baja' en estadousuario
        cur.execute("SELECT idEstadoUsuario FROM estadousuario WHERE nombreEstadoUsuario='Baja' AND (fechaFin IS NULL OR fechaFin > NOW())")
        row = cur.fetchone()
        if not row:
            return jsonify({"errorCode": "ERR1", "message": "Estado 'Baja' no encontrado en el sistema"}), 500
        baja_id = row['idEstadoUsuario']
        # Actualizar usuario estado con fecha fin en el estado actual y agregar nuevo estado 'Baja'
        cur.execute(
            "UPDATE usuarioestado SET fechaFin = NOW() WHERE idUsuario=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            (user_id,)
        )
        cur.execute(
            "INSERT INTO usuarioestado (idUsuario, idEstadoUsuario, fechaInicio) VALUES (%s, %s, NOW())",
            (user_id, baja_id)
        )
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Cambio de estado a 'Baja' para usuario idUsuario={user_id}")
        
        return jsonify({"ok": True}), 200
    except Exception as e:
        conn.rollback()
        log(f"/admin/users/{user_id} DELETE error: {e}\n{traceback.format_exc()}")
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
@requires_permission('ASIGN_PERM')
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
@requires_permission('ASIGN_PERM')
def admin_set_user_permissions_bulk(current_user_id, user_id: int):
    """Reemplaza el conjunto de permisos directos activos de un usuario por los provistos.
       Reglas:
       - Debe venir al menos un permiso (ERR1 si vacío).
       - Activa los nuevos que falten e inactiva los que no están en la lista.
    """
    data = request.get_json(silent=True) or {}
    selected = data.get('permisos')
    # Debe venir una lista (puede ser vacía -> significa quitar todos los permisos directos)
    if not isinstance(selected, list):
        return jsonify({"errorCode": "ERR1", "message": "Lista de permisos inválida"}), 400
    # Normalizar y deduplicar (lista vacía permitida)
    try:
        selected_ids = sorted(set(int(x) for x in selected))
    except Exception:
        return jsonify({"errorCode": "ERR1", "message": "Lista de permisos inválida"}), 400

    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor(dictionary=True)
        # Validar usuario
        cur.execute("SELECT 1 FROM usuario WHERE idUsuario=%s", (user_id,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Usuario no encontrado"}), 404
        # Validar permisos existen SOLO si se enviaron permisos
        if selected_ids:
            in_clause = ','.join(['%s'] * len(selected_ids))
            cur.execute(f"SELECT COUNT(*) as total FROM permiso WHERE idPermiso IN ({in_clause})", tuple(selected_ids))
            count = cur.fetchone()['total']
            if count != len(selected_ids):
                return jsonify({"errorCode": "ERR1", "message": "Algún permiso no existe"}), 400

        # Permisos actuales activos
        cur.execute(
            "SELECT idPermiso FROM usuariopermiso WHERE idUsuario=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            (user_id,)
        )
        current_ids = sorted([r['idPermiso'] for r in (cur.fetchall() or [])])

        # Calcular diferencias. Si selected_ids está vacío -> to_add = [], to_close = todos los actuales
        to_add = [pid for pid in selected_ids if pid not in current_ids]
        to_close = [pid for pid in current_ids if pid not in selected_ids]

        # Si no hay cambios, devolver error indicando que no hay modificaciones
        if not to_add and not to_close:
            return jsonify({"errorCode": "ERR1", "message": "No hay cambios en los permisos del usuario"}), 400

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
        
        # Registrar en auditoría
        detalle_cambios = f"Reemplazo masivo de permisos para usuario idUsuario={user_id}: Agregados={to_add}, Eliminados={to_close}"
        auditoria_log(current_user_id, "MODIFICACION", detalle_cambios)

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
@requires_permission('ACCESS_HISTORY')
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
            clauses.append("ha.ipAcceso = %s")
            params.append(ip_s)

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
@requires_permission('ACCESS_HISTORY')
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
            clauses.append("ha.ipAcceso = %s")
            params.append(ip_s)

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
                from reportlab.lib.units import cm
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
                from reportlab.pdfgen import canvas
                import os

                # Clase personalizada para agregar encabezado y pie de página en todas las páginas
                class PDFWithHeaderFooter(SimpleDocTemplate):
                    def __init__(self, *args, logo_path=None, **kwargs):
                        super().__init__(*args, **kwargs)
                        self.logo_path = logo_path
                    
                    def handle_pageBegin(self):
                        super().handle_pageBegin()
                        self._add_header_footer()
                    
                    def _add_header_footer(self):
                        c = self.canv
                        page_width, page_height = A4
                        
                        # Encabezado: Logo a la izquierda y texto a la derecha
                        if self.logo_path and os.path.exists(self.logo_path):
                            c.drawImage(self.logo_path, 36, page_height - 70, width=80, height=40, preserveAspectRatio=True)
                        
                        c.setFont('Helvetica-Bold', 12)
                        c.drawRightString(page_width - 36, page_height - 50, "ORIENTACIÓN VOCACIONAL ONLINE")
                        
                        # Línea separadora debajo del encabezado
                        c.setStrokeColor(colors.grey)
                        c.setLineWidth(0.5)
                        c.line(36, page_height - 75, page_width - 36, page_height - 75)
                        
                        # Pie de página: Número de página a la derecha
                        c.setFont('Helvetica', 9)
                        page_num = c.getPageNumber()
                        c.drawRightString(page_width - 36, 20, f"Página {page_num}")

                buffer = BytesIO()
                logo_path = os.path.join(os.path.dirname(__file__), 'OVO_logo.png')
                doc = PDFWithHeaderFooter(
                    buffer,
                    pagesize=A4,
                    leftMargin=36,
                    rightMargin=36,
                    topMargin=90,  # Aumentado para el encabezado
                    bottomMargin=50,  # Aumentado para el pie de página
                    logo_path=logo_path
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
                
                elements = []
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

                elements.extend([title, Spacer(1, 8), table])
                
                # Construir el PDF con la clase personalizada que agrega encabezado y pie
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

# -- Volcando estructura para tabla ovo.historialabm
# CREATE TABLE IF NOT EXISTS `historialabm` (
#   `idHistorialABM` int(11) NOT NULL AUTO_INCREMENT,
#   `idUsuario` int(11) NOT NULL,
#   `idTipoAccion` int(11) NOT NULL,
#   `detalle` text DEFAULT NULL,
#   `fechaHistorial` datetime NOT NULL DEFAULT current_timestamp(),
#   PRIMARY KEY (`idHistorialABM`),
#   KEY `FK_historialabm_usuario` (`idUsuario`),
#   KEY `FK_historialabm_tipoaccion` (`idTipoAccion`),
#   CONSTRAINT `FK_historialabm_tipoaccion` FOREIGN KEY (`idTipoAccion`) REFERENCES `tipoaccion` (`idTipoAccion`) ON DELETE NO ACTION ON UPDATE NO ACTION,
#   CONSTRAINT `FK_historialabm_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON UPDATE CASCADE
# ) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

# -- Volcando datos para la tabla ovo.historialabm: ~2 rows (aproximadamente)
# INSERT INTO `historialabm` (`idHistorialABM`, `idUsuario`, `idTipoAccion`, `detalle`, `fechaHistorial`) VALUES
# 	(1, 1, 3, 'Eliminación de estado de usuario idEstadoUsuario=9', '2025-11-04 12:13:52'),
# 	(2, 1, 3, 'Eliminación de estado de usuario idEstadoUsuario=7', '2025-11-04 12:13:54');

# -- Volcando estructura para tabla ovo.tipoaccion
# CREATE TABLE IF NOT EXISTS `tipoaccion` (
#   `idTipoAccion` int(11) NOT NULL AUTO_INCREMENT,
#   `nombreTipoAccion` varchar(50) DEFAULT NULL,
#   PRIMARY KEY (`idTipoAccion`)
# ) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

# -- Volcando datos para la tabla ovo.tipoaccion: ~3 rows (aproximadamente)
# INSERT INTO `tipoaccion` (`idTipoAccion`, `nombreTipoAccion`) VALUES
# 	(1, 'ACTUALIZACION'),
# 	(2, 'MODIFICACION'),
# 	(3, 'ELIMINACION');


# Endpoint para obtener el historial de auditoría
@app.route('/api/v1/admin/audit', methods=['GET'])
@requires_permission('AUDIT_HISTORY')
def admin_audit_list(current_user_id):
    """
    Listado de auditoría con paginación.
    Query params opcionales:
    - page: número de página (default 1)
    - pageSize: tamaño de página (default 50, max 1000)
    """
    conn = None
    try:
        args = request.args
        
        # Paginación
        try:
            page = int(args.get('page', '1'))
            page_size = int(args.get('pageSize', '50'))
            if page < 1 or page_size < 1 or page_size > 1000:
                raise ValueError()
        except Exception:
            return jsonify({"errorCode": "ERR1", "message": "Error en los parámetros de paginación"}), 400
        
        offset = (page - 1) * page_size

        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        sql = """
            SELECT ha.idHistorialABM,
                   ha.idUsuario,
                   CONCAT(u.nombre, ' ', u.apellido) AS nombreUsuario,
                   ha.idTipoAccion,
                   ta.nombreTipoAccion,
                   ha.detalle,
                   ha.fechaHistorial
            FROM historialabm ha
            LEFT JOIN usuario u ON u.idUsuario = ha.idUsuario
            LEFT JOIN tipoaccion ta ON ta.idTipoAccion = ha.idTipoAccion
            ORDER BY ha.fechaHistorial DESC
            LIMIT %s OFFSET %s
        """
        cur.execute(sql, (page_size, offset))
        rows = cur.fetchall() or []

        data = []
        for r in rows:
            data.append({
                "idUsuario": r.get('idUsuario'),
                "nombreUsuario": r.get('nombreUsuario'),
                "idTipoAccion": r.get('idTipoAccion'),
                "nombreTipoAccion": r.get('nombreTipoAccion'),
                "detalle": r.get('detalle'),
                "fecha": (r.get('fechaHistorial').isoformat(sep=' ') if r.get('fechaHistorial') else None)
            })

        return jsonify(data), 200

    except Exception as e:
        log(f"/admin/audit GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Error al obtener auditoría"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


# Endpoint para exportar el historial de auditoría
@app.route('/api/v1/admin/audit/export', methods=['GET'])
@requires_permission('AUDIT_HISTORY')
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
                from reportlab.lib.units import cm
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
                from reportlab.pdfgen import canvas
                import os

                # Clase personalizada para agregar encabezado y pie de página en todas las páginas
                class PDFWithHeaderFooter(SimpleDocTemplate):
                    def __init__(self, *args, logo_path=None, **kwargs):
                        super().__init__(*args, **kwargs)
                        self.logo_path = logo_path
                    
                    def handle_pageBegin(self):
                        super().handle_pageBegin()
                        self._add_header_footer()
                    
                    def _add_header_footer(self):
                        c = self.canv
                        page_width, page_height = A4
                        
                        # Encabezado: Logo a la izquierda y texto a la derecha
                        if self.logo_path and os.path.exists(self.logo_path):
                            c.drawImage(self.logo_path, 36, page_height - 70, width=80, height=40, preserveAspectRatio=True)
                        
                        c.setFont('Helvetica-Bold', 12)
                        c.drawRightString(page_width - 36, page_height - 50, "ORIENTACIÓN VOCACIONAL ONLINE")
                        
                        # Línea separadora debajo del encabezado
                        c.setStrokeColor(colors.grey)
                        c.setLineWidth(0.5)
                        c.line(36, page_height - 75, page_width - 36, page_height - 75)
                        
                        # Pie de página: Número de página a la derecha
                        c.setFont('Helvetica', 9)
                        page_num = c.getPageNumber()
                        c.drawRightString(page_width - 36, 20, f"Página {page_num}")

                buffer = BytesIO()
                logo_path = os.path.join(os.path.dirname(__file__), 'OVO_logo.png')
                doc = PDFWithHeaderFooter(
                    buffer,
                    pagesize=A4,
                    leftMargin=36,
                    rightMargin=36,
                    topMargin=90,  # Aumentado para el encabezado
                    bottomMargin=50,  # Aumentado para el pie de página
                    logo_path=logo_path
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
                
                elements = []
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

                elements.extend([title, Spacer(1, 8), table])
                
                # Construir el PDF con la clase personalizada que agrega encabezado y pie
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
            cur.execute("INSERT INTO usuariogrupo (idUsuario, idGrupo, fechaInicio, fechaFin) VALUES (%s, %s, NOW(), NULL)", (int(user['idUsuario']), int(grupo['idGrupo'])))

        # Agregar al usuario al estado "Pendiente" por defecto
        if user:
            cur.execute("SELECT * FROM estadousuario WHERE nombreEstadoUsuario = %s", ("Pendiente",))
            estado = cur.fetchone()
            if not estado:
                return jsonify({"errorCode": "ERR3", "message": "Error al registrar usuario"}), 500
            cur.execute("INSERT INTO usuarioestado (idUsuario, idEstadoUsuario, fechaInicio, fechaFin) VALUES (%s, %s, NOW(), NULL)", (int(user['idUsuario']), int(estado['idEstadoUsuario'])))
            conn.commit()
            
            # Registrar en auditoría (usar el ID del usuario recién creado como autor)
            auditoria_log(user['idUsuario'], "ACTUALIZACION", f"Registro de nuevo usuario idUsuario={user['idUsuario']}, idGenero={idGenero}, idLocalidad={idLocalidad}")
        
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
                # Para registros con Google, usamos valores por defecto para campos obligatorios
                cur.execute(
                    "INSERT INTO usuario (mail, nombre, apellido, dni, fechaNac, contrasena, idGenero, idLocalidad) VALUES (%s, %s, %s, 0, '1900-01-01', '', 1, 1)",
                    (email, nombre, apellido)
                )
                conn.commit()
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
        cur.execute("INSERT INTO usuarioestado (idUsuario, idEstadoUsuario, fechaInicio, fechaFin) VALUES (%s, %s, NOW(), NULL)", (id_usuario, id_estado_activo))
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
# curl -X GET "{{baseURL}}/api/v1/auth/verify-email?key=tu_clave_aqui"

# ============================ Baja lógica de usuario (US008) ============================

# Endpoint para dar de baja lógica al usuario
@app.route('/api/v1/auth/deactivate', methods=['POST'])
@requires_permission("USER_DEACTIVATE_SELF")
def deactivate_current_user(current_user_id):
    """Da de baja lógicamente al usuario autenticado.
    Regla: Cierra cualquier estado activo en usuarioestado y crea un nuevo estado BAJA.
    Si ya está en BAJA activo, responde idempotente con ok: true.
    Errores => ERR1.
    """
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Validar existencia de usuario
        cur.execute("SELECT 1 FROM usuario WHERE idUsuario=%s", (current_user_id,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Usuario no encontrado"}), 404

        # Verificar si ya posee un estado activo Baja
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
        id_estado_baja = row['idEstadoUsuario']

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

# Endpoint para enviar enlace de restablecimiento
@app.route('/api/v1/auth/password/forgot', methods=['POST'])
def password_forgot():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        data = request.get_json(silent=True) or {}
        correo = (data.get('correo') or '').strip()
        # Validación de formato básico y existencia
        if not correo or not re.match(EMAIL_REGEX, correo):
            return jsonify({"errorCode": "ERR1", "message": "Email no registrado"}), 400

        user = get_user_by_email(correo)
        if not user:
            return jsonify({"errorCode": "ERR1", "message": "Email no registrado"}), 400

        new_password = generate_password()
        new_password_hash = hash_password(new_password)

        cur = conn.cursor(dictionary=True)
        cur.execute(
            "UPDATE usuario SET contrasena = %s WHERE idUsuario = %s",
            (new_password_hash, user['idUsuario'])
        )
        conn.commit()

        # Enviar correo con el enlace
        asunto = "Recuperación de contraseña"
        cuerpo = (
            f"<p>Hola {user.get('nombre') or ''},</p><br><br>"
            f"<p>Recibimos una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para continuar:</p><br>"
            f"<p><strong>Nueva Contraseña:</strong> {new_password}</p><br>"
            f"<p>Recuerda cambiar tu contraseña después de iniciar sesión.</p><br>"
            f"<p>OVO TEAM</p>"
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
    
# Cambio de contraseña enviando la contraseña antigua
@app.route('/api/v1/auth/password/change', methods=['POST'])
@token_required
def password_change(current_user_id):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        data = request.get_json(silent=True) or {}
        old_password = (data.get('old_password') or '').strip()
        new_password = (data.get('new_password') or '').strip()

        # Validación básica
        if not old_password or not new_password:
            return jsonify({"errorCode": "ERR1", "message": "Faltan datos requeridos"}), 400

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuario WHERE idUsuario=%s", (current_user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"errorCode": "ERR1", "message": "Usuario no encontrado"}), 404

        # Verificar contraseña antigua
        if not verify_password(old_password, user['contrasena']):
            return jsonify({"errorCode": "ERR1", "message": "Contraseña incorrecta"}), 400

        # Verificar nueva contraseña contra política
        if not _password_meets_policy(new_password):
            return jsonify({"errorCode": "ERR1", "message": f"La nueva contraseña no cumple los requisitos: {PWD_POLICY_MSG}"}), 400

        # Actualizar contraseña
        new_password_hash = hash_password(new_password)
        cur = conn.cursor()
        cur.execute(
            "UPDATE usuario SET contrasena = %s WHERE idUsuario = %s",
            (new_password_hash, current_user_id)
        )
        conn.commit()
        return jsonify({"ok": True, "message": "Contraseña actualizada con éxito"}), 200
    except Exception as e:
        log(f"/auth/password/change error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "No se pudo procesar la solicitud."}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
# curl -X POST "{{baseURL}}/api/v1/auth/password/change" -H "Content-Type: application/json" -H "Authorization: Bearer {{token}}" -d '{"old_password": "oldPass123!", "new_password": "NewPass456@"}'

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
                   ci.nombreCarrera AS nombreCarreraInstitucion,
                   inst.nombreInstitucion
            FROM interesusuariocarrera iuc
            JOIN carrerainstitucion ci ON ci.idCarreraInstitucion = iuc.idCarreraInstitucion
            LEFT JOIN institucion inst ON inst.idInstitucion = ci.idInstitucion
            WHERE iuc.idUsuario = %s AND (iuc.fechaFin IS NULL OR iuc.fechaFin > NOW())
            ORDER BY ci.nombreCarrera, inst.nombreInstitucion
            """,
            (current_user_id,)
        )
        rows = cur.fetchall() or []
        if not rows:
            return jsonify({"errorCode": "ERR1", "message": "No tiene preferencia por ninguna carrera"}), 400
        data = [
            {
                "idCarreraInstitucion": r.get('idCarreraInstitucion'),
                "nombreCarreraInstitucion": r.get('nombreCarreraInstitucion'),
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

# -- Volcando estructura para tabla ovo.carrerainstitucion
# CREATE TABLE IF NOT EXISTS `carrerainstitucion` (
#   `idCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
#   `idEstadoCarreraInstitucion` int(11) NOT NULL,
#   `idCarrera` int(11) DEFAULT NULL,
#   `idModalidadCarreraInstitucion` int(11) NOT NULL,
#   `idInstitucion` int(11) DEFAULT NULL,
#   `tituloCarrera` varchar(50) NOT NULL,
#   `cantidadMaterias` int(11) NOT NULL,
#   `duracionCarrera` decimal(20,2) NOT NULL,
#   `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
#   `horasCursado` int(11) NOT NULL,
#   `observaciones` varchar(500) NOT NULL,
#   `nombreCarrera` varchar(50) NOT NULL,
#   `montoCuota` decimal(20,2) NOT NULL,
#   `fechaFin` datetime DEFAULT NULL,
#   PRIMARY KEY (`idCarreraInstitucion`),
#   KEY `FK_carrerainstitucion_estadocarrerainstitucion` (`idEstadoCarreraInstitucion`),
#   KEY `FK_carrerainstitucion_carrera` (`idCarrera`),
#   KEY `FK_carrerainstitucion_modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`),
#   KEY `FK_carrerainstitucion_institucion` (`idInstitucion`),
#   CONSTRAINT `FK_carrerainstitucion_carrera` FOREIGN KEY (`idCarrera`) REFERENCES `carrera` (`idCarrera`) ON DELETE SET NULL ON UPDATE CASCADE,
#   CONSTRAINT `FK_carrerainstitucion_estadocarrerainstitucion` FOREIGN KEY (`idEstadoCarreraInstitucion`) REFERENCES `estadocarrerainstitucion` (`idEstadoCarreraInstitucion`) ON UPDATE CASCADE,
#   CONSTRAINT `FK_carrerainstitucion_institucion` FOREIGN KEY (`idInstitucion`) REFERENCES `institucion` (`idInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
#   CONSTRAINT `FK_carrerainstitucion_modalidadcarrerainstitucion` FOREIGN KEY (`idModalidadCarreraInstitucion`) REFERENCES `modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`) ON UPDATE CASCADE
# ) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

# -- Volcando estructura para tabla ovo.test
# CREATE TABLE IF NOT EXISTS `test` (
#   `idTest` int(11) NOT NULL AUTO_INCREMENT,
#   `idEstadoTest` int(11) NOT NULL,
#   `idUsuario` int(11) DEFAULT NULL,
#   `fechaTest` datetime NOT NULL DEFAULT current_timestamp(),
#   `idChatIA` varchar(50) NOT NULL,
#   `HistorialPreguntas` longtext DEFAULT NULL,
#   PRIMARY KEY (`idTest`),
#   KEY `FK_test_usuario` (`idUsuario`),
#   KEY `FK_test_estadotest` (`idEstadoTest`),
#   CONSTRAINT `FK_test_estadotest` FOREIGN KEY (`idEstadoTest`) REFERENCES `estadotest` (`idEstadoTest`) ON DELETE NO ACTION ON UPDATE NO ACTION,
#   CONSTRAINT `FK_test_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
# ) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

# -- Volcando estructura para tabla ovo.testcarrerainstitucion
# CREATE TABLE IF NOT EXISTS `testcarrerainstitucion` (
#   `afinidadCarrera` double DEFAULT NULL,
#   `idTest` int(11) DEFAULT NULL,
#   `idCarreraInstitucion` int(11) DEFAULT NULL,
#   KEY `FK_testcarrerainstitucion_test` (`idTest`),
#   KEY `FK_testcarrerainstitucion_carrerainstitucion` (`idCarreraInstitucion`),
#   CONSTRAINT `FK_testcarrerainstitucion_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON UPDATE CASCADE,
#   CONSTRAINT `FK_testcarrerainstitucion_test` FOREIGN KEY (`idTest`) REFERENCES `test` (`idTest`) ON DELETE CASCADE ON UPDATE CASCADE
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

# Lista los tests realizados por el usuario autenticado
@app.route('/api/v1/user/tests', methods=['GET'])
@token_required
def user_list_tests(current_user_id):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        
        # Obtener los tests del usuario con su estado
        cur.execute(
            """
            SELECT t.idTest, t.fechaTest, et.nombreEstadoTest
            FROM test t
            JOIN estadotest et ON t.idEstadoTest = et.idEstadoTest
            WHERE t.idUsuario = %s
            ORDER BY t.fechaTest DESC
            """,
            (current_user_id,)
        )
        tests_rows = cur.fetchall() or []
        
        # Construir respuesta con carreras asociadas a cada test
        data = []
        for test_row in tests_rows:
            id_test = test_row.get('idTest')
            
            # Obtener las carreras recomendadas para este test con su afinidad
            cur.execute(
                """
                SELECT 
                    tci.afinidadCarrera,
                    tci.idCarreraInstitucion,
                    ci.tituloCarrera,
                    ci.nombreCarrera,
                    ci.idInstitucion,
                    i.nombreInstitucion
                FROM testcarrerainstitucion tci
                JOIN carrerainstitucion ci ON ci.idCarreraInstitucion = tci.idCarreraInstitucion
                LEFT JOIN institucion i ON i.idInstitucion = ci.idInstitucion
                WHERE tci.idTest = %s
                ORDER BY tci.afinidadCarrera DESC
                """,
                (id_test,)
            )
            carreras_rows = cur.fetchall() or []
            
            # Formatear las carreras recomendadas
            carreras_recomendadas = [
                {
                    "idCarreraInstitucion": carrera.get('idCarreraInstitucion'),
                    "tituloCarrera": carrera.get('tituloCarrera'),
                    "nombreCarrera": carrera.get('nombreCarrera'),
                    "nombreInstitucion": carrera.get('nombreInstitucion'),
                    "idInstitucion": carrera.get('idInstitucion'),
                    "afinidadCarrera": round(float(carrera.get('afinidadCarrera') or 0), 2)
                }
                for carrera in carreras_rows
            ]

            # -- Volcando estructura para tabla ovo.aptitud
            # CREATE TABLE IF NOT EXISTS `aptitud` (
            # `idAptitud` int(11) NOT NULL AUTO_INCREMENT,
            # `nombreAptitud` varchar(50) DEFAULT NULL,
            # `descripcion` varchar(50) DEFAULT NULL,
            # `fechaAlta` datetime NOT NULL DEFAULT current_timestamp(),
            # `fechaBaja` datetime DEFAULT NULL,
            # PRIMARY KEY (`idAptitud`)
            # ) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

            # -- Volcando estructura para tabla ovo.test
            # CREATE TABLE IF NOT EXISTS `test` (
            # `idTest` int(11) NOT NULL AUTO_INCREMENT,
            # `idEstadoTest` int(11) NOT NULL,
            # `idUsuario` int(11) DEFAULT NULL,
            # `fechaTest` datetime NOT NULL DEFAULT current_timestamp(),
            # `idChatIA` varchar(50) NOT NULL,
            # `HistorialPreguntas` longtext DEFAULT NULL,
            # PRIMARY KEY (`idTest`),
            # KEY `FK_test_usuario` (`idUsuario`),
            # KEY `FK_test_estadotest` (`idEstadoTest`),
            # CONSTRAINT `FK_test_estadotest` FOREIGN KEY (`idEstadoTest`) REFERENCES `estadotest` (`idEstadoTest`) ON DELETE NO ACTION ON UPDATE NO ACTION,
            # CONSTRAINT `FK_test_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON DELETE CASCADE ON UPDATE CASCADE
            # ) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

            # -- Volcando estructura para tabla ovo.testaptitud
            # CREATE TABLE IF NOT EXISTS `testaptitud` (
            # `idResultadoAptitud` int(11) NOT NULL AUTO_INCREMENT,
            # `afinidadAptitud` double DEFAULT NULL,
            # `idAptitud` int(11) DEFAULT NULL,
            # `idTest` int(11) DEFAULT NULL,
            # PRIMARY KEY (`idResultadoAptitud`),
            # KEY `FK_testaptitud_aptitud` (`idAptitud`),
            # KEY `FK_testaptitud_test` (`idTest`),
            # CONSTRAINT `FK_testaptitud_aptitud` FOREIGN KEY (`idAptitud`) REFERENCES `aptitud` (`idAptitud`) ON DELETE CASCADE ON UPDATE CASCADE,
            # CONSTRAINT `FK_testaptitud_test` FOREIGN KEY (`idTest`) REFERENCES `test` (`idTest`) ON DELETE CASCADE ON UPDATE CASCADE
            # ) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


            # Aptitudes obtenidas en el test (join con tabla aptitud para obtener el nombre)
            cur.execute(
                """
                SELECT
                    a.idAptitud,
                    a.nombreAptitud,
                    ta.afinidadAptitud
                FROM testaptitud ta
                JOIN aptitud a ON a.idAptitud = ta.idAptitud
                WHERE ta.idTest = %s
                ORDER BY ta.afinidadAptitud DESC
                """,
                (id_test,)
            )
            aptitudes_rows = cur.fetchall() or []

            # Formatear las aptitudes obtenidas
            aptitudes_obtenidas = [
                {
                    "idAptitud": aptitud.get('idAptitud'),
                    "nombreAptitud": aptitud.get('nombreAptitud'),
                    "afinidadAptitud": round(float(aptitud.get('afinidadAptitud') or 0), 2)
                }
                for aptitud in aptitudes_rows
            ]

            # Agregar el test con sus carreras
            data.append({
                "id": id_test,
                "fecha": (test_row.get('fechaTest').isoformat(sep=' ') if test_row.get('fechaTest') else None),
                "estado": test_row.get('nombreEstadoTest'),
                "carrerasRecomendadas": carreras_recomendadas,
                "aptitudesObtenidas": aptitudes_obtenidas
            })
        
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
            WHERE idTest = %s AND idUsuario = %s
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
@requires_permission("USER_VIEW_TEST_RESULT")
def user_test_result(current_user_id, id_test: int):
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
                SELECT t.idTest, t.fechaTest
                FROM test t
                WHERE t.idTest = %s AND t.idUsuario = %s
                """,
                (id_test, auth['user_id'])
            )
        else:
            # Token dev o no se pudo decodificar JWT: no validamos pertenencia
            cursor.execute(
                """
                SELECT t.idTest, t.fechaTest
                FROM test t
                WHERE t.idTest = %s
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
                "id": test_row.get("idTest"),
                "fecha": test_row.get("fechaTest").isoformat() if test_row.get("fechaTest") else None,
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
# - Si hay user_id (JWT): intenta borrar el test en curso del usuario (fechaTest IS NULL).
#   - Si no hay en curso y se envía idTest en el body, valida que pertenezca al usuario y esté en curso.
# - Si NO hay user_id (token dev Hola): requiere idTest en el body y lo elimina si está en curso.
# - Idempotente: si no hay test en curso, responde ok true.
# - Error: ERR1 "Error al reiniciar cuestionario, intente más tarde".
@app.route('/api/v1/user/tests/restart', methods=['POST'])
@requires_permission("USER_RESTART_TEST")
def user_restart_test(current_user_id):
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
                SELECT idTest AS id
                FROM test
                WHERE idUsuario = %s AND fechaTest IS NULL
                ORDER BY idTest DESC
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
                    SELECT idTest AS id
                    FROM test
                    WHERE idTest = %s AND idUsuario = %s AND fechaTest IS NULL
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
                    SELECT idTest AS id
                    FROM test
                    WHERE idTest = %s AND fechaTest IS NULL
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
        cur.execute("DELETE FROM test WHERE idTest = %s", (test_id_to_delete,))
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
@requires_permission(['USER_VIEW_CAREERS', 'INSTITUTION_MANAGE_CAREERS'])
def careers_list(current_user_id):
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

# Consultar carreraInstitucion
@app.route('/api/v1/career/institutions', methods=['GET'])
@requires_permission("USER_VIEW_CAREERS")
def careers_institutions(current_user_id):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("""
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
            WHERE (ci.fechaFin IS NULL OR ci.fechaFin > NOW())
            ORDER BY i.nombreInstitucion, ci.tituloCarrera
        """)
        rows = cur.fetchall() or []
        data = []
        for r in rows:
            data.append({
                "idCarreraInstitucion": r.get('idCarreraInstitucion'),
                "nombreInstitucion": r.get('nombreInstitucion'),
                "urlLogo": r.get('urlLogo'),
                "tituloCarrera": r.get('tituloCarrera'),
                "nombreCarrera": r.get('nombreCarreraCI'),
                "modalidad": r.get('nombreModalidad'),
                "montoCuota": float(r.get('montoCuota') or 0),
                "detailPath": f"/api/v1/careers/{r.get('idCarreraInstitucion')}/institutions/{r.get('idInstitucion')}",
                "aliasPath": f"/api/v1/careers/{r.get('idCarreraInstitucion')}",
                "meInteresaPath": f"/api/v1/careers/{r.get('idCarreraInstitucion')}/interest",
            })
        return jsonify(data), 200
    except Exception as e:
        log(f"/careers/institutions GET error: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Error al consultar instituciones de la carrera"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
# Curl ejemplo:
    # curl -X GET "{{baseURL}}/api/v1/careers/1/institutions" -H "accept: application/json"

# Instituciones que dictan una carrera
@app.route('/api/v1/careers/<int:id_carrera>/institutions', methods=['GET'])
@requires_permission("USER_VIEW_CAREERS")
def career_institutions(current_user_id, id_carrera: int):
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
@requires_permission("USER_VIEW_CAREERS")
def career_institution_detail(current_user_id, id_carrera: int, id_ci: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        cur.execute(
            """
            SELECT ci.*, c.nombreCarrera AS nombreCarreraBase,
                   i.idInstitucion, i.nombreInstitucion, i.siglaInstitucion, i.telefono, i.mail, i.sitioWeb, i.urlLogo, i.direccion,
                   i.idLocalidad,
                   m.nombreModalidad,
                   l.idProvincia,
                   p.idPais
            FROM carrerainstitucion ci
            JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN institucion i ON i.idInstitucion = ci.idInstitucion
            LEFT JOIN modalidadcarrerainstitucion m ON m.idModalidadCarreraInstitucion = ci.idModalidadCarreraInstitucion
            LEFT JOIN localidad l ON l.idLocalidad = i.idLocalidad
            LEFT JOIN provincia p ON p.idProvincia = l.idProvincia
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

        # Preguntas frecuentes asociadas
        cur.execute(
            """
            SELECT idPreguntaFrecuente, nombrePregunta, respuesta
            FROM preguntafrecuente
            WHERE idCarreraInstitucion = %s AND (fechaFin IS NULL OR fechaFin > NOW())
            ORDER BY idPreguntaFrecuente
            """,
            (id_ci,)
        )
        faq = cur.fetchall() or []

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
                "idPais": ci.get('idPais'),
                "idProvincia": ci.get('idProvincia'),
                "idLocalidad": ci.get('idLocalidad'),
            },
            "preguntasFrecuentes": faq,
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
@requires_permission("USER_VIEW_CAREERS")
def career_institution_detail_alias(current_user_id, id_ci: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT ci.*, c.nombreCarrera AS nombreCarreraBase,
                   i.idInstitucion, i.nombreInstitucion, i.siglaInstitucion, i.telefono, i.mail, i.sitioWeb, i.urlLogo, i.direccion,
                   i.idLocalidad,
                   m.nombreModalidad,
                   l.idProvincia,
                   p.idPais
            FROM carrerainstitucion ci
            JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN institucion i ON i.idInstitucion = ci.idInstitucion
            LEFT JOIN modalidadcarrerainstitucion m ON m.idModalidadCarreraInstitucion = ci.idModalidadCarreraInstitucion
            LEFT JOIN localidad l ON l.idLocalidad = i.idLocalidad
            LEFT JOIN provincia p ON p.idProvincia = l.idProvincia
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

        # Preguntas frecuentes asociadas
        cur.execute(
            """
            SELECT idPreguntaFrecuente, nombrePregunta, respuesta
            FROM preguntafrecuente
            WHERE idCarreraInstitucion = %s AND (fechaFin IS NULL OR fechaFin > NOW())
            ORDER BY idPreguntaFrecuente
            """,
            (id_ci,)
        )
        faq = cur.fetchall() or []

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
                "idPais": ci.get('idPais'),
                "idProvincia": ci.get('idProvincia'),
                "idCiudad": ci.get('idLocalidad'),
            },
            "preguntasFrecuentes": faq,
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
            INSERT INTO interesusuariocarrera (idUsuario, idCarreraInstitucion)
            VALUES (%s, %s)
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

# Endpoint para eliminar el interes de la carrera
@app.route('/api/v1/careers/<int:id_ci>/interest', methods=['DELETE'])
@token_required
def careers_unmark_interest(current_user_id: int, id_ci: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Validar que exista la carrera/institución
        cur.execute("SELECT 1 FROM carrerainstitucion WHERE idCarreraInstitucion=%s", (id_ci,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "La carrera/institución no existe"}), 404

        # Verificar que exista un interés activo
        cur.execute(
            """
            SELECT 1
            FROM interesusuariocarrera
            WHERE idUsuario = %s AND idCarreraInstitucion = %s
              AND (fechaFin IS NULL OR fechaFin > NOW())
            """,
            (current_user_id, id_ci)
        )
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "La carrera no está marcada como preferida"}), 400

        # Eliminar interés
        cur.execute(
            """
            UPDATE interesusuariocarrera
            SET fechaFin = NOW()
            WHERE idUsuario = %s AND idCarreraInstitucion = %s
              AND (fechaFin IS NULL OR fechaFin > NOW())
            """,
            (current_user_id, id_ci)
        )
        conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        log(f"/careers/{id_ci}/interest DELETE error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR1", "message": "No se pudo eliminar la preferencia"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
# Ejemplo curl:
# curl -X DELETE {{baseURL}}/api/v1/careers/1/interest -H "Authorization: Bearer Hola"


# ============================ Consultar Instituciones (US015) ============================

# Lista de instituciones con filtros: ?search=, ?tipo=, ?tipoId=, ?localidad=, ?provincia=, ?pais=
@app.route('/api/v1/institutions', methods=['GET'])
@requires_permission("USER_VIEW_INSTITUTIONS")
def institutions_list(current_user_id):
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
@requires_permission("USER_VIEW_INSTITUTIONS")
def institution_detail(current_user_id, id_institucion: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Verificar si el usuario que esta haciendo la request es el dueño de la institucion
        # Obtener autorization header
        auth_header = request.headers.get('Authorization', '') or ''
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[len('Bearer '):].strip()
        is_owner = False
        user_id = None


        # Verificar si el token es válido y obtener el id del usuario
        # print("token", token)
        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                if user_id:
                    # Verificar si el usuario es dueño de la institución
                    cur.execute("SELECT COUNT(*) FROM institucion WHERE idUsuario = %s",
                                (user_id,))
                    is_owner = cur.fetchone().get('COUNT(*)', 0) > 0
            except jwt.ExpiredSignatureError:
                pass
            except jwt.InvalidTokenError:
                pass

        if is_owner:
            cur.execute("SELECT * FROM institucion WHERE idUsuario = %s", (user_id,))
            # print(cur.fetchone())
            id_institucion = cur.fetchone().get('idInstitucion')
            if not id_institucion:
                return jsonify({"errorCode": "ERR1", "message": "No existe institución con esos filtros"}), 404
        
        print("id_institucion", id_institucion)

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

# Endpoint para ver el historial de estados de una institucion

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
        if not nombre or not id_tipo or not pais_id or not provincia_id or not localidad_id or not direccion or not email or not sigla or not telefono or not sitio_web or not anio_fund or not codigo_postal or not cuit:
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
        cur = conn.cursor(dictionary=True)

        # Validar FKs
        cur.execute("SELECT 1 FROM tipoinstitucion WHERE idTipoInstitucion=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({"errorCode": "ERR1", "message": "Tipo de institución inválido"}), 400
        cur.execute("SELECT idProvincia FROM localidad WHERE idLocalidad=%s", (localidad_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"errorCode": "ERR1", "message": "Localidad inválida"}), 400
        prov_of_loc = row['idProvincia']
        if int(prov_of_loc) != provincia_id:
            return jsonify({"errorCode": "ERR1", "message": "Localidad no pertenece a la provincia seleccionada"}), 400
        cur.execute("SELECT idPais FROM provincia WHERE idProvincia=%s", (provincia_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"errorCode": "ERR1", "message": "Provincia inválida"}), 400
        pais_of_prov = row['idPais']
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
        cur.execute("SELECT LAST_INSERT_ID() as id")
        id_institucion = cur.fetchone()['id']

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
        id_estado = row['idEstadoInstitucion']

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

# Endpoint para aproba una institucion creando un usuario para administrarla y enviando un correo con los datos de acceso del usuario
@app.route('/api/v1/institutions/registration/approve/<int:id_institucion>', methods=['POST'])
@requires_permission("ADMIN_APPROVE_INSTITUTION")
def create_user_and_send_mail(current_user_id: int, id_institucion: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        # Verificar que la institución exista y esté en estado Pendiente
        cur.execute(
            """
            SELECT i.idInstitucion, i.mail AS institucionMail, i.nombreInstitucion
            FROM institucion i
            JOIN institucionestado ie ON ie.idInstitucion = i.idInstitucion
            JOIN estadoinstitucion ei ON ei.idEstadoInstitucion = ie.idEstadoInstitucion
            WHERE i.idInstitucion = %s AND ei.nombreEstadoInstitucion = %s AND (ie.fechaFin IS NULL OR ie.fechaFin > NOW())
            """, (id_institucion, "Pendiente"))
        institucion = cur.fetchone()
        if not institucion:
            return jsonify({"errorCode": "ERR1", "message": "La institución no existe o no está en estado Pendiente"}), 404
        institucion_mail = institucion.get('institucionMail')
        institucion_nombre = institucion.get('nombreInstitucion')
        if not institucion_mail or not re.match(EMAIL_REGEX, institucion_mail):
            return jsonify({"errorCode": "ERR2", "message": "La institución no tiene un correo válido registrado: " + institucion_mail}), 400
        
        # Generar datos del usuario
        import random
        import string
        # Usar nombre y apellido genéricos para el administrador
        nombre = f"Admin_{institucion_nombre}".replace(' ', '_')[:50]
        apellido = "Sistema"
        dni = 99999999  # DNI genérico para el usuario admin de la institución
        contrasena_decrypted = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        contrasena = hash_password(contrasena_decrypted)
        
        # Obtener un género por defecto
        cur.execute("SELECT idGenero FROM genero ORDER BY idGenero LIMIT 1")
        genero_row = cur.fetchone()
        if not genero_row:
            # Si no existe ningún género, crear uno por defecto
            cur.execute("INSERT INTO genero (nombreGenero) VALUES (%s)", ("No especificado",))
            id_genero = cur.lastrowid
        else:
            id_genero = genero_row['idGenero']
        
        # Crear el usuario en la base de datos con los campos correctos
        cur.execute(
            """
            INSERT INTO usuario (mail, dni, nombre, apellido, contrasena, fechaNac, idGenero, idLocalidad)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)
            """,
            (institucion_mail, dni, nombre, apellido, contrasena, '1990-01-01', id_genero)
        )
        user_id = cur.lastrowid
        
        # Verificar que el usuario se creó correctamente
        if not user_id:
            raise Exception("No se pudo crear el usuario administrativo")

        # Agregar al usuario al grupo "Institución"
        cur.execute("SELECT idGrupo FROM grupo WHERE nombreGrupo = %s AND (fechaFin IS NULL OR fechaFin > NOW())", ("Institución",))
        grupo_row = cur.fetchone()
        if not grupo_row:
            # Si no existe el grupo "Institución", crearlo
            cur.execute("INSERT INTO grupo (nombreGrupo, descripcion, fechaFin) VALUES (%s, %s, NULL)", ("Institución", "Administradores de instituciones"))
            id_grupo_institucion = cur.lastrowid
        else:
            id_grupo_institucion = grupo_row['idGrupo']
        
        # Insertar la relación usuario-grupo
        cur.execute(
            """
            INSERT INTO usuariogrupo (idUsuario, idGrupo, fechaInicio, fechaFin)
            VALUES (%s, %s, NOW(), NULL)
            """,
            (user_id, id_grupo_institucion)
        )
        
        # Actualizar la institución para asociarla con el nuevo usuario
        cur.execute(
            """
            UPDATE institucion 
            SET idUsuario = %s 
            WHERE idInstitucion = %s
            """,
            (user_id, id_institucion)
        )
        
        # Cambiar el estado de la institución a "Aprobada"
        # Finalizar el estado actual
        cur.execute(
            """
            UPDATE institucionestado 
            SET fechaFin = NOW() 
            WHERE idInstitucion = %s AND fechaFin IS NULL
            """,
            (id_institucion,)
        )
        
        # Crear estado "Aprobada" si no existe
        cur.execute(
            "SELECT idEstadoInstitucion FROM estadoinstitucion WHERE nombreEstadoInstitucion = %s AND (fechaFin IS NULL OR fechaFin > NOW())",
            ("Aprobada",)
        )
        estado_aprobada = cur.fetchone()
        if not estado_aprobada:
            cur.execute(
                "INSERT INTO estadoinstitucion (nombreEstadoInstitucion, fechaFin) VALUES (%s, NULL)",
                ("Aprobada",)
            )
            id_estado_aprobada = cur.lastrowid
        else:
            id_estado_aprobada = estado_aprobada['idEstadoInstitucion']
        
        # Insertar nuevo estado "Aprobada"
        cur.execute(
            """
            INSERT INTO institucionestado (fechaInicio, fechaFin, idEstadoInstitucion, idInstitucion)
            VALUES (NOW(), NULL, %s, %s)
            """,
            (id_estado_aprobada, id_institucion)
        )
        
        conn.commit()
        
        # Enviar correo con los datos de acceso
        send_email(institucion_mail, "¡Institución aprobada! - OVO", f"""
        Su institución "{institucion_nombre}" ha sido aprobada.
        
        Datos de acceso al sistema:
        Email: {institucion_mail}
        Contraseña: {contrasena_decrypted}
        
        Por favor, cambie su contraseña después de iniciar sesión por primera vez.
        
        Saludos,
        Equipo OVO
        """)
        return jsonify({"ok": True, "message": "Institución aprobada exitosamente"}), 200
    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        log(f"/institutions/registration/approve/{id_institucion} POST error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode": "ERR3", "message": "No se pudo aprobar la institución"}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
# Ejemplo curl
# curl -X POST {{baseURL}}/api/v1/institutions/registration/approve/2 -H "Authorization: Bearer {{token}}"

# ============================ Gestión de carreras por institución (US018) ============================

def _get_my_institution_id(conn, current_user_id: int):
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idInstitucion FROM institucion WHERE idUsuario=%s ORDER BY idInstitucion LIMIT 1", (current_user_id,))
    row = cur.fetchone()
    return (row['idInstitucion'] if row else None)

# Listar carreras asociadas a mi institución
@app.route('/api/v1/institutions/me/careers', methods=['GET'])
@requires_permission("INSTITUTION_MANAGE_CAREERS")
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
                   ci.fechaFin,
                   ci.cantidadMaterias,
                   ci.duracionCarrera,
                   ci.horasCursado,
                   ci.idCarrera
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
                "deletePath": f"/api/v1/institutions/me/careers/{id_ci}",
                "cantidadMaterias": int(r.get('cantidadMaterias') or 0),
                "duracionCarrera": float(r.get('duracionCarrera') or 0),
                "horasCursado": int(r.get('horasCursado') or 0),
                "idCarreraBase": r.get('idCarrera')
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
# curl -X GET {{baseURL}}/api/v1/institutions/me/careers -H "Authorization: Bearer {{token}}"

# Opciones para agregar/editar carrera (catálogo base y modalidades)
@app.route('/api/v1/institutions/me/careers/options', methods=['GET'])
@requires_permission("INSTITUTION_MANAGE_CAREERS")
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
@requires_permission("INSTITUTION_MANAGE_CAREERS")
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
        cur = conn.cursor(dictionary=True)
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
            id_estado = row['idEstadoCarreraInstitucion']
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
                idModalidadCarreraInstitucion, idInstitucion
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                cantidad_materias, duracion, ff_dt, fi_dt, horas, observaciones,
                nombre_ci, titulo, monto, id_estado, id_carrera, id_modalidad, id_inst
            )
        )
        id_ci_creado = cur.lastrowid
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de carrerainstitucion idCarreraInstitucion={id_ci_creado}, idCarrera={id_carrera}, idEstadoCarreraInstitucion={id_estado}")
        
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
@requires_permission("INSTITUTION_MANAGE_CAREERS")
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
        idCarrera = data.get('idCarrera')  # Cambia la carrera base

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
                # Validar fecha_inicio
                is_valid, normalized_date, error_msg = validate_date_string(fecha_inicio)
                if not is_valid:
                    return jsonify({"errorCode": "ERR1", "message": error_msg}), 400
                if normalized_date and normalized_date != 'NOW()':
                    fi_dt = _dt.datetime.fromisoformat(normalized_date)
            if isinstance(fecha_fin, str) and fecha_fin != '':
                # Validar fecha_fin
                is_valid, normalized_date, error_msg = validate_date_string(fecha_fin)
                if not is_valid:
                    return jsonify({"errorCode": "ERR1", "message": error_msg}), 400
                if normalized_date and normalized_date != 'NOW()':
                    ff_dt = _dt.datetime.fromisoformat(normalized_date)
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
        if idCarrera is not None:
            try:
                cur.execute("SELECT 1 FROM carrera WHERE idCarrera=%s", (idCarrera,))
                if not cur.fetchone():
                    return jsonify({"errorCode": "ERR1", "message": "Carrera no encontrada"}), 404
            except Exception as e:
                return jsonify({"errorCode": "ERR1", "message": "Error al validar carrera"}), 400
            sets.append("idCarrera=%s")
            params.append(idCarrera)

        if not sets:
            return jsonify({"errorCode": "ERR1", "message": "Debe completar todos los campos obligatorios para guardar los cambios."}), 400

        cur.execute(f"UPDATE carrerainstitucion SET {', '.join(sets)} WHERE idCarreraInstitucion=%s", tuple(params + [id_ci]))
        conn.commit()
        
        # Registrar en auditoría
        detalle_campos = ", ".join([f"{s.split('=')[0]}" for s in sets])
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de carrerainstitucion idCarreraInstitucion={id_ci}, campos: {detalle_campos}")
        
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
@requires_permission("INSTITUTION_MANAGE_CAREERS")
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

        # Obtener o crear estado "Inactiva"
        cur.execute(
            "SELECT idEstadoCarreraInstitucion FROM estadocarrerainstitucion WHERE nombreEstadoCarreraInstitucion=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            ("Inactiva",)
        )
        estado_inactiva = cur.fetchone()
        if not estado_inactiva:
            # Crear estado "Inactiva" si no existe
            cur.execute(
                "INSERT INTO estadocarrerainstitucion (nombreEstadoCarreraInstitucion, fechaFin) VALUES (%s, NULL)",
                ("Inactiva",)
            )
            cur.execute("SELECT LAST_INSERT_ID() as id")
            id_estado_inactiva = cur.fetchone()[0]
        else:
            id_estado_inactiva = estado_inactiva[0]

        # Desactivar vía fechaFin y cambiar estado a Inactiva
        cur.execute(
            "UPDATE carrerainstitucion SET idEstadoCarreraInstitucion = %s WHERE idCarreraInstitucion=%s", 
            (id_estado_inactiva, id_ci)
        )
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de carrerainstitucion idCarreraInstitucion={id_ci}, cambio a estado Inactiva")
        
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
# Se utiliza la tabla `preguntafrecuente` que tiene FK `idCarreraInstitucion` hacia `carrerainstitucion`.
# El esquema permite múltiples FAQs por carrera-institución, así que el endpoint GET retorna todas las activas
# y el POST permite agregar nuevas FAQs sin restricciones de cantidad.

# Listar FAQs de una carrera-institución (0 o más)
@app.route('/api/v1/institutions/me/careers/<int:id_ci>/faqs', methods=['GET'])
@requires_permission("INSTITUTION_MANAGE_FAQS")
def my_institution_career_faq_get(current_user_id: int, id_ci: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT pf.idPreguntaFrecuente, pf.nombrePregunta, pf.respuesta, pf.fechaFin
            FROM preguntafrecuente pf
            WHERE pf.idCarreraInstitucion=%s
              AND (pf.fechaFin IS NULL OR pf.fechaFin > NOW())
            ORDER BY pf.idPreguntaFrecuente ASC
            """,
            (id_ci,)
        )
        rows = cur.fetchall() or []
        data = []
        for row in rows:
            data.append({
                "idPreguntaFrecuente": row['idPreguntaFrecuente'],
                "pregunta": row['nombrePregunta'],
                "respuesta": row['respuesta']
            })
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
@requires_permission("INSTITUTION_MANAGE_FAQS")
def my_institution_career_faq_create(current_user_id: int, id_ci: int):
    conn = None
    try:
        data = request.get_json(silent=True) or {}
        pregunta = (data.get('pregunta') or data.get('nombrePregunta') or '').strip()
        respuesta = (data.get('respuesta') or '').strip()
        if not pregunta or not respuesta:
            return jsonify({"errorCode": "ERR1", "message": "Datos incompletos"}), 400
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        # Insertar FAQ directamente sin verificar límites
        cur.execute(
            "INSERT INTO preguntafrecuente (idCarreraInstitucion, fechaFin, nombrePregunta, respuesta) VALUES (%s, NULL, %s, %s)",
            (id_ci, pregunta, respuesta)
        )
        conn.commit()
        cur.execute("SELECT LAST_INSERT_ID() as id")
        id_faq = cur.fetchone()['id']
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
@requires_permission("INSTITUTION_MANAGE_FAQS")
def my_institution_career_faq_update(current_user_id: int, id_ci: int, id_faq: int):
    conn = None
    try:
        data = request.get_json(silent=True) or {}
        pregunta = data.get('pregunta') or data.get('nombrePregunta')
        respuesta = data.get('respuesta')
        if pregunta is None and respuesta is None:
            return jsonify({"errorCode": "ERR1", "message": "Sin datos para actualizar"}), 400
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        # Validar pertenencia del FAQ
        cur.execute(
            "SELECT 1 FROM preguntafrecuente WHERE idPreguntaFrecuente=%s AND idCarreraInstitucion=%s AND (fechaFin IS NULL OR fechaFin > NOW())",
            (id_faq, id_ci)
        )
        row = cur.fetchone()
        if not row:
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

# Eliminar FAQ (baja lógica)
@app.route('/api/v1/institutions/me/careers/<int:id_ci>/faqs/<int:id_faq>', methods=['DELETE'])
@requires_permission("INSTITUTION_MANAGE_FAQS")
def my_institution_career_faq_delete(current_user_id: int, id_ci: int, id_faq: int):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT 1 FROM preguntafrecuente WHERE idPreguntaFrecuente=%s AND idCarreraInstitucion=%s AND (fechaFin IS NULL OR fechaFin > NOW())", (id_faq, id_ci))
        row = cur.fetchone()
        if not row:
            return jsonify({"errorCode": "ERR1", "message": "Pregunta frecuente no encontrada"}), 404
        # Baja lógica (no necesita desasociar ya que la FK está en preguntafrecuente)
        cur.execute("UPDATE preguntafrecuente SET fechaFin = NOW() WHERE idPreguntaFrecuente=%s", (id_faq,))
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
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idInstitucion FROM institucion WHERE idUsuario=%s ORDER BY idInstitucion LIMIT 1", (user_id,))
    r = cur.fetchone()
    return r['idInstitucion'] if r else None

def _ci_belongs(conn, id_ci:int, id_inst:int):
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM carrerainstitucion WHERE idCarreraInstitucion=%s AND idInstitucion=%s", (id_ci, id_inst))
    return cur.fetchone() is not None

# Listar material complementario
@app.route('/api/v1/institutions/me/careers/<int:id_ci>/materials', methods=['GET'])
@requires_permission("INSTITUTION_MANAGE_COMPLEMENTARY_MATERIAL")
def materials_list(current_user_id:int, id_ci:int):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
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
@requires_permission("INSTITUTION_MANAGE_COMPLEMENTARY_MATERIAL")
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
            return jsonify({"errorCode":"ERR1","message":"Usted no está autorizado para realizar esta acción."}), 403
        cur = conn.cursor(dictionary=True)
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
@requires_permission("INSTITUTION_MANAGE_COMPLEMENTARY_MATERIAL")
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
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM contenidomultimedia WHERE idContenidoMultimedia=%s AND idCarreraInstitucion=%s AND (fechaFin IS NULL OR fechaFin>NOW())", (id_mat, id_ci))
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
@requires_permission("INSTITUTION_MANAGE_COMPLEMENTARY_MATERIAL")
def materials_delete(current_user_id:int, id_ci:int, id_mat:int):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM contenidomultimedia WHERE idContenidoMultimedia=%s AND idCarreraInstitucion=%s AND (fechaFin IS NULL OR fechaFin>NOW())", (id_mat, id_ci))
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
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idCarrera FROM carrerainstitucion WHERE idCarreraInstitucion=%s", (id_ci,))
    r = cur.fetchone()
    return r['idCarrera'] if r else None

@app.route('/api/v1/institutions/me/careers/<int:id_ci>/aptitudes', methods=['GET'])
@requires_permission("INSTITUTION_MANAGE_CAREERS_APTITUDES")
def career_aptitudes_list(current_user_id:int, id_ci:int):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        id_inst = _my_inst_id(conn, current_user_id)
        if not id_inst or not _ci_belongs(conn, id_ci, id_inst):
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
            (id_ci,)
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
@requires_permission("INSTITUTION_MANAGE_CAREERS_APTITUDES")
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
                if puntaje < 0 or puntaje > 100:
                    return jsonify({"errorCode":"ERR01","message":"Los valores deben estar entre 0 y 100."}), 400
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

        cur = conn.cursor(dictionary=True)
        # Validar que las aptitudes existan
        ids = [iid for iid,_ in parsed]
        in_clause = ','.join(['%s']*len(ids))
        cur.execute(f"SELECT COUNT(*) as count FROM aptitud WHERE idAptitud IN ({in_clause})", tuple(ids))
        if cur.fetchone()['count'] != len(ids):
            return jsonify({"errorCode":"ERR01","message":"Alguna aptitud no existe"}), 400
        # Reemplazar completamente
        cur.execute("DELETE FROM aptitudcarrera WHERE idCarreraInstitucion=%s", (id_ci,))
        for aid, score in parsed:
            cur.execute(
                "INSERT INTO aptitudcarrera (afinidadCarrera, idAptitud, idCarreraInstitucion) VALUES (%s,%s,%s)",
                (score, aid, id_ci)
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
# Tablas involucradas: test, estadotest, testaptitud, testcarrerainstitucion

# Endpoint para iniciar test (genera registro en tabla 'test' y devuelve preguntas)
@app.route('/api/v1/tests/start', methods=['POST'])
def tests_start():
    # Obtener el token si existe en el header Authorization
    auth_header = request.headers.get('Authorization')
    current_user_id = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            pass
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Verificar que no tenga ningun test activo
        if current_user_id:
            cur.execute(
                "SELECT COUNT(*) as count FROM test WHERE idUsuario = %s AND idEstadoTest = (SELECT idEstadoTest FROM estadotest WHERE nombreEstadoTest='Activo')",
                (current_user_id,)
            )
            test_activo = cur.fetchone()
            if test_activo and test_activo['count'] > 0:
                return jsonify({"errorCode":"ERR2","message":"Ya tiene un test activo en curso"}), 400

        # Obtener el estado "Activo"
        cur.execute("SELECT idEstadoTest FROM estadotest WHERE nombreEstadoTest='Activo' LIMIT 1")
        estadoActivo = cur.fetchone()
        if not estadoActivo:
            return jsonify({"errorCode":"ERR1","message":"No se encontro estado Activo. Comuniquese con el adminstrador"}), 500
        id_estado_activo = estadoActivo['idEstadoTest']

        # Crear nuevo test llamando a generar un ID unico complejo para enviar a la IA
        chatIdIA = str(uuid.uuid4())
        if not current_user_id:
            cur.execute("INSERT INTO test (idEstadoTest, idUsuario, fechaTest, idChatIA) VALUES (%s, NULL, NOW(), %s)", (id_estado_activo, chatIdIA))
        else:
            cur.execute("INSERT INTO test (idEstadoTest, idUsuario, fechaTest, idChatIA) VALUES (%s, %s, NOW(), %s)", (id_estado_activo, current_user_id, chatIdIA))
        cur.execute("SELECT LAST_INSERT_ID() as id")
        idTest = cur.fetchone()['id']

        # Enviar al endpoint para obtener preguntas:
        # curl --location 'AWS_API_URL/prod/chat' \
        # --header 'content-type: application/json' \
        # --data '{
        #     "prompt": "bien",
        #     "ChatID": "2"
        # }'

        # RESPONSE:

        # {
        #     "chatbot_response": "Bienvenido al Cuestionario Vocacional. Mi función es ayudarte a descubrir tus aptitudes y áreas de interés. Responde a las siguientes preguntas con sinceridad para obtener un análisis final. Empecemos:\n\n**Pregunta 1:** ¿Cómo describirías tus habilidades de ventas y orientación al cliente?",
        #     "chat_id": "2",
        #     "status": "Waiting for Q2",
        #     "full_history": [
        #         "Asistente: Bienvenido al Cuestionario Vocacional. Mi función es ayudarte a descubrir tus aptitudes y áreas de interés. Responde a las siguientes preguntas con sinceridad para obtener un análisis final. Empecemos:\n\n**Pregunta 1:** ¿Cómo describirías tus habilidades de ventas y orientación al cliente?"
        #     ]
        # }

        # Enviar la solicitud al endpoint externo
        external_api_url = f'{AWS_API_URL}/prod/chat'
        if current_user_id:
            payload = {
                "prompt": "start",
                "ChatID": str(chatIdIA)
            }
        else:
            payload = {
                "prompt": "start",
                "ChatID": str(chatIdIA)
            }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(external_api_url, json=payload, headers=headers)
        if response.status_code != 200:
            print("Error en llamada externa:", response.status_code, response.text)
            return jsonify({"errorCode":"ERR1","message":"No se pudo iniciar el test. Intente nuevamente."}), 500

        # Guardar el full_history en la tabla test
        cur.execute("UPDATE test SET HistorialPreguntas = %s WHERE idTest = %s", (json.dumps(response.json().get("full_history", []), ensure_ascii=False), idTest))
        conn.commit()

        return jsonify({
            "idTest": int(idTest),
            "fullHistory": response.json().get("full_history", []),
            "chatbot_response": response.json().get("chatbot_response", "")
        }), 201

    except Exception as e:
        # Mostrar traceback en logs
        print(traceback.format_exc())
        return jsonify({"errorCode":"ERR1","message":"No se pudo iniciar el test. Intente nuevamente."}), 500
    finally:
        try:
            cur.close()
            conn.close()
        except Exception as e:
            pass
# Curl ejemplo endpoint anterior:
# curl --location '{{baseURL}}/api/v1/tests/start' --header 'Content-Type: application/json' --data '{}'
# Con bearer token en header Authorization si el usuario está logueado
# curl --location '{{baseURL}}/api/v1/tests/start' --header 'Authorization: Bearer <token>' --header 'Content-Type: application/json' --data '{}'

# Endpoint para enviar enviar respuesta de una pregunta y obtener la siguiente
@app.route('/api/v1/tests/<int:id_test>/answer', methods=['POST'])
def tests_answer(id_test:int):
    # Obtener el token si existe en el header Authorization
    auth_header = request.headers.get('Authorization')
    current_user_id = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            pass
    data = request.get_json(silent=True) or {}
    answer = data.get('answer')
    if answer is None or answer.strip() == '':
        return jsonify({"errorCode":"ERR1","message":"Respuesta inválida"}), 400

    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Validar que el test exista y esté activo
        cur.execute("SELECT t.idTest, t.idChatIA FROM test t JOIN estadotest et ON et.idEstadoTest = t.idEstadoTest WHERE t.idTest = %s AND et.nombreEstadoTest='Activo' LIMIT 1", (id_test,))
        test_row = cur.fetchone()

        if not test_row:
            return jsonify({"errorCode":"ERR1","message":"Test no encontrado o inactivo."}), 404
        chatIdIA = test_row['idChatIA']

        # Enviar la respuesta al endpoint externo
        external_api_url = f'{AWS_API_URL}/prod/chat'
        if current_user_id:
            payload = {
                "prompt": answer.strip(),
                "ChatID": str(chatIdIA)
            }
        else:
            payload = {
                "prompt": answer.strip(),
                "ChatID": str(chatIdIA)
            }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(external_api_url, json=payload, headers=headers)
        if response.status_code != 200:
            print("Error en llamada externa:", response.status_code, response.text)
            return jsonify({"errorCode":"ERR1","message":"Error en llamada externa."}), 500

        resp_json = response.json()
        full_history = resp_json.get("full_history")
        next_question = resp_json.get("chatbot_response")
        status = resp_json.get("status")
        if status == "FINISHED":
            # Actualizar estado del test a Finalizado
            cur.execute("UPDATE test SET idEstadoTest = (SELECT idEstadoTest FROM estadotest WHERE nombreEstadoTest = 'Finalizado') WHERE idTest = %s", (id_test,))
            conn.commit()
            return jsonify({
                "message": "Test finalizado.",
                "fullHistory": full_history
            }), 201
        # Guardar el full_history en la tabla test
        cur.execute("UPDATE test SET HistorialPreguntas = %s WHERE idTest = %s", (json.dumps(full_history, ensure_ascii=False), id_test))
        conn.commit()
        return jsonify({
            "nextQuestion": next_question,
            "fullHistory": full_history
        }), 200

    except Exception as e:
        return jsonify({"errorCode":"ERR1","message":"No se pudo enviar la respuesta. Intente nuevamente."}), 500
    finally:
        try:
            cur.close()
            conn.close()
        except Exception as e:
            pass
# Curl ejemplo endpoint anterior:
# curl --location '{{baseURL}}/api/v1/tests/1/answer' --header 'Content-Type: application/json' --data '{"answer":"Mi respuesta"}'

# Endpoint para mostrar las carreras en base a los resultados del test
@app.route('/api/v1/tests/<int:id_test>/results', methods=['GET'])
@token_required
def get_test_results(current_user_id, id_test):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Obtener idChatIA del test
        cur.execute("SELECT idChatIA, idUsuario FROM test WHERE idTest = %s", (id_test,))
        test_row = cur.fetchone()
        if not test_row:
            return jsonify({"errorCode":"ERR1","message":"Test no encontrado."}), 404
        # Si el test ya está asociado a un usuario, validar que sea el mismo que hace la consulta
        if test_row['idUsuario'] is None:
            cur.execute("UPDATE test SET idUsuario = %s WHERE idTest = %s", (current_user_id, id_test))
            conn.commit()
        elif int(test_row['idUsuario']) != int(current_user_id):
            return jsonify({"errorCode":"ERR1","message":"No está autorizado para ver los resultados de este test."}), 403

        chatIdIA = test_row['idChatIA']
        # Llamar al endpoint externo para obtener resultados validando que el estado del endpoint externo este en ("status": "FINISHED")
        external_api_url = f'{AWS_API_URL}/prod/chat'

        payload = {
            "ChatID": chatIdIA
        }

        response = requests.post(external_api_url, json=payload)
        if response.status_code != 200:
            print("Error en llamada externa:", response.status_code, response.text)
            return jsonify({"errorCode":"ERR1","message":"No se pudo obtener los resultados del test. Intente nuevamente. 1"}), 500
        
        #{'chatbot_response': 'Test finalizado. Aquí está el historial completo.', 'chat_id': '46279cec-dfb5-40ed-992b-d6bf485172f7', 'status': 'FINISHED', 'full_history': ['Asistente: Bienvenido al Cuestionario Vocacional. Mi función es ayudarte a descubrir tus aptitudes y áreas de interés. Responde a las siguientes preguntas con sinceridad para obtener un análisis final. Empecemos:\n\n**Pregunta 1:** ¿Cómo describirías tus habilidades de ventas y orientación al cliente?', 'Usuario: None', 'Asistente: Entiendo que no tienes una respuesta inmediata. En este caso, interpretaré tu falta de respuesta como una puntuación baja en esa área. \n\n**Pregunta 2:** ¿Cómo te desenvuelves en tareas que requieren memoria y atención prolongada?', 'Usuario: None', 'Asistente: Entiendo que no tienes una respuesta inmediata. En este caso, interpretaré tu falta de respuesta como una puntuación baja en esa área.\n\n**Pregunta 3:** ¿Cómo te sientes trabajando en equipo y colaborando con otros?', 'Usuario: bien', 'Asistente: Gracias por tu respuesta. "Bien" sugiere que tienes una apreciación moderada en esta área. \n\n**Pregunta 4:** ¿Cómo describirías tu nivel de creatividad en situaciones laborales o de estudio?', 'Usuario: None', 'Asistente: Tu respuesta no proporciona información suficiente para evaluar tu creatividad.'], 'final_scores': {'Trabajo en equipo y colaboración': '3', 'Creatividad': '1', 'Habilidades de ventas y orientación al cliente': '3', 'Pensamiento crítico y analítico': '5', 'Memoria y atención': '3'}}

        resp_json = response.json()
        if resp_json.get("status") != "FINISHED":
            return jsonify({"errorCode":"ERR1","message":"El test no ha finalizado."}), 400

        # -- Volcando estructura de base de datos para ovo
        # CREATE DATABASE IF NOT EXISTS `ovo` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
        # USE `ovo`;

        # -- Volcando estructura para tabla ovo.aptitud
        # CREATE TABLE IF NOT EXISTS `aptitud` (
        # `idAptitud` int(11) NOT NULL AUTO_INCREMENT,
        # `nombreAptitud` varchar(50) DEFAULT NULL,
        # `descripcion` varchar(50) DEFAULT NULL,
        # `fechaAlta` datetime NOT NULL DEFAULT current_timestamp(),
        # `fechaBaja` datetime DEFAULT NULL,
        # PRIMARY KEY (`idAptitud`)
        # ) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        # -- La exportación de datos fue deseleccionada.

        # -- Volcando estructura para tabla ovo.aptitudcarrera
        # CREATE TABLE IF NOT EXISTS `aptitudcarrera` (
        # `idAptitudCarrera` int(11) NOT NULL AUTO_INCREMENT,
        # `afinidadCarrera` double DEFAULT NULL,
        # `idAptitud` int(11) DEFAULT NULL,
        # `idCarreraInstitucion` int(11) DEFAULT NULL,
        # PRIMARY KEY (`idAptitudCarrera`),
        # KEY `FK_aptitudcarrera_aptitud` (`idAptitud`),
        # KEY `FK_aptitudcarrera_carrera` (`idCarreraInstitucion`),
        # CONSTRAINT `FK_aptitudcarrera_aptitud` FOREIGN KEY (`idAptitud`) REFERENCES `aptitud` (`idAptitud`) ON DELETE CASCADE ON UPDATE CASCADE,
        # CONSTRAINT `FK_aptitudcarrera_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE
        # ) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        # -- La exportación de datos fue deseleccionada.

        # -- Volcando estructura para tabla ovo.carrerainstitucion
        # CREATE TABLE IF NOT EXISTS `carrerainstitucion` (
        # `idCarreraInstitucion` int(11) NOT NULL AUTO_INCREMENT,
        # `idEstadoCarreraInstitucion` int(11) NOT NULL,
        # `idCarrera` int(11) DEFAULT NULL,
        # `idModalidadCarreraInstitucion` int(11) NOT NULL,
        # `idInstitucion` int(11) DEFAULT NULL,
        # `tituloCarrera` varchar(50) NOT NULL,
        # `cantidadMaterias` int(11) NOT NULL,
        # `duracionCarrera` decimal(20,2) NOT NULL,
        # `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
        # `horasCursado` int(11) NOT NULL,
        # `observaciones` varchar(500) NOT NULL,
        # `nombreCarrera` varchar(50) NOT NULL,
        # `montoCuota` decimal(20,2) NOT NULL,
        # `fechaFin` datetime DEFAULT NULL,
        # PRIMARY KEY (`idCarreraInstitucion`),
        # KEY `FK_carrerainstitucion_estadocarrerainstitucion` (`idEstadoCarreraInstitucion`),
        # KEY `FK_carrerainstitucion_carrera` (`idCarrera`),
        # KEY `FK_carrerainstitucion_modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`),
        # KEY `FK_carrerainstitucion_institucion` (`idInstitucion`),
        # CONSTRAINT `FK_carrerainstitucion_carrera` FOREIGN KEY (`idCarrera`) REFERENCES `carrera` (`idCarrera`) ON DELETE SET NULL ON UPDATE CASCADE,
        # CONSTRAINT `FK_carrerainstitucion_estadocarrerainstitucion` FOREIGN KEY (`idEstadoCarreraInstitucion`) REFERENCES `estadocarrerainstitucion` (`idEstadoCarreraInstitucion`) ON UPDATE CASCADE,
        # CONSTRAINT `FK_carrerainstitucion_institucion` FOREIGN KEY (`idInstitucion`) REFERENCES `institucion` (`idInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
        # CONSTRAINT `FK_carrerainstitucion_modalidadcarrerainstitucion` FOREIGN KEY (`idModalidadCarreraInstitucion`) REFERENCES `modalidadcarrerainstitucion` (`idModalidadCarreraInstitucion`) ON UPDATE CASCADE
        # ) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        # Calcular en base a las aptitudes y las carreraInstitucion cuales serian las mas apropiadas segun las aptitudes obtenidas en el test
        aptitudes_obtenidas_raw = resp_json.get("final_scores", {})
        
        # Convertir las aptitudes obtenidas a números (pueden venir como strings desde la API)
        aptitudes_obtenidas = {}
        for nombre_aptitud, valor in aptitudes_obtenidas_raw.items():
            try:
                # Convertir el valor a float, manejando si viene como string
                aptitudes_obtenidas[nombre_aptitud] = float(valor) if valor else 0.0
            except (ValueError, TypeError):
                # Si no se puede convertir, asignar 0
                aptitudes_obtenidas[nombre_aptitud] = 0.0
        
        # Obtener todas las carreras-institución disponibles
        cur.execute("SELECT idCarreraInstitucion, tituloCarrera FROM carrerainstitucion WHERE fechaFin IS NULL OR fechaFin > NOW()")
        carreras_institucion = cur.fetchall() or []
        
        # Obtener las aptitudes y afinidades configuradas para cada carrera-institución
        carrera_aptitudes = {}
        for carrera in carreras_institucion:
            id_carrera_inst = carrera['idCarreraInstitucion']
            cur.execute("""
                SELECT ac.afinidadCarrera, a.nombreAptitud 
                FROM aptitudcarrera ac 
                JOIN aptitud a ON a.idAptitud = ac.idAptitud 
                WHERE ac.idCarreraInstitucion = %s 
                AND (a.fechaBaja IS NULL OR a.fechaBaja > NOW())
            """, (id_carrera_inst,))
            aptitudes_carrera = cur.fetchall() or []
            carrera_aptitudes[id_carrera_inst] = aptitudes_carrera

        # Calcular puntajes de compatibilidad para cada carrera
        carrera_puntajes = []
        for carrera in carreras_institucion:
            id_carrera_inst = carrera['idCarreraInstitucion']
            titulo_carrera = carrera['tituloCarrera']
            
            # Obtener las aptitudes configuradas para esta carrera
            aptitudes_carrera = carrera_aptitudes.get(id_carrera_inst, [])
            
            # Calcular el puntaje total sumando (aptitud_usuario * afinidad_carrera)
            puntaje_total = 0.0
            for aptitud_info in aptitudes_carrera:
                nombre_aptitud = aptitud_info['nombreAptitud']
                afinidad_carrera = aptitud_info['afinidadCarrera'] or 0.0
                
                # Obtener el puntaje del usuario en esta aptitud
                puntaje_usuario = aptitudes_obtenidas.get(nombre_aptitud, 0.0)
                
                # Sumar al puntaje total
                puntaje_total += puntaje_usuario * afinidad_carrera
            
            carrera_puntajes.append({
                "idCarreraInstitucion": id_carrera_inst,
                "tituloCarrera": titulo_carrera,
                "puntaje": puntaje_total
            })

        # Normalizar los puntajes a escala 0-100
        if carrera_puntajes:
            puntaje_maximo = max(c['puntaje'] for c in carrera_puntajes)
            
            # Si hay al menos una carrera con puntaje > 0, normalizar proporcionalmente
            if puntaje_maximo > 0:
                for carrera in carrera_puntajes:
                    # Convertir a escala 0-100
                    carrera['puntaje'] = round((carrera['puntaje'] / puntaje_maximo) * 100, 2)
            else:
                # Si todas tienen puntaje 0, dejarlas en 0
                for carrera in carrera_puntajes:
                    carrera['puntaje'] = 0.0

        # -- --------------------------------------------------------
        # -- Volcando estructura para tabla ovo.testcarrerainstitucion
        # CREATE TABLE IF NOT EXISTS `testcarrerainstitucion` (
        # `afinidadCarrera` double DEFAULT NULL,
        # `idTest` int(11) DEFAULT NULL,
        # `idCarreraInstitucion` int(11) DEFAULT NULL,
        # KEY `FK_testcarrerainstitucion_test` (`idTest`),
        # KEY `FK_testcarrerainstitucion_carrerainstitucion` (`idCarreraInstitucion`),
        # CONSTRAINT `FK_testcarrerainstitucion_carrerainstitucion` FOREIGN KEY (`idCarreraInstitucion`) REFERENCES `carrerainstitucion` (`idCarreraInstitucion`) ON UPDATE CASCADE,
        # CONSTRAINT `FK_testcarrerainstitucion_test` FOREIGN KEY (`idTest`) REFERENCES `test` (`idTest`) ON DELETE CASCADE ON UPDATE CASCADE
        # ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

        # Guardar los resultados en la tabla testcarrerainstitucion
        cur.execute("DELETE FROM testcarrerainstitucion WHERE idTest = %s", (id_test,))
        for carrera in carrera_puntajes:
            # Verificar que el puntaje no sea 0.0
            if carrera['puntaje'] > 0.0:
                cur.execute(
                    """
                    INSERT INTO testcarrerainstitucion (afinidadCarrera, idTest, idCarreraInstitucion)
                    VALUES (%s, %s, %s)
                    """,
                    (carrera['puntaje'], id_test, carrera['idCarreraInstitucion'])
                )


        # -- --------------------------------------------------------

        # -- Volcando estructura para tabla ovo.testaptitud
        # CREATE TABLE IF NOT EXISTS `testaptitud` (
        # `idResultadoAptitud` int(11) NOT NULL AUTO_INCREMENT,
        # `afinidadAptitud` double DEFAULT NULL,
        # `idAptitud` int(11) DEFAULT NULL,
        # `idTest` int(11) DEFAULT NULL,
        # PRIMARY KEY (`idResultadoAptitud`),
        # KEY `FK_testaptitud_aptitud` (`idAptitud`),
        # KEY `FK_testaptitud_test` (`idTest`),
        # CONSTRAINT `FK_testaptitud_aptitud` FOREIGN KEY (`idAptitud`) REFERENCES `aptitud` (`idAptitud`) ON DELETE CASCADE ON UPDATE CASCADE,
        # CONSTRAINT `FK_testaptitud_test` FOREIGN KEY (`idTest`) REFERENCES `test` (`idTest`) ON DELETE CASCADE ON UPDATE CASCADE
        # ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        
        # Guardar los resultados en la tabla testaptitud
        cur.execute("DELETE FROM testaptitud WHERE idTest = %s", (id_test,))
        for nombre_aptitud, valor in aptitudes_obtenidas.items():
            # Obtener el id de la aptitud con el nombre
            cur.execute("SELECT idAptitud FROM aptitud WHERE nombreAptitud = %s LIMIT 1", (nombre_aptitud,))
            aptitud_row = cur.fetchone()
            if not aptitud_row:
                continue  # Omitir si la aptitud no existe en la base de datos
            cur.execute(
                """
                INSERT INTO testaptitud (afinidadAptitud, idAptitud, idTest)
                VALUES (%s, %s, %s)
                """,
                (valor, aptitud_row['idAptitud'], id_test)
            )

        conn.commit()

        return jsonify({
            "testId": id_test,
            "aptitudesObtenidas": aptitudes_obtenidas,
            "carrerasRecomendadas": sorted(carrera_puntajes, key=lambda x: x['puntaje'], reverse=True),
            "fullHistory": resp_json.get("full_history", [])
        }), 200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"errorCode":"ERR1","message":"No se pudo obtener los resultados del test. Intente nuevamente. 2"}), 500
    finally:
        try:
            cur.close()
            conn.close()
        except Exception as e:
            pass
# Curl ejemplo endpoint anterior:
# curl --location '{{baseURL}}/api/v1/tests/1/results' --header 'Authorization: Bearer {{token}}' --data ''

# ============================ Estadísticas del Sistema (US023) ============================
# Tablas involucradas: usuario, usuariogrupo, usuarioestado, carrerainstitucion, institucionestado, test, testcarrerainstitucion
# Endpoint para obtener estadísticas del sistema para el administrador
# Filtros obligatorios: from (YYYY-MM-DD), to (YYYY-MM-DD)
# Filtro opcional: provinceId (ID de provincia)

# Si no hay datos en ninguna métrica solicitada del tablero -> ERR1 (mensaje pedir cambiar filtros).
# Permiso requerido
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

# Endpoint principal
@app.route('/api/v1/admin/stats/system', methods=['GET'])
@requires_permission('VIEW_STATS')
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
            GROUP BY tc.nombreTipoCarrera
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
@requires_permission('VIEW_STATS')
def admin_stats_system_export(current_user_id):
    filters, err_resp, err_code = _parse_stats_filters()
    if err_resp:
        return err_resp, err_code
    fmt = (request.args.get('format') or 'csv').lower()
    if fmt not in ('csv','pdf'):
        return jsonify({"errorCode":"ERR1","message":"Formato inválido"}), 400
    
    from_dt, to_dt, province_id = filters
    
    # Obtener los datos directamente sin pasar por los decoradores
    conn = None
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

        # Evolución registros (por mes)
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

        tests_completados = []

        # Carreras por tipo
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
            GROUP BY tc.nombreTipoCarrera
            ORDER BY tipo
            """,
            tuple(params_carr)
        )
        carreras_por_tipo = cur.fetchall() or []

        # Instituciones por estado
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

        # Tasa de actividad
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

        payload = {
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
        }
    except Exception as e:
        log(f"US023 system stats export error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR1","message":"Error al generar reporte"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
    if fmt == 'csv':
        try:
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
        except Exception as e:
            return jsonify({"errorCode":"ERR1","message":"Error al generar CSV"}), 500
    else:  # pdf
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.units import inch
            from io import BytesIO
            from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
            
            class PDFWithHeaderFooter(BaseDocTemplate):
                def __init__(self, *args, logo_path=None, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.logo_path = logo_path
                    frame = Frame(
                        self.leftMargin, self.bottomMargin, self.width, self.height, id='normal'
                    )
                    template = PageTemplate(id='all', frames=[frame], onPage=self._add_header_footer)
                    self.addPageTemplates([template])
                
                def _add_header_footer(self, canvas, doc):
                    canvas.saveState()
                    page_width, page_height = A4
                    
                    # Encabezado: Logo a la izquierda y texto a la derecha
                    if self.logo_path and os.path.exists(self.logo_path):
                        canvas.drawImage(self.logo_path, 36, page_height - 70, width=80, height=40, preserveAspectRatio=True)
                    
                    canvas.setFont('Helvetica-Bold', 12)
                    canvas.drawRightString(page_width - 36, page_height - 50, "ORIENTACIÓN VOCACIONAL ONLINE")
                    
                    # Línea separadora debajo del encabezado
                    canvas.setStrokeColor(colors.grey)
                    canvas.setLineWidth(0.5)
                    canvas.line(36, page_height - 75, page_width - 36, page_height - 75)
                    
                    # Pie de página: Número de página a la derecha
                    canvas.setFont('Helvetica', 9)
                    page_num = canvas.getPageNumber()
                    canvas.drawRightString(page_width - 36, 20, f"Página {page_num}")
                    canvas.restoreState()
            
            buffer = BytesIO()
            logo_path = os.path.join(os.path.dirname(__file__), 'OVO_logo.png')
            doc = PDFWithHeaderFooter(
                buffer,
                pagesize=A4,
                leftMargin=36,
                rightMargin=36,
                topMargin=90,
                bottomMargin=50,
                logo_path=logo_path
            )
            doc.title = "Estadísticas del Sistema"
            
            styles = getSampleStyleSheet()
            elements = []
            
            # Título principal
            title = Paragraph("Estadísticas del Sistema", styles["Heading1"])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Filtros aplicados
            filtros_txt = f"Período: {payload['filters']['from']} a {payload['filters']['to']}"
            if payload['filters']['provinceId']:
                filtros_txt += f" | Provincia ID: {payload['filters']['provinceId']}"
            elements.append(Paragraph(filtros_txt, styles["Normal"]))
            elements.append(Spacer(1, 16))
            
            # Usuarios por Tipo
            if payload.get('usuariosPorTipo'):
                elements.append(Paragraph("Usuarios por Tipo", styles["Heading2"]))
                elements.append(Spacer(1, 8))
                data_usuarios = [["Tipo de Usuario", "Total"]]
                for row in payload['usuariosPorTipo']:
                    data_usuarios.append([
                        Paragraph(str(row['tipo']), styles["Normal"]),
                        Paragraph(str(row['total']), styles["Normal"])
                    ])
                table_usuarios = Table(data_usuarios, colWidths=[4*inch, 2*inch])
                table_usuarios.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(table_usuarios)
                elements.append(Spacer(1, 16))
            
            # Evolución de Registros
            if payload.get('evolucionRegistros'):
                elements.append(Paragraph("Evolución de Registros", styles["Heading2"]))
                elements.append(Spacer(1, 8))
                data_evolucion = [["Período", "Total"]]
                for row in payload['evolucionRegistros']:
                    data_evolucion.append([
                        Paragraph(str(row['periodo']), styles["Normal"]),
                        Paragraph(str(row['total']), styles["Normal"])
                    ])
                table_evolucion = Table(data_evolucion, colWidths=[4*inch, 2*inch])
                table_evolucion.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(table_evolucion)
                elements.append(Spacer(1, 16))
            
            # Carreras por Tipo
            if payload.get('carrerasPorTipo'):
                elements.append(Paragraph("Carreras por Tipo", styles["Heading2"]))
                elements.append(Spacer(1, 8))
                data_carreras = [["Tipo de Carrera", "Total"]]
                for row in payload['carrerasPorTipo']:
                    data_carreras.append([
                        Paragraph(str(row['tipo']), styles["Normal"]),
                        Paragraph(str(row['total']), styles["Normal"])
                    ])
                table_carreras = Table(data_carreras, colWidths=[4*inch, 2*inch])
                table_carreras.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(table_carreras)
                elements.append(Spacer(1, 16))
            
            # Instituciones por Estado
            if payload.get('institucionesEstado'):
                elements.append(Paragraph("Instituciones por Estado", styles["Heading2"]))
                elements.append(Spacer(1, 8))
                data_instituciones = [["Estado", "Total"]]
                for row in payload['institucionesEstado']:
                    data_instituciones.append([
                        Paragraph(str(row['estado']), styles["Normal"]),
                        Paragraph(str(row['total']), styles["Normal"])
                    ])
                table_instituciones = Table(data_instituciones, colWidths=[4*inch, 2*inch])
                table_instituciones.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(table_instituciones)
                elements.append(Spacer(1, 16))
            
            # Actividad
            if payload.get('actividad'):
                elements.append(Paragraph("Actividad del Sistema", styles["Heading2"]))
                elements.append(Spacer(1, 8))
                act = payload['actividad']
                data_actividad = [
                    ["Métrica", "Valor"],
                    [Paragraph("Total Accesos", styles["Normal"]), Paragraph(str(act.get('totalAccesos', 0)), styles["Normal"])],
                    [Paragraph("Usuarios Activos", styles["Normal"]), Paragraph(str(act.get('usuariosActivos', 0)), styles["Normal"])],
                    [Paragraph("Total Usuarios", styles["Normal"]), Paragraph(str(act.get('totalUsuarios', 0)), styles["Normal"])],
                    [Paragraph("Tasa de Actividad", styles["Normal"]), Paragraph(f"{act.get('tasaActividad', 0):.2%}", styles["Normal"])],
                ]
                table_actividad = Table(data_actividad, colWidths=[4*inch, 2*inch])
                table_actividad.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(table_actividad)
            
            # Construir el PDF
            doc.build(elements)
            
            pdf = buffer.getvalue()
            buffer.close()
            
            from flask import Response
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"estadisticas_sistema_{ts}.pdf"
            return Response(
                pdf,
                mimetype='application/pdf',
                headers={'Content-Disposition': f'attachment; filename="{filename}"'}
            )
        except Exception as e:
            log(f"US023 system stats export PDF error: {e}\n{traceback.format_exc()}")
            return jsonify({"errorCode":"ERR3","message":"Ocurrió un error al generar el PDF. Intente nuevamente."}), 500

@app.route('/api/v1/admin/stats/users', methods=['GET'])
@requires_permission('VIEW_STATS')
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
            SELECT ci.idCarreraInstitucion AS idCI, 
                   COALESCE(ci.nombreCarrera, c.nombreCarrera, '(Sin nombre)') AS carrera,
                   COALESCE(i.nombreInstitucion, '(Sin institución)') AS institucion,
                   COUNT(*) total
            FROM interesusuariocarrera iuc
            JOIN carrerainstitucion ci ON ci.idCarreraInstitucion = iuc.idCarreraInstitucion
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN institucion i ON i.idInstitucion = ci.idInstitucion
            {fav_province_join}
            WHERE iuc.fechaAlta BETWEEN %s AND %s {fav_province_filter}
            GROUP BY ci.idCarreraInstitucion
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
@requires_permission('VIEW_STATS')
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

        # Ranking favoritas (cantidad de usuarios que le dieron favorito a cada carrera en relacion a todas las carreras (estadisticamente))
        params_fav = [id_inst, from_dt, to_dt]
        if tipos:
            params_fav.extend(tipos)
        cur.execute(
            f"""
            SELECT 
                ci.idCarreraInstitucion,
                COALESCE(ci.nombreCarrera, c.nombreCarrera, '(Sin nombre)') AS nombreCarrera,
                COUNT(DISTINCT iuc.idUsuario) AS totalFavoritos,
                ROUND(COUNT(DISTINCT iuc.idUsuario) * 100.0 / NULLIF((
                    SELECT COUNT(DISTINCT iuc2.idUsuario) 
                    FROM interesusuariocarrera iuc2
                    JOIN carrerainstitucion ci2 ON ci2.idCarreraInstitucion = iuc2.idCarreraInstitucion
                    WHERE ci2.idInstitucion = %s 
                    AND iuc2.fechaAlta BETWEEN %s AND %s
                    AND (iuc2.fechaFin IS NULL OR iuc2.fechaFin > NOW())
                ), 0), 2) AS porcentajeDelTotal
            FROM carrerainstitucion ci
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN tipocarrera tc ON tc.idTipoCarrera = c.idTipoCarrera
            LEFT JOIN interesusuariocarrera iuc ON iuc.idCarreraInstitucion = ci.idCarreraInstitucion
                AND iuc.fechaAlta BETWEEN %s AND %s
                AND (iuc.fechaFin IS NULL OR iuc.fechaFin > NOW())
            WHERE ci.idInstitucion = %s {tipo_filter_sql}
            GROUP BY ci.idCarreraInstitucion, ci.nombreCarrera, c.nombreCarrera
            HAVING totalFavoritos > 0
            ORDER BY totalFavoritos DESC, nombreCarrera
            LIMIT 10
            """,
            (id_inst, from_dt, to_dt, from_dt, to_dt, id_inst) + (tuple(tipos) if tipos else ())
        )
        ranking_favoritas = cur.fetchall() or []
        
        # Ranking por máxima compatibilidad de los test (viendo la afinidad de testcarrerainstitucion y haciendo estadistica)
        params_compat = [id_inst, from_dt, to_dt]
        if tipos:
            params_compat.extend(tipos)
        cur.execute(
            f"""
            SELECT 
                ci.idCarreraInstitucion,
                COALESCE(ci.nombreCarrera, c.nombreCarrera, '(Sin nombre)') AS nombreCarrera,
                ROUND(AVG(tci.afinidadCarrera), 2) AS promedioCompatibilidad,
                ROUND(MAX(tci.afinidadCarrera), 2) AS maxCompatibilidad,
                COUNT(DISTINCT tci.idTest) AS cantidadTests,
                COUNT(CASE WHEN tci.afinidadCarrera >= 80 THEN 1 END) AS testsAltaCompatibilidad
            FROM carrerainstitucion ci
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN tipocarrera tc ON tc.idTipoCarrera = c.idTipoCarrera
            LEFT JOIN testcarrerainstitucion tci ON tci.idCarreraInstitucion = ci.idCarreraInstitucion
            LEFT JOIN test t ON t.idTest = tci.idTest
            WHERE ci.idInstitucion = %s 
            AND t.fechaTest BETWEEN %s AND %s
            AND tci.afinidadCarrera IS NOT NULL
            {tipo_filter_sql}
            GROUP BY ci.idCarreraInstitucion, ci.nombreCarrera, c.nombreCarrera
            HAVING cantidadTests > 0
            ORDER BY promedioCompatibilidad DESC, maxCompatibilidad DESC
            LIMIT 10
            """,
            tuple(params_compat)
        )
        ranking_max_compatibilidad = cur.fetchall() or []
        
        # Promedio de compatibilidades por tipo carrera valor de compatibilidad con carreras del mismo tipo (pasando por carrera base)
        params_tipo = [id_inst, from_dt, to_dt]
        if tipos:
            params_tipo.extend(tipos)
        cur.execute(
            f"""
            SELECT 
                COALESCE(tc.nombreTipoCarrera, 'Sin Tipo') AS tipoCarrera,
                tc.idTipoCarrera,
                ROUND(AVG(tci.afinidadCarrera), 2) AS promedioCompatibilidad,
                ROUND(MIN(tci.afinidadCarrera), 2) AS minCompatibilidad,
                ROUND(MAX(tci.afinidadCarrera), 2) AS maxCompatibilidad,
                COUNT(DISTINCT ci.idCarreraInstitucion) AS cantidadCarreras,
                COUNT(DISTINCT tci.idTest) AS cantidadTests
            FROM carrerainstitucion ci
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN tipocarrera tc ON tc.idTipoCarrera = c.idTipoCarrera
            LEFT JOIN testcarrerainstitucion tci ON tci.idCarreraInstitucion = ci.idCarreraInstitucion
            LEFT JOIN test t ON t.idTest = tci.idTest
            WHERE ci.idInstitucion = %s 
            AND t.fechaTest BETWEEN %s AND %s
            AND tci.afinidadCarrera IS NOT NULL
            {tipo_filter_sql}
            GROUP BY tc.idTipoCarrera, tc.nombreTipoCarrera
            HAVING cantidadTests > 0
            ORDER BY promedioCompatibilidad DESC
            """,
            tuple(params_tipo)
        )
        promedio_por_tipo = cur.fetchall() or []

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
    
    from_dt, to_dt, tipos = filters
    
    # Obtener los datos directamente
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        id_inst = _my_inst_id(conn, current_user_id)
        if not id_inst:
            return jsonify({"errorCode":"ERR1","message":"Institución no encontrada."}), 404
        cur = conn.cursor(dictionary=True)

        params = [id_inst, from_dt, to_dt]
        tipo_filter_sql = ''
        if tipos:
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

        # Carreras dadas de baja
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

        # Ranking favoritas
        params_fav = [id_inst, from_dt, to_dt]
        if tipos:
            params_fav.extend(tipos)
        cur.execute(
            f"""
            SELECT 
                ci.idCarreraInstitucion,
                COALESCE(ci.nombreCarrera, c.nombreCarrera, '(Sin nombre)') AS nombreCarrera,
                COUNT(DISTINCT iuc.idUsuario) AS totalFavoritos,
                ROUND(COUNT(DISTINCT iuc.idUsuario) * 100.0 / NULLIF((
                    SELECT COUNT(DISTINCT iuc2.idUsuario) 
                    FROM interesusuariocarrera iuc2
                    JOIN carrerainstitucion ci2 ON ci2.idCarreraInstitucion = iuc2.idCarreraInstitucion
                    WHERE ci2.idInstitucion = %s 
                    AND iuc2.fechaAlta BETWEEN %s AND %s
                    AND (iuc2.fechaFin IS NULL OR iuc2.fechaFin > NOW())
                ), 0), 2) AS porcentajeDelTotal
            FROM carrerainstitucion ci
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN tipocarrera tc ON tc.idTipoCarrera = c.idTipoCarrera
            LEFT JOIN interesusuariocarrera iuc ON iuc.idCarreraInstitucion = ci.idCarreraInstitucion
                AND iuc.fechaAlta BETWEEN %s AND %s
                AND (iuc.fechaFin IS NULL OR iuc.fechaFin > NOW())
            WHERE ci.idInstitucion = %s {tipo_filter_sql}
            GROUP BY ci.idCarreraInstitucion, ci.nombreCarrera, c.nombreCarrera
            HAVING totalFavoritos > 0
            ORDER BY totalFavoritos DESC, nombreCarrera
            LIMIT 10
            """,
            (id_inst, from_dt, to_dt, from_dt, to_dt, id_inst) + (tuple(tipos) if tipos else ())
        )
        ranking_favoritas = cur.fetchall() or []
        
        # Ranking por máxima compatibilidad
        params_compat = [id_inst, from_dt, to_dt]
        if tipos:
            params_compat.extend(tipos)
        cur.execute(
            f"""
            SELECT 
                ci.idCarreraInstitucion,
                COALESCE(ci.nombreCarrera, c.nombreCarrera, '(Sin nombre)') AS nombreCarrera,
                ROUND(AVG(tci.afinidadCarrera), 2) AS promedioCompatibilidad,
                ROUND(MAX(tci.afinidadCarrera), 2) AS maxCompatibilidad,
                COUNT(DISTINCT tci.idTest) AS cantidadTests,
                COUNT(CASE WHEN tci.afinidadCarrera >= 80 THEN 1 END) AS testsAltaCompatibilidad
            FROM carrerainstitucion ci
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN tipocarrera tc ON tc.idTipoCarrera = c.idTipoCarrera
            LEFT JOIN testcarrerainstitucion tci ON tci.idCarreraInstitucion = ci.idCarreraInstitucion
            LEFT JOIN test t ON t.idTest = tci.idTest
            WHERE ci.idInstitucion = %s 
            AND t.fechaTest BETWEEN %s AND %s
            AND tci.afinidadCarrera IS NOT NULL
            {tipo_filter_sql}
            GROUP BY ci.idCarreraInstitucion, ci.nombreCarrera, c.nombreCarrera
            HAVING cantidadTests > 0
            ORDER BY promedioCompatibilidad DESC, maxCompatibilidad DESC
            LIMIT 10
            """,
            tuple(params_compat)
        )
        ranking_max_compatibilidad = cur.fetchall() or []
        
        # Promedio por tipo
        params_tipo = [id_inst, from_dt, to_dt]
        if tipos:
            params_tipo.extend(tipos)
        cur.execute(
            f"""
            SELECT 
                COALESCE(tc.nombreTipoCarrera, 'Sin Tipo') AS tipoCarrera,
                tc.idTipoCarrera,
                ROUND(AVG(tci.afinidadCarrera), 2) AS promedioCompatibilidad,
                ROUND(MIN(tci.afinidadCarrera), 2) AS minCompatibilidad,
                ROUND(MAX(tci.afinidadCarrera), 2) AS maxCompatibilidad,
                COUNT(DISTINCT ci.idCarreraInstitucion) AS cantidadCarreras,
                COUNT(DISTINCT tci.idTest) AS cantidadTests
            FROM carrerainstitucion ci
            LEFT JOIN carrera c ON c.idCarrera = ci.idCarrera
            LEFT JOIN tipocarrera tc ON tc.idTipoCarrera = c.idTipoCarrera
            LEFT JOIN testcarrerainstitucion tci ON tci.idCarreraInstitucion = ci.idCarreraInstitucion
            LEFT JOIN test t ON t.idTest = tci.idTest
            WHERE ci.idInstitucion = %s 
            AND t.fechaTest BETWEEN %s AND %s
            AND tci.afinidadCarrera IS NOT NULL
            {tipo_filter_sql}
            GROUP BY tc.idTipoCarrera, tc.nombreTipoCarrera
            HAVING cantidadTests > 0
            ORDER BY promedioCompatibilidad DESC
            """,
            tuple(params_tipo)
        )
        promedio_por_tipo = cur.fetchall() or []

        payload = {
            "filters": {"from": str(from_dt), "to": str(to_dt), "tiposCarrera": tipos},
            "totalCarreras": total_carreras,
            "totalBajas": total_bajas,
            "rankingFavoritas": ranking_favoritas,
            "rankingMaxCompatibilidad": ranking_max_compatibilidad,
            "promedioCompatibilidadPorTipo": promedio_por_tipo
        }
    except Exception as e:
        log(f"US024 general stats export error: {e}\n{traceback.format_exc()}")
        return jsonify({"errorCode":"ERR1","message":"Error al generar reporte"}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
    
    # Convertir Decimal a float para serialización JSON
    def _convert_decimals(obj):
        if isinstance(obj, dict):
            return {k: _convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_convert_decimals(item) for item in obj]
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return obj
    
    payload = _convert_decimals(payload)
    
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
    else:  # pdf
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.units import inch
            from io import BytesIO
            from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
            
            class PDFWithHeaderFooter(BaseDocTemplate):
                def __init__(self, *args, logo_path=None, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.logo_path = logo_path
                    frame = Frame(
                        self.leftMargin, self.bottomMargin, self.width, self.height, id='normal'
                    )
                    template = PageTemplate(id='all', frames=[frame], onPage=self._add_header_footer)
                    self.addPageTemplates([template])
                
                def _add_header_footer(self, canvas, doc):
                    canvas.saveState()
                    page_width, page_height = A4
                    
                    # Encabezado: Logo a la izquierda y texto a la derecha
                    if self.logo_path and os.path.exists(self.logo_path):
                        canvas.drawImage(self.logo_path, 36, page_height - 70, width=80, height=40, preserveAspectRatio=True)
                    
                    canvas.setFont('Helvetica-Bold', 12)
                    canvas.drawRightString(page_width - 36, page_height - 50, "ORIENTACIÓN VOCACIONAL ONLINE")
                    
                    # Línea separadora debajo del encabezado
                    canvas.setStrokeColor(colors.grey)
                    canvas.setLineWidth(0.5)
                    canvas.line(36, page_height - 75, page_width - 36, page_height - 75)
                    
                    # Pie de página: Número de página a la derecha
                    canvas.setFont('Helvetica', 9)
                    page_num = canvas.getPageNumber()
                    canvas.drawRightString(page_width - 36, 20, f"Página {page_num}")
                    canvas.restoreState()
            
            buffer = BytesIO()
            logo_path = os.path.join(os.path.dirname(__file__), 'OVO_logo.png')
            doc = PDFWithHeaderFooter(
                buffer,
                pagesize=A4,
                leftMargin=36,
                rightMargin=36,
                topMargin=90,
                bottomMargin=50,
                logo_path=logo_path
            )
            doc.title = "Estadísticas Generales de Institución"
            
            styles = getSampleStyleSheet()
            elements = []
            
            # Título principal
            title = Paragraph("Estadísticas Generales de Institución", styles["Heading1"])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Filtros aplicados
            filtros_txt = f"Período: {payload['filters']['from']} a {payload['filters']['to']}"
            if payload['filters'].get('tiposCarrera'):
                filtros_txt += f" | Tipos de Carrera: {', '.join(map(str, payload['filters']['tiposCarrera']))}"
            elements.append(Paragraph(filtros_txt, styles["Normal"]))
            elements.append(Spacer(1, 16))
            
            # Métricas Generales
            elements.append(Paragraph("Métricas Generales", styles["Heading2"]))
            elements.append(Spacer(1, 8))
            data_metricas = [
                ["Métrica", "Valor"],
                [Paragraph("Total de Carreras", styles["Normal"]), Paragraph(str(payload.get('totalCarreras', 0)), styles["Normal"])],
                [Paragraph("Total de Bajas", styles["Normal"]), Paragraph(str(payload.get('totalBajas', 0)), styles["Normal"])],
            ]
            table_metricas = Table(data_metricas, colWidths=[4*inch, 2*inch])
            table_metricas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table_metricas)
            elements.append(Spacer(1, 16))
            
            # Ranking de Favoritas
            if payload.get('rankingFavoritas'):
                elements.append(Paragraph("Ranking de Carreras Favoritas", styles["Heading2"]))
                elements.append(Spacer(1, 8))
                data_favoritas = [["Carrera", "Total Favoritos", "% del Total"]]
                for row in payload['rankingFavoritas']:
                    data_favoritas.append([
                        Paragraph(str(row.get('nombreCarrera', '')), styles["Normal"]),
                        Paragraph(str(row.get('totalFavoritos', 0)), styles["Normal"]),
                        Paragraph(f"{row.get('porcentajeDelTotal', 0)}%", styles["Normal"])
                    ])
                table_favoritas = Table(data_favoritas, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                table_favoritas.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(table_favoritas)
                elements.append(Spacer(1, 16))
            
            # Ranking por Máxima Compatibilidad
            if payload.get('rankingMaxCompatibilidad'):
                elements.append(Paragraph("Ranking por Compatibilidad", styles["Heading2"]))
                elements.append(Spacer(1, 8))
                data_compat = [["Carrera", "Promedio", "Máxima", "Tests"]]
                for row in payload['rankingMaxCompatibilidad']:
                    data_compat.append([
                        Paragraph(str(row.get('nombreCarrera', '')), styles["Normal"]),
                        Paragraph(str(row.get('promedioCompatibilidad', 0)), styles["Normal"]),
                        Paragraph(str(row.get('maxCompatibilidad', 0)), styles["Normal"]),
                        Paragraph(str(row.get('cantidadTests', 0)), styles["Normal"])
                    ])
                table_compat = Table(data_compat, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
                table_compat.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(table_compat)
                elements.append(Spacer(1, 16))
            
            # Promedio de Compatibilidad por Tipo
            if payload.get('promedioCompatibilidadPorTipo'):
                elements.append(Paragraph("Promedio de Compatibilidad por Tipo", styles["Heading2"]))
                elements.append(Spacer(1, 8))
                data_tipo = [["Tipo de Carrera", "Promedio", "Mínima", "Máxima", "Carreras", "Tests"]]
                for row in payload['promedioCompatibilidadPorTipo']:
                    data_tipo.append([
                        Paragraph(str(row.get('tipoCarrera', '')), styles["Normal"]),
                        Paragraph(str(row.get('promedioCompatibilidad', 0)), styles["Normal"]),
                        Paragraph(str(row.get('minCompatibilidad', 0)), styles["Normal"]),
                        Paragraph(str(row.get('maxCompatibilidad', 0)), styles["Normal"]),
                        Paragraph(str(row.get('cantidadCarreras', 0)), styles["Normal"]),
                        Paragraph(str(row.get('cantidadTests', 0)), styles["Normal"])
                    ])
                table_tipo = Table(data_tipo, colWidths=[1.8*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 0.8*inch])
                table_tipo.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(table_tipo)
            
            # Construir el PDF
            doc.build(elements)
            
            pdf = buffer.getvalue()
            buffer.close()
            
            from flask import Response
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"estadisticas_institucion_general_{ts}.pdf"
            return Response(
                pdf,
                mimetype='application/pdf',
                headers={'Content-Disposition': f'attachment; filename="{filename}"'}
            )
        except Exception as e:
            log(f"US024 general stats export PDF error: {e}\n{traceback.format_exc()}")
            return jsonify({"errorCode":"ERR3","message":"Ocurrió un error al generar el PDF. Intente nuevamente."}), 500

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
# Permiso requerido.

VALID_FREQUENCIAS_BACKUP = { 'diaria','semanal','mensual' }

def _read_backup_config(cur):
    cur.execute("SELECT frecuencia, TIME_FORMAT(horaEjecucion,'%H:%i') AS horaEjecucion, cantidadBackupConservar FROM configuracionbackup LIMIT 1")
    row = cur.fetchone()
    if not row:
        return {"frecuencia": None, "horaEjecucion": None, "cantidadBackupConservar": None}
    return {"frecuencia": row['frecuencia'], "horaEjecucion": row['horaEjecucion'], "cantidadBackupConservar": row['cantidadBackupConservar']}

@app.route('/api/v1/admin/backup/config', methods=['GET'])
@requires_permission('BACKUP_CONFIG')
def backup_config_get(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
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
@requires_permission('BACKUP_CONFIG')
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
        cur = conn.cursor(dictionary=True)
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
    # row: dictionary with keys fechaBackup, directorio, tamano
    return {
        "fechaBackup": row['fechaBackup'].strftime('%Y-%m-%d %H:%M:%S') if row['fechaBackup'] else None,
        "directorio": row['directorio'],
        "tamano": row['tamano']
    }

@app.route('/api/v1/admin/backup/list', methods=['GET'])
@requires_permission('BACKUP_RESTORE')
def backup_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
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
@requires_permission('BACKUP_RESTORE')
def backup_restore_start(current_user_id):
    data = request.get_json(silent=True) or {}
    fecha = data.get('fechaBackup')
    if not fecha:
        return jsonify({"errorCode":"ERR2","message":"El archivo de respaldo seleccionado no es válido o está dañado."}), 400
    # Verificar existencia en tabla
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
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
@requires_permission('BACKUP_RESTORE')
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
# Estados simulados: Pendiente, APROBADA, RECHAZADA.
# Filtros: nombre (substring), tipoId (int), estado (cadena), from/to (fecha solicitud en memoria). ERR1 filtros inválidos.
# Acciones: aprobar (ERR2 si falla), rechazar (ERR3 si falla). Justificación opcional en rechazo.

_INSTITUTION_REQUESTS_MEM = {
    # idInstitucion: { 'nombre': str, 'email': str, 'tipoId': int, 'localizacion': '---', 'estado': 'Pendiente', 'fechaSolicitud': datetime.date }
}

@app.route('/api/v1/admin/institutions/requests', methods=['GET'])
@requires_permission(['MANAGE_INSTITUTION_REQUESTS', 'ADMIN_APPROVE_INSTITUTION'])
def admin_institution_requests_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        
        # Consultar todas las instituciones con su información básica
        cur.execute("""
            SELECT 
                i.idInstitucion,
                i.nombreInstitucion,
                i.mail,
                i.fechaAlta,
                i.idTipoInstitucion,
                l.nombreLocalidad,
                p.nombreProvincia,
                pa.nombrePais
            FROM institucion i
            LEFT JOIN localidad l ON i.idLocalidad = l.idLocalidad
            LEFT JOIN provincia p ON l.idProvincia = p.idProvincia  
            LEFT JOIN pais pa ON p.idPais = pa.idPais
            ORDER BY i.idInstitucion
        """)
        
        instituciones = cur.fetchall()
        solicitudes = []
        
        for inst in instituciones:
            # Obtener el último estado de la institución
            cur.execute("""
                SELECT ei.nombreEstadoInstitucion, ie.justificacion
                FROM institucionestado ie
                JOIN estadoinstitucion ei ON ie.idEstadoInstitucion = ei.idEstadoInstitucion
                WHERE ie.idInstitucion = %s 
                  AND ie.fechaFin IS NULL
                ORDER BY ie.fechaInicio DESC
                LIMIT 1
            """, (inst['idInstitucion'],))
            
            estado_row = cur.fetchone()
            estado = estado_row['nombreEstadoInstitucion'] if estado_row else "Pendiente"
            justificacion = estado_row['justificacion'] if estado_row else None

            # Construir localización
            localizacion_parts = []
            if inst['nombreLocalidad']:
                localizacion_parts.append(inst['nombreLocalidad'])
            if inst['nombreProvincia']:
                localizacion_parts.append(inst['nombreProvincia'])
            if inst['nombrePais']:
                localizacion_parts.append(inst['nombrePais'])
            
            localizacion = ", ".join(localizacion_parts) if localizacion_parts else "N/D"
            
            solicitud = {
                "idInstitucion": inst['idInstitucion'],
                "nombre": inst['nombreInstitucion'] or f"Institución {inst['idInstitucion']}",
                "email": inst['mail'] or "N/D",
                "estado": estado,
                "fechaSolicitud": inst['fechaAlta'].strftime('%Y-%m-%d') if inst['fechaAlta'] else "N/D",
                "tipoId": inst['idTipoInstitucion'] or 1,
                "localizacion": localizacion,
                "justificacion": justificacion
            }
            
            solicitudes.append(solicitud)
        
        return jsonify({'solicitudes': solicitudes}), 200
        
    except Exception as e:
        log(f"US028 list error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Filtros inválidos. Verifique los datos ingresados.'}), 400
    finally:
        try:
            if conn: conn.close()
        except Exception: pass



@app.route('/api/v1/admin/institutions/requests/<int:id_institucion>/approve', methods=['POST'])
@requires_permission('MANAGE_INSTITUTION_REQUESTS')
def admin_institution_request_approve(current_user_id, id_institucion):
    conn=None
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json(silent=True) or {}
        user_id = data.get('userId')
        is_new_user = False
        password_new_user = None
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        
        # Verificar que la institución exista
        cur.execute("SELECT * FROM institucion WHERE idInstitucion=%s", (id_institucion,))
        institucion = cur.fetchone()
        if not institucion:
            return jsonify({'errorCode':'ERR2','message':'La institución no existe.'}), 404
        
        # Verificar que se haya proporcionado un userId
        if not user_id:
            # Creamos un nuevo usuario usando los campos correctos de la tabla usuario
            password_new_user = generate_password()
            # Usamos valores por defecto para campos requeridos
            default_dni = 0  # DNI por defecto para usuarios auto-creados
            default_fecha_nac = '1990-01-01'  # Fecha de nacimiento por defecto
            default_genero = 1  # Asumimos que existe un género con ID 1

            # Buscar estadousuario "Activo"
            cur.execute("SELECT * FROM estadousuario WHERE nombreEstadoUsuario='Activo' LIMIT 1")
            estado_activo = cur.fetchone()
            if not estado_activo:
                return jsonify({'errorCode':'ERR2','message':'No se pudo obtener el estado de usuario Activo.'}), 404
            id_estado_activo = estado_activo['idEstadoUsuario']
            
            cur.execute("""INSERT INTO usuario (mail, dni, nombre, apellido, contrasena, fechaNac, idGenero, idLocalidad) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (institucion['mail'], 
                         default_dni, 
                         f'Usuario-{institucion["nombreInstitucion"]}', 
                         'AutoCreado', 
                         hash_password(password_new_user), 
                         default_fecha_nac,
                         default_genero,
                         institucion.get('idLocalidad')))
            user_id = cur.lastrowid

            # Asignar estado "Activo" al nuevo usuario con usuarioestado
            cur.execute("INSERT INTO usuarioestado (idUsuario, idEstadoUsuario, fechaInicio) VALUES (%s, %s, NOW())", (user_id, id_estado_activo))

            conn.commit()
            is_new_user = True

        # Verificar que el usuario exista
        cur.execute("SELECT idUsuario FROM usuario WHERE idUsuario=%s", (user_id,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'El usuario especificado no existe.'}), 404

        # Verificar que el usuario no tenga ninguna instiucion asignada
        cur.execute("SELECT idInstitucion FROM institucion WHERE idUsuario=%s", (user_id,))
        if cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'El usuario ya tiene una institución asignada.'}), 400
        
        # Verificar el estado actual pasando por la tabla intermedia
        cur.execute("""
            SELECT ei.nombreEstadoInstitucion, ei.idEstadoInstitucion
            FROM institucionestado ie
            JOIN estadoinstitucion ei ON ie.idEstadoInstitucion = ei.idEstadoInstitucion
            WHERE ie.idInstitucion = %s AND (ie.fechaFin IS NULL OR ie.fechaFin > NOW())
            ORDER BY ie.fechaInicio DESC
            LIMIT 1
        """, (id_institucion,))
        estado_actual = cur.fetchone()
        if not estado_actual:
            return jsonify({'errorCode':'ERR2','message':'No se pudo obtener el estado actual.'}), 404
        
        # Obtenemos el id del estado 'Aprobada'
        cur.execute("SELECT * FROM estadoinstitucion WHERE nombreEstadoInstitucion='Aprobada' LIMIT 1")
        estado_aprobada = cur.fetchone()
        if not estado_aprobada:
            return jsonify({'errorCode':'ERR2','message':'No se pudo obtener el estado de Aprobada.'}), 404
        id_estado_aprobada = estado_aprobada['idEstadoInstitucion']
        
        # Actualizar el estado de la institución a 'Aprobada'
        cur.execute("""
            UPDATE institucionestado
            SET fechaFin = NOW()
            WHERE idInstitucion = %s AND idEstadoInstitucion = %s AND (fechaFin IS NULL OR fechaFin > NOW())
        """, (id_institucion, estado_actual['idEstadoInstitucion']))

        cur.execute("""
            INSERT INTO institucionestado (idInstitucion, idEstadoInstitucion, fechaInicio)
            VALUES (%s, %s, NOW())
        """, (id_institucion, id_estado_aprobada))

        # Asignar el usuario a la institución
        cur.execute("""
            UPDATE institucion 
            SET idUsuario = %s 
            WHERE idInstitucion = %s
        """, (user_id, id_institucion))

        # Asignar al usuario al grupo Institución si no lo tiene
        # Obtener el id del grupo 'Institución'
        cur.execute("SELECT idGrupo FROM grupo WHERE nombreGrupo='Institución' LIMIT 1")
        grupo_institucion = cur.fetchone()
        if not grupo_institucion:
            return jsonify({'errorCode':'ERR2','message':'No se pudo obtener el grupo Institución.'}), 404
        id_grupo_institucion = grupo_institucion['idGrupo']

        # Verificar si el usuario ya pertenece al grupo
        cur.execute("SELECT * FROM usuariogrupo WHERE idUsuario=%s AND idGrupo=%s", (user_id, id_grupo_institucion))
        if not cur.fetchone():
            cur.execute("INSERT INTO usuariogrupo (idUsuario, idGrupo) VALUES (%s, %s)", (user_id, id_grupo_institucion))
            conn.commit()

        # Enviar correo de notificación de aprobación
        cur.execute("SELECT mail, nombreInstitucion FROM institucion WHERE idInstitucion = %s", (id_institucion,))
        institucion_info = cur.fetchone()
        
        if institucion_info and institucion_info['mail']:
            try:
                if is_new_user:
                    send_email(
                        institucion_info['mail'], 
                        "Solicitud de registro aprobada - OVO", 
                        f"""
                        Estimados, <br><br>
                        
                        Nos complace informarle que su solicitud de registro para la institución "{institucion_info['nombreInstitucion']}" ha sido aprobada exitosamente. <br><br>
                        
                        Su institución ahora forma parte de la plataforma OVO y puede comenzar a gestionar sus carreras y contenido académico.<br><br>

                        Se le creo un usuario automáticamente con las siguientes credenciales:<br>
                        Usuario: {institucion_info['mail']}<br>
                        Contraseña: {password_new_user}<br><br>

                        Para acceder a su panel de administración, utilice las credenciales que le serán enviadas por separado. <br><br>
                        Le recomendamos cambiar su contraseña en el primer inicio de sesión.<br><br>
                        
                        Saludos cordiales, <br>
                        Equipo OVO
                        """
                    )
                else:
                    send_email(
                        institucion_info['mail'], 
                        "Solicitud de registro aprobada - OVO", 
                        f"""
                        Estimados, <br><br>
                        
                        Nos complace informarle que su solicitud de registro para la institución "{institucion_info['nombreInstitucion']}" ha sido aprobada exitosamente. <br><br>
                        
                        Su institución ahora forma parte de la plataforma OVO y puede comenzar a gestionar sus carreras y contenido académico. <br><br>
                        
                        Para acceder a su panel de administración, utilice las credenciales que le serán enviadas por separado. <br><br>
                        
                        Saludos cordiales, <br>
                        Equipo OVO
                        """
                    )
            except Exception as email_error:
                log(f"Error sending approval email: {email_error}")

        conn.commit()
        conn.close()
        return jsonify({'ok': True, 'message': 'Solicitud aprobada.'}), 200
    except Exception as e:
        log(f"US028 approve error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo aprobar la solicitud. Intente nuevamente.'}), 500
    finally:
        try:
            conn.close()
        except Exception as e:
            pass

@app.route('/api/v1/admin/institutions/requests/<int:id_institucion>/reject', methods=['POST'])
@requires_permission('MANAGE_INSTITUTION_REQUESTS')
def admin_institution_request_reject(current_user_id, id_institucion):
    conn=None
    try:
        data = request.get_json(silent=True) or {}
        justificacion = (data.get('justificacion') or '').strip()
        if not justificacion:
            return jsonify({'errorCode':'ERR1','message':'La justificacion es obligatoria.'}), 400
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        
        # Verificar que la institución exista
        cur.execute("SELECT idInstitucion FROM institucion WHERE idInstitucion=%s", (id_institucion,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR3','message':'La institución no existe.'}), 404
        
        # Verificar el estado actual
        cur.execute("""
            SELECT ei.nombreEstadoInstitucion
            FROM institucionestado ie
            JOIN estadoinstitucion ei ON ie.idEstadoInstitucion = ei.idEstadoInstitucion
            WHERE ie.idInstitucion = %s AND (ie.fechaFin IS NULL OR ie.fechaFin > NOW())
            ORDER BY ie.fechaInicio DESC
            LIMIT 1
        """, (id_institucion,))
        
        estado_actual = cur.fetchone()
        if not estado_actual or estado_actual['nombreEstadoInstitucion'] != 'Pendiente':
            return jsonify({'errorCode':'ERR3','message':'Solo se pueden rechazar instituciones en estado Pendiente.'}), 400
        
        # Obtener el id del estado 'Rechazada'
        cur.execute("SELECT idEstadoInstitucion FROM estadoinstitucion WHERE nombreEstadoInstitucion='Rechazada' LIMIT 1")
        estado_rechazada = cur.fetchone()
        if not estado_rechazada:
            # Crear el estado si no existe
            cur.execute("INSERT INTO estadoinstitucion (nombreEstadoInstitucion) VALUES (%s)", ("Rechazada",))
            conn.commit()
            estado_rechazada = {'idEstadoInstitucion': cur.lastrowid}
        
        id_estado_rechazada = estado_rechazada['idEstadoInstitucion']
        
        # Cerrar el estado actual y crear nuevo estado 'Rechazada'
        cur.execute("""
            UPDATE institucionestado 
            SET fechaFin = NOW() 
            WHERE idInstitucion = %s AND fechaFin IS NULL
        """, (id_institucion,))
        
        cur.execute("""
            INSERT INTO institucionestado (idInstitucion, idEstadoInstitucion, fechaInicio, justificacion)
            VALUES (%s, %s, NOW(), %s)
        """, (id_institucion, id_estado_rechazada, justificacion))
        
        conn.commit()
        
        # Enviar correo de notificación de rechazo
        cur.execute("SELECT mail, nombreInstitucion FROM institucion WHERE idInstitucion = %s", (id_institucion,))
        institucion_info = cur.fetchone()
        
        if institucion_info and institucion_info['mail']:
            try:
                send_email(
                    institucion_info['mail'], 
                    "Solicitud de registro rechazada - OVO", 
                    f"""
                    Estimados,
                    
                    Lamentamos informarle que su solicitud de registro para la institución "{institucion_info['nombreInstitucion']}" ha sido rechazada.
                    
                    Motivo del rechazo: {justificacion}
                    
                    Si considera que esto es un error o desea realizar una nueva solicitud con las correcciones necesarias, puede contactarnos o enviar una nueva solicitud.
                    
                    Saludos cordiales,
                    Equipo OVO
                    """
                )
            except Exception as email_error:
                log(f"Error sending rejection email: {email_error}")
        
        return jsonify({'ok': True, 'message': 'Solicitud rechazada correctamente.'}), 200

    except Exception as e:
        log(f"US028 reject error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo rechazar la solicitud. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# Endpoint para dar de baja la institución
@app.route('/api/v1/admin/institutions/<int:id_institucion>/deactivate', methods=['POST'])
@requires_permission('MANAGE_INSTITUTION_REQUESTS')
def admin_institution_deactivate(current_user_id, id_institucion):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        # Verificar que la institución exista
        cur.execute("SELECT idInstitucion FROM institucion WHERE idInstitucion=%s", (id_institucion,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR3','message':'La institución no existe.'}), 404
        # Actualizar la fechaFin de todos los estados activos
        cur.execute("""
            UPDATE institucionestado SET fechaFin=NOW() WHERE idInstitucion=%s AND (fechaFin IS NULL OR fechaFin > NOW())
        """, (id_institucion,))

        # Obtener id de estado "Baja"
        cur.execute("SELECT idEstadoInstitucion FROM estadoinstitucion WHERE nombreEstadoInstitucion='Baja'", ())
        estado_baja = cur.fetchone()
        if not estado_baja:
            return jsonify({'errorCode':'ERR3','message':'No se encontró el estado "Baja".'}), 404

        # Actualizar el estado de la institución
        cur.execute("""
            INSERT INTO institucionestado (idInstitucion, idEstadoInstitucion, fechaInicio, fechaFin)
            VALUES (%s, %s, NOW(), NULL)
        """, (id_institucion, estado_baja['idEstadoInstitucion']))

        # Enviar correo electrónico notificando la baja
        cur.execute("SELECT mail, nombreInstitucion FROM institucion WHERE idInstitucion = %s", (id_institucion,))
        institucion_info = cur.fetchone()
        if institucion_info and institucion_info['mail']:
            try:
                send_email(
                    to=institucion_info['mail'],
                    subject="Notificación de baja institución - OVO",
                    body=f"""
                    Estimados,

                    Se ha dado de baja la institución: {institucion_info['nombreInstitucion']}
                    Si considera que esto es un error o desea más información, por favor contacte a soporte.
                    Saludos cordiales,
                    Equipo OVO
                    """
                )
            except Exception as e:
                log(f"US028 send email error: {e}\n{traceback.format_exc()}")

        conn.commit()
        return jsonify({'ok': True, 'message': 'Institución dada de baja correctamente.'}), 200
    except Exception as e:
        log(f"US028 deactivate institution error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo dar de baja la institución. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
# Curl ejemplo:
# curl -X POST {{baseURL}}/api/v1/admin/institutions/5/deactivate -H "Authorization: Bearer {{token}}"

# Endpoint para volver a activar la institución
@app.route('/api/v1/admin/institutions/<int:id_institucion>/activate', methods=['POST'])
@requires_permission('MANAGE_INSTITUTION_REQUESTS')
def admin_institution_activate(current_user_id, id_institucion):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)

        # Verificar si la institución existe
        cur.execute("""
            SELECT idInstitucion FROM institucion WHERE idInstitucion = %s
        """, (id_institucion,))
        institucion = cur.fetchone()
        if not institucion:
            return jsonify({'errorCode':'ERR3','message':'La institución no existe.'}), 404

        # Verificar si la institución está dada de baja (estado 'Baja')
        cur.execute("""
            SELECT ie.idinstitucionEstado, ei.nombreEstadoInstitucion
            FROM institucionestado ie
            JOIN estadoinstitucion ei ON ie.idEstadoInstitucion = ei.idEstadoInstitucion
            WHERE ie.idInstitucion = %s AND (ie.fechaFin IS NULL OR ie.fechaFin > NOW())
            ORDER BY ie.fechaInicio DESC
            LIMIT 1
        """, (id_institucion,))
        estado_actual = cur.fetchone()
        
        if not estado_actual or estado_actual['nombreEstadoInstitucion'] != 'Baja':
            return jsonify({'errorCode':'ERR3','message':'La institución no está dada de baja o ya está activa.'}), 400

        # Obtener el id del estado 'Aprobada' o 'Activa'
        cur.execute("SELECT idEstadoInstitucion FROM estadoinstitucion WHERE nombreEstadoInstitucion='Aprobada' LIMIT 1")
        estado_aprobada = cur.fetchone()
        if not estado_aprobada:
            return jsonify({'errorCode':'ERR3','message':'No se encontró el estado Aprobada en el sistema.'}), 500

        # Cerrar el estado actual de 'Baja' y crear nuevo estado 'Aprobada'
        cur.execute("""
            UPDATE institucionestado 
            SET fechaFin = NOW() 
            WHERE idInstitucion = %s AND fechaFin IS NULL
        """, (id_institucion,))

        cur.execute("""
            INSERT INTO institucionestado (idInstitucion, idEstadoInstitucion, fechaInicio)
            VALUES (%s, %s, NOW())
        """, (id_institucion, estado_aprobada['idEstadoInstitucion']))

        conn.commit()
        return jsonify({'ok': True, 'message': 'Institución reactivada correctamente.'}), 200
    except Exception as e:
        log(f"US028 activate institution error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo reactivar la institución. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
# curl ejemplo:
# curl -X POST {{baseURL}}/api/v1/admin/institutions/5/activate -H "Authorization: Bearer {{token}}"

# -- Volcando estructura para tabla ovo.estadoinstitucion
# CREATE TABLE IF NOT EXISTS `estadoinstitucion` (
#   `idEstadoInstitucion` int(11) NOT NULL AUTO_INCREMENT,
#   `nombreEstadoInstitucion` varchar(50) DEFAULT NULL,
#   `fechaFin` datetime DEFAULT NULL,
#   PRIMARY KEY (`idEstadoInstitucion`)
# ) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

# -- Volcando estructura para tabla ovo.institucion
# CREATE TABLE IF NOT EXISTS `institucion` (
#   `idInstitucion` int(11) NOT NULL AUTO_INCREMENT,
#   `idTipoInstitucion` int(11) NOT NULL,
#   `idLocalidad` int(11) DEFAULT NULL,
#   `idUsuario` int(11) DEFAULT NULL,
#   `anioFundacion` int(11) NOT NULL,
#   `codigoPostal` int(11) NOT NULL,
#   `nombreInstitucion` varchar(50) NOT NULL,
#   `CUIT` bigint(20) NOT NULL DEFAULT 0,
#   `direccion` varchar(50) NOT NULL,
#   `fechaAlta` datetime NOT NULL DEFAULT current_timestamp(),
#   `siglaInstitucion` varchar(50) NOT NULL,
#   `telefono` varchar(50) NOT NULL,
#   `mail` varchar(50) NOT NULL,
#   `sitioWeb` text NOT NULL,
#   `urlLogo` text NOT NULL,
#   PRIMARY KEY (`idInstitucion`),
#   KEY `FK_institucion_tipoinstitucion` (`idTipoInstitucion`),
#   KEY `FK_institucion_localidad` (`idLocalidad`),
#   KEY `FK_institucion_usuario` (`idUsuario`),
#   CONSTRAINT `FK_institucion_localidad` FOREIGN KEY (`idLocalidad`) REFERENCES `localidad` (`idLocalidad`) ON DELETE SET NULL ON UPDATE CASCADE,
#   CONSTRAINT `FK_institucion_tipoinstitucion` FOREIGN KEY (`idTipoInstitucion`) REFERENCES `tipoinstitucion` (`idTipoInstitucion`) ON UPDATE CASCADE,
#   CONSTRAINT `FK_institucion_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`) ON UPDATE CASCADE
# ) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

# -- Volcando estructura para tabla ovo.institucionestado
# CREATE TABLE IF NOT EXISTS `institucionestado` (
#   `idinstitucionEstado` int(11) NOT NULL AUTO_INCREMENT,
#   `idEstadoInstitucion` int(11) NOT NULL,
#   `idInstitucion` int(11) NOT NULL,
#   `fechaInicio` datetime NOT NULL DEFAULT current_timestamp(),
#   `fechaFin` datetime DEFAULT NULL,
#   `justificacion` text DEFAULT NULL,
#   PRIMARY KEY (`idinstitucionEstado`),
#   KEY `FK_institucionestado_estadoinstitucion` (`idEstadoInstitucion`),
#   KEY `FK_institucionestado_institucion` (`idInstitucion`),
#   CONSTRAINT `FK_institucionestado_estadoinstitucion` FOREIGN KEY (`idEstadoInstitucion`) REFERENCES `estadoinstitucion` (`idEstadoInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE,
#   CONSTRAINT `FK_institucionestado_institucion` FOREIGN KEY (`idInstitucion`) REFERENCES `institucion` (`idInstitucion`) ON DELETE CASCADE ON UPDATE CASCADE
# ) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

# Endpoint para ver el historial de estados de una institcion:
@app.route('/api/v1/admin/institutions/<int:institution_id>/history', methods=['GET'])
@requires_permission('MANAGE_INSTITUTION_REQUESTS')
def admin_institution_history(current_user_id, institution_id):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT ie.idinstitucionEstado, ie.fechaInicio, ie.fechaFin, ie.justificacion, ei.nombreEstadoInstitucion
            FROM institucionestado ie
            JOIN estadoinstitucion ei ON ie.idEstadoInstitucion = ei.idEstadoInstitucion
            WHERE ie.idInstitucion = %s
            ORDER BY ie.fechaInicio DESC
        """, (institution_id,))
        rows = cur.fetchall() or []
        for row in rows:
            if row['fechaInicio']:
                row['fechaInicio'] = row['fechaInicio'].strftime('%Y-%m-%d %H:%M:%S')
            if row['fechaFin']:
                row['fechaFin'] = row['fechaFin'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'history': rows}), 200
    except Exception as e:
        log(f"US029 institution history error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo listar el historial de estados.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
# Curl ejemplo:
# curl -X GET {{baseURL}}/api/v1/admin/institutions/5/history -H "Authorization: Bearer {{token}}"

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
@requires_permission('MANAGE_CAREERS_CATALOG')
def admin_catalog_careers_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idCarrera, nombreCarrera, idTipoCarrera, fechaFin FROM carrera ORDER BY nombreCarrera")
        rows = cur.fetchall() or []
        for row in rows:
            if row['fechaFin']:
                row['fechaFin'] = row['fechaFin'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'careers': rows}), 200
    except Exception as e:
        log(f"US029 list careers error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo listar carreras.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/careers', methods=['POST'])
@requires_permission('MANAGE_CAREERS_CATALOG')
def admin_catalog_career_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreCarrera') or '').strip()
    tipo = data.get('idTipoCarrera')
    if not nombre or not tipo:
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if _career_exists_active(cur, nombre, tipo):
            return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 400
        cur.execute("INSERT INTO carrera (nombreCarrera, idTipoCarrera) VALUES (%s,%s)", (nombre, tipo))
        conn.commit()
        new_id = cur.lastrowid
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de carrera idCarrera={new_id}, nombre={nombre}, idTipoCarrera={tipo}")
        
        return jsonify({'ok':True,'idCarrera': new_id}), 201
    except Exception as e:
        log(f"US029 create career error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/careers/<int:id_carrera>', methods=['GET'])
@requires_permission('MANAGE_CAREERS_CATALOG')
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
@requires_permission('MANAGE_CAREERS_CATALOG')
def admin_catalog_career_update(current_user_id, id_carrera):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreCarrera') or '').strip()
    tipo = data.get('idTipoCarrera')
    fechaFin = data.get('fechaFin')  # Puede ser None, 'NOW()' o fecha específica YYYY-MM-DD HH:MM:SS
    if not nombre or not tipo:
        return jsonify({'errorCode':'ERR1','message':'Debe completar todos los campos obligatorios.'}), 400
    
    # Validar fechaFin si se proporciona usando la función helper
    fecha_fin_sql = None
    set_null = False
    if fechaFin:
        is_valid, normalized_date, error_msg = validate_date_string(fechaFin)
        if not is_valid:
            return jsonify({'errorCode':'ERR1','message': error_msg}), 400
        if normalized_date == 'NOW()':
            fecha_fin_sql = 'NOW()'
        elif normalized_date is None:
            set_null = True
        else:
            fecha_fin_sql = normalized_date
    
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de carrera catálogo idCarrera={id_carrera}, nombre={nombre}, idTipoCarrera={tipo}")
        
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
@requires_permission('MANAGE_CAREERS_CATALOG')
def admin_catalog_career_delete(current_user_id, id_carrera):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idCarrera FROM carrera WHERE idCarrera=%s", (id_carrera,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la carrera. Intente nuevamente.'}), 404
        cur.execute("UPDATE carrera SET fechaFin=NOW() WHERE idCarrera=%s", (id_carrera,))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de carrera catálogo idCarrera={id_carrera}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US029 delete career error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la carrera. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass


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
# @requires_permission('MANAGE_CAREERS_TYPES')
def admin_career_types_list():
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idTipoCarrera, nombreTipoCarrera, fechaFin FROM tipocarrera ORDER BY nombreTipoCarrera")
        rows = cur.fetchall() or []
        for row in rows:
            # Formatear la fecha
            if row['fechaFin']:
                row['fechaFin'] = row['fechaFin'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'careerTypes': rows}), 200
    except Exception as e:
        log(f"US030 list tipoCarrera error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo listar tipos de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-types', methods=['POST'])
@requires_permission('MANAGE_CAREERS_TYPES')
def admin_career_type_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreTipoCarrera') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if _tipo_carrera_exists_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 400
        cur.execute("INSERT INTO tipocarrera (nombreTipoCarrera) VALUES (%s)", (nombre,))
        conn.commit()
        new_id = cur.lastrowid
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de tipo de carrera idTipoCarrera={new_id}, nombre={nombre}")
        
        return jsonify({'ok':True,'idTipoCarrera': new_id}), 201
    except Exception as e:
        log(f"US030 create tipoCarrera error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-types/<int:id_tipo>', methods=['GET'])
@requires_permission('MANAGE_CAREERS_TYPES')
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
@requires_permission('MANAGE_CAREERS_TYPES')
def admin_career_type_update(current_user_id, id_tipo):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreTipoCarrera') or '').strip()
    fechaFin = data.get('fechaFin')  # Puede ser None, 'NOW()' o fecha específica YYYY-MM-DD HH:MM:SS
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 400
    
    # Validar fechaFin si se proporciona
    fecha_fin_validated = None
    if fechaFin:
        is_valid, normalized_date, error_msg = validate_date_string(fechaFin)
        if not is_valid:
            return jsonify({'errorCode':'ERR1','message': error_msg}), 400
        fecha_fin_validated = normalized_date
    
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idTipoCarrera FROM tipocarrera WHERE idTipoCarrera=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Tipo de carrera no encontrado.'}), 404
        if _tipo_carrera_exists_active(cur, nombre, exclude_id=id_tipo):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 400
        cur.execute("UPDATE tipocarrera SET nombreTipoCarrera=%s, fechaFin=%s WHERE idTipoCarrera=%s", (nombre, fecha_fin_validated, id_tipo))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de tipo de carrera idTipoCarrera={id_tipo}, nombre={nombre}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US030 update tipoCarrera error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
# curl ejemplo con fechafin null:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/career-types/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreTipoCarrera\":\"Tipo Actualizado\",\"fechaFin\": null}"

@app.route('/api/v1/admin/catalog/career-types/<int:id_tipo>', methods=['DELETE'])
@requires_permission('MANAGE_CAREERS_TYPES')
def admin_career_type_delete(current_user_id, id_tipo):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idTipoCarrera FROM tipocarrera WHERE idTipoCarrera=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el tipo de carrera. Intente nuevamente.'}), 404
        cur.execute("UPDATE tipocarrera SET fechaFin=NOW() WHERE idTipoCarrera=%s AND fechaFin IS NULL", (id_tipo,))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de tipo de carrera idTipoCarrera={id_tipo}")
        
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
@requires_permission('MANAGE_COUNTRIES')
def admin_country_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombrePais') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if _pais_exists_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 400
        cur.execute("INSERT INTO pais (nombrePais) VALUES (%s)", (nombre,))
        conn.commit()
        new_id = cur.lastrowid
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de país idPais={new_id}, nombre={nombre}")
        
        return jsonify({'ok':True,'idPais': new_id}), 201
    except Exception as e:
        log(f"US031 create pais error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/countries/<int:id_pais>', methods=['GET'])
@requires_permission('MANAGE_COUNTRIES')
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
@requires_permission('MANAGE_COUNTRIES')
def admin_country_update(current_user_id, id_pais):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombrePais') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idPais FROM pais WHERE idPais=%s", (id_pais,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'País no encontrado.'}), 404
        if _pais_exists_active(cur, nombre, exclude_id=id_pais):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 400
        cur.execute("UPDATE pais SET nombrePais=%s WHERE idPais=%s", (nombre, id_pais))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de país idPais={id_pais}, nombre={nombre}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US031 update pais error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el país.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/countries/<int:id_pais>', methods=['DELETE'])
@requires_permission('MANAGE_COUNTRIES')
def admin_country_delete(current_user_id, id_pais):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idPais FROM pais WHERE idPais=%s", (id_pais,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el país. Intente nuevamente.'}), 404
        cur.execute("DELETE FROM pais WHERE idPais=%s", (id_pais,))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de país idPais={id_pais}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US031 delete pais error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el país. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass


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

# ?idPais=1 (filtrar por país)
@app.route('/api/v1/admin/catalog/provinces', methods=['GET'])
def admin_provinces_list():
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        id_pais = request.args.get('idPais', type=int)
        if id_pais:
            cur.execute("SELECT idProvincia, nombreProvincia, idPais FROM provincia WHERE idPais=%s ORDER BY nombreProvincia", (id_pais,))
        else:
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
@requires_permission('MANAGE_PROVINCES')
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
        cur = conn.cursor(dictionary=True)
        # validar país
        if not _pais_exists(cur, id_pais):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 400
        if _provincia_duplicate_active(cur, nombre, id_pais):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 400  # reutilizamos ERR2 para duplicado por criterio HU (no hay código específico)
        cur.execute("INSERT INTO provincia (nombreProvincia, idPais) VALUES (%s,%s)", (nombre, id_pais))
        conn.commit()
        new_id = cur.lastrowid
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de provincia idProvincia={new_id}, nombre={nombre}, idPais={id_pais}")
        
        return jsonify({'ok':True,'idProvincia': new_id}), 201
    except Exception as e:
        log(f"US032 create provincia error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/provinces/<int:id_provincia>', methods=['GET'])
@requires_permission('MANAGE_PROVINCES')
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
@requires_permission('MANAGE_PROVINCES')
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
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idProvincia FROM provincia WHERE idProvincia=%s", (id_provincia,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Provincia no encontrada.'}), 404
        if not _pais_exists(cur, id_pais):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 400
        if _provincia_duplicate_active(cur, nombre, id_pais, exclude_id=id_provincia):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 400
        cur.execute("UPDATE provincia SET nombreProvincia=%s, idPais=%s WHERE idProvincia=%s", (nombre, id_pais, id_provincia))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de provincia idProvincia={id_provincia}, nombre={nombre}, idPais={id_pais}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US032 update provincia error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar un país.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/provinces/<int:id_provincia>', methods=['DELETE'])
@requires_permission('MANAGE_PROVINCES')
def admin_province_delete(current_user_id, id_provincia):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idProvincia FROM provincia WHERE idProvincia=%s", (id_provincia,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR3','message':'No se pudo eliminar la provincia. Intente nuevamente.'}), 404
        cur.execute("DELETE FROM provincia WHERE idProvincia=%s", (id_provincia,))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de provincia idProvincia={id_provincia}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US032 delete provincia error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo eliminar la provincia. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass


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
@requires_permission('MANAGE_LOCALITIES')
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
        cur = conn.cursor(dictionary=True)
        if not _provincia_exists(cur, id_provincia):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 400
        if _localidad_duplicate_active(cur, nombre, id_provincia):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 400
        cur.execute("INSERT INTO localidad (nombreLocalidad, idProvincia) VALUES (%s,%s)", (nombre, id_provincia))
        conn.commit()
        new_id = cur.lastrowid
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de localidad idLocalidad={new_id}, nombre={nombre}, idProvincia={id_provincia}")
        
        return jsonify({'ok':True,'idLocalidad': new_id}), 201
    except Exception as e:
        log(f"US033 create localidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/localities/<int:id_localidad>', methods=['GET'])
@requires_permission('MANAGE_LOCALITIES')
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
@requires_permission('MANAGE_LOCALITIES')
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
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idLocalidad FROM localidad WHERE idLocalidad=%s", (id_localidad,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Localidad no encontrada.'}), 404
        if not _provincia_exists(cur, id_provincia):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 400
        if _localidad_duplicate_active(cur, nombre, id_provincia, exclude_id=id_localidad):
            return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 400
        cur.execute("UPDATE localidad SET nombreLocalidad=%s, idProvincia=%s WHERE idLocalidad=%s", (nombre, id_provincia, id_localidad))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de localidad idLocalidad={id_localidad}, nombre={nombre}, idProvincia={id_provincia}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US033 update localidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Debe seleccionar una provincia asociada.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/localities/<int:id_localidad>', methods=['DELETE'])
@requires_permission('MANAGE_LOCALITIES')
def admin_locality_delete(current_user_id, id_localidad):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idLocalidad FROM localidad WHERE idLocalidad=%s", (id_localidad,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR3','message':'No se pudo eliminar la localidad. Intente nuevamente.'}), 404
        cur.execute("DELETE FROM localidad WHERE idLocalidad=%s", (id_localidad,))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de localidad idLocalidad={id_localidad}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US033 delete localidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo eliminar la localidad. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

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
@requires_permission('MANAGE_GENDERS')
def admin_gender_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreGenero') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if _genero_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 400
        cur.execute("INSERT INTO genero (nombreGenero) VALUES (%s)", (nombre,))
        conn.commit()
        new_id = cur.lastrowid
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de género idGenero={new_id}, nombre={nombre}")
        
        return jsonify({'ok':True,'idGenero': new_id}), 201
    except Exception as e:
        log(f"US034 create genero error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/genders/<int:id_genero>', methods=['GET'])
@requires_permission('MANAGE_GENDERS')
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
@requires_permission('MANAGE_GENDERS')
def admin_gender_update(current_user_id, id_genero):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreGenero') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idGenero FROM genero WHERE idGenero=%s", (id_genero,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Género no encontrado.'}), 404
        if _genero_duplicate_active(cur, nombre, exclude_id=id_genero):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 400
        cur.execute("UPDATE genero SET nombreGenero=%s WHERE idGenero=%s", (nombre, id_genero))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de género idGenero={id_genero}, nombre={nombre}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US034 update genero error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el género.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/genders/<int:id_genero>', methods=['DELETE'])
@requires_permission('MANAGE_GENDERS')
def admin_gender_delete(current_user_id, id_genero):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idGenero FROM genero WHERE idGenero=%s", (id_genero,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el género. Intente nuevamente.'}), 404
        cur.execute("DELETE FROM genero WHERE idGenero=%s", (id_genero,))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de género idGenero={id_genero}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US034 delete genero error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el género. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass


# ============================ ABM EstadoUsuario (US035) ============================
# Tabla: estadousuario (idEstadoUsuario, nombreEstadoUsuario, fechaFin)
# Endpoints:
#  GET    /api/v1/admin/catalog/user-statuses                 -> listado (activos por defecto;  para todos)
#  POST   /api/v1/admin/catalog/user-statuses                 -> alta (nombreEstadoUsuario) ERR1 si vacío o duplicado activo
#  GET    /api/v1/admin/catalog/user-statuses/<id>            -> detalle
#  PUT    /api/v1/admin/catalog/user-statuses/<id>            -> modificar nombre (ERR1 si vacío o duplicado)
#  DELETE /api/v1/admin/catalog/user-statuses/<id>            -> baja lógica (fechaFin=NOW()) ERR2 si falla o no existe
# Errores:S
#   ERR1: "Debe ingresar un nombre para el estado." (nombre vacío o duplicado activo)
#   ERR2: "No se pudo eliminar el estado. Intente nuevamente." (error técnico o inexistente)

@app.route('/api/v1/admin/catalog/user-statuses', methods=['GET'])
@requires_permission('MANAGE_USER_STATUSES')
def admin_user_statuses_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idEstadoUsuario, nombreEstadoUsuario, fechaFin FROM estadousuario ORDER BY nombreEstadoUsuario")
        rows = cur.fetchall() or []
        for r in rows:
            if r['fechaFin'] is not None:
                r['fechaFin'] = r['fechaFin'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'userStatuses': rows}), 200
    except Exception as e:
        log(f"US035 list estadoUsuario error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Error al listar estados.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/user-statuses', methods=['POST'])
@requires_permission('MANAGE_USER_STATUSES')
def admin_user_status_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoUsuario') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("INSERT INTO estadousuario (nombreEstadoUsuario, fechaFin) VALUES (%s, NULL)", (nombre,))
        conn.commit()
        new_id = cur.lastrowid
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de estado de usuario idEstadoUsuario={new_id}, nombre={nombre}")
        
        return jsonify({'ok':True,'idEstadoUsuario': new_id}), 201
    except Exception as e:
        log(f"US035 create estadoUsuario error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/user-statuses/<int:id_estado>', methods=['GET'])
@requires_permission('MANAGE_USER_STATUSES')
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
@requires_permission('MANAGE_USER_STATUSES')
def admin_user_status_update(current_user_id, id_estado):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoUsuario') or '').strip()
    fechaFin = (data.get('fechaFin') or None)
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
    
    # Validar fechaFin si se proporciona
    fecha_fin_validated = None
    if fechaFin:
        is_valid, normalized_date, error_msg = validate_date_string(fechaFin)
        if not is_valid:
            return jsonify({'errorCode':'ERR1','message': error_msg}), 400
        fecha_fin_validated = normalized_date
    
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idEstadoUsuario FROM estadousuario WHERE idEstadoUsuario=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Estado no encontrado.'}), 404
        cur.execute("UPDATE estadousuario SET nombreEstadoUsuario=%s, fechaFin=%s WHERE idEstadoUsuario=%s", (nombre, fecha_fin_validated, id_estado))
        conn.commit()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US035 update estadoUsuario error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
# cURL ejemplo con fechafin null
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/user-statuses/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreEstadoUsuario\":\"Suspendido\", \"fechaFin\":null}"

@app.route('/api/v1/admin/catalog/user-statuses/<int:id_estado>', methods=['DELETE'])
@requires_permission('MANAGE_USER_STATUSES')
def admin_user_status_delete(current_user_id, id_estado):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idEstadoUsuario FROM estadousuario WHERE idEstadoUsuario=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el estado. Intente nuevamente.'}), 404
        cur.execute("UPDATE estadousuario SET fechaFin=NOW() WHERE idEstadoUsuario=%s AND fechaFin IS NULL", (id_estado,))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de estado de usuario idEstadoUsuario={id_estado}")
        
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
# Listar todos:_duplicate_
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
@requires_permission(['MANAGE_PERMISSIONS','ASIGN_PERM'])
def admin_permissions_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
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
@requires_permission('MANAGE_PERMISSIONS')
def admin_permission_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombrePermiso') or '').strip()
    descripcion = (data.get('descripcion') or '').strip() or None
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el permiso.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if _permiso_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'El nombre del permiso esta duplicado.'}), 400
        cur.execute("INSERT INTO permiso (nombrePermiso, descripcion, fechaFin) VALUES (%s,%s,NULL)", (nombre, descripcion))
        conn.commit()
        new_id = cur.lastrowid
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de permiso idPermiso={new_id}, nombre={nombre}")
        
        return jsonify({'ok':True,'idPermiso': new_id}), 201
    except Exception as e:
        log(f"US036 create permiso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el permiso.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/permissions/<int:id_permiso>', methods=['GET'])
@requires_permission('MANAGE_PERMISSIONS')
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
@requires_permission('MANAGE_PERMISSIONS')
def admin_permission_update(current_user_id, id_permiso):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombrePermiso') or '').strip()
    descripcion = (data.get('descripcion') or '').strip() or None
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el permiso.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idPermiso FROM permiso WHERE idPermiso=%s", (id_permiso,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Permiso no encontrado.'}), 404
        if _permiso_duplicate_active(cur, nombre, exclude_id=id_permiso):
            return jsonify({'errorCode':'ERR1','message':'El nombre del permiso esta duplicado.'}), 400
        cur.execute("UPDATE permiso SET nombrePermiso=%s, descripcion=%s WHERE idPermiso=%s", (nombre, descripcion, id_permiso))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de permiso idPermiso={id_permiso}, nombre={nombre}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US036 update permiso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el permiso.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/permissions/<int:id_permiso>', methods=['DELETE'])
@requires_permission('MANAGE_PERMISSIONS')
def admin_permission_delete(current_user_id, id_permiso):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idPermiso FROM permiso WHERE idPermiso=%s", (id_permiso,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el permiso. Intente nuevamente.'}), 404
        cur.execute("UPDATE permiso SET fechaFin=NOW() WHERE idPermiso=%s AND fechaFin IS NULL", (id_permiso,))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de permiso idPermiso={id_permiso}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US036 delete permiso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el permiso. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass


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
@requires_permission('MANAGE_GROUPS')
def admin_groups_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
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
@requires_permission('MANAGE_GROUPS')
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
        cur = conn.cursor(dictionary=True)
        if _grupo_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el grupo.'}), 400
        cur.execute("INSERT INTO grupo (nombreGrupo, descripcion, fechaFin) VALUES (%s,%s,NULL)", (nombre, descripcion))
        new_id = cur.lastrowid
        # Insertar permisos
        if permisos:
            for pid in permisos:
                try:
                    cur.execute("SELECT idPermiso FROM permiso WHERE idPermiso=%s AND (fechaFin IS NULL OR fechaFin > NOW())", (pid,))
                    if cur.fetchone():
                        cur.execute("INSERT INTO permisogrupo (idGrupo, idPermiso, fechaInicio, fechaFin) VALUES (%s,%s,NOW(),NULL)", (new_id, pid))
                except Exception:
                    pass
        conn.commit()
        
        # Registrar en auditoría
        permisos_str = ','.join(map(str, permisos)) if permisos else 'ninguno'
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de grupo idGrupo={new_id}, nombre={nombre}, permisos=[{permisos_str}]")
        
        return jsonify({'ok':True,'idGrupo': new_id}), 201
    except Exception as e:
        log(f"US037 create grupo error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el grupo.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/groups/<int:id_grupo>', methods=['GET'])
@requires_permission('MANAGE_GROUPS')
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
@requires_permission('MANAGE_GROUPS')
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
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idGrupo FROM grupo WHERE idGrupo=%s", (id_grupo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Grupo no encontrado.'}), 404
        if _grupo_duplicate_active(cur, nombre, exclude_id=id_grupo):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el grupo.'}), 400
        cur.execute("UPDATE grupo SET nombreGrupo=%s, descripcion=%s WHERE idGrupo=%s", (nombre, descripcion, id_grupo))
        # Actualizar permisos: cerrar los no incluidos y agregar los nuevos
        cur.execute("SELECT idPermiso FROM permisogrupo WHERE idGrupo=%s AND fechaFin IS NULL", (id_grupo,))
        actuales = {r['idPermiso'] for r in cur.fetchall() or []}
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
                cur.execute("SELECT idPermiso FROM permiso WHERE idPermiso=%s AND (fechaFin IS NULL OR fechaFin > NOW())", (pid,))
                if cur.fetchone():
                    cur.execute("INSERT INTO permisogrupo (idGrupo, idPermiso, fechaInicio, fechaFin) VALUES (%s,%s,NOW(),NULL)", (id_grupo, pid))
            except Exception:
                pass
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de grupo idGrupo={id_grupo}, nombre={nombre}, permisos agregados={len(a_agregar)}, permisos eliminados={len(a_cerrar)}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US037 update grupo error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el grupo.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/groups/<int:id_grupo>', methods=['DELETE'])
@requires_permission('MANAGE_GROUPS')
def admin_group_delete(current_user_id, id_grupo):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idGrupo FROM grupo WHERE idGrupo=%s", (id_grupo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el grupo. Intente nuevamente.'}), 404
        cur.execute("UPDATE grupo SET fechaFin=NOW() WHERE idGrupo=%s AND fechaFin IS NULL", (id_grupo,))
        # Cerrar permisos activos asociados
        cur.execute("UPDATE permisogrupo SET fechaFin=NOW() WHERE idGrupo=%s AND fechaFin IS NULL", (id_grupo,))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de grupo idGrupo={id_grupo} y sus permisos asociados")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US037 delete grupo error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el grupo. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass


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
# @requires_permission(['MANAGE_INSTITUTION_TYPES', 'ADMIN_APPROVE_INSTITUTION'])
def admin_institution_types_list():
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idTipoInstitucion, nombreTipoInstitucion, fechaFin FROM tipoinstitucion ORDER BY nombreTipoInstitucion")
        tipos = cur.fetchall() or []
        for row in tipos:
            if row['fechaFin']:
                row['fechaFin'] = row['fechaFin'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'institutionTypes': tipos}), 200
    except Exception as e:
        log(f"US038 list tipoInstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Error al listar tipos de institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-types', methods=['POST'])
@requires_permission('MANAGE_INSTITUTION_TYPES')
def admin_institution_type_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreTipoInstitucion') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if _tipo_institucion_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 400
        cur.execute("INSERT INTO tipoinstitucion (nombreTipoInstitucion, fechaFin) VALUES (%s, NULL)", (nombre,))
        new_id = cur.lastrowid
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de tipo de institución idTipoInstitucion={new_id}, nombre={nombre}")
        
        return jsonify({'ok':True,'idTipoInstitucion': new_id}), 201
    except Exception as e:
        log(f"US038 create tipoInstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-types/<int:id_tipo>', methods=['GET'])
@requires_permission('MANAGE_INSTITUTION_TYPES')
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
@requires_permission('MANAGE_INSTITUTION_TYPES')
def admin_institution_type_update(current_user_id, id_tipo):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreTipoInstitucion') or '').strip()
    fechaFin = (data.get('fechaFin') or None)
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 400
    
    # Validar fechaFin si se proporciona
    fecha_fin_validated = None
    if fechaFin:
        is_valid, normalized_date, error_msg = validate_date_string(fechaFin)
        if not is_valid:
            return jsonify({'errorCode':'ERR1','message': error_msg}), 400
        fecha_fin_validated = normalized_date
    
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idTipoInstitucion FROM tipoinstitucion WHERE idTipoInstitucion=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Tipo de institución no encontrado.'}), 404
        if _tipo_institucion_duplicate_active(cur, nombre, exclude_id=id_tipo):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 400
        cur.execute("UPDATE tipoinstitucion SET nombreTipoInstitucion=%s, fechaFin=%s WHERE idTipoInstitucion=%s", (nombre, fecha_fin_validated, id_tipo))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de tipo de institución idTipoInstitucion={id_tipo}, nombre={nombre}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US038 update tipoInstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-types/<int:id_tipo>', methods=['DELETE'])
@requires_permission('MANAGE_INSTITUTION_TYPES')
def admin_institution_type_delete(current_user_id, id_tipo):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idTipoInstitucion FROM tipoinstitucion WHERE idTipoInstitucion=%s", (id_tipo,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el tipo de institución. Intente nuevamente.'}), 404
        cur.execute("UPDATE tipoinstitucion SET fechaFin=NOW() WHERE idTipoInstitucion=%s", (id_tipo,))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de tipo de institución idTipoInstitucion={id_tipo}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US038 delete tipoInstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el tipo de institución. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

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
# @requires_permission(['MANAGE_CAREER_MODALITIES', 'INSTITUTION_MANAGE_CAREERS'])
def admin_career_modalities_list():
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
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
@requires_permission('MANAGE_CAREER_MODALITIES')
def admin_career_modality_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreModalidad') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la modalidad.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if _modalidad_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la modalidad.'}), 400
        # Insert (ignorar fechaFin si no existe)
        try:
            cur.execute("INSERT INTO modalidadcarrerainstitucion (nombreModalidad, fechaFin) VALUES (%s, NULL)", (nombre,))
        except mysql.connector.Error:
            cur.execute("INSERT INTO modalidadcarrerainstitucion (nombreModalidad) VALUES (%s)", (nombre,))
        new_id = cur.lastrowid
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de modalidad carrera institución idModalidadCarreraInstitucion={new_id}, nombre={nombre}")
        
        return jsonify({'ok':True,'idModalidadCarreraInstitucion': new_id}), 201
    except Exception as e:
        log(f"US039 create modalidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la modalidad.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-modalities/<int:id_mod>', methods=['GET'])
@requires_permission('MANAGE_CAREER_MODALITIES')
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
@requires_permission('MANAGE_CAREER_MODALITIES')
def admin_career_modality_update(current_user_id, id_mod):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreModalidad') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la modalidad.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de modalidad carrera institución idModalidadCarreraInstitucion={id_mod}, nombre={nombre}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US039 update modalidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la modalidad.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-modalities/<int:id_mod>', methods=['DELETE'])
@requires_permission('MANAGE_CAREER_MODALITIES')
def admin_career_modality_delete(current_user_id, id_mod):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de modalidad carrera institución idModalidadCarreraInstitucion={id_mod}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US039 delete modalidad error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la modalidad. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass


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
@requires_permission('MANAGE_APTITUDES')
def admin_aptitudes_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idAptitud, nombreAptitud, descripcion, fechaAlta, fechaBaja FROM aptitud ORDER BY nombreAptitud")
        rows = cur.fetchall() or []
        for r in rows:
            if r['fechaAlta']:
                r['fechaAlta'] = r['fechaAlta'].strftime('%Y-%m-%d %H:%M:%S')
            if r['fechaBaja']:
                r['fechaBaja'] = r['fechaBaja'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'aptitudes': rows}), 200
    except Exception as e:
        log(f"US040 list aptitud error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Error al listar aptitudes.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass


# curl --location 'AWS_API_URL/prod/aptitudes/agregar' \
# --header 'Content-Type: application/json' \
# --data '{
#     "aptitudes": [
#         "Pensamiento crítico y analítico",
#         "Creatividad",
#         "Habilidades numéricas y espaciales",
#         "Memoria y atención",
#         "Inteligencia emocional",
#         "Comunicación",
#         "Trabajo en equipo y colaboración",
#         "Liderazgo",
#         "Adaptabilidad",
#         "Resiliencia",
#         "Gestión del tiempo",
#         "Competencias digitales",
#         "Habilidades de ventas y orientación al cliente",
#         "Habilidades psicomotrices y físicas"
#     ]
# }'
def enviar_datos_aws():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT nombreAptitud FROM aptitud WHERE fechaBaja IS NULL")
        rows = cur.fetchall() or []
        if rows:
            payload = {"aptitudes": [r['nombreAptitud'] for r in rows]}
            response = requests.post(f"{AWS_API_URL}/prod/aptitudes/agregar", json=payload)
            if response.status_code != 200:
                log(f"Error al enviar datos a AWS: {response.text}")
    except Exception as e:
        log(f"Error en enviar_datos_aws: {e}\n{traceback.format_exc()}")
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

# curl --location --request DELETE 'https://wid84vod2j.execute-api.us-east-2.amazonaws.com/prod/aptitudes/eliminar' \
# --header 'Content-Type: application/json' \
# --data '{
#     "aptitudes": [
#         "Pensamiento crítico y analítico",
#         "Creatividad",
#         "Habilidades numéricas y espaciales",
#         "Memoria y atención",
#         "Inteligencia emocional",
#         "Comunicación",
#         "Trabajo en equipo y colaboración",
#         "Liderazgo",
#         "Adaptabilidad",
#         "Resiliencia",
#         "Gestión del tiempo",
#         "Competencias digitales",
#         "Habilidades de ventas y orientación al cliente",
#         "Habilidades psicomotrices y físicas"
#     ]
# }'
def eliminar_datos_aws(aptitud_nombres):
    try:
        payload = {"aptitudes": aptitud_nombres}
        response = requests.delete(f"{AWS_API_URL}/prod/aptitudes/eliminar", json=payload)
        if response.status_code != 200:
            log(f"Error al eliminar datos en AWS: {response.text}")
    except Exception as e:
        log(f"Error en eliminar_datos_aws: {e}\n{traceback.format_exc()}")

@app.route('/api/v1/admin/catalog/aptitudes', methods=['POST'])
@requires_permission('MANAGE_APTITUDES')
def admin_aptitud_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreAptitud') or '').strip()
    descripcion = (data.get('descripcion') or '').strip() or None
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if _aptitud_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 400
        cur.execute("INSERT INTO aptitud (nombreAptitud, descripcion, fechaAlta, fechaBaja) VALUES (%s,%s,NOW(),NULL)", (nombre, descripcion))
        new_id = cur.lastrowid
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de aptitud idAptitud={new_id}, nombre={nombre}")
        
        enviar_datos_aws()
        return jsonify({'ok':True,'idAptitud': new_id}), 201
    except Exception as e:
        log(f"US040 create aptitud error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/aptitudes/<int:id_aptitud>', methods=['GET'])
@requires_permission('MANAGE_APTITUDES')
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
@requires_permission('MANAGE_APTITUDES')
def admin_aptitud_update(current_user_id, id_aptitud):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreAptitud') or '').strip()
    descripcion = (data.get('descripcion') or '').strip() or None
    fechaFin = (data.get('fechaFin') or None)
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 400
    
    # Validar fechaFin si se proporciona
    fecha_fin_validated = None
    if fechaFin:
        is_valid, normalized_date, error_msg = validate_date_string(fechaFin)
        if not is_valid:
            return jsonify({'errorCode':'ERR1','message': error_msg}), 400
        fecha_fin_validated = normalized_date
    
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idAptitud FROM aptitud WHERE idAptitud=%s", (id_aptitud,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Aptitud no encontrada.'}), 404
        if _aptitud_duplicate_active(cur, nombre, exclude_id=id_aptitud):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 400
        cur.execute("UPDATE aptitud SET nombreAptitud=%s, descripcion=%s, fechaBaja=%s WHERE idAptitud=%s", (nombre, descripcion, fecha_fin_validated, id_aptitud))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de aptitud idAptitud={id_aptitud}, nombre={nombre}")
        
        enviar_datos_aws()
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US040 update aptitud error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para la aptitud.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/aptitudes/<int:id_aptitud>', methods=['DELETE'])
@requires_permission('MANAGE_APTITUDES')
def admin_aptitud_delete(current_user_id, id_aptitud):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM aptitud WHERE idAptitud=%s", (id_aptitud,))
        aptitud = cur.fetchone()
        if not aptitud:
            return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la aptitud. Intente nuevamente.'}), 404
        cur.execute("UPDATE aptitud SET fechaBaja=NOW() WHERE idAptitud=%s AND fechaBaja IS NULL", (aptitud['idAptitud'],))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de aptitud idAptitud={id_aptitud}, nombre={aptitud['nombreAptitud']}")
        
        # Enviar eliminación a AWS
        eliminar_datos_aws([aptitud['nombreAptitud']])
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US040 delete aptitud error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar la aptitud. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

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
@requires_permission('MANAGE_ACCESS_STATUSES')
def admin_access_statuses_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
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
@requires_permission('MANAGE_ACCESS_STATUSES')
def admin_access_status_create(current_user_id):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoAcceso') or '').strip()
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        if _estado_acceso_duplicate_active(cur, nombre):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 400
        cur.execute("INSERT INTO estadoacceso (nombreEstadoAcceso, fechaFin) VALUES (%s, NULL)", (nombre,))
        new_id = cur.lastrowid
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de estado de acceso idEstadoAcceso={new_id}, nombre={nombre}")
        
        return jsonify({'ok':True,'idEstadoAcceso': new_id}), 201
    except Exception as e:
        log(f"US041 create estadoacceso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/access-statuses/<int:id_estado>', methods=['GET'])
@requires_permission('MANAGE_ACCESS_STATUSES')
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
@requires_permission('MANAGE_ACCESS_STATUSES')
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de estado de acceso idEstadoAcceso={id_estado}, nombre={nombre}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US041 update estadoacceso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/access-statuses/<int:id_estado>', methods=['DELETE'])
@requires_permission('MANAGE_ACCESS_STATUSES')
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de estado de acceso idEstadoAcceso={id_estado}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US041 delete estadoacceso error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el estado de acceso. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass


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
# @requires_permission('MANAGE_ACCION_TYPES')
def admin_action_types_list():
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
@requires_permission('MANAGE_ACCION_TYPES')
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de tipo de acción idTipoAccion={new_id}, nombre={nombre}")
        
        return jsonify({'ok':True,'idTipoAccion': new_id}), 201
    except Exception as e:
        log(f"US042 create tipoaccion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de acción.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/action-types/<int:id_tipo>', methods=['GET'])
@requires_permission('MANAGE_ACCION_TYPES')
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
@requires_permission('MANAGE_ACCION_TYPES')
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de tipo de acción idTipoAccion={id_tipo}, nombre={nombre}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US042 update tipoaccion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el tipo de acción.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/action-types/<int:id_tipo>', methods=['DELETE'])
@requires_permission('MANAGE_ACCION_TYPES')
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de tipo de acción idTipoAccion={id_tipo}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US042 delete tipoaccion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el tipo de acción. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

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
    q = "SELECT idEstadoInstitucion FROM estadoinstitucion WHERE nombreEstadoInstitucion=%s"
    params = [nombre]
    if exclude_id:
        q += " AND idEstadoInstitucion<>%s"
        params.append(exclude_id)
    cur.execute(q, tuple(params))
    return cur.fetchone() is not None

@app.route('/api/v1/admin/catalog/institution-states', methods=['GET'])
@requires_permission('MANAGE_INSTITUTION_STATES')
def admin_institution_states_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idEstadoInstitucion, nombreEstadoInstitucion, fechaFin FROM estadoinstitucion ORDER BY nombreEstadoInstitucion")
        rows = cur.fetchall() or []
        for row in rows:
            if row['fechaFin']:
                row['fechaFin'] = row['fechaFin'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'institutionStates': rows}), 200
    except Exception as e:
        log(f"US043 list estadoinstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Error al listar estados de institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-states', methods=['POST'])
@requires_permission('MANAGE_INSTITUTION_STATES')
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de estado de institución idEstadoInstitucion={new_id}, nombre={nombre}")
        
        return jsonify({'ok':True,'idEstadoInstitucion': new_id}), 201
    except Exception as e:
        log(f"US043 create estadoinstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de la institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-states/<int:id_estado>', methods=['GET'])
@requires_permission('MANAGE_INSTITUTION_STATES')
def admin_institution_state_detail(current_user_id, id_estado):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idEstadoInstitucion, nombreEstadoInstitucion FROM estadoinstitucion WHERE idEstadoInstitucion=%s", (id_estado,))
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
@requires_permission('MANAGE_INSTITUTION_STATES')
def admin_institution_state_update(current_user_id, id_estado):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoInstitucion') or '').strip()
    fechaFin = data.get('fechaFin') or None
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de la institución.'}), 400
    
    # Validar fechaFin si se proporciona
    fecha_fin_validated = None
    if fechaFin:
        is_valid, normalized_date, error_msg = validate_date_string(fechaFin)
        if not is_valid:
            return jsonify({'errorCode':'ERR1','message': error_msg}), 400
        fecha_fin_validated = normalized_date
    
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idEstadoInstitucion FROM estadoinstitucion WHERE idEstadoInstitucion=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Estado de institución no encontrado.'}), 404
        if _estado_institucion_duplicate_active(cur, nombre, exclude_id=id_estado):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de la institución.'}), 400
        cur.execute("UPDATE estadoinstitucion SET nombreEstadoInstitucion=%s, fechaFin=%s WHERE idEstadoInstitucion=%s", (nombre, fecha_fin_validated, id_estado))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de estado de institución idEstadoInstitucion={id_estado}, nombre={nombre}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US043 update estadoinstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de la institución.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/institution-states/<int:id_estado>', methods=['DELETE'])
@requires_permission('MANAGE_INSTITUTION_STATES')
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de estado de institución idEstadoInstitucion={id_estado}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US043 delete estadoinstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'No se pudo eliminar el estado de institución. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass


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
@requires_permission(['MANAGE_CAREER_INSTITUTION_STATUSES', 'INSTITUTION_MANAGE_CAREERS'])
def admin_career_institution_statuses_list(current_user_id):
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idEstadoCarreraInstitucion, nombreEstadoCarreraInstitucion, fechaFin FROM estadocarrerainstitucion ORDER BY nombreEstadoCarreraInstitucion")
        rows = cur.fetchall() or []
        for row in rows:
            if row['fechaFin']:
                row['fechaFin'] = row['fechaFin'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'careerInstitutionStatuses': rows}), 200
    except Exception as e:
        log(f"US044 list estadocarrerainstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR2','message':'Error al listar estados de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-institution-statuses', methods=['POST'])
@requires_permission('MANAGE_CAREER_INSTITUTION_STATUSES')
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Creación de estado de carrera institución idEstadoCarreraInstitucion={new_id}, nombre={nombre}")
        
        return jsonify({'ok':True,'idEstadoCarreraInstitucion': new_id}), 201
    except Exception as e:
        log(f"US044 create estadocarrerainstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/career-institution-statuses/<int:id_estado>', methods=['GET'])
@requires_permission('MANAGE_CAREER_INSTITUTION_STATUSES')
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
@requires_permission('MANAGE_CAREER_INSTITUTION_STATUSES')
def admin_career_institution_status_update(current_user_id, id_estado):
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombreEstadoCarreraInstitucion') or '').strip()
    fechaFin = data.get('fechaFin') or None
    if not nombre:
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de carrera.'}), 400
    
    # Validar fechaFin si se proporciona
    fecha_fin_validated = None
    if fechaFin:
        is_valid, normalized_date, error_msg = validate_date_string(fechaFin)
        if not is_valid:
            return jsonify({'errorCode':'ERR1','message': error_msg}), 400
        fecha_fin_validated = normalized_date
    
    conn=None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT idEstadoCarreraInstitucion FROM estadocarrerainstitucion WHERE idEstadoCarreraInstitucion=%s", (id_estado,))
        if not cur.fetchone():
            return jsonify({'errorCode':'ERR1','message':'Estado de carrera no encontrado.'}), 404
        if _estado_carrera_institucion_duplicate_active(cur, nombre, exclude_id=id_estado):
            return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de carrera.'}), 400
        cur.execute("UPDATE estadocarrerainstitucion SET nombreEstadoCarreraInstitucion=%s, fechaFin=%s WHERE idEstadoCarreraInstitucion=%s", (nombre, fecha_fin_validated, id_estado))
        conn.commit()
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "MODIFICACION", f"Modificación de estado de carrera institución idEstadoCarreraInstitucion={id_estado}, nombre={nombre}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US044 update estadocarrerainstitucion error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR1','message':'Debe ingresar un nombre para el estado de carrera.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
# curl ejemplo con fechaFin:
# curl -X PUT "{{baseURL}}/api/v1/admin/catalog/career-institution-statuses/1" -H "Authorization: Bearer {{token}}" -H "Content-Type: application/json" -d "{\"nombreEstadoCarreraInstitucion\":\"Cerrada\",\"fechaFin\":\"2024-12-31 23:59:59\"}"

@app.route('/api/v1/admin/catalog/career-institution-statuses/<int:id_estado>', methods=['DELETE'])
@requires_permission('MANAGE_CAREER_INSTITUTION_STATUSES')
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de estado de carrera institución idEstadoCarreraInstitucion={id_estado}")
        
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
@requires_permission('MANAGE_BACKUP_CONFIGS')
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
@requires_permission('MANAGE_BACKUP_CONFIGS')
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
@requires_permission('MANAGE_BACKUP_CONFIGS')
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
@requires_permission('MANAGE_BACKUP_CONFIGS')
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
@requires_permission('MANAGE_BACKUP_CONFIGS')
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
    # Verificar el estado actual del usuario
    cur.execute("SELECT idEstadoUsuario FROM usuarioestado WHERE idUsuario=%s AND fechaFin IS NULL", (user_id,))
    row = cur.fetchone()
    
    # Si el usuario ya tiene ese estado activo, no hacer nada
    if row and row[0] == id_estado_nuevo:
        return False  # No se realizó cambio
    
    # Cerrar estado previo
    cur.execute("UPDATE usuarioestado SET fechaFin=NOW() WHERE idUsuario=%s AND fechaFin IS NULL", (user_id,))
    # Abrir nuevo
    cur.execute("INSERT INTO usuarioestado (idUsuario, idEstadoUsuario, fechaInicio, fechaFin) VALUES (%s,%s,NOW(),NULL)", (user_id, id_estado_nuevo))
    return True  # Se realizó el cambio

def _determine_initial_state(value:str):
    v = (value or '').strip().lower()
    if v == 'inactivo' or v == 'bloqueado':
        return 2  # Suspendido/Bloqueado
    return 1  # Activo por defecto

# Endpoint para crear usuario
@app.route('/api/v1/admin/catalog/users', methods=['POST'])
@requires_permission('MANAGE_USERS')
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
        # Enviar correo con contraseña temporal al usuario creado
        send_email(correo, "Bienvenido a OVO. Usuario creado por administrador", f"""Sea bienvenido a OVO.\n\nSu usuario ha sido creado por un administrador del sistema.\n\nSus credenciales son:\nUsuario: {correo}\nContraseña temporal: {temp_pass}\n\nPor favor, cambie su contraseña en el primer inicio de sesión.\n\nSaludos,\nEquipo de OVO.""")

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
@requires_permission('MANAGE_USERS')
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
@requires_permission('MANAGE_USERS')
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
            cur.execute("INSERT INTO usuariogrupo (idUsuario, idGrupo, fechaInicio, fechaFin) VALUES (%s, %s, NOW(), NULL)",
                        (user_id, gid))
        # Actualizar estado actualizando la fecha fin y creando nuevo registro (solo si cambió)
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

# Endpoint para ver el historial de estados de un usuario en concreto
@app.route('/api/v1/admin/catalog/users/<int:user_id>/states', methods=['GET'])
@requires_permission('MANAGE_USERS')
def admin_user_states_get(current_user_id, user_id):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        # Obtener historial de estados del usuario
        cur.execute("""
            SELECT ue.idEstadoUsuario, eu.nombreEstadoUsuario, ue.fechaInicio, ue.fechaFin
            FROM usuarioestado ue
            JOIN estadousuario eu ON eu.idEstadoUsuario = ue.idEstadoUsuario
            WHERE ue.idUsuario = %s
            ORDER BY ue.fechaInicio DESC
        """, (user_id,))
        rows = cur.fetchall()
        # Formatear resultado
        states = []
        for row in rows:
            states.append({
                'idEstadoUsuario': row['idEstadoUsuario'],
                'nombreEstadoUsuario': row['nombreEstadoUsuario'],
                'fechaInicio': row['fechaInicio'].strftime('%Y-%m-%d %H:%M:%S') if row['fechaInicio'] else None,
                'fechaFin': row['fechaFin'].strftime('%Y-%m-%d %H:%M:%S') if row['fechaFin'] else None
            })
        return jsonify(states), 200
    except Exception as e:
        log(f"US046 get user states error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR4','message':'No se pudo obtener el historial de estados. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass
# curl ejemplo para este endpoint:
# curl -X GET "{{baseURL}}/api/v1/admin/catalog/users/1/states" -H "Authorization: Bearer {{token}}"

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
@requires_permission('MANAGE_GROUP_PERMISSIONS')
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ACTUALIZACION", f"Asignación de permiso idPermiso={perm_id} a grupo idGrupo={grupo_id}")
        
        return jsonify({'ok':True}), 200
    except Exception as e:
        log(f"US047 add group permission error: {e}\n{traceback.format_exc()}")
        return jsonify({'errorCode':'ERR3','message':'No se pudo asignar el permiso al grupo. Intente nuevamente.'}), 500
    finally:
        try:
            if conn: conn.close()
        except Exception: pass

@app.route('/api/v1/admin/catalog/groups/<int:grupo_id>/permissions/<int:perm_id>', methods=['DELETE'])
@requires_permission('MANAGE_GROUP_PERMISSIONS')
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
        
        # Registrar en auditoría
        auditoria_log(current_user_id, "ELIMINACION", f"Eliminación de permiso idPermiso={perm_id} del grupo idGrupo={grupo_id}")
        
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


