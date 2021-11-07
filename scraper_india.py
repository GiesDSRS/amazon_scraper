import requests
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def main():


    driver = webdriver.Chrome(ChromeDriverManager().install())

    #URL to use to search for product
    #URL = "https://www.amazon.com/s?k=fire+stick&i=electronics&crid=1N6P3O3CZIBJT&sprefix=f%2Caps%2C193&ref=nb_sb_ss_c_2_1_ts-doa-p"
    search = input("Enter search value:")
    URL = "https://www.amazon.in/s?k=" + generate_search_for_URL(search)
    print(URL)
    next = URL

    #list to contain rows of data extracted
    data = []
    #index of items
    index = 1



    while len(URL) != 0:

        #until we get an ERR_CONNECTION_REFUSED
        try:
            driver.get(URL)
        except WebDriverException as exception:
            break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results =soup.find_all('div', {'data-component-type': 's-search-result'})


        #going through the results of all divs
        for items in results:



            name = "No Name"
            rating = "No Rating Available"
            rating1 = "No Rating Available"
            #review = "No Review Available"
            #delivery_date = "Check Website"
            #prime = "No"
            ranking = -1
            price = "No Price Available"
            url_print = ""


            #getting name
            if  items.find('a', {'class' : 'a-link-normal a-text-normal'}) != None:
                name = items.find('a', {'class' : 'a-link-normal a-text-normal'}).get_text()


            #getting price
            if items.find('span',{'class':'a-offscreen'}) != None:
                price = items.find('span',{'class':'a-offscreen'}).get_text()
                #print(items.find('span',{'class':'a-offscreen'}).get_text())



            #Getting reviews and ratings
            if items.find('div',{'class': 'a-row a-size-small'}) != None:
                rating = items.find('div',{'class': 'a-row a-size-small'}).get_text()
                rating1 = rating.split('out')[0]
                #review = rating.split('stars ')[1]

                '''
            #getting delivery dates if provided, otherwsie website have to be checked
            if items.find('div',{'class':'a-row s-align-children-center' }) != None :
                if (len(items.find('div',{'class':'a-row s-align-children-center' }).get_text())) >= 2:
                    delivery_date = items.find('div',{'class':'a-row s-align-children-center' }).get_text().split(', ')[1]


            #If it is prime or not
            if items.find('div',{'class', 'a-row s-align-children-center', 'span' , 'class' ,'aok-inline-block s-image-logo-view'}) is not None:
                prime = "Yes"
                '''

            next = str(soup.find('li', {'class' : 'a-last'}))
            postfix = ""

            URL = get_next(next,postfix,0,0)


            url_product = str(items.find('a',{'class' : 'a-link-normal a-text-normal'}))
            ranking_url = "https://www.amazon.in" + get_ranking(url_product)
            #print(ranking_url[43:51])
            if ranking_url[43:51] == "Redirect":
                continue;

            #get the URL to get the ranking of the product
            driver.get(ranking_url)
            soup2 = BeautifulSoup(driver.page_source, 'html.parser')
            url_print = ranking_url

            final_ranking = ""





            if soup2.find('div' , {'id' : 'detailBulletsWrapper_feature_div'}) != None:
                ranking = soup2.find('div' , {'id' : 'detailBulletsWrapper_feature_div'})
                ranking2 = ranking.find_all('ul', {'class' : 'a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list'})


                if len(ranking2) >=2:
                    ranking3 = str(ranking2[1])
                    #print(ranking3)

                    #print(ranking3)
                    pos_of_ranking = get_category_ranking(ranking3, search)

                    #print(pos_of_ranking)



                    if pos_of_ranking == -1:
                        final_ranking =-1
                    else:
                        final_ranking = get_category_ranking_val(ranking3, pos_of_ranking)



                #print(final_ranking)
                ranking = final_ranking



            elif soup2.find('div' , {'class' : 'a-section table-padding'}) != None:
                ranking = soup2.find('div' , {'class' : 'a-section table-padding'})
                ranking2 = ranking.find_all('tr')


                for s in ranking2:
                    ranking3 = s.get_text()
                    if 'Rank' in ranking3:
                        pos_of_ranking = get_category_ranking(ranking3, search)

                        if pos_of_ranking == -1:
                            final_ranking =-1

                        else:
                            final_ranking = get_category_ranking_val(ranking3, pos_of_ranking)

                ranking = final_ranking
                #print('3')
                #print(ranking)
                #print(ranking_url)

            if len(str(ranking)) ==0:
                ranking = -1
            #data.insert(len(data), [index, name,rating1,review,delivery_date,prime,ranking,price])
            data.insert(len(data), [index, name,rating1,ranking,price,url_print])
            index+=1



    with open ('scraped_results.csv', 'w', newline ='',encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Index", "Name", "Rating", "Ranking", "Price", "URL"])
        writer.writerows(data)







'''
Function: generate_search_for_URL
Inputs:
    search: the value inputted by user to searh on amazon
Outputs:
    ret: the returned value where the searchable string in returned with lowercase and + between different words
Purpose: to parse the user inputted value to be searched
'''
def generate_search_for_URL(search):

    ret = ""
    search.strip()

    for x in search:

        if x == ' ':
            ret+='+'
            continue

        ret+= x.lower()


    return ret




'''
Function: get_next
Inputs:
    next: the string to be parsed to find the values for next URL
    postfix: the URL to be returned
    flag: signal to break out of the loop when the URL is created
    ctr: signal that we have found the URL and we should start processing
Outputs:
    postfix: the generated postfix for the amazon URL to
Purpose: to parse the next URL to load the page with the next product
'''
#def to generate the next URL
def get_next(next, postfix, flag, ctr):

    postfix= "https://www.amazon.in"

    for i in next:

        if i == '>':
            flag+=1
        if flag ==2:
            break
        if i == "/":
            ctr= 1
        if ctr == 1:
            postfix=postfix+i


    postfix = postfix[0:-1]
    return postfix





'''
Function: get_ranking
Inputs:
    url_product:
Outputs:
    postfix: the generated postfix for the amazon URL to
Purpose: to parse the next URL to load the page with the next product
'''
#def to get url of each product
def get_ranking(url_product):

    url = ""
    ctr = 0
    flag = 0

    for i in url_product:

        if i == ';' and ctr == 1:
            break

        if i == '/':
            ctr = 1
            flag = 1

        if flag == 1:
            url+=i

    return url







'''
Function: get_category_ranking
Inputs:
    ranking3: the string from which the ranking has to be found
    search: user-inputted value for search for which the rank has to be found
Outputs:
    pos_of_ranking: the position of the # before the ranking that needs to be found
Purpose: to parse and sends the position for # before the ranking for the specific user-input search,
         if does not exist it returns -1
'''
# returns the postion of # before the search values category
def get_category_ranking(ranking3, search):

    search = search.lower()
    ranking4 = ranking3.lower()


    if search not in ranking4:

        return -1



    c = "#"
    foo = ( [pos for pos, char in enumerate(ranking4) if char == c])
    #print(foo)

    if len(foo) == 0:
        return -1



    pos = ranking4.find(search)



    pos_of_ranking = 0

    for val in range(len(foo)-1):
        next = val+1
        if next > len(foo)-1:
            break

        if pos >= foo[val] and pos <= foo[next]:
            pos_of_ranking = foo[val]


    if pos_of_ranking == 0:
        pos_of_ranking = foo[len(foo) -1]

    return pos_of_ranking





'''
Function: get_category_ranking_val
Inputs:
    ranking3: the string from which the ranking has to be found
    pos_of_ranking: the position of the # before the ranking that needs to be found
Outputs:
    s: the string value of the integer which is the rank
Purpose: returns the string value of the rank
'''
def get_category_ranking_val(ranking3, pos_of_ranking):

    s = ""
    for y in range(pos_of_ranking+1, len(ranking3), 1):
        #print (ranking3[y])
        if ranking3[y] == ' ':
            break
        if ranking3[y] == ',':
            continue
        s+= ranking3[y]

    if len(s) == 0:
        return -1

    return int(s)

if __name__ == "__main__":
    main()
