import json
import xmltodict
import pprint
import time
import html 
import re
import gzip
import html.entities

entities = {k: v for k, v in html.entities.entitydefs.items() if v not in "&'\"<>"}

entity_re = re.compile("&([^;]+);")

def append_to_list(item):
    """
    Appends selected types of publication to a list of types to export.
    """
    if item in selected_items:
        print ("The selected item is already in the list")
    else: 
        selected_items.append(item)

def resolve_entity(m):
    try:
        return entities[m.group(1)]
    except KeyError:
        return m.group(0)


def expand_line(line):
    return entity_re.sub(resolve_entity,line)

        
def import_file(file):
    """
    Unzips dblp file, changes it codification to UTF-8 and reads its content.
    
    Then parses that info and stores it into a dictionary
    """
    f = gzip.open(file, mode="rt", encoding="ISO-8859-1", newline="\n")
    XML_content = expand_line(f.read())
    f.close()
    dictionary = xmltodict.parse(XML_content)
    return dictionary


def create_authors_dictionary(dictionary):
    """
    As an author can be represented with different names in dblp file this function selects the first appearance 
    as a key name and store all different names in a dictionary.
    """
    
    #authors_file = open("authors_dictionary.json", 'w', encoding='UTF-8')
    
    authors_dict={}
    #tmp_authors_dict={}
    for key, value in dictionary.items():
        for tipo in value:
            if tipo == "www":
                for dic in value[tipo]:
                    for key in dic:
                        if key == "author":
                            if isinstance(dic[key], list): 
                                for value in dic[key]:
                                    if isinstance(value, str): 
                                        selected_author_name = dic[key][0]
                                        author_name = value
                                        authors_dict[author_name]=selected_author_name
                                        
    #json.dump(authors_dict, authors_file, ensure_ascii=False)
    return authors_dict

def export_authors_dictionary(dictionary):

    outputfile = open("authors_dictionary.json", 'w', encoding='UTF-8')
    
    authors_dict={}
    for key, value in dictionary.items():
        for tipo in value:
            if tipo == "www":
                for dic in value[tipo]:
                    for key in dic:
                        if key == "author":
                            if isinstance(dic[key], list): 
                                for value in dic[key]:
                                    if isinstance(value, str): 
                                        selected_author_name = dic[key][0]
                                        author_name = value
                                        if author_name != selected_author_name:
                                            authors_dict['author'] = selected_author_name
                                            authors_dict['authors_synonym'] = author_name
                                            json.dump(authors_dict, outputfile, ensure_ascii=False)
                                        authors_dict={}
    outputfile.close()


def insert_author(publication, key, authors, authors_dict, pub_type):
    """
    Inserts author's information for a publication. 
    
    Acts differently depending on the publication's type, the number of authors provided or if the author appears with another name in the dblp file.
    """
    
    if pub_type == "www":
        publication[key] = authors
    else:
        if isinstance(authors, list):
            author_list=[]
            for author in authors:
                if isinstance(author, str):  
                    if author in authors_dict: # checking if homonimous
                        author_list.append(authors_dict[author])
                    else:
                        author_list.append(author)
                else: # if author info is a dictionary
                    author_list.append(author['#text'])
            publication[key]=author_list
        else:
            if isinstance(authors, str):
                if authors in authors_dict:
                    publication[key] = authors_dict[authors]
                else:
                    publication[key] = authors
                
    return publication

    
def create_JSON(dictionary, authors_dict, output_file_name):
    """
    Creates the output file containing every publication's information. 
    """
    if output_file_name:
        outputfile = open(output_file_name, 'w', encoding='UTF-8') 
    else:
        outputfile = open("dblp.json", 'w', encoding='UTF-8')     
    publication = {}

    for key, value in dictionary.items():
        for type in value:
            if type in selected_items:
                for dic in value[type]:
                    publication['type'] = type
                    for key in dic:
                        if key == "year":
                            if isinstance(dic[key], list): 
                                publication[key] = dic[key]
                            else: 
                                publication[key] = int(dic[key])                             
                        elif key == "author":
                            publication = insert_author(publication, key, dic[key], authors_dict, type)
                        else:
                            publication[key] = dic[key]
                    json.dump(publication, outputfile, ensure_ascii=False)
                    publication = {}
    outputfile.close()

    
def main(): 
    

    
    menu = {}
    menu['1']="article"
    menu['2']="inproceedings"
    menu['3']="proceedings"
    menu['4']="book" 
    menu['5']="incollection"
    menu['6']="phdthesis"
    menu['7']="mastersthesis"
    menu['8']="www" 
    menu['9']="Create JSON"
    menu['0']="Exit"
    
    while True:
        print ("")
        print ("------------------------")
        options=menu.keys()
        for entry in options:
            print (entry, menu[entry])

        print ("------------------------")
        print ("")
        print ("Selected items: " + str(selected_items))
        selection=input("Please Select:")

        if selection in menu.keys():
            if selection == '0' :
                break
            elif selection =='9':
            
                output_file_name=input("Please specify the output file name: [Default: dblp.json]")
                
                input_file = 'data/dblp.xml.gz'
                     
                start_time = time.time()
                    
                dictionary = import_file(input_file)
                     
                import_time = time.time()
                     
                print("XML to dictionary time: "+str(round(import_time - start_time,3))+" sec.")
                    
                pre_dictionary = time.time()

                authors_dict = create_authors_dictionary(dictionary)

                export_authors_dictionary(dictionary)
                
                post_dictionary = time.time()
                    
                print("Authors dictionary time: "+str(round(post_dictionary - pre_dictionary,3))+" sec.")
                    
                start_time = time.time() 

                create_JSON(dictionary, authors_dict, output_file_name)
                
                JSON_time = time.time()

                print("Create JSON time: "+str(round(JSON_time - start_time,3))+" sec.")    

                break
            else:
                append_to_list(menu[selection])
        else:
            print ("Unknown Option Selected!")
        
    
if __name__ == '__main__': 

    selected_items=[]
    
    main()