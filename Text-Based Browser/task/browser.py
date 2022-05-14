from bs4 import BeautifulSoup
from collections import deque
from colorama import Fore
import os
import re
import requests
import sys


args = sys.argv
if len(args) < 2:
    exit()
dir_name = args[1]
if not os.access(dir_name, os.W_OK):
    os.mkdir(dir_name)

previous_pages = deque()
next_pages = deque()


def get_path(file_name: str) -> str:
    return f"{dir_name}/{file_name}"


def add_http_prefix(url: str) -> str:
    return url if re.match("https?://", url) else "https://" + url


def parse_html(content):
    soup = BeautifulSoup(content, 'html.parser')
    headings = [f'h{n}' for n in range(1, 7)]
    parsing_tags = headings + ['title', 'p', 'a', 'ul', 'ol', 'li']
    output = ''
    for tag in soup.find_all(parsing_tags):
        if tag.text:
            text = tag.text
            if tag.name == 'a':
                text += Fore.BLUE + text + Fore.RESET
            output += text + '\n'
    return output


def trim_filename(_url: str) -> str:
    result = _url
    dot_position = _url.rfind('.')
    if dot_position != -1:
        result = result[:dot_position]
    if re.match("https?://", result):
        result = result[result.find('//') + 2:]
    return result


def open_url(url: str) -> str:
    url = add_http_prefix(url)
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return "Incorrect URL"
    if response:
        file_name = trim_filename(url)
        parsed_page = parse_html(response.content)
        save_to_file(file_name, parsed_page)
        previous_pages.append(file_name)
        return parsed_page
    else:
        return f"Error {response.status_code}"


def load_previous_page():
    if previous_pages:
        next_pages.append(previous_pages.pop())
        return load_from_cache(previous_pages[-1])


def load_from_cache(name: str) -> str:
    with open(get_path(name), 'r', encoding='UTF-8') as file:
        output = file.read()
    previous_pages.append(name)
    return output


def save_to_file(file_name: str, content: str):
    with open(get_path(file_name), 'w', encoding='UTF-8') as file:
        file.write(content)


def process_input(user_input: str):
    if user_input == "exit":
        exit()
    elif user_input == "back":
        print(load_previous_page())
    elif os.access(get_path(user_input), os.R_OK):
        print(load_from_cache(user_input))
    else:
        print(open_url(user_input))


while True:
    process_input(input())
