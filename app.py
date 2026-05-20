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

# 새로운 파일이 업로드되거나 삭제되면, 이전 변환 결과 초기화
if "current_file" not in st.session_state or st.session_state.current_file != (uploaded_file.name if uploaded_file else None):
    st.session_state.pop('converted_text', None)
    st.session_state.current_file = uploaded_file.name if uploaded_file else None

if uploaded_file is not None:
    # 3. '변환하기' 버튼 추가 (이 버튼을 눌러야만 아래 로직 실행)
    if st.button("🔄 마크다운으로 변환하기", type="primary"):
        
        file_extension = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
            
        try:
            with st.spinner('문서를 분석하고 변환하는 중입니다. (OCR은 시간이 조금 더 걸릴 수 있습니다)...'):
                
                # API 키 유무에 따른 모델 설정
                if api_key:
                    client = OpenAI(api_key=api_key)
                    md = MarkItDown(
                        enable_plugins=True, 
                        llm_client=client,
                        llm_model="gpt-4o"
                    )
                else:
                    md = MarkItDown(enable_plugins=False)
                
                # 변환 실행
                result = md.convert(tmp_path)
                
                # 변환된 결과를 화면 새로고침 시에도 유지하기 위해 session_state에 저장
                st.session_state['converted_text'] = result.text_content
                st.success("✅ 변환이 완료되었습니다!")
                
        except Exception as e:
            st.error(f"변환 중 오류가 발생했습니다: {str(e)}")
            if "AuthenticationError" in str(e):
                st.error("💡 OpenAI API 키가 올바르지 않거나 만료되었습니다. 다시 확인해 주세요.")
                
        finally:
            os.remove(tmp_path)
            
    # 4. 변환 완료된 결과가 메모리(session_state)에 있을 때만 결과 및 다운로드 버튼 표시
    if 'converted_text' in st.session_state:
        st.text_area("마크다운 미리보기", st.session_state['converted_text'], height=400)
        
        st.download_button(
            label="📥 마크다운 파일(.md) 다운로드",
            data=st.session_state['converted_text'],
            file_name=f"{os.path.splitext(uploaded_file.name)[0]}_converted.md",
            mime="text/markdown"
        )
