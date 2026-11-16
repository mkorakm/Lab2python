
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
<style>
    body { font-family: sans-serif; }
    table { border-collapse: collapse; width: 100%; max-width: 800px; margin-top: 15px; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
    th { background-color: #f4f4f4; }
    .passed { color: green; font-size: 1.2em; }
    .failed { color: red; font-size: 1.2em; }
    .empty-grade { color: #aaa; }
</style>
</head>
<body>

<h1>Список студентов</h1>

<table>
  <tr>
    <th>id</th>
    <th>Имя</th>
    {% for i in range(1, max_grades + 1) %}
    <th>Оценка {{ i }}</th>
    {% endfor %}
    <th>Средний</th>
    <th>Статус</th>
  </tr>
  {% for s in students %}
  <tr>
    <td>{{ s.id }}</td>
    <td style="text-align: left;">{{ s.name }}</td>

    {# Выводим оценки, дорисовывая прочерки, если оценок меньше максимума #}
    {% for i in range(max_grades) %}
      <td>
        {% if i < s.grades|length and s.grades[i] is not none %}
          {{ s.grades[i] }}
        {% else %}
          <span class="empty-grade">-</span>
        {% endif %}
      </td>
    {% endfor %}

    <td>{{ '%.2f'|format(s.average) }}</td>

    {# Статус: галочка или крестик #}
    <td>
      {% if s.is_passed %}
        <span class="passed">✔</span>
      {% else %}
        <span class="failed">✘</span>
      {% endif %}
    </td>
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
            // Проверяем, изменилось ли содержимое, чтобы не сбрасывать скролл
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

    def __init__(self, sid, name, grades):
        self.id = sid
        self.name = name
        self.grades = grades

    @property
    def average(self):
        valid = [g for g in self.grades if g is not None]
        return sum(valid) / len(valid) if valid else 0.0

    @property
    def is_passed(self):
        if not self.grades:
            return False
        if any(g is None for g in self.grades):
            return False
        return self.average >= 75

def load_session():
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

    max_grades = max((len(s.grades) for s in students), default=0)

    return render_template_string(PAGE, students=students, max_grades=max_grades)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)