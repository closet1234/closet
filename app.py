import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import datetime
import os
import json
import base64
from streamlit_calendar import calendar

# --- 한글 폰트 (Mac)
import matplotlib
matplotlib.rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False
# ================================
# --- 경로 설정 ---
# ================================
DATA_DIR = "data"
IMG_DIR = os.path.join(DATA_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

WARDROBE_FILE = os.path.join(DATA_DIR, "wardrobe.csv")
CALENDAR_FILE = os.path.join(DATA_DIR, "calendar.csv")
USER_INFO_FILE = os.path.join(DATA_DIR, "user_info.json")
COMMUNITY_FILE = os.path.join(DATA_DIR, "community.json")
# ================================
# --- 세션 상태 초기화 ---
# ================================
for key in ['logged_in', 'avatar', 'user_info', 'wardrobe', 'community_posts', 'wear_calendar','logout_message']:
    if key not in st.session_state:
        if key == 'wardrobe':
            st.session_state[key] = pd.DataFrame(columns=['카테고리','색상','스타일','사이즈','이미지'])
        elif key == 'wear_calendar':
            st.session_state[key] = pd.DataFrame(columns=['날짜','카테고리','색상','스타일','사이즈'])
        elif key == 'community_posts':
            st.session_state[key] = []
        elif key == 'logout_message':
            st.session_state[key] = False
        else:
            st.session_state[key] = False if key == 'logged_in' else {}
# ================================
# --- 데이터 저장 함수 ---
# ================================
def save_data():
    st.session_state.wardrobe.to_csv(WARDROBE_FILE, index=False)
    st.session_state.wear_calendar.to_csv(CALENDAR_FILE, index=False)
    with open(USER_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.user_info, f, ensure_ascii=False)
    with open(COMMUNITY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.community_posts, f, ensure_ascii=False)

# ================================
# --- 데이터 로딩 함수 ---
# ================================
def load_data():
    if os.path.exists(WARDROBE_FILE):
        df = pd.read_csv(WARDROBE_FILE)
        df['이미지'] = df['이미지'].fillna('')
        st.session_state.wardrobe = df

    if os.path.exists(CALENDAR_FILE):
        st.session_state.wear_calendar = pd.read_csv(CALENDAR_FILE)

    if os.path.exists(USER_INFO_FILE):
        with open(USER_INFO_FILE, encoding="utf-8") as f:
            st.session_state.user_info = json.load(f)

    if os.path.exists(COMMUNITY_FILE):
        with open(COMMUNITY_FILE, encoding="utf-8") as f:
            st.session_state.community_posts = json.load(f)
# ================================
# --- 상단 헤더 + 내 캐릭터 프로필 이미지 ---
# ================================
def get_image_base64(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode()

# 1️⃣ 헤더 + 자리 만드는 HTML
st.markdown(
    """
    <style>
    .main-header {
        position: relative;
        background-color: #e0e0e0;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: black;
        font-size: 36px;
        margin-bottom: 5px;
        font-weight: bold;
    }
    .main-header p {
        color: #616161;
        font-size: 16px;
        margin-top: 0;
    }
    .avatar-circle {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #ccc;
    }
    </style>
    <div class="main-header">
        <h1>🧣CLOSET</h1>
        <p>나만의 옷장</p>
    </div>
    """,
    unsafe_allow_html=True
)

# 2️⃣ 내 캐릭터 이미지가 있으면 바로 위쪽 헤더에 띄우기
if st.session_state.avatar and st.session_state.avatar.get('image') is not None:
    img_base64 = get_image_base64(st.session_state.avatar['image'])
    st.markdown(
        f"""
        <img src="data:image/png;base64,{img_base64}" class="avatar-circle">
        """,
        unsafe_allow_html=True
    )
# ================================
# --- 사이드바 ---
# ================================
st.sidebar.title("🧣CLOSET")

# ✅ 내 캐릭터 프로필

try:
    logo_image = Image.open("logo.JPG")
    st.sidebar.image(logo_image, caption="CLOSET", use_container_width=True)
except:
    st.sidebar.warning("⚠️ 로고 이미지를 불러올 수 없습니다.")

if st.session_state.logged_in:
    menu = st.sidebar.radio(
        "✨ 메뉴를 선택하세요",
        [
            "🏠 홈",
            "🧸 캐릭터 생성",
            "📝 사용자 정보",
            "👗 내 옷장",
            "📊 색상/스타일 분석",
            "🌤️ 오늘 날씨 코디 추천",
            "📅 착장 캘린더",
            "💬 의류 커뮤니티"
        ]
    )
else:
    menu = "로그인"
# ================================
# --- 로그인 화면 ---
# ================================
if not st.session_state.logged_in and menu == "로그인":
    st.subheader("🔐 로그인")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        if username == "closet" and password == "1234":
            st.session_state.logged_in = True
            load_data()
            st.success("✅ 로그인 성공!")
            st.rerun()
        else:
            st.error("❌ 아이디 또는 비밀번호 오류")
if st.session_state.logout_message:
    st.success("🩷 이용해주셔서 감사합니다! 다음에 또 만나요!")
    st.session_state.logout_message = False
# ================================
# --- 로그아웃 버튼 ---
# ================================
if st.session_state.logged_in:
    with st.sidebar:
        if st.button("로그아웃", key="logout_button"):
            save_data()
            st.session_state.logged_in = False
            st.session_state.logout_message= True
            st.rerun()

        if st.button("데이터 저장", key="save_and_exit_button"):
            save_data()
            st.success("✅ 데이터가 저장되었습니다!")

# ================================
# --- 각 메뉴별 화면 ---
# ================================
if st.session_state.logged_in:
    if menu == "🏠 홈":
        st.title("🧣CLOSET")
        st.markdown("""
        - 나만의 옷장 관리
        - 오늘 날씨 맞춤 코디 추천
        - 색상/스타일 분석
        - 착장 캘린더
        - 커뮤니티
        """)
    elif menu == "🧸 캐릭터 생성":
        st.header("🧸 캐릭터 생성")
        with st.form("avatar_form"):
            nickname = st.text_input("닉네임")
            style = st.text_input("스타일")
            color = st.text_input("좋아하는 색상")
            image = st.file_uploader("아바타 이미지", type=["png","jpg","jpeg"])
            submitted = st.form_submit_button("저장하기")
            if submitted:
                st.session_state.avatar = {
                    "nickname": nickname,
                    "style": style,
                    "color": color,
                    "image": image
                }
                st.success("✅ 캐릭터 정보가 저장되었습니다!")
        if st.session_state.avatar:
            st.subheader("✨ 내 캐릭터 정보")
            st.write(f"닉네임: {st.session_state.avatar.get('nickname','')}")
            st.write(f"스타일: {st.session_state.avatar.get('style','')}")
            st.write(f"좋아하는 색상: {st.session_state.avatar.get('color','')}")
            if st.session_state.avatar.get('image') is not None:
                st.image(st.session_state.avatar['image'], use_container_width=True)
    elif menu == "📝 사용자 정보":
        st.header("📝 사용자 정보 입력")
        with st.form("user_info_form"):
            gender = st.text_input("성별")
            height = st.text_input("키(cm)")
            weight = st.text_input("몸무게(kg)")
            body_type = st.text_input("체형")
            favorite_brand = st.text_input("좋아하는 브랜드")
            submitted = st.form_submit_button("저장")
            
 
        if submitted:
            st.session_state.user_info = {
                "gender": gender,
                "height": height,
                "weight": weight,
                "body_type": body_type,
                "favorite_brand": favorite_brand,
         
            }
    
        if st.session_state.user_info:
            st.subheader("✅ 현재 사용자 정보")
            st.json(st.session_state.user_info)
        else:
            st.info("ℹ️ 사용자 정보가 아직 입력되지 않았습니다.")
    elif menu == "👗 내 옷장":
        st.header("👗 내 옷장")

        with st.form("add_clothes_form"):
            category = st.text_input("카테고리")
            color = st.text_input("색상")
            style = st.text_input("스타일")
            size = st.text_input("사이즈")

            image_file = st.file_uploader("옷 사진 추가", type=["jpg","jpeg","png"])
            submitted2 = st.form_submit_button("옷장에 추가")

        if submitted2:
            img_path = ""
            if image_file:
                img_filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.name}"
                img_path = os.path.join(IMG_DIR, img_filename)
                with open(img_path, "wb") as f:
                    f.write(image_file.getvalue())

            new_item = pd.DataFrame({
                '카테고리':[category],
                '색상':[color],
                '스타일':[style],
                '사이즈':[size],
                '이미지':[img_path]
            })
            st.session_state.wardrobe = pd.concat([st.session_state.wardrobe, new_item], ignore_index=True)
            st.success("✅ 옷장이 업데이트 되었습니다!")

        if st.session_state.wardrobe.empty:
            st.info("아직 옷장이 비어 있어요. 옷을 추가해 보세요!")
        else:
            st.subheader("내 옷장 아이템")
            for idx, row in st.session_state.wardrobe.iterrows():
                st.markdown(f"**{idx+1}. {row['카테고리']} - {row['스타일']} - {row['색상']} - {row['사이즈']}**")
                if row['이미지'] and os.path.exists(row['이미지']):
                    st.image(row['이미지'], width=200)
                st.markdown("---")
    elif menu == "📊 색상/스타일 분석":
        st.header("📊 내 옷장 색상/스타일 분석")
        if st.session_state.wardrobe.empty:
            st.info("아직 옷장이 비어 있어요. 옷을 추가해 보세요!")
        else:
            color_counts = st.session_state.wardrobe['색상'].value_counts()
            style_counts = st.session_state.wardrobe['스타일'].value_counts()

            st.subheader("✅ 색상 분포")
            fig1, ax1 = plt.subplots()
            color_counts.plot(kind='bar', ax=ax1)
            st.pyplot(fig1)

            st.subheader("✅ 스타일 분포")
            fig2, ax2 = plt.subplots()
            style_counts.plot(kind='bar', ax=ax2)
            st.pyplot(fig2)
    elif menu == "🌤️ 오늘 날씨 코디 추천":
        st.header("🌤️ 오늘 날씨 맞춤 코디 추천")
        if st.session_state.wardrobe.empty:
            st.info("✅ 옷장이 비어 있어요. 먼저 옷을 등록해 주세요!")
        else:
            weather = st.text_input("오늘 날씨를 입력해주세요 (예: 맑음, 비, 추움, 더움)")
            if weather:
                st.subheader("✅ 오늘 날씨 기반 추천")
                weather = weather.lower()
                recommendations = st.session_state.wardrobe.copy()

                if "비" in weather:
                    recommendations = recommendations[
                        (recommendations['카테고리'] == '아우터') | (recommendations['색상'].isin(['검정', '네이비']))
                    ]
                    st.info("☔️ 비 오는 날엔 어두운 색 아우터를 추천합니다!")
                elif "추움" in weather:
                    recommendations = recommendations[
                        (recommendations['카테고리'].isin(['아우터','상의'])) & (recommendations['스타일'] != '스포티')
                    ]
                    st.info("🧥 추운 날엔 아우터나 긴팔 상의를 추천합니다!")
                elif "더움" in weather:
                    recommendations = recommendations[
                        (recommendations['카테고리'] == '상의') & (~recommendations['색상'].isin(['검정', '네이비']))
                    ]
                    st.info("👕 더운 날엔 밝은 색상의 상의를 추천합니다!")
                elif "맑음" in weather:
                    st.info("🌤️ 맑은 날엔 모든 스타일이 어울려요!")

                if not recommendations.empty:
                    for idx, row in recommendations.iterrows():
                        st.markdown(f"**{row['카테고리']} - {row['스타일']} - {row['색상']} - {row['사이즈']}**")
                        if row['이미지'] and os.path.exists(row['이미지']):
                            st.image(row['이미지'], width=200)
                        st.markdown("---")
                else:
                    st.warning("옷장에 조건에 맞는 아이템이 없어요. 더 추가해 보세요!")
    elif menu == "📅 착장 캘린더":
        st.header("📅 착장 캘린더")
        st.subheader("✅ 오늘의 착장 기록")
        with st.form("calendar_form"):
            selected_date = st.date_input("날짜를 선택하세요", value=datetime.date.today())

            st.markdown("### ✅ 등록 방식 선택")
            input_mode = st.radio("등록 방식", ["옷장에서 선택", "직접 입력"])

            if input_mode == "옷장에서 선택" and not st.session_state.wardrobe.empty:
                selected_item_idx = st.selectbox(
                    "입은 옷 선택",
                    options=st.session_state.wardrobe.index,
                    format_func=lambda x: f"{st.session_state.wardrobe.loc[x,'카테고리']} - {st.session_state.wardrobe.loc[x,'스타일']} - {st.session_state.wardrobe.loc[x,'색상']} - {st.session_state.wardrobe.loc[x,'사이즈']}"
                )
            elif input_mode == "직접 입력":
                manual_category = st.text_input("카테고리 (자유 입력)")
                manual_color = st.text_input("색상 (자유 입력)")
                manual_style = st.text_input("스타일 (자유 입력)")
                manual_size = st.text_input("사이즈 (자유 입력)")

            save_calendar = st.form_submit_button("저장하기")

        if save_calendar:
            if input_mode == "옷장에서 선택" and not st.session_state.wardrobe.empty:
                item = st.session_state.wardrobe.loc[selected_item_idx]
                new_entry = pd.DataFrame({
                    '날짜':[selected_date],
                    '카테고리':[item['카테고리']],
                    '색상':[item['색상']],
                    '스타일':[item['스타일']],
                    '사이즈':[item['사이즈']]
                })
            elif input_mode == "직접 입력":
                new_entry = pd.DataFrame({
                    '날짜':[selected_date],
                    '카테고리':[manual_category],
                    '색상':[manual_color],
                    '스타일':[manual_style],
                    '사이즈':[manual_size]
                })
            else:
                new_entry = None

            if new_entry is not None:
                st.session_state.wear_calendar = pd.concat([st.session_state.wear_calendar, new_entry], ignore_index=True)
                st.success("✅ 오늘의 착장 기록이 저장되었습니다!")

        if not st.session_state.wear_calendar.empty:
            st.subheader("🗂️ 기록된 착장 내역")
            st.dataframe(st.session_state.wear_calendar)

            st.subheader("📅 달력에서 확인하기")
            events = []
            for idx, row in st.session_state.wear_calendar.iterrows():
                events.append({
                    "title": f"{row['카테고리']} - {row['스타일']}",
                    "start": str(row['날짜']),
                    "allDay": True
                })

            calendar(
                events=events,
                options={"initialView":"dayGridMonth"},
                key="calendar"
            )
    elif menu == "💬 의류 커뮤니티":
        st.header("💬 의류 커뮤니티 (토론방)")
        with st.form("community_form"):
            post_title = st.text_input("글 제목")
            post_content_long = st.text_area("내용 (긴 글)")
            post_content_short = st.text_input("내용 (짧은 글)")
            submitted_post = st.form_submit_button("등록하기")
        if submitted_post:
            content = ""
            if post_content_long.strip():
                content = post_content_long.strip()
            elif post_content_short.strip():
                content = post_content_short.strip()

            if post_title.strip() and content:
                new_post = {"제목": post_title.strip(), "내용": content}
                st.session_state.community_posts.append(new_post)
                st.success("✅ 글이 등록되었습니다!")
            else:
                st.warning("⚠️ 제목과 내용을 모두 입력해주세요.")
        if st.session_state.community_posts:
            st.subheader("📌 커뮤니티 글 목록")
            for idx, post in enumerate(reversed(st.session_state.community_posts), 1):
                st.markdown(f"**{idx}. {post['제목']}**")
                st.write(post['내용'])
                st.markdown("---")
        else:
            st.info("아직 작성된 글이 없습니다. 첫 글을 남겨보세요!")











