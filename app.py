import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import json
import pandas as pd
#import asyncio
import random
import time

# 씨앗 생성 서버 url
url_generate_seeds = "http://43.201.106.200"

# 씨앗 정보 저장소
initial_seeds_array = []#[{'id': '751364', 'date': '208978', 'image_status': '544091'}, {'id': '52790', 'date': '777259', 'image_status': '110512'}, {'id': '384410', 'date': '914923', 'image_status': '869746'}]

if "seeds" not in st.session_state:
    st.session_state.seeds = initial_seeds_array

#---------------------------------------------------------------------------
# 타이틀
st.set_page_config(page_title="씨앗 월드", page_icon="./images/icon_seed01.jpg")
st.title("씨앗 월드")

#---------------------------------------------------------------------------
#if st.button("씨앗 생성 - local"):
    # 빈 딕셔너리 생성
#    data_dict = {"id": "", "date": "", "image_status": ""}
    # 각 키에 대해 랜덤 정수를 생성하고 문자열로 변환하여 추가
#    for key in data_dict:
#        random_int = random.randint(1, 1000000)  # 1부터 1,000,000 사이의 랜덤 정수 생성
#        data_dict[key] = str(random_int)  # 정수를 문자열로 변환하여 딕셔너리에 추가
    # 결과 출력
#    print(data_dict)

    # 씨앗 메타데이터 값을 취득한다.
#    st.session_state.seeds.append(data_dict)  
#    st.write(len(st.session_state.seeds)) 

#---------------------------------------------------------------------------
if st.button("씨앗 생성"):
    try:
        # 씨앗 생성
        response = requests.get(f"{url_generate_seeds}/generate")
        
        # 응답 상태 코드 확인
        if response.status_code == 200:
            try:
                # JSON 문자열을 가져오고 파싱
                json_string = response.text
              
                # 1. 문자열 정제
                #json_string = json_string.replace('\n', '')
                # 2. 작은따옴표를 큰따옴표로 변경
                #cleaned_string = json_string.replace("'", '"')

                # json.loads() 두번 처리하면 딕셔너리로 변환 된다. 문자열 처리 다른 것 해봐도 소용없음, 걍 함수 2번 호출이 짱~
                # JSON 문자열을 딕셔너리로 변환
                data_dict = json.loads(json_string)
                data_dict = json.loads(data_dict)

                # 문자열인지 체크하는 코드
                #if isinstance(data_dict, str):
                    # data가 문자열일 경우 실행할 코드
                #    st.write("data는 문자열입니다.")
                    # 여기서 문자열을 파싱하거나 다른 처리를 수행할 수 있습니다.
                #else:
                #    st.write("data는 문자열이 아닙니다.")    
                #                 

                data_dict["image"] = ""
                # 씨앗 메타데이터 값을 취득한다.
                st.session_state.seeds.append(data_dict)
                #st.write(len(st.session_state.seeds)) 

            except SyntaxError as e:
                print(f"구문 오류 발생: {e}")
            except ValueError as e:
                print(f"값 오류 발생: {e}")
            except Exception as e:
                print(f"예상치 못한 오류 발생: {e}")
        else:
            st.error(f"(error) 상태 코드: {response.status_code}")
    
    except requests.RequestException as e:
        st.error(f"요청 중 오류 발생: {e}")
    except IOError:
        st.error("유효한 이미지 URL인지 확인해주세요.")

#---------------------------------------------------------------------------
cols = st.columns(2)
for i in range(len(st.session_state.seeds)):
    with cols[i % 2]:
        seed = st.session_state.seeds[i]
        with st.expander(label=seed["image_status"], expanded=True):
            # 딕셔너리에서 원하는 값을 추출하여 변수에 할당
            id = seed["id"]
            date = seed["date"]
            image_status = seed["image_status"]
            # DataFrame 생성
            df = pd.DataFrame({'ID':[id], '생성일':[date], '이미지 상태':[image_status]})
            # 행과 열을 바꾼 표에 열 이름 추가
            df_transposed = df.transpose().reset_index()
            # 열 이름
            df_transposed.columns = ['key', 'value']
            # CSS를 사용하여 헤더를 숨김
            hide_table_row_index = """
                <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                </style>
            """
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            st.table(df_transposed)         

            # 이미지 존재 유무 체크해서 있으면 버튼 없앰
            # 업데이트 후 자동 갱신 안되서 걍 수동 버튼 하나 만듦
            if seed["image"]:
                # 슬라이스 표시    
                select_slider = st.select_slider("성장 이미지", options=["1","2","3","4","5","6"], key=f"image_{i}")
                int_select_slider = int(select_slider) - 1
                img_x_position = 512*int_select_slider
                # 이미지 표시
                image_slice = seed["image"]
                image_slice = image_slice.crop((img_x_position, 0, img_x_position+512, 512))
                st.image(image_slice, use_column_width=True) 
            else:
                # 슬라이스 표시 : 비활성 처리 힘들어서 걍 표시     
                st.select_slider("성장 이미지", options=["1","2","3","4","5","6"], key=f"image_{i}") 
                # 디폴트 이미지 표시
                # 이미지 파일 경로
                default_image_path = "./images/image_processing.png"     
                # 이미지 열기
                default_image = Image.open(default_image_path)
                # 이미지 표시
                st.image(default_image, use_column_width=True)                  

#---------------------------------------------------------------------------
status_flag = False
for i in range(len(st.session_state.seeds)):
    if "processing" in st.session_state.seeds[i]["image_status"]:  
        status_flag = True

if status_flag == True:
    with st.status("이미지 생성 중...") as status:
        for i in range(len(st.session_state.seeds)):
            if "processing" in st.session_state.seeds[i]["image_status"]:                  
                count = 0
                while True:
                    time.sleep(1)

                    try:
                        id = st.session_state.seeds[i]["id"]
                        # GET 요청으로 이미지 가져오기
                        response = requests.get(f"{url_generate_seeds}/image/{id}")
                        
                        content_type = response.headers.get('Content-Type')
                        # 응답 상태 코드 확인
                        if "image" in content_type:
                            st.write(f"이미지 생성 완료: {id}")
                            # 상태 변경
                            st.session_state.seeds[i]["image_status"] = "complete"
                            # 이미지 데이터를 PIL Image 객체로 변환
                            st.session_state.seeds[i]["image"] = Image.open(BytesIO(response.content))

                            # 데이터 갱신
                            st.rerun()
                            break
                    except requests.RequestException as e:
                        st.error(f"요청 중 오류 발생: {e}")
                    except IOError:
                        st.error("이미지를 열 수 없습니다. 유효한 이미지 URL인지 확인해주세요.")                        
                    
                    count += 1
                    if count > 120:
                        break
        status.update(label="이미지 생성 완료!", state="complete", expanded=False)    

#---------------------------------------------------------------------------
# 버튼 클릭 이벤트 핸들러
#async def check_status():
#    url = "https://example.com/api"  # API 엔드포인트
#    st.write("요청을 시작합니다...")

#    while True:
#        response = requests.get(url)
#        st.write(f"응답 상태 코드: {response.status_code}")
        
#        if response.status_code == 200:
#            st.write("요청이 완료되었습니다!")
#            break
        
#        await asyncio.sleep(1)
#---------------------------------------------------------------------------
#if st.button("쓰레드 시작"):
#    asyncio.run(check_status())

#---------------------------------------------------------------------------
#if st.button("씨앗 이미지"):
#    try:
        # GET 요청으로 이미지 가져오기
#        response = requests.get("https://fastly.picsum.photos/id/0/5000/3333.jpg?hmac=_j6ghY5fCfSD6tvtcV74zXivkJSPIfR9B8w34XeQmvU")
        
        # 응답 상태 코드 확인
#        if response.status_code == 200:
            # 이미지 데이터를 PIL Image 객체로 변환
#            image = Image.open(BytesIO(response.content))
            
            # 이미지 표시
#            st.image(image, caption="가져온 이미지", use_column_width=True)
            
            # 추가 정보 표시
#            st.write(f"이미지 크기: {image.size}")
#            st.write(f"이미지 형식: {image.format}")
#        else:
#            st.error(f"이미지를 가져올 수 없습니다. 상태 코드: {response.status_code}")
    
#    except requests.RequestException as e:
#        st.error(f"요청 중 오류 발생: {e}")
#    except IOError:
#        st.error("이미지를 열 수 없습니다. 유효한 이미지 URL인지 확인해주세요.")              