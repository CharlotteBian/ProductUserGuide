from pathlib import Path
from fpdf import FPDF
import requests  
import streamlit as st
import base64
import os
import json

url = "https://ngc-genai-proxy-stage.pwcinternal.com/chat/completions"  
headers = {'Authorization': 'Bearer sk-Tc05RYjXNEaHEiCGpcmVqg'}
frames_dir = "data/processed/frames/test_video_test6/frame_1140.jpg"


base64_encoded_image = base64.b64encode(frames_dir)
base64_image_string = base64_encoded_image.decode('utf-8')
transcription = "This is tom"
data = {
"messages": [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Refined Prompt for Generating a Professional, Engaging User Guide PDF Objective: Develop a two-page professional User Guide with clear instructions, balanced text-to-image ratio (one image per 1–2 paragraphs), and UK spelling. The guide should be engaging, easy to understand, and help users effectively utilise the software/product with minimal support. Instructions:Engage the user: Ask up to five key questions to tailor the guide. Ensure clarity & structure: Use concise, step-by-step instructions with relevant images. Use professional formatting: Maintain a logical flow with clear headings, subheadings, and bullet points where needed. Balance content & visuals: Include at least one relevant image per 1–2 paragraphs to enhance understanding. Maintain quality & accuracy: Apply industry best practices for user documentation, referencing key sources such as The Elements of Style and Don’t Make Me Think. Generate a well-formatted PDF: Convert the final guide into a polished PDF format for easy distribution. Success Criteria: Comprehensiveness: Covers all relevant features and use cases. Ease of Understanding: Uses plain language and a structured layout. Professional Tone: Engaging yet authoritative writing style. Visual Support: Includes well-placed, relevant images to aid comprehension. Accessibility: Easily readable and scannable for users of all skill levels. Final Output: A two-page PDF User Guide that is visually engaging, structured, and easy to follow. Ensure the document maintains a clean, professional design, using a mix of text, headings, and visuals for an optimal user experience."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/gif;base64,{str(base64_image_string)}"
                }
            }
        ]
    }
],
"model": "azure.gpt-4o"
} 
response = requests.post(url, headers=headers, json=data, verify=False)
st.info(f"Response, {response.json()}")