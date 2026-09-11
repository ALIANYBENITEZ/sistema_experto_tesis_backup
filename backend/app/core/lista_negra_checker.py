"""
Servicio de verificación contra lista negra ONU/OFAC.
Compara nombre y documento del cliente contra la tabla lista_negra_onu.
Usa búsqueda parcial (LIKE) para manejar nombres completos y variaciones.
"""
from app.extensions import db
from app.models.lista_negra import ListaNegra
from sqlalchemy import or_, func


def verificar_lista_negra(nombre: str, apellido: str = None, num_doc: str = None) -> dict:
    """
    Verifica si un cliente coincide con algún registro de la lista negra ONU/OFAC.

    Estrategia de búsqueda:
    1. LIKE parcial por nombre (case-insensitive)
    2. LIKE parcial por apellido (case-insensitive)
    3. Combinación nombre + apellido
    4. Coincidencia de número de documento/identidad/pasaporte

    Returns:
        {
            "en_lista": bool,
            "coincidencias": [...],
            "nivel_alerta": str  # "ninguno", "posible", "confirmado"
        }
    """
    coincidencias = []

    if not nombre and not apellido and not num_doc:
        return {"en_lista": False, "coincidencias": [], "nivel_alerta": "ninguno"}

    nombre_clean = nombre.strip() if nombre else ""
    apellido_clean = apellido.strip() if apellido else ""

    # --- Búsqueda por nombre y/o apellido con LIKE ---
    filtros_nombre = []

    if nombre_clean:
        # Buscar nombre del cliente en campo nombre O apellido de la lista
        filtros_nombre.append(ListaNegra.nombre.ilike(f"%{nombre_clean}%"))
        filtros_nombre.append(ListaNegra.apellido.ilike(f"%{nombre_clean}%"))

    if apellido_clean:
        # Buscar apellido del cliente en campo nombre O apellido de la lista
        filtros_nombre.append(ListaNegra.nombre.ilike(f"%{apellido_clean}%"))
        filtros_nombre.append(ListaNegra.apellido.ilike(f"%{apellido_clean}%"))

    if filtros_nombre:
        matches_nombre = ListaNegra.query.filter(or_(*filtros_nombre)).all()

        for reg in matches_nombre:
            reg_nombre = (reg.nombre or "").lower()
            reg_apellido = (reg.apellido or "").lower()
            cliente_nombre = nombre_clean.lower()
            cliente_apellido = apellido_clean.lower()

            # Calcular confianza del match
            confianza = 0

            # Match de nombre
            if cliente_nombre and reg_nombre:
                if cliente_nombre == reg_nombre:
                    confianza += 50
                elif cliente_nombre in reg_nombre or reg_nombre in cliente_nombre:
                    confianza += 30

            # Match de apellido
            if cliente_apellido and reg_apellido:
                if cliente_apellido == reg_apellido:
                    confianza += 50
                elif cliente_apellido in reg_apellido or reg_apellido in cliente_apellido:
                    confianza += 30

            # Cross-match (nombre del cliente = apellido en lista o viceversa)
            if cliente_nombre and reg_apellido and (cliente_nombre == reg_apellido or cliente_nombre in reg_apellido):
                confianza += 20
            if cliente_apellido and reg_nombre and (cliente_apellido == reg_nombre or cliente_apellido in reg_nombre):
                confianza += 20

            # Solo incluir si la confianza es significativa
            if confianza >= 50:
                coincidencias.append({
                    "registro": reg.registro,
                    "nombre": reg.nombre,
                    "apellido": reg.apellido,
                    "cargo": reg.cargo,
                    "tipo_match": "nombre",
                    "confianza": confianza,
                })

    # --- Búsqueda por número de documento ---
    if num_doc and num_doc.strip():
        doc_clean = num_doc.strip()
        if len(doc_clean) >= 4:  # Solo buscar si tiene al menos 4 caracteres
            doc_matches = ListaNegra.query.filter(
                or_(
                    ListaNegra.num_identidad.ilike(f"%{doc_clean}%"),
                    ListaNegra.num_pasaporte.ilike(f"%{doc_clean}%"),
                )
            ).all()

            for reg in doc_matches:
                # Evitar duplicados
                if not any(c["registro"] == reg.registro for c in coincidencias):
                    coincidencias.append({
                        "registro": reg.registro,
                        "nombre": reg.nombre,
                        "apellido": reg.apellido,
                        "cargo": reg.cargo,
                        "tipo_match": "documento",
                        "confianza": 100,
                    })

    # --- Determinar nivel de alerta ---
    if not coincidencias:
        nivel = "ninguno"
    elif any(c["confianza"] >= 100 for c in coincidencias):
        nivel = "confirmado"
    elif any(c["confianza"] >= 80 for c in coincidencias):
        nivel = "confirmado"
    elif any(c["confianza"] >= 50 for c in coincidencias):
        nivel = "posible"
    else:
        nivel = "ninguno"

    # Ordenar por confianza
    coincidencias.sort(key=lambda c: c["confianza"], reverse=True)

    return {
        "en_lista": len(coincidencias) > 0,
        "coincidencias": coincidencias[:5],  # máximo 5 coincidencias
        "nivel_alerta": nivel,
    }
