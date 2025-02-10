from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
import json

# 경로 설정
PERSIST_DIRECTORY = r"Raw_DB\vector_store\contents"
COLLECTION_NAME = "contents"
EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)


# JSON 데이터 불러오기
with open("Raw_DB/total.json", "r", encoding="utf-8") as f:
    total = json.load(f)

# Document 객체로 변환
documents = []
for idx in range(len(total)):
    content = total[idx]
    merged_text = f"id: {content["id"]}, type: {content["type"]}, platform: {content["platform"]}, title: {content["title"]}, status: {content["status"]}, thumbnail: {content["thumbnail"]}, genre: {content['genre']}, views: {content["views"]}, rating: {content["rating"]}, like: {content["like"]}, description: {content["description"]}, keyword: {content["keywords"]}, author: {content['author']}, illustrator: {content['illustrator']}, original: {content['original']}, age_rating: {content['age_rating']}, price_type: {content['price_type']}, price_price: {content['price_price']}"
    if isinstance(content["keywords"], str):
        keywords = content["keywords"]
    else:
        keywords = ", ".join(content["keywords"])
    documents.append(
        Document(
            page_content=merged_text,
            metadata={
                "type": content["type"],
                "platform": content["platform"],
                "title": content["title"],
                "genre": content["genre"],
                "author": content["author"],
                "age_rating": content["age_rating"],
                "price_type": content["price_type"],
            },
        )
    )
vector_store = Chroma.from_documents(
    documents=documents,
    embedding=embedding_model,
    collection_name=COLLECTION_NAME,
    persist_directory=PERSIST_DIRECTORY,
)
