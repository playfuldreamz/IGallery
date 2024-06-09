# iGallery: Repost Your Saved Instagram Pictures

**Tired of limitations when trying to repost saved Instagram pics?** Instagram's API doesn't directly support reposting saved media. iGallery offers a workaround! This Django web app lets you view your saved Instagram pictures and provides a way to download them, making it easy to repost them as you wish.

## ✨ Features

- **Instagram Authentication:** Securely log in with your Instagram account.
- **View Saved Pictures:** Browse through all the pictures you've saved on Instagram.
- **Download for Reposting:**  Download your saved pictures locally. Repost them using Instagram's regular posting features—no more restrictions!

## 🚀 Getting Started

### Prerequisites

- **Python 3.7+** (check with `python --version`)
- **pip** (usually comes with Python - check with `pip --version`)
- **Git** (optional for cloning the repo - check with `git --version`)

### Setup

1. **Clone the Repository (Optional):**
   ```bash
   git clone https://github.com/your-username/igallery.git
   cd igallery
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Instagram App Credentials:**
   - Create an Instagram [developer account](https://developers.facebook.com/apps/).
   - Register a new app, selecting "Consumer" as the app type.
   - In your app settings, set the following:
     - **Valid OAuth Redirect URIs:** `https://localhost:8000/instagram/callback/` (adjust the port if needed).
   - Obtain your app's **Client ID** and **Client Secret**. 
   - **Create a `.env` file in your project root:**
     ```
     INSTAGRAM_CLIENT_ID=your_client_id
     INSTAGRAM_CLIENT_SECRET=your_client_secret
     DJANGO_SECRET_KEY=your_django_secret_key
     ```

5. **Apply Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Run the Development Server:**
   ```bash
   python manage.py runserver 
   ```

7. **Access the App:**
   - Open your web browser and go to `http://127.0.0.1:8000/` (or your specified port).

## 🔐 Security

- We strongly recommend **NOT** hardcoding sensitive information directly into the code.
- Use a robust production server and deployment strategy for live environments.
- Consider using HTTPS for all communication.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have any ideas or improvements.

## 📄 License

This project is licensed under the MIT License.
