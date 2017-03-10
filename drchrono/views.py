import datetime, pytz, requests

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from django.contrib.auth import logout

from drchrono.models import Doctor, Patient, SentMessages
from drchrono.forms import OptOutForm

def check_current_access(user):
    access_token = user.social_auth.get(provider = 'drchrono').extra_data['access_token']
    endpoint_list = ['https://drchrono.com/api/doctors','https://drchrono.com/api/patients']
    for endpoint in endpoint_list:
        response = requests.get(endpoint, headers = { 'Authorization': 'Bearer %s' % access_token})
        if response.status_code != 200:
            return False
    return True

def home(request):
    if request.user.is_authenticated():
        user_access_status = check_current_access(request.user)
        if user_access_status:
            return redirect('/app/')
        else:
            logout(request)
            return render(request, 'index.html', { 'user_access_status': user_access_status })
    else:
        return render(request, 'index.html', {})

@login_required()
@user_passes_test(check_current_access)
def app(request):
    #get token
    access_token = request.user.social_auth.get(provider = 'drchrono').extra_data['access_token']
    header = { 'Authorization': 'Bearer %s' % access_token }

    # determine current doctor and update db
    response = requests.get('https://drchrono.com/api/users/current', headers=header)
    if response.status_code != 200:
        # FIXME: access failure
        logout(request)
        return render(request, 'index.html', { 'user_access_status': False })

    data = response.json()
    doctor = {}
    doctor['id'] = data['doctor']

    response = requests.get('https://drchrono.com/api/doctors/'+str(doctor['id']), headers=header)

    if response.status_code != 200:
        # FIXME: access failure
        logout(request)
        return render(request, 'index.html', { 'user_access_status': False })

    data = response.json()
    doctor['first_name'] = data['first_name']

    try:
        savedDoctor = Doctor.objects.get(doctorRef=doctor['id'])
    except Doctor.DoesNotExist:
        # add doctor
        newDoctor = Doctor(doctorRef=doctor['id'], active='N', lastPatientsUpdate='1900-01-01', msg='Happy Birthday from Dr. '+doctor['first_name']+' and colleagues!')
        newDoctor.save()
    else:
        # update doctor
        # FIXME: only update on msg change
        savedDoctor.msg = 'Happy Birthday from Dr. '+doctor['first_name']+' and colleagues!'
        savedDoctor.save()

    # HACK: one accessor for now; possible race conditions
    savedDoctor = Doctor.objects.get(doctorRef=doctor['id'])

    # retrieve and update patients
    curDate = datetime.datetime.now()

    patients = []
    patients_url = 'https://drchrono.com/api/patients?doctor='+str(doctor['id'])+'&since='+str(savedDoctor.lastPatientsUpdate)

    # TODO: check status code
    while patients_url:
        data = requests.get(patients_url, headers=header).json()
        patients.extend(data['results'])
        patients_url = data['next'] # A JSON null on the last page

    for patient in patients:
        try:
            savedPatient = Patient.objects.get(patientRef=patient['id'])
        except Patient.DoesNotExist:
            newPatient = Patient(patientRef=patient['id'], doctor=savedDoctor, active='Y')
            newPatient.save()

        # HACK: possible race condition
        savedPatient = Patient.objects.get(patientRef=patient['id'])

        # FIXME: update preferences only if different
        if 'date_of_birth' in patient:
            savedPatient.bday = patient['date_of_birth']

        if 'email' in patient:
            savedPatient.email = patient['email']

        if 'cell_phone' in patient:
            savedPatient.mobile = patient['cell_phone']
            
        savedPatient.save()

    savedDoctor.lastPatientsUpdate = curDate
    savedDoctor.save()

    form = OptOutForm(request.POST or None)
    if form.is_valid():
        form_data = form.cleaned_data
        try:
            savedPatient = Patient.objects.get(patientRef=form_data['patientRef'])
        except Patient.DoesNotExist:
            # invalid request
            pass
        else:
            if form_data['action'] == 'Y':
                savedPatient.active = 'Y'
            else:
                savedPatient.active = 'N'
            savedPatient.save()

    # get fresh objects in case of concurrent updates
    drInstance = Doctor.objects.get(doctorRef=doctor['id'])
    return render(request, 'app.html', { 'doctor': drInstance, 'patients': Patient.objects.all().order_by("patientRef"), 'messages': SentMessages.objects.filter(doctor=drInstance).order_by("date") })

@login_required()
def leave(request):
    logout(request)
    return redirect('/')
