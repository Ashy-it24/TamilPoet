# Deploying TamilPoet to Render

Follow these steps to deploy your Streamlit app on Render:

## 1. Add requirements.txt
You already have a `requirements.txt` with all dependencies. Render will use this to install packages.

## 2. Set the Start Command
In your Render "Web Service" settings, set the Start Command to:
```
streamlit run app.py --server.port $PORT
```
Render sets the `$PORT` environment variable automatically.

## 3. Python Version
Render will use Python 3.11 if you add this to your `render.yaml` or as a Build Command (optional):
```
echo "python-3.11" > runtime.txt
```
Or, add a `runtime.txt` file with:
```
python-3.11
```

## 4. Expose the Correct Port
Streamlit must listen on the port provided by Render (`$PORT`). The above start command ensures this.

## 5. (Optional) render.yaml
For advanced configuration, create a `render.yaml` file.

## 6. Troubleshooting
- If you see "ModuleNotFoundError", check that all dependencies are in `requirements.txt`.
- If you see "Address already in use" or "Cannot bind to port", make sure you use `$PORT` in the start command.
- For environment variables (like OpenAI API keys), add them in the Render dashboard under "Environment".

## Example requirements.txt
```
gtts>=2.5.4
openai>=1.107.1
pandas>=2.3.2
psycopg2-binary>=2.9.10
sqlalchemy>=2.0.43
streamlit>=1.49.1
```

## 7. Deploy
- Push your code to GitHub.
- Create a new Web Service on Render, connect your repo, and follow the above steps.

Your app should now deploy successfully!
