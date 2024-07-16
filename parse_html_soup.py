import re


def is_match(re_module, text1: str, text2: str):
    """Compare to the first text to the second one by checking if all the keywords are in the second text"""
    words = re_module.findall(r"\w*", text1)
    for word in words:
        if len(word) <= 1:
            continue
        if not (word.lower() in text2.lower()):
            return False
    return True


def filter_parsed_result_list(re, arr: list, query: str):
    filtered_data = []
    for data in arr:
        if is_match(re, query, data[0]):
            filtered_data.append(data)
    return filtered_data


def remove_non_text_tags(soup_obj):
    tags = ["script", "img", "style", "svg"]
    for tag in tags:
        try:
            for tag_data in soup_obj.find_all(tag):
                tag_data.decompose()
        except:
            continue
    return soup_obj
