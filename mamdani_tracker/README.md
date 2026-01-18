# Mamdani Promise Tracker - AI-Powered Edition

This project is a sophisticated, AI-powered web application designed to track the campaign promises of fictional NYC Mayor Zohran Mamdani. It moves beyond simple keyword matching to provide **nuanced, real-world analysis** of the administration's progress, offering a frank, human perspective on the real-world impact of policy decisions.

The system leverages a powerful combination of **Perplexity Sonar** for real-time, web-grounded research and **Google Gemini** for intelligent, multi-faceted analysis. It's designed to be a living, breathing tool for political accountability, updated daily with the latest news and insights.

## Core Philosophy

This tracker is built on the idea that political accountability requires more than just checking boxes. It's about understanding the gap between **campaign rhetoric and governing reality**. We aim to answer not just "what was done?" but:

*   **What does this actually mean for New Yorkers?**
*   **Is this real progress or just political theater?**
*   **What are the real-world obstacles to implementation?**
*   **How does this compare to what was originally promised?**

We strive to minimize bias by incorporating multiple perspectives and providing a frank, conversational assessment of the administration's actions, successes, and failures.

## System Architecture

The application is built on a modern Python stack, with a powerful AI core for research and analysis.

| Component               | Technology/Service        | Purpose                                                                                                                            |
| ----------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Web Framework**       | Flask & Flask-SocketIO    | Serves the frontend dashboard and handles API requests and real-time updates.                                                      |
| **Database**            | SQLAlchemy (SQLite)       | Stores all promise data, status updates, and research logs.                                                                        |
| **Real-Time Research**  | Perplexity Sonar API      | Conducts daily, up-to-the-minute web research to find news, announcements, and analysis related to the Mamdani administration.      |
| **Intelligent Analysis**| Google Gemini API         | Analyzes research findings for relevance, substance, status changes, and real-world impact. Provides nuanced, multi-perspective views. |
| **Orchestration**       | APScheduler               | Runs the daily research jobs automatically, ensuring the tracker is always up-to-date.                                             |
| **Frontend**            | HTML, CSS, JavaScript     | Provides a clean, interactive dashboard to visualize promise status and research findings.                                         |

### How It Works

1.  **Daily Research Trigger**: An `APScheduler` job kicks off the daily research process (or it can be triggered manually).
2.  **Perplexity Research**: The `ai_research.py` module queries the web for the latest news, policy updates, and analyses related to Mayor Mamdani, his administration, and key policy areas.
3.  **Gemini Analysis**: The `ai_analyzer.py` module takes the research findings and analyzes them against each promise in the database. It assesses relevance, determines if a status change is warranted, evaluates the real-world impact, and provides a frank, conversational assessment.
4.  **Database Update**: Any relevant findings, status changes, or new analyses are committed to the SQLite database.
5.  **Real-Time Dashboard**: The Flask application serves this data to the user. `Flask-SocketIO` is used to push live updates to the dashboard whenever the daily research job finds a significant change.

## Key Features

*   **AI-Powered Daily Research**: Automatically scans the web for the latest news and analysis, ensuring the tracker is always current.
*   **Nuanced Status Tracking**: Promises are categorized with statuses like `In Progress`, `Delivered`, `Stalled`, and `Walked Back`, based on intelligent analysis, not just keywords.
*   **Real-World Impact Analysis**: The AI provides a frank assessment of what each policy decision actually means for the people of New York City.
*   **Stance Change Detection**: The system is specifically designed to identify and analyze shifts between campaign promises and governing reality.
*   **Multi-Perspective Views**: To minimize bias, the system can analyze topics from the perspective of the administration, progressive allies, moderates, conservatives, and affected communities.
*   **Interactive Dashboard**: A clean, responsive frontend to easily explore promises, view their history, and read the latest analysis.
*   **Automated & Scheduled**: Runs automatically in the background, requiring no manual intervention to stay up-to-date.

## Core Modules

*   `app.py`: The main Flask application. Handles routing, database initialization, scheduler setup, and serves the frontend.
*   `models.py`: Defines the SQLAlchemy database models for `Promise`, `PromiseUpdate`, and `ScrapeLog`.
*   `ai_research.py`: The **Perplexity Sonar** integration. Contains enhanced prompts designed to elicit nuanced, real-world analysis from a seasoned NYC political analyst persona.
*   `ai_analyzer.py`: The **Google Gemini** integration. Contains prompts that force the AI to act as a frank, straight-talking analyst, assessing substance vs. spin and providing balanced perspectives.
*   `daily_research.py`: The orchestration engine that combines the power of the `PerplexityResearcher` and `GeminiPromiseAnalyzer` to run the full daily research workflow.
*   `scraper.py` / `analyzer.py`: Legacy modules for basic web scraping and analysis, kept as a potential fallback but superseded by the AI-powered system.

## Setup and Installation

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/nickm538/nickm538.git
    cd nickm538/mamdani_tracker
    ```

2.  **Set up environment variables**:

    Create a `.env` file in the `mamdani_tracker` directory and add your API keys:

    ```
    SONAR_API_KEY="your_perplexity_sonar_api_key"
    GEMINI_API_KEY="your_google_gemini_api_key"
    SECRET_KEY="a_strong_and_random_secret_key"
    ```

3.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**:

    ```bash
    python app.py
    ```

    The application will start, initialize the database (and seed it with initial promises on the first run), and start the background scheduler. You can access the dashboard at `http://localhost:5000`.

## Final Validation

This system is designed for **real-world application** with no placeholders or mock data. Every time the research process is run (either automatically on schedule or by clicking the "Scan Now" button), it performs a full, comprehensive analysis using live API calls to Perplexity and Gemini. The results are stored and displayed immediately, providing a sleek, intuitive, and up-to-date interface for tracking political accountability.
