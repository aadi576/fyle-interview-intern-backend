# script.py

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy # type: ignore
from marshmallow import Schema, fields # type: ignore
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum
from core.libs.helpers import GeneralObject
from core.libs.exceptions import FyleError
from marshmallow.exceptions import ValidationError # type: ignore
from sqlalchemy.exc import IntegrityError # type: ignore
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./store.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class AssignmentSchema(Schema):
    # Define your schema here
    pass

class AssignmentSubmitSchema(Schema):
    # Define your schema here
    pass

@app.route('/')
def ready():
    return jsonify({
        'status': 'ready',
        'time': GeneralObject.get_utc_now()
    })

@app.route('/assignments', methods=['GET'])
def list_assignments():
    assignments = Assignment.query.all()
    assignments_dump = AssignmentSchema().dump(assignments, many=True)
    return jsonify(data=assignments_dump)

@app.route('/assignments', methods=['POST'])
def upsert_assignment():
    incoming_payload = request.json
    assignment = AssignmentSchema().load(incoming_payload)
    Assignment.upsert(assignment)
    db.session.commit()
    upserted_assignment_dump = AssignmentSchema().dump(assignment)
    return jsonify(data=upserted_assignment_dump)

@app.route('/assignments/submit', methods=['POST'])
def submit_assignment():
    incoming_payload = request.json
    submit_assignment_payload = AssignmentSubmitSchema().load(incoming_payload)
    submitted_assignment = Assignment.submit(
        _id=submit_assignment_payload.id,
        teacher_id=submit_assignment_payload.teacher_id
    )
    db.session.commit()
    submitted_assignment_dump = AssignmentSchema().dump(submitted_assignment)
    return jsonify(data=submitted_assignment_dump)

@app.errorhandler(Exception)
def handle_error(err):
    if isinstance(err, FyleError):
        return jsonify(
            error=err.__class__.__name__, message=err.message
        ), err.status_code
    elif isinstance(err, ValidationError):
        return jsonify(
            error=err.__class__.__name__, message=err.messages
        ), 400
    elif isinstance(err, IntegrityError):
        return jsonify(
            error=err.__class__.__name__, message=str(err.orig)
        ), 400
    elif isinstance(err, HTTPException):
        return jsonify(
            error=err.__class__.__name__, message=str(err)
        ), err.code

    return jsonify(
        error='InternalServerError', message='An unexpected error occurred'
    ), 500

if __name__ == '__main__':
    app.run(debug=True)
