from flask import Flask
from flask_cors import CORS
import os
import openai

app = Flask(__name__)
CORS(app)

#Google Sheets
SHEET_ID = '1attk70G_v7pYUF6pwmDh7NK1hPRXNYEkBHo6UvklZuQ'
SHEET_NAME = 'playasguanacaste'

#OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")