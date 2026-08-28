import os
from fpdf import FPDF
from datetime import datetime

class PDFGenerator(FPDF):
    def header(self):
        # Header with branding
        self.set_font("helvetica", "B", 16)
        self.set_text_color(0, 210, 255) # Electric Blue
        self.cell(0, 10, "HARMIX AI - Performance Engineering Report", border=False, ln=1, align="C")
        self.ln(5)

    def footer(self):
        # Footer with page numbers
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    @staticmethod
    def generate_report(apis, warnings, ai_summary, output_path):
        pdf = PDFGenerator()
        pdf.add_page()
        
        # 1. Executive Summary (AI)
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "1. Executive Summary (AI Analysis)", ln=1)
        
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, ai_summary if ai_summary else "No AI analysis provided.")
        pdf.ln(10)
        
        # 2. API Inventory Table
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "2. API Inventory & Health", ln=1)
        
        # Table Header
        pdf.set_font("helvetica", "B", 10)
        pdf.set_fill_color(0, 210, 255) # Electric Blue Header
        pdf.set_text_color(255, 255, 255)
        pdf.cell(70, 8, "Endpoint", border=1, fill=True)
        pdf.cell(20, 8, "Method", border=1, fill=True)
        pdf.cell(20, 8, "Status", border=1, fill=True)
        pdf.cell(25, 8, "Time (ms)", border=1, fill=True)
        pdf.cell(55, 8, "Auth Detected", border=1, fill=True, ln=1)
        
        # Table Rows
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(0, 0, 0)
        for api in apis:
            # Truncate strings to prevent table overflow
            endpoint = api.get('endpoint', '')[:35]
            auth = api.get('auth_detected', 'None')[:25]
            
            pdf.cell(70, 8, endpoint, border=1)
            pdf.cell(20, 8, api.get('method', ''), border=1)
            pdf.cell(20, 8, str(api.get('status_code', '')), border=1)
            pdf.cell(25, 8, str(api.get('response_time', '')), border=1)
            pdf.cell(55, 8, auth, border=1, ln=1)
            
        pdf.ln(10)
        
        # 3. Rule Violations & Warnings
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "3. Rule Engine Warnings", ln=1)
        
        pdf.set_font("helvetica", "", 10)
        if not warnings:
            pdf.cell(0, 8, "No warnings detected. Test plan is optimal.", ln=1)
        else:
            for w in warnings:
                if w['level'] == 'Critical':
                    pdf.set_text_color(220, 53, 69) # Red
                elif w['level'] == 'Warning':
                    pdf.set_text_color(255, 193, 7) # Orange/Yellow
                else:
                    pdf.set_text_color(23, 162, 184) # Info Blue
                    
                pdf.cell(0, 6, f"[{w['level']}] {w['message']}", ln=1)
                
        # Save output
        pdf.output(output_path)
        return output_path