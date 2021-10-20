def main():
  job_crawler()


def job_crawler():
    database_path = "jobdata.db"
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv: 49.0) Gecko / 20100101 Firefox / 49.0'}
    components_list = []
    for counter in range(1, 11):
        if counter == 1:
            requested_site = requests.get(
                "https://jobs.meinestadt.de/reinfeld-holstein/suche?words=Data%20Analyst#order=search(stelle%2Cfalse)"
                "&jobsSearch=%7B%22radius%22%3A75%2C%22d%22%3Anull%2C%22minijob%22%3Afalse%2C%22filters%22%3A%5B%5D%7D",
                headers=header
            )
        else:
            requested_site = requests.get(
                "https://jobs.meinestadt.de/reinfeld-holstein/suche?words=Data%20Analyst&page="
                + str(counter) + "#order=search(stelle%2Cfalse)"
                "&jobsSearch=%7B%22radius%22%3A75%2C%22d%22%3Anull%2C%22minijob%22%3Afalse%2C%22filters%22%3A%5B%5D%7D",
                headers=header
            )
        site_html = BeautifulSoup(requested_site.text, "html.parser")
        #Get all the hyperlink elements out of the html document and save them to a list
        hyperlink_elements_list = site_html.find_all("a", {"class": "m-resultListEntryJobScan__clickArea"})
        for hyperlink_element in hyperlink_elements_list:
            #get all the components out of the hyperlink element as a list and save them inside another list
            components_list.append(re.findall(re.compile(r"'.+?'"), str(hyperlink_element)))
        for components in components_list:
            component_dicts_list = []
            for component in components:
                #Remove not needed stuff from the string
                component = component.replace(r"\'", "").replace(r"'", "")
                #load the data as json and save the returned dict to a list
                component_dicts_list.append(json.loads(component))
            url = component_dicts_list[0]["url"]
            job_name = component_dicts_list[3]["mslayer_element_text"]
            company_name = component_dicts_list[3]["mslayer_element_company_name"]
            entry_date = component_dicts_list[3]["mslayer_element_detail_start_date"]
            if not find_in_database(database_path, company_name):
                insert_into_database(database_path, url, job_name, company_name, entry_date)
            else:
                print(find_in_database(database_path, company_name))
        time.sleep(2)
        
        
def find_in_database(db_name, company_name):
    con = sl.connect(db_name)
    with con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM jobdata WHERE company_name = ? ", (company_name,))
        return cursor.fetchone()


def insert_into_database(db_name, url, job_description, company_name, entry_date):
    con = sl.connect(db_name)
    with con:
        con.execute("INSERT INTO jobdata (url, job_description, company_name, entry_date) VALUES (?, ?, ?, ?)",
                    (url, job_description, company_name, entry_date))


if __name__ == '__main__':
    main()
