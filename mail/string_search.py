import re

def string_to_perceelnr(string):
    gem = re.findall(r"([A-Za-z]{3}[0-9]{2})",string)[0]
    sec = re.findall(r"([A-Za-z]{1,2})",string.replace(gem,""))[0]
    nr = re.findall(r"([0-9]{2,5})",string.replace(gem,""))[0]
    return f"{gem}-{sec}-{nr}"

def get_perceelnr_units_from_txt(txt_string):
    units_string = re.findall(r"instruct(.*?)toeli",txt_string,re.DOTALL)
    perceelnr_string = re.findall(r"aanduiding(.*?)bezoek",txt_string,re.DOTALL)

    if units_string:
        units = re.findall(r"[1-9]{1,2}",units_string[0],re.DOTALL)
        units_sum = sum([int(u) for u in units])

    if perceelnr_string:
        perceelnr = string_to_perceelnr(perceelnr_string[0]).upper()
        
    return perceelnr,units_sum

def get_nr_from_string(string,min_length,max_length,parentheses=False):
    if parentheses:
        pattern = r"\(([0-9]{min_length,max_length})\)".replace("min_length",str(min_length)).replace("max_length",str(max_length))
    else:
        pattern = r"[0-9]{min_length,max_length}".replace("min_length",str(min_length)).replace("max_length",str(max_length))
    if (match:=re.search(pattern,string)):
        return int(re.findall(r"\d+",match.group())[0])

def format_fname(string):
    bad_chars = '[< > : " / \ | ? * ( ) @ + -]'
    fname = re.sub(bad_chars,"_",string).strip("_")
    return re.sub(r"[_]+","_",fname)