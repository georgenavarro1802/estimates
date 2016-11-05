#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import threading

from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

from estimates.settings import EMAIL_HOST_USER


def bad_json(mensaje=None, error=None, extradata=None):
    data = {'result': 'bad'}
    if mensaje:
        data.update({'mensaje': mensaje})
    if error:
        if error == 0:
            data.update({"mensaje": u"Solicitud incorrecta."})
        elif error == 1:
            data.update({"mensaje": u"Error al guardar los datos."})
        elif error == 2:
            data.update({"mensaje": u"Error al eliminar los datos."})
        elif error == 3:
            data.update({"mensaje": u"Error al obtener los datos."})
        elif error == 4:
            data.update({"mensaje": u"No tiene permisos para realizar esta acción."})
        elif error == 5:
            data.update({"mensaje": u"Error al generar la información."})
        else:
            data.update({"mensaje": u"Error en el sistema."})
    if extradata:
        data.update(extradata)
    return HttpResponse(json.dumps(data), content_type="application/json")


def ok_json(data=None, simple=None):
    if data:
        if not simple:
            if 'result' not in data.keys():
                data.update({"result": "ok"})
    else:
        data = {"result": "ok"}
    return HttpResponse(json.dumps(data), content_type="application/json")


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list, replyto=None):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.replyto = replyto
        threading.Thread.__init__(self)

    def run (self):
        try:
            headers = {}
            if self.replyto:
                headers['Reply-To'] = self.replyto
            msg = EmailMessage(self.subject, self.html_content, EMAIL_HOST_USER, self.recipient_list, headers=headers)
            msg.content_subtype = "html"
            msg.send()
        except:
            pass


def send_html_mail(subject, html_template, data, recipient_list, replyto=None):

    template = get_template(html_template)
    d = Context(data)
    html_content = template.render(d)

    EmailThread(subject, html_content, recipient_list, replyto).start()
