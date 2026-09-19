from flask import Flask, render_template, request, jsonify
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
    "Pothole": "MCC Engineering Department",
    "Streetlight": "MCC Electrical Department",
    "Garbage": "MCC Solid Waste Management Department",
    "Water Supply": "Vani Vilas Water Works",
    "Drainage": "MCC Engineering / Drainage Department",
    "Other": "MCC General Administration"
}

# =====================================================
# FOLLOW-THROUGH STATUS MODEL
# =====================================================

STATUS_ORDER = [
    "Submitted",
    "Viewed by Department",
    "Action in Progress",
    "Resolved"
]

STATUS_MESSAGES = {
    "Submitted": "Your complaint has been registered. We are waiting for the latest department update.",
    "Viewed by Department": "The responsible department has viewed your complaint.",
    "Action in Progress": "The department has started working on the reported issue.",
    "Resolved": "The complaint has been marked as resolved by the department."
}


def add_status_update(complaint, status):
    """Add a new follow-through status to the complaint timeline."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    complaint["status"] = status
    complaint["status_message"] = STATUS_MESSAGES[status]
    complaint["last_updated_at"] = now
    complaint["status_history"].append({
        "status": status,
        "message": STATUS_MESSAGES[status],
        "updated_at": now
    })


# =====================================================
# HOME PAGE + COMPLAINT SUBMISSION
# =====================================================

@app.route("/", methods=["GET", "POST"])
def home():
    global complaint_counter

    if request.method == "POST":
        issue_type = request.form.get("issue_type")
        description = request.form.get("description")
        location = request.form.get("location")
        priority = request.form.get("priority")

        department = DEPARTMENT_MAP.get(
            issue_type,
            "MCC General Administration"
        )

        complaint_id = f"CP-2026-{complaint_counter:04d}"
        complaint_counter += 1

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        complaint = {
            "complaint_id": complaint_id,
            "issue_type": issue_type,
            "description": description,
            "location": location,
            "priority": priority,
            "department": department,
            "status": "Submitted",
            "status_message": STATUS_MESSAGES["Submitted"],
            "created_at": created_at,
            "last_updated_at": created_at,
            "status_history": [
                {
                    "status": "Submitted",
                    "message": "Complaint submitted successfully and assigned a tracking ID.",
                    "updated_at": created_at
                }
            ]
        }

        complaints.append(complaint)

        return render_template(
            "index.html",
            submitted=True,
            complaint=complaint
        )

    return render_template(
        "index.html",
        submitted=False
    )


# =====================================================
# TRACK COMPLAINT
# =====================================================

@app.route("/track/<complaint_id>")
def track_complaint(complaint_id):
    for complaint in complaints:
        if complaint["complaint_id"] == complaint_id:
            return render_template(
                "track.html",
                complaint=complaint,
                status_order=STATUS_ORDER
            )

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
                box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            }
            h1 { color: #172033; }
            p { color: #6d7889; }
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
            <h1>Complaint Not Found</h1>
            <p>We couldn't find a complaint with this ID.</p>
            <a href="/">Return to CivicPulse</a>
        </div>
    </body>
    </html>
    """


# =====================================================
# DEPARTMENT STATUS UPDATE API
# =====================================================
# This API is the integration point for a future official
# department system. It is intentionally not exposed as a
# department dashboard in the citizen MVP.

@app.route("/api/complaints/<complaint_id>/status", methods=["POST"])
def update_complaint_status(complaint_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in STATUS_ORDER:
        return jsonify({
            "success": False,
            "message": "Invalid status.",
            "allowed_statuses": STATUS_ORDER
        }), 400

    for complaint in complaints:
        if complaint["complaint_id"] == complaint_id:
            add_status_update(complaint, new_status)

            return jsonify({
                "success": True,
                "complaint_id": complaint_id,
                "status": complaint["status"],
                "message": complaint["status_message"],
                "updated_at": complaint["last_updated_at"]
            })

    return jsonify({
        "success": False,
        "message": "Complaint not found."
    }), 404


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)
