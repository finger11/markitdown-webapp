import streamlit as st
from markitdown import MarkItDown
from openai import OpenAI
import tempfile
import os

st.title("📄 지능형 MarkItDown 변환기 (OCR 지원)")
st.write("문서를 마크다운으로 변환합니다. API 키를 입력하면 복잡한 표나 이미지 속 글자도 완벽하게 구조화(OCR)합니다.")

# 1. 사이드바: OpenAI API 키 입력란 구성
with st.sidebar:
    st.header("⚙️ OCR 설정")
    st.write("복잡한 표나 스캔된 PDF를 변환할 때 필요합니다.")
    # 비밀번호 타입으로 입력받아 화면에 노출되지 않게 함
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    if api_key:
        st.success("API 키가 입력되었습니다! (OCR 모드 활성화)")
    else:
        st.info("키가 없으면 텍스트만 추출하는 일반 모드로 동작합니다.")

# 2. 메인 화면: 파일 업로드
uploaded_file = st.file_uploader(
    "파일을 여기에 끌어다 놓으세요 (Drag & Drop)", 
    type=['pdf', 'docx', 'xlsx', 'pptx', 'jpg', 'png', 'html']
)

if uploaded_file is not None:
    # 보안 및 처리를 위해 임시 파일로 저장
    file_extension = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
        
    try:
        with st.spinner('문서를 분석하고 변환하는 중입니다. (OCR은 시간이 조금 더 걸릴 수 있습니다)...'):
            
            # 3. API 키 유무에 따른 MarkItDown 초기화 설정
            if api_key:
                # OCR(Vision LLM) 모드 활성화
                client = OpenAI(api_key=api_key)
                md = MarkItDown(
                    enable_plugins=True,  # 플러그인 활성화
                    llm_client=client,
                    llm_model="gpt-4o"    # 표와 이미지를 읽는 데 가장 성능이 좋은 gpt-4o 사용
                )
            else:
                # 일반 텍스트 추출 모드 (API 키 미입력 시)
                md = MarkItDown(enable_plugins=False)
            
            # 파일 변환 실행
            result = md.convert(tmp_path)
            
            st.success("✅ 변환이 완료되었습니다!")
            
            # 4. 결과 출력 및 다운로드
            st.text_area("마크다운 미리보기", result.text_content, height=400)
            
            st.download_button(
                label="📥 마크다운 파일(.md) 다운로드",
                data=result.text_content,
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_converted.md",
                mime="text/markdown"
            )
            
    except Exception as e:
        st.error(f"변환 중 오류가 발생했습니다: {str(e)}")
        if "AuthenticationError" in str(e):
            st.error("💡 OpenAI API 키가 올바르지 않거나 만료되었습니다. 다시 확인해 주세요.")
            
    finally:
        # 5. 서버에 남은 임시 파일 삭제 (용량 및 보안 관리)
        os.remove(tmp_path)
