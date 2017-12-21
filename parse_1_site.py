import requests
import bs4
import json
import csv
import pandas

url = "http://quotes.toscrape.com"

# GET more info about author, that has id equal specified


def request_author(id_author):
    with open('author.json', 'r') as f:
        list_data = json.load(f)
        for item in list_data:
            if item['id'] == id_author:
                print('id: {0} \n'
                      'url: {1} \n'
                      'author_title: {2}\n'
                      'born_data: {3}\n'
                      'born_place: {4}\n'
                      'author_info: {5}\n'.format(item['id'],
                                                   item['url'],
                                                   item['author_title'],
                                                   item['born_data'],
                                                   item['born_place'],
                                                   item['author_info'],
                                                   ))
                break

    return None


def clear_files():

    clear_one_type('author')
    clear_one_type('quote')
    clear_one_type('tags')


def clear_one_type(name):

    with open(name + '.json', 'w') as f:
        json.dump([], f)
    with open(name + '.csv', 'w') as f:
        pass
    with open(name + '.xls', 'w') as f:
        pass
    with open(name + '.txt', 'w') as f:
        pass

# before data save in .json file and than in others files


def write_to_file(data, file_name):

    with open(file_name+'.json', 'r') as f:
        last_data = json.load(f)

    with open(file_name+'.json', 'w') as f:
        last_data.append(data)
        json.dump(last_data, f)

        f_txt = open (file_name + '.txt', 'w')

        for row in last_data:
            f_txt.write(str(row))
            with open (file_name + '.csv', "w") as file:
                columns = row.keys()
                writer = csv.DictWriter (file, fieldnames=columns)
                writer.writeheader ()

                writer.writerows (last_data)

        data = pandas.read_csv(file_name+'.csv')

        writer = pandas.ExcelWriter(file_name + ".xlsx", engine='xlsxwriter')
        data.to_excel(writer)
        writer.save()

        f_txt.close()


    return
    # with open(file_name+'.xls', 'a') as f:
    #     json.dump(data, f)

# this function search more info about author`s quote


def par_of_author(author_url, id_author, author_list):

    r = requests.get(url=url + author_url)

    if r.status_code != 200:
        return None

    soup_author = bs4.BeautifulSoup(r.content, "html.parser")

    author_title = soup_author.select('h3.author-title')[0].text
    born_data = soup_author.select('span.author-born-date')[0].text
    born_place = soup_author.select('span.author-born-location')[0].text
    author_info = soup_author.select('div.author-description')[0].text
    # check duplicate record in file
    if not (author_title in author_list):
        author_list.append(author_title)
        # create record about author
        author_dict = {
            'id': id_author,
            'url': author_url,
            'author_title': author_title,
            'born_data': born_data,
            'born_place': born_place,
            'author_info': author_info[9:]
        }

        id_author += 1

        write_to_file(author_dict, 'author')

    return id_author, author_list

# this function search more info about tags in quote


def par_of_tags(tag, tag_url):

    dict_quote_tag = {}
    # check access to web-page
    try:
        r = requests.get (url=url + tag_url)
    except:
        return None

    soup_tag = bs4.BeautifulSoup(r.content, "html.parser")

    id_quote_tag = 1
    # search info about all tag in current quote
    for i in range (len (soup_tag.select ("div.quote"))):

        quote_tag = soup_tag.select ("div.quote")[i]
        text_tag = quote_tag.select ('span.text')[0].text[1:-1]

        author_tag = quote_tag.select ("small.author")[0].text
        author_url_tag = quote_tag.select ("span > a")[0].get ("href")

        # create record about tag
        dict_quote_tag = {'id': id_quote_tag,'tag': tag, 'tag_url': tag_url, 'Text': text_tag,
                                        'author': author_tag, 'author_url': url + author_url_tag}
        id_quote_tag += 1

    return dict_quote_tag


def par_of_page():

    id_quote = 1
    id_author = 1
    next_page_url = ""
    has_next = True
    num_page = 1
    author_dict = {}
    author_list = []
    list_tags = []
    list_tags_deep = []

    currently_tags = {}

    while has_next:
        # execute request need web-page
        r = requests.get(url=url + next_page_url)
        # check access to web-page
        if r.status_code != 200:
            break

        print("\n\nPage: ", num_page)
        #print("\n")

        soup = bs4.BeautifulSoup(r.content, "html.parser")
        # parsing every quote on current page
        for i in range(len(soup.select("div.quote"))):
            quote = soup.select ("div.quote")[i]
            text = quote.select ('span.text')[0].text[1:-1]

            author = quote.select ("small.author")[0].text
            author_url = quote.select ("span > a")[0].get("href")
            # print(author, ' ---- ', author_url)

            # parsing data about author and sava this information
            id_author, author_list = par_of_author(author_url, id_author, author_list)

            # check all tags for this quote
            for num_tag in range(len(quote.select (".tags > a"))):

                try:
                    tag = quote.select(".tags > a")[num_tag].text
                except IndexError:
                    tag_url = None
                else:
                    tag_url = quote.select (".tags > a")[num_tag].get ("href")

                #print(tag, ' ---- ', tag_url)

                # find all quote, that applies to current tag
                list_tags_deep.append(par_of_tags(tag, tag_url))

                currently_tags[tag] = {'tag': tag, "tag_url": tag_url}

                # check duplicate in file and write if hasn`t
                if not(tag in list_tags):
                    list_tags.append(tag)
                    dict_tags = {'tag': tag, "tag_url": url + tag_url}

                    write_to_file(dict_tags, 'tags')
                    dict_tags.clear()

            # create record about quote
            dict_quote = {
                'id_quote': id_quote,
                'Text': text,
                'author_title': author,
                'author_url': url+author_url,
                'tags': list_tags_deep
            }
            id_quote += 1

            write_to_file(dict_quote, "quote")

        # clear data
            list_tags_deep.clear()
            author_dict.clear()
            currently_tags.clear()
            dict_quote.clear()

        # check page on existence button and get url next page
        try:
            next_page_url = soup.select("li.next > a")[0].get("href")
        except IndexError:
            print('tHE last pages')
            break
        else:
            print(next_page_url)

        num_page += 1

    return


def main():
    # clear all files for future work
    clear_files()
    # parse the website
    par_of_page()
    # search information about author
    request_author(17)
    return

# This program starting and execute parsing web-page
# and save data in 3 files in different type4


main()
