import streamlit as st
import random
import openai
import os
from pathlib import Path


# OpenAI API 설정
os.environ["OPENAI_API_KEY"] = st.secrets["API_KEY"]
openai.api_key = os.environ.get("API_KEY")

# 캐릭터 클래스 정의
class Character:
    def __init__(self, name, personality, info, catchphrases):
        self.name = name  # 캐릭터 이름
        self.personality = personality  # 캐릭터 성격
        self.info = info  # 캐릭터 기본 정보
        self.catchphrases = catchphrases  # 캐릭터가 자주 사용하는 말

# 캐릭터 인스턴스 생성
character_1 = Character(
    name="양세찬",
    personality="요즘 유행하는 유머를 적절하게 구사함. 츤데레스타일, 누구에게나 건방지게 반말사용",
    info="1986년생, ISFP, 2남중 둘째",
    catchphrases=["헤이! 헤이!", "미쳤네 다안단히 미쳤네"]
)

character_2 = Character(
    name="Bob",
    personality="Calm and analytical",
    info="Bob enjoys solving puzzles and reading books.",
    catchphrases=["Let's think this through.", "Knowledge is power."]
)

# 캐릭터 사전 생성
characters = {
    "양세찬": character_1,
    "Bob": character_2
}

# 캐릭터와 대화하는 함수
def chat_with_character(character):
    speech_index = 0

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 사용자가 입력한 메시지를 받는 부분
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_input("You: ", key="input")
        submit_button = st.form_submit_button(label='Send')

    # 버튼 클릭 시 채팅을 업데이트하는 부분
    if submit_button:
        if user_input:
            st.session_state.chat_history.append(f"You: {user_input}")
            
            # 캐릭터의 응답을 생성하는 부분
            response = ""
            if random.randint(0, 10) % 2 == 0:
                response = generate_response(user_input, character)
            else:
                index = random.randint(0, len(character.catchphrases) - 1)
                response = f"{character.name}: {character.catchphrases[index]}"
            st.session_state.chat_history.append(response)

            speech_file_path = Path(str(speech_index) + ".mp3")
            with st.spinner('Converting to the voice...'):
                speech_response = openai.audio.speech.create(
                model="tts-1",
                voice="echo",
                input=response
            )
    
            speech_response.stream_to_file(speech_file_path)

            with open(speech_file_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
            speech_index += 1

    # 채팅 기록을 표시하는 부분
    for chat in st.session_state.chat_history:
        st.write(chat)

# OpenAI API를 사용하여 응답 생성
def generate_response(user_input, character):
    messages = [
        {
            "role": "system",
            "content": f"You are playing the role of {character.name}. Please stay in character and provide a response as {character.name}. Personality: {character.personality}. Info: {character.info}",
        },
        {
            "role": "user",
            "content": user_input,
        }
    ]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    print(response)
    result = response.choices[0].message.content
    return f"{character.name}: {result}"

# 메인 함수
def main():
    st.title("Character Selector")
    
    st.sidebar.title("Select a Character")
    # 사이드바에서 캐릭터를 선택하는 부분
    selected_character_name = st.sidebar.selectbox("Choose your character:", list(characters.keys()))

    if selected_character_name:
        selected_character = characters[selected_character_name]
        st.write("---")
        chat_with_character(selected_character)

if __name__ == "__main__":
    main()