import requests
import bs4
import time
import pandas

#
url = 'https://www.expireddomains.net/deleted-net-domains'

# login in system with login: mister007; password: mister007


def log_in():

    login_data = {"username": "mister007", "password": "mister007"}

    with requests.Session () as c:
        url_log = 'https://www.expireddomains.net/login/'

        c.post(url_log, data=login_data)
        page = c.get(url)
        if 'Logout' in page.text:
            print ("True")
        else:
            print("FAlse")

    return


def clear_files():

    with open('del_domains.json', 'w') as f:
        pass
    with open('del_domains.csv', 'w') as f:
        pass
    with open('del_domains.xlsx', 'w') as f:
        pass
    with open('del_domains.txt', 'w') as f:
        pass


def write_to_file(data):

    f_txt = open ('del_domains.txt', 'a')
    f_txt.write(data)
    f_txt.close()

    f_json = open ('del_domains.json', 'a')
    f_json.write(data)
    f_json.close()

    f_csv = open ('del_domains.csv', 'a')
    f_csv.write (data)
    f_csv.close ()

    return


def last_write():

    data = pandas.read_csv('del_domains.csv')

    writer = pandas.ExcelWriter("del_domains.xlsx", engine='xlsxwriter')
    data.to_excel(writer)
    writer.save()


    return


def par_of_page():

    next_page_url = ""
    has_next = True
    num_page = 1
    count = 1
    flag_start = False

    while has_next:

        if not flag_start:
            r = requests.get(url=url + next_page_url[20:])
            flag_start = True
        else:
            r = requests.get (url=url[:-20] + next_page_url)

        if r.status_code != 200:
            print(url + next_page_url)
            break

        print("\n\nPage: ", num_page)
        print("\n")

        soup = bs4.BeautifulSoup(r.content, "html.parser")

        # get name deleted domains .net
        for i in range(len(soup.select("td.field_domain"))):
            print("\nThis is domain ", count)

            block = soup.select("td.field_domain")[i]
            text = block.select('a')[0].text

            print("TEXT: ", text)

            write_to_file(text+'\n\r')

            count += 1

        # check page on existence button and get url next page
        try:
            next_page_url = soup.select("a.next")[0].get("href")
        except IndexError:
            print('tHE last pages')
            print (next_page_url)
            break
        else:
            print(next_page_url)

        num_page += 1

        time.sleep(3)

    return


def main():
    # clear all files for future work
    clear_files()
    # login in system
    log_in()
    # process parsing
    par_of_page()
    # save data to .xlsx and .json files
    last_write()
    return


main()
