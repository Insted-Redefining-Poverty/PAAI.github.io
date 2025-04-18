from flask import Flask, render_template, request
import json

app = Flask(__name__)

# Load the JSON data files
with open('MPI.json', 'r') as mpi_file:
    mpi_data = json.load(mpi_file)

with open('PSL.json', 'r') as comp_file:
    comp_data = json.load(comp_file)

# Define the list of attributes for comparison.
ATTRIBUTES = ["education", "electricity", "sanitation", "water", "housing", "assets"]

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    key = None

    if request.method == 'POST':
        key = request.form.get('key')
        if key:
            if key in mpi_data and key in comp_data:
                mpi_entry  = mpi_data[key]
                comp_entry = comp_data[key]

                # Build a dictionary with attribute values and both MPI/PSL descriptions.
                result = {
                    'mpi_attributes': {
                        attr: mpi_entry.get(attr, 'N/A')
                        for attr in ATTRIBUTES
                    },
                    'mpi_attribute_descriptions': {
                        attr: mpi_entry.get(attr + "_string", 'No description available')
                        for attr in ATTRIBUTES
                    },
                    'comp_attributes': {
                        attr: comp_entry.get(attr, 'N/A')
                        for attr in ATTRIBUTES
                    },
                    'comp_attribute_descriptions': {
                        attr: comp_entry.get(attr + "_description", 'No description available')
                        for attr in ATTRIBUTES
                    },
                    'mpi_description': mpi_entry.get('description', 'No description available'),
                    'comp_description': comp_entry.get('description', 'No description available'),
                    'mpi_label': mpi_entry.get('label', 'N/A')
                }
            else:
                error = f"Key {key} not found in one or both files."
        else:
            error = "Please enter a key."

    return render_template(
        "index.html",
        result=result,
        error=error,
        key=key,
        numFams=200
    )

@app.route('/update', methods=['GET'])
def update():
    # Retrieve slider values (0 means no preference)
    ed      = request.args.get('ed',      default=0, type=int)
    elec    = request.args.get('elec',    default=0, type=int)
    san     = request.args.get('san',     default=0, type=int)
    water   = request.args.get('water',   default=0, type=int)
    housing = request.args.get('housing', default=0, type=int)
    assets  = request.args.get('assets',  default=0, type=int)

    # Mapping from quality strings to numeric values.
    quality_mapping = {
        "Poor": 1,
        "Normal": 2,
        "Good": 3,
        "Vulnerable": 1,
        "Extremely Poor": 0
    }

    # Compute a match score for each MPI family.
    family_scores = []
    for key, data in mpi_data.items():
        total_diff = 0
        count = 0
        for attr, pref in [
            ('education', ed),
            ('electricity', elec),
            ('sanitation', san),
            ('water', water),
            ('housing', housing),
            ('assets', assets)
        ]:
            if pref != 0:
                family_val = data.get(attr)
                if family_val in quality_mapping:
                    total_diff += abs(pref - quality_mapping[family_val])
                    count += 1
        avg_diff = (total_diff / count) if count > 0 else 0
        family_scores.append((key, avg_diff))

    family_scores.sort(key=lambda x: x[1])

    # Build HTML table of buttons
    buttons_html = "<table>"
    for key, score in family_scores:
        buttons_html += (
            f"<tr>"
            f"  <td>"
            f"    <button "
            f"      type='button' "
            f"      class='px-4 py-2 bg-gray-200 rounded my-1 w-full text-left' "
            f"      onclick=\"document.getElementById('key').value='{key}'\">"
            f"      Family {key}"
            f"    </button>"
            f"  </td>"
            f"</tr>"
        )
    buttons_html += "</table>"

    return buttons_html

if __name__ == '__main__':
    app.run(debug=True)
