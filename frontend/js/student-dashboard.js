const API_URL = "http://127.0.0.1:8000";

/* =========================================
   GET ACCESS TOKEN
========================================= */

const token = localStorage.getItem("access_token");


/* =========================================
   CHECK LOGIN
========================================= */

if (!token) {
    alert("Please login first.");
    window.location.href = "../index.html";
}


/* =========================================
   LOAD STUDENT PROFILE
========================================= */

async function loadStudentProfile() {

    try {

        const response = await fetch(
            `${API_URL}/student/profile`,
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );


        const data = await response.json();


        console.log(
            "STUDENT PROFILE RESPONSE:",
            data
        );


        /* ================================
           ERROR
        ================================= */

        if (!response.ok) {

            alert(
                data.detail ||
                "Unable to load student profile."
            );

            return;
        }


        /* ================================
           STUDENT INFORMATION
        ================================= */

        document.getElementById(
            "studentName"
        ).textContent =
            data.full_name || "Not available";


        document.getElementById(
            "studentEmail"
        ).textContent =
            data.email || "Not available";


        document.getElementById(
            "studentPhone"
        ).textContent =
            data.phone || "Not available";


        document.getElementById(
            "studentDob"
        ).textContent =
            data.dob || "Not available";


        document.getElementById(
            "studentStandard"
        ).textContent =
            data.standard || "Not available";


        /* ================================
           TEACHER INFORMATION
        ================================= */

        if (data.teacher) {

            document.getElementById(
                "teacherName"
            ).textContent =
                data.teacher.full_name ||
                "Not available";


            document.getElementById(
                "teacherEmail"
            ).textContent =
                data.teacher.email ||
                "Not available";


            document.getElementById(
                "teacherSubject"
            ).textContent =
                data.teacher.subject ||
                "Not available";

        } else {

            document.getElementById(
                "teacherName"
            ).textContent =
                "No teacher assigned";


            document.getElementById(
                "teacherEmail"
            ).textContent =
                "—";


            document.getElementById(
                "teacherSubject"
            ).textContent =
                "—";
        }


    } catch (error) {

        console.error(
            "Student profile error:",
            error
        );


        alert(
            "Unable to connect to the server. " +
            "Make sure FastAPI is running."
        );
    }
}


/* =========================================
   LOGOUT
========================================= */

const logoutButton =
    document.getElementById("logoutButton");


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


/* =========================================
   LOAD PROFILE WHEN PAGE OPENS
========================================= */

loadStudentProfile();