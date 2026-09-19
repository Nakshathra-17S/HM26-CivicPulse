from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)


# =====================================================
# TEMPORARY COMPLAINT STORAGE
# =====================================================

complaints = []

complaint_counter = 1


# =====================================================
# DEPARTMENT MAPPING
# =====================================================

DEPARTMENT_MAP = {

    "Pothole":
        "MCC Engineering Department",

    "Streetlight":
        "MCC Electrical Department",

    "Garbage":
        "MCC Solid Waste Management Department",

    "Water Supply":
        "Vani Vilas Water Works",

    "Drainage":
        "MCC Engineering / Drainage Department",

    "Other":
        "MCC General Administration"

}


# =====================================================
# HOME PAGE + COMPLAINT SUBMISSION
# =====================================================

@app.route("/", methods=["GET", "POST"])
def home():

    global complaint_counter


    # -----------------------------------------------
    # SUBMIT COMPLAINT
    # -----------------------------------------------

    if request.method == "POST":

        issue_type = request.form.get("issue_type")

        description = request.form.get("description")

        location = request.form.get("location")

        priority = request.form.get("priority")


        # Find department

        department = DEPARTMENT_MAP.get(
            issue_type,
            "MCC General Administration"
        )


        # Generate complaint ID

        complaint_id = (
            f"CP-2026-{complaint_counter:04d}"
        )

        complaint_counter += 1


        # Create complaint

        complaint = {

            "complaint_id":
                complaint_id,

            "issue_type":
                issue_type,

            "description":
                description,

            "location":
                location,

            "priority":
                priority,

            "department":
                department,

            "status":
                "Open",

            "created_at":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        }


        # Store complaint

        complaints.append(complaint)


        # Show success page

        return render_template(

            "index.html",

            submitted=True,

            complaint=complaint

        )


    # Normal homepage

    return render_template(

        "index.html",

        submitted=False

    )


# =====================================================
# TRACK COMPLAINT
# =====================================================

@app.route("/track/<complaint_id>")
def track_complaint(complaint_id):


    # Search for complaint

    for complaint in complaints:

        if complaint["complaint_id"] == complaint_id:

            return render_template(

                "track.html",

                complaint=complaint

            )


    # Complaint not found

    return """

    <!DOCTYPE html>

    <html>

    <head>

        <title>Complaint Not Found</title>

        <style>

            body {

                font-family: Arial, sans-serif;

                background: #f7f9fc;

                display: flex;

                justify-content: center;

                align-items: center;

                min-height: 100vh;

                margin: 0;

            }

            .box {

                background: white;

                padding: 40px;

                border-radius: 15px;

                text-align: center;

                box-shadow:
                    0 10px 30px
                    rgba(0,0,0,0.08);

            }

            h1 {

                color: #172033;

            }

            p {

                color: #6d7889;

            }

            a {

                display: inline-block;

                margin-top: 15px;

                background: #176b87;

                color: white;

                padding: 12px 18px;

                border-radius: 8px;

                text-decoration: none;

            }

        </style>

    </head>


    <body>

        <div class="box">

            <h1>
                Complaint Not Found
            </h1>

            <p>
                We couldn't find a complaint with this ID.
            </p>

            <a href="/">
                Return to CivicPulse
            </a>

        </div>

    </body>

    </html>

    """


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

    app.run(debug=True)