import json
import os
from openai import OpenAI

# 优先读取环境变量 (GitHub Secrets)
API_KEY = os.environ.get("API_KEY") 

BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "MiniMaxAI/MiniMax-M2"

INPUT_FILE = "raw_news.json"
OUTPUT_FILE = "final_report.md"

def generate_report():
    if not API_KEY:
        print("❌ 错误：未检测到 API Key，请在 GitHub Secrets 中配置 SILICONFLOW_API_KEY")
        return

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
    # 限制给AI看的数量，防止 Token 溢出
    for i, item in enumerate(news_data[:50]):
        news_content += f"{i+1}. 【{item['source']}】{item['title']}\n   链接：{item['link']}\n"

    system_prompt = """
    你是一位科技早报主编。请根据提供的资讯，筛选 5-8 条最有价值的 AI 行业新闻，写成 Markdown 早报。
    结构：1.📅日期 2.🚀头条 3.💡大模型 4.🛠️工具 5.🌊简讯。
    每条必须附带 [🔗原文](URL)。
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
        
        print("\n✅ 早报生成成功！内容如下：")
        print("-" * 30)
        print(content) # 👈 这里会直接打印在网页日志里给你看

    except Exception as e:
        print(f"❌ AI 生成失败: {e}")

if __name__ == "__main__":
    generate_report()

