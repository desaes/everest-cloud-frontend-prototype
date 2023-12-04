import streamlit as st
import os
import pymongo
import pandas as pd
from dotenv import dotenv_values
config = dotenv_values(".env")

def get_vms():
    vms = []
    try:
        myclient = pymongo.MongoClient(f'mongodb://{config["DB_USER"]}:{config["DB_PASS"]}@{config["DB_HOST"]}:{config["DB_PORT"]}/')
        mydb = myclient["cloud"]
        project_collection = mydb["nutanix_project"]
        vm_collection = mydb["nutanix_vm"]
    except Exception as e:
        print(f"Error connectiong to mongo {e}")
    for vm in vm_collection.find({}):
        application = vm["metadata"]["categories"]["CalmApplication"] if vm["metadata"]["categories"].get("CalmApplication") else 'Aplicacao nao preenchida'
        if vm["metadata"].get("project_reference"):
            project_uuid = vm["metadata"]["project_reference"]["uuid"]
            project = project_collection.find_one({"status.uuid": project_uuid})
            description = project["status"]["description"] if project else 'Descricao nao preenchida'
            #for project in project_collection.find_one({"metadata.uuid": project_uuid}):
            #    project_description = project["status"]["description"]
            vms.append(
                {"VM": vm["status"].get("name"),
                "UUID": vm["metadata"].get("uuid"),
                "CLUSTER": vm["status"]["cluster_reference"].get("name"),
                "NOME PROJETO": vm["metadata"]["project_reference"]["name"],
                "DESCRICAO DO PROJETO": description,
                "APLICACAO": application
                })
        else:
            vms.append(
                {"VM": vm["status"].get("name"),
                 "UUID": vm["metadata"].get("uuid"),
                "CLUSTER": vm["status"]["cluster_reference"].get("name"),
                "NOME PROJETO": "Sem projeto",
                "DESCRICAO DO PROJETO": "Sem descricao",
                "APLICACAO": application
                })
            print(f'The VM {vm["status"]["name"]} has no project reference')

    return vms    

st.dataframe(get_vms())

@st.cache_data 
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(pd.DataFrame(get_vms()))

st.download_button(
    label="Download da lista",
    data=csv,
    file_name='vms.csv',
    mime='text/csv',
)