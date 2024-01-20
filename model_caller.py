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
storage={}
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