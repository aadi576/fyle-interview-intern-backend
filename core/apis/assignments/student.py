from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from marshmallow import ValidationError # type: ignore
from sqlalchemy.exc import SQLAlchemyError # type: ignore
from .schema import AssignmentSchema, AssignmentSubmitSchema

student_assignments_resources = Blueprint('student_assignments_resources', __name__)

# Route to list assignments for a student
@student_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    students_assignments = Assignment.get_assignments_by_student(p.student_id)
    students_assignments_dump = AssignmentSchema().dump(students_assignments, many=True)
    return APIResponse.respond(data=students_assignments_dump)

# Route to create or edit an assignment
@student_assignments_resources.route('/assignments', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def upsert_assignment(p, incoming_payload):
    """Create or Edit an assignment"""
    try:
        assignment = AssignmentSchema().load(incoming_payload)
        assignment.student_id = p.student_id

        upserted_assignment = Assignment.upsert(assignment)
        db.session.commit()
    except ValidationError as err:
        return APIResponse.respond_error(err.messages, status_code=400)
    except SQLAlchemyError as err:
        db.session.rollback()
        return APIResponse.respond_error("Database error occurred", status_code=500)

    upserted_assignment_dump = AssignmentSchema().dump(upserted_assignment)
    return APIResponse.respond(data=upserted_assignment_dump)

# Route to submit an assignment
@student_assignments_resources.route('/assignments/submit', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def submit_assignment(p, incoming_payload):
    """Submit an assignment"""
    try:
        submit_assignment_payload = AssignmentSubmitSchema().load(incoming_payload)

        submitted_assignment = Assignment.submit(
            _id=submit_assignment_payload.id,
            teacher_id=submit_assignment_payload.teacher_id,
            auth_principal=p
        )
        db.session.commit()
    except ValidationError as err:
        return APIResponse.respond_error(err.messages, status_code=400)
    except SQLAlchemyError as err:
        db.session.rollback()
        return APIResponse.respond_error("Database error occurred", status_code=500)

    submitted_assignment_dump = AssignmentSchema().dump(submitted_assignment)
    return APIResponse.respond(data=submitted_assignment_dump)
