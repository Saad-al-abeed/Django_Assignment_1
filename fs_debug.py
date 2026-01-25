
import os
import stat
import pwd
import grp

file_path = '/home/saad/Django_Assignment_1/events/templates/events/event_list.html'
log_file = '/home/saad/Django_Assignment_1/fs_debug.log'

def log(msg):
    print(msg)
    with open(log_file, 'a') as f:
        f.write(str(msg) + "\n")

# Clear log
with open(log_file, 'w') as f:
    f.write("Starting FS debug...\n")

try:
    if os.path.exists(file_path):
        st = os.stat(file_path)
        try:
            user = pwd.getpwuid(st.st_uid).pw_name
        except:
            user = str(st.st_uid)
        try:
            group = grp.getgrgid(st.st_gid).gr_name
        except:
            group = str(st.st_gid)
            
        log(f"File exists. Owner: {user}, Group: {group}, Mode: {oct(st.st_mode)}")
        
        # Try to delete
        try:
            os.remove(file_path)
            log("File deleted successfully via os.remove")
        except Exception as e:
            log(f"Failed to delete file: {e}")
    else:
        log("File does not exist initially!")

    # Try to write correct content
    correct_content = """{% extends 'base.html' %}

{% block content %}
<div class="mb-6 flex justify-between items-center">
    <h2 class="text-3xl font-bold">All Events (FIXED)</h2>
    <a href="{% url 'event_create' %}" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
        + Create Event
    </a>
</div>

<!-- Search and Filter -->
<div class="bg-white p-4 rounded shadow mb-6">
    <form method="GET" class="flex flex-wrap gap-4 items-end">
        <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input type="text" name="search" value="{{ request.GET.search }}"
                placeholder="Search by name or location..."
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2">
        </div>

        <div class="w-48">
            <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select name="category" class="w-full rounded-md border-gray-300 shadow-sm border p-2">
                <option value="">All Categories</option>
                {% for cat in categories %}
                <option value="{{ cat.id }}" {% if request.GET.category|add:"0" == cat.id %}selected{% endif %}>{{
                    cat.name }}</option>
                {% endfor %}
            </select>
        </div>

        <div class="w-40">
            <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input type="date" name="start_date" value="{{ request.GET.start_date }}"
                class="w-full rounded-md border-gray-300 shadow-sm border p-2">
        </div>

        <div class="w-40">
            <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input type="date" name="end_date" value="{{ request.GET.end_date }}"
                class="w-full rounded-md border-gray-300 shadow-sm border p-2">
        </div>

        <button type="submit" class="bg-gray-800 hover:bg-gray-900 text-white font-medium py-2 px-6 rounded">
            Filter
        </button>
        <a href="{% url 'event_list' %}" class="text-gray-600 hover:text-gray-900 font-medium py-2 px-4">Clear</a>
    </form>
</div>

{% include "events/includes/event_table.html" %}

{% endblock %}
"""
    with open(file_path, 'w') as f:
        f.write(correct_content)
    log("File written successfully.")
    
    # Read back
    with open(file_path, 'r') as f:
        read_back = f.read()
        if '(FIXED)' in read_back:
            log("Verification: SUCCESS (FIXED marker found)")
        else:
            log("Verification: FAILED (FIXED marker missing)")
            
except Exception as e:
    log(f"Fatal error: {e}")

