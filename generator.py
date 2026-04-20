from faker import Faker
import random

# 한국어 가짜 데이터 생성기 소환
fake = Faker('ko_KR')

print("🏭 AI Privacy SDK 스트레스 테스트용 데이터 공장 가동...\n")

# 가짜 고객 데이터 5명분 무한 생성 (나중엔 이걸 10만 개로 늘릴 거다)
for i in range(1, 6):
    name = fake.name()
    # 한국식 전화번호 형태 (010-XXXX-XXXX)
    phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    # 가짜 주민번호 형태
    rrn = f"{random.randint(60, 99)}{random.randint(1, 12):02d}{random.randint(1, 28):02d}-{random.randint(1, 4)}{random.randint(100000, 999999)}"
    email = fake.email()
    address = fake.address()
    
    # AI 엔진을 헷갈리게 할 다양한 실전 문장 패턴
    patterns = [
        f"고객명: {name}, 연락처: {phone}. 이메일 주소는 {email} 이고 주민번호는 {rrn} 입니다. 거주지는 {address}입니다.",
        f"이번에 가입한 {name}님의 번호는 {phone}이며, {address}에 삽니다. 담당자 이메일({email}). [주민: {rrn}]",
        f"안녕하세요 {name}입니다. 제 민증번호는 {rrn}이고요, 폰번호 {phone}로 연락주세요."
    ]
    
    print(f"[{i}번 데이터] : {random.choice(patterns)}")