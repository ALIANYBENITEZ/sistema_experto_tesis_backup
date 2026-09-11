# Modelo Logico - Etiquetas de campos (PK / FK)

Guia para completar el diagrama del modelo logico. En tu herramienta
(draw.io / DBeaver), cada campo debe mostrar su etiqueta como en el
ejemplo del profesor: `id (PK)`, `empresa_id (FK)`, `campo (PK, FK)`.

## usuarios
- id (PK)
- nombre
- apellido
- email
- password_hash
- rol
- activo
- creado_en
- actualizado_en
- id_empresa
- totp_secret
- totp_estado
- totp_fecha_config
- totp_fecha_reset

## empresas
- id (PK)
- nombre
- ruc
- direccion
- telefono
- email
- activo
- creado_en
- consultas_habilitadas
- motivo_bloqueo
- fecha_bloqueo
- fecha_desbloqueo

## paises
- id_pais (PK)
- nombre_pais

## departamento
- id_departamento (PK)
- nombre_departamento

## ciudad
- id_ciudad
- nombre_ciudad
- id_departamento (FK -> departamento)

## clientes
- id (PK)
- tipo_doc
- num_doc
- nombre
- apellido
- email
- telefono
- direccion
- fecha_nacimiento
- estado
- creado_por (FK -> usuarios)
- creado_en
- nacionalidad (FK -> paises)
- id_ciudad

## cliente_empresa
- id (PK)
- id_cliente (FK -> clientes)
- id_empresa (FK -> empresas)
- estado
- creado_en

## documentos
- id (PK)
- cliente_id (FK -> clientes)
- tipo
- nombre_archivo
- ruta
- subido_por (FK -> usuarios)
- subido_en

## historial_crediticio
- id (PK)
- cliente_id (FK -> clientes)
- fuente_externa
- score_externo
- cantidad_atrasos
- deuda_total_sistema
- historial_pagos
- en_lista_negra
- nivel_endeudamiento
- meses_empleo_actual
- tipo_empleo
- referencias_personales
- fecha_consulta
- actualizado_en

## criterios
- id (PK)
- nombre
- descripcion
- peso
- activo

## evaluaciones
- id (PK)
- cliente_id (FK -> clientes)
- evaluador_id (FK -> usuarios)
- fecha
- puntaje_total
- resultado
- observaciones
- estado

## evaluacion_detalle
- id (PK)
- evaluacion_id (FK -> evaluaciones)
- criterio_id (FK -> criterios)
- valor
- comentario

## motor_reglas
- id (PK)
- nombre
- version
- descripcion
- activo
- creado_por (FK -> usuarios)
- creado_en
- id_empresa_motor

## reglas
- id (PK)
- motor_id (FK -> motor_reglas)
- nombre
- descripcion
- parametro
- operador
- valor_referencia
- tipo_valor
- peso_puntos
- es_determinante
- activo
- orden

## evaluacion_riesgo
- id (PK)
- cliente_id (FK -> clientes)
- motor_id (FK -> motor_reglas)
- usuario_id (FK -> usuarios)
- fecha_analisis
- score_final
- score_maximo
- categoria_riesgo
- estado
- observaciones
- regla_determinante_id (FK -> reglas)
- id_empresa

## resultado_detalle
- id (PK)
- evaluacion_id (FK -> evaluacion_riesgo)
- regla_id (FK -> reglas)
- cumplido
- valor_evaluado
- puntos_obtenidos

## detalle_operacion
- id (PK)
- evaluacion_id (FK -> evaluacion_riesgo)
- tipo_propiedad
- valor_propiedad
- monto_solicitado
- plazo_meses
- ubicacion
- destino

## scoring_modelo
- id (PK)
- nombre
- version
- descripcion
- id_empresa
- activo
- creado_en

## scoring_factor
- id (PK)
- modelo_id (FK -> scoring_modelo)
- codigo
- nombre
- descripcion
- tipo_dato
- tipo_persona
- categoria
- obligatorio
- activo
- orden

## scoring_catalogo
- id (PK)
- factor_id (FK -> scoring_factor)
- valor
- etiqueta
- orden

## scoring_regla
- id (PK)
- factor_id (FK -> scoring_factor)
- nombre
- operador
- valor_min
- valor_max
- nivel
- peso
- explicacion
- orden

## scoring_umbral
- id (PK)
- modelo_id (FK -> scoring_modelo)
- nivel
- score_min
- score_max
- descripcion

## scoring_evaluacion
- id (PK)
- cliente_id (FK -> clientes)
- modelo_id (FK -> scoring_modelo)
- modelo_version
- usuario_id
- id_empresa
- tipo_persona
- fecha
- score_total
- clasificacion
- explicacion
- factores_evaluados
- factores_sin_dato
- estado

## scoring_detalle
- id (PK)
- evaluacion_id (FK -> scoring_evaluacion)
- factor_codigo
- factor_nombre
- categoria
- valor_original
- estado
- regla_aplicada
- nivel
- peso
- explicacion

## planes
- id (PK)
- nombre
- cantidad_reportes_incluidos
- precio_plan
- precio_reporte_incluido
- precio_reporte_sobre_facturado
- activo
- creado_en
- actualizado_en

## empresa_planes
- id (PK)
- empresa_id (FK -> empresas)
- plan_id (FK -> planes)
- fecha_inicio
- fecha_fin
- estado
- precio_plan_contratado
- cantidad_reportes_incluidos
- precio_reporte_sobre_facturado
- creado_en

## periodos_facturacion
- id (PK)
- empresa_id (FK -> empresas)
- empresa_plan_id (FK -> empresa_planes)
- anio
- mes
- fecha_inicio
- fecha_fin
- cantidad_reportes_incluidos
- reportes_consumidos
- reportes_sobre_facturados
- monto_plan
- monto_sobre_facturado
- monto_total
- monto_pagado
- saldo_pendiente
- estado

## consumo_reportes
- id (PK)
- empresa_id (FK -> empresas)
- usuario_id
- evaluacion_id
- periodo_facturacion_id (FK -> periodos_facturacion)
- tipo_consumo
- precio_unitario
- fecha_consumo

## pagos
- id (PK)
- empresa_id (FK -> empresas)
- periodo_facturacion_id (FK -> periodos_facturacion)
- monto
- proveedor
- referencia_externa
- estado
- metodo_pago
- observacion
- fecha_inicio
- fecha_confirmacion

## historial_empresa_planes
- id (PK)
- empresa_id (FK -> empresas)
- plan_id (FK -> planes)
- plan_nombre
- precio_plan
- cantidad_reportes
- precio_sobre_fact
- fecha_desde
- fecha_hasta
- cambiado_por (FK -> usuarios)
- fecha_cambio

## auditoria
- id (PK)
- usuario_id
- usuario_nombre
- id_empresa
- tipo_evento
- accion
- modulo
- entidad
- registro_id
- resultado
- ip
- info_adicional
- valores_anteriores
- valores_nuevos
- fecha

## lista_negra_onu
- id (PK)
- registro
- nombre
- apellido
- cargo
- fecha_nacimiento
- nacionalidad
- num_identidad
- num_pasaporte
- otros
