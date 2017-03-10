# drchrono Hackathon

## Birthday Greetings Project

Birthday Greetings Project automates birthday greetings for a drchrono doctor using the drchrono API.

**Brief:** How awesome would it be to get a text or email from your doctor wishing you a Happy Birthday? Let's have you create a fun birthday reminder system to tell patients it's their birthday, e.g. Happy bday from Dr Smith!

### Notes

**Parts that may be interesting might include the analysis of the brief and subsequent design and user experience, the minimal data storage, and checks for scope grants.**

Implicit in the brief is the view that it is permissible and reasonable to (1) reveal the patient's birthday over text or email (with the associated consequences of outdated/incorrect contact information) and (2) to utilize the doctor's communication channel for this (non-medical) purpose.

For such a system, likely envisioned to elicit joy on behalf of the patient and contribute to the relationship, there are various base considerations and also use considerations that may not be apparent until the system is utilized.

As a result, this project is built to be a MVP, a minimum viable product, that can be revised in accordance to user feedback.

### Base considerations

 1. Behavior for February 29 birthdays on non-leap years: contact on February 28 for now.
 2. Multiple service providers may be in contact with a patient at a medical practice: have the birthday greeting be from the primary doctor on behalf of the primary doctor and "their colleagues". A clinic-based message with the appropriate names will not include doctors that are not part of the patient's record while nurses and reception staff may also have a connection to a patient. Automated inclusion of names will create a need to filter for those who are no longer with the office and may also include a doctor the patient did not prefer (unlikely to be an issue for their primary doctor). Further, per the API documentation (https://observer.drchrono.com/api-docs/popup/v2016_06/scope), it is suggested that summary version of the patient scope is sufficient for this task. However, contact information is not returned in that scope.
 3. If yearly birthday messages were configured by the clinic, there is a reasonable possibility that the message maintenance would be overlooked/not occur at the appropriate time (e.g., patient receives two messages referencing the same event/content/promotion): a generic, timeless birthday message to begin.
 4. Some patients should not be contacted (e.g., contact declined, dead, under the care of a guardian, or require special handling): ideally, filter by status, avoiding inactive/dead, check preferred communications channel to see if declined. However, this relevant information does not appear to be accessible through the API. For those requiring special handling, allow the doctor or their associated staff to opt them out of the birthday notes. Also, communications need to be scheduled on the day to ensure status is current.
 5. The birthday information must be valid and present: skip if not present. In the future, consider flagging birthdays that were in the future at any time of the checks, OK if no year listed. Consider for the timezone for the recipient later, acting based on UTC for now.
 6. The recipient may have a preferred language and communication channel: future issue. The API does not expose the preferred communication channel and English should be fine as a start.
 7. A patient might have no assigned doctor: skip if no assigned doctor.
 8. The drchrono API does not have an ad-hoc messaging method and it appears that messages can only be associated with appointments and it would not be appropriate to create dummy appointments to message birthday greetings: use external service providers for email and SMS.

### Implementation

From these base considerations, there should be components to handle:

1. Login with drchrono OAuth provider
2. Options to activate/deactivate messaging and an opt-out patients for personal handling with some patient information (e.g., view greeting history, see patients with invalid DOBs that have been skipped). The activation piece is designed involve contact from the user to ensure that the automated nature of the system (and its limitations) is understood.
3. A scheduled helper utility to send messages

### Requirements
- [pip](https://pip.pypa.io/en/stable/)
- [python virtual env](https://packaging.python.org/installing/#creating-and-using-virtual-environments)

### Setup
``` bash
$ virtualenv drchrono-project
```
Register for a drchrono API account and retrieve API key and secrets while specifying the redirect URL. Export the key and secret under environmental variables `SOCIAL_AUTH_DRCHRONO_KEY` and `SOCIAL_AUTH_DRCHRONO_SECRET`.
```
$ source drchrono-project/bin/activate
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py runserver
```
Build prerequisites may be needed for the cryptography python package (needed for twilio to send SMS).
Set up a daily cron job for `python manage.py dispatch_messages`.

### TODO for production
1. Set up a scheduled task to use the user's access token to update patient information
2. Turn debug off: Set DEBUG = False in settings.py
3. Update site URL for LOGIN_REDIRECT_URL in settings.py and on API registration
4. Update SECRET_KEY in settings.py to new value
5. Deploy site on SSL and set secure cookie flags
6. Disable logging in settings.py
7. Implement handler for SMS and e-mail delivery failures and do not mark as having been sent
8. More graceful error handling for API response failures
9. Add consistency checks to deactivate removed patients
10. Investigate patient pagination race condition possibility
11. Consider enhancing patient listing information (less data held is better and in any case, master data is held by drchrono and users cannot modify attributes through this interface)
12. Configure live e-mail backend and update Twilio credentials for SMS (both in `dispatch_messages.py`)
13. Create testing plan and add sensible automated tests
