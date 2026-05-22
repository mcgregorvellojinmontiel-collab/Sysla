document.addEventListener("DOMContentLoaded", function () {
    /*
    ==========================================
    LOGIN
    ==========================================
    */
    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", function (event) {
            const email = document.getElementById("email")?.value.trim();
            const password = document.getElementById("password")?.value.trim();

            if (email === "" || password === "") {
                event.preventDefault();
                alert("Por favor completa todos los campos.");
            }
        });
    }

    /*
    ==========================================
    REGISTRO Y RECUPERACIÓN
    ==========================================
    */
    const registerForm = document.getElementById("registerForm");
    const forgotPasswordForm = document.getElementById("forgotPasswordForm");

    if (registerForm) {
        registerForm.addEventListener("submit", function (event) {
            const password = document.getElementById("registerPassword")?.value.trim();
            const confirmPassword = document.getElementById("confirmPassword")?.value.trim();

            if (password.length < 6) {
                event.preventDefault();
                alert("La contraseña debe tener al menos 6 caracteres.");
                return;
            }

            if (password !== confirmPassword) {
                event.preventDefault();
                alert("Las contraseñas no coinciden.");
                return;
            }
        });
    }

    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener("submit", function (event) {
            const password = document.getElementById("newPassword")?.value.trim();
            const confirmPassword = document.getElementById("confirmNewPassword")?.value.trim();

            if (password.length < 6) {
                event.preventDefault();
                alert("La nueva contraseña debe tener al menos 6 caracteres.");
                return;
            }

            if (password !== confirmPassword) {
                event.preventDefault();
                alert("Las contraseñas no coinciden.");
                return;
            }
        });
    }

    /*
    ==========================================
    FORMULARIO DE ESTUDIANTE
    ==========================================
    */
    const studentForm = document.getElementById("studentForm");

    const gradeValues = {
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
    };

    function scoreToLevel(score) {
        if (score < 1.8) {
            return "Uniestructural";
        } else if (score < 3.0) {
            return "Multiestructural";
        } else if (score < 4.3) {
            return "Relacional";
        } else {
            return "Abstracto Ampliado";
        }
    }

    function updateAverage() {
        const averagePreview = document.getElementById("averagePreview");

        if (!averagePreview) {
            return;
        }

        const inputs = ["grade_1", "grade_2", "grade_3"];
        let scores = [];

        inputs.forEach(function (id) {
            const input = document.getElementById(id);

            if (input && input.value.trim() !== "") {
                const selectedValue = input.value.trim();
                const score = gradeValues[selectedValue];

                if (score !== undefined) {
                    scores.push(score);
                }
            }
        });

        if (scores.length === 0) {
            averagePreview.textContent = "Nivel final: Sin notas";
            return;
        }

        const total = scores.reduce(function (sum, score) {
            return sum + score;
        }, 0);

        const average = (total / scores.length).toFixed(2);
        const finalLevel = scoreToLevel(parseFloat(average));

        averagePreview.textContent = "Promedio: " + average + " - Nivel final: " + finalLevel;

        if (parseFloat(average) < 3.0) {
            averagePreview.textContent += " - Requiere apoyo";
        } else {
            averagePreview.textContent += " - Buen estado";
        }
    }

    ["grade_1", "grade_2", "grade_3"].forEach(function (id) {
        const input = document.getElementById(id);

        if (input) {
            input.addEventListener("change", updateAverage);
        }
    });

    if (studentForm) {
        studentForm.addEventListener("submit", function (event) {
            const allowedValues = [
                "",

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
            ];

            const inputs = ["grade_1", "grade_2", "grade_3"];

            for (let id of inputs) {
                const input = document.getElementById(id);
                const value = input.value.trim();

                if (!allowedValues.includes(value)) {
                    event.preventDefault();
                    alert("Selecciona una nota válida.");
                    return;
                }
            }
        });

        updateAverage();
    }

    /*
    ==========================================
    FILTROS DE ESTUDIANTES
    ==========================================
    */
    const searchInput = document.getElementById("searchInput");
    const classFilter = document.getElementById("classFilter");
    const semesterFilter = document.getElementById("semesterFilter");
    const statusFilter = document.getElementById("statusFilter");
    const clearFiltersBtn = document.getElementById("clearFiltersBtn");
    const studentsTable = document.getElementById("studentsTable");

    function filterStudents() {
        if (!studentsTable) return;

        const searchText = searchInput ? searchInput.value.toLowerCase().trim() : "";
        const selectedClass = classFilter ? classFilter.value.toLowerCase().trim() : "";
        const selectedSemester = semesterFilter ? semesterFilter.value.toLowerCase().trim() : "";
        const selectedStatus = statusFilter ? statusFilter.value.toLowerCase().trim() : "";

        const rows = studentsTable.getElementsByTagName("tr");

        for (let row of rows) {
            const rowText = row.innerText.toLowerCase();
            const rowClass = (row.getAttribute("data-class") || "").toLowerCase();
            const rowSemester = (row.getAttribute("data-semester") || "").toLowerCase();
            const rowStatus = (row.getAttribute("data-status") || "").toLowerCase();

            const matchesSearch = rowText.includes(searchText);
            const matchesClass = selectedClass === "" || rowClass === selectedClass;
            const matchesSemester = selectedSemester === "" || rowSemester === selectedSemester;
            const matchesStatus = selectedStatus === "" || rowStatus === selectedStatus;

            row.style.display = matchesSearch && matchesClass && matchesSemester && matchesStatus ? "" : "none";
        }
    }

    if (searchInput) {
        searchInput.addEventListener("input", filterStudents);
    }

    if (classFilter) {
        classFilter.addEventListener("change", filterStudents);
    }

    if (semesterFilter) {
        semesterFilter.addEventListener("change", filterStudents);
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", filterStudents);
    }

    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener("click", function () {
            if (searchInput) searchInput.value = "";
            if (classFilter) classFilter.value = "";
            if (semesterFilter) semesterFilter.value = "";
            if (statusFilter) statusFilter.value = "";

            filterStudents();
        });
    }

    /*
    ==========================================
    FILTRO DE CASOS
    ==========================================
    */
    const caseSearchInput = document.getElementById("caseSearchInput");
    const casesTable = document.getElementById("casesTable");

    if (caseSearchInput && casesTable) {
        caseSearchInput.addEventListener("input", function () {
            const searchText = caseSearchInput.value.toLowerCase();
            const rows = casesTable.getElementsByTagName("tr");

            for (let row of rows) {
                const rowText = row.innerText.toLowerCase();
                row.style.display = rowText.includes(searchText) ? "" : "none";
            }
        });
    }

    /*
    ==========================================
    FILTRO DE CLASES
    ==========================================
    */
    const classSearchInput = document.getElementById("classSearchInput");
    const classesTable = document.getElementById("classesTable");

    if (classSearchInput && classesTable) {
        classSearchInput.addEventListener("input", function () {
            const searchText = classSearchInput.value.toLowerCase();
            const rows = classesTable.getElementsByTagName("tr");

            for (let row of rows) {
                const rowText = row.innerText.toLowerCase();
                row.style.display = rowText.includes(searchText) ? "" : "none";
            }
        });
    }

    /*
    ==========================================
    BARRAS DE PROGRESO / REPORTES SI EXISTEN
    ==========================================
    */
    const bars = document.querySelectorAll(".bar-fill");

    bars.forEach(function (bar) {
        const width = bar.getAttribute("data-width");

        if (width !== null) {
            bar.style.width = width + "%";
        }
    });
});