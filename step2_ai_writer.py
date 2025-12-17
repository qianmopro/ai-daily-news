import json
import os
from openai import OpenAI

# ================= 配置区 =================
# 优先读取环境变量（适配 GitHub Actions），如果没有则使用本地硬编码的 Key
API_KEY = os.environ.get("API_KEY", "sk-thaptnhclznybryjsvyerfvaibkkyduevnvsysyvxbwtdqyh") 

BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "MiniMaxAI/MiniMax-M2"

INPUT_FILE = "raw_news.json"
OUTPUT_FILE = "final_report.md"
# =========================================

def generate_report():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 找不到 {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    if not news_data:
        print("⚠️ 没有抓取到新闻数据")
        return

    print(f"🤖 AI ({MODEL_NAME}) 正在阅读 {len(news_data)} 条新闻...")

    news_content = ""
    # 为了省钱/省Token，如果新闻太多，只取前 50 条
    for i, item in enumerate(news_data[:50]):
        news_content += f"{i+1}. 【{item['source']}】{item['title']}\n   链接：{item['link']}\n"

    system_prompt = """
    你是一位科技早报主编。请根据提供的资讯，筛选最有价值的 5-8 条 AI 行业新闻，写成一份 Markdown 格式的早报。
    结构要求：
    1. 📅 日期
    2. 🚀 头条重磅 (1条)
    3. 💡 大模型动态 (2-3条)
    4. 🛠️ 开源与工具 (2-3条)
    5. 🌊 简讯 (1-2条)
    注意：每条新闻后必须附带 [🔗原文](URL)。
    """

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"今日资讯(部分)：\n{news_content}"},
            ],
            stream=False
        )
        
        content = response.choices[0].message.content
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✅ 早报生成成功！")
        print("-" * 30)
        print(content)

    except Exception as e:
        print(f"❌ AI 生成失败: {e}")

if __name__ == "__main__":

    generate_report()
