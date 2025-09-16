# Documentación de Endpoints Backend OVO

> Estado: muchas funciones aún no implementadas (stubs). Esta documentación se basa en los comentarios y nombres presentes en `main.py`. Ajustar cuando se codifique la lógica real.

## Convenciones Generales
- Autenticación: Header `Authorization: Bearer <token>`.
- Token especial de desarrollo: `Hola` (se acepta como autenticado pero sin validar pertenencias en algunos endpoints de test).
- JWT: Algoritmo HS256 con `SECRET_KEY`.
- Respuesta estándar sugerida: `{ "ok": true|false, "data"?: ..., "code"?: "ERR...", "message"?: "..." }`.
- Fechas de baja lógica: campos `fechaFin` / `fechaBaja`.

## Leyenda de Permisos Clave
| Permiso | Uso |
|---------|-----|
| ADMIN_PANEL | Acceso a panel admin y estadísticas avanzadas |
| LIST_USERS | Listar usuarios |
| LIST_GROUPS | Listar grupos |
| USER_GROUPS | Ver/editar grupos de un usuario |
| USER_PERMS | Ver/editar permisos directos de un usuario |
| LIST_PERMS | Listar permisos disponibles |
| USER_HISTORY | Acceder historial de accesos |

---

## US001 Autenticación
### POST `/api/v1/auth/login`
- Descripción: Login con email y password. Genera JWT.
- Auth: Pública.
- Errores esperados: `AUTH_INVALID`, `AUTH_DISABLED`, `PWD_INVALID`.

### POST `/api/v1/auth/google`
- Descripción: Login federado Google (stub).
- Auth: Pública.

### GET `/api/v1/auth/me`
- Descripción: Datos del usuario autenticado.
- Auth: Requiere JWT o token de prueba.

### POST `/api/v1/email`
- Descripción: Prueba de envío de correo.
- Auth: Pública (podría restringirse).

## US003 Gestión de Perfiles (Admin)
### GET `/api/v1/admin/users` (perm: LIST_USERS)
### GET `/api/v1/admin/groups` (perm: LIST_GROUPS)
### GET `/api/v1/admin/users/{user_id}/groups` (perm: USER_GROUPS)
### GET `/api/v1/admin/users/{user_id}/permissions` (perm: USER_PERMS)
### PUT `/api/v1/admin/users/{user_id}/group` (perm: USER_GROUPS)
### DELETE `/api/v1/admin/users/{user_id}/group/{id_grupo}` (perm: USER_GROUPS)
### POST `/api/v1/admin/users/{user_id}/permissions` (perm: USER_PERMS)
### DELETE `/api/v1/admin/users/{user_id}/permissions/{id_permiso}` (perm: USER_PERMS)

## US004 Permisos Dinámicos
### GET `/api/v1/admin/permissions` (perm: LIST_PERMS)
### PUT `/api/v1/admin/users/{user_id}/permissions` (perm: USER_PERMS)

## US005 Historial de Accesos
### GET `/api/v1/admin/access-history` (perm: USER_HISTORY)
### GET `/api/v1/admin/access-history/export` (perm: USER_HISTORY)

## US006 Auditoría
### GET `/api/v1/admin/audit` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/audit/export` (perm: ADMIN_PANEL)

## US007 Registro de Usuario
### POST `/api/v1/auth/register`
### POST `/api/v1/auth/register/google`

## US008 Baja Lógica Usuario
### POST `/api/v1/auth/deactivate` (auth requerida)

## US009 Recuperación de Contraseña
### POST `/api/v1/auth/password/forgot`
### POST `/api/v1/auth/password/reset`
### GET `/api/v1/auth/password/validate`

## US010 Preferencias (Intereses)
### GET `/api/v1/user/interests` (auth)
### DELETE `/api/v1/user/interests/{id_carrera_institucion}` (auth)
### POST `/api/v1/user/interests` (auth)

## US011 Histórico de Tests
### GET `/api/v1/user/tests` (auth)

## US012 Resultado de Test
### GET `/api/v1/user/tests/{id_test}/access` (auth)
### GET `/api/v1/user/tests/{id_test}/result`
- Reglas especiales según autenticación.

## US013 Reiniciar Cuestionario
### POST `/api/v1/user/tests/restart` (auth)

## US014 Carreras
### GET `/api/v1/careers` (búsqueda opcional `?search=`)
### GET `/api/v1/careers/{id_carrera}/institutions`
### GET `/api/v1/careers/{id_carrera}/institutions/{id_ci}`
### GET `/api/v1/careers/{id_ci}` (alias carrera-institución)
### POST `/api/v1/careers/{id_ci}/interest` (auth)

## US015 Instituciones
### GET `/api/v1/institutions` (filtros: search, tipo, tipoId, localidad, provincia, pais)
### GET `/api/v1/institutions/{id_institucion}`

## US016 Perfil Usuario
### GET `/api/v1/user/profile` (auth)
### PUT `/api/v1/user/profile` (auth)

## US017 Registro de Institución
### GET `/api/v1/institutions/registration/options`
### POST `/api/v1/institutions/registration`
- Errores: ERR1 campos*, ERR2 identificación inválida, ERR3 correo inválido.

## US018 Carreras por Institución (Representante)
### GET `/api/v1/institutions/me/careers` (auth)
### GET `/api/v1/institutions/me/careers/options` (auth)
### POST `/api/v1/institutions/me/careers` (auth)
### PUT `/api/v1/institutions/me/careers/{id_ci}` (auth)
### DELETE `/api/v1/institutions/me/careers/{id_ci}` (auth)

## US019 FAQ Carrera-Institución
### GET `/api/v1/institutions/me/careers/{id_ci}/faqs` (auth)
### POST `/api/v1/institutions/me/careers/{id_ci}/faqs` (auth)
### PUT `/api/v1/institutions/me/careers/{id_ci}/faqs/{id_faq}` (auth)
### DELETE `/api/v1/institutions/me/careers/{id_ci}/faqs/{id_faq}` (auth)

## US020 Material Complementario
### GET `/api/v1/institutions/me/careers/{id_ci}/materials` (auth)
### POST `/api/v1/institutions/me/careers/{id_ci}/materials` (auth)
### PUT `/api/v1/institutions/me/careers/{id_ci}/materials/{id_mat}` (auth)
### DELETE `/api/v1/institutions/me/careers/{id_ci}/materials/{id_mat}` (auth)
- Errores: ERR1 título vacío, ERR2 enlace inválido, ERR3 guardar, ERR4 eliminar.

## US021 Aptitudes por Carrera Base
### GET `/api/v1/institutions/me/careers/{id_ci}/aptitudes` (auth)
### PUT `/api/v1/institutions/me/careers/{id_ci}/aptitudes` (auth)
- Validaciones: ERR01 (>50), ERR02 (>=25 mín 3), ERR03 (≤3 con 99), ERR04 (no todos iguales), ERR05 (≤50% en 0).

## US022 Test (Runtime en memoria)
### POST `/api/v1/tests/start`
### POST `/api/v1/tests/{id_test}/answer`
### GET `/api/v1/tests/{id_test}/progress`
### POST `/api/v1/tests/{id_test}/pause`
### POST `/api/v1/tests/{id_test}/resume`
### POST `/api/v1/tests/{id_test}/save-exit`
### POST `/api/v1/tests/{id_test}/abandon`
### POST `/api/v1/tests/{id_test}/finish`

## US023 Tablero Estadísticas Sistema (Admin)
### GET `/api/v1/admin/stats/system` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/stats/system/export` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/stats/users` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/stats/users/export` (perm: ADMIN_PANEL)

## US024 Tablero Estadísticas Institución
### GET `/api/v1/institucion/stats/general` (auth)
### GET `/api/v1/institucion/stats/general/export` (auth)
### GET `/api/v1/institucion/stats/carreras` (auth)
### GET `/api/v1/institucion/stats/carrera/{idCarreraInstitucion}` (auth)
### GET `/api/v1/institucion/stats/carrera/{idCarreraInstitucion}/export` (auth)

## US025 Tablero Estadísticas Estudiante
### GET `/api/v1/estudiante/stats/perfil` (auth)
### GET `/api/v1/estudiante/stats/perfil/export` (auth)
### GET `/api/v1/estudiante/stats/compatibilidad` (auth)
### GET `/api/v1/estudiante/stats/compatibilidad/export` (auth)

## US026 Configuración Backups (Admin)
### GET `/api/v1/admin/backup/config` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/backup/config` (perm: ADMIN_PANEL)

## US027 Restauración Backups (Admin)
### GET `/api/v1/admin/backup/list` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/backup/restore` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/backup/restore/status` (perm: ADMIN_PANEL)

## US028 Solicitudes Instituciones (Admin / Simulado)
### GET `/api/v1/admin/institutions/requests` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/institutions/requests/{id}/approve` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/institutions/requests/{id}/reject` (perm: ADMIN_PANEL)

## US029 Catálogo Carrera (Admin)
### GET `/api/v1/admin/catalog/careers` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/careers` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/careers/{id}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/careers/{id}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/careers/{id}` (perm: ADMIN_PANEL)

## US030 TipoCarrera (Admin)
### GET `/api/v1/admin/catalog/career-types` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/career-types` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/career-types/{id}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/career-types/{id}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/career-types/{id}` (perm: ADMIN_PANEL)

## US031 País (Admin)
### GET `/api/v1/admin/catalog/countries` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/countries` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/countries/{id}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/countries/{id}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/countries/{id}` (perm: ADMIN_PANEL)

## US032 Provincia (Admin)
### GET `/api/v1/admin/catalog/provinces` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/provinces` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/provinces/{id}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/provinces/{id}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/provinces/{id}` (perm: ADMIN_PANEL)

## US033 Localidad (Admin)
### GET `/api/v1/admin/catalog/localities` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/localities` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/localities/{id}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/localities/{id}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/localities/{id}` (perm: ADMIN_PANEL)

## US034 Género (Admin)
### GET `/api/v1/admin/catalog/genders` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/genders` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/genders/{id}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/genders/{id}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/genders/{id}` (perm: ADMIN_PANEL)

## US035 EstadoUsuario (Admin)
### GET `/api/v1/admin/catalog/user-statuses` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/user-statuses` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/user-statuses/{id}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/user-statuses/{id}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/user-statuses/{id}` (perm: ADMIN_PANEL)

## US036 Permiso (Admin)
### GET `/api/v1/admin/catalog/permissions` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/permissions` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/permissions/{id}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/permissions/{id}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/permissions/{id}` (perm: ADMIN_PANEL)

## US037 Grupo (Admin)
### GET `/api/v1/admin/catalog/groups` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/groups` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/groups/{id}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/groups/{id}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/groups/{id}` (perm: ADMIN_PANEL)

## US038 TipoInstitución (Admin)
### GET `/api/v1/admin/catalog/institution-types` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/institution-types` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/institution-types/{id}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/institution-types/{id}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/institution-types/{id}` (perm: ADMIN_PANEL)

## US039 Modalidad Carrera-Institución (Admin)
### GET `/api/v1/admin/catalog/career-modalities` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/career-modalities` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/career-modalities/{id_mod}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/career-modalities/{id_mod}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/career-modalities/{id_mod}` (perm: ADMIN_PANEL)

## US040 Aptitud (Admin)
### GET `/api/v1/admin/catalog/aptitudes` (perm: ADMIN_PANEL)
### POST `/api/v1/admin/catalog/aptitudes` (perm: ADMIN_PANEL)
### GET `/api/v1/admin/catalog/aptitudes/{id_aptitud}` (perm: ADMIN_PANEL)
### PUT `/api/v1/admin/catalog/aptitudes/{id_aptitud}` (perm: ADMIN_PANEL)
### DELETE `/api/v1/admin/catalog/aptitudes/{id_aptitud}` (perm: ADMIN_PANEL)

---

## Opciones de Auto-Documentación Futuras
| Opción | Beneficio | Notas |
|--------|-----------|-------|
| Flask-RESTX | Swagger UI rápido | Requiere refactor a Namespace/Api |
| Flasgger | Decoradores simples | Añadir specs YAML en docstrings |
| apispec + marshmallow | Control granular | Más código manual |
| Flask-Smorest | OpenAPI 3 + schemas | Reestructurar endpoints a Blueprints |
| drf-spectacular (no Flask) | Referencia Django | No aplica directamente |

### Ejemplo rápido con Flasgger
```python
from flasgger import Swagger
app = Flask(__name__)
Swagger(app)

@app.route('/api/v1/auth/login', methods=['POST'])
"""Login usuario
---
parameters:
  - in: body
    name: body
    schema:
      type: object
      required: [email, password]
      properties:
        email: {type: string}
        password: {type: string}
responses:
  200:
    description: JWT emitido
"""
```
Luego visitar `/apidocs`.

## Próximos Pasos Recomendados
1. Elegir librería (Flasgger para mínima fricción inicial).
2. Añadir docstrings OpenAPI a endpoints críticos.
3. Definir modelos de respuesta y error comunes.
4. Implementar versionado (prefijo `/api/v1`).
5. Añadir tests para validar que los paths documentados existen.

---
Generado automáticamente a partir de comentarios del código. Ajustar cuando se implemente lógica real.
