from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import (UserCreate,OTPVerify,UserLogin,ChangePassword,ForgotPasswordRequest,
ForgotPasswordVerifyOTP,ResetPassword,ResendOTP,AssignTeacher,TeacherStudentResponse,TeacherStudentUpdate,
StudentProfileResponse,AdminStudentResponse,AdminTeacherResponse,AdminUserCreate,FirstLoginOTPVerify,
FirstLoginPasswordChange,AdminStudentUpdate,AdminTeacherUpdate,AdminRoleUpdate)
from auth import (hash_password,verify_password,create_access_token,verify_token,
create_reset_token,generate_temporary_password,create_first_login_token)
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from otp import generate_otp
from datetime import datetime,timedelta
from email_service import send_otp_email,send_password_changed_email,send_login_credentials_email
from fastapi.middleware.cors import CORSMiddleware
import models
from fastapi import BackgroundTasks

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security=HTTPBearer()

Base.metadata.create_all(bind=engine)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    if payload.get("type") in ["password_reset", "first_login"]:
        raise HTTPException(
        status_code=403,
        detail="Reset token cannot be used for this endpoint"
    )

    return payload



def get_current_admin(
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user


def get_current_teacher(
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Teacher access required"
        )

    return current_user


def get_current_student(
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=403,
            detail="Student access required"
        )

    return current_user


def get_password_reset_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired reset token"
        )

    if payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=403,
            detail="Invalid token type"
        )

    return payload



def get_first_login_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    if payload.get("type") != "first_login":
        raise HTTPException(
            status_code=403,
            detail="First-login token required"
        )

    return payload


@app.post("/registration",tags=["Authentication"])
def user_create(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Check if email already exists
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email Already Registered"
        )

    # Hash password
    hashed_password = hash_password(user.password)

    # Generate OTP
    otp = generate_otp()

    # OTP valid for 5 minutes
    otp_expiry = datetime.now() + timedelta(minutes=5)

    # Create new user
    new_user = models.User(
    full_name=user.full_name,
    email=user.email,
    phone=user.phone,
    dob=user.dob,
    role=user.role,
    subject=user.subject,
    standard=user.standard,
    password_hash=hashed_password,
    otp=otp,
    otp_expiry=otp_expiry
    )

    # Save user to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send OTP email in background
    background_tasks.add_task(
        send_otp_email,
        user.email,
        otp
    )

    return {
        "message": "Registration successful",
        "user_id": new_user.id
    }

@app.post("/resend-otp",tags=["Authentication"])
def resend_otp(
    data: ResendOTP,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.email_verified:
        raise HTTPException(
            status_code=400,
            detail="Email is already verified"
        )

   
    new_otp = generate_otp()

   
    new_otp_expiry = datetime.now() + timedelta(minutes=5)

    
    user.otp = new_otp
    user.otp_expiry = new_otp_expiry

    db.commit()

   
    send_otp_email(user.email, new_otp)

    return {
        "message": "New OTP sent successfully"
    }


@app.post("/verify-otp",tags=["Authentication"])
def verify_otp(
    data: OTPVerify,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.otp != data.otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    if user.otp_expiry < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="OTP has expired"
        )

    user.email_verified = True
    user.otp = None
    user.otp_expiry = None

    db.commit()

    return {
        "message": "Email verified successfully"
    }


@app.post("/login",tags=["Authentication"])
def login(
    user: UserLogin,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not verify_password(
        user.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    # First-time login for Admin-created users
    if existing_user.must_change_password:
        otp = generate_otp()
        otp_expiry = datetime.now() + timedelta(minutes=5)

        existing_user.otp = otp
        existing_user.otp_expiry = otp_expiry

        db.commit()

        background_tasks.add_task(
            send_otp_email,
            existing_user.email,
            otp
        )

        return {
            "message": "First-time login required",
            "requires_otp": True,
            "user_id": existing_user.id
        }

    # Normal users must have verified email
    if not existing_user.email_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified"
        )

    # Create normal access token
    token = create_access_token(
        {
            "user_id": existing_user.id,
            "email": existing_user.email,
            "role": existing_user.role
        }
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
    }


@app.put("/change-password",tags=["Password Management"])
def change_password(
    data: ChangePassword,
    background_tasks:BackgroundTasks,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not verify_password(
        data.old_password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Old password is incorrect"
        )

    user.password_hash = hash_password(data.new_password)

    db.commit()

    background_tasks.add_task(
        send_password_changed_email,
        user.email
    )

    return {
        "message": "Password changed successfully"
    }


@app.post("/forget-password",tags=["Password Management"])
def forget_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    otp = generate_otp()

    user.otp = otp
    user.otp_expiry = datetime.now() + timedelta(minutes=5)

    db.commit()

    background_tasks.add_task(
        send_otp_email,
        user.email,
        otp
    )

    return {
        "message": "OTP Send To Your Email."
    }


@app.post("/forgot-password/verify-otp",tags=["Password Management"])
def verify_forgot_password_otp(
    data: ForgotPasswordVerifyOTP,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.otp != data.otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    if user.otp_expiry < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="OTP has expired"
        )

    user.otp = None
    user.otp_expiry = None
    db.commit()


    reset_token = create_reset_token(user.id)


    return {
        "message": "OTP verified successfully",
        "reset_token":reset_token
    }



@app.post("/reset-password",tags=["Password Management"])
def reset_password(
    data: ResetPassword,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_password_reset_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.password_hash = hash_password(data.new_password)

    db.commit()

    background_tasks.add_task(
            send_password_changed_email,
            user.email
        )
    
    
    return {
        "message": "Password reset successfully"
    }


@app.post("/logout",tags=["Logout"])
def logout(
    current_user=Depends(get_current_user)
):
    return {
        "message": "Logout successful"
    }




@app.put("/admin/students/{student_id}/assign-teacher",tags=["Admin"])
def assign_teacher(
    student_id: int,
    assignment: AssignTeacher,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    student = db.query(models.User).filter(
        models.User.id == student_id,
        models.User.role == "student"
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    teacher = db.query(models.User).filter(
        models.User.id == assignment.teacher_id,
        models.User.role == "teacher"
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    student.teacher_id = teacher.id

    db.commit()
    db.refresh(student)

    return {
        "message": "Student assigned to teacher successfully",
        "student_id": student.id,
        "teacher_id": teacher.id
    }




@app.get("/teacher/students",response_model=list[TeacherStudentResponse],tags=["Teacher"])
def get_assigned_students(
    current_teacher: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    teacher_id = current_teacher.get("user_id")

    students = db.query(models.User).filter(
        models.User.role == "student",
        models.User.teacher_id == teacher_id
    ).all()

    return students






@app.put("/teacher/students/{student_id}",tags=["Teacher"])
def update_assigned_student(
    student_id: int,
    student_data: TeacherStudentUpdate,
    current_teacher: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    teacher_id = current_teacher.get("user_id")

    student = db.query(models.User).filter(
        models.User.id == student_id,
        models.User.role == "student"
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if student.teacher_id != teacher_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your assigned students"
        )

    if student_data.full_name is not None:
        student.full_name = student_data.full_name

    if student_data.phone is not None:
        student.phone = student_data.phone

    if student_data.dob is not None:
        student.dob = student_data.dob

    if student_data.standard is not None:
        student.standard = student_data.standard

    db.commit()
    db.refresh(student)

    return {
        "message": "Student updated successfully",
        "student_id": student.id
    }





@app.get(
    "/student/profile",
    response_model=StudentProfileResponse,
     tags=["Student"]
)
def get_student_profile(
    current_student: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student_id = current_student.get("user_id")

    student = db.query(models.User).filter(
        models.User.id == student_id,
        models.User.role == "student"
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    teacher = None

    if student.teacher_id:
        teacher = db.query(models.User).filter(
            models.User.id == student.teacher_id,
            models.User.role == "teacher"
        ).first()

    return {
        "id": student.id,
        "full_name": student.full_name,
        "email": student.email,
        "phone": student.phone,
        "dob": student.dob,
        "standard": student.standard,
        "teacher": teacher
    }



@app.get(
    "/admin/students",
    response_model=list[AdminStudentResponse],
    tags=["Admin"]
)
def get_all_students(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    students = db.query(models.User).filter(
        models.User.role == "student"
    ).all()

    return students




@app.get(
    "/admin/teachers",
    response_model=list[AdminTeacherResponse],
    tags=["Admin"]
)
def get_all_teachers(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    teachers = db.query(models.User).filter(
        models.User.role == "teacher"
    ).all()

    return teachers



@app.post("/admin/users",tags=["Admin"])
def admin_create_user(
    user: AdminUserCreate,
    background_tasks: BackgroundTasks,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Check if email already exists
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Generate temporary password
    temporary_password = generate_temporary_password()

    # Hash temporary password
    hashed_password = hash_password(temporary_password)

    # Create new user
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        dob=user.dob,
        role=user.role,
        subject=user.subject,
        standard=user.standard,
        password_hash=hashed_password,
        email_verified=False,
        must_change_password=True
    )

    # Save user to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send login credentials by email
    background_tasks.add_task(
        send_login_credentials_email,
        user.email,
        temporary_password
    )

    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "role": new_user.role,
        "email": new_user.email
    }





@app.post("/first-login/verify-otp",tags=["First Login"])
def verify_first_login_otp(
    data: FirstLoginOTPVerify,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not user.must_change_password:
        raise HTTPException(
            status_code=400,
            detail="First-time login is not required"
        )

    if user.otp != data.otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    if not user.otp_expiry or user.otp_expiry < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="OTP expired"
        )

    first_login_token = create_first_login_token(user.id)

    return {
        "message": "OTP verified successfully",
        "first_login_token": first_login_token
    }





@app.post("/first-login/change-password",tags=["First Login"])
def first_login_change_password(
    data: FirstLoginPasswordChange,
    first_login_user: dict = Depends(get_first_login_user),
    db: Session = Depends(get_db)
):
    user_id = first_login_user.get("user_id")

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not user.must_change_password:
        raise HTTPException(
            status_code=400,
            detail="First-time password change is not required"
        )

    user.password_hash = hash_password(data.new_password)
    user.must_change_password = False
    user.email_verified = True

    user.otp = None
    user.otp_expiry = None

    db.commit()

    return {
        "message": "Password changed successfully. You can now login normally."
    }










@app.put("/admin/students/{student_id}",tags=["Admin"])
def update_student_by_admin(
    student_id: int,
    student_data: AdminStudentUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    student = db.query(models.User).filter(
        models.User.id == student_id,
        models.User.role == "student"
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if student_data.full_name is not None:
        student.full_name = student_data.full_name

    if student_data.phone is not None:
        student.phone = student_data.phone

    if student_data.dob is not None:
        student.dob = student_data.dob

    if student_data.standard is not None:
        student.standard = student_data.standard

    if student_data.teacher_id is not None:

        teacher = db.query(models.User).filter(
            models.User.id == student_data.teacher_id,
            models.User.role == "teacher"
        ).first()

        if not teacher:
            raise HTTPException(
                status_code=404,
                detail="Teacher not found"
            )

        student.teacher_id = teacher.id

    db.commit()
    db.refresh(student)

    return {
        "message": "Student updated successfully",
        "student_id": student.id
    }



@app.put("/admin/teachers/{teacher_id}",tags=["Admin"])
def update_teacher_by_admin(
    teacher_id: int,
    teacher_data: AdminTeacherUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    teacher = db.query(models.User).filter(
        models.User.id == teacher_id,
        models.User.role == "teacher"
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    if teacher_data.full_name is not None:
        teacher.full_name = teacher_data.full_name

    if teacher_data.phone is not None:
        teacher.phone = teacher_data.phone

    if teacher_data.dob is not None:
        teacher.dob = teacher_data.dob

    if teacher_data.subject is not None:
        teacher.subject = teacher_data.subject

    db.commit()
    db.refresh(teacher)

    return {
        "message": "Teacher updated successfully",
        "teacher_id": teacher.id
    }





@app.delete("/admin/students/{student_id}",tags=["Admin"])
def delete_student_by_admin(
    student_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    student = db.query(models.User).filter(
        models.User.id == student_id,
        models.User.role == "student"
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted successfully",
        "student_id": student_id
    }





@app.delete("/admin/teachers/{teacher_id}",tags=["Admin"])
def delete_teacher_by_admin(
    teacher_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    teacher = db.query(models.User).filter(
        models.User.id == teacher_id,
        models.User.role == "teacher"
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    students = db.query(models.User).filter(
        models.User.teacher_id == teacher_id,
        models.User.role == "student"
    ).all()

    for student in students:
        student.teacher_id = None

    db.delete(teacher)
    db.commit()

    return {
        "message": "Teacher deleted successfully",
        "teacher_id": teacher_id
    }




@app.get(
    "/admin/students/{student_id}",
    response_model=AdminStudentResponse,
    tags=["Admin"]
)
def get_student_by_admin(
    student_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    student = db.query(models.User).filter(
        models.User.id == student_id,
        models.User.role == "student"
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student





@app.get(
    "/admin/teachers/{teacher_id}",
    response_model=AdminTeacherResponse,
    tags=["Admin"]
)
def get_teacher_by_admin(
    teacher_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    teacher = db.query(models.User).filter(
        models.User.id == teacher_id,
        models.User.role == "teacher"
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return teacher





@app.put("/admin/users/{user_id}/role",tags=["Admin"])
def update_user_role(
    user_id: int,
    role_data: AdminRoleUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Admin's role cannot be changed
    if user.role == "admin":
        raise HTTPException(
            status_code=400,
            detail="Admin role cannot be changed"
        )


    # Teacher → Student
  
    if user.role == "teacher" and role_data.role == "student":

        # Find students currently assigned to this teacher
        assigned_students = db.query(models.User).filter(
            models.User.teacher_id == user_id,
            models.User.role == "student"
        ).all()

        # Remove the old teacher relationship
        for student in assigned_students:
            student.teacher_id = None

        # Convert teacher into student
        user.role = "student"
        user.standard = role_data.standard
        user.subject = None
        user.teacher_id = None

   
    # Student → Teacher
   
    elif user.role == "student" and role_data.role == "teacher":

        # Convert student into teacher
        user.role = "teacher"
        user.subject = role_data.subject
        user.standard = None

        # A teacher cannot have a teacher
        user.teacher_id = None

    
    # Same role → Same role
    
    elif user.role == role_data.role:

        if role_data.role == "teacher":
            user.subject = role_data.subject
            user.standard = None
            user.teacher_id = None

        elif role_data.role == "student":
            user.standard = role_data.standard
            user.subject = None

    db.commit()
    db.refresh(user)

    return {
        "message": "User role updated successfully",
        "user_id": user.id,
        "role": user.role
    }