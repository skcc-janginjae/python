from google import genai

client = genai.Client(api_key="AIzaSyD8lEP-RALzM2-02gKsOJz8qDNgydZHqo0")

def main():
    print("Gemini AI 챗봇입니다. (종료: q, 히스토리: h)")
    history = []
    
    while True:
        user_input = input("\n질문을 입력하세요: ").strip()
        
        if user_input.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        elif user_input.lower() == 'h':
            print("\n--- 대화 히스토리 ---")
            for idx, entry in enumerate(history, 1):
                print(f"{idx}. Q: {entry['question'][:50]}...")
                print(f"   A: {entry['answer'][:50]}...")
            print("--------------------\n")
            continue
        
        if not user_input:
            print("내용을 입력해 주세요.")
            continue
        
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=user_input,
            )
            answer = response.text
            print(f"\n답변: {answer}")
            
            history.append({
                "question": user_input,
                "answer": answer
            })
        except Exception as e:
            print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()