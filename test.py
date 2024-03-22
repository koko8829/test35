import requests
import json
import random
from bs4 import BeautifulSoup

# URL에서 HTML 가져오기
url_github = 'https://raw.githubusercontent.com/koko8829/chm_TEST/main/'
module_name = "Calendar"
url_object = f'{url_github}Components_Component_{module_name}.html'
response = requests.get(url_object)
html = response.text

soup = BeautifulSoup(html, 'html.parser')

# (공통 함수) 설명 텍스트 가져오기 
# Object > Description
# Object > Remark
def get_desc_text(soup, title, item=None):
    desc_title_td = soup.find('td', class_='sub_title', string=title)
    if not desc_title_td:
        raise ValueError(f"{title}을 포함한 요소를 찾을 수 없습니다. 참고 {item}")
        
    desc_content_td = desc_title_td.find_next('td', class_='list')
    if desc_content_td and desc_content_td.pre:
        desc_text = desc_content_td.pre.get_text().strip()
        desc_text = get_html_text(desc_text)
    else:
        print(f"{title} 본문 텍스트를 포함한 요소를 찾을 수 없습니다. 참고 {item}")
    
    return desc_text

# (공통 함수) 제목, 표 형식 가져오기 
# Object > Contents Sizing
# Object > Basic Key Action
# Object > Accessibility Key Action
# Object > Constructor
# Property > Setting Syntax
# Method > Parameters
# Method > Return
def get_table_content(soup, title, layout, bTitle=None, item=None):
    content_title_td = soup.find('td', class_='sub_title', string=title)
    if not content_title_td:
        raise ValueError(f"{title}을 포함한 요소를 찾을 수 없습니다. 참고 {item}")

    if title=="Constructor":
        content_tds = content_title_td.find_next('td', class_='list').find_all_next('td', class_='list')
    else:
        content_tds = content_title_td.find_all_next('td', class_='list')

    for index, content_td in enumerate(content_tds):
        if (content_td.find_previous('td', class_='sub_title').get_text() != title):
            break
        
        # {title} 설명 텍스트만 있는 경우
        if content_td and content_td.find_next().name=='pre':
            if title=="Constructor":
                content_type = "command"
            else:
                content_type = "pre"
            add_element("u_09_"+str(random.random()), content_type, content_td.pre.get_text().strip())
        # {title} 샘플만 있는 경우
        # 속성 Parameters 항목 중 bringToFront() 처럼 값이 없지만 샘플 설명이 있는 경우
        elif content_td and content_td.find_next().name == 'br':
            add_element("u_09_"+str(random.random()), "command", content_td.find_next().find_next().get_text().strip())
        # {title} 관련 표가 있는 경우 
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
            if title == "Constructor" or title == "Parameters":
                for td_tag in table_tag.find_all('td'):
                    if target_string in ''.join(map(str, td_tag.contents)):
                        td_tag.contents[0].replace_with("")
                        td_tag.contents[1].replace_with("")
                        td_tag['class'] = "code_cell"

                if index == 2:
                    table_tag.find('td')['class'] = "code_cell"
                    layout = "100%"
            
            # Setting Syntax 예외 - colspan=3이 있으면 code_cell, 없으면 th
            if title == "Setting Syntax":
                for td_tag in table_tag.find_all('td'):
                    if 'colspan' in td_tag.attrs and td_tag.attrs['colspan'] == '3':
                        td_tag['class'] = 'code_cell'
                    elif 'colspan' not in td_tag.attrs:
                        th_tag = soup.new_tag('th')
                        th_tag.string = td_tag.string
                        td_tag.replace_with(th_tag)          

            # div 태그를 제외한 나머지 결과물에서 줄바꿈(\n) 삭제
            for element in table_tag.find_all(string=True):
                if element.parent.name != "div":
                    element.replace_with(element.replace("\n", ""))

            add_element("u_10_"+str(random.random()), "table", str(table_tag), get_table_option(layout))            
        else:
            print(f"{title} 본문 텍스트, 표를 포함한 요소를 찾을 수 없습니다. 참고 {item}")

# 속성, 메서드, 이벤트 목록 처리
def set_item_list(soup, title="Property"):
    content_title_td = soup.find('td', class_='sub_title', string=title)
    if not content_title_td:
        raise ValueError(f"{title}을 포함한 요소를 찾을 수 없습니다.")
    
    table_tag = content_title_td.find_next('table')
    item_list = [a_tag.string for a_tag in table_tag.find_all('a')]
    for item in item_list:
        if title=="Property":
            set_property_data(item)
        elif title=="Method":
            set_method_data(item)
        elif title=="Event":
            set_event_data(item)

# 속성 데이터 처리
def set_property_data(property):
    property_url = f"{url_github}Components_Component_{module_name}_Property_{property}.html"
    property_response = requests.get(property_url)
    property_html = property_response.text
    property_soup = BeautifulSoup(property_html, 'html.parser')

    add_element(f"p_01_{property}", "heading2", property, get_alias_option(module_name, property))
    add_element(f"p_02_{property}", "pre", get_desc_text(property_soup, "Description"))
    add_element(f"p_03_{property}", "headline", "지원 환경")
    add_element(f"p_04_{property}", "table", get_support_table(property_soup), get_table_option())
    add_element(f"p_05_{property}", "headline", "속성 타입")
    add_element(f"p_06_{property}", "table", get_property_type_table(property_soup), get_table_option('80,70,90,90,110,80,110,140'))
    add_element(f"p_07_{property}", "headline", "문법")
    add_element(f"p_08_{property}", "command", get_desc_text(property_soup, "Syntax"))
    if property_soup.find('td', class_='sub_title', string="Setting Syntax"):
        add_element(f"p_09_{property}", "headline", "문법 설정")
        get_table_content(property_soup, "Setting Syntax", "180,120,?", None, property)  

    if property_soup.find('td', class_='sub_title', string="Remark"):
        add_element(f"p_11_{property}", "headline", "참고")
        add_element(f"p_12_{property}", "pre", get_desc_text(property_soup, "Remark", property))       

# 메서드 데이터 처리
def set_method_data(method):
    method_url = f"{url_github}Components_Component_{module_name}_Method_{method}.html"
    method_response = requests.get(method_url)
    method_html = method_response.text
    method_soup = BeautifulSoup(method_html, 'html.parser')

    add_element("m_01"+method, "heading2", method, get_alias_option(module_name, method))
    add_element(f"m_02_{method}", "pre", get_desc_text(method_soup, "Description"))
    add_element(f"m_03_{method}", "headline", "지원 환경")
    add_element(f"m_04_{method}", "table", get_support_table(method_soup), get_table_option()) 
    add_element(f"m_05_{method}", "headline", "문법")
    add_element(f"m_06_{method}", "command", get_desc_text(method_soup, "Syntax"))    
    add_element(f"m_07_{method}", "headline", "파라미터")
    get_table_content(method_soup, "Parameters", "180,120,?", True, method) 

    if method_soup.find('td', class_='sub_title', string="Return"):
        # Return 항목이 없는 경우 "없음"으로 자동 기재되어 있어 해당 건 예외 처리
        content_title_td = method_soup.find('td', class_='sub_title', string="Return")
        content_td = content_title_td.find_next('td', class_='list')
        if content_td.text.strip() != "없음":
            add_element(f"m_08_{method}", "headline", "반환")
            get_table_content(method_soup, "Return", "180,?", True, method)  

    if method_soup.find('td', class_='sub_title', string="Remark"):
        add_element(f"m_09_{method}", "headline", "참고")
        add_element(f"m_10_{method}", "pre", get_desc_text(method_soup, "Remark", method))        

# 속성 데이터 처리
def set_event_data(event):
    add_element("e_16"+event, "heading3", event)        


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
    
    return f"<img src='{url_github}2663%5C{structure_img}?raw=true'/>"

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

# (공통 함수) Property Type 표 생성
# Object > Property > Property Type
def get_property_type_table(soup):
    support_icon = []
    env_keywords = ["Enum", "Expr", "Control", "Hidden", "ReadOnly", "Bind", "Collection", "StringResource"]

    property_type_title_td = soup.find('td', class_='sub_title', string='Property Type')    
    if not property_type_title_td:
        raise ValueError("Property Type 타이틀을 찾을 수 없습니다.")
    
    property_type_table_td = property_type_title_td.find_next('td', class_='list')
    td_keywords = property_type_table_td.find_all('input')
    for td_keyword in td_keywords:
        if td_keyword.get('checked'):
            support_icon.append("■");
        else:
            support_icon.append("▢");
                

    return f"<table class='r_no_border_table column_count_8'><caption></caption><tbody><tr><td><div>{support_icon[0]} {env_keywords[0]}</div></td><td><div>{support_icon[1]} {env_keywords[1]}</div></td><td><div>{support_icon[2]} {env_keywords[2]}</div></td><td><div>{support_icon[3]} {env_keywords[3]}</div></td><td><div>{support_icon[4]} {env_keywords[4]}</div></td><td><div>{support_icon[5]} {env_keywords[5]}</div></td><td><div>{support_icon[6]} {env_keywords[6]}</div></td><td><div>{support_icon[7]} {env_keywords[7]}</div></td></tr></tbody></table>"

# (공통 함수) 텍스트 변환
def get_html_text(target_text):
    return target_text.replace("<", "&lt;").replace(">", "&gt;")


# (공통 함수) 표 config
# Object > Supported Environments (110,110,110,110,110,110,110)
def get_table_option(layout="110,110,110,110,110,110,110"):
    return {
        "table_layout": "user",
        "codeLanguage": "Javascript",
        "table_layout_setting": layout
    }

# (공통 함수) alias config
def get_alias_option(module, title):
    return {
        "alias": module+"_"+title
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

# Object 정보 처리
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
add_element("u_16", "heading1", "속성")
set_item_list(soup, "Property")
add_element("u_17", "heading1", "메서드")
set_item_list(soup, "Method")
add_element("u_18", "heading1", "이벤트")
set_item_list(soup, "Event")

data = {
    "elements": elements
}

# JSON 파일로 저장
with open('result.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=2)    

print("JSON 파일이 생성되었습니다.")    
