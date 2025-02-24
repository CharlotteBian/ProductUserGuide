from fpdf import FPDF  

# Create a PDF class inheriting from FPDF  
class PDF(FPDF):  
    def header(self):  
        # Custom header if needed  
        self.set_font('Arial', 'B', 12)  
        self.cell(0, 10, 'PDF Header', ln=True, align='C')  

    def footer(self):  
        # Custom footer if needed  
        self.set_y(-15)  
        self.set_font('Arial', 'I', 8)  
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C') 