# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn, options
from firebase_functions.options import set_global_options
from firebase_admin import initialize_app
import os
import random
import re
import io

# For cost control, you can set the maximum number of containers that can be
# running at the same time. This helps mitigate the impact of unexpected
# traffic spikes by instead downgrading performance. This limit is a per-function
# limit. You can override the limit for each function using the max_instances
# parameter in the decorator, e.g. @https_fn.on_request(max_instances=5).
set_global_options(max_instances=10)


initialize_app()

# --- Configuration (Same lists as before) ---
ADJECTIVES = ["happy", "brave", "clever", "calm", "eager", "fancy", "jolly", "kind", "lively", "proud", "silly", "witty", "gentle", "fierce", "silent", "rapid", "polite", "grumpy", "sleepy", "wise", "swift", "mighty"]
ANIMALS = ["giraffes", "penguins", "badgers", "falcons", "koalas", "pandas", "tigers", "wolves", "eagles", "bears", "foxes", "whales", "dolphins", "sharks", "lions", "zebras", "rabbits", "hawks", "otters", "lemurs", "jaguars", "panthers", "dragons"]

def generate_random_filename():
    return f"test_for_{random.choice(ADJECTIVES)}_{random.choice(ANIMALS)}.py"

def get_category_from_filename(filename):
    base = os.path.splitext(filename)[0] 
    parts = base.split('_')
    return parts[-1] if len(parts) >= 2 else "unknown"

def select_files_balanced(base_path, folder_name, n_needed):
    """
    base_path: The directory where the function is running
    folder_name: e.g., 'gto_1'
    """
    folder_path = os.path.join(base_path, folder_name)
    
    if not os.path.exists(folder_path):
        return []

    all_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
    
    if len(all_files) < n_needed:
        n_needed = len(all_files)

    category_buckets = {}
    for f in all_files:
        cat = get_category_from_filename(f)
        if cat not in category_buckets:
            category_buckets[cat] = []
        category_buckets[cat].append(f)

    for cat in category_buckets:
        random.shuffle(category_buckets[cat])

    selected_files = []
    categories = list(category_buckets.keys())
    random.shuffle(categories)
    
    while len(selected_files) < n_needed:
        for cat in categories:
            if len(selected_files) >= n_needed:
                break
            if category_buckets[cat]:
                selected_files.append(category_buckets[cat].pop())
                
    return selected_files

# We allow CORS so your website can talk to this function
@https_fn.on_request(cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
def generate_test_file(req: https_fn.Request) -> https_fn.Response:
    
    # 1. Setup paths
    # In Cloud Functions, files are located in the current working directory
    base_path = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_path, "template.txt")

    # 2. Parse Template
    header_lines = []
    requirements = [] 
    after_block_lines = []
    reading_after_block = False

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if stripped == ">> AFTER":
                    reading_after_block = True
                    continue
                elif stripped == ">> ENDAFTER":
                    reading_after_block = False
                    continue
                
                if reading_after_block:
                    after_block_lines.append(line)
                    continue

                match = re.match(r"^>>\s*(\d+)\s*x\s*(gto_\d+)", stripped, re.IGNORECASE)
                if match:
                    requirements.append((int(match.group(1)), match.group(2)))
                else:
                    header_lines.append(line)
    except FileNotFoundError:
        return https_fn.Response("Server Error: Template not found.", status=500)

    # 3. Generate Content in Memory
    output_buffer = io.StringIO()
    exercise_counter = 1

    output_buffer.writelines(header_lines)
    output_buffer.write("\n\n# " + ("="*30) + "\n")

    for count, folder in requirements:
        try:
            points = folder.split('_')[1]
        except IndexError:
            points = "?"

        # Note: We pass base_path to help find the folders
        selected_filenames = select_files_balanced(base_path, folder, count)
        
        for fname in selected_filenames:
            file_path = os.path.join(base_path, folder, fname)
            
            output_buffer.write(f"# Exercise {exercise_counter} - {points} points\n")
            output_buffer.write("#" + "-" * 30 + "\n\n")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as ex_file:
                    content = ex_file.read()
                    output_buffer.write(content)
                    if not content.endswith('\n'):
                        output_buffer.write("\n")
            except Exception as e:
                output_buffer.write(f"# Error reading file {fname}\n")
            
            if after_block_lines:
                output_buffer.write("\n")
                output_buffer.writelines(after_block_lines)

            output_buffer.write("\n\n# " + ("-"*30) + "\n")
            exercise_counter += 1

    # 4. Prepare Response
    filename = generate_random_filename()
    final_content = output_buffer.getvalue()
    output_buffer.close()

    # Return JSON
    return https_fn.Response(
        response=final_content,
        headers={
            "Content-Type": "text/plain",
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )