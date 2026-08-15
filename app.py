import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

st.title("🧾 レシートから毎晩の献立を提案！")

# SecretsからAPIキーを取得
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not API_KEY:
    st.error("APIキーが設定されていません。StreamlitのSecretsに GEMINI_API_KEY を登録してください。")
    st.stop()

client = genai.Client(api_key=API_KEY)

uploaded_file = st.file_uploader("レシートの写真をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされたレシート", use_container_width=True)

    if st.button("🍽️ 献立を考える"):
        with st.spinner("レシートを解析して献立を考えています..."):
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format if image.format else "JPEG")
            image_bytes = img_byte_arr.getvalue()

            try:
                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type="image/jpeg",
                        ),
                        (
                            "このレシートに写っている食材をすべて読み取り、"
                            "それらを使った毎晩の献立（主菜・副菜）を3つ提案してください。"
                            "足りない一般的な調味料（塩、醤油、油など）は家にあるものと仮定してください。"
                        ),
                    ],
                )
                st.success("献立が完成しました！")
                st.markdown("### 🤖 提案された献立")
                st.write(response.text)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
