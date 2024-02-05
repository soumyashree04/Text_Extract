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
      "Atm_Savings": [],
      "Atm_Checking": [],
      "Branch": [],
      "Date_Accomplished": [],
      "Company_Name": [],
      "Access_To_Alternative_Channels": {
        "Mobile_Banking": {
          "Enroll": [],
          "No_Need": []
        },
        "Online_Banking": {
          "Enroll": [],
          "No_Need": [],
          "Preferred_User_Id": {
            "Preferred_User_Id1": [],
            "Preferred_User_Id2": [],
            "Preferred_User_Id3": []
          }
        }
      },
      "For_Bank_Use": {
        "Employee_Cif_No": [],
        "Employer_Cif_No": [],
        "Employee_Account_No": [],
        "Atm_Card_No": [],
        "Referred_By": [],
        "Sig_Verified_By_Date": [],
        "Account_Opened_By_Date": [],
        "Approved_By_Date": [],
        "Scanned_By_Date": []
      },
      "For_Acd_Use": {
        "Received_By_Date": [],
        "Processed_By_Date": [],
        "Checked_By_Date": [],
        "Remarks": []
      },
      "Employee_Information": {
        "Name": [],
        "Gender": {
          "Male": [],
          "Female": []
        },
        "Date_Of_Birth": [],
        "Place_Of_Birth": {
          "Philippines": [],
          "Others": {
            "Box": [],
            "Value": []
          }
        },
        "Nationality": {
          "Filipino": [],  
          "Others": {
            "Box": [],   
            "Value": []    
          }
        },
        "Civil_Status": {
          "Single": [],
          "Married": [],
          "Separated": [],
          "Divorced": [],
          "Widowed": []
        },
        "Name_Of_Spouse": [],
        "Mother_Maiden_Name": [],
        "Home_Phone_Number": [],
        "Home_Permanent_Address": [],
        "Home_Permanent_Address_Zip_Code": [],
        "Present_Address": {
            "Same_As_Home_Address": [],
            "Others": [],
            "Zipcode":[]
          },
        "Mobile_Phone_Number": [],
        "Email_Address": [],
        "Tin_Sss": {
            "Tin":[],
            "Sss":[],
            "Value": []
        },
        "Occupation": {
          "Accountant": [],
          "Custom_Broker": [],
          "Jeweler": [],
          "Lawyer": [],
          "Money_Changer": [],
          "Others": {
            "Box": [],
            "Value": []
          }
        },
        "Employee_Id": [],
        "Date_Hired": [],
        "Gross_Monthly_Income": {
            "Below_PHP_20000": [],
            "PHP_20000_To_49999": [],
            "PHP_50000_To_99999": [],
            "PHP_100000_To_499999": [],
            "PHP_500000_To_999000": [],
            "PHP_1000000_And_Above": []
        },
        "Employer_Nature_Of_Business": {
          "Agriculture_Fishing": [],
          "Admin_Support": [],
          "Construction": [],
          "Education": [],
          "Financial_Insurance": [],
          "It_Communication": [],
          "Manufacturing": [],
          "Mining_Quarrying": [],
          "Professional_Service": [],
          "Transportation_Storage": [],
          "Wholesale_Retail": [],
          "Others": {
            "Box": [],
            "Value": []
          }
        },
        "Work_Business_Address": [],
        "Work_Business_Phone_Number":[],
        "Affiliations_With_China_Bank": {
            "I_Am_A_Director": {
              "Yes": [],
              "No": [],
              "Employee_No": []
            },
            "My_Relative_Is_A_Director": {
              "Yes": [],
              "No": [],
              "Name": [],
              "Relationship": []
            },
            "I_Am_Related": {
              "Yes": [],
              "No": []
            },
            "Relationship_With_Government_Personnel": {
              "Occupying":[],
                "Relative": [],
                "Association": [],
                "Position": []
              }
          },
        "Residency": {
          "Resident": [],
          "Acr_I_Card_No": [],
          "Non_Resident": []
        },
        "Preferred_Mailing_Address": {
          "Home_Permanent_Address": [],
          "Present_Address": [],
          "Work_Business_Address": []
        }
      },
      "Foreign_Account_Tax_Compliance_Act_Information": {
        "Are_You_Us_Citizen": {
          "Yes": [],
          "No": []
        },
        "Do_You_Have_Any_Records_In_Us": {
          "Yes": [],
          "No": []
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
        if "signature" in name.lower():
            points=field.bounding_regions[0].polygon
            for p in points:
                coordinates.append((p.x*72,p.y*72))


nested_dict={}
nested_dict_all={}
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

reader = PdfReader(FORM_NAME)
page = reader.pages[0]
original_lower_left=page.cropbox.lower_left
original_lower_right=page.cropbox.lower_right
original_upper_left=page.cropbox.upper_left
original_upper_right=page.cropbox.upper_right

height_of_pdf=original_upper_left[1]
width_of_pdf=original_lower_right[0]

writer = PdfWriter()
page.mediabox.upper_left = (coordinates[0][0],height_of_pdf-coordinates[0][1])
page.mediabox.upper_right = (coordinates[1][0],height_of_pdf-coordinates[1][1])
page.mediabox.lower_right = (coordinates[2][0],height_of_pdf-coordinates[2][1])
page.mediabox.lower_left = (coordinates[3][0],height_of_pdf-coordinates[3][1])


writer.add_page(page)

with open("output.pdf", "wb") as fp:
    writer.write(fp)
    print("done")
