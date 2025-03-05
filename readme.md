python3 -m venv my-app  
source my-app/bin/activate
pip install -r requirements.txt


pip install ollama ollama-python sentence-transformers faiss-cpu numpy 
scikit-learn watchdog


pip install --upgrade streamlit

ollama run mistral

streamlit run app.py

streamlit run app.py --server.port 8501


sqlite3 chat_history.db "select * from chat_history"  