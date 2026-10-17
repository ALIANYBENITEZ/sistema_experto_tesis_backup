# Modelo de costos y justificación de precios

Documento de respaldo para el marco metodológico. Cuantifica los costos del modelo de
negocio, justifica los precios de los planes y demuestra la sostenibilidad del sistema
mediante un punto de equilibrio básico.

> Tipo de cambio referencial: **1 USD ≈ Gs. 7.300** (deducido del dato Render:
> US$ 7/mes = Gs. 51.100). Todos los montos son hipótesis comerciales sujetas a
> validación con proveedores y con la encuesta de disposición a pagar.

---

## 1. Clasificación de costos

Siguiendo la recomendación de separar inversión única y gastos de operación, los costos
del modelo se dividen en dos tipos.

### A. Inversión inicial (costo único de desarrollo)

Esfuerzo y recursos empleados una sola vez para construir el sistema (Tablas 5, 6 y 8 del
presupuesto):

- Recursos humanos (500 h: análisis, diseño, frontend, backend, base de datos, sistema
  experto, modelo de negocio, pasarela, pruebas y documentación): Gs. 5.000.000
- Hardware (laptop + smartphone de pruebas): Gs. 4.300.000
- Software y licencias del período de desarrollo: Gs. 232.200
- **Total inversión inicial: Gs. 9.532.200 (≈ US$ 1.306)**

> Los gastos administrativos de la tesis (Tabla 7, Gs. 731.250: impresión, encuadernación,
> viáticos) se consideran propios del trabajo académico y no del producto comercial, por lo
> que se excluyen del modelo de negocio. Si se incluyeran, la inversión sube a Gs. 10.263.450.

### B. Costos recurrentes (operación mensual de la plataforma)

Costos necesarios para mantener el sistema funcionando. Es el bloque sobre el que se
concentra el Business Model Canvas:

- Hosting backend (Render Web Service Starter, US$ 7): Gs. 51.100/mes — Gs. 613.200/año
- Base de datos PostgreSQL administrada (Render): Gs. 51.100/mes — Gs. 613.200/año
- Frontend estático (Render, plan Free): Gs. 0/mes — Gs. 0/año
- Dominio (prorrateado): ~Gs. 7.300/mes — ~Gs. 87.600/año
- Mantenimiento y actualización del motor de scoring: ~Gs. 40.000/mes — ~Gs. 480.000/año
- Soporte técnico, seguridad y respaldos: ~Gs. 30.000/mes — ~Gs. 360.000/año
- **Subtotal fijo: ~Gs. 179.600/mes — ~Gs. 2.154.000/año**
- Comisión de pasarela (Pagopar): costo variable (% por transacción, proporcional a ventas)

> La comisión de la pasarela es un costo variable proporcional a las ventas, por lo que no
> integra el subtotal fijo sino que se trata como porcentaje por operación.

---

## 2. Costo operativo por evaluación

El costo marginal de producir una evaluación adicional es prácticamente cero (el sistema ya
está desarrollado y en operación). El costo relevante es el costo fijo mensual repartido
entre las evaluaciones vendidas:

> **Costo unitario = Costo fijo mensual ÷ evaluaciones vendidas en el mes**

- 30 evaluaciones/mes: 179.600 ÷ 30 = **~Gs. 6.000 por evaluación** (escenario conservador)
- 50 evaluaciones/mes: 179.600 ÷ 50 = ~Gs. 3.592 por evaluación
- 100 evaluaciones/mes: 179.600 ÷ 100 = ~Gs. 1.796 por evaluación
- 200 evaluaciones/mes: 179.600 ÷ 200 = ~Gs. 898 por evaluación

Se adopta **Gs. 6.000** como piso de costo para no subestimar en el escenario inicial.

---

## 3. Derivación de los precios (reglas de pricing)

Los precios no se fijan de forma arbitraria: se derivan combinando cuatro reglas estándar.

### Paso 1 — Piso de costo

Costo operativo por evaluación en el escenario conservador: **Gs. 6.000**.

### Paso 2 — Margen sobre costo (markup)

> **Precio = Costo ÷ (1 − margen deseado)**

Para servicios de software, donde el costo marginal es casi nulo, se usa un margen alto
(60-70%). Con margen 65%: 6.000 ÷ (1 − 0,65) = ~Gs. 17.000. Este valor supera el techo de
valor (Paso 3), por lo que se ajusta hacia abajo.

### Paso 3 — Techo de valor (anclaje)

El cliente no paga más de lo que le cuesta hacer la evaluación de forma manual. Una
evaluación manual toma 20-40 min; a un costo de analista de ~Gs. 30.000-50.000/hora, equivale
a **Gs. 10.000-15.000 por evaluación manual**. Ese es el techo: el precio debe quedar por
debajo para que al cliente le convenga automatizar.

Rango viable por evaluación: **piso Gs. 6.000 → techo Gs. 10.000-15.000**.

### Paso 4 — Descuento por volumen

A mayor volumen, menor precio unitario (el costo marginal lo permite e incentiva compras
mayores). Partiendo del plan de entrada en la zona alta del rango:

- Bronce (entrada, sin descuento): Gs. 10.000/evaluación
- Plata (−10%): Gs. 9.000/evaluación
- Oro (−20%): Gs. 8.000/evaluación

### Precio final por reporte y por plan

| Plan | Reportes | Precio por reporte | Precio del plan | Margen vs. piso (Gs. 6.000) |
|------|----------|--------------------|-----------------|------------------------------|
| Bronce | 15 | Gs. 10.000 | Gs. 150.000 | 40% |
| Plata | 30 | Gs. 9.000 | Gs. 270.000 | 33% |
| Oro | 50 | Gs. 8.000 | Gs. 400.000 | 25% |

**Precio por reporte en cada plan:**

- Bronce: **Gs. 10.000 por reporte**
- Plata: **Gs. 9.000 por reporte**
- Oro: **Gs. 8.000 por reporte**

Todos los precios quedan por encima del piso de costo (Gs. 6.000) y por debajo del techo de
valor (Gs. 10.000-15.000), con descuento por volumen coherente. Los precios propuestos
originalmente quedan así **validados por el cálculo**.

---

## 4. Punto de equilibrio

> **Punto de equilibrio (unidades) = Costos fijos mensuales ÷ margen de contribución por plan**

Como el costo variable por evaluación es casi nulo, el margen de contribución ≈ precio del
plan.

**¿Cuánto cuesta mantener el sistema por mes?** → Gs. 179.600.

**¿Cuántos clientes de cada plan cubren ese costo?**

- Solo Bronce (Gs. 150.000 c/u): 179.600 ÷ 150.000 = 1,2 → **2 clientes Bronce**
- Solo Plata (Gs. 270.000 c/u): 179.600 ÷ 270.000 = 0,67 → **1 cliente Plata**
- Solo Oro (Gs. 400.000 c/u): 179.600 ÷ 400.000 = 0,45 → **1 cliente Oro**

**Combinación de ejemplo que demuestra sostenibilidad:**

- 1 Bronce (Gs. 150.000) + 1 Plata (Gs. 270.000) = Gs. 420.000 de ingreso mensual
- Costo fijo mensual: Gs. 179.600
- **Superávit mensual: ~Gs. 240.400**

Con un solo cliente Plata u Oro al mes el modelo ya cubre infraestructura, soporte y
mantenimiento. Cualquier cliente adicional genera margen para reinvertir.

### Recuperación de la inversión inicial (opcional)

Si se destina el superávit a recuperar la inversión inicial (Gs. 9.532.200):

- Con un superávit de ~Gs. 240.400/mes: 9.532.200 ÷ 240.400 ≈ **40 meses** (~3,3 años)
- Con 5 clientes Plata/mes (ingreso Gs. 1.350.000, superávit ~Gs. 1.170.400):
  9.532.200 ÷ 1.170.400 ≈ **8 meses**

---

## 5. Conclusión

El modelo propuesto es sostenible: basta **un cliente Plata u Oro mensual** para cubrir la
totalidad de los costos recurrentes. Los precios de los planes (Gs. 10.000 / 9.000 / 8.000
por reporte) se justifican porque:

- superan el costo operativo por evaluación (margen positivo);
- quedan por debajo del costo del proceso manual (ahorro de tiempo para la inmobiliaria);
- aplican un descuento por volumen coherente.

Estos precios se presentan como **hipótesis comercial** respaldada por el cálculo de costos y
pendiente de ajuste según los resultados de la encuesta de disposición a pagar
(`docs/encuesta_scoring_inmobiliarias.md`) y las condiciones reales de los proveedores.
