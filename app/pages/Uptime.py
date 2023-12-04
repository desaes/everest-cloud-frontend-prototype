import streamlit as st
import os
import pymongo
import datetime
import requests
import pandas as pd
from dotenv import dotenv_values
config = dotenv_values(".env")

def get_projects():
    projects = []
    try:
        myclient = pymongo.MongoClient(f'mongodb://{config["DB_USER"]}:{config["DB_PASS"]}@{config["DB_HOST"]}:{config["DB_PORT"]}/')
        mydb = myclient["cloud"]
        project_collection = mydb["nutanix_project"]
    except Exception as e:
        print(f"Error connectiong to mongo {e}")
    for item in project_collection.find({}):
        #projects.append(item["metadata"].get("name"))
        projects.append(
            {"name": item["metadata"].get("name"), 
             "description": item["status"].get("description"),
             "uuid": item["metadata"].get("uuid")})
    return projects

def get_vms(project_uuid=0):
    vms = []
    try:
        myclient = pymongo.MongoClient(f'mongodb://{config["DB_USER"]}:{config["DB_PASS"]}@{config["DB_HOST"]}:{config["DB_PORT"]}/')
        mydb = myclient["cloud"]
        vm_collection = mydb["nutanix_vm"]
    except Exception as e:
        print(f"Error connectiong to mongo {e}")
    for item in vm_collection.find({"metadata.project_reference.uuid": project_uuid}):
        vms.append(
            {"name": item["status"]["name"],
             "uuid": item["metadata"]["uuid"]})
    return vms

project_list = get_projects()

project_description = st.selectbox(
    "Selecione o projeto",
    [project["description"] for project in project_list])

project_dict = next(item for item in project_list if item["description"] == project_description)
print(project_dict)

vm_list = get_vms(project_dict["uuid"])
vms = st.multiselect(
    'Selecione as máquinas virtuais',
    [vm["name"] for vm in vm_list])

def start_date():
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    year = current_year if current_month > 1 else current_year - 1
    month = current_month - 1 if current_month > 1 else 12
    return datetime.date(year, month, 1)
    
def stop_date():
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    month = current_month if current_month > 1 else 12
    first_day = datetime.datetime(current_year, month, 1)
    last_day_previous_month = first_day - datetime.timedelta(days=1)
    return last_day_previous_month.date()

col1, col2 = st.columns(2)
with col1:
    start = st.date_input("Selecione a data de início", start_date())
with col2:
    stop = st.date_input("Select a data de fim", stop_date())

table = []
for vm in vms:
    vm_dict = next(item for item in vm_list if item["name"] == vm)
    url = config["NUTANIX_API_URL"] + "/v1/vms/" + vm_dict["uuid"] + "/uptime?" + "start=" + start.strftime("%Y/%m/%d") + "&" + "stop=" + stop.strftime("%Y/%m/%d")
    response = requests.get(url)
    print(f'{vm_dict["name"]}: {response.json()["uptime"]}')
    table.append(
        {"Virtual Machine": vm_dict["name"],
        "Uptime": response.json()["uptime"]}
        )
if len(table) > 0:
    st.dataframe(table,width=800)

@st.cache_data 
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(pd.DataFrame(table))

st.download_button(
    label="Download da lista",
    data=csv,
    file_name='uptime.csv',
    mime='text/csv',
)    