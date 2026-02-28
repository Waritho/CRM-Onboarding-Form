"""seed form builder master data

Revision ID: 94f8c4c9883c
Revises: 21511a338827
Create Date: 2026-02-28

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "94f8c4c9883c"
down_revision: Union[str, Sequence[str], None] = "21511a338827"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# HELPER

def insert_fields(connection, section_id, fields):
    for index, (key, label, field_type) in enumerate(fields, start=1):
        connection.execute(
            sa.text("""
                INSERT INTO form_fields_master
                (section_id, field_key, label, field_type, default_sort_order, is_active)
                VALUES (:section_id, :field_key, :label, :field_type, :order, true)
            """),
            {
                "section_id": section_id,
                "field_key": key,
                "label": label,
                "field_type": field_type,
                "order": index
            }
        )


# UPGRADE

def upgrade():

    connection = op.get_bind()

    # INSERT SECTIONS

    sections = [
        ("Personal Details", "personal_details", 1, False),
        ("Parent Details", "parent_details", 2, False),
        ("Current Address", "current_address", 3, False),
        ("10th or Equivalent Details", "tenth_details", 4, False),
        ("12th Details", "twelfth_details", 5, False),
        ("Diploma Details", "diploma_details", 6, False),
        ("Under Graduation Details", "ug_details", 7, False),
        ("Post Graduation Details", "pg_details", 8, False),
        ("Entrance Exam Details", "entrance_exam_details", 9, True),
        ("Work Experience", "work_experience", 10, True),
        ("Extra Curricular Activity", "extra_curricular_activity", 11, True),
        ("Upload Documents", "upload_documents", 12, False),
    ]

    for name, code, order, repeatable in sections:
        connection.execute(
            sa.text("""
                INSERT INTO form_sections
                (name, code, default_sort_order, is_repeatable, is_active)
                VALUES (:name, :code, :order, :repeatable, true)
            """),
            {
                "name": name,
                "code": code,
                "order": order,
                "repeatable": repeatable
            }
        )

    section_rows = connection.execute(
        sa.text("SELECT id, code FROM form_sections")
    ).fetchall()

    section_map = {row.code: row.id for row in section_rows}

    # PERSONAL DETAILS

    personal_fields = [
        ("first_name", "First Name", "text"),
        ("middle_name", "Middle Name", "text"),
        ("last_name", "Last Name", "text"),
        ("email", "Email", "email"),
        ("alternate_email", "Alternate Email", "email"),
        ("mobile_no", "Mobile No", "text"),
        ("alternate_mobile_no", "Alternate Mobile No", "text"),
        ("dob", "Date of Birth", "date"),
        ("admission_year", "Admission Year", "number"),
        ("gender", "Gender", "select"),
        ("nationality", "Nationality", "text"),
        ("caste", "Caste", "text"),
        ("blood_group", "Blood Group", "select"),
        ("language_spoken", "Language Spoken", "text"),
        ("health_issues", "Any Health Issues?", "textarea"),
        ("specially_abled", "Are you Specially Abled?", "boolean"),
        ("lived_outside_india", "Have you Lived Outside India?", "boolean"),
        ("state_domicile", "State Domicile", "text"),
    ]

    insert_fields(connection, section_map["personal_details"], personal_fields)

    # PARENT DETAILS

    parent_fields = [
        ("father_name", "Father Name", "text"),
        ("father_mobile", "Father Mobile", "text"),
        ("father_email", "Father Email", "email"),
        ("father_occupation", "Father Occupation", "text"),
        ("father_org_details", "Father Organisation Details", "text"),
        ("father_designation", "Father Designation", "text"),
        ("father_education", "Father Highest Education", "text"),

        ("mother_name", "Mother Name", "text"),
        ("mother_mobile", "Mother Mobile", "text"),
        ("mother_email", "Mother Email", "email"),
        ("mother_occupation", "Mother Occupation", "text"),
        ("mother_org_details", "Mother Organisation Details", "text"),
        ("mother_designation", "Mother Designation", "text"),
        ("mother_education", "Mother Highest Education", "text"),

        ("family_annual_income", "Family Annual Income", "number"),

        ("guardian_name", "Guardian Name", "text"),
        ("guardian_relationship", "Guardian Relationship", "text"),
        ("guardian_mobile", "Guardian Mobile", "text"),
        ("guardian_email", "Guardian Email", "email"),
        ("guardian_occupation", "Guardian Occupation", "text"),
        ("guardian_designation", "Guardian Designation", "text"),
        ("guardian_org_details", "Guardian Organisation Details", "text"),
    ]

    insert_fields(connection, section_map["parent_details"], parent_fields)

    # CURRENT ADDRESS

    current_address_fields = [
        ("address_line_1", "Address Line 1", "text"),
        ("address_line_2", "Address Line 2", "text"),
        ("city", "City", "text"),
        ("state", "State", "text"),
        ("country", "Country", "text"),
        ("pincode", "Pincode", "text"),
        ("same_address_for_communication", "Same Address for Communication", "boolean"),
    ]

    insert_fields(connection, section_map["current_address"], current_address_fields)

    # 10TH DETAILS

    tenth_fields = [
        ("tenth_school_name", "School Name", "text"),
        ("tenth_board_name", "Board Name", "text"),
        ("tenth_marking_scheme", "Marking Scheme", "text"),
        ("tenth_maximum_marks", "Maximum Marks", "number"),
        ("tenth_obtained_marks", "Obtained Marks", "number"),
        ("tenth_year_of_passing", "Year of Passing", "number"),
        ("tenth_registration_number", "Registration Number", "text"),
    ]

    insert_fields(connection, section_map["tenth_details"], tenth_fields)

    # 12TH DETAILS

    twelfth_fields = [
        ("twelfth_school_name", "School Name", "text"),
        ("twelfth_board_name", "Board Name", "text"),
        ("twelfth_stream", "Stream", "text"),
        ("twelfth_marking_scheme", "Marking Scheme", "text"),
        ("twelfth_maximum_marks", "Maximum Marks", "number"),
        ("twelfth_obtained_marks", "Obtained Marks", "number"),
        ("twelfth_year_of_passing", "Year of Passing", "number"),
        ("twelfth_registration_number", "Registration Number", "text"),
    ]

    insert_fields(connection, section_map["twelfth_details"], twelfth_fields)

    # DIPLOMA

    diploma_fields = [
        ("diploma_college_name", "College Name", "text"),
        ("diploma_stream", "Stream", "text"),
        ("diploma_marking_scheme", "Marking Scheme", "text"),
        ("diploma_maximum_marks", "Maximum Marks", "number"),
        ("diploma_obtained_marks", "Obtained Marks", "number"),
        ("diploma_year_of_passing", "Year of Passing", "number"),
        ("diploma_completed_12th", "Completed 12th?", "boolean"),
    ]

    insert_fields(connection, section_map["diploma_details"], diploma_fields)

    # UG DETAILS

    ug_fields = [
        ("ug_result_mode", "Result Mode (Year/Semester)", "select"),
        ("ug_university", "University", "text"),
        ("ug_college_name", "College Name", "text"),
        ("ug_degree", "Degree", "text"),
        ("ug_marking_scheme", "Marking Scheme", "text"),
        ("ug_year_of_passing", "Year of Passing", "number"),
        ("ug_total_marks", "Total Marks", "number"),
        ("ug_maximum_marks", "Maximum Marks", "number"),
        ("ug_aggregate_percentage", "Aggregate Percentage", "number"),
        ("ug_table_enabled", "Enable Semester Table", "boolean"),
    ]

    insert_fields(connection, section_map["ug_details"], ug_fields)

    # PG DETAILS

    pg_fields = [
        ("pg_result_mode", "Result Mode (Year/Semester)", "select"),
        ("pg_university", "University", "text"),
        ("pg_college_name", "College Name", "text"),
        ("pg_degree", "Degree", "text"),
        ("pg_marking_scheme", "Marking Scheme", "text"),
        ("pg_year_of_passing", "Year of Passing", "number"),
        ("pg_total_marks", "Total Marks", "number"),
        ("pg_maximum_marks", "Maximum Marks", "number"),
        ("pg_aggregate_percentage", "Aggregate Percentage", "number"),
        ("pg_table_enabled", "Enable Semester Table", "boolean"),
    ]

    insert_fields(connection, section_map["pg_details"], pg_fields)

    # ENTRANCE EXAM

    entrance_fields = [
        ("exam_name", "Exam Name", "text"),
        ("exam_roll_number", "Roll Number", "text"),
        ("exam_year_of_appearing", "Year of Appearing", "number"),
        ("exam_rank", "Rank", "number"),
        ("exam_total_marks", "Total Marks", "number"),
        ("exam_maximum_marks", "Maximum Marks", "number"),
        ("exam_aggregate_percentage", "Aggregate Percentage", "number"),
    ]

    insert_fields(connection, section_map["entrance_exam_details"], entrance_fields)

    # WORK EXPERIENCE

    work_fields = [
        ("work_organisation", "Organisation Name", "text"),
        ("work_position", "Position", "text"),
        ("work_from_date", "From Date", "date"),
        ("work_to_date", "To Date", "date"),
        ("work_current_organisation", "Is Current Organisation?", "boolean"),
    ]

    insert_fields(connection, section_map["work_experience"], work_fields)

    # EXTRA CURRICULAR

    extra_fields = [
        ("extra_activity_name", "Activity Name", "text"),
        ("extra_description", "Description", "textarea"),
        ("extra_participation_period", "Period of Participation", "text"),
        ("extra_participation_level", "Level of Participation", "text"),
    ]

    insert_fields(connection, section_map["extra_curricular_activity"], extra_fields)

    # UPLOAD DOCUMENTS

    document_fields = [
        ("doc_photo", "Recent Photo", "document"),
        ("doc_signature", "Signature", "document"),
        ("doc_aadhar_card", "Aadhar Card", "document"),
        ("doc_driving_license", "Driving License", "document"),
        ("doc_voter_id", "Voter ID", "document"),
        ("doc_ug_marksheets", "UG Marksheets", "document"),
        ("doc_pg_marksheets", "PG Marksheets", "document"),
        ("doc_entrance_admit_card", "Entrance Admit Card", "document"),
        ("doc_experience_letter", "Experience Letter", "document"),
        ("doc_offer_letter", "Offer Letter", "document"),
        ("doc_resume", "Resume", "document"),
        ("doc_extra_certificate", "Extra Curricular Certificate", "document"),
    ]

    insert_fields(connection, section_map["upload_documents"], document_fields)


# DOWNGRADE

def downgrade():
    op.execute("DELETE FROM form_fields_master")
    op.execute("DELETE FROM form_sections")