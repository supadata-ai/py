from supadata.client import Supadata
supadata = Supadata(api_key="your_api_key_here")

web_content = supadata.web.scrape("https://openai.com/index/introducing-deep-research/")

with open("issue.txt", 'w+') as f:
    f.write(f"PAGE TITLE : {web_content.name}\n")

    f.write(f"PAGE CONTENT : {web_content.content}")

# print(f"Page title : {web_content.name}")
# print(f"page content : {web_content.content}")
