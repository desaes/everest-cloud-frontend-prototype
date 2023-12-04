import streamlit as st
import os, sys
import pymongo
import pandas as pd
from dotenv import dotenv_values
import json
from collections import ChainMap
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

    fields = f'''
        {{
        "_id":0,
        "status.name": 1,
        "metadata.uuid": 1,
        "status.cluster_reference.name": 1,	
        "metadata.project_reference.name": 1,
        "metadata.creation_time": 1,
        "spec.resources.num_sockets": 1,
        "spec.resources.memory_size_mib": 1,
        "metadata.categories_mapping": 1
        }}
    '''    

    for vm in vm_collection.find({}):
        if vm["metadata"].get("project_reference"):
            project_uuid = vm["metadata"]["project_reference"]["uuid"]
            project = project_collection.find_one({"status.uuid": project_uuid})
            description = project["status"]["description"] if project else 'Descricao nao preenchida'
            #for project in project_collection.find_one({"metadata.uuid": project_uuid}):
            #    project_description = project["status"]["description"]
            try:
                vms.append(ChainMap(
                    {"VM": vm["status"].get("name"),
                    "UUID": vm["metadata"].get("uuid"),
                    "CLUSTER": vm["status"]["cluster_reference"].get("name"),
                    "NOME PROJETO": vm["metadata"]["project_reference"]["name"],
                    "DATA CRIACAO": vm["metadata"]["creation_time"],
                    "NUMERO DE SOCKETS": vm["spec"]["resources"]["num_sockets"],
                    "MEMORIA": vm["spec"]["resources"]["memory_size_mib"],
                    "DESCRICAO DO PROJETO": description
                    }, vm["metadata"].get("categories")))

                
            except Exception as e:
                print(f'Data error 1 {e}:\n {vm}')
        else:
            print("entrei aqui")
            try:
                vms.append(ChainMap(
                    {"VM": vm["status"].get("name"),
                    "UUID": vm["metadata"].get("uuid"),
                    "CLUSTER": vm["status"]["cluster_reference"].get("name"),
                    "NOME PROJETO": "Sem projeto",
                    "DATA CRIACAO": vm["metadata"]["creation_time"],
                    "NUMERO DE SOCKETS": vm["spec"]["resources"]["num_sockets"],
                    "MEMORIA": vm["spec"]["resources"]["memory_size_mib"],
                    "DESCRICAO DO PROJETO": "Sem descricao"
                    }, vm["metadata"].get("categories")))
                
            except Exception as e:
                print(f'Data error 2 {e}:\n {vm}')
            #print(f'The VM {vm["status"]["name"]} has no project reference')

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