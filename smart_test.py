import re
from presidio_analyzer import AnalyzerEngine, EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

print("🧠 [Chapter 2.2 최종 복구본] 독자적 한국어 눈치 엔진 (돋보기 장착 완료) 가동 중...\n")

# --- 1. 우리가 직접 창조한 통합 한국어 눈치 엔진 ---
class KoreanUnifiedRecognizer(EntityRecognizer):
    def __init__(self):
        super().__init__(supported_entities=["PERSON", "KR_PHONE_NUMBER", "KR_RRN"], supported_language="ko")

    def analyze(self, text, entities, nlp_artifacts=None):
        results = []

        # [전화번호 눈치]
        for match in re.finditer(r"010-\d{3,4}-\d{4}", text):
            start, end = match.span()
            surrounding = text[max(0, start-15):min(len(text), end+15)]
            if any(w in surrounding for w in ["연락처", "번호", "전화", "핸드폰"]):
                results.append(RecognizerResult(entity_type="KR_PHONE_NUMBER", start=start, end=end, score=0.8))

        # [주민번호 눈치]
        for match in re.finditer(r"\d{6}-[1-4]\d{6}", text):
            start, end = match.span()
            surrounding = text[max(0, start-15):min(len(text), end+15)]
            # 뒤에 '원'이 붙어있으면 돈이므로 무시 (오탐지 완벽 방어)
            if text[end:end+2] == " 원" or text[end:end+1] == "원":
                continue
            if any(w in surrounding for w in ["주민번호", "주민등록번호", "신분증"]):
                results.append(RecognizerResult(entity_type="KR_RRN", start=start, end=end, score=0.8))

        # [이름 눈치]
        for match in re.finditer(r"[가-힣]{2,4}", text):
            word = match.group()
            # 멍청하게 가리면 안 되는 단어들 미리 차단
            if word in ["사과", "담당자", "주민번호", "연락처", "입니다", "회사", "가격은"]:
                continue
            start, end = match.span()
            surrounding = text[max(0, start-15):min(len(text), end+15)]
            if any(w in surrounding for w in ["담당자", "성명", "이름"]):
                results.append(RecognizerResult(entity_type="PERSON", start=start, end=end, score=0.8))

        return results

# --- 2. 기본 한글 돋보기 세팅 및 엔진 조립 ---
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "ko", "model_name": "ko_core_news_sm"}]
}
provider = NlpEngineProvider(nlp_configuration=configuration)

# 한글 돋보기(provider)와 우리가 만든 독자적 뇌(KoreanUnifiedRecognizer)를 결합
analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["ko"])
analyzer.registry.add_recognizer(KoreanUnifiedRecognizer())
anonymizer = AnonymizerEngine()

# --- 3. 최악의 함정 데이터 ---
trap_text = "우리 회사 사과 가격은 990101-1234567 원 입니다. 담당자 김민수 의 주민번호는 990101-1234567 이고 연락처는 010-9999-8888 입니다."
print(f"원본 문장: {trap_text}\n")

# --- 4. 검사 및 가리기 ---
results = analyzer.analyze(text=trap_text, language='ko')
anonymized_result = anonymizer.anonymize(text=trap_text, analyzer_results=results)

print("🎯 [독자적 한국어 눈치 훈련 결과]")
print(f"가려진 문장: {anonymized_result.text}")
print("--------------------------------------------------")