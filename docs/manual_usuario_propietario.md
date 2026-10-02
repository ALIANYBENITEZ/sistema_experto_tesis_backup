# Manual de Usuario — Rol Propietario

Este manual describe el uso del sistema de evaluación crediticia para el rol **Propietario**, el perfil de mayor nivel de la plataforma. El propietario administra el sistema completo (modelo multi-inquilino o SaaS): gestiona las empresas clientes, los planes de facturación y supervisa la actividad de toda la plataforma.

> **Nota sobre roles.** El sistema contempla tres roles: **Propietario** (dueño del sistema, acceso global), **Administrador** (gestiona una sola empresa) y **Comercial** (registra clientes y ejecuta evaluaciones). Este manual cubre únicamente el rol **Propietario**. El propietario tiene acceso a todas las funciones de los demás roles más las funciones exclusivas de administración de la plataforma.

---

## 1. Acceso al sistema

### 1.1 Inicio de sesión

1. Abra la aplicación en el navegador.
2. En la pantalla de **Inicio de sesión**, ingrese su **correo electrónico** y **contraseña**.
3. Presione **Iniciar sesión**.

### 1.2 Autenticación de doble factor (2FA)

El sistema exige un segundo factor con **Google Authenticator** para proteger el acceso.

- **Primer ingreso (configuración):** tras validar la contraseña, el sistema muestra un **código QR**. Escanéelo con la app Google Authenticator en su teléfono e ingrese el **código de 6 dígitos** para activar el 2FA.
- **Ingresos posteriores:** luego de la contraseña, el sistema pide el **código de 6 dígitos** vigente en su authenticator.

### 1.3 Recuperación de contraseña

Si olvidó su contraseña, use la opción **¿Olvidó su contraseña?** en la pantalla de login. Deberá ingresar su correo, el **código de 6 dígitos** de su Google Authenticator y la nueva contraseña (mínimo 8 caracteres). Esto solo funciona si ya tiene el 2FA activado.

### 1.4 Cerrar sesión

Use la opción **Cerrar sesión** en la parte inferior del menú lateral.

---

## 2. Navegación general

Tras iniciar sesión, el propietario ve un **menú lateral** con todos los módulos del sistema:

| Módulo | Descripción |
|--------|-------------|
| **Dashboard** | Resumen e indicadores generales |
| **Clientes** | Registro y gestión de clientes |
| **Evaluaciones** | Ejecución y consulta de evaluaciones de riesgo |
| **Scoring Riesgo** | Configuración de modelos y motores de reglas |
| **Reportes** | Estadísticas y reportes en PDF |
| **Facturación** | Planes, consumo y pagos de las empresas |
| **Seguridad** | Estado de 2FA de los usuarios |
| **Auditoría** | Bitácora de eventos de toda la plataforma |
| **Empresas Clientes** | Alta y administración de empresas (exclusivo del propietario) |
| **Usuarios** | Gestión de usuarios del sistema (exclusivo del propietario) |

---

## 3. Dashboard

Al ingresar, el **Dashboard** muestra un panorama general del sistema con indicadores y gráficos. Como propietario, la vista abarca información consolidada de la plataforma, no de una sola empresa.

---

## 4. Empresas Clientes (función exclusiva del propietario)

Este es el módulo central del propietario, donde administra las empresas que usan la plataforma.

### 4.1 Ver el listado de empresas

Entre a **Empresas Clientes** para ver todas las empresas registradas con su nombre, RUC y estado (activa/inactiva).

### 4.2 Registrar una nueva empresa

1. En **Empresas Clientes**, use la opción para **crear/registrar empresa**.
2. Complete los datos: **Nombre** (obligatorio), **RUC**, **Dirección**, **Teléfono** y **Email**.
3. Guarde. El RUC no puede repetirse: si ya existe, el sistema lo advierte.

### 4.3 Editar o activar/desactivar una empresa

- Desde el detalle de la empresa puede **editar** sus datos.
- Puede **activar o desactivar** una empresa. Una empresa desactivada deja de operar en el sistema.

### 4.4 Gestionar los usuarios de una empresa

Desde el detalle de cada empresa, el propietario puede:

- **Ver** los usuarios de esa empresa.
- **Crear** un usuario asignándole rol **administrador** o **comercial** (nombre, apellido, email y contraseña).
- **Editar** un usuario (nombre, apellido, rol, estado y contraseña).
- **Activar o desactivar** un usuario.

> El propietario crea el **administrador** de cada empresa; luego ese administrador gestiona a sus propios comerciales.

---

## 5. Facturación (función exclusiva del propietario)

El módulo de **Facturación** permite administrar los planes y la cobranza de todas las empresas.

### 5.1 Administrar planes

El propietario define los **planes** de la plataforma. Cada plan incluye:

- **Nombre** del plan.
- **Cantidad de reportes incluidos** por período.
- **Precio del plan**.
- **Precio por reporte sobrefacturado** (los que exceden el límite incluido).

Puede **crear** nuevos planes y **editar** o **desactivar** los existentes.

### 5.2 Vista general de facturación

El propietario ve, para cada empresa: su plan vigente, reportes consumidos, reportes sobrefacturados, monto total, monto pagado, saldo pendiente y estado de pago del período actual.

### 5.3 Asignar un plan a una empresa

Desde la vista de facturación, seleccione una empresa y **asigne un plan**. El plan anterior se finaliza y queda registrado en el historial.

### 5.4 Bloquear y desbloquear consultas de una empresa

- **Bloquear:** suspende las consultas/evaluaciones de la empresa (por ejemplo, por deuda).
- **Desbloquear:** reactiva las consultas.

> Cuando una empresa bloqueada **por deuda** salda su período, el sistema la **desbloquea automáticamente**.

### 5.5 Pagos

Puede consultar el listado de **pagos** de todas las empresas y su estado (pendiente, aprobado, rechazado). La plataforma admite pagos a través de la pasarela **Pagopar** cuando está configurada.

---

## 6. Clientes

En **Clientes** se registran y gestionan las personas a evaluar.

- Registre clientes con sus datos personales y documento (**DNI**, **RUC** o **CE**).
- Consulte, edite y adjunte documentos a cada cliente.
- La baja de clientes es lógica (quedan inactivos, no se eliminan físicamente).

---

## 7. Evaluaciones

En **Evaluaciones** se ejecuta el análisis de riesgo de un cliente.

1. Inicie una **nueva evaluación** y seleccione el cliente.
2. Complete los datos solicitados por el motor.
3. El sistema calcula el resultado y clasifica el riesgo (**bajo, medio, alto o rechazado**).
4. Antes de emitir el resultado, el sistema contrasta al cliente contra la **lista de sanciones** (ONU/OFAC); una coincidencia fuerza el riesgo alto.
5. Consulte el **detalle** de cada evaluación y su historial.

---

## 8. Scoring / Motor de Reglas

En **Scoring Riesgo** se configuran los **modelos** y **motores de reglas** (sistema experto IF-THEN) que gobiernan las evaluaciones.

- Cree y edite **modelos de scoring**.
- Defina **reglas** con parámetro, operador (`>=`, `<=`, `==`, `>`, `<`, `!=`) y valor de referencia.
- Marque reglas **determinantes** cuando corresponda.
- Consulte los **motores** disponibles y su detalle.

> Como propietario, puede administrar motores **globales** del sistema además de los específicos de cada empresa.

---

## 9. Reportes

En **Reportes** encontrará estadísticas del sistema y la generación de **reportes en PDF** de las evaluaciones realizadas.

---

## 10. Seguridad

El módulo **Seguridad** muestra el estado de **2FA** de los usuarios. Como propietario, ve a los usuarios de **todas** las empresas, con su estado de autenticación de doble factor.

### Restablecer 2FA de un usuario

Si un usuario pierde el acceso a su Google Authenticator, el propietario puede **restablecer su 2FA**. En el siguiente ingreso, ese usuario volverá a configurar el doble factor desde cero.

---

## 11. Auditoría

El módulo **Auditoría** es la bitácora de eventos del sistema (solo lectura). El propietario ve la actividad de **toda la plataforma**.

Puede filtrar los eventos por:

- **Rango de fechas** (desde / hasta).
- **Empresa** (opción exclusiva del propietario; incluye los eventos del "Sistema").
- **Tipo de evento** (Autenticación, Seguridad, Usuarios, Empresas, Clientes, Evaluaciones, Facturación).
- **Acción**, **módulo** y **resultado** (Éxito / Fallo).
- **Búsqueda libre** por usuario, acción o entidad.

Cada evento registra quién lo realizó, el módulo, la entidad afectada y el resultado.

---

## 12. Buenas prácticas de seguridad

- Mantenga su Google Authenticator en un dispositivo seguro.
- Cambie su contraseña periódicamente (mínimo 8 caracteres) desde la opción de cambio de contraseña.
- Revise la **Auditoría** con regularidad para detectar accesos o acciones inusuales.
- Asigne a cada usuario el **rol mínimo** necesario (comercial para operación, administrador para gestión de una empresa).
- Bloquee las consultas de empresas con pagos vencidos y desbloquéelas solo al regularizarse.
