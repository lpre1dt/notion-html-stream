import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Secrets aus Streamlit-Konfiguration
#NOTION_TOKEN = "secret_oIlS8Ss0JfsEfUp0AfVpNpmN1rj41AcsPbIFGwokBhm"
#DATABASE_ID = "1732268253ab80cd8829ceb924798f0e"


posts = []

def get_database_name(NOTION_TOKEN, DATABASE_ID):
    headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
    }
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("title", [])[0].get("plain_text", "Unnamed Database")
    else:
        st.error(f"Fehler beim Abrufen des Datenbanknamens: {response.status_code}")
        return "Unknown"

def get_pages(NOTION_TOKEN, DATABASE_ID):
    headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
    }
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        pages = []
        for result in data.get("results", []):
            properties = result.get("properties", {})
            title = properties.get("Name", {}).get("title", [])[0].get("plain_text", "No Title")
            date = properties.get("Date", {}).get("date", {}).get("start", "No Date")
            url = result.get("url", "")
            page_id = result.get("id", "")
            content = get_page_content(page_id, headers)
            pages.append({"title": title, "date": date, "url": url, "content": content})
        return pages
    else:
        st.error(f"Fehler beim Abrufen der Notion-Daten: {response.status_code}")
        return []

def get_page_content(page_id, headers):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        blocks = response.json().get("results", [])
        content = """<style>
            body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
            pre {
                background-color: #f6f6f6;
                padding: 10px;
                border-radius: 5px;
                font-family: 'Courier New', Courier, monospace;
                color: #eb5757;
                overflow-x: auto;
            }
            code {
                color: #eb5757;
                font-size: 0.95em;
            }
            code .uppercase {
                color: blue;
            }
            code .lowercase {
                color: black;
            }
        </style>"""
        for block in blocks:
            block_type = block.get("type")
            text_elements = block.get(block_type, {}).get("rich_text", [])
            block_content = ""
            for text_element in text_elements:
                text = text_element.get("plain_text", "")
                href = text_element.get("href")
                styled_text = ''.join([f"<span class='{'uppercase' if char.isupper() else 'lowercase'}'>{char}</span>" for char in text])
                if href:
                    block_content += f"<a href='{href}' target='_blank'>🔗 {styled_text}</a>"
                else:
                    block_content += styled_text

            if block_type == "heading_1":
                content += f"<h1>{block_content}</h1>\n"
            elif block_type == "heading_2":
                content += f"<h2>{block_content}</h2>\n"
            elif block_type == "heading_3":
                content += f"<h3>{block_content}</h3>\n"
            elif block_type == "paragraph":
                content += f"<p>{block_content}</p>\n"
            elif block_type == "bulleted_list_item":
                content += f"<ul><li>{block_content}</li></ul>\n"
            elif block_type == "numbered_list_item":
                content += f"<ol><li>{block_content}</li></ol>\n"
            elif block_type == "code":
                code_text = block.get("code", {}).get("rich_text", [])[0].get("plain_text", "")
                styled_code = ''.join([f"<span class='{'uppercase' if char.isupper() else 'lowercase'}'>{char}</span>" for char in code_text])
                content += f"<pre><code>{styled_code}</code></pre>\n"
            elif block_type == "image":
                image_url = block.get("image", {}).get("file", {}).get("url")
                if image_url:
                    content += f"<img src='{image_url}' alt='Notion Image' style='max-width:100%; margin: 10px 0;'/>\n"
            else:
                content += f"<div>{block_content}</div>\n"

        return content
    else:
        return "<p>Inhalt konnte nicht geladen werden.</p>"
def display_dataframe(posts):
    df = pd.DataFrame({
        "name": [post['title'] for post in posts],
        "date": [post['date'] for post in posts],
        "url":  [post['url'] for post in posts]
    })
    outtab =  st.dataframe(df, column_config={"name": "Page name",
                                    "date": "Publishing date",
                                    "url": "Url"}, on_select="rerun",
                                    selection_mode="multi-row")
    return outtab

st.title("Get lightweight HTMLs out of your Notion Database")
api_key_input = st.text_input("Notion API Key")
database_id_input = st.text_input("Database ID")

if "posts" not in st.session_state:
    st.session_state["posts"] = []

fetch = st.button("Fetch", icon="🔍")

if fetch:
    db_name = get_database_name(api_key_input, database_id_input)
    st.subheader(f"Database: {db_name}")
    st.session_state["posts"] = get_pages(api_key_input, database_id_input)

if st.session_state["posts"]:
    st.write("Select and download")
    outtab = display_dataframe(st.session_state["posts"])
    selection =  outtab["selection"]
    st.write(f"Selected pages: {len(selection["rows"])}")
    if len(selection["rows"]) > 0:
        for selection_row in selection["rows"]:
            selected_row = selection_row
            if len(st.session_state["posts"]) >= selected_row and selected_row is not None:
                post = st.session_state["posts"][selected_row]
                html_content = post['content']
                download_button = st.download_button(
                    label=f"📥 Download {post['title']} HTML",
                    data=html_content,
                    file_name=f"{post['title'].replace(' ', '_')}.html",
                    mime="text/html"
                )
                
  
 #   for post in st.session_state["posts"]:
#        st.markdown(f"### [{post['title']}]({post['url']})")
#        st.caption(f"🗓️ {post['date']}")
##        html_content = post['content']
#        st.download_button(
#            label="📥 Download HTML",
 #           data=html_content,
#            file_name=f"{post['title'].replace(' ', '_')}.html",
 #           mime="text/html"
 #       )
else:
    if fetch:
        st.info("No Data found")

# Hinweis: 
# 1. Secrets in Streamlit hinzufügen: 
#    notion_token = "your_secret_token"
#    database_id = "your_database_id"
# 2. App starten: `streamlit run app.py`
