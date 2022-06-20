import random
import sqlite3
import json
import requests
import re

# Define the INIT state
INIT = 0
# Define the CHOOSE_COFFEE state
CHOOSE_city = 1
# Define the ORDERED state
finished = 2

policy = {
    (INIT, "none"): (INIT, "你好，欢迎使用我们的软件，请输入你的城市 "),
    (INIT, "wrong"): (INIT, " 对不起，请输入有效字符"),
    (CHOOSE_city, "specify_city"): (CHOOSE_city, "欢迎"),
}


def interpret(message):
    response = requests.get(
        'https://api.map.baidu.com/place/v2/search?query=' + (message) + '&tag=' + (message) + '&region=' + (
            message) + '&output=json&ak=Xr4riipOhrvWzKq3rItcolwrUPHpsOGV')
    msg = message.lower()
    a = re.search(r"(hello|hey|hi|你好)", message)
    if (a != None):
        return "none"
    if len(response.json()['results']) == 0:
        return 'wrong'
    if response.json()['results'][0]['name'].strip('市') not in msg:
        return 'wrong'
    if response.json()['results'][0]['name'].strip('市') in msg:
        return 'specity_city'


def respond(state, message):
    new_state, response = policy[(state, interpret(message))]
    return new_state, response


responses = [
    "对不起，我们未能找到符合你条件的地点",
    '{} 是一个好的选择!',
    '{}怎么样？',
    '{} 是其中一个选择, 但是我还有其他可供你选择 :)'
]


def send_message(city, purpose):
    # Fill the dictionary with entities
    # Select the nth element of the responses array
    # Find hotels that match the dictionary
    response = requests.get(
        'https://api.map.baidu.com/place/v2/search?query=' + (purpose) + '&tag=' + (purpose) + '&region=' + (
            city) + '&output=json&ak=Xr4riipOhrvWzKq3rItcolwrUPHpsOGV')
    results = response.json()['results']
    placelist = {}
    for l in response.json()['results']:
        if (l.__contains__('telephone') == False):
            l['telephone'] = '0'
        placelist[l['name']] = l['name'], l['area'], l['address'], l['telephone']
    # Get the names of the hotels and index of the response
    names = [r['name'] for r in results]
    n = min(len(names), 3)
    # Select the nth element of the responses array
    return responses[n].format(*names), names[0], placelist, names


def output(city, purpose):
    response = requests.get(
        'https://api.map.baidu.com/place/v2/search?query=' + (purpose) + '&tag=' + (purpose) + '&region=' + (
            city) + '&output=json&ak=Xr4riipOhrvWzKq3rItcolwrUPHpsOGV')
    results = response.json()['results']


def second(question, name, placelist, namelist):
    responses = [
        "对不起，我们未能找到符合你条件的地点",
        '{} 是一个好的选择!',
        '{}怎么样？',
        '{} 是其中一个选择, 但是我还有其他可供你选择 :)'
    ]
    responses1 = {'question': [
        "这个地点的区是 {0}".format(placelist[name][1]),
        '{0}'.format(placelist[name][1]),
        "区域是 {0}".format(placelist[name][1]),
    ]}
    responses2 = {'question': [
        "电话号码 {0}".format(placelist[name][3]),
        "好的电话号码是 {0}".format(placelist[name][3])
    ]}

    responses3 = {'question': [
        "对不起，我没有找到",
        " 很抱歉，这个地点没有电话号码"
    ]}
    responses4 = {'question': [
        "地址是 {0}".format(placelist[name][2]),
        '{0}'.format(placelist[name][2]),
        "这个地点是{0}".format(placelist[name][2]),
    ]}

    if "区域" in question or "哪个区" in question:
        return random.choices(responses1['question']), placelist, name

    if "手机号" in question or "电话号" in question:
        if (placelist[name][3] == 0):
            return random.choices(responses3['question']), placelist, name
        else:
            return random.choices(responses2['question']), placelist, name

    if '在哪' in question or '地址' in question:
        return random.choices(responses4['question']), placelist, name

    if "不喜欢" in question or "换一个" in question or "讨厌" in question:
        namelist.pop(0)
        placelist.pop(name)
        n = min(len(placelist), 3)
        return responses[n].format(*namelist), placelist, namelist[0]
    if "好的" in question or "谢谢" in question:
        return "end", placelist, name

    if '换城市' in question:
        return "back", placelist, name

    if '其他地点' in question or "换" in question:
        return "changeplace", placelist, name

    else:
        return "对不起，我不明白你的意思", placelist, name


def main():
    state = INIT;
    first = input()
    while (interpret(first) != 'specity_city'):
        newstate, response = respond(state, first)
        print(response)
        state = newstate
        first = input()
    city = first

    print("请告诉我你想找什么地点")
    restaurant = input()
    answer, names, place, namelist = send_message(city, restaurant)
    print(answer)
    question = input()
    answer1, newplace1, newname = second(question, names, place, namelist)
    print(answer1)
    while (answer1 != "end"):
        question = input()
        newplace = newplace1
        answer1, newplace1, newname = second(question, newname, newplace, namelist)
        print(answer1)
        if (answer1) == 'back':
            print("好的，请问你想切换哪个城市")
            state = INIT;
            first = input()
            while (interpret(first) != 'specity_city'):
                ewstate, response = respond(state, first)
                print(response)
                state = newstate
                first = input()
            city = first
            answer, names, place, namelist = send_message(city, restaurant)
            print(answer)
            answer1, newplace1, newname = second(question, names, place, namelist)
        if (answer1 == 'changeplace'):
            print("好的，请告诉我你想去哪")
            restaurant = input()
            answer, names, place, namelist = send_message(city, restaurant)
            print(answer)
            answer1, newplace1, newname = second(question, names, place, namelist)


if __name__ == '__main__':
    main()