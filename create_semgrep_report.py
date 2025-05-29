import json

with open("semgrep-result.json") as f:
    data = json.load(f)

html = """
<html>
<head><title>Semgrep Report</title></head>
<body>
<h1>Semgrep 분석 결과</h1>
<table border="1" cellpadding="5" cellspacing="0">
<tr>
<th>취약점 ID</th>
<th>메시지</th>
<th>파일</th>
<th>라인</th>
</tr>
"""

for r in data.get("results", []):
    html += "<tr>"
    html += f"<td>{r.get('check_id')}</td>"
    html += f"<td>{r.get('message')}</td>"
    html += f"<td>{r.get('path')}</td>"
    html += f"<td>{r['start']['line']}</td>"
    html += "</tr>"

html += "</table></body></html>"

with open("semgrep-report.html", "w") as out:
    out.write(html)
