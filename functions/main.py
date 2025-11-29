import os
import random
import re
import io
import uuid
import datetime
import subprocess
import sys
from firebase_functions import https_fn, options
from firebase_admin import initialize_app, firestore

# Initialize Firebase App and Firestore
initialize_app()

_db_client = None

def get_db():
    """
    Returns the Firestore client, initializing it only if necessary.
    """
    global _db_client
    if _db_client is None:
        _db_client = firestore.client()
    return _db_client

# --- Configuration ---
# (We no longer need the Animal lists since we use the Student Name)

def get_category_from_filename(filename):
    base = os.path.splitext(filename)[0] 
    parts = base.split('_')
    return parts[-1] if len(parts) >= 2 else "unknown"

def select_files_balanced(base_path, folder_name, n_needed):
    """Selects files ensuring category diversity."""
    folder_path = os.path.join(base_path, folder_name)
    if not os.path.exists(folder_path): return []

    all_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
    if len(all_files) < n_needed: n_needed = len(all_files)

    category_buckets = {}
    for f in all_files:
        cat = get_category_from_filename(f)
        if cat not in category_buckets: category_buckets[cat] = []
        category_buckets[cat].append(f)

    for cat in category_buckets: random.shuffle(category_buckets[cat])

    selected_files = []
    categories = list(category_buckets.keys())
    
    while len(selected_files) < n_needed:
        random.shuffle(categories)
        for cat in categories:
            if len(selected_files) >= n_needed: break
            if category_buckets[cat]:
                selected_files.append(category_buckets[cat].pop())
                
    return selected_files

def execute_snippet(code_content):
    """
    Runs a python code snippet in a subprocess.
    Returns the output string (stdout + stderr) or specific messages for timeouts.
    """
    try:
        # Run the code with a 2-second timeout
        result = subprocess.run(
            [sys.executable, "-c", code_content],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        output = ""
        if result.stdout:
            output += f"--- STDOUT ---\n{result.stdout}\n"
        if result.stderr:
            output += f"--- ERROR/STDERR ---\n{result.stderr}\n"
        
        if not output:
            output = "(No output printed to screen)"
            
        return output.strip()

    except subprocess.TimeoutError:
        return "--- INFINITE LOOP DETECTED (Timed out after 2s) ---"
    except Exception as e:
        return f"--- SYSTEM ERROR ---\n{str(e)}"

# ==========================================
# FUNCTION 1: GENERATE TEST (User Facing)
# ==========================================
@https_fn.on_request(cors=options.CorsOptions(cors_origins="*", cors_methods=["post"]))
def generate_test_file(req: https_fn.Request) -> https_fn.Response:
    
    # 1. Parse Request Data
    try:
        data = req.get_json()
        fullname = data.get('fullname', 'Unknown_Student').replace(" ", "_")
    except:
        fullname = "Unknown_Student"

    # Generate unique ID (8 chars)
    test_id = uuid.uuid4().hex[:8].upper()
    timestamp = datetime.datetime.now().isoformat()

    # 2. Setup paths & Template
    base_path = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_path, "template.txt")

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

    # 3. Select Files & Generate Content
    output_buffer = io.StringIO()
    
    # Mandatory Header ID
    output_buffer.write(f"# ID {test_id}\n")
    output_buffer.writelines(header_lines)
    output_buffer.write("\n\n# " + ("="*30) + "\n")

    exercises_log = [] # To store in Firestore
    exercise_counter = 1

    for count, folder in requirements:
        try:
            points = folder.split('_')[1]
        except IndexError:
            points = "?"

        selected_filenames = select_files_balanced(base_path, folder, count)
        
        for fname in selected_filenames:
            # Log the selection
            file_rel_path = f"{folder}/{fname}"
            exercises_log.append(file_rel_path)
            
            # Read content
            file_path = os.path.join(base_path, folder, fname)
            out_str = f"# Exercise {exercise_counter} - {points} points\n"
            out_str += "# " + "-" * 30 + "\n\n"
            
            try:
                with open(file_path, 'r', encoding='utf-8') as ex_file:
                    content = ex_file.read()
                    out_str += content
                    if not content.endswith('\n'): out_str += "\n"
            except:
                out_str += f"# Error reading file {fname}\n"
            
            output_buffer.write(out_str)
            
            if after_block_lines:
                output_buffer.write("\n")
                output_buffer.writelines(after_block_lines)

            output_buffer.write("\n\n# " + ("-"*30) + "\n")
            exercise_counter += 1

    # 4. Save to Firestore
    doc_ref = get_db().collection("generated_tests").document(test_id)
    doc_ref.set({
        "id": test_id,
        "fullname": fullname,
        "timestamp": timestamp,
        "exercises": exercises_log
    })

    # 5. Return Response
    final_content = output_buffer.getvalue()
    output_buffer.close()
    
    filename = f"test_{fullname}.py"

    return https_fn.Response(
        response=final_content,
        headers={
            "Content-Type": "text/plain",
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


# ==========================================
# FUNCTION 2: GENERATE SOLUTION (Teacher Tool)
# ==========================================
@https_fn.on_request(cors=options.CorsOptions(cors_origins="*", cors_methods=["get"]))
def generate_solution_file(req: https_fn.Request) -> https_fn.Response:
    
    # 1. Get ID from URL parameters
    test_id = req.args.get('id')
    if not test_id:
        return https_fn.Response("Error: Missing 'id' parameter.", status=400)

    # 2. Fetch Log from Firestore
    doc_ref = get_db().collection("generated_tests").document(test_id)
    doc = doc_ref.get()

    if not doc.exists:
        return https_fn.Response("Error: Test ID not found.", status=404)
    
    data = doc.to_dict()
    fullname = data.get('fullname', 'Unknown')
    exercises_list = data.get('exercises', [])

    # 3. Generate Solution Content
    base_path = os.path.dirname(os.path.abspath(__file__))
    output_buffer = io.StringIO()

    output_buffer.write(f"# ID {test_id}\n")
    output_buffer.write(f"# SOLUTION KEY FOR: {fullname}\n")
    output_buffer.write(f"# Generated: {datetime.datetime.now()}\n")
    output_buffer.write("# " + "="*40 + "\n\n")

    for idx, rel_path in enumerate(exercises_list):
        output_buffer.write(f"--- Exercise {idx + 1} ({rel_path}) ---\n")
        
        full_path = os.path.join(base_path, rel_path)
        
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # EXECUTE THE CODE
            result_output = execute_snippet(code_content)
            output_buffer.write(result_output)
        else:
            output_buffer.write(f"ERROR: File {rel_path} not found on server.")
            
        output_buffer.write("\n\n# " + ("="*40) + "\n")

    # 4. Return Response
    final_content = output_buffer.getvalue()
    output_buffer.close()

    filename = f"SOLUTION_{fullname}.txt"

    return https_fn.Response(
        response=final_content,
        headers={
            "Content-Type": "text/plain",
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )