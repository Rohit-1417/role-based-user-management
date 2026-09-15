const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");


/* =========================================================
   CHECK LOGIN
========================================================= */

if (!token) {

    alert("Please login first.");

    window.location.href = "../index.html";
}


/* =========================================================
   ELEMENTS
========================================================= */

const studentsContainer =
    document.getElementById("studentsContainer");

const studentModal =
    document.getElementById("studentModal");

const closeStudentModal =
    document.getElementById("closeStudentModal");

const cancelStudentEdit =
    document.getElementById("cancelStudentEdit");

const studentEditForm =
    document.getElementById("studentEditForm");


/* =========================================================
   LOAD ASSIGNED STUDENTS
========================================================= */

async function loadAssignedStudents() {

    try {

        studentsContainer.innerHTML = `
            <div class="student-loading">

                <div class="loading-spinner"></div>

                <p>
                    Loading students...
                </p>

            </div>
        `;


        const response = await fetch(
            `${API_URL}/teacher/students`,
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );


        const data = await response.json();


        console.log(
            "TEACHER STUDENTS RESPONSE:",
            data
        );


        /* =========================================
           ERROR
        ========================================= */

        if (!response.ok) {

            studentsContainer.innerHTML = `
                <div class="student-empty">

                    <p>
                        ${
                            data.detail ||
                            "Unable to load students."
                        }
                    </p>

                </div>
            `;

            return;
        }


        /* =========================================
           NO STUDENTS
        ========================================= */

        if (!data || data.length === 0) {

            studentsContainer.innerHTML = `
                <div class="student-empty">

                    <p>
                        No students are currently assigned to you.
                    </p>

                </div>
            `;

            return;
        }


        /* =========================================
           DISPLAY STUDENTS
        ========================================= */

        studentsContainer.innerHTML = "";


        data.forEach((student) => {

            const studentItem =
                document.createElement("div");

            studentItem.className =
                "student-item";


            studentItem.innerHTML = `

                <div class="student-avatar">
                    👨‍🎓
                </div>


                <div class="student-details">

                    <div class="student-text">

                        <h4>
                            ${
                                student.full_name ||
                                "Unnamed Student"
                            }
                        </h4>

                        <p>
                            ${
                                student.email ||
                                "No email available"
                            }
                        </p>

                    </div>


                    <div class="student-meta">

                        <span class="standard-badge">
                            ${
                                student.standard ||
                                "No standard"
                            }
                        </span>

                    </div>

                </div>


                <button
                    type="button"
                    class="student-action-button"
                    data-student-id="${student.id}"
                >
                    View / Edit
                </button>

            `;


            studentsContainer.appendChild(
                studentItem
            );

        });


        /* =========================================
           VIEW / EDIT BUTTONS
        ========================================= */

        const actionButtons =
            studentsContainer.querySelectorAll(
                ".student-action-button"
            );


        actionButtons.forEach((button) => {

            button.addEventListener(
                "click",
                () => {

                    const studentId =
                        Number(
                            button.dataset.studentId
                        );


                    /*
                     * IMPORTANT:
                     * We already received the student
                     * information from /teacher/students.
                     *
                     * So we don't need:
                     * GET /teacher/students/{id}
                     *
                     * That endpoint doesn't exist.
                     */

                    const student =
                        data.find(
                            (student) =>
                                student.id === studentId
                        );


                    if (!student) {

                        alert(
                            "Student information not found."
                        );

                        return;
                    }


                    openStudentEditor(
                        student
                    );

                }
            );

        });

    }

    catch (error) {

        console.error(
            "Load students error:",
            error
        );


        studentsContainer.innerHTML = `
            <div class="student-empty">

                <p>
                    Unable to connect to the server.
                    Make sure FastAPI is running.
                </p>

            </div>
        `;

    }

}


/* =========================================================
   OPEN STUDENT EDITOR
========================================================= */

function openStudentEditor(student) {

    console.log(
        "SELECTED STUDENT:",
        student
    );


    document.getElementById(
        "editStudentId"
    ).value =
        student.id;


    document.getElementById(
        "editFullName"
    ).value =
        student.full_name || "";


    document.getElementById(
        "editEmail"
    ).value =
        student.email || "";


    document.getElementById(
        "editPhone"
    ).value =
        student.phone || "";


    document.getElementById(
        "editDob"
    ).value =
        student.dob || "";


    document.getElementById(
        "editStandard"
    ).value =
        student.standard || "";


    studentModal.classList.add(
        "active"
    );

}


/* =========================================================
   CLOSE MODAL
========================================================= */

function closeModal() {

    studentModal.classList.remove(
        "active"
    );

}


/* =========================================================
   CLOSE BUTTON
========================================================= */

if (closeStudentModal) {

    closeStudentModal.addEventListener(
        "click",
        () => {

            closeModal();

        }
    );

}


/* =========================================================
   CANCEL BUTTON
========================================================= */

if (cancelStudentEdit) {

    cancelStudentEdit.addEventListener(
        "click",
        () => {

            closeModal();

        }
    );

}


/* =========================================================
   CLOSE WHEN CLICKING OUTSIDE MODAL
========================================================= */

if (studentModal) {

    studentModal.addEventListener(
        "click",
        (event) => {

            if (
                event.target === studentModal
            ) {

                closeModal();

            }

        }
    );

}


/* =========================================================
   UPDATE STUDENT
========================================================= */

if (studentEditForm) {

    studentEditForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            const studentId =
                document.getElementById(
                    "editStudentId"
                ).value;


            const fullName =
                document.getElementById(
                    "editFullName"
                ).value.trim();


            const email =
                document.getElementById(
                    "editEmail"
                ).value.trim();


            const phone =
                document.getElementById(
                    "editPhone"
                ).value.trim();


            const dob =
                document.getElementById(
                    "editDob"
                ).value;


            const standard =
                document.getElementById(
                    "editStandard"
                ).value.trim();


            /* =====================================
               BASIC VALIDATION
            ===================================== */

            if (
                !fullName ||
                !email ||
                !phone ||
                !dob ||
                !standard
            ) {

                alert(
                    "Please fill in all fields."
                );

                return;
            }


            try {

                console.log(
                    "UPDATING STUDENT:",
                    studentId
                );


                const response =
                    await fetch(
                        `${API_URL}/teacher/students/${studentId}`,
                        {
                            method: "PUT",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Authorization":
                                    `Bearer ${token}`
                            },

                            body: JSON.stringify({

                                full_name:
                                    fullName,

                                email:
                                    email,

                                phone:
                                    phone,

                                dob:
                                    dob,

                                standard:
                                    standard

                            })
                        }
                    );


                const data =
                    await response.json();


                console.log(
                    "UPDATE STUDENT RESPONSE:",
                    data
                );


                /* =================================
                   UPDATE ERROR
                ================================= */

                if (!response.ok) {

                    alert(
                        data.detail ||
                        "Unable to update student."
                    );

                    return;
                }


                /* =================================
                   SUCCESS
                ================================= */

                alert(
                    "Student updated successfully."
                );


                closeModal();


                /*
                 * Reload the student list so the
                 * updated information appears.
                 */

                await loadAssignedStudents();

            }

            catch (error) {

                console.error(
                    "Update student error:",
                    error
                );


                alert(
                    "Unable to connect to the server. " +
                    "Make sure FastAPI is running."
                );

            }

        }
    );

}


/* =========================================================
   LOGOUT
========================================================= */

const logoutButton =
    document.getElementById(
        "logoutButton"
    );


if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        () => {

            localStorage.removeItem(
                "access_token"
            );


            localStorage.removeItem(
                "user_role"
            );


            window.location.href =
                "../index.html";

        }
    );

}


/* =========================================================
   START DASHBOARD
========================================================= */

loadAssignedStudents();