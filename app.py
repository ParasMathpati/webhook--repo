from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# MongoDB connection (same logic)
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.github_events
collection = db.events


# ---------- Format function (unchanged logic, not strictly needed for UI but kept) ----------
def format_event(e):
    ts = datetime.fromisoformat(e["timestamp"])
    time_str = ts.strftime("%d %b %Y %I:%M %p")

    if e["action"] == "PUSH":
        return f'{e["author"]} pushed to {e["to_branch"]} on {time_str}'
    elif e["action"] == "PULL_REQUEST":
        return f'{e["author"]} opened a pull request from {e["from_branch"]} to {e["to_branch"]} on {time_str}'
    elif e["action"] == "MERGE":
        return f'{e["author"]} merged {e["from_branch"]} to {e["to_branch"]} on {time_str}'
    else:
        return "Unknown event"


# ---------- Beautiful UI Page (only UI changed) ----------
@app.route("/")
def home():
    # same DB query logic
    events = list(collection.find({}, {"_id": 0}).sort("timestamp", -1))

    # calculate stats (read-only, does not change backend logic)
    pushes = sum(1 for e in events if e["action"] == "PUSH")
    prs = sum(1 for e in events if e["action"] == "PULL_REQUEST")
    merges = sum(1 for e in events if e["action"] == "MERGE")

    html = """
<!DOCTYPE html>
<html>
<head>
    <title>GitHub Activity Dashboard</title>
    <meta http-equiv="refresh" content="15">
    <script src="https://cdn.tailwindcss.com"></script>

    <style>
        body.dark {
            background:#0d1117;
            color:#e5e7eb;
        }
        body.light {
            background:#f3f4f6;
            color:#111827;
        }

        .card {
            background:#161b22;
            border:1px solid #374151;
        }
        body.light .card{
            background:#ffffff;
            border:1px solid #d1d5db;
        }

        .muted { color:#9ca3af; }
        body.light .muted{ color:#4b5563; }

        .idbox{
            background:#0d1117;
            border:1px solid #374151;
        }
        body.light .idbox{
            background:#f3f4f6;
            border:1px solid #d1d5db;
        }

        .title{ color:white; }
        body.light .title{ color:#111827; }
    </style>
</head>

<body id="body" class="dark min-h-screen p-6 md:p-10 font-sans">

<!-- Header -->
<div class="max-w-4xl mx-auto mb-8 flex justify-between items-start">
    <div>
        <h1 class="text-3xl md:text-4xl font-bold title flex items-center gap-3">
            🐙 Recent GitHub Activity
        </h1>
        <p class="muted mt-2">Live updates from your GitHub webhook (auto refresh every 15s)</p>
    </div>

    <button onclick="toggleTheme()"
        class="px-4 py-2 rounded-lg border text-sm font-semibold
               border-gray-500 hover:bg-gray-700 hover:text-white transition">
        Toggle Dark / Light
    </button>
</div>

<!-- Stats -->
<div class="max-w-4xl mx-auto grid grid-cols-3 gap-4 mb-8">
    <div class="card p-4 rounded-xl text-center">
        <div class="text-blue-400 text-2xl font-bold">{{ pushes }}</div>
        <div class="text-xs uppercase tracking-wider muted">Pushes</div>
    </div>
    <div class="card p-4 rounded-xl text-center">
        <div class="text-purple-400 text-2xl font-bold">{{ prs }}</div>
        <div class="text-xs uppercase tracking-wider muted">Pull Requests</div>
    </div>
    <div class="card p-4 rounded-xl text-center">
        <div class="text-green-400 text-2xl font-bold">{{ merges }}</div>
        <div class="text-xs uppercase tracking-wider muted">Merges</div>
    </div>
</div>

<!-- Activity Feed -->
<div class="max-w-4xl mx-auto space-y-4">

{% if events|length == 0 %}
<div class="card p-10 rounded-xl text-center muted">
    No events yet. Push or create a PR to see activity.
</div>
{% endif %}

{% for e in events %}
<div class="card p-5 rounded-xl hover:shadow-xl transition">

    <div class="flex justify-between items-start gap-4">
        <div class="text-base md:text-lg font-semibold leading-relaxed title">

            {% if e.action == "PUSH" %}
                {{ e.author }} pushed to
                <span class="bg-blue-500/10 text-blue-400 px-2 py-1 rounded font-mono">"{{ e.to_branch }}"</span>

            {% elif e.action == "PULL_REQUEST" %}
                {{ e.author }} opened PR from
                <span class="bg-purple-500/10 text-purple-400 px-2 py-1 rounded font-mono">"{{ e.from_branch }}"</span>
                to
                <span class="bg-purple-500/10 text-purple-400 px-2 py-1 rounded font-mono">"{{ e.to_branch }}"</span>

            {% elif e.action == "MERGE" %}
                {{ e.author }} merged
                <span class="bg-green-500/10 text-green-400 px-2 py-1 rounded font-mono">"{{ e.from_branch }}"</span>
                into
                <span class="bg-green-500/10 text-green-400 px-2 py-1 rounded font-mono">"{{ e.to_branch }}"</span>
            {% endif %}
        </div>

        <div class="text-[10px] px-2 py-1 rounded border uppercase tracking-wider font-bold
            {% if e.action == 'PUSH' %} border-blue-500/30 text-blue-400 bg-blue-500/10
            {% elif e.action == 'PULL_REQUEST' %} border-purple-500/30 text-purple-400 bg-purple-500/10
            {% elif e.action == 'MERGE' %} border-green-500/30 text-green-400 bg-green-500/10
            {% endif %}">
            {{ e.action }}
        </div>
    </div>

    <div class="mt-3 flex flex-wrap gap-4 text-sm muted">
        <div>🕒 {{ e.timestamp }}</div>
        <div class="font-mono text-xs px-2 py-1 rounded idbox">
            ID: {{ e.request_id }}
        </div>
    </div>

</div>
{% endfor %}
</div>

<!-- Footer -->
<div class="max-w-4xl mx-auto mt-10 text-center">
    <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full
                border border-green-500/30 text-green-400 text-xs uppercase tracking-widest bg-green-500/5">
        ● Live Monitoring Active
    </div>
</div>

<script>
function toggleTheme(){
    const body = document.getElementById("body");
    body.classList.toggle("light");
    body.classList.toggle("dark");
}
</script>

</body>
</html>
"""


    return render_template_string(
        html,
        events=events,
        pushes=pushes,
        prs=prs,
        merges=merges
    )


# ---------- Webhook Receiver (UNCHANGED LOGIC) ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    headers = request.headers
    event_type = headers.get("X-GitHub-Event")

    doc = {}

    if event_type == "push":
        doc = {
            "action": "PUSH",
            "author": data["pusher"]["name"],
            "from_branch": None,
            "to_branch": data["ref"].split("/")[-1],
            "request_id": data["after"],
            "timestamp": datetime.utcnow().isoformat()
        }

    elif event_type == "pull_request" and data["action"] == "opened":
        doc = {
            "action": "PULL_REQUEST",
            "author": data["pull_request"]["user"]["login"],
            "from_branch": data["pull_request"]["head"]["ref"],
            "to_branch": data["pull_request"]["base"]["ref"],
            "request_id": str(data["pull_request"]["id"]),
            "timestamp": datetime.utcnow().isoformat()
        }

    elif event_type == "pull_request" and data["action"] == "closed" and data["pull_request"]["merged"]:
        doc = {
            "action": "MERGE",
            "author": data["pull_request"]["user"]["login"],
            "from_branch": data["pull_request"]["head"]["ref"],
            "to_branch": data["pull_request"]["base"]["ref"],
            "request_id": str(data["pull_request"]["id"]),
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        return jsonify({"status": "ignored"}), 200

    collection.insert_one(doc)
    return jsonify({"status": "stored"}), 200


# ---------- Raw API (UNCHANGED) ----------
@app.route("/events", methods=["GET"])
def get_events():
    events = list(collection.find({}, {"_id": 0}))
    return jsonify(events)


if __name__ == "__main__":
    app.run(debug=True)
