const API_URL = "http://127.0.0.1:8000";


/* ==================================================
   GET USER ID
================================================== */

const userId = localStorage.getItem("first_login_user_id");


/* ==================================================
   OTP FORM
================================================== */

const otpForm = document.getElementById("firstLoginOTPForm");


if (otpForm) {

    otpForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const otpInput = document.getElementById("otp");

        const otp = otpInput
            ? otpInput.value.trim()
            : "";


        /* ================================
           CHECK USER ID
        ================================ */

        if (!userId) {

            alert(
                "First login session expired. Please login again."
            );

            window.location.href = "/frontend/index.html";

            return;
        }


        /* ================================
           OTP VALIDATION
        ================================ */

        if (!otp) {

            alert("Please enter the OTP.");

            return;
        }


        if (!/^\d{6}$/.test(otp)) {

            alert("OTP must be exactly 6 digits.");

            return;
        }


        try {

            /* ================================
               VERIFY OTP
            ================================ */

            const response = await fetch(
                `${API_URL}/first-login/verify-otp`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        user_id: Number(userId),
                        otp: otp
                    })
                }
            );


            const data = await response.json();


            console.log(
                "FIRST LOGIN OTP RESPONSE:",
                data
            );


            /* ================================
               OTP ERROR
            ================================ */

            if (!response.ok) {

                alert(
                    data.detail ||
                    "OTP verification failed."
                );

                return;
            }


            /* ================================
               SAVE FIRST LOGIN TOKEN
            ================================ */

            if (data.first_login_token) {

                localStorage.setItem(
                    "first_login_token",
                    data.first_login_token
                );

                console.log(
                    "FIRST LOGIN TOKEN SAVED"
                );

            } else {

                console.error(
                    "first_login_token missing from response"
                );

                alert(
                    "First login token was not received."
                );

                return;
            }


            /* ================================
               SHOW PASSWORD FORM
            ================================ */

            showPasswordChangeForm();

        }

        catch (error) {

            console.error(
                "First login OTP error:",
                error
            );

            alert(
                "Unable to connect to the server. " +
                "Make sure FastAPI is running."
            );

        }

    });

}


/* ==================================================
   SHOW PASSWORD CHANGE FORM
================================================== */

function showPasswordChangeForm() {

    const card = document.querySelector(".login-card");


    if (!card) {

        console.error(
            "Login card not found."
        );

        return;
    }


    card.innerHTML = `

        <div class="mobile-logo">

            <div class="logo-icon">
                R
            </div>

            <div>

                <h1>
                    RUBM
                </h1>

                <p>
                    Role-Based User Management
                </p>

            </div>

        </div>


        <div class="login-header">

            <span class="welcome-text">
                ACCOUNT SECURITY
            </span>

            <h2>
                Create your new password
            </h2>

            <p>
                Your OTP has been verified.
                Please create a new password
                to continue.
            </p>

        </div>


        <form id="firstLoginPasswordForm">

            <!-- NEW PASSWORD -->

            <div class="input-group">

                <label for="newPassword">
                    New Password
                </label>

                <div class="input-wrapper">

                    <span class="input-icon">
                        🔒
                    </span>

                    <input
                        type="password"
                        id="newPassword"
                        placeholder="Enter new password"
                        required
                    >

                    <button
                        type="button"
                        class="show-password"
                        id="toggleNewPassword"
                    >
                        👁
                    </button>

                </div>

            </div>


            <!-- CONFIRM PASSWORD -->

            <div class="input-group">

                <label for="confirmPassword">
                    Confirm Password
                </label>

                <div class="input-wrapper">

                    <span class="input-icon">
                        🔒
                    </span>

                    <input
                        type="password"
                        id="confirmPassword"
                        placeholder="Confirm new password"
                        required
                    >

                </div>

            </div>


            <!-- PASSWORD RULES -->

            <div class="password-rules">

                <p>
                    Password must contain:
                </p>

                <span>
                    • At least 10 characters
                </span>

                <span>
                    • At least one alphabet
                </span>

                <span>
                    • At least one number
                </span>

                <span>
                    • At least one special character
                </span>

            </div>


            <!-- SUBMIT -->

            <button
                type="submit"
                class="login-button"
            >

                <span>
                    Set New Password
                </span>

                <span class="arrow">
                    →
                </span>

            </button>

        </form>

    `;


    /* ==================================================
       SHOW / HIDE NEW PASSWORD
    ================================================== */

    const passwordInput =
        document.getElementById("newPassword");

    const togglePassword =
        document.getElementById("toggleNewPassword");


    if (passwordInput && togglePassword) {

        togglePassword.addEventListener(
            "click",
            () => {

                if (
                    passwordInput.type === "password"
                ) {

                    passwordInput.type = "text";

                    togglePassword.textContent = "🙈";

                } else {

                    passwordInput.type = "password";

                    togglePassword.textContent = "👁";

                }

            }
        );

    }

}


/* ==================================================
   PASSWORD FORM SUBMIT
   EVENT DELEGATION
================================================== */

document.addEventListener(
    "submit",
    (event) => {

        if (
            event.target &&
            event.target.id ===
            "firstLoginPasswordForm"
        ) {

            event.preventDefault();

            console.log(
                "🔥 CHANGE PASSWORD FUNCTION CALLED"
            );

            changeFirstLoginPassword();

        }

    }
);


/* ==================================================
   CHANGE FIRST LOGIN PASSWORD
================================================== */

async function changeFirstLoginPassword() {

    console.log(
        "🔥 CHANGE PASSWORD FUNCTION STARTED"
    );


    /* ================================
       GET INPUTS
    ================================ */

    const newPasswordElement =
        document.getElementById("newPassword");

    const confirmPasswordElement =
        document.getElementById("confirmPassword");


    if (
        !newPasswordElement ||
        !confirmPasswordElement
    ) {

        console.error(
            "Password input fields not found."
        );

        return;
    }


    const newPassword =
        newPasswordElement.value;

    const confirmPassword =
        confirmPasswordElement.value;


    /* ================================
       PASSWORD VALIDATION
    ================================ */

    if (newPassword.length < 10) {

        alert(
            "Password must contain at least 10 characters."
        );

        return;
    }


    if (!/[A-Za-z]/.test(newPassword)) {

        alert(
            "Password must contain at least one alphabet."
        );

        return;
    }


    if (!/[0-9]/.test(newPassword)) {

        alert(
            "Password must contain at least one number."
        );

        return;
    }


    if (!/[^A-Za-z0-9]/.test(newPassword)) {

        alert(
            "Password must contain at least one special character."
        );

        return;
    }


    if (newPassword !== confirmPassword) {

        alert(
            "Passwords do not match."
        );

        return;
    }


    /* ==================================================
       GET FIRST LOGIN TOKEN
    ================================================== */

    const token =
        localStorage.getItem(
            "first_login_token"
        );


    console.log(
        "FIRST LOGIN TOKEN EXISTS:",
        !!token
    );


    if (!token) {

        alert(
            "First login session expired. Please login again."
        );

        window.location.href =
            "/frontend/index.html";

        return;
    }


    try {

        console.log(
            "🔥 SENDING PASSWORD CHANGE REQUEST..."
        );


        /* ==================================================
           CHANGE PASSWORD API
        ================================================== */

        const response = await fetch(
            `${API_URL}/first-login/change-password`,
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json",

                    "Authorization":
                        `Bearer ${token}`

                },

                body: JSON.stringify({

                    new_password:
                        newPassword

                })

            }
        );


        const data =
            await response.json();


        console.log(
            "FIRST LOGIN PASSWORD RESPONSE:",
            data
        );


        /* ================================
           API ERROR
        ================================ */

        if (!response.ok) {

            alert(
                data.detail ||
                "Unable to change password."
            );

            return;
        }


        /* ==================================================
           SUCCESS
        ================================================== */

        console.log(
            "🔥 PASSWORD CHANGE SUCCESS"
        );


        /* ==================================================
           CLEAR FIRST LOGIN DATA
        ================================================== */

        localStorage.removeItem(
            "first_login_user_id"
        );

        localStorage.removeItem(
            "first_login_token"
        );


        console.log(
            "🔥 FIRST LOGIN DATA CLEARED"
        );


        /* ==================================================
           GO TO LOGIN PAGE
        ================================================== */

        console.log(
            "🔥 REDIRECTING TO LOGIN PAGE"
        );


        window.location.href =
            "/frontend/index.html";

    }

    catch (error) {

        console.error(
            "First login password error:",
            error
        );

        alert(
            "Unable to connect to the server. " +
            "Make sure FastAPI is running."
        );

    }

}