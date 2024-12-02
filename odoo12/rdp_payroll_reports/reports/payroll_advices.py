from odoo import models
import datetime
from datetime import datetime
from datetime import date
# from datetime import strftime

class PayrollAdviceXLSX(models.AbstractModel):
    _name = 'report.rdp_payroll_reports.payment_advices_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        format1 = workbook.add_format({'font_size':12,'align':'center','valign': 'vcenter','text_wrap':True})
        format2 = workbook.add_format({'font_size':12,'valign': 'vcenter'   })
        date_style = workbook.add_format({'text_wrap': True, 'num_format': 'dd/mm/yyyy'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        sheet = workbook.add_worksheet('RDP'+ ' - ' + str(lines.date) + ' - ' + 'Salary')
        row = 0
        row_count = 1
        col_name = 65
        # A =0
        # B =0
        # C =0
        # D =0
        # E =0
        # F =0
        # G =0
        # H =0
        for line in lines.line_ids:
            # string_detail = 'N,,' + str(line.name) +','+ str(line.bysal) +','+ str(line.employee_id.name) +',,,,,,,,,'+ 'RDP SALALY' +',,,,,,,,,'+ str(lines.date) +',,'+ str(line.ifsc_code) +',,,'+ str(line.employee_id.work_email)
            string_detail = '='
            # =A4&",,"&B4&","&CJ34&","&D4&",,,,,,,,,"&E4&",,,,,,,,,"&F4&",,"&G4&",,,"&H4
            sheet.set_column(0,0,28)
            sheet.write(0,0,'Transaction Type mention as N', format1)
            val_a = sheet.write(row +1,0,'N',format2)
            string_detail += str(chr(65)) + str(row_count+1) +'&",,"&'

            sheet.set_column(1,1,18)
            sheet.write(0,1,'Account Number', format1)
            val_b = sheet.write(row +1,1,line.name,format2)
            string_detail += str(chr(66)) + str(row_count+1) +'&","&'

            sheet.set_column(2,2,12)
            sheet.write(0,2,'Amount', format1)
            val_c = sheet.write(row +1,2,line.bysal,format2)
            string_detail += str(chr(67)) + str(row_count+1) +'&","&'

            sheet.set_column(3,3,25)
            sheet.write(0,3,'Ben Name', format1)
            val_d = sheet.write(row +1 ,3,line.employee_id.name,format2)
            string_detail += str(chr(68)) + str(row_count+1) +'&",,,,,,,,,"&'

            sheet.set_column(4,4,26)
            sheet.write(0,4,'Narration Max 20 Characters', format1)
            val_f = sheet.write(row +1 ,4,'RDP SALARY',format2)
            string_detail += str(chr(69)) + str(row_count+1) +'&",,,,,,,,,"&'

            sheet.set_column(5,5,28)
            sheet.write(0,5,'Transaction date DD/MM/YYYY', format1,)
            date_obj = datetime.strftime(lines.date,"%d/%m/%Y")
            sheet.write(row +1,5,str(date_obj))
            string_detail += str(chr(70)) + str(row_count+1)+'&",,"&'

            sheet.set_column(6,6,15)
            sheet.write(0,6,'IFSC Code', format1)
            val_h = sheet.write(row +1, 6,line.ifsc_code,format2)
            string_detail += str(chr(71))+ str(row_count+1) +'&",,,"&'

            sheet.set_column(7,7,30)
            sheet.write(0,7,'Email id(Optional)', format1)
            # =========Dayan ====30-11-2022=========
            # val_i = sheet.write(row +1 ,7,line.employee_id.work_email,format2)
            # val_i = sheet.write(row +1 ,7,line.employee_id.x_studio_personal_email,format2)
            val_i = sheet.write(row +1 ,7,line.employee_id.personal_email,format2)
            string_detail += str(chr(72))+ str(row_count+1)

            sheet.set_column(9,9,120)
            sheet.write(0,9,'Copy the data from Below and paste it in Notepad,save it and upload to Enet', format1)
            sheet.write_formula(row +1,9,string_detail,format2)
            # sheet.write(row +1,9,'=A4&",,"&B4&","&CJ34&","&D4&",,,,,,,,,"&E4&",,,,,,,,,"&F4&",,"&G4&",,,"&H4',format2)
            # sheet.write(row +1,9,'='+str(row +1) + str(0) +'&",,"&'+ str(row +1) + str(7),format2)
            # =10&",,"&17
            # sheet.write(row +1,9,'=concat(B0,B3)',format2)
            row += 1
            row_count += 1

            # A = 'N' or ','
            # B = str(line.name) or ','
            # C = str(line.bysal) or ','
            # D = str(line.employee_id.name) or ','
            # E = 'RDP SALARY' or ''
            # F = str(lines.date) or ','
            # G = str(line.ifsc_code) or ','
            # H = str(line.employee_id.work_email) or ','
            # H = str(line.employee_id.x_studio_personal_email) or ','
            # val = str(A +",, "+ B  +", "+ C +", "+  D +",,,,,,,,, "+ E +",,,,,,,,, "+ F +",, "+  G +",,, "+ H)
            # sheet.write(row +1,9,val,format2)
            # sheet.write(row +1,9,'=A + 1&",,"&B +1&","&C +1&","&D+1&",,,,,,,,,"&E+1&",,,,,,,,,"&F+1&",,"&G+1&",,,"&H+1',format2)
            
            # A +=1
            # B +=1
            # C +=1
            # D +=1
            # E +=1
            # F +=1
            # G +=1
            # H +=1

            


# =A2&",,"&B2&","&C2&","&D2&",,,,,,,,,"&E2&",,,,,,,,,"&F2&",,"&G2&",,,"&H2

            # ====================end================
        # row = 1
        # # count = 1
        # for line in lines.line_ids:
        #     
        #     sheet.write(row +1,1,line.name,format2)
        #     
        #     
        #     sheet.write(row +1,4,line.debit_credit,format2)
        #     # count += 1
        #     row += 1
     

    