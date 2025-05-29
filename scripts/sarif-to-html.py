#!/usr/bin/env python3
import json

with open('result.sarif', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data.get('runs', [])[0].get('results', [])
rules = {r['id']: r for r in data.get('runs', [])[0].get('tool', {}).get('driver', {}).get('rules', [])}

print("<html><head><meta charset='utf-8'><title>CodeQL Report</title></head><body>")
print(f"<h1>CodeQL 취약점 리포트 (총 {len(results)}건)</h1>")
print("<table border='1' cellspacing='0' cellpadding='5'>")
print("<tr><th>#</th><th>파일</th><th>라인</th><th>규칙</th><th>설명</th></tr>")

for idx, result in enumerate(results, 1):
    rule_id = result.get('ruleId', 'unknown')
    message = result.get('message', {}).get('text', '')
    locations = result.get('locations', [])
    file_path = line = 'N/A'
    if locations:
        physical_location = locations[0]['physicalLocation']
        file_path = physical_location['artifactLocation'].get('uri', 'unknown')
        line = physical_location['region'].get('startLine', '?')

    rule = rules.get(rule_id, {})
    desc = rule.get('fullDescription', {}).get('text', '')

    print(f"<tr><td>{idx}</td><td>{file_path}</td><td>{line}</td><td>{rule_id}</td><td>{desc or message}</td></tr>")

print("</table></body></html>")
