# -*- coding: utf-8 -*-
"""Generate gracias.html (Spanish confirmation) from thank-you.html.

Same contract as tools/make-es.py: the output is a committed artefact, and any
string in the map that no longer appears in the source is reported so the two
pages cannot silently drift.

    python tools/make-gracias.py
"""
import io
import sys

T = {
    "<title>Request received — 60 Minute Car Deals</title>":
        "<title>Solicitud recibida — 60 Minute Car Deals</title>",
    "Your vehicle request is in. We will reply by email with real vehicles and real numbers.":
        "Tu solicitud ya está enviada. Te responderemos por correo con vehículos y números reales.",
    '<html lang="en">': '<html lang="es">',
    "Your request is in.": "Tu solicitud ya está enviada.",
    "It is with our team now. We will reply to the email you gave us.":
        "Ya está con nuestro equipo. Te responderemos en español al correo que nos diste.",
    "We read your request and match it to real vehicles.":
        "Leemos tu solicitud y la comparamos con vehículos reales.",
    "You get real numbers back by email — no dealership calls until you say go.":
        "Recibes números reales por correo, sin llamadas del concesionario hasta que tú digas.",
    "Compare against the budget you set, not the one you&rsquo;re sold.":
        "Compara con el presupuesto que tú pusiste, no con el que te quieren vender.",
    "Back to 60 Minute Car Deals": "Volver a 60 Minute Car Deals",
    "No payment. No credit pull. No obligation.":
        "Sin pago. Sin consulta de crédito. Sin compromiso.",
    "'language': 'en'": "'language': 'es'",
    'href="/"': 'href="/es"',

    # testimonial wall
    "What people are saying": "Lo que dice la gente",
    "Unedited comments from real customers.":
        "Comentarios sin editar de clientes reales.",
    'alt="Customer comment about 60 Minute Car Deals"':
        'alt="Comentario de un cliente sobre 60 Minute Car Deals"',
}


def main():
    src = io.open('thank-you.html', encoding='utf-8').read()
    missing = [k for k in T if k not in src]

    out = src
    for k in sorted(T, key=len, reverse=True):
        out = out.replace(k, T[k])

    io.open('gracias.html', 'w', encoding='utf-8', newline='\n').write(out)
    print("gracias.html written: %d/%d strings applied" % (len(T) - len(missing), len(T)))
    for m in missing:
        print("  NOT FOUND IN thank-you.html: %s" % m[:90])
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
