# supabase_utils.py

from supabase import create_client
import streamlit as st
print("✅ Supabase URL:", st.secrets["SUPABASE_URL"])

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_ANON_KEY"]
supabase = create_client(url, key)

def add_comment(name, text):
    result = supabase.table("comments").insert({"name": name, "text": text}).execute()
    return result.data[0]["id"] if result.data else None

def get_comments():
    response = supabase.table("comments").select("*").order("created_at", desc=True).limit(20).execute()
    return response.data

def update_comment(comment_id, new_text):
    supabase.table("comments").update({"text": new_text}).eq("id", comment_id).execute()

def delete_comment(comment_id):
    supabase.table("comments").delete().eq("id", comment_id).execute()
