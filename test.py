import requests
import json
import random
from bs4 import BeautifulSoup

# URL에서 HTML 가져오기
url = 'https://raw.githubusercontent.com/koko8829/chm_TEST/main/2663%5CENG%5CComponents_Component_Calendar.html'
response = requests.get(url)
html = response.text

soup = BeautifulSoup(html, 'html.parser')

# (공통 함수) 설명 텍스트 가져오기 
# Object > Description
# Object > Remark
def get_desc_text(soup, title):
    desc_title_td = soup.find('td', class_='sub_title', string=title)
    if not desc_title_td:
        raise ValueError(f"{title}을 포함한 요소를 찾을 수 없습니다.")
        
    desc_content_td = desc_title_td.find_next('td', class_='list')
    if desc_content_td and desc_content_td.pre:
        desc_text = desc_content_td.pre.get_text().strip()
    else:
        print(f"{title} 본문 텍스트를 포함한 요소를 찾을 수 없습니다.")
    
    return desc_text

# (공통 함수) 제목, 표 형식 가져오기 
# Object > Contents Sizing
# Object > Basic Key Action
# Object > Accessibility Key Action
# Object > Constructor
def get_table_content(soup, title, layout, bTitle=None):
    content_title_td = soup.find('td', class_='sub_title', string=title)
    if not content_title_td:
        raise ValueError(f"{title}을 포함한 요소를 찾을 수 없습니다.")

    if title=="Constructor":
        content_tds = content_title_td.find_next('td', class_='list').find_all_next('td', class_='list')
    else:
        content_tds = content_title_td.find_all_next('td', class_='list')

    for index, content_td in enumerate(content_tds):
        if (content_td.find_previous('td', class_='sub_title').get_text() != title):
            break

        if content_td and content_td.find_next().name=='pre':
            add_element("u_09_"+str(random.random()), "pre", content_td.pre.get_text().strip())
        elif content_td and content_td.find_next().name=='table':
            
            # 속성 제거
            for tag in content_td.find_all():
                attrs_to_remove = [attr for attr in tag.attrs if attr != 'colspan']
                for attr in attrs_to_remove:
                    del tag[attr]

            table_tag = content_td.find('table')  

            # colgroup 태그 삭제
            for colgroup in table_tag.find_all('colgroup'):
                colgroup.decompose()

            bTitleSkip = True

            if bTitle:
                thead_tag = soup.new_tag('thead')
                first_tr_tag = table_tag.find('tr')
                first_tr_tag.wrap(thead_tag)
                bTitleSkip = None
                bTitle = None

                for td_tag in first_tr_tag.find_all('td'):
                    th_tag = soup.new_tag('th')
                    th_tag.string = td_tag.string
                    if td_tag.get('colspan'):
                        th_tag['colspan'] = td_tag.get('colspan')
                    td_tag.replace_with(th_tag)

            tbody_tag = soup.new_tag('tbody')
            caption_tag = soup.new_tag('caption')

            for tr_tag in table_tag.find_all('tr'):
                if(bTitleSkip):
                    tr_tag.wrap(tbody_tag)
                else:
                    bTitleSkip = True

            table_tag.insert(0, caption_tag)

            # 태그 사이의 공백과 줄바꿈 제거
            for pre_tag in table_tag.find_all('pre'):
                pre_tag.string = pre_tag.text.strip()

            for pre_tag in table_tag.find_all('pre'):
                div_tag = soup.new_tag('div')
                div_tag.string = pre_tag.string
                pre_tag.replace_with(div_tag)

            # Constructor 예외 - 특정 문자열 삭제, class 속성 추가
            target_string = "Sample Call:<br/>"
            if title == "Constructor":
                for td_tag in table_tag.find_all('td'):
                    if target_string in ''.join(map(str, td_tag.contents)):
                        td_tag.contents[0].replace_with("")
                        td_tag.contents[1].replace_with("")
                        td_tag['class'] = "code_cell"

                if index == 2:
                    table_tag.find('td')['class'] = "code_cell"
                    layout = "100%"

            # div 태그를 제외한 나머지 결과물에서 줄바꿈(\n) 삭제
            for element in table_tag.find_all(string=True):
                if element.parent.name != "div":
                    element.replace_with(element.replace("\n", ""))

            add_element("u_10_"+str(random.random()), "table", str(table_tag), get_table_option(layout))            
        else:
            print(f"{title} 본문 텍스트, 표를 포함한 요소를 찾을 수 없습니다.")

# 속성 목록 처리
def set_property_list(soup, title="Property"):
    content_title_td = soup.find('td', class_='sub_title', string=title)
    if not content_title_td:
        raise ValueError(f"{title}을 포함한 요소를 찾을 수 없습니다.")
    
    table_tag = content_title_td.find_next('table')
    property_list = [a_tag.string for a_tag in table_tag.find_all('a')]
    for property in property_list:
        add_element("u_16"+property, "heading3", property)

# 메서드 목록 처리
def set_method_list(soup, title="Method"):
    content_title_td = soup.find('td', class_='sub_title', string=title)
    if not content_title_td:
        raise ValueError(f"{title}을 포함한 요소를 찾을 수 없습니다.")
    
    table_tag = content_title_td.find_next('table')
    method_list = [a_tag.string for a_tag in table_tag.find_all('a')]
    for method in method_list:
        add_element("u_16"+method, "heading3", method)

# 이벤트 목록 처리
def set_event_list(soup, title="Event"):
    content_title_td = soup.find('td', class_='sub_title', string=title)
    if not content_title_td:
        raise ValueError(f"{title}을 포함한 요소를 찾을 수 없습니다.")
    
    table_tag = content_title_td.find_next('table')
    event_list = [a_tag.string for a_tag in table_tag.find_all('a')]
    for event in event_list:
        add_element("u_16"+event, "heading3", event)        

# (공통 함수) Structure 이미지 파일명 가져오기
# Object > Structure
def get_structure_img(soup):
    structure_title_td = soup.find('td', class_='sub_title', string='Structure')
    if not structure_title_td:
        raise ValueError("Structure를 포함한 요소를 찾을 수 없습니다.")
        
    structure_content_td = structure_title_td.find_next('td', class_='list')
    if structure_content_td and structure_content_td.pre:
        structure_img = structure_content_td.pre.find('img')['src'].split('/')[-1]
    else:
        print("Structure 이미지를 포함한 요소를 찾을 수 없습니다.")
    
    return f"<img src='https://github.com/koko8829/chm_TEST/blob/main/2663%5C{structure_img}?raw=true'/>"

# (공통 함수) Supported Environments 표 생성
# Object > Supported Environments
def get_support_table(soup):
    support_icon = []
    env_keywords = ["Windows", "macOS", "Edge", "Chrome", "Safari", "Firefox", "Opera", "Android", "iOS/iPadOS", "Android", "iOS/iPadOS"]

    support_title_td = soup.find('td', class_='sub_title', string='Supported Environments')    
    if not support_title_td:
        raise ValueError("Supported Environments 타이틀을 찾을 수 없습니다.")
    
    for env_keyword in env_keywords:
        if support_title_td:
            keyword_td = support_title_td.find_next('td', string=env_keyword)
            if keyword_td:
                img_src = keyword_td.find_previous_sibling('td').find('img')['src']
                if img_src == "../../support01.gif":
                    support_icon.append("■");
                else:
                    support_icon.append("▢");
                
            else:
                print(f"{env_keyword} 환경이 지원되지 않습니다.")


    return "<table class='table column_count_7'><caption></caption><thead><tr><th colspan='2'><div>Desktop NRE</div></th><th colspan='5'><div>Desktop WRE</div></th></tr></thead><tbody><tr><td><div>"+support_icon[0]+" Windows</div></td><td><div>"+support_icon[1]+" macOS</div></td><td><div>"+support_icon[2]+" Edge</div></td><td><div>"+support_icon[3]+" Chrome</div></td><td><div>"+support_icon[4]+" Safari</div></td><td><div>"+support_icon[5]+" Firefox</div></td><td><div>"+support_icon[6]+" Opera</div></td></tr><tr><th colspan='2'><div>Mobile NRE</div></th><th colspan='5'><div>Mobile WRE</div></th></tr><tr><td><div>"+support_icon[7]+" Android</div></td><td><div>"+support_icon[8]+" iOS/iPadOS</div></td><td><div>"+support_icon[9]+" Android</div></td><td><div>"+support_icon[10]+" iOS/iPadOS</div></td><td><div></div></td><td><div></div></td><td><div></div></td></tr></tbody></table>"

# (공통 함수) 표 config
# Object > Supported Environments (110,110,110,110,110,110,110)
def get_table_option(layout="110,110,110,110,110,110,110"):
    return {
        "table_layout": "user",
        "codeLanguage": "Javascript",
        "table_layout_setting": layout
    }


# JSON 파일 생성
elements = []

def add_element(id, type, content, option=None):
    element = {
        "id": id,
        "type": type,
        "content": content
    }
    if option is not None:
        element["option"] = option
    elements.append(element)    

add_element("u_01", "heading1", "개요")
add_element("u_02", "pre", get_desc_text(soup, "Description"))
add_element("u_03", "heading2", "지원 환경")
add_element("u_04", "table", get_support_table(soup), get_table_option())
add_element("u_05", "pre", get_desc_text(soup, "Remark"))
add_element("u_06", "heading2", "컴포넌트 구조")
add_element("u_07", "normal", get_structure_img(soup))
add_element("u_08", "heading2", "컴포넌트, 내부 컨텐츠 크기")
get_table_content(soup, "Contents Sizing", "120,?")
add_element("u_11", "heading2", "Basic Key Action")
get_table_content(soup, "Basic Key Action", "120,120,?", True)
add_element("u_12", "heading2", "Accessibility Key Action")
get_table_content(soup, "Accessibility Key Action", "120,120,?", True)
add_element("u_13", "heading2", "생성자")
get_table_content(soup, "Constructor", "120,120,?", True)
add_element("u_14", "heading2", "Status")
get_table_content(soup, "Status", "120,120,?", True)
add_element("u_15", "heading2", "Control")
get_table_content(soup, "Control", "120,120,?", True)
add_element("u_16", "heading2", "속성")
set_property_list(soup)
add_element("u_17", "heading2", "메서드")
set_method_list(soup)
add_element("u_18", "heading2", "이벤트")
set_event_list(soup)

data = {
    "elements": elements
}

# JSON 파일로 저장
with open('result.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=2)    

print("JSON 파일이 생성되었습니다.")    
