from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import json
from PyPDF2 import PdfWriter, PdfReader, PdfMerger

endpoint = "ENDPOINT"
key = "KEY"
# model_id = "FormType1_Version3"
model_id = "abc"

FORM_NAME = "ATAC_Test_3.pdf"


document_intelligence_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

with open(FORM_NAME, "rb") as f:
    poller = document_intelligence_client.begin_analyze_document(
        model_id, document=f
    )
result = poller.result()


coordinates=[]
nested_dict={
    "Root": {
        "Single_Ownership": [],
        "Sole_Proprietorship": [],
        "Date_Opened": [],
        "Cif_Number": [],
        "Account_Name": [],
        "Account_Number": [],
        "Account_To_Be_Opened": {
            "Atm_Savings": [],
            "Passbook_Savings": [],
            "Money_Plus_Savings": [],
            "China_Check_Plus": [],
            "Time_Deposit": [],
            "Diamond_Savings": {
                "Box": [],
                "None": [],
                "Principal_Interest": [],
                "Principal_Only": {
                    "Box": [],
                    "Value": []
                }
            },
                "Others": {
                    "Box": [],
                    "Value": []
            }
        },
        "Currency": {
            "Php": [],
            "Usd": [],
            "Eur": [],
            "Cny": [],
            "Others": {
                "Box": [],
                "Value": []
            }
        },
        "Purpose_of_Account_Opening": {
            "For_Personal_Transactions": [],
            "For_Business_Investment_Transactions": []
        },
        "Preferred_Mailing_Address": {
            "Home_Permanent": [],
            "Present": [],
            "Work_Business": [],
            "Email": []
        },
        "Do_You_Want_To_Avail_Enroll": {
            "Atm_Card": {
                "Avail_Link": [],
                "No_Need": [],
                "Atm_Card_Number": []
            },
            "Mobile_Banking": {
                "Enroll": [],
                "No_Need": []
            },
            "Online_Banking": {
                "Enroll_Link": [],
                "No_Need": [],
                "User_Id": []
            },
            "Preferred_User_Id_1": [],
            "Preferred_User_Id_2": [],
            "Preferred_User_Id_3": []
        },
        "For_Banks_Use_Only": {
            "Remarks": [],
            "Referred_By": {
                "Box": [],
                "Value": []
            },
            "Account_Opened_By": [],
            "Signature_Verified_By": [],
            "Approved_By_Date": []
        },
        "Customers_Acknowledgement_Of_Items": {
            "Atm_Card": {
                "Box": [],
                "Issued_By_Date": [],
                "Received_By_Date": []
            },
            "Atm_Pin": {
                "Box": [],
                "Issued_By_Date": [],
                "Received_By_Date": []
            },
            "Passbook": {
                "Box": [],
                "Serial_No": [],
                "Issued_By_Date": [],
                "Received_By_Date": []
            },
            "Checkbook": {
                "Box": [],
                "Series_No": [],
                "Issued_By_Date": [],
                "Received_By_Date": []
            }  
        }
    }
}


storage={}
for document in result.documents:
    for name, field in document.fields.items():
        value=field.value if field.value else field.content
        #print(f"{name}={value} [{field.confidence}]")\
        storage[name]=[value,field.confidence]
        if field.value_type=="signature":
            print(name,field)
            points=field.bounding_regions[0].polygon
            temp_list=[]
            for p in points:
                temp_list.append((p.x*72,p.y*72))
            coordinates.append(temp_list)


nested_dict_all=copy.deepcopy(nested_dict)
for key, value in storage.items():
    keys_list=key.split("|")
    temp_dict=nested_dict
    temp_dict_all=nested_dict_all

    for k in keys_list[:-1]:
        temp_dict=temp_dict.setdefault(k,{})
        temp_dict_all=temp_dict_all.setdefault(k,{})

    print(f'''{key}=={value}''')
    if value[1]<0.9:
      temp_dict[keys_list[-1]]=value
    temp_dict_all[keys_list[-1]]=value
    
json_str = json.dumps(nested_dict, indent=4)
json_str_all = json.dumps(nested_dict_all, indent=4)
print(json_str)
print('-----')
print(json_str_all)
print(coordinates)

def coordinate_get(idx,c):
  reader = PdfReader(FORM_NAME)
  page = reader.pages[0]
  original_lower_left=page.cropbox.lower_left
  original_lower_right=page.cropbox.lower_right
  original_upper_left=page.cropbox.upper_left
  original_upper_right=page.cropbox.upper_right

  height_of_pdf=float(original_upper_left[1])
  width_of_pdf=original_lower_right[0]

  writer = PdfWriter()
  page.mediabox.upper_left = (c[0][0],height_of_pdf-c[0][1])
  page.mediabox.upper_right = (c[1][0],height_of_pdf-c[1][1])
  page.mediabox.lower_right = (c[2][0],height_of_pdf-c[2][1])
  page.mediabox.lower_left = (c[3][0],height_of_pdf-c[3][1])


  writer.add_page(page)

  with open(f"output_{idx}.pdf", "wb") as fp:
      writer.write(fp)
      print("done")

for idx,c in enumerate(coordinates):
    coordinate_get(idx,c)
