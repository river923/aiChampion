import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chat.services import answer_question
from characters.models import AICharacter
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()
char = AICharacter.objects.filter(name="김총무").first()

if not char:
    print("❌ '김총무' 캐릭터를 찾을 수 없습니다.")
else:
    print(f"✅ 테스트 준비 완료: 사용자({user.username}), 캐릭터({char.name})")

    question = "복무 규정에서 휴가와 관련된 내용을 알려줘"
    print(f"👉 질문: {question}")

    try:
        result = answer_question(user.id, char.id, question)
        print("------------------------------------------")
        print(f"💬 상태: {result.status}")
        print(f"💬 답변: {result.answer}")
        print(f"💬 인용: {result.citations}")
        if result.error_message:
            print(f"⚠️ 에러 메시지: {result.error_message}")
        print("------------------------------------------")
        print("✅ 성공적으로 챗봇이 동작합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
