const API_URL = "http://127.0.0.1:8000";

const loginForm = document.getElementById("loginForm");
const passwordInput = document.getElementById("password");
const togglePassword = document.getElementById("togglePassword");


/* ================================
   SHOW / HIDE PASSWORD
================================ */

togglePassword.addEventListener("click", () => {

    if (passwordInput.type === "password") {

        passwordInput.type = "text";
        togglePassword.textContent = "🙈";

    } else {

        passwordInput.type = "password";
        togglePassword.textContent = "👁";

    }

});


/* ================================
   LOGIN
================================ */

loginForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = passwordInput.value;


    /* ================================
       BASIC VALIDATION
    ================================ */

    if (!email || !password) {

        alert("Please enter your email and password.");
        return;

    }


    try {

        /* ================================
           SEND LOGIN REQUEST
        ================================ */

        const response = await fetch(`${API_URL}/login`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })

        });


        const data = await response.json();


        /* ================================
           DEBUG LOGIN RESPONSE
        ================================ */

        console.log("LOGIN RESPONSE:", data);


        /* ================================
           LOGIN FAILED
        ================================ */

        if (!response.ok) {

            const message =
                data.detail || "Login failed. Please try again.";

            alert(message);

            return;

        }


        /* ================================
           FIRST LOGIN
        ================================ */

        if (data.requires_otp === true) {

            localStorage.setItem(
                "first_login_user_id",
                data.user_id
            );

            window.location.href = "first-login.html";

            return;

        }


        /* ================================
           NORMAL LOGIN
        ================================ */

        if (data.access_token) {

            /* ================================
               SAVE ACCESS TOKEN
            ================================ */

            localStorage.setItem(
                "access_token",
                data.access_token
            );


            /* ================================
               GET ROLE FROM JWT
            ================================ */

            const payload = JSON.parse(
                atob(data.access_token.split(".")[1])
            );

            const role = payload.role;

            console.log("USER ROLE:", role);


            /* ================================
               SAVE USER ROLE
            ================================ */

            localStorage.setItem(
                "user_role",
                role
            );


            /* ================================
               ROLE REDIRECTION
            ================================ */

            if (role === "admin") {

                window.location.href =
                    "admin/dashboard.html";

            } else if (role === "teacher") {

                window.location.href =
                    "teacher/dashboard.html";

            } else if (role === "student") {

                window.location.href =
                    "student/dashboard.html";

            } else {

                alert("Unknown user role.");

            }

        } else {

            alert("Login successful, but access token was not received.");

        }


    } catch (error) {

        /* ================================
           SERVER / NETWORK ERROR
        ================================ */

        console.error("Login error:", error);

        alert(
            "Unable to connect to the server. " +
            "Make sure FastAPI is running."
        );

    }

});