from openai import OpenAI
import json
import re
from dotenv import load_dotenv
import os

load_dotenv()


def restaurant_category_to_restaurant_type(category_list):
    result_dict = dict()
    try:
        # GPT API 키 설정 (여기에 진짜 키 넣어야 돼!)
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"))

        # GPT에게 줄 프롬프트
        prompt = f"""
        다음은 음식점의 자유 텍스트 카테고리 또는 대표 음식 이름 목록이야.
    
        이 목록의 각 항목을 아래 기준에 따라 대분류, 중분류, 세분류로 나눠줘:
    
        - 대분류는 반드시 다음 5개 중 하나로만 분류해줘:
          ["한식", "중식", "일식", "양식", "아시아음식"]
    
        - 중분류는 음식 스타일이나 지역 기반 분류로 해줘. 예: 면류, 분식, 이탈리안, 베트남음식 등
        - 세분류는 가능한 한 해당 음식이나 카테고리명을 그대로 써줘. 예: 떡볶이, 라멘, 파스타 등
    
        아래와 같은 JSON 형식으로 응답해줘:
    
        {{
          "피자": {{
            "대분류": "양식",
            "중분류": "이탈리안",
            "세분류": "피자"
          }},
          ...
        }}
    
        이제 이 항목들을 분류해줘:
        {category_list}
        """

        # GPT API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 텍스트를 음식 분류 체계로 잘 정리하는 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        # GPT 응답 텍스트 추출
        result_text = response.choices[0].message.content.strip()

        # JSON 텍스트만 추출
        json_match = re.search(r"\{[\s\S]*\}", result_text)
        if json_match:
            json_str = json_match.group(0)
            result_dict = json.loads(json_str)
        else:
            raise ValueError("GPT 응답에서 JSON을 찾을 수 없습니다.")
    except:
        result_dict = dict()
        for category in category_list:
            result_dict[category] = {"대분류": None, "중분류": None, "세분류": None}
    finally:
        return result_dict

        # results = []
        # # 결과 출력
        # for k, v in result_dict.items():
        #     # print(f"{k} → 대분류: {v['대분류']}, 중분류: {v['중분류']}, 세분류: {v['세분류']}")
        #     results.append({
        #         "l1": v["대분류"],
        #         "l2": v["중분류"],
        #         "l3": v["세분류"],
        #     })
        # print(len(results))
        # return results


if __name__ == "__main__":
    results = restaurant_category_to_restaurant_type(["양식", "요리주점", "와인", "마라탕", "브런치", "스페인음식"])
    print(results)