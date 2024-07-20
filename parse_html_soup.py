import re


def is_match(re_module, text1: str, text2: str):
    """Compare to the first text to the second one by checking if all the keywords are in the second text"""
    keywords = re_module.findall(r"[a-zA-Z]+|\d+", text1)
    for word in keywords:
        if (len(word) == 0 or # skip empty strings
        (len(word) == 1 and re.match(r'\W', word)) #Skip special charectors
        ):
            continue
        if (not (word.lower() in text2.lower()) ): # If the keyword isn't in result reject result
            return False
    return True



def filter_parsed_result_list(arr: list, query: str):
    filtered_data = []
    for data in arr:
        if is_match(re, query, data[0]):
            filtered_data.append(data)
    return filtered_data


def remove_non_text_tags(soup_obj):
    tags = ["script", "img", "style", "svg", "head"]
    for tag in tags:
        try:
            for tag_data in soup_obj.find_all(tag):
                tag_data.decompose()
        except:
            continue
    return soup_obj
