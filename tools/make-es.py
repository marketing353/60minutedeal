# -*- coding: utf-8 -*-
"""Generate es.html from index.html.

The Spanish page is a committed artefact, not a build-time output — the site has
no build step and Vercel just serves the file. Re-run this after editing English
copy so the two stay in sync:

    python tools/make-es.py

Any string in COPY that no longer appears in index.html is reported, so an edit
on the English side cannot silently leave Spanish text behind.
"""
import io
import re
import sys

COPY = {
    # header / hero
    "Today’s matching window closes in": "La ventana de búsqueda de hoy cierra en",
    "Find my vehicle — free ↗": "Buscar mi vehículo — gratis ↗",
    "Find my next vehicle ↗": "Buscar mi próximo vehículo ↗",
    "Find my vehicle ↗": "Buscar mi vehículo ↗",
    "Find my vehicle": "Buscar mi vehículo",
    "For Californians who’d rather be driving than negotiating":
        "Para californianos que prefieren manejar en vez de negociar",
    "Stop shopping. Start ": "Deja de buscar. Empieza a ",
    ">driving<": ">manejar<",
    "Tell us what you want in ": "Dinos qué quieres en ",
    "60 seconds": "60 segundos",
    ". We match it to real vehicles and real numbers — so you walk in knowing the answer instead of asking the question.":
        ". Lo comparamos con vehículos y números reales, para que llegues sabiendo la respuesta en vez de preguntársela a alguien.",
    "Or read why we built this ↓": "O lee por qué creamos esto ↓",
    "No credit check": "Sin revisión de crédito",
    "Trade-ins welcome": "Aceptamos tu auto a cuenta",
    "No dealership calls until you say go": "Sin llamadas del concesionario hasta que tú digas",
    "Your brief · example": "Tu resumen · ejemplo",
    ">Ready<": ">Listo<",
    ">Want<": ">Quiero<",
    "Ram 1500, pre-owned": "Ram 1500, seminuevo",
    ">Afford<": ">Puedo pagar<",
    "$500/mo · $2,000 down": "$500/mes · $2,000 de enganche",
    ">Trade<": ">A cuenta<",
    "Yes — details ready": "Sí — datos listos",
    ">Walk-away<": ">Me retiro si<",
    "Anything over $540/mo": "Pasa de $540/mes",
    "8,000+ five-star reviews": "8,000+ reseñas de cinco estrellas",
    "from real customers": "de clientes reales",
    "Customers served": "Clientes atendidos",
    "Five-star reviews": "Reseñas de cinco estrellas",
    "60 sec": "60 seg",
    "Average time to complete": "Tiempo promedio para completarlo",
    "Cost to submit a request": "Costo de enviar una solicitud",

    # story
    "I · The truck": "I · La camioneta",
    "The 90-second read": "Lectura de 90 segundos",
    "Two years ago, I spent six Saturdays buying a truck. I’m still angry about it.":
        "Hace dos años pasé seis sábados comprando una camioneta. Todavía me da coraje.",
    "Not at the dealer.": "No con el concesionario.",
    "At myself.": "Conmigo mismo.",
    "Because I did everything “right.”": "Porque hice todo “bien”.",
    "I compared. I haggled. I walked out twice.": "Comparé. Regateé. Me salí dos veces.",
    "I brought my brother-in-law — the one who “knows cars.”":
        "Llevé a mi cuñado, el que “sabe de autos”.",
    "Forty-eight hours of my life. Gone.": "Cuarenta y ocho horas de mi vida. Perdidas.",
    "And three weeks later, I found out a guy two exits up the 5 paid":
        "Y tres semanas después supe que un señor a dos salidas por la 5 pagó",
    "$3,400 less": "$3,400 menos",
    "for the exact same truck.": "por exactamente la misma camioneta.",
    "Same color.": "Mismo color.",
    "Same packages.": "Mismos paquetes.",
    "Same bank.": "Mismo banco.",
    "Same Tuesday afternoon.": "La misma tarde de martes.",
    "II · Three questions": "II · Tres preguntas",
    "Here’s what still eats at me:": "Esto es lo que todavía me carcome:",
    "He wasn’t smarter.": "No era más listo.",
    "He wasn’t a “better negotiator.”": "No era “mejor negociador”.",
    "He just knew three things before he walked in that I didn’t know until I walked out.":
        "Solo sabía tres cosas antes de entrar que yo no supe hasta que salí.",
    "What he ": "Lo que él ",
    "actually wanted.": "de verdad quería.",
    "What he could ": "Lo que él ",
    "actually afford.": "de verdad podía pagar.",
    "What his trade-in was ": "Lo que su auto a cuenta ",
    "actually worth.": "de verdad valía.",
    "That’s it. Three questions.": "Eso es todo. Tres preguntas.",
    "Answered before the first “let me talk to my manager.”":
        "Respondidas antes del primer “déjame hablar con mi gerente”.",
    "Skip the story — start my 60-second request ↗":
        "Saltar la historia — empezar mi solicitud de 60 segundos ↗",
    "Free · No credit check · No dealership calls unless you say go.":
        "Gratis · Sin revisión de crédito · Sin llamadas del concesionario a menos que lo pidas.",

    # the math
    "The math nobody shows you": "Las cuentas que nadie te muestra",
    "Shopping without a plan isn’t free.": "Buscar sin un plan no es gratis.",
    "It just doesn’t show up on the invoice.": "Solo que no aparece en la factura.",
    "Lost weekends": "Fines de semana perdidos",
    "The average buyer visits 3–4 dealerships and still leaves unsure.":
        "El comprador promedio visita 3–4 concesionarios y aun así se va con dudas.",
    "Left on the table": "Dinero dejado en la mesa",
    "What people typically give up when they negotiate without knowing the numbers first.":
        "Lo que la gente suele perder al negociar sin conocer los números primero.",
    "11 days": "11 días",
    "Decision drag": "Decisión estancada",
    "Time spent “thinking about it” — because nobody ever gave you a clear answer.":
        "Tiempo “pensándolo”, porque nadie te dio nunca una respuesta clara.",
    "Your time is worth more than ": "Tu tiempo vale más que ",
    "free coffee and a folding chair.": "un café gratis y una silla plegable.",

    # the fix
    "III · The fix": "III · La solución",
    "So we built the thing I wish someone had handed me at that first dealership.":
        "Así que creamos lo que me hubiera gustado que alguien me diera en aquel primer concesionario.",
    "Eight short screens. Sixty seconds, honestly.":
        "Ocho pantallas cortas. Sesenta segundos, de verdad.",
    "The same three questions — plus five follow-ups every good salesperson would ask you anyway.":
        "Las mismas tres preguntas, más cinco que cualquier buen vendedor te haría de todos modos.",
    "You answer them in private. Before anyone’s selling you anything.":
        "Las respondes en privado. Antes de que alguien te venda algo.",
    "Then you walk in different.": "Luego entras distinto.",
    "Not with a pitch.": "No con un discurso.",
    "With a brief.": "Con un resumen.",
    "You know the number. You know the trade.":
        "Sabes el número. Sabes cuánto vale tu auto.",
    "You know the walk-away.": "Sabes cuándo retirarte.",
    "You know what you’ll say yes to — and what you’ll laugh at.":
        "Sabes a qué vas a decir que sí y de qué te vas a reír.",
    "The people who win at this aren’t smarter. They’re just prepared.":
        "Los que ganan en esto no son más listos. Solo llegan preparados.",
    "Sixty seconds now. Six Saturdays back.": "Sesenta segundos ahora. Seis sábados de vuelta.",
    "— The 60 Minute Car Deals team": "— El equipo de 60 Minute Car Deals",
    "Built for Californians who’d rather be driving.":
        "Hecho para californianos que prefieren estar manejando.",

    # how it works
    "Less hassle. More driving.": "Menos complicaciones. Más manejar.",
    "Your next car, in three steps.": "Tu próximo auto, en tres pasos.",
    "Tell us what you want": "Dinos qué quieres",
    "Eight quick screens — vehicle, budget, trade-in, timeline. Most people finish in under 60 seconds.":
        "Ocho pantallas rápidas: vehículo, presupuesto, auto a cuenta y plazo. La mayoría termina en menos de 60 segundos.",
    "See your matches": "Mira tus opciones",
    "Review vehicles and real numbers that fit your budget, your timeline and your situation.":
        "Revisa vehículos y números reales que encajan con tu presupuesto, tu plazo y tu situación.",
    "Walk in ready": "Llega preparado",
    "You already know what you want and what you won’t accept. Confirm the details and drive.":
        "Ya sabes qué quieres y qué no vas a aceptar. Confirma los detalles y maneja.",

    # form shell + confirmation fallback
    "Your vehicle request": "Tu solicitud de vehículo",
    "Write your brief.": "Escribe tu resumen.",
    "Your request is in.": "Tu solicitud ya está enviada.",
    "It is with our team now. We will reply to the email you gave us.":
        "Ya está con nuestro equipo. Te responderemos en español al correo que nos diste.",
    "We read your request and match it to real vehicles.":
        "Leemos tu solicitud y la comparamos con vehículos reales.",
    "You get real numbers back by email — no dealership calls until you say go.":
        "Recibes números reales por correo, sin llamadas del concesionario hasta que tú digas.",
    "Compare against the budget you set, not the one you’re sold.":
        "Compara con el presupuesto que tú pusiste, no con el que te quieren vender.",
    "Start another request": "Empezar otra solicitud",

    # testimonials
    "People who stopped guessing": "Gente que dejó de adivinar",
    "They walked in already knowing.": "Entraron ya sabiendo.",
    "Real outcomes start with a clear request. Here’s what that looks like.":
        "Los buenos resultados empiezan con una solicitud clara. Así se ve.",
    "“I filled it out on my lunch break in Koreatown. Walked in Saturday, knew exactly what I wanted and what my trade was worth. Out in two hours.”":
        "“Lo llené en mi hora de comida en Koreatown. Llegué el sábado sabiendo exactamente qué quería y cuánto valía mi auto. Salí en dos horas.”",
    "“The budget screen was the wake-up call. I was shopping $80/month too high. That one answer changed the whole search.”":
        "“La pantalla del presupuesto me abrió los ojos. Estaba buscando $80 al mes por encima. Esa sola respuesta cambió toda la búsqueda.”",
    "“First time buying without my dad. The request sheet made me feel like I wasn’t walking in blind. No one talked me into anything.”":
        "“Primera vez comprando sin mi papá. La solicitud hizo que no entrara a ciegas. Nadie me convenció de nada.”",

    # comparison
    "Two ways to buy a car": "Dos formas de comprar un auto",
    "A little preparation. A much smoother experience.":
        "Un poco de preparación. Una experiencia mucho más fácil.",
    "The usual back-and-forth": "El ir y venir de siempre",
    "Start searching without a clear plan": "Empezar a buscar sin un plan claro",
    "Repeat your preferences at every visit": "Repetir tus preferencias en cada visita",
    "Work through every detail on arrival": "Resolver cada detalle al llegar",
    "Spend hours considering unsuitable vehicles": "Pasar horas viendo vehículos que no te sirven",
    "Find out your trade value last": "Enterarte al final de cuánto vale tu auto",
    "The 60 Minute approach": "El método 60 Minute",
    "Share your preferences before visiting": "Compartir tus preferencias antes de visitar",
    "Focus only on vehicles that fit your needs": "Ver solo vehículos que encajan contigo",
    "Know your budget before you walk in": "Saber tu presupuesto antes de entrar",
    "Arrive with a clear next step": "Llegar con un siguiente paso claro",
    "Bring your trade-in details up front": "Traer los datos de tu auto a cuenta desde el inicio",

    # deliveries
    "Real deliveries": "Entregas reales",
    "People who stopped shopping.": "Gente que dejó de buscar.",
    "Every one of these started with the same 60-second request you are about to write.":
        "Cada una empezó con la misma solicitud de 60 segundos que estás por escribir.",
    "Picked it up the same week.": "Lo recogió esa misma semana.",
    "Keys in hand, no haggling.": "Llaves en mano, sin regateo.",
    "Two names on one happy day.": "Dos nombres en un día feliz.",
    "First car, done in an afternoon.": "Primer auto, resuelto en una tarde.",
    "Traded in and drove home.": "Entregó el suyo y se fue manejando.",
    "Found the number that worked.": "Encontró el número que le funcionaba.",
    "Real customers photographed at delivery, used with permission. Vehicles shown have been sold and do not represent current inventory.":
        "Clientes reales fotografiados en la entrega, con su permiso. Los vehículos mostrados ya se vendieron y no representan el inventario actual.",

    # zero risk
    ">Zero<": ">Cero<",
    ">Risk<": ">Riesgo<",
    ">Request<": ">Solicitud<",
    "Your request costs nothing. Literally.": "Tu solicitud no cuesta nada. Literalmente.",
    "No payment. No credit pull. No obligation. No dealership calls unless you decide you want them. If it isn’t useful, close the tab — nothing happens.":
        "Sin pago. Sin consulta de crédito. Sin compromiso. Sin llamadas del concesionario a menos que tú las quieras. Si no te sirve, cierra la pestaña y no pasa nada.",

    # faq
    "Good questions": "Buenas preguntas",
    "Before you get started.": "Antes de empezar.",
    "Does completing the form affect my credit?": "¿Llenar el formulario afecta mi crédito?",
    "No. This form does not run a credit check of any kind. Any future credit application requires a separate process and your explicit authorization.":
        "No. Este formulario no hace ninguna revisión de crédito. Cualquier solicitud de crédito futura requiere un proceso aparte y tu autorización expresa.",
    "Can I trade in my current vehicle?": "¿Puedo entregar mi auto actual a cuenta?",
    "Yes. Select the trade-in option in the form. Final valuation depends on an appraisal, vehicle condition, mileage and other details.":
        "Sí. Elige la opción de auto a cuenta en el formulario. El valor final depende de un avalúo, el estado del vehículo, el kilometraje y otros detalles.",
    "Is a 60-minute purchase guaranteed?": "¿Garantizan una compra en 60 minutos?",
    "No. Completion time depends on vehicle availability, financing, documentation and your individual circumstances. What we can promise is that you’ll arrive prepared.":
        "No. El tiempo depende de la disponibilidad del vehículo, el financiamiento, la documentación y tu situación. Lo que sí prometemos es que llegarás preparado.",
    "Can I browse both new and used vehicles?": "¿Puedo ver vehículos nuevos y seminuevos?",
    "Yes. Choose new, pre-owned, or open to both when completing your request.":
        "Sí. Elige nuevo, seminuevo o ambos al llenar tu solicitud.",
    "What happens to my information?": "¿Qué pasa con mi información?",
    "Your answers stay on your own device while you fill the form in. When you press send on the last step, they are emailed to our team so we can match your request — and nowhere else. We do not sell your details, and no dealership calls you until you tell us to.":
        "Tus respuestas se quedan en tu dispositivo mientras llenas el formulario. Al presionar enviar en el último paso, llegan por correo a nuestro equipo para poder atender tu solicitud, y a ningún otro lado. No vendemos tus datos y ningún concesionario te llama hasta que tú lo pidas.",
    "How long does it actually take?": "¿Cuánto tarda en realidad?",
    "Most people finish all eight screens in under 60 seconds. You can go back and change any answer at any time.":
        "La mayoría termina las ocho pantallas en menos de 60 segundos. Puedes regresar y cambiar cualquier respuesta cuando quieras.",

    # footer / sticky bar
    "Your next vehicle starts here.": "Tu próximo vehículo empieza aquí.",
    "Tell us what you’re looking for. Walk in knowing the answer.":
        "Dinos qué buscas. Llega sabiendo la respuesta.",
    "60-second form": "Formulario de 60 seg",

    # footer legal
    "Demonstration website. Vehicle availability, pricing, financing and completion times are subject to confirmation. Statistics, testimonials and live activity shown on this page are illustrative placeholders for design demonstration and do not represent verified customer data. This website is not affiliated with or endorsed by Meta or Facebook.":
        "Sitio de demostración. La disponibilidad de vehículos, los precios, el financiamiento y los tiempos están sujetos a confirmación. Las estadísticas, los testimonios y la actividad en vivo que aparecen en esta página son ejemplos ilustrativos de diseño y no representan datos verificados de clientes. Este sitio no está afiliado ni respaldado por Meta o Facebook.",

    # Must sit in COPY, not WIZARD: it contains "No dealership calls until you
    # say go" as a substring, and COPY runs first. Length-sorted within one pass
    # guarantees this longer string is replaced before the fragment inside it.
    "'Sent straight to our team. No dealership calls until you say go.'":
        "'Va directo a nuestro equipo. Sin llamadas del concesionario hasta que tú digas.'",
}

# Wizard strings live inside the x-dc <script>, quoted. Replaced with their
# quotes attached so a bare word cannot match marketing copy elsewhere.
WIZARD = {
    "'First — what do you want to drive?'": "'¿Qué quieres manejar?'",
    "'Start with your ideal vehicle. A second choice is optional.'":
        "'Empieza con tu vehículo ideal. La segunda opción no es obligatoria.'",
    "'Preferred make and model'": "'Marca y modelo preferido'",
    "'e.g. Ram 1500'": "'ej. Ram 1500'",
    "'Another vehicle you like'": "'Otro vehículo que te guste'",
    "'Optional'": "'Opcional'",
    "'Do you have a trade-in?'": "'¿Tienes un auto a cuenta?'",
    # Used as an option value on two screens (trade-in and financing history).
    # 'No' is identical in Spanish, so only 'Yes' needs mapping.
    "'Yes'": "'Sí'",

    "'Now let’s talk budget.'": "'Ahora hablemos del presupuesto.'",
    "'A rough estimate is all we need — it narrows the search instantly.'":
        "'Con un estimado basta; acota la búsqueda al instante.'",
    "'Target monthly payment ($)'": "'Pago mensual deseado ($)'",
    "'e.g. 500'": "'ej. 500'",
    "'How would you like to purchase?'": "'¿Cómo te gustaría comprar?'",
    "'Finance'": "'Financiamiento'",
    "'Lease'": "'Arrendamiento'",
    "'Pay cash'": "'Pago de contado'",
    "'Which vehicles are you considering?'": "'¿Qué vehículos estás considerando?'",
    "'New'": "'Nuevo'",
    "'Pre-owned'": "'Seminuevo'",
    "'Open to both'": "'Ambos'",

    "'When do you want to be driving it?'": "'¿Cuándo quieres estar manejándolo?'",
    "'Choose a timeline that matches your real life.'": "'Elige un plazo realista para ti.'",
    "'Estimated down payment ($)'": "'Enganche estimado ($)'",
    "'e.g. 2000'": "'ej. 2000'",
    "'Your timeline'": "'Tu plazo'",
    "'Today'": "'Hoy'",
    "'Within 7 days'": "'En 7 días'",
    "'Within 30 days'": "'En 30 días'",
    "'Just exploring'": "'Solo explorando'",

    "'A little about your situation.'": "'Un poco sobre tu situación.'",
    "'Pick the option that fits best. Nothing here is a credit check.'":
        "'Elige la opción que mejor te describa. Nada de esto es una revisión de crédito.'",
    "'Employment status'": "'Situación laboral'",
    "'Employed'": "'Empleado'",
    "'Self-employed'": "'Trabajo por mi cuenta'",
    "'Retired'": "'Jubilado'",
    "'Other'": "'Otro'",
    "'Time in your current situation'": "'Tiempo en tu situación actual'",
    "'Under 6 months'": "'Menos de 6 meses'",
    "'6–12 months'": "'6–12 meses'",
    "'1–2 years'": "'1–2 años'",
    "'2+ years'": "'Más de 2 años'",

    "'Your estimated income range.'": "'Tu rango de ingresos estimado.'",
    "'An estimate is enough. This is not a credit application.'":
        "'Un estimado es suficiente. Esto no es una solicitud de crédito.'",
    "'Monthly income before deductions'": "'Ingreso mensual antes de deducciones'",
    "'Under $3,000'": "'Menos de $3,000'",
    "'Over $6,000'": "'Más de $6,000'",
    "'Prefer to discuss'": "'Prefiero comentarlo'",

    "'How would you describe your credit?'": "'¿Cómo describirías tu crédito?'",
    "'An estimate is fine — or discuss it later.'": "'Un estimado está bien, o lo vemos después.'",
    "'Estimated credit range'": "'Rango de crédito estimado'",
    "'Excellent'": "'Excelente'",
    "'Good'": "'Bueno'",
    "'Fair'": "'Regular'",
    "'Rebuilding'": "'En recuperación'",
    "'Not sure'": "'No estoy seguro'",
    "'Have you financed or leased before?'": "'¿Has financiado o arrendado antes?'",
    "'First-time buyer'": "'Es mi primera vez'",

    "'Where are you shopping?'": "'¿ Dónde estás buscando?'",
    "'So we narrow the search to somewhere you’d actually drive to.'":
        "'Para acotar la búsqueda a un lugar al que de verdad irías.'",
    "'Street address'": "'Dirección'",
    "'123 Main St'": "'Calle y número'",
    "'Date of birth (optional — helps us pre-check financing)'":
        "'Fecha de nacimiento (opcional — nos ayuda a revisar el financiamiento)'",
    "'City'": "'Ciudad'",
    "'Your city'": "'Tu ciudad'",
    "'State or province'": "'Estado'",
    "'ZIP or postal code'": "'Código postal'",

    "'Last step — where do we send your matches?'":
        "'Último paso: ¿a dónde te enviamos tus opciones?'",
    "'You’re one click from a finished, personal vehicle request.'":
        "'Estás a un clic de terminar tu solicitud personalizada.'",
    "'Full name'": "'Nombre completo'",
    "'Your name'": "'Tu nombre'",
    "'Email address'": "'Correo electrónico'",
    "'Phone number'": "'Número de teléfono'",
    "'Your phone number'": "'Tu teléfono'",
    "'I agree that 60 Minute Car Deals can contact me by email or phone about this request.'":
        "'Acepto que 60 Minute Car Deals me contacte por correo o teléfono sobre esta solicitud.'",

    # runtime strings
    "'One quick answer needed above — then you’re straight through.'":
        "'Falta una respuesta arriba y seguimos.'",
    "'We could not send your request. Please try again.'":
        "'No pudimos enviar tu solicitud. Inténtalo de nuevo.'",
    "'Network problem — your answers are safe. Please try again.'":
        "'Problema de conexión. Tus respuestas están guardadas. Inténtalo de nuevo.'",
    "'Sending…'": "'Enviando…'",
    "'Send my request →'": "'Enviar mi solicitud →'",
    "'Continue →'": "'Continuar →'",
    "'Last one'": "'La última'",
    "'Answers saved on this device. You can leave and come back.'":
        "'Respuestas guardadas en este dispositivo. Puedes salir y volver.'",
    "'Your answers stay on this device until you send them.'":
        "'Tus respuestas se quedan en este dispositivo hasta que las envíes.'",
    "`Step ${step + 1} of ${SCREENS.length}`": "`Paso ${step + 1} de ${SCREENS.length}`",
    "`${left} to go`": "`faltan ${left}`",
}

EN_URL = "https://usedcarssimivalley.com/"
ES_URL = "https://usedcarssimivalley.com/es"

ES_TITLE = "60 Minute Car Deals — Deja de buscar. Empieza a manejar."
ES_DESC = ("Dinos qué quieres manejar en 60 segundos. Lo comparamos con vehículos y "
           "números reales en California: sin revisión de crédito, aceptamos tu auto a "
           "cuenta y nadie te llama hasta que tú digas.")


def build(src):
    out = src
    missing = []

    for mapping in (COPY, WIZARD):
        for en in sorted(mapping, key=len, reverse=True):
            if en not in out:
                missing.append(en)
            out = out.replace(en, mapping[en])

    # document language
    out = out.replace('<html lang="en">', '<html lang="es">', 1)

    # head: title, description, canonical, og/twitter
    out = re.sub(r"<title>[^<]*</title>",
                 "<title>%s</title>" % ES_TITLE, out, count=1)
    out = re.sub(r'(<meta name="description" content=")[^"]*(">)',
                 lambda m: m.group(1) + ES_DESC + m.group(2), out, count=1)
    out = re.sub(r'(<meta property="og:title" content=")[^"]*(">)',
                 lambda m: m.group(1) + ES_TITLE + m.group(2), out, count=1)
    out = re.sub(r'(<meta property="og:description" content=")[^"]*(">)',
                 lambda m: m.group(1) + ES_DESC + m.group(2), out, count=1)
    out = re.sub(r'(<meta name="twitter:title" content=")[^"]*(">)',
                 lambda m: m.group(1) + ES_TITLE + m.group(2), out, count=1)
    out = re.sub(r'(<meta name="twitter:description" content=")[^"]*(">)',
                 lambda m: m.group(1) + ES_DESC + m.group(2), out, count=1)
    out = out.replace('<link rel="canonical" href="%s">' % EN_URL,
                      '<link rel="canonical" href="%s">' % ES_URL, 1)
    out = out.replace('<meta property="og:url" content="%s">' % EN_URL,
                      '<meta property="og:url" content="%s">' % ES_URL, 1)
    out = out.replace('<meta property="og:locale" content="en_US">',
                      '<meta property="og:locale" content="es_US">', 1)

    # Separate storage key: a half-finished English run must not restore into
    # the Spanish form, where the stored choice values would not match any option.
    out = out.replace("const KEY = 'cmcd_request_v3';",
                      "const KEY = 'cmcd_request_v3_es';", 1)

    # Spanish confirmation page
    out = out.replace("window.location.assign('/thank-you')",
                      "window.location.assign('/gracias')", 1)

    # Language switcher points back to English on the Spanish page.
    out = out.replace(
        '<a href="/es" hreflang="es" lang="es"',
        '<a href="/" hreflang="en" lang="en"', 1)
    out = out.replace('>Español</a>', '>English</a>', 1)

    # Tell the API which language the lead came from.
    out = out.replace("payload.pageUrl = location.href;",
                      "payload.pageUrl = location.href;\n    payload.lang = 'es';", 1)

    return out, missing


def main():
    src = io.open('index.html', encoding='utf-8').read()
    out, missing = build(src)
    io.open('es.html', 'w', encoding='utf-8', newline='\n').write(out)

    total = len(COPY) + len(WIZARD)
    print("es.html written: %d/%d strings applied" % (total - len(missing), total))
    for m in missing:
        print("  NOT FOUND IN index.html: %s" % m[:90])
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
