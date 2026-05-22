from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Student, SupportCase
import csv
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change_this_secret_key")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

DB_USER = os.getenv("MYSQLUSER", "root")
DB_PASSWORD = quote_plus(os.getenv("MYSQLPASSWORD", "1234"))
DB_HOST = os.getenv("MYSQLHOST", "localhost")
DB_PORT = os.getenv("MYSQLPORT", "3306")
DB_NAME = os.getenv("MYSQLDATABASE", "student_support_db")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

db.init_app(app)

def parse_grade(value):
    if value is None or str(value).strip() == "":
        return None

    value = str(value).strip()

    allowed_values = [
        "Uniestructural 1",
        "Uniestructural 3",
        "Uniestructural 5",

        "Multiestructural 1",
        "Multiestructural 3",
        "Multiestructural 5",

        "Relacional 1",
        "Relacional 3",
        "Relacional 5",

        "Abstracto Ampliado 1",
        "Abstracto Ampliado 3",
        "Abstracto Ampliado 5"
    ]

    if value not in allowed_values:
        return "invalid"

    return value

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/init-db")
def init_db():
    db.create_all()

    users_to_create = [
        {
            "name": "Test Teacher",
            "email": "teacher@test.com",
            "password": "1234",
            "role": "teacher"
        },
        {
            "name": "Second Teacher",
            "email": "teacher2@test.com",
            "password": "1234",
            "role": "teacher"
        },
        {
            "name": "Test Monitor",
            "email": "monitor@test.com",
            "password": "1234",
            "role": "monitor"
        },
        {
            "name": "Second Monitor",
            "email": "monitor2@test.com",
            "password": "1234",
            "role": "monitor"
        }
    ]

    for user_data in users_to_create:
        existing_user = User.query.filter_by(email=user_data["email"]).first()

        if not existing_user:
            new_user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=generate_password_hash(user_data["password"]),
                role=user_data["role"]
            )
            db.session.add(new_user)

    db.session.commit()

    return """
    Database initialized successfully.<br><br>

    <strong>Teachers:</strong><br>
    teacher@test.com / 1234<br>
    teacher2@test.com / 1234<br><br>

    <strong>Monitors:</strong><br>
    monitor@test.com / 1234<br>
    monitor2@test.com / 1234
    """


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = user.role
            return redirect(url_for("dashboard"))

        flash("Email o contraseña invalida", "error")

    return render_template("login.html")

def validate_password(password):
    if not password:
        return False, "La contraseña es obligatoria."

    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    return True, ""


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "")

        if not name or not email or not password or not confirm_password or not role:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("register"))

        if "@" not in email or "." not in email:
            flash("Debes ingresar un correo válido.", "error")
            return redirect(url_for("register"))

        if role not in ["teacher", "monitor"]:
            flash("Rol de usuario inválido.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for("register"))

        is_valid, message = validate_password(password)

        if not is_valid:
            flash(message, "error")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Ya existe un usuario registrado con este correo.", "error")
            return redirect(url_for("register"))

        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Usuario registrado exitosamente. Ahora puedes iniciar sesión.", "exito")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not new_password or not confirm_password:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("forgot_password"))

        if "@" not in email or "." not in email:
            flash("Debes ingresar un correo válido.", "error")
            return redirect(url_for("forgot_password"))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No existe un usuario registrado con este correo.", "error")
            return redirect(url_for("forgot_password"))

        if new_password != confirm_password:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for("forgot_password"))

        is_valid, message = validate_password(new_password)

        if not is_valid:
            flash(message, "error")
            return redirect(url_for("forgot_password"))

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash("Contraseña actualizada exitosamente. Ya puedes iniciar sesión.", "exito")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    role = session.get("role")
    user_id = session.get("user_id")

    if role == "teacher":
        total_students = Student.query.filter_by(
            teacher_id=user_id
        ).count()

        students_needing_support = Student.query.filter_by(
            teacher_id=user_id,
            needs_support=True
        ).count()

        no_scores_students = Student.query.filter(
            Student.teacher_id == user_id,
            Student.grade_1.is_(None),
            Student.grade_2.is_(None),
            Student.grade_3.is_(None)
        ).count()

        total_cases = SupportCase.query.filter_by(
            teacher_id=user_id
        ).count()

        pending_cases = SupportCase.query.filter_by(
            teacher_id=user_id,
            status="pending"
        ).count()

        assigned_cases = SupportCase.query.filter_by(
            teacher_id=user_id,
            status="assigned"
        ).count()

        scheduled_cases = SupportCase.query.filter_by(
            teacher_id=user_id,
            status="scheduled"
        ).count()

        completed_cases = SupportCase.query.filter_by(
            teacher_id=user_id,
            status="completed"
        ).count()

        return render_template(
            "dashboard.html",
            role=role,
            total_students=total_students,
            students_needing_support=students_needing_support,
            no_scores_students=no_scores_students,
            total_cases=total_cases,
            pending_cases=pending_cases,
            assigned_cases=assigned_cases,
            scheduled_cases=scheduled_cases,
            completed_cases=completed_cases
        )

    elif role == "monitor":
        assigned_cases = SupportCase.query.filter_by(
            monitor_id=user_id
        ).count()

        scheduled_cases = SupportCase.query.filter_by(
            monitor_id=user_id,
            status="scheduled"
        ).count()

        in_progress_cases = SupportCase.query.filter_by(
            monitor_id=user_id,
            status="in_progress"
        ).count()

        completed_cases = SupportCase.query.filter_by(
            monitor_id=user_id,
            status="completed"
        ).count()

        pending_followups = SupportCase.query.filter(
            SupportCase.monitor_id == user_id,
            SupportCase.status.in_(["assigned", "scheduled", "in_progress"])
        ).count()

        return render_template(
            "dashboard.html",
            role=role,
            assigned_cases=assigned_cases,
            scheduled_cases=scheduled_cases,
            in_progress_cases=in_progress_cases,
            completed_cases=completed_cases,
            pending_followups=pending_followups
        )

    else:
        total_students = Student.query.count()
        total_cases = SupportCase.query.count()
        total_teachers = User.query.filter_by(role="teacher").count()
        total_monitors = User.query.filter_by(role="monitor").count()

        return render_template(
            "dashboard.html",
            role=role,
            total_students=total_students,
            total_cases=total_cases,
            total_teachers=total_teachers,
            total_monitors=total_monitors
        )


@app.route("/students")
def students():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") not in ["teacher", "monitor"]:
        flash("No tienes permiso para acceder al módulo de estudiantes.", "error")
        return redirect(url_for("dashboard"))

    all_students = (
        Student.query
        .order_by(Student.created_at.desc())
        .all()
    )

    return render_template("students.html", students=all_students)


@app.route("/students/create", methods=["GET", "POST"])
def create_student():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") not in ["teacher", "monitor"]:
        flash("No tienes permiso para registrar estudiantes.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        student_code = request.form.get("student_code")
        full_name = request.form.get("full_name")
        semester = request.form.get("semester")
        group_name = request.form.get("group_name")
        class_code = request.form.get("class_code")
        class_name = request.form.get("class_name")

        if not student_code or not full_name or not group_name:
            flash("Debes completar los datos principales del estudiante.", "error")
            return redirect(url_for("create_student"))

        if not class_code:
            flash("Class code is required.", "error")
            return redirect(url_for("create_student"))
        
        if not class_name:
            flash("El nombre de la clase es obligatorio.", "error")
            return redirect(url_for("create_student"))

        if not semester:
            semester = "Unassigned"

        grade_1 = parse_grade(request.form.get("grade_1"))
        grade_2 = parse_grade(request.form.get("grade_2"))
        grade_3 = parse_grade(request.form.get("grade_3"))

        if "invalid" in [grade_1, grade_2, grade_3]:
            flash("Scores must be valid numbers between 0 and 5.", "error")
            return redirect(url_for("create_student"))

        existing_student = Student.query.filter_by(
            teacher_id=session["user_id"],
            student_code=student_code,
            class_code=class_code
        ).first()

        if existing_student:
            flash("Este estudiante ya existe para esta clase.", "error")
            return redirect(url_for("create_student"))

        student = Student(
            teacher_id=session["user_id"],
            student_code=student_code,
            full_name=full_name,
            semester=semester,
            group_name=group_name,
            class_code=class_code,
            class_name=class_name,
            grade_1=grade_1,
            grade_2=grade_2,
            grade_3=grade_3,
            average=0,
            needs_support=False,
        )

        student.calculate_average()

        db.session.add(student)
        db.session.commit()

        flash("Estudiante registrado exitosamente.", "exito")
        return redirect(url_for("students"))

    return render_template("student_form.html", student=None, edit_mode=False)


@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Solo profesores pueden editar estudiantes.", "error")
        return redirect(url_for("students"))

    student = Student.query.get_or_404(student_id)

    if request.method == "POST":
        student_code = request.form.get("student_code")
        full_name = request.form.get("full_name")
        semester = request.form.get("semester")
        group_name = request.form.get("group_name")
        class_code = request.form.get("class_code")
        class_name = request.form.get("class_name")

        if not student_code or not full_name or not group_name:
            flash("Debes completar los datos principales del estudiante.", "error")
            return redirect(url_for("edit_student", student_id=student.id))

        if not class_code:
            flash("Class code is required.", "error")
            return redirect(url_for("edit_student", student_id=student.id))
        
        if not class_name:
            flash("El nombre de la clase es obligatorio.", "error")
            return redirect(url_for("edit_student", student_id=student.id))
        
        if not semester:
            semester = "Unassigned"

        duplicate_student = Student.query.filter(
            Student.teacher_id == session["user_id"],
            Student.student_code == student_code,
            Student.class_code == class_code,
            Student.id != student.id
        ).first()

        if duplicate_student:
            flash("Ya existe otro estudiante con ese codigo en esta clase.", "error")
            return redirect(url_for("edit_student", student_id=student.id))

        grade_1 = parse_grade(request.form.get("grade_1"))
        grade_2 = parse_grade(request.form.get("grade_2"))
        grade_3 = parse_grade(request.form.get("grade_3"))

        if "invalid" in [grade_1, grade_2, grade_3]:
            flash("Scores must be valid numbers between 0 and 5.", "error")
            return redirect(url_for("edit_student", student_id=student.id))

        student.student_code = student_code
        student.full_name = full_name
        student.semester = semester
        student.group_name = group_name
        student.class_code = class_code
        student.grade_1 = grade_1
        student.grade_2 = grade_2
        student.grade_3 = grade_3
        student.class_name = class_name

        student.calculate_average()

        db.session.commit()

        flash("Estudiante actualizado exitosamente.", "exito")
        return redirect(url_for("students"))

    return render_template("student_form.html", student=student, edit_mode=True)


@app.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") not in ["teacher", "monitor"]:
        flash("No tienes permiso para eliminar estudiantes.", "error")
        return redirect(url_for("dashboard"))

    student = Student.query.get_or_404(student_id)

    related_cases = SupportCase.query.filter_by(student_id=student.id).all()

    for case in related_cases:
        db.session.delete(case)

    db.session.delete(student)
    db.session.commit()

    flash("Estudiante y casos relacionados eliminados exitosamente.", "exito")
    return redirect(url_for("students"))


@app.route("/students/import", methods=["GET", "POST"])
def import_students():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") not in ["teacher", "monitor"]:
        flash("No tienes permiso para importar estudiantes.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        file = request.files.get("csv_file")

        if not file or file.filename == "":
            flash("Please select a CSV file.", "error")
            return redirect(url_for("import_students"))

        if not file.filename.lower().endswith(".csv"):
            flash("Only CSV files are allowed.", "error")
            return redirect(url_for("import_students"))

        try:
            content = file.stream.read().decode("utf-8-sig")
            lines = [line.strip() for line in content.splitlines() if line.strip()]

            if len(lines) < 2:
                flash("The CSV file must contain headers and at least one student row.", "error")
                return redirect(url_for("import_students"))

            def parse_line(line):
                comma_values = next(csv.reader([line], delimiter=","))
                semicolon_values = next(csv.reader([line], delimiter=";"))

                if len(semicolon_values) > len(comma_values):
                    values = semicolon_values
                else:
                    values = comma_values

                return [value.strip() for value in values]

            headers = parse_line(lines[0])
            headers = [header.strip().replace(",", "") for header in headers]

            required_columns = [
                "student_code",
                "full_name",
                "semester",
                "group_name",
                "class_code",
                "class_name",
                "grade_1",
                "grade_2",
                "grade_3"
            ]

            missing_columns = [
                column for column in required_columns
                if column not in headers
            ]

            if missing_columns:
                flash(f"Missing columns: {', '.join(missing_columns)}", "error")
                return redirect(url_for("import_students"))

            imported_count = 0
            skipped_count = 0
            error_rows = []

            for index, line in enumerate(lines[1:], start=2):
                values = parse_line(line)

                if len(values) != len(headers):
                    error_rows.append(
                        f"Row {index}: expected {len(headers)} columns but found {len(values)}."
                    )
                    skipped_count += 1
                    continue

                row = dict(zip(headers, values))

                student_code = row.get("student_code", "").strip()
                full_name = row.get("full_name", "").strip()
                semester = row.get("semester", "").strip()
                group_name = row.get("group_name", "").strip()
                class_code = row.get("class_code", "").strip()
                class_name = row.get("class_name", "").strip()

                grade_1 = parse_grade(row.get("grade_1"))
                grade_2 = parse_grade(row.get("grade_2"))
                grade_3 = parse_grade(row.get("grade_3"))

                if not semester:
                    semester = "Unassigned"

                if not student_code or not full_name or not group_name or not class_code or not class_name:
                    error_rows.append(f"Row {index}: missing required data.")
                    skipped_count += 1
                    continue

                if "invalid" in [grade_1, grade_2, grade_3]:
                    error_rows.append(
                        f"Row {index}: invalid grade. Grades must be empty or between 0 and 5."
                    )
                    skipped_count += 1
                    continue

                existing_student = Student.query.filter_by(
                    teacher_id=session["user_id"],
                    student_code=student_code,
                    class_code=class_code
                ).first()

                if existing_student:
                    error_rows.append(f"Row {index}: student already exists in this class: {student_code}.")
                    skipped_count += 1
                    continue

                student = Student(
                    teacher_id=session["user_id"],
                    student_code=student_code,
                    full_name=full_name,
                    semester=semester,
                    group_name=group_name,
                    class_code=class_code,
                    class_name=class_name,
                    grade_1=grade_1,
                    grade_2=grade_2,
                    grade_3=grade_3,
                    average=0,
                    needs_support=False
                )

                student.calculate_average()

                db.session.add(student)
                imported_count += 1

            db.session.commit()

            message_type = "success" if imported_count > 0 else "error"
            message = f"Import completed. Imported: {imported_count}. Skipped: {skipped_count}."

            if error_rows:
                message += " Details: " + " | ".join(error_rows[:8])

            flash(message, message_type)
            return redirect(url_for("students"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error importing CSV file: {str(e)}", "error")
            return redirect(url_for("import_students"))

    return render_template("import_students.html")


@app.route("/students/template")
def download_students_template():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Only teachers can download the template.", "error")
        return redirect(url_for("dashboard"))

    csv_content = (
        "student_code,full_name,semester,group_name,class_code,class_name,grade_1,grade_2,grade_3\n"
        "ST001,Juan Perez,3rd Semester,A,MATH101,Calculo I,2.5,3.0,\n"
        "ST002,Ana Torres,4th Semester,B,PROG202,Programacion II,4.0,4.2,3.8\n"
        "ST003,Carlos Ruiz,Unassigned,A,ENG101,Ingles I,2.0,,\n"
    )
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=students_template.csv"
        }
    )


@app.route("/cases")
def cases():
    if "user_id" not in session:
        return redirect(url_for("login"))

    view = request.args.get("view", "active")

    active_statuses = ["pending", "assigned", "scheduled", "in_progress"]
    closed_statuses = ["completed", "cancelled"]

    if view == "closed":
        selected_statuses = closed_statuses
    else:
        selected_statuses = active_statuses
        view = "active"

    if session.get("role") == "teacher":
        all_cases = (
            SupportCase.query
            .filter(
                SupportCase.teacher_id == session["user_id"],
                SupportCase.status.in_(selected_statuses)
            )
            .order_by(SupportCase.created_at.desc())
            .all()
        )

    elif session.get("role") == "monitor":
        all_cases = (
            SupportCase.query
            .filter(
                SupportCase.monitor_id == session["user_id"],
                SupportCase.status.in_(selected_statuses)
            )
            .order_by(SupportCase.created_at.desc())
            .all()
        )

    else:
        all_cases = (
            SupportCase.query
            .filter(SupportCase.status.in_(selected_statuses))
            .order_by(SupportCase.created_at.desc())
            .all()
        )

    return render_template("cases.html", cases=all_cases, view=view)


@app.route("/cases/create/<int:student_id>", methods=["GET", "POST"])
def create_case(student_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") not in ["teacher", "monitor"]:
        flash("No tienes permiso para crear casos.", "error")
        return redirect(url_for("dashboard"))

    student = Student.query.get_or_404(student_id)

    monitors = User.query.filter_by(role="monitor").all()

    if request.method == "POST":
        subject = request.form.get("subject")
        reason = request.form.get("reason")
        monitor_id = request.form.get("monitor_id")
        teacher_notes = request.form.get("teacher_notes")

        urgency_level = request.form.get("urgency_level")
        support_type = request.form.get("support_type")

        if not subject or not reason:
            flash("Subject and reason are required.", "error")
            return redirect(url_for("create_case", student_id=student.id))

        if urgency_level not in ["Baja", "Media", "Alta", "Crítica"]:
            flash("Nivel de urgencia inválido.", "error")
            return redirect(url_for("create_case", student_id=student.id))

        if support_type not in ["Monitoría", "Tutoría"]:
            flash("Tipo de apoyo inválido.", "error")
            return redirect(url_for("create_case", student_id=student.id))

        if monitor_id == "":
            monitor_id = None

        # Si lo crea un monitor, se puede autoasignar si no escoge monitor
        if session.get("role") == "monitor" and monitor_id is None:
            monitor_id = session["user_id"]

        teacher_id = student.teacher_id if student.teacher_id else session["user_id"]

        new_case = SupportCase(
            student_id=student.id,
            teacher_id=teacher_id,
            monitor_id=monitor_id,
            subject=subject,
            grade=student.average,
            reason=reason,
            urgency_level=urgency_level,
            support_type=support_type,
            status="assigned" if monitor_id else "pending",
            teacher_notes=teacher_notes
        )

        db.session.add(new_case)
        db.session.commit()

        flash("Caso creado exitosamente.", "exito")
        return redirect(url_for("cases"))

    return render_template("case_form.html", student=student, monitors=monitors)


@app.route("/cases/update/<int:case_id>", methods=["GET", "POST"])
def update_case(case_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    support_case = SupportCase.query.get_or_404(case_id)

    if session.get("role") == "monitor":
        if support_case.monitor_id != session["user_id"]:
            flash("You can only update cases assigned to you.", "error")
            return redirect(url_for("cases"))

    elif session.get("role") == "teacher":
        if support_case.teacher_id != session["user_id"]:
            flash("You can only review cases created by you.", "error")
            return redirect(url_for("cases"))

        if request.method == "POST":
            flash("Profesores pueden revisar el caso, pero solo monitores pueden actualizar la informacion.", "error")
            return redirect(url_for("cases"))

    else:
        flash("No tienes permiso para acceder a este caso.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        support_date = request.form.get("support_date")
        support_time = request.form.get("support_time")
        status = request.form.get("status")
        monitor_notes = request.form.get("monitor_notes")
        appointment_reason = request.form.get("appointment_reason")
        progress_update = request.form.get("progress_update")

        if not status:
            flash("Status is required.", "error")
            return redirect(url_for("update_case", case_id=support_case.id))

        if status == "scheduled" and (not support_date or not support_time):
            flash("Para agendar una cita debes seleccionar fecha y hora.", "error")
            return redirect(url_for("update_case", case_id=support_case.id))

        if status == "completed" and not progress_update:
            flash("Para completar el caso debes escribir una actualización de progreso.", "error")
            return redirect(url_for("update_case", case_id=support_case.id))

        support_case.status = status
        support_case.monitor_notes = monitor_notes
        support_case.appointment_reason = appointment_reason
        support_case.progress_update = progress_update

        if support_date:
            support_case.support_date = support_date

        if support_time:
            support_case.support_time = support_time

        db.session.commit()

        flash("Caso actualizado exitosamente.", "exito")
        return redirect(url_for("cases"))

    return render_template("update_case.html", case=support_case)

@app.route("/classes")
def classes():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") not in ["teacher", "monitor"]:
        flash("Solo profesores pueden acceder al módulo de clases.", "error")
        return redirect(url_for("dashboard"))

    students = Student.query.order_by(Student.class_code, Student.full_name).all()

    classes_dict = {}

    for student in students:
        code = student.class_code or "SIN_CODIGO"
        name = student.class_name or "Sin nombre"

        if code not in classes_dict:
            classes_dict[code] = {
                "class_code": code,
                "class_name": name,
                "students": []
            }

        classes_dict[code]["students"].append(student)

    classes_list = list(classes_dict.values())

    return render_template("classes.html", classes=classes_list)

@app.route("/classes/<class_code>")
def class_detail(class_code):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") not in ["teacher", "monitor"]:
        flash("Solo profesores pueden acceder al detalle de clases.", "error")
        return redirect(url_for("dashboard"))

    students = (
        Student.query
        .filter_by(class_code=class_code)
        .order_by(Student.full_name.asc())
        .all()
    )

    if not students:
        flash("No se encontraron estudiantes para esta clase.", "error")
        return redirect(url_for("classes"))

    class_name = students[0].class_name or "Sin nombre"

    return render_template(
        "class_detail.html",
        students=students,
        class_code=class_code,
        class_name=class_name
    )

@app.route("/cases/delete/<int:case_id>", methods=["POST"])
def delete_case(case_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Solo profesores pueden eliminar casos.", "error")
        return redirect(url_for("cases"))

    support_case = SupportCase.query.get_or_404(case_id)

    if support_case.teacher_id != session["user_id"]:
        flash("Solo puedes eliminar casos creados por ti.", "error")
        return redirect(url_for("cases"))

    db.session.delete(support_case)
    db.session.commit()

    flash("Caso eliminado exitosamente.", "exito")
    return redirect(url_for("cases"))


@app.route("/debug-users")
def debug_users():
    users = User.query.all()

    output = "<h2>Users</h2>"

    for user in users:
        output += f"{user.id} - {user.name} - {user.email} - {user.role}<br>"

    return output
@app.route("/users")
def users():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") not in ["teacher", "monitor"]:
        flash("No tienes permiso para ver usuarios.", "error")
        return redirect(url_for("dashboard"))

    all_users = (
        User.query
        .filter(User.role.in_(["teacher", "monitor"]))
        .order_by(User.role.asc(), User.name.asc())
        .all()
    )

    return render_template("users.html", users=all_users)

@app.route("/stats")
def stats():
    if "user_id" not in session:
        return redirect(url_for("login"))

    role = session.get("role")
    user_id = session.get("user_id")

    if role == "teacher":
        total_students = Student.query.count()

        students_needing_support = Student.query.filter_by(
            needs_support=True
        ).count()

        no_scores_students = Student.query.filter(
            Student.grade_1.is_(None),
            Student.grade_2.is_(None),
            Student.grade_3.is_(None)
        ).count()

        total_cases = SupportCase.query.filter_by(
            teacher_id=user_id
        ).count()

        pending_cases = SupportCase.query.filter_by(
            teacher_id=user_id,
            status="pending"
        ).count()

        assigned_cases = SupportCase.query.filter_by(
            teacher_id=user_id,
            status="assigned"
        ).count()

        scheduled_cases = SupportCase.query.filter_by(
            teacher_id=user_id,
            status="scheduled"
        ).count()

        in_progress_cases = SupportCase.query.filter_by(
            teacher_id=user_id,
            status="in_progress"
        ).count()

        completed_cases = SupportCase.query.filter_by(
            teacher_id=user_id,
            status="completed"
        ).count()

        cancelled_cases = SupportCase.query.filter_by(
            teacher_id=user_id,
            status="cancelled"
        ).count()

        return render_template(
            "stats.html",
            role=role,
            total_students=total_students,
            students_needing_support=students_needing_support,
            no_scores_students=no_scores_students,
            total_cases=total_cases,
            pending_cases=pending_cases,
            assigned_cases=assigned_cases,
            scheduled_cases=scheduled_cases,
            in_progress_cases=in_progress_cases,
            completed_cases=completed_cases,
            cancelled_cases=cancelled_cases
        )

    elif role == "monitor":
        total_students = Student.query.count()

        assigned_cases = SupportCase.query.filter_by(
            monitor_id=user_id
        ).count()

        scheduled_cases = SupportCase.query.filter_by(
            monitor_id=user_id,
            status="scheduled"
        ).count()

        in_progress_cases = SupportCase.query.filter_by(
            monitor_id=user_id,
            status="in_progress"
        ).count()

        completed_cases = SupportCase.query.filter_by(
            monitor_id=user_id,
            status="completed"
        ).count()

        cancelled_cases = SupportCase.query.filter_by(
            monitor_id=user_id,
            status="cancelled"
        ).count()

        pending_followups = SupportCase.query.filter(
            SupportCase.monitor_id == user_id,
            SupportCase.status.in_(["assigned", "scheduled", "in_progress"])
        ).count()

        return render_template(
            "stats.html",
            role=role,
            total_students=total_students,
            assigned_cases=assigned_cases,
            scheduled_cases=scheduled_cases,
            in_progress_cases=in_progress_cases,
            completed_cases=completed_cases,
            cancelled_cases=cancelled_cases,
            pending_followups=pending_followups
        )

    else:
        total_students = Student.query.count()
        total_cases = SupportCase.query.count()
        total_teachers = User.query.filter_by(role="teacher").count()
        total_monitors = User.query.filter_by(role="monitor").count()

        return render_template(
            "stats.html",
            role=role,
            total_students=total_students,
            total_cases=total_cases,
            total_teachers=total_teachers,
            total_monitors=total_monitors
        )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)