import time
from faker import Faker
import random
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

print("🚀 [Chapter 2 진입 준비] AI Privacy SDK 성능 벤치마크 가동 중...\n")

# 1. 뇌와 방패 세팅 (우리가 만든 하이브리드 엔진)
print("⏳ 엔진 예열 중 (약 5~10초 소요)...")
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "ko", "model_name": "ko_core_news_sm"}]
}
provider = NlpEngineProvider(nlp_configuration=configuration)
analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["ko"])
anonymizer = AnonymizerEngine()

# ---------------------------------------------------------
# [버그 수정 완료]: 파라미터(이름표) 명확히 지정하여 방패 장착
# ---------------------------------------------------------
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="KR_PHONE_NUMBER", patterns=[Pattern(name="kr_phone", regex=r"010-\d{3,4}-\d{4}", score=1.0)], supported_language="ko"))
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="KR_RRN", patterns=[Pattern(name="kr_rrn", regex=r"\d{6}-[1-4]\d{6}", score=1.0)], supported_language="ko"))
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="PERSON", patterns=[Pattern(name="kr_name_context", regex=r"(?<=이름은\s)[가-힣]{2,4}", score=0.9)], supported_language="ko"))

# 2. 극한의 테스트 데이터 100건 생성 (가짜 공장 가동)
fake = Faker('ko_KR')
TEST_COUNT = 100  

test_data_list = []
for _ in range(TEST_COUNT):
    name = fake.name()
    phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    rrn = f"{random.randint(60, 99)}{random.randint(1, 12):02d}{random.randint(1, 28):02d}-{random.randint(1, 4)}{random.randint(100000, 999999)}"
    test_data_list.append(f"제 이름은 {name}입니다. 주민번호는 {rrn} 이고, 연락처는 {phone}입니다.")

print(f"✅ 엔진 예열 완료 및 테스트 데이터 {TEST_COUNT}건 준비 완료.\n")

# 3. 속도 측정 시작 (타이머 ON)
print(f"🔥 {TEST_COUNT}건 연속 방어 테스트 시작...")
start_time = time.time()

# 4. 무한 방어
success_count = 0
for text in test_data_list:
    results = analyzer.analyze(text=text, language='ko')
    filtered = [res for res in results if res.entity_type != "URL"]
    anonymized = anonymizer.anonymize(text=text, analyzer_results=filtered)
    success_count += 1

# 5. 결과 집계 (타이머 OFF)
end_time = time.time()
total_time = end_time - start_time
tps = TEST_COUNT / total_time  # TPS: 1초당 처리 건수

print("\n📊 --- [벤치마크 결과 리포트] ---")
print(f"총 처리 건수: {success_count}건")
print(f"총 소요 시간: {total_time:.2f}초")
print(f"🔥 초당 처리 속도 (TPS): {tps:.2f} 건/초")
print("---------------------------------")