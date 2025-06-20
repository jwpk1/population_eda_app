import streamlit as st
import pyrebase
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

# ---------------------
# Streamlit & Seaborn Settings
# ---------------------
st.set_option('deprecation.showPyplotGlobalUse', False)
sns.set_style("whitegrid")

# ---------------------
# Firebase 설정 (기존 값 그대로 유지)
# ---------------------
firebase_config = {
    "apiKey": "AIzaSyCswFmrOGU3FyLYxwbNPTp7hvQxLfTPIZw",
    "authDomain": "sw-projects-49798.firebaseapp.com",
    "databaseURL": "https://sw-projects-49798-default-rtdb.firebaseio.com",
    "projectId": "sw-projects-49798",
    "storageBucket": "sw-projects-49798.appspot.com",
    "messagingSenderId": "...",
    "appId": "..."
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
storage = firebase.storage()

# ---------------------
# 세션 상태 초기화
# ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.id_token = ""
    st.session_state.user_name = ""
    st.session_state.user_gender = "선택 안함"
    st.session_state.user_phone = ""
    st.session_state.profile_image_url = ""

# ---------------------
# 한글 → 영어 지역명 매핑
# ---------------------
REGION_MAP = {
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "광주": "Gwangju",
    "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong", "경기": "Gyeonggi",
    "강원": "Gangwon", "충북": "Chungbuk", "충남": "Chungnam", "전북": "Jeonbuk",
    "전남": "Jeonnam", "경북": "Gyeongbuk", "경남": "Gyeongnam", "제주": "Jeju"
}

class Login:
    def __init__(self):
        st.title("🔐 로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.id_token = user['idToken']

                user_info = firestore.child("users").child(email.replace(".", "_")).get().
                if user_info:
                    st.session_state.user_name = user_info.get("name", "")
                    st.session_state.user_gender = user_info.get("gender", "선택 안함")
                    st.session_state.user_phone = user_info.get("phone", "")
                    st.session_state.profile_image_url = user_info.get("profile_image_url"

                st.success("로그인 성공!")
                time.sleep(1)
                st.rerun()
            except Exception:
                st.error("로그인 실패")

# ---------------------
# 회원가입 페이지 클래스
# ---------------------
class Register:
    def __init__(self, login_page_url):
        st.title("📝 회원가입")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        name = st.text_input("성명")
        gender = st.selectbox("성별", ["선택 안함", "남성", "여성"])
        phone = st.text_input("휴대전화번호")

        if st.button("회원가입"):
            try:
                auth.create_user_with_email_and_password(email, password)
                firestore.child("users").child(email.replace(".", "_")).set({
                    "email": email,
                    "name": name,
                    "gender": gender,
                    "phone": phone,
                    "role": "user",
                    "profile_image_url": ""
                })
                st.success("회원가입 성공! 로그인 페이지로 이동합니다.")
                time.sleep(1)
                st.switch_page(login_page_url)
            except Exception:
                st.error("회원가입 실패")

# ---------------------
# 비밀번호 찾기 페이지 클래스
# ---------------------
class FindPassword:
    def __init__(self):
        st.title("🔎 비밀번호 찾기")
        email = st.text_input("이메일")
        if st.button("비밀번호 재설정 메일 전송"):
            try:
                auth.send_password_reset_email(email)
                st.success("비밀번호 재설정 이메일을 전송했습니다.")
                time.sleep(1)
                st.rerun()
            except:
                st.error("이메일 전송 실패")

# ---------------------
# 사용자 정보 수정 페이지 클래스
# ---------------------
class UserInfo:
    def __init__(self):
        st.title("👤 사용자 정보")

        email = st.session_state.get("user_email", "")
        new_email = st.text_input("이메일", value=email)
        name = st.text_input("성명", value=st.session_state.get("user_name", ""))
        gender = st.selectbox(
            "성별",
            ["선택 안함", "남성", "여성"],
            index=["선택 안함", "남성", "여성"].index(st.session_state.get("user_gender", 
        )
        phone = st.text_input("휴대전화번호", value=st.session_state.get("user_phone", "")

        uploaded_file = st.file_uploader("프로필 이미지 업로드", type=["jpg", "jpeg", "png
        if uploaded_file:
            file_path = f"profiles/{email.replace('.', '_')}.jpg"
            storage.child(file_path).put(uploaded_file, st.session_state.id_token)
            image_url = storage.child(file_path).get_url(st.session_state.id_token)
            st.session_state.profile_image_url = image_url
            st.image(image_url, width=150)
        elif st.session_state.get("profile_image_url"):
            st.image(st.session_state.profile_image_url, width=150)

        if st.button("수정"):
            st.session_state.user_email = new_email
            st.session_state.user_name = name
            st.session_state.user_gender = gender
            st.session_state.user_phone = phone

            firestore.child("users").child(new_email.replace(".", "_")).update({
                "email": new_email,
                "name": name,
                "gender": gender,
                "phone": phone,
                "profile_image_url": st.session_state.get("profile_image_url", "")
            })

            st.success("사용자 정보가 저장되었습니다.")
            time.sleep(1)
            st.rerun()

# ---------------------
# 로그아웃 페이지 클래스
# ---------------------
class Logout:
    def __init__(self):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.id_token = ""
        st.session_state.user_name = ""
        st.session_state.user_gender = "선택 안함"
        st.session_state.user_phone = ""
        st.session_state.profile_image_url = ""
        st.success("로그아웃 되었습니다.")
        time.sleep(1)
        st.rerun()
# ---------------------
# Home Page (simple description)
# ---------------------
class Home:
    def __init__(self):
        st.title("🏠 Home – Population Trends App")
        st.markdown(
            """
            This application provides **exploratory data analysis** for the South‑Korean _population_trends.csv_ dataset.  
            Go to the **EDA** page in the sidebar, upload the CSV file, and explore statistics and visualisations.
            """
        )
        st.info("Firebase login & storage modules remain unchanged; analysis logic resides in the EDA class.")

# ---------------------
# EDA Page
# ---------------------
class EDA:
    def __init__(self):
        st.title("📊 Exploratory Data Analysis – Population")

        # 1) CSV upload
        uploaded_pop = st.file_uploader("📂 Upload population_trends.csv", type=["csv"])

        if uploaded_pop:
            # 2) Load dataframe
            pop_df = pd.read_csv(uploaded_pop)

            # 3) Pre‑processing ------------------------------------------------
            # (i) Replace '-' with 0 for Sejong rows
            sejong_mask = pop_df["지역"] == "세종"
            pop_df.loc[sejong_mask] = pop_df.loc[sejong_mask].replace("-", 0)

            # (ii) Convert numerical columns to int
            num_cols = ["인구", "출생아수(명)", "사망자수(명)"]
            for col in num_cols:
                pop_df[col] = pd.to_numeric(pop_df[col], errors="coerce").fillna(0).astype(int)

            # 4) Tab layout ----------------------------------------------------
            tabs = st.tabs([
                "기초 통계",     # 0 Basic Stats
                "연도별 추이",   # 1 National Trend
                "지역별 분석",   # 2 Regional Analysis (heatmap)
                "변화량 분석",   # 3 5‑year Change
                "시각화"        # 4 Stacked Area Chart
            ])

            # -----------------------------------------------------------------
            # TAB 0 – 기초 통계
            # -----------------------------------------------------------------
            with tabs[0]:
                st.subheader("📈 Basic Descriptive Statistics")
                buffer = io.StringIO()
                pop_df.info(buf=buffer)
                st.text("DataFrame info()")
                st.text(buffer.getvalue())

                st.write("## Describe")
                st.dataframe(pop_df.describe(include="all"))

            # -----------------------------------------------------------------
            # TAB 1 – 연도별 전체 인구 추이 (전국)
            # -----------------------------------------------------------------
            with tabs[1]:
                st.subheader("📈 National Population Trend – All Years")

                nat_df = pop_df[pop_df["지역"] == "전국"].copy().sort_values("연도")

                fig_nat, ax_nat = plt.subplots(figsize=(8, 5))
                ax_nat.plot(nat_df["연도"], nat_df["인구"], marker="o")
                ax_nat.set_title("National Population by Year")
                ax_nat.set_xlabel("Year")
                ax_nat.set_ylabel("Population")

                # Predict 2035 population
                recent = nat_df.tail(3)
                mean_delta = (recent["출생아수(명)"] - recent["사망자수(명)"]).mean()
                pred_2035 = nat_df.iloc[-1]["인구"] + mean_delta * (2035 - nat_df.iloc[-1]["연도"])

                ax_nat.scatter(2035, pred_2035, color="red")
                ax_nat.annotate(f"2035 Est.: {pred_2035:,.0f}", (2035, pred_2035),
                                textcoords="offset points", xytext=(0, 10), ha='center')

                st.pyplot(fig_nat)
                st.metric(label="2035 Est. Population", value=f"{pred_2035:,.0f}")

            # -----------------------------------------------------------------
            # TAB 2 – 지역별 분석 (Heatmap)
            # -----------------------------------------------------------------
            with tabs[2]:
                st.subheader("🏙️ Regional Analysis – Heatmap")

                # Pivot table (region × year) excluding national total
                regional = pop_df[pop_df["지역"] != "전국"].copy()
                pivot_ht = regional.pivot(index="지역", columns="연도", values="인구")
                pivot_ht = pivot_ht.sort_index()

                # Translate index to English
                pivot_ht.index = pivot_ht.index.map(lambda x: REGION_MAP.get(x, x))

                # Convert to thousand persons for readability
                pivot_ht_k = pivot_ht / 1000.0

                fig_ht, ax_ht = plt.subplots(figsize=(10, 8))
                sns.heatmap(pivot_ht_k, cmap="YlGnBu", ax=ax_ht, linewidths=0.3, linecolor="gray")
                ax_ht.set_title("Population (thousand) by Region & Year")
                ax_ht.set_xlabel("Year")
                ax_ht.set_ylabel("Region")

                st.pyplot(fig_ht)
                st.write("The heatmap highlights absolute population levels across regions and years, enabling quick identification of growth hotspots and declining areas.")

            # -----------------------------------------------------------------
            # TAB 3 – 변화량 분석 (최근 5년)
            # -----------------------------------------------------------------
            with tabs[3]:
                st.subheader("🔄 Regional Population Change – Last 5 Years")

                latest_year = pop_df["연도"].max()
                window_years = list(range(latest_year - 4, latest_year + 1))

                win_df = pop_df[(pop_df["연도"].isin(window_years)) & (pop_df["지역"] != "전국")]
                pivot_win = win_df.pivot(index="지역", columns="연도", values="인구").dropna()

                abs_change = pivot_win[latest_year] - pivot_win[latest_year - 4]
                pct_change = abs_change / pivot_win[latest_year - 4] * 100

                change_df = pd.DataFrame({
                    "region_ko": abs_change.index,
                    "abs": abs_change.values,
                    "pct": pct_change.values
                })
                change_df["region"] = change_df["region_ko"].map(lambda x: REGION_MAP.get(x, x))
                change_df["abs_k"] = change_df["abs"] / 1000.0  # thousand

                # Absolute change bar plot
                ch_sorted = change_df.sort_values("abs", ascending=False)
                fig_abs, ax_abs = plt.subplots(figsize=(10, 7))
                sns.barplot(data=ch_sorted, x="abs_k", y="region", ax=ax_abs, palette="Blues_r", orient="h")
                ax_abs.set_title("Absolute Change (thousand)")
                ax_abs.set_xlabel("Change (thousand persons)")
                ax_abs.set_ylabel("Region")

                for i, p in enumerate(ax_abs.patches):
                    val = ch_sorted.iloc[i]["abs_k"]
                    ax_abs.text(p.get_width() + 1, p.get_y() + p.get_height()/2, f"{val:,.1f}", va="center")

                st.pyplot(fig_abs)

                # Percentage change bar plot
                pct_sorted = change_df.sort_values("pct", ascending=False)
                fig_pct, ax_pct = plt.subplots(figsize=(10, 7))
                sns.barplot(data=pct_sorted, x="pct", y="region", ax=ax_pct, palette="Greens_r", orient="h")
                ax_pct.set_title("Percentage Change (%)")
                ax_pct.set_xlabel("Change (%)")
                ax_pct.set_ylabel("Region")

                for i, p in enumerate(ax_pct.patches):
                    pc_val = pct_sorted.iloc[i]["pct"]
                    ax_pct.text(p.get_width() + 0.1, p.get_y() + p.get_height()/2, f"{pc_val:,.1f}%", va="center")

                st.pyplot(fig_pct)
                st.write("These charts reveal regions with the highest absolute and relative population shifts over the past five years.")

            # -----------------------------------------------------------------
            # TAB 4 – 시각화 (Stacked Area Chart)
            # -----------------------------------------------------------------
            with tabs[4]:
                st.subheader("📊 Stacked Area Chart – Regional Composition")

                vis_df = pop_df[pop_df["지역"] != "전국"].copy()
                pivot_area = vis_df.pivot(index="연도", columns="지역", values="인구").sort_index()
                pivot_area = pivot_area.fillna(0)

                # Translate columns to English and divide by thousand
                pivot_area.columns = [REGION_MAP.get(c, c) for c in pivot_area.columns]
                pivot_area_k = pivot_area / 1000.0

                fig_area, ax_area = plt.subplots(figsize=(10, 6))
                ax_area.stackplot(pivot_area_k.index, pivot_area_k.T, labels=pivot_area_k.columns,
                                  colors=sns.color_palette("tab20", n_colors=len(pivot_area_k.columns)))
                ax_area.set_title("Regional Population Composition (thousand)")
                ax_area.set_xlabel("Year")
                ax_area.set_ylabel("Population (thousand)")
                ax_area.legend(loc="upper left", bbox_to_anchor=(1, 1))

                st.pyplot(fig_area)
                st.write("The stacked area chart visualises how each region contributes to the overall population over time, emphasising proportional shifts as well as absolute growth.")

# ---------------------
# Main
# ---------------------
PAGES = {
    "Home": Home,
    "EDA": EDA
}

def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page = PAGES[selection]
    page()

if __name__ == "__main__":
    main()


# ---------------------
# 페이지 객체 생성
# ---------------------
Page_Login    = st.Page(Login,    title="Login",    icon="🔐", url_path="login")
Page_Register = st.Page(lambda: Register(Page_Login.url_path), title="Register", icon="📝", url_path="register")
Page_FindPW   = st.Page(FindPassword, title="Find PW", icon="🔎", url_path="find-password")
Page_Home     = st.Page(lambda: Home(Page_Login, Page_Register, Page_FindPW), title="Home", icon="🏠", url_path="home", default=True)
Page_User     = st.Page(UserInfo, title="My Info", icon="👤", url_path="user-info")
Page_Logout   = st.Page(Logout,   title="Logout",  icon="🔓", url_path="logout")
Page_EDA      = st.Page(EDA,      title="EDA",     icon="📊", url_path="eda")

# ---------------------
# 네비게이션 실행
# ---------------------
if st.session_state.logged_in:
    pages = [Page_Home, Page_User, Page_Logout, Page_EDA]
else:
    pages = [Page_Home, Page_Login, Page_Register, Page_FindPW]

selected_page = st.navigation(pages)
selected_page.run()