# Diccionario de Datos

**Sistema:** Sistema Experto de Scoring Comercial Inmobiliario
**Base de datos:** inmobiliaria_db
**Motor:** Microsoft SQL Server 2022

El presente diccionario de datos documenta cada tabla y campo de la base de datos del sistema, especificando el nombre exacto, el tipo de dato, la longitud, la descripción de su función y la identificación de claves primarias (PK), claves foráneas (FK) y restricciones.

---

## Tabla: usuarios
**Descripción:** Almacena la información principal de las personas con acceso al sistema (propietario, administradores y comerciales) junto con sus parámetros de seguridad y autenticación de dos factores.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del usuario (Clave Primaria). Autoincremental. |
| nombre | VARCHAR | 100 | Nombre del usuario. Obligatorio. |
| apellido | VARCHAR | 100 | Apellido del usuario. Obligatorio. |
| email | VARCHAR | 150 | Correo electrónico de inicio de sesión. Debe ser único (Unique). Obligatorio. |
| password_hash | VARCHAR | 255 | Contraseña del usuario almacenada mediante cifrado (scrypt). Obligatorio. |
| rol | VARCHAR | 20 | Rol del usuario: 'propietario', 'administrador' o 'comercial'. Obligatorio. |
| activo | BIT | 1 | Indica si el usuario está activo (1) o inactivo (0). Obligatorio. |
| id_empresa | INT | - | Empresa a la que pertenece el usuario (0 = propietario del sistema). |
| totp_secret | VARCHAR | 255 | Secreto para la autenticación de dos factores (2FA). |
| totp_estado | VARCHAR | 20 | Estado del 2FA: 'no_configurado', 'pendiente', 'activado', 'restablecido'. |
| totp_fecha_config | DATETIME | - | Fecha en que el usuario configuró el 2FA. |
| totp_fecha_reset | DATETIME | - | Fecha del último restablecimiento del 2FA. |
| creado_en | DATETIME | - | Fecha y hora de creación del registro. Obligatorio. |
| actualizado_en | DATETIME | - | Fecha y hora de la última modificación del registro. Obligatorio. |

---

## Tabla: empresas
**Descripción:** Registra las empresas (inmobiliarias) que contratan el uso del sistema, incluyendo su estado y el control de bloqueo de consultas por facturación.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único de la empresa (Clave Primaria). Autoincremental. |
| nombre | VARCHAR | 150 | Nombre o razón social de la empresa. Obligatorio. |
| ruc | VARCHAR | 30 | Registro Único del Contribuyente. Debe ser único (Unique). |
| direccion | VARCHAR | 255 | Dirección física de la empresa. |
| telefono | VARCHAR | 30 | Teléfono de contacto. |
| email | VARCHAR | 150 | Correo electrónico de contacto. |
| activo | BIT | 1 | Indica si la empresa está activa (1) o inactiva (0). |
| consultas_habilitadas | BIT | 1 | Indica si la empresa puede realizar evaluaciones (1) o está bloqueada (0). Obligatorio. |
| motivo_bloqueo | VARCHAR | 50 | Motivo del bloqueo: 'BLOQUEADO_DEUDA' o 'BLOQUEADO_MANUAL'. |
| fecha_bloqueo | DATETIME | - | Fecha en que se bloquearon las consultas. |
| fecha_desbloqueo | DATETIME | - | Fecha en que se desbloquearon las consultas. |
| creado_en | DATETIME | - | Fecha y hora de creación del registro. |

---

## Tabla: clientes
**Descripción:** Almacena los datos de los clientes (personas físicas o jurídicas) que son evaluados por el sistema.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del cliente (Clave Primaria). Autoincremental. |
| tipo_doc | VARCHAR | 10 | Tipo de documento: 'CI', 'RUC' o 'PAS'. Obligatorio. |
| num_doc | VARCHAR | 20 | Número de documento. Debe ser único (Unique). Obligatorio. |
| nombre | VARCHAR | 100 | Nombre del cliente. Obligatorio. |
| apellido | VARCHAR | 100 | Apellido del cliente. |
| email | VARCHAR | 150 | Correo electrónico del cliente. |
| telefono | VARCHAR | 20 | Teléfono de contacto. |
| direccion | VARCHAR | 255 | Dirección del cliente. |
| fecha_nacimiento | DATE | - | Fecha de nacimiento del cliente. |
| nacionalidad | VARCHAR | 10 | Código de país de nacionalidad (FK a paises.id_pais). |
| id_ciudad | INT | - | Ciudad de residencia (FK a ciudad.id_ciudad). |
| estado | VARCHAR | 20 | Estado del cliente: 'activo' o 'inactivo'. Obligatorio. |
| creado_por | INT (FK) | - | Usuario que registró al cliente (FK a usuarios.id). |
| creado_en | DATETIME2 | - | Fecha y hora de creación del registro. Obligatorio. |

---

## Tabla: cliente_empresa
**Descripción:** Tabla de relación que vincula clientes con empresas (relación muchos a muchos). Permite que un mismo cliente esté registrado en varias empresas de forma independiente.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del vínculo (Clave Primaria). Autoincremental. |
| id_cliente | INT (FK) | - | Cliente vinculado (FK a clientes.id). Obligatorio. |
| id_empresa | INT (FK) | - | Empresa vinculada (FK a empresas.id). Obligatorio. |
| estado | VARCHAR | 20 | Estado del vínculo: 'activo' o 'inactivo'. |
| creado_en | DATETIME | - | Fecha y hora de creación del vínculo. |

---

## Tabla: paises
**Descripción:** Catálogo de países utilizado para la nacionalidad de los clientes.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id_pais | VARCHAR (PK) | 3 | Código del país (Clave Primaria). Ej: 'PY', 'AR'. Obligatorio. |
| nombre_pais | VARCHAR | 20 | Nombre del país. Obligatorio. |

---

## Tabla: departamento
**Descripción:** Catálogo de departamentos de Paraguay.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id_departamento | INT (PK) | - | Identificador único del departamento (Clave Primaria). Obligatorio. |
| nombre_departamento | VARCHAR | 100 | Nombre del departamento. Obligatorio. |

---

## Tabla: ciudad
**Descripción:** Catálogo de ciudades, relacionadas a un departamento.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id_ciudad | INT (PK) | - | Identificador único de la ciudad (Clave Primaria). Obligatorio. |
| nombre_ciudad | VARCHAR | 100 | Nombre de la ciudad. Obligatorio. |
| id_departamento | INT (FK) | - | Departamento al que pertenece (FK a departamento.id_departamento). Obligatorio. |

---

## Tabla: documentos
**Descripción:** Almacena los documentos adjuntos de cada cliente.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del documento (Clave Primaria). Autoincremental. |
| cliente_id | INT (FK) | - | Cliente propietario del documento (FK a clientes.id). Obligatorio. |
| tipo | VARCHAR | 50 | Tipo de documento (Ej: 'cedula', 'contrato'). Obligatorio. |
| nombre_archivo | VARCHAR | 255 | Nombre original del archivo. Obligatorio. |
| ruta | VARCHAR | 500 | Ruta de almacenamiento del archivo. Obligatorio. |
| subido_por | INT (FK) | - | Usuario que subió el documento (FK a usuarios.id). |
| subido_en | DATETIME2 | - | Fecha y hora de la carga. Obligatorio. |

---

## Tabla: historial_crediticio
**Descripción:** Registra los datos financieros e históricos de cada cliente utilizados para la evaluación de riesgo. Relación uno a uno con clientes.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único (Clave Primaria). Autoincremental. |
| cliente_id | INT (FK) | - | Cliente asociado (FK a clientes.id). Único (relación 1 a 1). Obligatorio. |
| fuente_externa | VARCHAR | 100 | Fuente de la información crediticia externa. |
| score_externo | NUMERIC | 6,2 | Puntaje crediticio obtenido de una fuente externa. |
| cantidad_atrasos | INT | - | Cantidad de atrasos en pagos registrados. |
| deuda_total_sistema | NUMERIC | 14,2 | Deuda total del cliente en el sistema financiero. |
| historial_pagos | VARCHAR | 20 | Calificación del historial: 'bueno', 'regular', 'malo', 'sin_historial'. |
| en_lista_negra | BIT | 1 | Indica si el cliente está en lista negra (1) o no (0). |
| nivel_endeudamiento | NUMERIC | 5,2 | Porcentaje de endeudamiento del cliente. |
| meses_empleo_actual | INT | - | Antigüedad laboral en meses. |
| tipo_empleo | VARCHAR | 50 | Tipo de empleo: 'dependiente', 'independiente', 'desempleado'. |
| referencias_personales | VARCHAR | 20 | Calificación de referencias: 'buenas', 'regulares', 'malas', 'no_verificadas'. |
| fecha_consulta | DATETIME | - | Fecha de consulta de los datos. |
| actualizado_en | DATETIME | - | Fecha de la última actualización. |

---

## Tabla: criterios
**Descripción:** Catálogo de criterios ponderados utilizados en la evaluación por criterios.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del criterio (Clave Primaria). Autoincremental. |
| nombre | VARCHAR | 100 | Nombre del criterio. Obligatorio. |
| descripcion | VARCHAR | 255 | Descripción del criterio. |
| peso | DECIMAL | 5,2 | Porcentaje de ponderación del criterio. Obligatorio. |
| activo | BIT | 1 | Indica si el criterio está activo (1) o no (0). Obligatorio. |

---

## Tabla: evaluaciones
**Descripción:** Registra las evaluaciones por criterios ponderados realizadas a los clientes.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único de la evaluación (Clave Primaria). Autoincremental. |
| cliente_id | INT (FK) | - | Cliente evaluado (FK a clientes.id). Obligatorio. |
| evaluador_id | INT (FK) | - | Usuario que realizó la evaluación (FK a usuarios.id). Obligatorio. |
| fecha | DATETIME2 | - | Fecha y hora de la evaluación. Obligatorio. |
| puntaje_total | DECIMAL | 5,2 | Puntaje total obtenido. |
| resultado | VARCHAR | 20 | Resultado: 'aprobado', 'observado', 'rechazado'. |
| observaciones | NVARCHAR | MAX | Observaciones de la evaluación. |
| estado | VARCHAR | 20 | Estado de la evaluación. Obligatorio. |

---

## Tabla: evaluacion_detalle
**Descripción:** Detalle de cada criterio evaluado dentro de una evaluación por criterios.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del detalle (Clave Primaria). Autoincremental. |
| evaluacion_id | INT (FK) | - | Evaluación a la que pertenece (FK a evaluaciones.id). Obligatorio. |
| criterio_id | INT (FK) | - | Criterio evaluado (FK a criterios.id). Obligatorio. |
| valor | DECIMAL | 5,2 | Valor asignado al criterio. Obligatorio. |
| comentario | VARCHAR | 255 | Comentario sobre el criterio evaluado. |

---

## Tabla: motor_reglas
**Descripción:** Define los motores de reglas (sistema experto) asignados a cada empresa.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del motor (Clave Primaria). Autoincremental. |
| nombre | VARCHAR | 100 | Nombre del motor de reglas. Obligatorio. |
| version | VARCHAR | 20 | Versión del motor. Obligatorio. |
| descripcion | VARCHAR | 255 | Descripción del motor. |
| activo | BIT | 1 | Indica si el motor está activo (1) o no (0). |
| creado_por | INT (FK) | - | Usuario que creó el motor (FK a usuarios.id). |
| creado_en | DATETIME | - | Fecha y hora de creación. |
| id_empresa_motor | INT | - | Empresa propietaria del motor (0 = global/propietario). |

---

## Tabla: reglas
**Descripción:** Reglas individuales de tipo IF-THEN que componen un motor de reglas.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único de la regla (Clave Primaria). Autoincremental. |
| motor_id | INT (FK) | - | Motor al que pertenece la regla (FK a motor_reglas.id). Obligatorio. |
| nombre | VARCHAR | 100 | Nombre de la regla. Obligatorio. |
| descripcion | VARCHAR | 255 | Descripción de la regla. |
| parametro | VARCHAR | 50 | Campo del cliente a evaluar. Obligatorio. |
| operador | VARCHAR | 10 | Operador de comparación: >=, <=, ==, >, <, !=. Obligatorio. |
| valor_referencia | VARCHAR | 100 | Valor umbral de comparación. Obligatorio. |
| tipo_valor | VARCHAR | 20 | Tipo de valor: 'numerico', 'texto', 'booleano'. Obligatorio. |
| peso_puntos | NUMERIC | 6,2 | Puntos asignados si se cumple la regla. Obligatorio. |
| es_determinante | BIT | 1 | Indica si al fallar produce rechazo directo (1) o no (0). |
| activo | BIT | 1 | Indica si la regla está activa (1) o no (0). |
| orden | INT | - | Orden de evaluación de la regla. |

---

## Tabla: evaluacion_riesgo
**Descripción:** Registra el resultado de las evaluaciones de riesgo realizadas mediante el motor de reglas.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único de la evaluación (Clave Primaria). Autoincremental. |
| cliente_id | INT (FK) | - | Cliente evaluado (FK a clientes.id). Obligatorio. |
| motor_id | INT (FK) | - | Motor de reglas utilizado (FK a motor_reglas.id). Obligatorio. |
| usuario_id | INT (FK) | - | Usuario que ejecutó la evaluación (FK a usuarios.id). Obligatorio. |
| fecha_analisis | DATETIME | - | Fecha y hora del análisis. |
| score_final | NUMERIC | 6,2 | Puntaje final obtenido. |
| score_maximo | NUMERIC | 6,2 | Puntaje máximo posible. |
| categoria_riesgo | VARCHAR | 20 | Clasificación: 'bajo', 'medio', 'alto', 'rechazado'. |
| estado | VARCHAR | 20 | Estado de la evaluación. |
| observaciones | VARCHAR | MAX | Observaciones del análisis. |
| regla_determinante_id | INT (FK) | - | Regla determinante que produjo el resultado (FK a reglas.id). |
| id_empresa | INT | - | Empresa que realizó la evaluación. |

---

## Tabla: resultado_detalle
**Descripción:** Detalle por regla de una evaluación de riesgo.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del detalle (Clave Primaria). Autoincremental. |
| evaluacion_id | INT (FK) | - | Evaluación de riesgo asociada (FK a evaluacion_riesgo.id). Obligatorio. |
| regla_id | INT (FK) | - | Regla evaluada (FK a reglas.id). Obligatorio. |
| cumplido | BIT | 1 | Indica si la regla se cumplió (1) o no (0). Obligatorio. |
| valor_evaluado | VARCHAR | 100 | Valor real del cliente al momento de la evaluación. |
| puntos_obtenidos | NUMERIC | 6,2 | Puntos obtenidos por esta regla. |

---

## Tabla: detalle_operacion
**Descripción:** Datos de la operación inmobiliaria asociada a una evaluación de riesgo. Relación uno a uno con evaluacion_riesgo.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único (Clave Primaria). Autoincremental. |
| evaluacion_id | INT (FK) | - | Evaluación asociada (FK a evaluacion_riesgo.id). Obligatorio. |
| tipo_propiedad | VARCHAR | 50 | Tipo de propiedad: 'casa', 'departamento', 'terreno', etc. Obligatorio. |
| valor_propiedad | NUMERIC | 14,2 | Valor de la propiedad. Obligatorio. |
| monto_solicitado | NUMERIC | 14,2 | Monto solicitado por el cliente. Obligatorio. |
| plazo_meses | INT | - | Plazo de la operación en meses. Obligatorio. |
| ubicacion | VARCHAR | 255 | Ubicación de la propiedad. |
| destino | VARCHAR | 50 | Destino: 'vivienda', 'inversion', 'comercial'. |

---

## Tabla: scoring_modelo
**Descripción:** Define los modelos de scoring configurables del Core (sistema experto nuevo), asignados a cada empresa.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del modelo (Clave Primaria). Autoincremental. |
| nombre | VARCHAR | 100 | Nombre del modelo. Obligatorio. |
| version | VARCHAR | 20 | Versión del modelo. Obligatorio. |
| descripcion | VARCHAR | 500 | Descripción del modelo. |
| id_empresa | INT | - | Empresa propietaria del modelo. Obligatorio. |
| activo | BIT | 1 | Indica si el modelo está activo (1) o no (0). |
| creado_en | DATETIME | - | Fecha y hora de creación. |

---

## Tabla: scoring_factor
**Descripción:** Factores de evaluación que componen un modelo de scoring.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del factor (Clave Primaria). Autoincremental. |
| modelo_id | INT (FK) | - | Modelo al que pertenece (FK a scoring_modelo.id). Obligatorio. |
| codigo | VARCHAR | 50 | Código interno del factor. Obligatorio. |
| nombre | VARCHAR | 100 | Nombre del factor. Obligatorio. |
| descripcion | VARCHAR | 500 | Descripción del factor. |
| tipo_dato | VARCHAR | 20 | Tipo de dato esperado del factor. Obligatorio. |
| tipo_persona | VARCHAR | 10 | Aplicabilidad: 'PF', 'PJ' o 'AMBOS'. Obligatorio. |
| categoria | VARCHAR | 20 | Categoría: 'principal' o 'complementario'. |
| obligatorio | BIT | 1 | Indica si el factor es obligatorio (1) o no (0). |
| activo | BIT | 1 | Indica si el factor está activo (1) o no (0). |
| orden | INT | - | Orden de presentación del factor. |

---

## Tabla: scoring_catalogo
**Descripción:** Valores posibles (catálogo) para factores de tipo categórico.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único (Clave Primaria). Autoincremental. |
| factor_id | INT (FK) | - | Factor al que pertenece (FK a scoring_factor.id). Obligatorio. |
| valor | VARCHAR | 100 | Valor interno de la opción. Obligatorio. |
| etiqueta | VARCHAR | 100 | Etiqueta visible de la opción. Obligatorio. |
| orden | INT | - | Orden de presentación de la opción. |

---

## Tabla: scoring_regla
**Descripción:** Reglas IF-THEN asociadas a cada factor del modelo de scoring.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único de la regla (Clave Primaria). Autoincremental. |
| factor_id | INT (FK) | - | Factor al que pertenece (FK a scoring_factor.id). Obligatorio. |
| nombre | VARCHAR | 100 | Nombre de la regla. Obligatorio. |
| operador | VARCHAR | 10 | Operador de comparación. Obligatorio. |
| valor_min | VARCHAR | 100 | Valor mínimo del rango. |
| valor_max | VARCHAR | 100 | Valor máximo del rango. |
| nivel | VARCHAR | 10 | Nivel de riesgo resultante: 'bajo', 'medio', 'alto'. Obligatorio. |
| peso | NUMERIC | 8,2 | Peso (positivo o negativo) aplicado al score. Obligatorio. |
| explicacion | VARCHAR | 500 | Explicación de la regla. |
| orden | INT | - | Orden de evaluación. |

---

## Tabla: scoring_umbral
**Descripción:** Umbrales de clasificación de riesgo por modelo de scoring.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único (Clave Primaria). Autoincremental. |
| modelo_id | INT (FK) | - | Modelo al que pertenece (FK a scoring_modelo.id). Obligatorio. |
| nivel | VARCHAR | 10 | Nivel de clasificación: 'bajo', 'medio', 'alto'. Obligatorio. |
| score_min | NUMERIC | 8,2 | Puntaje mínimo del rango. Obligatorio. |
| score_max | NUMERIC | 8,2 | Puntaje máximo del rango. Obligatorio. |
| descripcion | VARCHAR | 200 | Descripción del umbral. |

---

## Tabla: scoring_evaluacion
**Descripción:** Registra el resultado de las evaluaciones realizadas con el Core de scoring nuevo.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único de la evaluación (Clave Primaria). Autoincremental. |
| cliente_id | INT | - | Cliente evaluado. Obligatorio. |
| modelo_id | INT (FK) | - | Modelo utilizado (FK a scoring_modelo.id). Obligatorio. |
| modelo_version | VARCHAR | 20 | Versión del modelo al momento de evaluar. Obligatorio. |
| usuario_id | INT | - | Usuario que ejecutó la evaluación. Obligatorio. |
| id_empresa | INT | - | Empresa que realizó la evaluación. Obligatorio. |
| tipo_persona | VARCHAR | 10 | Tipo de persona evaluada: 'PF' o 'PJ'. Obligatorio. |
| fecha | DATETIME | - | Fecha y hora de la evaluación. |
| score_total | NUMERIC | 8,2 | Puntaje total obtenido. Obligatorio. |
| clasificacion | VARCHAR | 10 | Clasificación final: 'bajo', 'medio', 'alto'. Obligatorio. |
| explicacion | VARCHAR | MAX | Explicación generada por el sistema. |
| factores_evaluados | INT | - | Cantidad de factores evaluados. |
| factores_sin_dato | INT | - | Cantidad de factores sin dato. |
| estado | VARCHAR | 20 | Estado: 'completa' o 'incompleta'. |

---

## Tabla: scoring_detalle
**Descripción:** Detalle del resultado por cada factor evaluado en una evaluación del Core.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del detalle (Clave Primaria). Autoincremental. |
| evaluacion_id | INT (FK) | - | Evaluación asociada (FK a scoring_evaluacion.id). Obligatorio. |
| factor_codigo | VARCHAR | 50 | Código del factor evaluado. Obligatorio. |
| factor_nombre | VARCHAR | 100 | Nombre del factor evaluado. Obligatorio. |
| categoria | VARCHAR | 20 | Categoría del factor. |
| valor_original | VARCHAR | 200 | Valor que tenía el cliente en ese factor. |
| estado | VARCHAR | 20 | Estado: 'evaluado', 'sin_dato', 'no_aplica', 'invalido'. Obligatorio. |
| regla_aplicada | VARCHAR | 100 | Nombre de la regla que se aplicó. |
| nivel | VARCHAR | 10 | Nivel de riesgo resultante del factor. |
| peso | NUMERIC | 8,2 | Peso aplicado al score. |
| explicacion | VARCHAR | 500 | Explicación del resultado del factor. |

---

## Tabla: planes
**Descripción:** Catálogo de planes comerciales prepago (tabla paramétrica de facturación).

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del plan (Clave Primaria). Autoincremental. |
| nombre | VARCHAR | 50 | Nombre del plan (Ej: 'Bronce', 'Plata', 'Oro'). Único. Obligatorio. |
| cantidad_reportes_incluidos | INT | - | Cantidad de reportes incluidos en el plan. Obligatorio. |
| precio_plan | NUMERIC | 14,0 | Precio del plan en guaraníes. Obligatorio. |
| precio_reporte_incluido | NUMERIC | 14,0 | Precio de referencia por reporte incluido. Obligatorio. |
| precio_reporte_sobre_facturado | NUMERIC | 14,0 | Precio de cada reporte sobre-facturado. Obligatorio. |
| activo | BIT | 1 | Indica si el plan está activo (1) o no (0). |
| creado_en | DATETIME | - | Fecha y hora de creación. |
| actualizado_en | DATETIME | - | Fecha de la última modificación. |

---

## Tabla: empresa_planes
**Descripción:** Plan vigente contratado por cada empresa, con copia de los valores al momento de la contratación.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único (Clave Primaria). Autoincremental. |
| empresa_id | INT | - | Empresa que contrata el plan. Obligatorio. |
| plan_id | INT (FK) | - | Plan contratado (FK a planes.id). Obligatorio. |
| fecha_inicio | DATETIME | - | Fecha de inicio del plan. Obligatorio. |
| fecha_fin | DATETIME | - | Fecha de finalización del plan. |
| estado | VARCHAR | 20 | Estado: 'activo' o 'finalizado'. |
| precio_plan_contratado | NUMERIC | 14,0 | Precio del plan al momento de contratar. Obligatorio. |
| cantidad_reportes_incluidos | INT | - | Reportes incluidos contratados. Obligatorio. |
| precio_reporte_sobre_facturado | NUMERIC | 14,0 | Precio del reporte extra contratado. Obligatorio. |
| creado_en | DATETIME | - | Fecha y hora de creación del registro. |

---

## Tabla: periodos_facturacion
**Descripción:** Períodos mensuales de facturación por empresa, con el detalle de consumo y montos.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del período (Clave Primaria). Autoincremental. |
| empresa_id | INT | - | Empresa del período. Obligatorio. |
| empresa_plan_id | INT (FK) | - | Plan vigente en el período (FK a empresa_planes.id). Obligatorio. |
| anio | INT | - | Año del período. Obligatorio. |
| mes | INT | - | Mes del período. Obligatorio. |
| fecha_inicio | DATETIME | - | Fecha de inicio del período. Obligatorio. |
| fecha_fin | DATETIME | - | Fecha de fin del período. Obligatorio. |
| cantidad_reportes_incluidos | INT | - | Reportes incluidos en el período. Obligatorio. |
| reportes_consumidos | INT | - | Cantidad de reportes consumidos. |
| reportes_sobre_facturados | INT | - | Cantidad de reportes sobre-facturados. |
| monto_plan | NUMERIC | 14,0 | Monto correspondiente al plan. |
| monto_sobre_facturado | NUMERIC | 14,0 | Monto por reportes sobre-facturados. |
| monto_total | NUMERIC | 14,0 | Monto total del período. |
| monto_pagado | NUMERIC | 14,0 | Monto ya pagado. |
| saldo_pendiente | NUMERIC | 14,0 | Saldo pendiente de pago. |
| estado | VARCHAR | 20 | Estado: 'PENDIENTE', 'PARCIAL', 'PAGADO', 'VENCIDO', 'BLOQUEADO'. |

---

## Tabla: consumo_reportes
**Descripción:** Registro individual de cada reporte consumido por una empresa.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único (Clave Primaria). Autoincremental. |
| empresa_id | INT | - | Empresa que consume el reporte. Obligatorio. |
| usuario_id | INT | - | Usuario que generó el reporte. Obligatorio. |
| evaluacion_id | INT | - | Evaluación asociada al reporte. Obligatorio. |
| periodo_facturacion_id | INT (FK) | - | Período de facturación (FK a periodos_facturacion.id). Obligatorio. |
| tipo_consumo | VARCHAR | 20 | Tipo: 'INCLUIDO' o 'SOBRE_FACTURADO'. Obligatorio. |
| precio_unitario | NUMERIC | 14,0 | Precio unitario del reporte. Obligatorio. |
| fecha_consumo | DATETIME | - | Fecha y hora del consumo. |

---

## Tabla: pagos
**Descripción:** Registra las transacciones de pago de las empresas.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del pago (Clave Primaria). Autoincremental. |
| empresa_id | INT | - | Empresa que realiza el pago. Obligatorio. |
| periodo_facturacion_id | INT (FK) | - | Período que se paga (FK a periodos_facturacion.id). Obligatorio. |
| monto | NUMERIC | 14,0 | Monto del pago. Obligatorio. |
| proveedor | VARCHAR | 50 | Proveedor de pago: 'TEST', 'BANCARD', 'PAGOPAR'. |
| referencia_externa | VARCHAR | 100 | Referencia externa de la transacción. |
| estado | VARCHAR | 20 | Estado: 'PENDIENTE', 'APROBADO', 'RECHAZADO', 'CANCELADO'. |
| metodo_pago | VARCHAR | 50 | Método de pago utilizado. |
| observacion | VARCHAR | 255 | Observaciones del pago. |
| fecha_inicio | DATETIME | - | Fecha de inicio de la transacción. |
| fecha_confirmacion | DATETIME | - | Fecha de confirmación del pago. |

---

## Tabla: historial_empresa_planes
**Descripción:** Historial de cambios de plan por empresa.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único (Clave Primaria). Autoincremental. |
| empresa_id | INT | - | Empresa asociada. Obligatorio. |
| plan_id | INT | - | Plan anterior. Obligatorio. |
| plan_nombre | VARCHAR | 50 | Nombre del plan anterior. Obligatorio. |
| precio_plan | NUMERIC | 14,0 | Precio del plan anterior. Obligatorio. |
| cantidad_reportes | INT | - | Reportes del plan anterior. Obligatorio. |
| precio_sobre_fact | NUMERIC | 14,0 | Precio de reporte extra del plan anterior. Obligatorio. |
| fecha_desde | DATETIME | - | Fecha de inicio de vigencia. Obligatorio. |
| fecha_hasta | DATETIME | - | Fecha de fin de vigencia. |
| cambiado_por | INT | - | Usuario que realizó el cambio de plan. |
| fecha_cambio | DATETIME | - | Fecha del cambio de plan. |

---

## Tabla: auditoria
**Descripción:** Bitácora centralizada que registra los eventos y acciones realizadas en el sistema, tanto desde la aplicación como directamente en la base de datos.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único del evento (Clave Primaria). Autoincremental. |
| usuario_id | INT | - | Usuario que ejecutó la acción. |
| usuario_nombre | VARCHAR | 150 | Nombre del usuario (copia al momento del evento). |
| id_empresa | INT | - | Empresa asociada al evento. |
| tipo_evento | VARCHAR | 30 | Tipo: 'AUTENTICACION', 'CLIENTES', 'EVALUACIONES', etc. Obligatorio. |
| accion | VARCHAR | 50 | Acción realizada (Ej: 'LOGIN_EXITOSO', 'REGISTRO_CLIENTE'). Obligatorio. |
| modulo | VARCHAR | 50 | Módulo del sistema donde ocurrió el evento. |
| entidad | VARCHAR | 50 | Entidad afectada (Ej: 'Cliente', 'Usuario'). |
| registro_id | VARCHAR | 50 | Identificador del registro afectado. |
| resultado | VARCHAR | 20 | Resultado del evento: 'EXITO' o 'FALLO'. |
| ip | VARCHAR | 50 | Dirección IP desde donde se realizó la acción. |
| info_adicional | VARCHAR | MAX | Información adicional en formato JSON. |
| valores_anteriores | VARCHAR | MAX | Valores antes de la modificación (JSON). |
| valores_nuevos | VARCHAR | MAX | Valores después de la modificación (JSON). |
| fecha | DATETIME | - | Fecha y hora del evento. |

---

## Tabla: lista_negra_onu
**Descripción:** Tabla de referencia con la lista consolidada de sanciones ONU/OFAC, utilizada para verificar si un cliente está en lista negra.

| Campo | Tipo de Dato | Longitud | Descripción |
|-------|--------------|----------|-------------|
| id | INT (PK) | - | Identificador único (Clave Primaria). Autoincremental. |
| registro | VARCHAR | 20 | Código de referencia del registro. |
| nombre | VARCHAR | 150 | Nombre de la persona/entidad sancionada. |
| apellido | VARCHAR | 150 | Apellido de la persona sancionada. |
| cargo | VARCHAR | 500 | Cargo o descripción. |
| fecha_nacimiento | VARCHAR | 200 | Fecha de nacimiento (texto). |
| nacionalidad | VARCHAR | 200 | Nacionalidad. |
| num_identidad | VARCHAR | 300 | Número de identidad nacional. |
| num_pasaporte | VARCHAR | 500 | Número de pasaporte. |
| otros | VARCHAR | MAX | Información adicional. |
