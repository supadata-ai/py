from supadata.client import Supadata
supadata = Supadata(api_key="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6IjEifQ.eyJpc3MiOiJuYWRsZXMiLCJpYXQiOiIxNzQ5MTExNTQzIiwicHVycG9zZSI6ImFwaV9hdXRoZW50aWNhdGlvbiIsInN1YiI6IjM1NTliZGY3ZjZjNTQzNWI5YzQ1NzFlMDRjNDQ4YzUyIn0.LMdb4g6efiZalUsjh2u01cD5b57zdB7VDGfopHeeOAI")

web_content = supadata.web.scrape("https://openai.com/index/introducing-deep-research/")

with open("issue.txt", 'w+') as f:
    f.write(f"PAGE TITLE : {web_content.name}\n")

    f.write(f"PAGE CONTENT : {web_content.content}")

# print(f"Page title : {web_content.name}")
# print(f"page content : {web_content.content}")
