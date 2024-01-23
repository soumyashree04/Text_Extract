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
storage={"Root": {
        "Branch_Name": [],
        "Date": [],
        "Cif_No": [],
        "Name": [],
        "Company_Name": [],
        "Enrollment_Instructions": {
            "Account_Number": [],
            "Atm_Card": {
                "Avail": [],
                "No_Need": [],
                "ATM_Card_Number": []
            },
            "Mobile_Banking": {
                "Enroll": [],
                "No_Need": []
            },
            "Online_Banking": {
                "Enroll": [],
                "No_Need": [],
                "User_Id": []
            },
            "Preferred_User_Ids": {
                "Id1": [],
                "Id2": [],
                "Id3": []
            }
        },
        "Maintenance_Requests": {
            "Atm_Card": {
                "Atm_Card_Number": [],
                "Request_For_Atm_Card_Replacement":[],
                "Request_For_Atm_Card_Replacement_With_New_Card_Name": {
                    "Box": [],
                    "Atm_Card_Name": []
                },
                "Request_For_Atm_Pin": [],
                "Unlink_Drop_Account_Numbers": {
                    "Unlink": [],
                    "Account_Numbers": []
                },
                "Close_Atm_Account": {
                    "Box":[],
                    "Reason": []
                }
               
            },
            "Mobile_Banking": {
                "User_Id": [],
                "Suspend_Access": [],
                "Reason": []
            },
            "Online_Banking": {
                "Username":[],
                "Request_For_Online_Banking_Login": [],
                "Request_For_Online_Banking_Transaction_Password": [],
                "Increase_My_Fund_Transfer": [],
                "Unlink_Drop_Account_Numbers": {
                    "Unlink": [],
                    "Account_Numbers": []
                },
                "Close_Online_Banking_Account": {
                    "Box":[],
                    "Reason": []
                }
            },
            "Phone_Banking": {
                "Phone_Banking_Account_Number": [],
                "Request_For_Phone_Banking_Access_Tpin": [],
                "Request_For_Phone_Banking_Transaction_Tpin": [],
                "Unlink_Drop_Account_Numbers": {
                    "Unlink": [],
                    "Account_Numbers": []
                },
                "Link_Drop_Account_Number": {
                    "Link": [],
                    "Drop":[],
                    "Account_Numbers": []
                },
                "For_Interbank_Fund_Transfers": {
                    "Account_Name": [],
                    "Name_Of_Bank": []
                }
            },
            "Remarks": []
        },
        "Receiving_Branch": {
            "Received_By_Date": [],
            "Branch_Name": []
        },
        "Maintaining_Branch": {
            "Checked_By_Date": [],
            "Approved_By_Date": []
        },
        "Alternative_Channels_Division": {
            "Received_By_Date": [],
            "Processed_By_Date": [],
            "Checked_By_Date": []
        },
        "Customer's_Acknowledgment": {
            "Atm_Card": {
                "Issued_By_Date": [],
                "Received_By_Date": []
            },
            "Atm_Pin": {
                "Issued_By_Date": [],
                "Received_By_Date": []
            },
            "Phone_Banking_Tpin": {
                "Issued_By_Date": [],
                "Received_By_Date": []
            }
        }
    }
}
for document in result.documents:
    for name, field in document.fields.items():
        value=field.value if field.value else field.content
        #print(f"{name}={value} [{field.confidence}]")
        storage[name]=[value,field.confidence]
        if "signature" in name.lower():
            points=field.bounding_regions[0].polygon
            for p in points:
                coordinates.append((p.x*72,p.y*72))


nested_dict={}

for key, value in storage.items():
    keys_list=key.split("|")
    temp_dict=nested_dict

    for k in keys_list[:-1]:
        temp_dict=temp_dict.setdefault(k,{})

    temp_dict[keys_list[-1]]=value
json_str = json.dumps(nested_dict, indent=4)
print(json_str)
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
