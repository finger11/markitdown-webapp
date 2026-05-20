import streamlit as st
from markitdown import MarkItDown
import tempfile
import os

st.title("📄 MarkItDown 파일 변환기")
st.write("문서(PDF, Word, Excel 등)를 업로드하면 마크다운(Markdown)으로 변환해 줍니다.")

# 파일 업로드 UI 생성
uploaded_file = st.file_uploader("파일을 선택하세요", type=['pdf', 'docx', 'xlsx', 'pptx', 'html', 'csv'])

if uploaded_file is not None:
    # MarkItDown 초기화
    md = MarkItDown(enable_plugins=False)
    
    # 보안 및 처리를 위해 업로드된 파일을 임시 파일로 저장
    file_extension = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
        
    try:
        with st.spinner('문서를 변환하고 있습니다. 잠시만 기다려주세요...'):
            # 임시 파일을 MarkItDown으로 변환
            result = md.convert(tmp_path)
            
            st.success("변환 성공!")
            
            # 1. 화면에 결과 보여주기
            st.text_area("변환된 마크다운 결과", result.text_content, height=400)
            
            # 2. 결과 다운로드 버튼 제공
            st.download_button(
                label="📥 마크다운 파일로 다운로드",
                data=result.text_content,
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}.md",
                mime="text/markdown"
            )
    except Exception as e:
        st.error(f"변환 중 오류가 발생했습니다: {e}")
    finally:
        # 작업 완료 후 서버의 임시 파일 삭제 (보안 및 용량 관리)
        os.remove(tmp_path)
