from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    # Allowed roles:
    # teacher = creates students and support cases
    # monitor = follows assigned cases
    # admin = optional future role
    role = db.Column(db.String(20), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.name} - {self.role}>"


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    student_code = db.Column(db.String(50), nullable=False)

    full_name = db.Column(db.String(150), nullable=False)

    semester = db.Column(db.String(50), nullable=True, default="Sin asignar")

    group_name = db.Column(db.String(50), nullable=False)

    class_code = db.Column(db.String(50), nullable=False)

    class_name = db.Column(db.String(150), nullable=False, default="Sin nombre")

    grade_1 = db.Column(db.String(50), nullable=True)
    grade_2 = db.Column(db.String(50), nullable=True)
    grade_3 = db.Column(db.String(50), nullable=True)

    average = db.Column(db.Float, nullable=True, default=0)

    final_level = db.Column(db.String(50), nullable=True)

    needs_support = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teacher = db.relationship(
        "User",
        foreign_keys=[teacher_id],
        backref=db.backref("students", lazy=True)
    )

    def qualitative_to_score(self, value):
        scale = {
            "Uniestructural 1": 1.5,
            "Uniestructural 3": 1.5,
            "Uniestructural 5": 1.5,

            "Multiestructural 1": 1.8,
            "Multiestructural 3": 2.3,
            "Multiestructural 5": 2.8,

            "Relacional 1": 3.0,
            "Relacional 3": 3.5,
            "Relacional 5": 4.0,

            "Abstracto Ampliado 1": 4.3,
            "Abstracto Ampliado 3": 4.8,
            "Abstracto Ampliado 5": 5.0
        }

        return scale.get(value)

    def score_to_qualitative(self, score):
        if score is None:
            return "Sin notas"

        if score < 1.8:
            return "Uniestructural"
        elif score < 3.0:
            return "Multiestructural"
        elif score < 4.3:
            return "Relacional"
        else:
            return "Abstracto Ampliado"

    def calculate_average(self):
        scores = []

        for grade in [self.grade_1, self.grade_2, self.grade_3]:
            score = self.qualitative_to_score(grade)

            if score is not None:
                scores.append(score)

        if len(scores) == 0:
            self.average = 0
            self.final_level = "Sin notas"
            self.needs_support = False
        else:
            self.average = round(sum(scores) / len(scores), 2)
            self.final_level = self.score_to_qualitative(self.average)
            self.needs_support = self.average < 3.0

    def __repr__(self):
        return f"<Student {self.full_name} - {self.final_level}>"

def score_to_qualitative(self, score):
    if score is None:
        return "Sin notas"

    if score < 1.8:
        return "Uniestructural"
    elif score < 3.0:
        return "Multiestructural"
    elif score < 4.3:
        return "Relacional"
    else:
        return "Abstracto Ampliado"


def calculate_average(self):
    scores = []

    for grade in [self.grade_1, self.grade_2, self.grade_3]:
        score = self.qualitative_to_score(grade)

        if score is not None:
            scores.append(score)

    if len(scores) == 0:
        self.average = 0
        self.final_level = "Sin notas"
        self.needs_support = False
    else:
        self.average = round(sum(scores) / len(scores), 2)
        self.final_level = self.score_to_qualitative(self.average)
        self.needs_support = self.average < 3.0

class SupportCase(db.Model):
    __tablename__ = "support_cases"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    monitor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    subject = db.Column(db.String(100), nullable=False)

    grade = db.Column(db.Float, nullable=True)

    reason = db.Column(db.Text, nullable=False)

    urgency_level = db.Column(db.String(30), nullable=False, default="Media")

    support_type = db.Column(db.String(30), nullable=False, default="Monitoría")

    support_date = db.Column(db.Date, nullable=True)

    support_time = db.Column(db.Time, nullable=True)

    appointment_reason = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(30), nullable=False, default="pending")

    teacher_notes = db.Column(db.Text, nullable=True)

    monitor_notes = db.Column(db.Text, nullable=True)

    progress_update = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    student = db.relationship(
        "Student",
        backref=db.backref("cases", lazy=True)
    )

    teacher = db.relationship(
        "User",
        foreign_keys=[teacher_id],
        backref=db.backref("created_cases", lazy=True)
    )

    monitor = db.relationship(
        "User",
        foreign_keys=[monitor_id],
        backref=db.backref("assigned_cases", lazy=True)
    )

    def __repr__(self):
        return f"<SupportCase Student {self.student_id} - Status {self.status}>"