# P.A.P.I. 3.0 (Programmable Artificial Personal Intelligence)

**PAPI 3.0** is an advanced personal AI interface built with Python and Streamlit. It serves as a central command hub capable of simulating app execution, voice interaction, and integrated security protocols.

## 🚀 Features

* **Voice-Enabled Interface:** Uses `gTTS` (Google Text-to-Speech) to provide audible feedback for all responses.
* **App Execution Simulation:** Visualizes the launching of internal modules (e.g., *Aegis Guard*, *Audio Workbench*, *Stock Market Data*) directly within the main dashboard.
* **Natural Language Processing:** Utilizes `TextBlob` for basic sentiment analysis and command parsing.
* **Secure Environment:** Designed with placeholders for high-level security verification and parental control locks.

## 📂 Project Structure

This repository contains the minimal deployment files required for cloud hosting (Render/Heroku):

* `app.py` - The main application source code.
* `requirements.txt` - List of Python dependencies (Streamlit, gTTS, TextBlob).
* `.gitignore` - Configuration to exclude unnecessary system files.

## 🛠️ Installation & Local Run

To run PAPI 3.0 on your local machine:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/papi-3-0.git](https://github.com/your-username/papi-3-0.git)
    cd papi-3-0
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## ☁️ Deployment (Render)

This app is optimized for deployment on [Render](https://render.com).

**Configuration Settings:**
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
* **Environment Variables:** Ensure `PYTHON_VERSION` matches your local environment (e.g., `3.9.13` or `3.11.0`).

## 🛡️ Modules

* **Aegis Guard:** Security and threat monitoring.
* **Audio Processor Workbench:** Advanced audio control interface.
* **PAPI Pro:** Enhanced life coaching and organizational tools.

---
*Developed by Troy Walker*