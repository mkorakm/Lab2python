# app.py
import json
import os

from flask import Flask, render_template_string

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(BASE_DIR, "data", "session.json")


PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Студенты</title>
</head>
<body>

<h1>Список студентов</h1>

<table border="1" cellpadding="6">
  <tr>
    <th>id</th>
    <th>Имя</th>
    <th>Оценки</th>
    <th>Средний</th>
  </tr>
  {% for s in students %}
  <tr>
    <td>{{ s.id }}</td>
    <td>{{ s.name }}</td>
    <td>{% for g in s.grades %}{{ g if g is not none else '-' }} {% endfor %}</td>
    <td>{{ '%.2f'|format(s.average) }}</td>
  </tr>
  {% endfor %}
</table>

{% if not students %}
<p>Список пуст.</p>
{% endif %}

<script>
setInterval(function () {
    fetch(window.location.href)
        .then(r => r.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newBody = doc.querySelector('body').innerHTML;
            if (document.body.innerHTML !== newBody) {
                document.body.innerHTML = newBody;
            }
        });
}, 2000);
</script>

</body>
</html>
"""


class _S:
    """Простой объект-студент для шаблона."""
    def __init__(self, sid, name, grades):
        self.id = sid
        self.name = name
        self.grades = grades

    @property
    def average(self):
        valid = [g for g in self.grades if g is not None]
        return sum(valid) / len(valid) if valid else 0.0


def load_session():
    """Читает session.json. Если файла нет — пустой список."""
    if not os.path.exists(SESSION_PATH):
        return []
    try:
        with open(SESSION_PATH, encoding="utf-8") as f:
            raw = json.load(f)
        return [_S(item["id"], item["name"], item["grades"]) for item in raw]
    except (OSError, json.JSONDecodeError, KeyError):
        return []


@app.route("/")
def index():
    students = load_session()
    return render_template_string(PAGE, students=students)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)