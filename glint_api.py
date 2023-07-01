import requests
import re
from csv import DictWriter
import pandas as pd
import time

# #default setting
# limit = 30
# offset =0



#kode region indonesia
# country_code ='ID'

# #pencarian pekerjaannya apa
# search_term = 'software engineer'

#domain glints
# domain = 'https://glints.com/'

print("BOT LowKer via Glints")

search_term = input('masukkan pekerjaan yang dicari: ')
name_file = input('masukkan nama file: ')

def write_csv_1(data, nama=name_file):
    with open(f'{nama}.csv','a',encoding='utf-8',newline='')as file:
        headers = [
            'pekerjaan','skills','pengalaman','gaji',
            'kerjaan_remote','nama_perusahaan',
            'lokasi_kota',
            'rilis_lowongan','link']
        csv_writer = DictWriter(file, fieldnames=headers)
        csv_writer.writeheader()
        for x in data:
            csv_writer.writerow(x)

def write_csv_2(data, nama=name_file):
    with open(f'{nama}.csv','a',encoding='utf-8',newline='')as file:
        headers = [
            'pekerjaan','skills','pengalaman','gaji',
            'kerjaan_remote','nama_perusahaan',
            'lokasi_kota',
            'rilis_lowongan','link']
        csv_writer = DictWriter(file, fieldnames=headers)        
        csv_writer.writerow(data)

counter = 1
offset =0
tampil = True
data_job =[]

while tampil:
    url = 'https://glints.com/api/graphql'
    payload = {
        "operationName": "searchJobs",
        "variables": {
            "data": {
                "SearchTerm": search_term,
                "CountryCode": "ID",
                "limit": 50,
                "offset": offset,
                "includeExternalJobs": True,
                "sources": [
                    "NATIVE",
                    "SUPER_POWERED"
                ],
                "searchVariant": "CURRENT"
            }
        },
        "query": "query searchJobs($data: JobSearchConditionInput!) {\n  searchJobs(data: $data) {\n    jobsInPage {\n      id\n      title\n      isRemote\n      status\n      createdAt\n      updatedAt\n      isActivelyHiring\n      isHot\n      shouldShowSalary\n      salaryEstimate {\n        minAmount\n        maxAmount\n        CurrencyCode\n        __typename\n      }\n      company {\n        ...CompanyFields\n        __typename\n      }\n      citySubDivision {\n        id\n        name\n        __typename\n      }\n      city {\n        ...CityFields\n        __typename\n      }\n      country {\n        ...CountryFields\n        __typename\n      }\n      category {\n        id\n        name\n        __typename\n      }\n      salaries {\n        ...SalaryFields\n        __typename\n      }\n      location {\n        ...LocationFields\n        __typename\n      }\n      minYearsOfExperience\n      maxYearsOfExperience\n      source\n      hierarchicalJobCategory {\n        id\n        level\n        name\n        children {\n          name\n          level\n          id\n          __typename\n        }\n        parents {\n          id\n          level\n          name\n          __typename\n        }\n        __typename\n      }\n      skills {\n        skill {\n          id\n          name\n          __typename\n        }\n        mustHave\n        __typename\n      }\n      __typename\n    }\n    totalJobs\n    __typename\n  }\n}\n\nfragment CompanyFields on Company {\n  id\n  name\n  logo\n  __typename\n}\n\nfragment CityFields on City {\n  id\n  name\n  __typename\n}\n\nfragment CountryFields on Country {\n  code\n  name\n  __typename\n}\n\nfragment SalaryFields on JobSalary {\n  id\n  salaryType\n  salaryMode\n  maxAmount\n  minAmount\n  CurrencyCode\n  __typename\n}\n\nfragment LocationFields on HierarchicalLocation {\n  id\n  name\n  administrativeLevelName\n  formattedName\n  level\n  parents {\n    id\n    name\n    administrativeLevelName\n    formattedName\n    level\n    __typename\n  }\n  __typename\n}\n"
    }

    reference = 'https://glints.com/id/opportunities/jobs/'
    response = requests.post(url=url,json=payload).json()
    jobs = response["data"]["searchJobs"]["jobsInPage"]
    total_jobs = response["data"]["searchJobs"]["totalJobs"]

    if offset==0:
        print(f'Ada total {total_jobs} ditemukan...')
        print('\n')
    
    for job in jobs:
        pekerjaan = job["title"]    
        pekerjaan_parse = pekerjaan.split(' ')
        domain_kerjaan = '-'.join(pekerjaan_parse)
        domain_kerjaan = domain_kerjaan.lower()

        remote = job["isRemote"]
        nama_perusahaan = job["company"]["name"]
        lokasi = job["city"]["name"]
        # status = job["status"]
        min_years = job['minYearsOfExperience']
        max_years = job['maxYearsOfExperience']
        pengalaman = f"{min_years} - {max_years} tahun"

        id = job['id']
        Link = reference + domain_kerjaan+ '/'+ id

        published = job['updatedAt']
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        date_post = re.search(date_pattern,published)

        skills = job['skills']
        keterampilan =[]
        for skill in skills:
            kebutuhan = skill['skill']['name']
            keterampilan.append(kebutuhan)

        gaji = job["salaries"]
        if len(gaji)==1:
            min_gaji = gaji[0]["minAmount"]
            max_gaji = gaji[0]["maxAmount"]
            kurs = gaji[0]["CurrencyCode"]
            rentang_gaji = f"{kurs} {min_gaji} - {max_gaji}"
        elif len(gaji)==2:
            min_gaji = gaji[0]["minAmount"]
            max_gaji = gaji[1]["maxAmount"]
            kurs = gaji[0]["CurrencyCode"]
            rentang_gaji = f"{kurs} {min_gaji} - {max_gaji}"
        elif len(gaji) <1:
            rentang_gaji = '-'    

        if remote == False:
            remote = 'tidak'
        else:
            remote = 'iya'

        report = {
            'pekerjaan' : pekerjaan,
            'skills' : keterampilan,
            'pengalaman' : pengalaman,
            'gaji' : rentang_gaji,
            'kerjaan_remote' : remote,
            'nama_perusahaan' : nama_perusahaan,
            'lokasi_kota' : lokasi,        
            'rilis_lowongan' : date_post[0],
            'link' : Link
        }
        print(f'({counter}){report}')
        if offset >= 50:
            buat_file = write_csv_2(report)            
        data_job.append(report)            
        counter = counter+1
    
    if offset == 0:
        buat_file = write_csv_1(data_job)
    
    if len(data_job) < total_jobs:
        notif = input("tampilkan lebih banyak lagi (y/n): ")
        while notif != 'y' and notif !='n':
            print('jawab dengan "y" atau "n"')
            notif = input("tampilkan lebih banyak lagi (y/n): ")
        if notif =='y':
            tampil=True
            offset = offset+50
            print('please wait...')
        else:
            offset=0
            print('please wait, menutup aplikasi...')
            tampil = False
    
    time.sleep(5)
    




    # list_kerjaan = pd.DataFrame(data_job)
    # list_kerjaan.to_csv('softWare_Engineer_3.csv')

    

    


