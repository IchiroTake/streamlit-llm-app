import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from openai import OpenAIError
from langchain.callbacks.base import BaseCallbackHandler

# 環境変数を読み込む
load_dotenv()

st.title("Lesson21 - Chapter 6 【提出課題】LLM機能を搭載したWebアプリ")

# Streamlit用のストリーミングコールバック
class StreamlitTokensHandler(BaseCallbackHandler):
    def __init__(self, placeholder: "st.delta_generator.DeltaGenerator") -> None:
        self.placeholder = placeholder
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        # markdownで太字やコードブロックも反映できる
        self.placeholder.markdown(self.text)

st.write("分野別の専門アシスタント（料理研究家/教育アドバイザー）が、あなたの質問に回答するアプリです。")
st.write("##### ● 使い方")
st.write("###### 1.質問したい分野を選択")
st.write("まずは、質問したい分野を選択してください。（「— 選択してください —」から「料理について」または「教育について」のいずれかを選択）")
st.write("###### 2.質問を入力")
st.write("次に、質問を入力してください。（分野を選択すると、入力欄が表示されます。）")
st.write("###### 3.実行")
st.write("最後に、入力が完了したら「実行」を押してください。")
st.write("##### ● メモ")
st.write("* 分野を切り替えると、それぞれの入力内容は個別に保持されます。")
st.write("* 入力が空のまま実行した場合はエラーを表示します。")
st.write("* 通信状況やAPI制限により応答に時間がかかる場合があります。")
# 区切り線
st.divider()

# デフォルトではリストの左端の要素が変数「selected_item」に格納されます.
# ダミーの未選択オプションを先頭に置き、選択されるまで入力欄を非表示にします.
# 専門家A（料理研究家）/Expert A と 専門家B（教育アドバイザー）/Expert B のプロンプトは後段で条件分岐します.
options = ["— 選択してください —", "料理について", "教育について"]
# ラジオの見出し
st.markdown("#### ▼ 質問したい分野を選択してください。")
selected_item = st.radio(
    label="質問したい分野を選択してください。",
    options=options,
    label_visibility="collapsed"  # ラベルを非表示にする
)

# 専門家A（料理研究家）: あなたは一流の料理研究家兼フードコンサルタントです。日本の家庭調理と外食産業の双方に精通し、科学的根拠に基づいた実践的なアドバイスを行います。 
# 専門家B（教育アドバイザー）: あなたは学習科学に基づく教育アドバイザーです。日本の学習者を想定し、レベルに応じて噛み砕き、理解→実践→定着まで伴走します。
system_message = None
# トピックごとに入力を保持する key マップ
key_map = {
    "料理について": "question_cooking",
    "教育について": "question_education",
}

# トピックごとの placeholder マップ
placeholder_map = {
    "— 選択してください —": "まずは分野を選択してください",
    "料理について": "例: 10分で作れる朝食のレシピを教えて / 鶏むね肉を柔らかく仕上げるコツは？",
    "教育について": "例: 1週間の学習計画を立てて / 英単語を効率よく覚える方法は？",
}

input_key = None
if selected_item != options[0]:
    if selected_item == "料理について":
        system_message = "You are a top-class culinary researcher and food consultant. You are well-versed in both Japanese home cooking and the restaurant industry, and you provide practical advice based on scientific evidence."
    else:
        system_message = "You are an education advisor grounded in learning science. You assume Japanese learners as your audience, and you provide step-by-step support tailored to their level—breaking concepts down and guiding them from understanding, to practice, to mastery."

    input_key = key_map[selected_item]
    # テキスト入力の見出し
    st.markdown("#### ▼ 質問してみましょう")
    st.text_input(
        label="質問してみましょう",
        key=input_key,
        label_visibility="collapsed",
    placeholder=placeholder_map.get(selected_item, "質問を入力してください")
)

# 現在トピックの入力値
current_text = st.session_state.get(input_key, "") if input_key else ""
input_filled = bool(current_text.strip())


if st.button("実行"):
    # 区切り線
    st.divider()

    # 互換性重視UIに合わせた安全な処理
    if selected_item == options[0]:
        st.error("分野を選択してください。")
    elif not input_filled:
        st.error("なにか質問を入力してください。")
    else:
        st.write("#### 【回答結果】")
        st.write(f"**選択:** 「{selected_item}」")
        st.write(f"**入力:** 「{current_text}」")
        # LLM呼び出し（ボタン押下かつバリデーション通過時のみ）
        with st.spinner("回答を生成中..."):
            try:
                # ストリーミング出力用プレースホルダ
                st.write("**回答:**")
                answer_placeholder = st.empty()

                llm = ChatOpenAI(
                    model_name="gpt-4o-mini",
                    temperature=0.5,
                    streaming=True,
                    callbacks=[StreamlitTokensHandler(answer_placeholder)]
                )
                messages = [
                    SystemMessage(content=system_message),
                    HumanMessage(content=current_text),
                ]
                result = llm(messages)
                # 既にハンドラで描画しているため最終描画は不要だが、
                # 念のため最終テキストで上書き（整形が必要な場合の保険）
                if hasattr(result, "content"):
                    answer_placeholder.markdown(result.content)
            except OpenAIError as e:
                st.error("OpenAI APIでエラーが発生しました。APIキー、レート制限、モデル名などを確認してください。")
                st.caption(str(e))
            except Exception as e:
                st.error("回答生成中に予期しないエラーが発生しました。")
                st.caption(str(e))
