🐙 GitPulse Dashboard
GitPulse is a lightweight automation tool designed to track and visualize activity across your GitHub repositories in real-time. It eliminates the need for manual monitoring by providing a centralized, live dashboard for all your repository events.

🛠 How It Works
Event Capture: The application listens for Push, Pull Request, and Merge events sent via GitHub Webhooks.

Database Storage: Every incoming event is stored in MongoDB, capturing essential details like the author, branch names, and timestamps.

Visual Analytics: The frontend features a clean analytics section that automatically calculates and displays total activity counts.

✨ Key Features
Live Webhook Receiver: Direct integration with GitHub for instant data processing.

Dynamic Dashboard: A responsive UI built with Tailwind CSS that auto-refreshes every 15 seconds.

Theme Toggle: Built-in support for both Dark and Light modes based on user preference.

Detailed Logging: Displays specific metadata for every activity, including unique Request IDs and ISO timestamps.

🚀 Tech Stack
Backend: Flask (Python), python-dotenv

Database: MongoDB

Frontend: HTML5, Tailwind CSS, Jinja2 Templating
