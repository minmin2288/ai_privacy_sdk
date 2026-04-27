import time
from faker import Faker
import random
from concurrent.futures import ProcessPoolExecutor
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

print("🚀 [Chapter 2.1 - 수정본] 다중 코어 가동 중...\n")

# 전역 변수: 각 코어가 공유할 뇌
global_analyzer = None
global_anonymizer = None

# --- 1. 작업자 세팅 (코어가 깨어날 때 딱 '한 번만' 실행됨) ---
def init_worker():
    global global_analyzer, global_anonymizer
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "ko", "model_name": "ko_core_news_sm"}]
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    global_analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["ko"])
    global_anonymizer = AnonymizerEngine()

    global_analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="KR_PHONE_NUMBER", patterns=[Pattern(name="kr_phone", regex=r"010-\d{3,4}-\d{4}", score=1.0)], supported_language="ko"))
    global_analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="KR_RRN", patterns=[Pattern(name="kr_rrn", regex=r"\d{6}-[1-4]\d{6}", score=1.0)], supported_language="ko"))
    global_analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="PERSON", patterns=[Pattern(name="kr_name_context", regex=r"(?<=이름은\s)[가-힣]{2,4}", score=0.9)], supported_language="ko"))

# --- 2. 실제 작업 (오지랖 끄고 핵심 3가지만 초고속으로 검사) ---
def process_data(text):
    # 엔진에게 목표물 3개만 찾으라고 조준점을 좁혀줌
    results = global_analyzer.analyze(text=text, language='ko', entities=["PERSON", "KR_PHONE_NUMBER", "KR_RRN"])
    filtered = [res for res in results if res.entity_type != "URL"]
    return global_anonymizer.anonymize(text=text, analyzer_results=filtered).text

if __name__ == '__main__':
    fake = Faker('ko_KR')
    TEST_COUNT = 1000  # 속도 체감을 위해 1000건으로 늘림
    test_data_list = []
    
    print("⏳ 데이터 공장 가동 중 (1000명 분량)...")
    for _ in range(TEST_COUNT):
        name = fake.name()
        phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        rrn = f"{random.randint(60, 99)}{random.randint(1, 12):02d}{random.randint(1, 28):02d}-{random.randint(1, 4)}{random.randint(100000, 999999)}"
        test_data_list.append(f"제 이름은 {name}입니다. 주민번호는 {rrn} 이고, 연락처는 {phone}입니다.")
    
    print(f"🔥 맥북 모든 코어 동원! {TEST_COUNT}건 병렬 방어 테스트 시작...")
    start_time = time.time()

    success_count = 0
    # init_worker를 통해 각 코어에 뇌를 미리 이식하고, chunksize=100으로 100건씩 묶음 배송
    with ProcessPoolExecutor(initializer=init_worker) as executor:
        results = executor.map(process_data, test_data_list, chunksize=100)
        for _ in results:
            success_count += 1

    end_time = time.time()
    total_time = end_time - start_time
    tps = TEST_COUNT / total_time

    print("\n📊 --- [최종 최적화: 묶음 배송 벤치마크 결과] ---")
    print(f"총 처리 건수: {success_count}건")
    print(f"총 소요 시간: {total_time:.2f}초")
    print(f"🚀 초당 처리 속도 (TPS): {tps:.2f} 건/초")
    print("---------------------------------------------")