from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
import gpt
import markdown
import json
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
        # Retrieve form data
        meal_type = request.form.get("meal_type")
        servings = request.form.get("servings")
        action = request.form.get("action")

        # Read ingredients from CSV
        with open(CSV_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            ingredients = list(reader)
        print(action)
        if action == "find_recipe":
            # Generate the recipe based on the inputs
            recipe_html = find_recipes(ingredients, meal_type, servings)
        elif action == "try_my_luck":
            # Generate a random recipe
            recipe_html = try_my_luck(ingredients, meal_type, servings)

        return render_template(
            "index.html",
            ingredients=ingredients,
            recipe_html=recipe_html,  # Pass the result to the template
        )
    except Exception as e:
        flash(f"Error generating recipes: {str(e)}", "danger")
        return redirect(url_for("home"))

def try_my_luck(ingredients, meal_type, servings):
    # Prepare the prompt
    prompt = f"""
    I have the following ingredients available: basic seasonings, oil, and these specific items:
    {ingredients}

    I want to prepare a {meal_type} for {servings} servings. The recipe should be a real, authentic dish. 
    While you don’t need to use all the available ingredients, try to incorporate as many as possible. 
    If additional ingredients or more of the existing ones are needed, include them in a "Shopping Cart" section formatted as:
    - [amount] [unit] - [ingredient]

    The recipe should include:
    1. A clear and descriptive title.
    2. A detailed list of ingredients, including quantities and measurements.
    3. Step-by-step preparation instructions:
    - Each step should be clearly numbered.
    - Include optional tips or variations where relevant.
    4. A "Shopping Cart" section listing any missing or additional ingredients required in this format:
    - [amount] [unit] - [ingredient]

    Ensure the recipe is easy to follow, realistic for the specified servings, and includes precise ingredient quantities. 
    If adjustments are necessary for the servings, add those ingredients to the shopping cart. Provide practical and authentic suggestions.
    """
    print(prompt)

    if True:
        # Call GPT and save the response to a text file
        result = gpt.ask_chat_gpt(prompt)
        print(result)
        with open("try_my_luck_output.txt", mode="w") as file:
            file.write(result)

    else:
        # Load the response from the text file
        time.sleep(1)
        with open("try_my_luck_output.txt", mode="r") as file:
            result = file.read()
    
    # Convert Markdown to HTML
    html_string = markdown.markdown(result, extensions=['extra', 'sane_lists'])
    return html_string

def find_recipes(ingredients, meal_type, servings):
    # Prepare the prompt
    prompt = f"""
        I have basic ingredients seasonings, oil and following ingredients available:
        {ingredients}

        I want to prepare a {meal_type} for {servings} servings. Please provide a single recipe that fits these criteria. You don't need to use all the ingredients.

        The recipe should include:
        1. A clear title for the dish.
        2. A list of ingredients with their quantities.
        3. Step-by-step instructions for preparation.
        - Each step should start with a numbered heading followed by detailed explanations.
        - Use subpoints for additional details or substeps under each main step.
        4. The output must include a JSON object at the end, formatted as follows:
        \\"\\"\\"json
        {{
            "ingredients_used": [
                {{
                    "name": "ingredient_name",
                    "quantity": "amount",
                    "unit": "measurement_unit"
                }}
            ]
        }}
        \\"\\"\\"

        This JSON object should list only the ingredients used in the recipe, along with their quantities and units.
        Ensure the recipe is realistic and appropriate for {servings} servings. If the available ingredients are insufficient for {servings} servings, mention this in the recipe and suggest additional quantities or ingredients needed.

        The JSON object should appear at the end of the response and should not be referenced or mentioned elsewhere in the recipe.
        """

    print(prompt)

    if True:
        # Call GPT and save the response to a text file
        result = gpt.ask_chat_gpt(prompt)
        print(result)
        with open("recipe_output.txt", mode="w") as file:
            file.write(result)

    else:
        # Load the response from the text file
        time.sleep(1)
        with open("recipe_output.txt", mode="r") as file:
            result = file.read()

    markdown_content = result[:result.find("```json")].strip()
    
    # Convert Markdown to HTML
    html_string = markdown.markdown(markdown_content, extensions=['extra', 'sane_lists'])
    return html_string

 

@app.route("/make_recipe", methods=["POST"])
def make_recipe():
    print("Processing Make Recipe...")

    # Read the recipe output from the file
    try:
        with open("recipe_output.txt", mode="r") as file:
            result = file.read()

        # Extract the JSON block from the response
        json_start = result.find("```json") + len("```json")
        json_end = result.find("```", json_start)
        json_block = result[json_start:json_end].strip()

        # Parse the JSON block
        print("Extracted JSON Block:", json_block)
        recipe_data = json.loads(json_block)
        ingredients_used = recipe_data["ingredients_used"]

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Error extracting JSON from GPT response: {e}")
        flash("Failed to process the recipe. Please try again.", "danger")
        return redirect(url_for("home"))

    # Read the current ingredients from the CSV
    try:
        with open(CSV_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            ingredients = list(reader)
        print("Current Ingredients:", ingredients)
        print("Ingredients Used:", ingredients_used)

        # Update the ingredients list by removing the used quantities
        updated_ingredients = []
        for ingredient in ingredients:
            match = next((used for used in ingredients_used if used["name"].lower() == ingredient["Ingredient"].lower()), None)
            if match:
                # Subtract quantities if units match
                if match["unit"].lower() == ingredient["Unit"].lower():
                    remaining_quantity = float(ingredient["Quantity"]) - float(match["quantity"])
                    if remaining_quantity > 0:
                        updated_ingredients.append({
                            "Ingredient": ingredient["Ingredient"],
                            "Quantity": remaining_quantity,
                            "Unit": ingredient["Unit"]
                        })
                    # Skip if quantity is zero or less
                else:
                    updated_ingredients.append(ingredient)
            else:
                # Keep the ingredient if it's not used
                updated_ingredients.append(ingredient)

        # Write the updated ingredients back to the CSV
        with open(CSV_FILE, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Ingredient", "Quantity", "Unit"])
            writer.writeheader()
            writer.writerows(updated_ingredients)

        flash("Recipe made successfully! Ingredients updated.", "success")
        return redirect(url_for("home"))

    except Exception as e:
        print(f"Error updating ingredients: {e}")
        flash("Failed to update ingredients. Please try again.", "danger")
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
