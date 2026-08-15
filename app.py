from flask import Flask, render_template, request, redirect, url_for, flash
import os
import pandas as pd

app = Flask(__name__)

app.secret_key = "jp-it-staffing-export"

UPLOAD_FOLDER = "data"
ALLOWED_EXTENSIONS = {"csv"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        if "file" not in request.files:
            flash("No file selected.")
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("Please select a CSV file.")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Only CSV files are allowed.")
            return redirect(request.url)

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "buyers.csv"
        )

        file.save(filepath)

        try:
            df = pd.read_csv(filepath)

            total_buyers = len(df)

            return render_template(
                "upload.html",
                uploaded=True,
                total_buyers=total_buyers,
                columns=list(df.columns)
            )

        except Exception as e:

            flash(f"Could not read the CSV file: {e}")

            return redirect(request.url)

    return render_template("upload.html", uploaded=False)


@app.route("/classify", methods=["GET", "POST"])
def classify():

    if request.method == "POST":

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "buyers.csv"
        )

        if not os.path.exists(filepath):
            flash("Please upload a buyer database first.")
            return redirect(url_for("upload"))

        try:
            df = pd.read_csv(filepath)

            business_count = 0
            individual_count = 0

            for _, row in df.iterrows():

                email = str(row.get("email", "")).lower()

                company = str(
                    row.get("company_name", "")
                ).lower()

                website = str(
                    row.get("website", "")
                ).lower()

                business_words = [
                    "company",
                    "store",
                    "shop",
                    "center",
                    "centre",
                    "business",
                    "wellness",
                    "clinic",
                    "enterprise"
                ]

                is_business = any(
                    word in company
                    for word in business_words
                )

                if not is_business:
                    is_business = (
                        "www." in website
                        or "http" in website
                    )

                if is_business:
                    business_count += 1
                else:
                    individual_count += 1

            total_contacts = len(df)

            return render_template(
                "classify.html",
                classified=True,
                business_count=business_count,
                individual_count=individual_count,
                total_contacts=total_contacts
            )

        except Exception as e:

            flash(f"Classification error: {e}")

            return redirect(url_for("classify"))

    return render_template(
        "classify.html",
        classified=False
    )


@app.route("/campaign")
def campaign():
    return "Campaign page - coming next"


@app.route("/reports")
def reports():
    return "Reports page - coming next"


@app.route("/settings")
def settings():
    return "Settings page - coming next"


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)