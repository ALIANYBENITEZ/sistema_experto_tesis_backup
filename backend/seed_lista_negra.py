"""
Seed: Cargar datos de la lista de sanciones ONU en la tabla lista_negra_onu.
Ejecutar: python seed_lista_negra.py
"""
from app import create_app
from app.extensions import db
from app.models.lista_negra import ListaNegra

# Datos extraídos del Excel ONU (nombre, apellido, cargo, num_identidad)
DATOS_ONU = [
    ("ERIC", "BADEGE", None, None),
    ("GASTON", "IYAMUREMYE", "Presidente interino de las FDLR", None),
    ("INNOCENT", "KAINA", "ex Vicecomandante del M23", None),
    ("JÉRÔME", "KAKWAVU", None, None),
    ("GERMAIN", "KATANGA", None, None),
    ("THOMAS", "LUBANGA", None, None),
    ("SULTANI", "MAKENGA", None, None),
    ("CALLIXTE", "MBARUSHIMANA", None, None),
    ("SYLVESTRE", "MUDACUMURA", "Comandante de las FDLR-FOCA", None),
    ("LEODOMIR", "MUGARAGU", None, None),
    ("LEOPOLD", "MUJYAMBERE", None, None),
    ("JAMIL", "MUKULU", "Jefe de las Fuerzas Democráticas Aliadas", None),
    ("IGNACE", "MURWANASHYAKA", None, None),
    ("STRATON", "MUSONI", None, None),
    ("JULES", "MUTEBUTSI", None, None),
    ("LAURENT", "NKUNDA", None, None),
    ("BOSCO", "TAGANDA", None, None),
    ("INNOCENT", "ZIMURINDA", None, None),
    ("JOSEPH", "KONY", "Comandante del Lord's Resistance Army", None),
    ("ABDOULAYE", "HISSENE", "general", None),
    ("ALI", "DARASSA", None, "10978000004482"),
    ("JIMMY", "CHERIZIER", None, None),
    ("SADDAM", "HUSSEIN", None, None),
    ("IZZAT", "IBRAHIM", None, None),
    ("TARIQ", "AZIZ", None, None),
    ("MUAMMAR", "MOHAMMED", "Líder de la Revolución", None),
    ("SAADI", "QADHAFI", None, None),
    ("ABDULLAH", "AL-SENUSSI", None, None),
    ("AIMAN", "MUHAMMED", None, None),
    ("OMAR", "MAHMOUD", None, None),
    ("DAWOOD", "IBRAHIM", None, None),
    ("MOKHTAR", "BELMOKHTAR", None, None),
    ("HAFIZ", "MUHAMMAD", None, None),
    ("ZAKI-UR-REHMAN", "LAKHVI", None, None),
    ("IBRAHIM", "AWWAD", None, None),
    ("MOHAMMED", "MASOOD", None, None),
    ("HAMZA", "USAMA", None, None),
    ("ABDELMALEK", "DROUKDEL", None, None),
    ("ANWAR", "NASSER", None, None),
    ("DOKU", "KHAMATOVICH", None, None),
    ("MOHAMMAD", "HASSAN", "First Deputy Taliban", None),
    ("MOHAMMED", "OMAR", "Líder de los Fieles Talibán", None),
    ("SIRAJUDDIN", "JALLALOUDINE", "Na'ib Amir Taliban", None),
    ("KHAIRULLAH", "KHAIRKHWAH", "Governor Herat Taliban", None),
    ("JALALUDDIN", "HAQQANI", None, None),
    ("ABDULMALIK", "AL-HOUTHI", None, None),
    ("AHMAD", "DIRIYE", None, None),
    ("MAALIM", "AYMAN", "Fundador Jaysh Ayman Al-Shabaab", None),
    ("ANJEM", "CHOUDARY", None, None),
    ("NURJAMAN", "RIDUAN", None, None),
    ("NAJMUDDIN", "FARAJ", None, None),
    ("FÉLICIEN", "NSANZUBUKIRE", "Coronel FDLR", None),
    ("PACIFIQUE", "NTAWUNGUKA", "General de Brigada FDLR", None),
    ("MUHINDO", "AKILI", "General FARDC", None),
    ("GUIDON", "SHIMIRAY", None, None),
    ("SEKA", "BALUKU", None, None),
    ("AHMAD", "MAHMOOD", "alto dirigente FDA", None),
    ("FRANÇOIS", "YANGOUVONDA", None, None),
    ("NOURREDINE", "ADAM", None, None),
    ("ALFRED", "YEKATOM", "Cabo Primero FACA", None),
    ("EUGÈNE", "BARRET", None, None),
    ("MARTIN", "KOUMTAMADJI", None, None),
    ("JOHNSON", "ANDRE", "dirigente banda 5", None),
    ("RENEL", "DESTINA", None, None),
    ("WILSON", "JOSEPH", "dirigente banda 400", None),
    ("VITELHOMME", "INNOCENT", None, None),
    ("LUCKSON", "ELAN", "líder banda Gran Grif", None),
    ("GAFFAR", "MOHAMMED", "General de División Sudán", None),
    ("MUSA", "HILAL", "ex-Diputado Sudán", None),
    ("ABDEL", "RAHMAN", "General FAR Darfur", None),
    ("PAUL", "MALONG", "Ex Jefe Estado Mayor ELPS", None),
    ("GABRIEL", "JOK", None, None),
    ("SIMON", "GATWECH", "Jefe Estado Mayor MLPS", None),
    ("GULMUROD", "KHALIMOV", None, None),
    ("NUSRET", "IMAMOVIC", None, None),
    ("PETER", "CHERIF", None, None),
    ("MAXIME", "HAUCHARD", None, None),
    ("SALIM", "BENGHALEM", None, None),
    ("TARKHAN", "TAYUMURAZOVICH", None, None),
]

app = create_app()
with app.app_context():
    db.create_all()

    if ListaNegra.query.count() > 0:
        print(f"! Ya hay {ListaNegra.query.count()} registros en lista_negra_onu. Se omite.")
    else:
        for i, (nombre, apellido, cargo, num_id) in enumerate(DATOS_ONU, 1):
            reg = ListaNegra(
                registro=f"ONU-{i:03d}",
                nombre=nombre,
                apellido=apellido,
                cargo=cargo,
                num_identidad=num_id,
            )
            db.session.add(reg)

        db.session.commit()
        print(f"✅ {len(DATOS_ONU)} registros cargados en lista_negra_onu.")
