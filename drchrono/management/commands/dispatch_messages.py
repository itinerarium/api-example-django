from django.core.management.base import BaseCommand, CommandError

import datetime, pytz, calendar
from drchrono.models import Doctor, Patient, SentMessages
from django.core.mail import send_mail
from twilio.rest import Client

class Command(BaseCommand):
    help = 'Scheduled task to handle birthday greeting dispatch. To be run once a day.'

    def handle(self, *args, **options):
        # twilio handler
        account_sid = "{{ account_sid }}" # Your Account SID from www.twilio.com/console
        auth_token  = "{{ auth_token }}"  # Your Auth Token from www.twilio.com/console
        client = Client(account_sid, auth_token)

        # determine day
        now = datetime.datetime.now()
        recipientsTodayEmail = []
        recipientsTodaySMS = []

        # HACK: more efficient filtering with SQL?
        patients = Patient.objects.filter(bday__isnull=False, active='Y')

        # also accept 2/29 birthdays for today's mailing?
        accept229 = False
        # check if 2/28 on non-leap year
        if not calendar.isleap(now.year) and now.month == 2 and now.day == 28:
            # add in 2/29 in today's mailing
            accept229 = True

        # preferentially send to e-mail (async) over SMS (more urgent/realtime medium)
        for patient in patients:
            if patient.bday.month == now.month and patient.bday.day == now.day or (accept229 and patient.bday.month == now.month and patient.bday.day == 29):
                if patient.email:
                    recipientsTodayEmail.append(patient)
                elif patient.mobile:
                    recipientsTodaySMS.append(patient)

        counter = 0
        # send e-mails
        for patient in recipientsTodayEmail:
            # TODO: consider switching to send_mass_mail if volume is large
            send_mail('Happy Birthday!', patient.doctor.msg, 'drchrono-birthdays@example.com', [patient.email], fail_silently=True)

            message = SentMessages(doctor = patient.doctor, patient = patient, date = datetime.datetime.now(), medium = 'E-mail', msg = patient.doctor.msg)
            message.save()
            counter += 1

        # send SMS
        for patient in recipientsTodaySMS:
            message = client.messages.create(to=patient.mobile, from_="+12345678901", body=patient.doctor.msg)

            #FIXME: investigate function declaration in this environment to reduce duplicate?
            message = SentMessages(doctor = patient.doctor, patient = patient, date = datetime.datetime.now(), medium = 'SMS', msg = patient.doctor.msg)
            message.save()
            counter += 1

        self.stdout.write(str(counter)+' birthday greetings message(s) sent!')
