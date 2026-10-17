# -*- coding: utf-8 -*-
"""
Arregla la zona Empresas / Facturacion / Auditoria del manual de usuario:
 - Reordena imagenes y pies para que cada captura quede bajo su titulo correcto.
 - Separa las 2 imagenes de Pagopar (facturacion) y les pone su pie de figura.
 - Corrige el texto de auditoria (quita "direccion IP", que el sistema no registra).

Imagenes confirmadas (vistas directamente):
 - image20 -> Pantalla Facturacion del sistema (plan, consumo, saldo, botones de pago)
 - image21 -> Checkout de Pagopar (resumen compra, medio de pago, confirmar pago)
 - image22 -> Empresas Clientes
 - image23 -> Auditoria del Sistema

Mapa de parrafos de origen:
 135  "Gestion de empresas (Propietario)"      [titulo]
 136  texto empresas
 137  texto usuarios por propietario
 138  (vacio)
 139  "Facturacion"                            [titulo]
 140  [IMG image20 + image21]  (juntas, sin pie)
 141  "Consultar la auditoria"                 [titulo]
 142  [IMG image22]  (Empresas)
 143  "Ilustracion 29"
 144  "Gestion de empresas (Propietario)"      [pie empresas]
 145  "Pantalla Empresas Clientes..."          [desc empresas]
 146  "El modulo de auditoria... direccion IP" [texto auditoria - CORREGIR]
 147  "Seguridad de la cuenta"                 [titulo]
 148  [IMG image23]  (Auditoria)
 149  "Ilustracion 30"
 150  "Auditoria del Sistema"                  [pie auditoria]
 151  "Pantalla Auditoria..."                  [desc auditoria]
"""
import copy
from docx import Document

NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}'

RUTA_IN  = r"C:\Users\RYZEN\Documents\TESIS 2026_DOCUMENTOS\TESIS 2026 ALIANY\Manual_de_Usuario - COMPLETO.docx"
RUTA_OUT = r"C:\Users\RYZEN\Documents\TESIS 2026_DOCUMENTOS\TESIS 2026 ALIANY\manual de verdad.docx"


def set_text(p_el, texto):
    """Deja en el parrafo un unico run con el texto dado, conservando su formato."""
    runs = p_el.findall(f'{NS}r')
    for r in runs[1:]:
        p_el.remove(r)
    runs = p_el.findall(f'{NS}r')
    if not runs:
        r = p_el.makeelement(f'{NS}r', {})
        p_el.append(r)
        runs = [r]
    r = runs[0]
    for t in r.findall(f'{NS}t'):
        r.remove(t)
    # eliminar <w:drawing> si lo hubiera (no es el caso en pies)
    t = r.makeelement(f'{NS}t', {f'{XML_SPACE}space': 'preserve'})
    t.text = texto
    r.append(t)


def split_images(p_el):
    """
    Dado un parrafo con 2 imagenes (2 runs con <w:drawing>), devuelve dos
    parrafos nuevos, cada uno con una sola imagen, clonando el parrafo original.
    """
    runs_con_img = [r for r in p_el.findall(f'{NS}r') if r.find(f'{NS}drawing') is not None]
    if len(runs_con_img) < 2:
        return [p_el]  # nada que separar

    # Parrafo 1: copia del original, dejar solo la 1a imagen
    p1 = copy.deepcopy(p_el)
    runs1 = [r for r in p1.findall(f'{NS}r') if r.find(f'{NS}drawing') is not None]
    for r in runs1[1:]:
        p1.remove(r)

    # Parrafo 2: copia del original, dejar solo la 2a imagen
    p2 = copy.deepcopy(p_el)
    runs2 = [r for r in p2.findall(f'{NS}r') if r.find(f'{NS}drawing') is not None]
    for r in runs2[:1]:
        p2.remove(r)

    return [p1, p2]


def main():
    d = Document(RUTA_IN)
    ps = d.paragraphs

    def P(i):
        return ps[i]._p

    titulo_emp   = P(135)
    txt_emp1     = P(136)
    txt_emp2     = P(137)
    vacio        = P(138)
    titulo_fact  = P(139)
    img_fact     = P(140)   # image20 + image21
    titulo_audit = P(141)
    img_emp      = P(142)   # image22 (empresas)
    ilus29       = P(143)
    pie_emp      = P(144)
    desc_emp     = P(145)
    txt_audit    = P(146)   # tiene "direccion IP" -> corregir
    titulo_seg   = P(147)
    img_audit    = P(148)   # image23 (auditoria)
    ilus30       = P(149)
    pie_audit    = P(150)
    desc_audit   = P(151)

    # ── 1) Corregir el texto de auditoria (quitar direccion IP) ──
    set_text(txt_audit,
             "El módulo de Auditoría muestra la bitácora de las operaciones "
             "realizadas en el sistema: quién realizó la acción, de qué tipo, "
             "sobre qué entidad, en qué empresa, cuándo y con qué resultado "
             "(éxito o fallo). Permite filtrar los registros por fecha, tipo de "
             "evento, resultado, acción, módulo y empresa.")

    # ── 2) Preparar los dos pies para las imagenes de facturacion ──
    pie_fact1 = copy.deepcopy(pie_audit)
    set_text(pie_fact1, "Facturación")
    desc_fact1 = copy.deepcopy(desc_audit)
    set_text(desc_fact1,
             "Pantalla «Facturación» donde la empresa consulta su plan vigente "
             "(por ejemplo, plan Plata), los reportes incluidos, los consumidos y "
             "el saldo pendiente del período. Los botones «Pagar con Pagopar» y "
             "«Pago de prueba» permiten abonar el período adeudado.")

    pie_fact2 = copy.deepcopy(pie_audit)
    set_text(pie_fact2, "Pago con Pagopar")
    desc_fact2 = copy.deepcopy(desc_audit)
    set_text(desc_fact2,
             "Formulario de pago (checkout) de la pasarela Pagopar al que el sistema "
             "redirige para abonar el período. Muestra el resumen de la compra y el "
             "medio de pago (por ejemplo, Código QR); con «Confirmar pago» se "
             "completa la transacción y el sistema habilita las consultas de la "
             "empresa.")

    # ── 3) Intro de facturacion ──
    intro_fact = copy.deepcopy(txt_emp1)
    set_text(intro_fact,
             "El módulo de Facturación permite a cada empresa consultar su plan, su "
             "consumo de reportes y su saldo pendiente, y realizar el pago en línea "
             "del período mediante la pasarela Pagopar.")

    # ── 4) Separar las 2 imagenes de facturacion en 2 parrafos ──
    img_fact1, img_fact2 = split_images(img_fact)

    # ── 5) Reconstruir el orden ──
    # Secuencia objetivo despues de titulo_emp:
    #   txt_emp1, txt_emp2, img_emp, ilus29, pie_emp, desc_emp,
    #   titulo_fact, intro_fact, img_fact1, pie_fact1, desc_fact1,
    #                            img_fact2, pie_fact2, desc_fact2,
    #   titulo_audit, txt_audit, img_audit, ilus30, pie_audit, desc_audit,
    #   titulo_seg, ...

    # Quitamos de su lugar los elementos que vamos a reinsertar (los que estan sueltos).
    # El parrafo img_fact original se reemplaza por img_fact1/img_fact2.
    parent = img_fact.getparent()
    parent.remove(img_fact)   # lo sacamos; usaremos img_fact1/2

    # Construimos la lista en el orden deseado, anclando tras titulo_emp.
    secuencia = [
        txt_emp1, txt_emp2, img_emp, ilus29, pie_emp, desc_emp,
        titulo_fact, intro_fact, img_fact1, pie_fact1, desc_fact1,
        img_fact2, pie_fact2, desc_fact2,
        titulo_audit, txt_audit, img_audit, ilus30, pie_audit, desc_audit,
    ]

    anchor = titulo_emp
    for el in secuencia:
        anchor.addnext(el)
        anchor = el

    # El parrafo vacio (138) queda flotando; lo movemos al final de la zona (inofensivo)
    # o lo dejamos donde quedo. Lo dejamos.

    d.save(RUTA_OUT)
    print("OK ->", RUTA_OUT)


if __name__ == "__main__":
    main()
