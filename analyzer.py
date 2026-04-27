from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

print("🚀 AI Privacy SDK 가동 시작...")

# 1. 다국어 AI 뇌 세팅
configuration = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "ko", "model_name": "ko_core_news_sm"},
        {"lang_code": "en", "model_name": "en_core_web_lg"}
    ]
}
provider = NlpEngineProvider(nlp_configuration=configuration)
analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["ko", "en"])
anonymizer = AnonymizerEngine()

# ---------------------------------------------------------
# [1.5 챕터 핵심]: 범용 AI의 구멍을 막는 한국어 특화 방패 3종 세트
# ---------------------------------------------------------

# ① 전화번호 방패
kr_phone_recognizer = PatternRecognizer(
    supported_entity="KR_PHONE_NUMBER",
    patterns=[Pattern(name="kr_phone", regex=r"010-\d{3,4}-\d{4}", score=1.0)],
    supported_language="ko"
)
analyzer.registry.add_recognizer(kr_phone_recognizer)

# ② 이름 강제 인식 방패 (AI가 놓쳐도 '이름은' 뒤의 글자를 멱살 잡고 끌고 옴)
kr_name_recognizer = PatternRecognizer(
    supported_entity="PERSON",
    patterns=[Pattern(name="kr_name_context", regex=r"(?<=이름은\s)[가-힣]{2,4}", score=0.9)],
    supported_language="ko"
)
analyzer.registry.add_recognizer(kr_name_recognizer)

# ③ 대한민국 1급 기밀 방패 (주민등록번호)
kr_rrn_recognizer = PatternRecognizer(
    supported_entity="KR_RRN",
    patterns=[Pattern(name="kr_rrn", regex=r"\d{6}-[1-4]\d{6}", score=1.0)],
    supported_language="ko"
)
analyzer.registry.add_recognizer(kr_rrn_recognizer)

print("✅ AI 뇌 및 한국어 특화(이름/주민번호/전화번호) 방패 3중 전개 완료")

# 2. 극한의 실전 데이터 투입 (주민번호 추가)
text_to_analyze = "제 이름은 김철수입니다. 주민번호는 900101-1234567 이고, 연락처는 010-9999-8888입니다. 이메일은 chulsoo@naver.com 입니다."
print(f"\n[원본 텍스트] : {text_to_analyze}")

# 3. 분석 및 필터링
results = analyzer.analyze(text=text_to_analyze, language='ko')
filtered_results = [res for res in results if res.entity_type != "URL"]

# 4. 완벽 마스킹
anonymized_result = anonymizer.anonymize(
    text=text_to_analyze,
    analyzer_results=filtered_results
)

print("\n--- 🛡 마스킹 완료된 절대 안전 데이터 ---")
print(anonymized_result.text)
