import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from openai import OpenAIError
# 環境変数を読み込む
load_dotenv()

st.title("Lesson21 - Chapter 6 【提出課題】LLM機能を搭載したWebアプリ")

st.write("##### 動作モード1: 文字数カウント")
st.write("入力フォームにテキストを入力し、「実行」ボタンを押すことで文字数をカウントできます。")
st.write("##### 動作モード2: BMI値の計算")
st.write("身長と体重を入力することで、肥満度を表す体型指数のBMI値を算出できます。")

# デフォルトではリストの左端の要素が変数「selected_item」に格納されます.
# ダミーの未選択オプションを先頭に置き、選択されるまで入力欄を非表示にします.
# 専門家A（料理研究家）/Expert A と 専門家B（教育アドバイザー）/Expert B のプロンプトは後段で条件分岐します.
options = ["— 選択してください —", "料理について", "教育について"]
selected_item = st.radio("質問したい分野を選択してください。", options)

# 区切り線
st.divider()

# 専門家A（料理研究家）: あなたは一流の料理研究家兼フードコンサルタントです。日本の家庭調理と外食産業の双方に精通し、科学的根拠に基づいた実践的なアドバイスを行います。 
# 専門家B（教育アドバイザー）: あなたは学習科学に基づく教育アドバイザーです。日本の学習者を想定し、レベルに応じて噛み砕き、理解→実践→定着まで伴走します。
system_message = None
# トピックごとに入力を保持する key マップ
key_map = {
    "料理について": "question_cooking",
    "教育について": "question_education",
}

input_key = None
if selected_item != options[0]:
    if selected_item == "料理について":
        system_message = "You are a top-class culinary researcher and food consultant. You are well-versed in both Japanese home cooking and the restaurant industry, and you provide practical advice based on scientific evidence."
    else:
        system_message = "You are an education advisor grounded in learning science. You assume Japanese learners as your audience, and you provide step-by-step support tailored to their level—breaking concepts down and guiding them from understanding, to practice, to mastery."

    input_key = key_map[selected_item]
    st.text_input(label="質問してみましょう", key=input_key)

# 送信可否の判定（選択済み かつ 入力が空でない）
current_text = st.session_state.get(input_key, "") if input_key else ""
input_filled = bool(current_text.strip())
can_submit = (selected_item != options[0]) and input_filled


if st.button("実行", disabled=not can_submit):
    # 区切り線
    st.divider()

    # 互換性重視UIに合わせた安全な処理
    if selected_item == options[0]:
        st.error("分野を選択してください。")
    elif not input_filled:
        st.error("なにか質問を入力してください。")
    else:
        st.write(f"選択: {selected_item}")
        st.write(f"入力: {current_text}")
        # LLM呼び出し（ボタン押下かつバリデーション通過時のみ）
        with st.spinner("回答を生成中..."):
            try:
                llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
                messages = [
                    SystemMessage(content=system_message),
                    HumanMessage(content=current_text),
                ]
                result = llm(messages)
                st.write(f"回答: {result.content}")
            except OpenAIError as e:
                st.error("OpenAI APIでエラーが発生しました。APIキー、レート制限、モデル名などを確認してください。")
                st.caption(str(e))
            except Exception as e:
                st.error("回答生成中に予期しないエラーが発生しました。")
                st.caption(str(e))
