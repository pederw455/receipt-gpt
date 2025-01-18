from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
import gpt
import markdown
import time

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for Flask session

CSV_FILE = "ingredients.csv"

# Ensure the CSV file exists
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Ingredient", "Quantity", "Unit"])

initialize_csv()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST" and "ingredient" in request.form:
        ingredient = request.form.get("ingredient")
        quantity = request.form.get("quantity")
        unit = request.form.get("unit")

        # Save to CSV
        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([ingredient, quantity, unit])

        return redirect(url_for("home"))

    # Read ingredients from CSV
    ingredients = []
    with open(CSV_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        ingredients = list(reader)

    # Retrieve generated recipes from session (if any)
    recipes = session.pop("recipes", None)

    return render_template("index.html", ingredients=ingredients, recipes=recipes)

@app.route("/delete", methods=["POST"])
def delete():
    index_to_delete = int(request.form.get("index"))

    # Read all rows except the one to delete
    with open(CSV_FILE, mode="r") as file:
        rows = list(csv.reader(file))

    # Remove the selected row
    if 0 <= index_to_delete < len(rows) - 1:  # Skip header
        rows.pop(index_to_delete + 1)

    # Write updated rows back to CSV
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    return redirect(url_for("home"))

@app.route("/generate_recipes", methods=["POST"])
def generate_recipes():
    try:
        # Retrieve meal type and servings from the form
        meal_type = request.form.get("meal_type")
        servings = request.form.get("servings")

        # Generate the recipe using the new parameters
        recipe_html = find_recipes(meal_type, servings)

        # Read ingredients from CSV
        with open(CSV_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            ingredients = list(reader)

        return render_template("index.html", ingredients=ingredients, recipe_html=recipe_html)
    except Exception as e:
        flash(f"Error generating recipes: {str(e)}", "danger")
        return redirect(url_for("home"))


def find_recipes(meal_type, servings):
    # Read ingredients from CSV
    with open(CSV_FILE, mode="r") as file:
        rows = list(csv.reader(file))

    # Prepare prompt
    prompt = f"""
    I have the following ingredients available:
    {rows}

    I want to prepare a {meal_type} for {servings} servings.
    Please provide a single recipe that fits these criteria. You don't need to use all ingredients.
    The recipe should include:

    1. A clear title for the dish.
    2. A list of ingredients with their quantities.
    3. Step-by-step instructions for preparation.
    4. Each step should start with a numbered heading followed by details as plain text or subpoints.
    5. The output must be in Markdown format.

    The recipe should:
    - Be realistic and appropriate for {servings} servings. Adjust ingredient quantities accordingly.
    - If the available ingredients are insufficient for the required servings, clearly state which ingredients are missing or insufficient.
    - Suggest what additional ingredients and quantities are needed to meet the requirement for {servings} servings.

    Ensure the subpoints are indented and do not continue the main numbering.
    Be realistic and don't invent recipes. If it doesn't exist, return that you didn't find anything.
    """

    print(prompt)

    if True:  # Replace with actual GPT call
        return_string = gpt.ask_chat_gpt(prompt)
        with open("recipe_output.txt", mode="w") as file:
            file.write(return_string)

    time.sleep(2)
    with open("recipe_output.txt", mode="r") as file:
        saved_string = file.read()

    # Convert Markdown to HTML
    html_string = markdown.markdown(saved_string, extensions=['extra', 'sane_lists'])
    return html_string


if __name__ == "__main__":
    app.run(debug=True)
