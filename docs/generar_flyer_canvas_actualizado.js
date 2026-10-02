const fs = require('fs');
const path = require('path');

const W = 1365;
const H = 768;
const out = path.join(__dirname, 'flyer_business_model_canvas_actualizado.pdf');

const COLORS = {
  paper: '#fcfaf5',
  navy: '#102a47',
  gold: '#d9a52c',
  purple: '#efe5f2',
  purpleLine: '#80658f',
  aqua: '#dff4f1',
  aquaLine: '#19a5a0',
  blue: '#e5effa',
  blueLine: '#3b7fb5',
  yellow: '#fff2c8',
  yellowLine: '#edbd36',
  pink: '#fce4e1',
  pinkLine: '#f06d62',
  teal: '#e0f3ef',
  tealLine: '#28a79f',
  red: '#fce9e4',
  redLine: '#ee705f',
  white: '#ffffff',
  sideGreen: '#20a89e',
  sidePurple: '#80658f',
};

function rgb(hex) {
  const value = hex.replace('#', '');
  return [0, 2, 4].map((i) => parseInt(value.slice(i, i + 2), 16) / 255);
}

const ops = [];
function add(value) { ops.push(Buffer.from(value, 'ascii')); }
function addText(value) { ops.push(Buffer.from(value, 'latin1')); }
function num(value) { return Number(value.toFixed(2)); }
function colorCmd(hex, mode) { const [r, g, b] = rgb(hex); return `${num(r)} ${num(g)} ${num(b)} ${mode}\n`; }
function esc(value) { return value.replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)'); }
function pdfText(value) {
  return Buffer.from(value, 'latin1').toString('binary');
}

function rect(x, y, w, h, fill, stroke = null, lineWidth = 1) {
  add('q\n');
  add(colorCmd(fill, 'rg'));
  if (stroke) {
    add(colorCmd(stroke, 'RG'));
    add(`${lineWidth} w\n${num(x)} ${num(y)} ${num(w)} ${num(h)} re B\n`);
  } else {
    add(`${num(x)} ${num(y)} ${num(w)} ${num(h)} re f\n`);
  }
  add('Q\n');
}

function line(x1, y1, x2, y2, stroke, lineWidth = 1) {
  add('q\n');
  add(colorCmd(stroke, 'RG'));
  add(`${lineWidth} w\n${num(x1)} ${num(y1)} m ${num(x2)} ${num(y2)} l S\nQ\n`);
}

function text(x, y, value, size = 10, font = 'F1', fill = COLORS.navy, align = 'left') {
  const approxWidth = value.length * size * 0.5;
  let tx = x;
  if (align === 'center') tx = x - approxWidth / 2;
  if (align === 'right') tx = x - approxWidth;
  add('BT\n');
  add(`/${font} ${size} Tf\n`);
  add(colorCmd(fill, 'rg'));
  add(`${num(tx)} ${num(y)} Td\n`);
  addText(`(${pdfText(esc(value))}) Tj\n`);
  add('ET\n');
}

function wrapLine(value, maxChars) {
  const words = value.split(/\s+/).filter(Boolean);
  const lines = [];
  let current = '';
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > maxChars && current) {
      lines.push(current);
      current = word;
    } else {
      current = next;
    }
  }
  if (current) lines.push(current);
  return lines.length ? lines : [''];
}

function fitLines(value, width, height, initialSize, minSize = 7.2) {
  let size = initialSize;
  while (size >= minSize) {
    const maxChars = Math.max(8, Math.floor(width / (size * 0.5)));
    const lines = [];
    for (const paragraph of value.split('\n')) {
      if (!paragraph.trim()) lines.push('');
      else lines.push(...wrapLine(paragraph, maxChars));
    }
    const lineHeight = size * 1.2;
    if (lines.length * lineHeight <= height) return { lines, size, lineHeight };
    size -= 0.25;
  }
  const maxChars = Math.max(8, Math.floor(width / (minSize * 0.5)));
  const lines = [];
  for (const paragraph of value.split('\n')) {
    if (!paragraph.trim()) lines.push('');
    else lines.push(...wrapLine(paragraph, maxChars));
  }
  return { lines, size: minSize, lineHeight: minSize * 1.2 };
}

function textBlock(x, y, w, h, value, options = {}) {
  const padding = options.padding || 12;
  const fitted = fitLines(value, w - padding * 2, h - padding * 2, options.size || 10, options.minSize || 7.2);
  const total = fitted.lines.length * fitted.lineHeight;
  let cursor = y + h - padding - fitted.size;
  if (options.vertical === 'center') cursor = y + h / 2 + total / 2 - fitted.size;
  for (const current of fitted.lines) {
    if (current) text(x + w / 2, cursor, current, fitted.size, options.font || 'F1', options.fill || COLORS.navy, 'center');
    cursor -= fitted.lineHeight;
  }
}

function block(x, y, w, h, title, body, fill, stroke, options = {}) {
  rect(x, y, w, h, fill, stroke, options.lineWidth || 1.1);
  const headerH = options.headerH || 29;
  rect(x, y + h - headerH, w, headerH, fill, stroke, options.lineWidth || 1.1);
  text(x + w / 2, y + h - headerH + 8, title, options.titleSize || 10.7, 'F2', COLORS.navy, 'center');
  textBlock(x, y, w, h - headerH, body, {
    size: options.size || 10,
    minSize: options.minSize || 7.2,
    padding: options.padding || 12,
    vertical: options.vertical || 'center',
  });
}

// Fondo y cabecera, conservando la composición del flyer de referencia.
rect(0, 0, W, H, COLORS.paper);
text(65, 715, 'Business Model Canvas: mapa visual del modelo', 27, 'F2', COLORS.navy, 'left');
text(65, 687, 'El Canvas representa la lógica; no la reemplaza.', 10.2, 'F1', '#626262', 'left');
line(65, 675, 1320, 675, COLORS.gold, 1.4);

// Retícula principal.
block(27, 195, 152, 460, 'Socios clave',
  'No se definen alianzas comerciales ni socios estratégicos.\n\nProveedores de tecnología e infraestructura (recursos necesarios, no socios):\n- OnRender: alojamiento e infraestructura.\n- GitHub: repositorio y control de versiones.\n- Pagopar: pasarela de pagos.\n\nONU / OFAC: fuentes externas de información, no socios comerciales.',
  COLORS.purple, COLORS.purpleLine, { size: 9.2, minSize: 7.1 });

block(183, 375, 225, 280, 'Actividades clave',
  'Desarrollo y mantenimiento del sistema web de scoring.\n\nConfiguración y actualización de criterios y reglas IF-THEN parametrizadas.\n\nProcesamiento de evaluaciones y generación de reportes.\n\nValidación funcional y actualización de reglas según el conocimiento definido.\n\nSoporte y mantenimiento de la plataforma.',
  COLORS.aqua, COLORS.aquaLine, { size: 9.5, minSize: 7.4 });

block(183, 195, 225, 180, 'Recursos clave',
  'Plataforma web React/Flask y base de datos PostgreSQL.\n\nMotor de reglas, criterios y conocimiento del dominio.\n\nReglas IF-THEN definidas y validadas dentro del proyecto.\n\nInfraestructura de alojamiento, seguridad, respaldos y soporte técnico.',
  COLORS.blue, COLORS.blueLine, { size: 9.3, minSize: 7.4 });

block(415, 195, 215, 460, 'Propuesta de valor',
  'Evaluación automatizada del riesgo comercial.\n\nScoring con variables como ingresos, historial de pagos, nivel de endeudamiento y comportamiento financiero.\n\nReglas IF-THEN parametrizadas para obtener puntaje y clasificación Alto, Medio o Bajo; apto/no apto según las reglas.\n\nVerificación automática contra listas negras (ONU/OFAC): diferenciador clave que bloquea evaluaciones con alertas de compliance.\n\nReportes para apoyar la toma de decisiones humanas.\n\nObjetivo: reducir el tiempo de evaluación de 20-40 min a 5-10 min (estimación sujeta a validación).\n\nMayor objetividad y consistencia en el análisis.',
  COLORS.yellow, COLORS.yellowLine, { size: 9.5, minSize: 7.2 });

block(641, 410, 189, 245, 'Relación con clientes',
  'Soporte técnico y asistencia durante el uso.\n\nOrientación inicial para la adopción de la plataforma.\n\nCapacitación básica a los usuarios autorizados.\n\nAsistencia durante el uso del sistema.\n\nMantenimiento y actualizaciones de la plataforma.\n\nComunicación digital.',
  COLORS.pink, COLORS.pinkLine, { size: 9.3, minSize: 7.3 });

block(641, 195, 189, 215, 'Canales',
  'Plataforma web.\n\nContacto comercial directo con inmobiliarias.\n\nDemostración del sistema.\n\nCanales digitales de soporte y comunicación.',
  COLORS.blue, COLORS.blueLine, { size: 9.8, minSize: 7.7 });

block(844, 195, 179, 460, 'Segmentos de clientes',
  'Cliente y pagador: inmobiliarias de Asunción.\n\nUsuarios: administradores, responsables de evaluación y otros usuarios autorizados dentro de la inmobiliaria.\n\nNecesidad: agilizar y estandarizar el análisis de clientes y apoyar decisiones de riesgo.',
  COLORS.teal, COLORS.tealLine, { size: 9.6, minSize: 7.5 });

// Franja lateral existente del flyer.
text(1030, 547, 'Mercado', 24, 'F2', COLORS.sideGreen, 'left');
text(1030, 490, 'Operación', 24, 'F2', COLORS.sidePurple, 'left');
text(1030, 430, 'Centro: propuesta de valor', 14, 'F2', COLORS.gold, 'left');
rect(1030, 360, 126, 30, '#1b5586');
text(1093, 370, 'Canvas', 10, 'F2', COLORS.white, 'center');

// Banda inferior de costos e ingresos/sostenimiento.
block(35, 36, 487, 150, 'Costos',
  'Infraestructura y alojamiento del sistema.\n\nBase de datos PostgreSQL administrada y servicios necesarios.\n\nDominio y operación de la plataforma.\n\nMantenimiento, actualizaciones funcionales y del motor de scoring.\n\nSeguridad, respaldos, soporte técnico y operación continua.\n\nMontos exactos: por definir según proveedor y escala de uso.',
  COLORS.red, COLORS.redLine, { size: 9.3, minSize: 7.6, titleSize: 11.2 });

block(566, 36, 464, 150, 'Ingresos / sostenimiento',
  'Quién paga: la inmobiliaria.\n\nQué paga: paquetes prepago de evaluaciones/reportes de scoring.\n\nBronce: 15 reportes - Gs. 150.000\nPlata: 30 reportes - Gs. 270.000\nOro: 50 reportes - Gs. 400.000\n\nSi supera su paquete, puede adquirir reportes/evaluaciones adicionales.\n\nLos ingresos por paquetes y adicionales sostienen infraestructura, mantenimiento, seguridad, soporte y actualizaciones.',
  COLORS.yellow, COLORS.yellowLine, { size: 9.6, minSize: 7.7, titleSize: 11.2 });

text(98, 16, 'Modelo de negocio aplicado a tesis tecnológicas', 8.4, 'F1', '#777777', 'left');

function object(value) { return Buffer.from(value, 'ascii'); }
const stream = Buffer.concat(ops);
const objects = [];
objects[1] = object('<< /Type /Catalog /Pages 2 0 R >>');
objects[2] = object('<< /Type /Pages /Kids [3 0 R] /Count 1 >>');
objects[3] = object('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 1365 768] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>');
objects[4] = object('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>');
objects[5] = object('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>');
objects[6] = Buffer.concat([object(`<< /Length ${stream.length} >>\nstream\n`), stream, object('\nendstream')]);

const chunks = [Buffer.from('%PDF-1.4\n%\xff\xff\xff\xff\n', 'binary')];
const offsets = [0];
for (let i = 1; i <= 6; i += 1) {
  offsets[i] = Buffer.concat(chunks).length;
  chunks.push(object(`${i} 0 obj\n`));
  chunks.push(objects[i]);
  chunks.push(object('\nendobj\n'));
}
const xrefOffset = Buffer.concat(chunks).length;
let xref = `xref\n0 7\n0000000000 65535 f \n`;
for (let i = 1; i <= 6; i += 1) xref += `${String(offsets[i]).padStart(10, '0')} 00000 n \n`;
chunks.push(object(xref));
chunks.push(object(`trailer\n<< /Size 7 /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`));
fs.writeFileSync(out, Buffer.concat(chunks));
console.log(out);
