from app.main.model.user import Diagnosis, User
from app.main import db

#from ..util.confirm_heartbeat import evaluate
from ..util.pdf_generator import send_pdf
from ..util.scrapper import scrape
from ..util.decorator import token_checker
from flask.ext.babel import gettext

import uuid
from hashlib import sha384
from scipy.io.wavfile import write, read
import json
from werkzeug.utils import secure_filename
from librosa import resample
from numpy import int16

from flask import send_file

from datetime import datetime
import os


@token_checker
def create_diagnosis(token, data, file):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()

    try:
        data = json.load(data)
    except:
        response_object = {
            'status': 'fail',
            'messages': gettext('No json file')
        }
        return response_object, 400

    if data['normal_proba'] + data['murmur_proba'] + data['extrasystole_proba'] > 1.0:
        response_object = {
            'status': 'fail',
            'message': gettext('Wrong values of probabilities')
        }
        return response_object

    if data['result'] < 0 or data['result'] > 2:
        response_object = {
            'status': 'fail',
            'message': gettext('Wrong value of result')
        }
        return response_object, 400

    new_diagnosis = Diagnosis(
            result=data['result'],
            normal_probability=data['normal_proba'],
            murmur_probability=data['murmur_proba'],
            extrasystole_probability=data['extrasystole_proba'],
            public_id=str(uuid.uuid4()),
            user_id=user.id
        )
    
    answer = check_wav_file(file)

    if answer['valid']:
        write(
            filename='./app/main/uploads/' + generate_name(
                    public_id=new_diagnosis.public_id,
                    checked_on=datetime.utcnow()
                ) + '.wav',
            rate=16000,
            data=answer['audio']
        )
    
    else:
        return answer['response'], 400

    save_diagnosis(new_diagnosis, user)

    if not user.subscriber and len(user.diagnoses) > 5:
        clear_diagnoses(user)

    response_object = {
            'status': 'done',
            'message': gettext('Diagnosis is saved'),
            'diagnosis_id': new_diagnosis.public_id
        }

    return response_object, 201


def clear_diagnoses(user):
    filename = './app/main/uploads/' + generate_name(user.diagnoses[0].public_id, 
        user.diagnoses[0].checked_on) + '.wav'
    try:
        os.remove(filename)
        user.diagnoses = user.diagnoses[1:]
        db.session.commit()
    except OSError:
        pass


@token_checker
def return_diagnosis_audio(token, diagnosis_id):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()

    diagnosis = get_diagnosis(diagnosis_id)
    
    if not user:
        response_object = {
            'status': 'fail',
            'message': gettext('User does not exist')
        }
        return response_object, 404

    if not diagnosis:
        response_object = {
            'status': 'fail',
            'message': gettext('Diagnosis not found')
        }
        return response_object, 404

    if diagnosis.user_id == user.id:
        filename = 'uploads/' + generate_name(diagnosis_id, diagnosis.checked_on) + '.wav'

        print(filename)
        sr, test = read('./app/main/'+filename)
        print(sr, test)

        return send_file(
            filename, 
            mimetype="audio/wav", 
            as_attachment=True, 
            attachment_filename="diagnosis.wav"
        )
    else:
        response_object = {
            'status': 'fail',
            'message': gettext('This diagnosis is not yours')
        }
        return response_object, 400


def get_diagnosis(diagnosis_id):
    return Diagnosis.query.filter_by(public_id=diagnosis_id).first()


@token_checker
def get_single_diagnosis(token, diagnosis_id):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()

    diagnosis = Diagnosis.query.filter_by(public_id=diagnosis_id).first()

    if not diagnosis:
        response_object = {
            'status': 'fail',
            'message': gettext('Diagnosis not found')
        }
        return response_object, 404
    
    if user.id == diagnosis.user_id:
        return diagnosis
    else:
        response_object = {
            'status': 'fail',
            'message': gettext('You can not view not yours diagnoses')
        }
        return response_object


@token_checker
def get_report(token, diagnosis_id, language):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()

    diagnosis = Diagnosis.query.filter_by(
                public_id=diagnosis_id).first()

    if not diagnosis:
        response_object = {
            'status': 'fail',
            'message': gettext('Diagnosis not found')
        }
        return response_object, 404

    return send_pdf(
        user, 
        diagnosis, 
        generate_name(diagnosis_id, diagnosis.checked_on),
        language.split('_')[0]
    )


@token_checker
def get_my_diagnoses(token):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()
    return list(user.diagnoses)


@token_checker
def get_advice(token, locale, diagnosis_id):
    diagnosis = Diagnosis.query.filter_by(public_id=diagnosis_id).first()

    if not diagnosis:
        response_object = {
            'status': 'fail',
            'message': gettext('Diagnosis not found')
        }
        return response_object, 404

    result = scrape(locale.split('_')[0], diagnosis.result)
    
    response_object = {
        'status': 'success',
        'message': gettext('Pieces of advice are gathered'),
        'result': result
    }

    return response_object, 200


def generate_name(public_id, checked_on):
    return sha384(
        public_id.encode('utf-8') \
         + checked_on.strftime("%d.%m.%Y %H:%M:%S").encode('utf-8')
    ).hexdigest()


def save_diagnosis(diagnosis, user):
    user.diagnoses.append(diagnosis)
    db.session.add(diagnosis)
    db.session.commit()


def check_wav_file(file):
    if allowed_file(file.filename):
        try:
            sr, audio = read(file)
        except Exception as e:
            return {
                'valid': False,
                'response': {
                    'status': 'fail',
                    'message': gettext('File was named as .wav, \
                        but it is either not really .wav or it is broken')
                }
            }
        
        new_sample_rate = 16000
        audio = resample(audio.astype(float), sr, new_sample_rate)

        #UNCOMMENT BEFORE DEPLOYMENT
        #if evaluate(audio) > 0.5:

        return {
            'valid': True,
            'audio': ((audio + audio.min()) * (2 ** 15) / audio.ptp()).astype(int16)
        }
        
        '''
        else:
            return {
                'valid': False,
                'response': {
                    'status': 'fail',
                    'message': gettext('Audio is not a heartbeat or it is too noisy')
                }
            }
        '''
    else:
        return {
                'valid': False,
                'response': {
                    'status': 'fail',
                    'message': gettext('File is not .wav')
                }
            }

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'wav'
