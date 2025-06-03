# GitHub Webhook Listener Documentation
## Project Overview
This project is a Flask-based application designed to listen for and process GitHub webhook events. It captures information about push events, pull requests (opened), and merges, storing them in a MongoDB database. A simple web interface displays the recent events.

**Key Features:**
*   Receives and parses GitHub webhook payloads.
*   Identifies push, pull request (opened), and merge events.
*   Stores event data (author, action, branches, timestamp) in MongoDB.
*   Provides a web interface to view recent events.

**Supported Platforms/Requirements:**
*   Python 3.6+
*   Flask
*   MongoDB
## Getting Started
### Installation
1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
    
2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**
    Create a `.env` file in the project root with the following variables:

      MONGO_URI=<your_mongodb_connection_string>
      
      MONGO_DB=<your_mongodb_database_name> # Optional, defaults to github_webhooks
    
      DEBUG=True # Optional, defaults to False
    
      FLASK_ENV=development # Optional, defaults to production
    

    Replace `<your_mongodb_connection_string>` with your MongoDB connection string.
6.  **Run the application:**
    ```bash
    python app.py
    ```
    The application will start on `http://0.0.0.0:5000`.
### Prerequisites
*   **Python:** Ensure you have Python 3.6 or higher installed.
*   **MongoDB:** You need a running MongoDB instance. You can use a local instance or a cloud-based service like MongoDB Atlas.
*   **GitHub Webhook:** Configure a webhook in your GitHub repository to send events to the `/webhook` endpoint of your application.  Set the Content type to `application/json`.
## Code Structure
```
.
├── .gitignore
├── app.py
├── config.py
├── db.py
├── requirements.txt
├── routes
│   └── webhook_routes.py
├── static
│   └── css
│       └── styles.css
└── templates
    └── index.html
```
    
*   **`.gitignore`:** Specifies intentionally untracked files that Git should ignore.
*   **`app.py`:** The main application file, initializes Flask, registers routes, and starts the server.
*   **`config.py`:** Contains configuration settings for the application (e.g., debug mode, MongoDB URI).
*   **`db.py`:** Handles the MongoDB connection and defines the `events` collection.
*   **`requirements.txt`:** Lists the Python packages required to run the application.
*   **`routes/webhook_routes.py`:** Defines the routes for handling webhook events and displaying events.
*   **`static/css/styles.css`:** Contains the CSS styles for the web interface.
*   **`templates/index.html`:** The HTML template for displaying the recent events.
## API Documentation
### Endpoints
*   **`GET /`**:
    *   Description: Renders the `index.html` template, displaying recent events.
    *   Input: None
    *   Output: HTML page displaying recent events.
*   **`POST /webhook`**:
    *   Description: Receives and processes GitHub webhook events.
    *   Input: JSON payload from GitHub webhook.
    *   Output:
        *   `{"status": "stored"}` (201 Created): If the event is successfully processed and stored.
        *   `{"status": "duplicate"}` (200 OK): If the event is a duplicate.
        *   `{"status": "ignored"}` (200 OK): If the event type is not supported.
        *   `{"error": "Bad JSON"}` (400 Bad Request): If the JSON payload is invalid.
        *   `{"error": "Empty payload"}` (400 Bad Request): If the JSON payload is empty.
    *   Example Request:
        ```json
        {
          "ref": "refs/heads/main",
          "before": "...",
          "after": "...",
          "commits": [
            {
              "id": "...",
              "message": "...",
              "timestamp": "...",
              "author": {
                "name": "...",
                "email": "..."
              }
            }
          ],
          "pusher": {
            "name": "...",
            "email": "..."
          }
        }
        ```
    *   Example Response (Success):
        ```json
        {"status": "stored"}
        ```
*   **`GET /events`**:
    *   Description: Returns a list of recent events from the database.
    *   Input: None
    *   Output: JSON array of event objects.
    *   Example Response:
        ```json
        [
          {
            "_id": "...",
            "request_id": "...",
            "author": "...",
            "action": "PUSH",
            "from_branch": null,
            "to_branch": "main",
            "timestamp": "..."
          },
          {
            "_id": "...",
            "request_id": "...",
            "author": "...",
            "action": "MERGE",
            "from_branch": "feature/new-feature",
            "to_branch": "main",
            "timestamp": "..."
          }
        ]
        ```

## FAQ
**Q: The application is not receiving webhook events.**

A:  
1.   Verify that the webhook is configured correctly in your GitHub repository.
2.   Ensure that the webhook URL is correct and points to the `/webhook` endpoint of your application.    
3.   Check the webhook's delivery logs in GitHub for any errors.
4.   Make sure the Content type is set to `application/json`.
    
**Q: I'm getting a "Bad JSON" error.**

A:
Verify that the JSON payload sent by GitHub is valid. You can use a JSON validator to check for errors.

**Q: The web interface is not displaying any events.**

A:
1.   Ensure that the MongoDB database is running and accessible.
2.   Check the application logs for any errors related to database connection or queries.
3.   Verify that the `/events` endpoint is returning data.
