from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

HTML = """
<h1>🎶 Jukebox Installer</h1>
<form method="post">
    <button name="action" value="1">Instalar</button>
    <button name="action" value="2">Reiniciar</button>
    <button name="action" value="3">Desinstalar</button>
</form>
<pre>{{ output }}</pre>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        action = request.form["action"]
        try:
            result = subprocess.run(["bash", "install.sh"], input=action.encode(), capture_output=True, text=True)
            output = result.stdout + "\n" + result.stderr
        except Exception as e:
            output = f"Erro ao executar: {e}"
    return render_template_string(HTML, output=output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)