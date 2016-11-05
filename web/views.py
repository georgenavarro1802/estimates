# Create your views here.
import json
from datetime import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response

from estimates.settings import CONTACT_EMAILS1, EMAIL_ACTIVE
from web.funciones import send_html_mail, ok_json, bad_json
from web.models import Customer, Element, Estimation, EstimationDetail


def addUserData(request, data):
    data["title"] = "Willys Paint & Body Shop of Miami Inc."
    data["title_short"] = "Willys P&B Inc."
    data["footer_text"] = "All rights reserved"
    data['current_time'] = datetime.now()
    data['usuario'] = request.user


def index(request):
    data = {}
    addUserData(request, data)
    if request.method == 'POST':
        user = authenticate(username=request.POST['user'].lower(), password=request.POST['passw'])
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/customers")
        else:
            return HttpResponseRedirect("/?error=1")

    data["error"] = True if 'error' in request.GET else ""
    return render_to_response('index.html', data)


@login_required(redirect_field_name='ret', login_url='/')
def customers(request):
    data = {}
    addUserData(request, data)
    data["customers"] = Customer.objects.all()
    return render_to_response('customers.html', data)


@login_required(redirect_field_name='ret', login_url='/')
def newcustomer(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                name = request.POST['name']
                phone = request.POST['phone']
                email = request.POST['email']
                if Customer.objects.filter(name=name).exists():
                    return bad_json(mensaje="Exists another customer with that name.")
                customer = Customer(name=name,
                                    phone=phone,
                                    email=email)
                customer.save()
                return ok_json()
        except:
            return bad_json(error=1)

    return render_to_response('newcustomer.html')


@login_required(redirect_field_name='ret', login_url='/')
def elements(request):
    data = {}
    addUserData(request, data)
    data['customer'] = Customer.objects.get(pk=request.GET['id'])
    data["elements"] = Element.objects.all()
    return render_to_response('elements.html', data)


@login_required(redirect_field_name='ret', login_url='/')
def hours(request):
    data = {}
    addUserData(request, data)
    data['customer'] = Customer.objects.get(pk=request.GET['id'])
    data['lista_ids'] = request.GET['lista']
    lista_elements = []
    for l in request.GET['lista'].split(","):
        element = Element.objects.get(pk=int(l))
        lista_elements.append(element)
    data['lista_elements'] = lista_elements
    return render_to_response('hours.html', data)


@login_required(redirect_field_name='ret', login_url='/')
def estimations(request):
    data = {}
    addUserData(request, data)
    if request.method == 'POST':
        estimation = Estimation.objects.get(pk=request.POST['ide'])
        estimation.valid = True
        estimation.discount_value = float(request.POST['discount'])
        estimation.save()

        # Delete not valid estimations
        Estimation.objects.filter(valid=False).delete()

        # Send Email
        if EMAIL_ACTIVE:
            send_html_mail(u"ESTIMATION - WILLY'S BODY SHOP APP", "emails/estimation.html",
                           {'estimation': estimation}, [CONTACT_EMAILS1])
        return HttpResponseRedirect("/customers")

    data['customer'] = customer = Customer.objects.get(pk=request.GET['id'])
    data['lista_ids'] = request.GET['lista_ids']
    lista_elements = json.loads(request.GET['lista'])

    estimation = Estimation(customer=customer)
    estimation.save()
    for elem in lista_elements:
        element = Element.objects.get(pk=int(elem['ide']))
        service_type = int(elem['listae'][0])
        hrs_labor = int(elem['listae'][1])
        hrs_refinish = int(elem['listae'][2])
        hrs_frame = int(elem['listae'][3])
        hrs_mechanical = int(elem['listae'][4])
        hrs_paint = int(elem['listae'][5])

        estimation_detail = EstimationDetail(estimation=estimation,
                                             element=element,
                                             service_type=service_type,  # 1 - Repair, 2 - Replace
                                             hrs_labor=hrs_labor,
                                             hrs_refinish=hrs_refinish,
                                             hrs_frame=hrs_frame,
                                             hrs_mechanical=hrs_mechanical,
                                             hrs_paint=hrs_paint)
        estimation_detail.save()

    estimation.save()  # recalcula totales hrs and value of the estimation
    data['estimation'] = estimation
    return render_to_response('estimation.html', data)
