from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from marshmallow import ValidationError # type: ignore
from sqlalchemy.exc import SQLAlchemyError # type: ignore
from .schema import AssignmentSchema, AssignmentGradeSchema

teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)

@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    try:
        teachers_assignments = Assignment.get_assignments_by_teacher(p.teacher_id)
        teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    except SQLAlchemyError as err:
        return APIResponse.respond_error("Database error occurred", status_code=500)

    return APIResponse.respond(data=teachers_assignments_dump)

@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment"""
    try:
        grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

        graded_assignment = Assignment.mark_grade(
            _id=grade_assignment_payload.id,
            grade=grade_assignment_payload.grade,
            auth_principal=p
        )
        db.session.commit()
    except ValidationError as err:
        return APIResponse.respond_error(err.messages, status_code=400)
    except SQLAlchemyError as err:
        db.session.rollback()
        return APIResponse.respond_error("Database error occurred", status_code=500)

    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)
