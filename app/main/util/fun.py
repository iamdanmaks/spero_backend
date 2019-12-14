import datetime
from datetime import datetime
from datetime import date

from scipy import signal
from statistics import mean

from flask_babel import gettext


def age(born):
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def preprocess(audio, sample_rate, filter_type):
    if filter_type == 'lowpass':
        n = 100
        b = [1.0 / n] * n
        a = 0.912
        audio = signal.lfilter(b, a, audio)
    
    elif filter_type == 'butterfilt':
        filt_ord  = 6
        cuttoff = 0.006
        B, A = signal.butter(filt_ord, cuttoff, output='ba')
        audio = signal.filtfilt(B,A, audio)

    return audio


def group_diagnoses(diagnoses):
    groups = set(map(lambda x:x.checked_on.date(), diagnoses))
    return [[y for y in diagnoses if y.checked_on.date() == x] for x in groups]


def decode_result(result, scrape):
    if result == 0 and scrape:
        return gettext('heart+healthy')
    elif result == 0 and not scrape:
        return gettext('Normal heartbeat')
    elif result == 1 and scrape:
        return gettext('murmur')
    elif result == 1 and not scrape:
        return gettext('Murmur')
    elif result == 2 and scrape:
        return gettext('extrasystole')
    elif result == 2 and not scrape:
        return gettext('Extrasystole')


def stats(grouped):
    return [
        {
            _[0].checked_on.strftime('%d.%m.%Y'): [
                mean([x.normal_probability for x in _]),
                mean([x.murmur_probability for x in _]),
                mean([x.extrasystole_probability for x in _])
            ]
        } for _ in grouped
    ]


def password_validate(password, password_repeat):
    if len(password) < 6 or len(password) > 30:
        return {
            'validity': False,
            'answer': {
                'status': 'fail',
                'message': gettext('Password length should be greater \
                    than 6 and less than 30 symbols')
            }
        }
    
    elif not any(char.isdigit() for char in password): 
        return {
            'validity': False,
            'answer': {
                'status': 'fail',
                'message': gettext('Password should have at least one \
                    numeral value')
            }
        }
          
    elif not any(char.isupper() for char in password): 
        return {
            'validity': False,
            'answer': {
                'status': 'fail',
                'message': gettext('Password should have at least one \
                    uppercase letter')
            }
        }
    
    elif not any(char.islower() for char in password): 
        return {
            'validity': False,
            'answer': {
                'status': 'fail',
                'message': gettext('Password should have at least one \
                    lowercase letter')
            }
        }
    
    elif password.lower() == 'qwerty':
        return {
            'validity': False,
            'answer': {
                'status': 'fail',
                'message': gettext('Password is too common')
            }
        }
    
    elif password != password_repeat:
        return {
            'validity': False,
            'answer': {
                'status': 'fail',
                'message': gettext('Password first and second inputs are \
                    not equal')
            }
        }

    else:
        return {
            'validity': True
        }
