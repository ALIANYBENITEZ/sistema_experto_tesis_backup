/**
 * Script de Google Apps Script para crear automáticamente la encuesta
 * "Sistema experto web de scoring para análisis de riesgo de clientes en inmobiliarias".
 *
 * LÓGICA CONDICIONAL (P1):
 *   - Si responde "Sí" o "Parcialmente"  -> continúa normalmente (P2, P3, ...).
 *   - Si responde "No"                   -> salta directo a la sección que inicia en P9
 *     ("La evaluación manual puede generar resultados diferentes..."), omitiendo P2 a P8.
 *
 * CÓMO USARLO:
 *  1. Abrí https://script.google.com  (con la cuenta de Google donde querés el formulario).
 *  2. Clic en "Nuevo proyecto".
 *  3. Borrá todo el código de ejemplo y pegá TODO este archivo.
 *  4. Clic en "Guardar" (ícono de disquete) y luego en "Ejecutar" (▶ Run).
 *  5. La primera vez te pedirá autorización: aceptá los permisos con tu cuenta.
 *  6. Al terminar, en el menú "Ver > Registros" (o "Ejecuciones") verás el enlace
 *     del formulario creado. También aparecerá en tu Google Drive.
 */
function crearEncuestaScoring() {
  var form = FormApp.create('Encuesta sobre evaluación de riesgo de clientes en inmobiliarias de Asunción');

  form.setDescription(
    'Estimado/a participante:\n\n' +
    'La presente encuesta forma parte del proyecto de investigación titulado ' +
    '“Desarrollo de un sistema experto web de scoring para la optimización de la toma de decisiones ' +
    'en el análisis de riesgo de clientes en inmobiliarias de Asunción, Paraguay 2026”, desarrollado ' +
    'en el marco de la carrera de Ingeniería Informática.\n\n' +
    'El objetivo de esta encuesta es conocer cómo se realiza actualmente la evaluación de riesgo de ' +
    'los clientes en las inmobiliarias, identificar las principales dificultades del proceso y conocer ' +
    'la percepción sobre una propuesta de sistema web de scoring que permita agilizar y estandarizar ' +
    'la evaluación para apoyar la toma de decisiones.\n\n' +
    'La encuesta está dirigida a administradores, responsables o personas encargadas de la evaluación ' +
    'de clientes en inmobiliarias de Asunción.\n\n' +
    'La información recopilada será utilizada exclusivamente con fines académicos y de investigación, ' +
    'manteniendo la confidencialidad de las respuestas.\n\n' +
    'Tiempo estimado: 5 a 7 minutos.'
  );

  form.setProgressBar(true);
  form.setCollectEmail(false);

  // ---- Consentimiento informado (obligatorio) ----
  form.addCheckboxItem()
    .setTitle('Consentimiento informado')
    .setHelpText('Marque la casilla para continuar.')
    .setChoiceValues(['He leído la información anterior y acepto participar de forma voluntaria.'])
    .setRequired(true);

  // =====================================================================
  // SECCIÓN 1. P1 sola (para poder bifurcar según su respuesta)
  // =====================================================================
  form.addPageBreakItem().setTitle('Sección 1. Situación actual del proceso de evaluación');

  // Creamos primero las secciones destino para poder referenciarlas en el salto.
  // (Se crean aquí como variables; su posición real en el formulario es la del
  //  momento en que se agregan, por eso definimos el orden más abajo.)

  // --- Páginas que se usarán como destino del salto ---
  // Página de P2..P8 (ruta normal)
  var seccionProceso = form.addPageBreakItem()
    .setTitle('Sección 1b. Detalle del proceso actual');

  // P2
  form.addMultipleChoiceItem()
    .setTitle('P2. ¿Cómo realiza actualmente su empresa la evaluación del perfil de los clientes?')
    .setChoiceValues([
      'Revisión manual de documentos',
      'Uso de herramientas informáticas',
      'Consulta de información externa'
    ])
    .showOtherOption(true)
    .setRequired(true);

  // P3
  form.addMultipleChoiceItem()
    .setTitle('P3. ¿Qué nivel de automatización tiene actualmente su proceso de evaluación?')
    .setChoiceValues([
      'Totalmente manual (papeles)',
      'Manual con Excel',
      'Mixto (herramientas + revisión manual)',
      'Mayormente automatizado (software)'
    ])
    .setRequired(true);

  // P4
  form.addMultipleChoiceItem()
    .setTitle('P4. ¿Cuánto tiempo demora aproximadamente el análisis de un cliente antes de tomar una decisión?')
    .setChoiceValues(['Menos de 10 min', '10 a 20 min', '20 a 40 min', 'Más de 40 min'])
    .setRequired(true);

  // P5
  form.addCheckboxItem()
    .setTitle('P5. ¿Cuáles son las principales limitaciones del proceso actual? (marque todas las que correspondan)')
    .setChoiceValues([
      'Errores humanos',
      'Información desorganizada',
      'Reprocesos por datos incompletos',
      'Pérdida de documentos',
      'Falta de criterio uniforme entre evaluadores',
      'Demora en información externa'
    ])
    .showOtherOption(true)
    .setRequired(true);

  // P6
  form.addGridItem()
    .setTitle('P6. Califique la importancia de cada criterio para evaluar el riesgo (1 = nada importante, 5 = muy importante)')
    .setRows([
      'Ingresos y capacidad de pago',
      'Estabilidad laboral',
      'Historial de pagos',
      'Nivel de endeudamiento',
      'Referencias personales/comerciales',
      'Historial crediticio'
    ])
    .setColumns(['1', '2', '3', '4', '5'])
    .setRequired(true);

  // P7
  form.addMultipleChoiceItem()
    .setTitle('P7. ¿Su empresa utiliza criterios definidos o reglas establecidas para clasificar el nivel de riesgo?')
    .setChoiceValues(['Sí', 'No', 'Parcialmente'])
    .setRequired(true);

  // P8
  form.addMultipleChoiceItem()
    .setTitle('P8. ¿Con qué frecuencia tiene dificultades para analizar la información por la cantidad de datos o falta de organización?')
    .setChoiceValues(['Siempre', 'Frecuentemente', 'A veces', 'Rara vez', 'Nunca'])
    .setRequired(true);

  // =====================================================================
  // SECCIÓN 2. Desde P9 (destino del salto cuando P1 = "No")
  // =====================================================================
  var seccionPercepcion = form.addPageBreakItem()
    .setTitle('Sección 2. Percepción general');

  // P9
  form.addMultipleChoiceItem()
    .setTitle('P9. La evaluación manual puede generar resultados diferentes según la persona encargada del análisis.')
    .setChoiceValues([
      'Totalmente de acuerdo',
      'De acuerdo',
      'Ni de acuerdo ni en desacuerdo',
      'En desacuerdo',
      'Totalmente en desacuerdo'
    ])
    .setRequired(true);

  // =====================================================================
  // SECCIÓN 3. Percepción de la propuesta (sistema web de scoring)
  // =====================================================================
  form.addPageBreakItem()
    .setTitle('Sección 3. Percepción de la propuesta (sistema web de scoring)')
    .setHelpText(
      'Se propone un sistema web que evalúa automáticamente a los clientes mediante criterios ponderados ' +
      'y un motor de reglas, clasifica su nivel de riesgo (bajo, medio o alto), centraliza la información ' +
      'y genera reportes, dejando registro de cada decisión.'
    );

  // P10
  form.addMultipleChoiceItem()
    .setTitle('P10. ¿Qué nivel de importancia tiene para usted contar con una clasificación automática del nivel de riesgo del cliente?')
    .setChoiceValues(['Muy importante', 'Importante', 'Moderadamente importante', 'Poco importante', 'Nada importante'])
    .setRequired(true);

  // P11
  form.addMultipleChoiceItem()
    .setTitle('P11. ¿Considera necesario un sistema que registre y centralice la información de los clientes evaluados?')
    .setChoiceValues(['Sí', 'No', 'Parcialmente'])
    .setRequired(true);

  // P12
  form.addMultipleChoiceItem()
    .setTitle('P12. Un sistema experto que genere automáticamente un puntaje de scoring permitiría mejorar el proceso actual.')
    .setChoiceValues([
      'Totalmente de acuerdo',
      'De acuerdo',
      'Ni de acuerdo ni en desacuerdo',
      'En desacuerdo',
      'Totalmente en desacuerdo'
    ])
    .setRequired(true);

  // P13
  form.addMultipleChoiceItem()
    .setTitle('P13. La clasificación automática en niveles de riesgo (bajo, medio y alto) facilitaría la toma de decisiones comerciales.')
    .setChoiceValues([
      'Totalmente de acuerdo',
      'De acuerdo',
      'Ni de acuerdo ni en desacuerdo',
      'En desacuerdo',
      'Totalmente en desacuerdo'
    ])
    .setRequired(true);

  // =====================================================================
  // SECCIÓN 4. Reportes y requisitos del sistema
  // =====================================================================
  form.addPageBreakItem().setTitle('Sección 4. Reportes y requisitos del sistema');

  // P14
  form.addCheckboxItem()
    .setTitle('P14. ¿Qué tipos de reportes le resultarían más útiles? (marque todas las que correspondan)')
    .setChoiceValues([
      'Ficha individual de riesgo por cliente',
      'Historial de evaluaciones',
      'Comparativo o ranking por nivel de riesgo',
      'Estadísticas generales',
      'Reporte por período',
      'Exportable en PDF'
    ])
    .showOtherOption(true)
    .setRequired(true);

  // P15
  form.addCheckboxItem()
    .setTitle('P15. ¿Qué datos considera imprescindibles en el reporte de un cliente? (marque todas las que correspondan)')
    .setChoiceValues([
      'Puntaje total de scoring',
      'Nivel de riesgo (bajo/medio/alto)',
      'Detalle por criterio',
      'Justificación de la decisión',
      'Recomendación final',
      'Fecha y responsable'
    ])
    .setRequired(true);

  // P16
  form.addMultipleChoiceItem()
    .setTitle('P16. ¿Cuánto tiempo considera aceptable que tome el sistema en entregar un resultado?')
    .setChoiceValues(['Menos de 1 min', '1 a 3 min', '3 a 5 min', 'Más de 5 min'])
    .setRequired(true);

  // P17
  form.addMultipleChoiceItem()
    .setTitle('P17. ¿Qué tan importante es que el sistema entregue resultados consistentes (mismo cliente = mismo puntaje, sin importar quién lo evalúe)?')
    .setChoiceValues(['Muy importante', 'Importante', 'Moderadamente importante', 'Poco importante', 'Nada importante'])
    .setRequired(true);

  // P18
  form.addMultipleChoiceItem()
    .setTitle('P18. ¿Es importante que el sistema controle el acceso de usuarios para proteger la información de los clientes?')
    .setChoiceValues(['Muy importante', 'Importante', 'Moderadamente importante', 'Poco importante', 'Nada importante'])
    .setRequired(true);

  // P19
  form.addMultipleChoiceItem()
    .setTitle('P19. ¿Qué tan importante es que el sistema permita consultar antecedentes o información complementaria para apoyar la evaluación?')
    .setChoiceValues(['Muy importante', 'Importante', 'Moderadamente importante', 'Poco importante', 'Nada importante'])
    .setRequired(true);

  // P20
  form.addMultipleChoiceItem()
    .setTitle('P20. ¿Estaría dispuesto a utilizar un sistema experto web de scoring para apoyar la evaluación del riesgo de clientes en su inmobiliaria?')
    .setChoiceValues(['Definitivamente sí', 'Probablemente sí', 'Indeciso', 'Probablemente no', 'Definitivamente no'])
    .setRequired(true);

  // =====================================================================
  // P1 con BIFURCACIÓN:
  //   "Sí" / "Parcialmente" -> van a la sección de P2..P8 (seccionProceso)
  //   "No"                  -> salta directo a la sección de P9 (seccionPercepcion)
  // Se agrega al final para poder referenciar las páginas destino ya creadas,
  // pero se MUEVE a la posición 2 (justo después del page break de la Sección 1).
  // =====================================================================
  var p1 = form.addMultipleChoiceItem();
  p1.setTitle('P1. ¿Su inmobiliaria cuenta con un proceso definido para evaluar el riesgo de los clientes antes de una operación de compra o financiamiento de un inmueble?')
    .setChoices([
      p1.createChoice('Sí', seccionProceso),
      p1.createChoice('No', seccionPercepcion),
      p1.createChoice('Parcialmente', seccionProceso)
    ])
    .setRequired(true);

  // Mover P1 para que aparezca al inicio, dentro de la Sección 1
  // (índice 2 = después del consentimiento[0] y del page break "Sección 1"[1]).
  form.moveItem(p1.getIndex(), 2);

  // ---- Mensaje de cierre ----
  form.setConfirmationMessage('Gracias por su tiempo y colaboración. Sus respuestas son muy valiosas para esta investigación.');

  // ---- Enlaces del formulario creado ----
  Logger.log('FORMULARIO CREADO CORRECTAMENTE');
  Logger.log('Enlace para responder (compartir): ' + form.getPublishedUrl());
  Logger.log('Enlace para editar: ' + form.getEditUrl());
}
