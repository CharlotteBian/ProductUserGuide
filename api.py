from pathlib import Path
from fpdf import FPDF
import requests  
import streamlit as st
import base64
import os
import json
import subprocess
import PyPDF2

from src.video.processor import VideoProcessor

st.info(f"This is for test")
  
  
# Read the image file in binary mode  
# Loop through all files in the directory 
url = "https://ngc-genai-proxy-stage.pwcinternal.com/chat/completions"  
headers = {'Authorization': 'Bearer sk-Tc05RYjXNEaHEiCGpcmVqg'}
frames_dir = "data/processed/frames/test_video_test6" 
pdf = FPDF()

entries = os.listdir(frames_dir)  
  
# Sort by modification time  
sorted_entries_by_mtime = sorted(entries, key=lambda entry: os.path.getmtime(os.path.join(frames_dir, entry)))  
i=0
image_arr = []
pdf_arr = []
imagepath_arr = []
Path("data/pdf/test_video_test6").mkdir(parents=True, exist_ok=True)
for filename in sorted_entries_by_mtime:  
    # Construct full file path 
    #st.info(f"File name, {filename}") 
    file_path = os.path.join(frames_dir, filename)  

    # Check if it is a file and has an image extension  
    if os.path.isfile(file_path) and filename.lower().endswith(('.jpg')):  
        try:  
            # Open the image file  
            #st.info(f"File path, {file_path}")
            i = i + 1
            with open(f"{file_path}", 'rb') as image_file:
             
                base64_encoded_image = base64.b64encode(image_file.read())
                base64_image_string = base64_encoded_image.decode('utf-8')
                image_arr.append(base64_image_string)
                imagepath_arr.append(file_path)
                # transcription = "Hi, this is Tom from the M&A Path team. I'm showing you how to create a project in M&A Path. Firstly, you click on the new project button, which brings up a modal. You enter the information of including project name, engagement lead and other fields. And when complete, you can click the Create button. "

                # data = {
                #     "messages": [
                #         {
                #             "role": "user",
                #             "content": [
                #                 {
                #                     "type": "text",
                #                     "text": f"Can you return code that I can use for my python fpdf package that I can pass to the package to generate a well-styled one-page pdf? M&A path will be in red color. I want the code to include an explanation of what the image represents and I want to include the image in the pdf as well and the content and image will not overlap. Content will be on top and image will be at bottom. The image path is {file_path} . I don't want any extra detail in your response.  I literally want to be able to pass your response into my fpdf package. the generated pdf name will be user_guide_{i}.pdf and file path will be data/pdf/test_video_test6/user_guide_{i}.pdf"
                #                 },
                #                 {
                #                     "type": "image_url",
                #                     "image_url": {
                #                         "url": f"data:image/gif;base64,{str(base64_image_string)}"
                #                     }
                #                 }
                #             ]
                #         }
                #     ],
                #     "model": "azure.gpt-4o"
                # } 
                # response = requests.post(url, headers=headers, json=data, verify=False)
                # data = json.loads(response.content)
                # st.info(data['choices'][0]['message']['content'])

                # code = data['choices'][0]['message']['content'].replace('python\n', '').replace('```','')

                # with open(f"data/pdf/test_video_test6/generated_code_{i}.py", "w") as file:
                #     file.write(code)
                
                
                # # Step 2: Execute the code using subprocess
                # try:
                #     subprocess.run(["venv/Scripts/python.exe", f"data/pdf/test_video_test6/generated_code_{i}.py"])
                #     pdf_arr.append(f'data/pdf/test_video_test6/user_guide_{i}.pdf')
                # except BaseException as e:  
                #     # Code that runs if the exception occurs  
                #     print(f"An error occurred: {e}")  
                
                # # Inform the user
                # print("PDF generated successfully")

                #st.info(f"Response, {response.json()}")
                # Check if the request was successful (status code 200)  
                # if response.status_code == 200:  
                #     # Parse the JSON response  
                #     data = json.loads(response.content)
                #     pdf.add_page()  

                #     # Set font  
                #     pdf.set_font("Arial", size=12)  

                #     pdf.multi_cell(0, 10, data['choices'][0]['message']['content'])
                #     current_y = pdf.get_y()  
  
                #     # Set image position to avoid overlap (below the text)  
                #     pdf.image(image_file, x=10, y=current_y + 10, w=100)
                # else:  
                #     print("Failed to retrieve data:", response.status_code)  
                # # Print image details or perform operations  
                # print(f"Processing image: {file_path}")  
                #print(f"Image size: {img.size}, Image format: {img.format}")  
            
        except Exception as e:  
            print(f"Could not open {filename}: {e}")

#Create and download PDF
# output_dir = Path("data/pdf")
# #output_dir.mkdir(parents=True, exist_ok=True)
# pdf_path = output_dir / f"pdf_user_guide.pdf"

# # Save the PDF to a file  
# pdf.output(pdf_path) 

# st.success(f"PDF created at {pdf_path}")  

# # Read the PDF file content  
# with open(pdf_path, 'rb') as file:  
#     pdf_data = file.read()  

# st.download_button(
#     label="⬇️ Download User Guide",
#     data=pdf_data,
#     file_name=f"user_guide_en.pdf",
#     mime="application/pdf"
# )

#pdf_files = ['file1.pdf', 'file2.pdf', 'file3.pdf']  

# Create a PDF writer object  
# pdf_writer = PyPDF2.PdfWriter()  

# # Loop through all the PDF files  
# for file in pdf_arr:  
#     # Open each PDF file  
#     with open(file, 'rb') as pdf_file:  
#         # Create a PDF reader object  
#         pdf_reader = PyPDF2.PdfReader(pdf_file)  

#         # Add each page to the writer object  
#         for page_num in range(len(pdf_reader.pages)):  
#             page = pdf_reader.pages[page_num]  
#             pdf_writer.add_page(page)  

# # Write the combined PDF to a new file  
# with open('data/pdf/test_video_test6/user_guide.pdf', 'wb') as output_pdf_file:  
#     pdf_writer.write(output_pdf_file)  

# print("PDF files have been combined into 'user_guide.pdf'") 

# image_contents = [{
#                     "type": "text",
#                     "text": f"Remove similar image and provide one of each duplicate image and unique images content and original image name. Don't provide any script"
#                 }]
# for image_data in image_arr:
#     image_content = {
#                 "type": "image_url",
#                 "image_url": {
#                     "url": f"data:image/gif;base64,{str(image_data)}"
#                 }
#             }
#     image_contents.append(image_content)                


# data = {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": image_contents
#             }
#         ],
#         "model": "azure.gpt-4o"
#     } 

#st.info(f"content, {data2}")
#response = requests.post(url, headers=headers, json=data, verify=False)
#data_resp = json.loads(response.content)
#st.info(data_resp['choices'][0]['message']['content'])

# with open("data/processed/frames/test_video_test6/frame_0.jpg", 'rb') as image_file:
#     base64_encoded_image = base64.b64encode(image_file.read())
#     base64_image_string = base64_encoded_image.decode('utf-8')

separator = ', '
st.info(f"{separator.join(imagepath_arr)}")
pdf_contents = [{
                    "type": "text",
                    "text": f"Remove similar image between the images The images are {separator.join(imagepath_arr)} and consider contents of one of each duplicate images and unique images and return code that I can use for my python fpdf package that I can pass to the package to generate a well-styled multi page pdf?  I want the code to include an explanation of each of the images represents and I want to include each image in the pdf as well and the content . Images and contents do not overlap. I don't want any extra detail in your response.  I literally want to be able to pass your response into my fpdf package. the generated pdf name will be user_guide.pdf and the file path will be data/pdf/test_video_test6/user_guide.pdf M&A Path text will be in red color. PDF should have a header and footer"
                }]
for image_data in image_arr:
    pdf_content = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/gif;base64,{str(image_data)}"
                }
            }
    pdf_contents.append(pdf_content)

data_pdf = {
        "messages": [
            {
                "role": "user",
                "content": pdf_contents

            }
        ],
        "model": "azure.gpt-4o"
    } 

response = requests.post(url, headers=headers, json=data_pdf, verify=False)
data_resp = json.loads(response.content)
st.info(data_resp['choices'][0]['message']['content'].replace('python\n', ''))


code = data_resp['choices'][0]['message']['content'].replace('python\n', '').replace('```','')

with open("data/pdf/test_video_test6/generated_code.py", "w") as file:
    file.write(code)
# Step 2: Execute the code using subprocess
subprocess.run(["venv/Scripts/python.exe", "data/pdf/test_video_test6/generated_code.py"])
 
#Inform the user
print("PDF generated successfully")





