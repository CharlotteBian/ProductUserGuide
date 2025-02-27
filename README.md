1. Install Python: Ensure Python is installed. Check with python3 --version or python --version.
    On Ubuntu, install Python with
        sudo apt update  
        sudo apt install python3 python3-pip
    On Mac, install Python with brew
        brew install python  
2. Navigate to your project directory and Use pip to install dependencies listed in your requirements.txt file:
    pip install -r requirements.txt  
3. RUN 
    python3 -m streamlit run app.py
