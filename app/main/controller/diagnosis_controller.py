from flask import request
from flask_restplus import Resource

from ..util.dto import DiagnosisDto, DiagnosisInfoDto
from ..util.decorator import token_required
from ..service.diagnosis_service import create_diagnosis, return_diagnosis_audio, \
    get_my_diagnoses, get_single_diagnosis, get_report, get_advice


api = DiagnosisDto.api
_diagnosis = DiagnosisDto.diagnosis

dapi = DiagnosisInfoDto.api
_diagnosis_info = DiagnosisInfoDto.diagnosis_info_details


@api.route('/')
class DiagnosisList(Resource):
    @api.response(201, 'Diagnosis successfully saved.')
    @api.doc('save a new diagnosis')
    @token_required
    def post(self):
        """ Saves new diagnosis """
        return create_diagnosis(
            request.headers.get('Authorization'),
            request.files['datas'], 
            request.files['sound']
        )
    
    @api.doc('get user\'s diagnoses')
    @token_required
    @api.marshal_with(_diagnosis_info)
    def get(self):
        return get_my_diagnoses(
            request.headers.get('Authorization')
        )


@api.route('/<diagnosis_id>/media')
class DiagnosisMedia(Resource):
    @api.doc('get a diagnosis attached audio')
    @token_required
    def get(self, diagnosis_id):
        return return_diagnosis_audio(
            request.headers.get('Authorization'), 
            diagnosis_id
        )


@api.route('/<public_id>')
@api.param('public_id', 'The Diagnosis identifier')
@api.response(404, 'Diagnosis not found.')
class Diagnosis(Resource):
    @api.doc('get a diagnosis')
    @token_required
    @api.marshal_with(_diagnosis_info)
    def get(self, public_id):
        """get a diagnosis given its identifier"""
        diagnosis = get_single_diagnosis(
            request.headers.get('Authorization'),
            public_id
        )
        
        if isinstance(diagnosis, dict):
            return diagnosis, 400

        if not diagnosis:
            api.abort(404)
        else:
            return diagnosis


@api.route('/<diagnosis_id>/report')
class DiagnosisReport(Resource):
    @api.doc('get a diagnosis pdf report')
    @token_required
    def get(self, diagnosis_id):
        return get_report(
            request.headers.get('Authorization'), 
            diagnosis_id, 
            request.headers.get('Accept-Language')
        )


@api.route('/<diagnosis_id>/advice')
class DiagnosisAdvice(Resource):
    @api.doc('get pieces of advice for diagnosis')
    @token_required
    def get(self, diagnosis_id):
        return get_advice(
            request.headers.get('Authorization'),  
            request.headers.get('Accept-Language'),
            diagnosis_id
        )
