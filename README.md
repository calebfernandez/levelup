# Level Up - Personalized Fitness Planner

![Level Up App Demo](https://images.unsplash.com/photo-1554284126-2b94f7cb4b9b?auto=format&fit=crop&w=1200&q=80)

A full-stack web application that generates personalized diet and workout plans based on user-specific data like age, weight, and body type. The application features a complete backend API built with Flask, secure user authentication, and a persistent database to save user progress and plans.

**Live Demo:** [Link to your deployed application]

---

## About The Project

This project was built from the ground up, starting from a single static HTML file and evolving into a complete, database-driven web application. It serves as a comprehensive portfolio piece showcasing the entire development lifecycle, from front-end UI to backend business logic, API design, and database management.

The core functionality allows users to register, log in, and input their physical metrics. The application then uses this data to generate a tailored fitness plan, which can be saved to their profile for future reference.

---

## Key Features

- ✅ **Secure User Authentication:** Full signup, login, and logout functionality with password hashing.
- ✅ **Password Reset Flow:** A secure, token-based system for users to reset forgotten passwords.
- ✅ **Persistent User Data:** Saves user details (age, height, body type) and progress (weight logs) to a SQLite database.
- ✅ **Dynamic Plan Generation:** Backend logic generates unique diet and workout suggestions based on the user's body type (Ectomorph, Mesomorph, Endomorph).
- ✅ **Save & View Plans:** Users can save their favorite generated plans and view their most recent one at any time.
- ✅ **RESTful API Backend:** A complete and secure API built with Flask handles all data operations.
- ✅ **Session Management:** Robust session handling keeps users logged in across page refreshes.

---

## Tech Stack

This project utilizes a modern web development stack:

- **Backend:**
  - [Python](https://www.python.org/)
  - [Flask](https://flask.palletsprojects.com/)
  - [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) for database ORM.
  - [Flask-Migrate](https://flask-migrate.readthedocs.io/) for database schema migrations.
  - [Flask-Login](https://flask-login.readthedocs.io/) for session management.
  - [Werkzeug](https://werkzeug.palletsprojects.com/) for password hashing.
  - [ItsDangerous](https://itsdangerous.palletsprojects.com/) for generating secure tokens.
- **Database:**
  - [SQLite](https://www.sqlite.org/index.html)
- **Frontend:**
  - HTML5
  - CSS3
  - Vanilla JavaScript (ES6+)

---

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

- Python 3.8+
- pip

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/your_username/your_repository.git](https://github.com/your_username/your_repository.git)
    ```
2.  **Navigate to the project directory:**
    ```sh
    cd levelup_flask_app
    ```
3.  **Create and activate a virtual environment:**
    - Windows:
      ```sh
      python -m venv venv
      venv\Scripts\activate
      ```
    - macOS / Linux:
      ```sh
      python3 -m venv venv
      source venv/bin/activate
      ```
4.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```
5.  **Initialize and upgrade the database:**
    ```sh
    flask db upgrade
    ```
6.  **Run the application:**
    ```sh
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.

---

## API Endpoints

The application exposes a full RESTful API for all its functionalities.

| Endpoint                      | Method | Protection         | Description                                       |
| ----------------------------- | ------ | ------------------ | ------------------------------------------------- |
| `/api/signup`                 | `POST` | Public             | Creates a new user account.                       |
| `/api/login`                  | `POST` | Public             | Authenticates a user and starts a session.        |
| `/api/logout`                 | `POST` | Login Required     | Terminates the current user session.              |
| `/api/status`                 | `GET`  | Login Required     | Checks if a user is currently logged in.          |
| `/api/details`                | `GET`  | Login Required     | Retrieves the current user's details.             |
| `/api/details`                | `POST` | Login Required     | Updates the current user's details.               |
| `/api/logs`                   | `GET`  | Login Required     | Retrieves all weight logs for the current user.   |
| `/api/logs`                   | `POST` | Login Required     | Adds a new weight log for the current user.       |
| `/api/generate-plan`          | `POST` | Login Required     | Generates a new fitness plan based on body type.  |
| `/api/plans`                  | `GET`  | Login Required     | Retrieves all saved plans for the current user.   |
| `/api/plans`                  | `POST` | Login Required     | Saves a generated plan for the current user.      |
| `/api/forgot-password`        | `POST` | Public             | Requests a password reset token.                  |
| `/api/reset-password/<token>` | `POST` | Public (Token Req) | Submits a new password using a valid reset token. |

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter) - email@example.com

Project Link: [https://github.com/your_username/your_repository](https://github.com/your_username/your_repository)
