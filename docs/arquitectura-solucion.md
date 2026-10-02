# Arquitectura de Solución

## Arquitectura Lógica

Como se fundamenta en el Diagrama de Componentes, la arquitectura lógica del sistema se estructuró bajo un patrón de separación en capas sobre un modelo cliente-servidor web, desacoplando completamente la interfaz de usuario de la lógica de negocio mediante una API REST. Las capas definidas son:

- **Capa de Presentación (SPA):** Aplicación de página única desarrollada en React que se ejecuta en el navegador del usuario. Es responsable de la interacción directa mediante formularios, captura las entradas del usuario, gestiona el estado de la sesión y consume los servicios del backend a través de peticiones HTTP. No accede nunca de forma directa a la base de datos.

- **Capa de Lógica de Negocio (API REST):** Núcleo central del sistema, implementado como una API REST con Flask organizada en *blueprints* por dominio (autenticación, clientes, evaluación, scoring, reportes, facturación y auditoría). Contiene las reglas operativas del negocio, entre ellas el motor de inferencia del sistema experto (evaluación de reglas IF-THEN, clasificación de riesgo y verificación contra lista de sanciones), cuya estructura interna se detalla en el Diagrama de Clases.

- **Capa de Acceso a Datos (ORM):** Componente intermedio que abstrae la comunicación con el motor de base de datos mediante el ORM SQLAlchemy. Traduce las operaciones de negocio a consultas SQL y expone los modelos de dominio (usuarios, clientes, modelos de scoring, evaluaciones, auditoría), evitando el manejo manual de sentencias SQL desde la capa de negocio.

## Arquitectura Física

Tal como se ilustra en el Diagrama de Despliegue, la topología del sistema opera bajo un modelo cliente-servidor web de tres nodos, compuesto por:

- **Cliente (Navegador Web):** Equipo del usuario que ejecuta la SPA de React. No requiere instalación de binarios: descarga los recursos estáticos y se comunica con el servidor exclusivamente por HTTPS.

- **Servidor de Aplicaciones (API):** Nodo que aloja la API REST de Flask. Recibe las peticiones del cliente, aplica la lógica de negocio y las validaciones de seguridad, y gestiona el intercambio de tokens JWT. Está desplegado en un entorno de nube (Render).

- **Servidor de Base de Datos (PostgreSQL):** Nodo central que aloja el motor relacional PostgreSQL, gestionando de forma transaccional la persistencia de los datos de todas las empresas (arquitectura multi-inquilino).

- **Red de Comunicaciones:** Canal de transmisión de datos cifrado (HTTPS/TLS) que conecta al cliente con el servidor de aplicaciones, y la conexión segura con *pool* de conexiones entre la API y la base de datos.

## Arquitectura de Seguridad

### Capas de Seguridad

El resguardo de la información se diseñó bajo un enfoque de defensa en profundidad, cuyo flujo temporal se evidencia en el Diagrama de Secuencia (login con doble factor):

- **Seguridad a Nivel de Interfaz:** Validaciones de formato y longitud en los formularios de la SPA (React Hook Form) para prevenir el envío de datos mal formados, complementadas con validaciones en el backend (marshmallow).

- **Seguridad a Nivel de Tránsito:** Comunicación cifrada mediante HTTPS/TLS entre el navegador y la API, con manejo de tokens JWT (access token de 8 horas y refresh token de 30 días) transportados por cabeceras.

- **Seguridad a Nivel de Almacenamiento:** Aplicación de funciones de *hashing* con sal (scrypt de Werkzeug) para las contraseñas y almacenamiento protegido del secreto TOTP utilizado en la autenticación de doble factor.

### Controles Preventivos

Para anticipar y bloquear acciones perjudiciales, el sistema emplea mecanismos proactivos:

- **Autenticación de Doble Factor (2FA):** Además de usuario y contraseña, el acceso exige un código temporal (TOTP) de Google Authenticator, mitigando el riesgo de credenciales comprometidas.

- **Validación de Entradas:** Verificación de formatos y tipos tanto en el cliente como en el servidor, evitando datos inconsistentes o intentos de inyección.

- **Verificación contra Lista de Sanciones:** Antes de emitir un resultado, el motor de scoring contrasta al cliente contra la lista negra (ONU/OFAC), forzando la clasificación de riesgo alto ante coincidencias.

### Controles Correctivos

Ante eventualidades, el sistema cuenta con protocolos de recuperación y análisis:

- **Trazabilidad y Auditoría (Logs):** Registro detallado de eventos críticos (inicios de sesión, reseteos de 2FA, ejecución de evaluaciones, cambios de contraseña) mediante el servicio de auditoría, que persiste cada acción con usuario, módulo, entidad y resultado para su posterior análisis.

- **Respaldos de Información:** Rutinas de copia de seguridad del motor PostgreSQL gestionadas por la plataforma de nube, que permiten restaurar el sistema a un estado estable previo a un incidente.

### Separación de Funciones

Esta segregación de responsabilidades se fundamenta en los perfiles definidos en el Diagrama de Casos de Uso, apoyada en decoradores de autorización (`@admin_required`, `@propietario_required`, `@roles_required`):

- **Roles Operativos (Operador):** Poseen permisos para registrar clientes, ejecutar evaluaciones y consultar reportes, pero el sistema les bloquea la gestión de usuarios y la configuración de los modelos de scoring.

- **Roles Administrativos (Administrador / Propietario):** Poseen la autoridad para gestionar usuarios, configurar los criterios y motores de reglas, auditar el sistema y administrar la facturación.

### Principio de Mínimo Privilegio

Las restricciones de acceso se aplican en todos los puntos de contacto del sistema, alineándose con las decisiones modeladas en el Diagrama de Actividades:

- **Restricción de Interfaz:** La SPA oculta y deshabilita dinámicamente las rutas y controles (mediante rutas protegidas con soporte `adminOnly`) a los que el usuario en sesión no tiene permisos, y el backend re-verifica cada permiso en la API.

- **Restricción Multi-Inquilino:** Cada operación filtra los datos por empresa, de modo que un usuario solo accede a la información de su propia organización, salvo el rol propietario.

- **Restricción de Base de Datos:** La aplicación se conecta a PostgreSQL con un usuario de servicio de privilegios limitados a las operaciones necesarias (lectura, inserción y actualización), sin autoridad para ejecutar sentencias estructurales destructivas sobre el esquema.
