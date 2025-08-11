import streamlit as st
from db import GooglesheetUtils
from loc_image import get_location_image
from datetime import datetime, timedelta

import pysqlite3
sys.modules['sqlite3'] = pysqlite3

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from langchain.retrievers.self_query.chroma import ChromaTranslator
from langchain_chroma import Chroma
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.retrievers import EnsembleRetriever

from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
)

import asyncio
import nest_asyncio

# 이벤트 루프 설정
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
nest_asyncio.apply()

gemini_api_key = st.secrets['GEMINI_API_KEY']
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=gemini_api_key)
# 임베딩도 Gemini로 교체
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=gemini_api_key)

class CustomRetriever():
    metadata_field_info = [
        AttributeInfo(
            name="Team code",
            description="Unique code that the team has. alphabetical uppercase + double digit combination.",
            type="string",
        ),
        AttributeInfo(
            name="Team name",
            description="Unique name that the team has.",
            type="string",
        ),
        AttributeInfo(
            name="Title",
            description="the topic that the team studied/made.",
            type="string",
        ),
        AttributeInfo(
            name="Teammate #1 name",
            description="A team member's name. name is two or three letters of Hangul.",
            type="string"
        ),
        AttributeInfo(
            name="Teammate #1 number",
            description="A team member's student number. The student number is four digits.",
            type="string"
        ),
        AttributeInfo(
            name="Teammate #2 name",
            description="A team member's name. name is two or three letters of Hangul.",
            type="string"
        ),
        AttributeInfo(
            name="Teammate #2 number",
            description="A team member's student number. The student number is four digits.",
            type="string"
        ),
        AttributeInfo(
            name="Teammate #3 name",
            description="A team member's name. name is two or three letters of Hangul.",
            type="string"
        ),
        AttributeInfo(
            name="Teammate #3 number",
            description="A team member's student number. The student number is four digits.",
            type="string"
        ),
        AttributeInfo(
            name="Physics",
            description="Whether Physics is used. Can be True or False",
            type="boolean"
        ),
        AttributeInfo(
            name="Chemistry",
            description="Whether Chemistry is used. Can be True or False",
            type="boolean"
        ),
        AttributeInfo(
            name="Biology",
            description="Whether Biology is used. Can be True or False",
            type="boolean"
        ),
        AttributeInfo(
            name="EarthScience",
            description="Whether Earth Science is used. Can be True or False",
            type="boolean"
        ),
        AttributeInfo(
            name="Youtube link",
            description="A youtube video link from the team. The vido can be played by clicking on the link.",
            type="string"
        )
    ]
    examples = [
        (
            "A23 팀?",
            {
                "query": "A23",
                "filter": 'eq("Team code", "A23")',
            },
        ),
        (
            "김석현 학생은 뭐했어?",
            {
                "query": "김석현",
                "filter": 'or(eq("Teammate #1 name", "김석현"), eq("Teammate #2 name", "김석현"))',
            },
        ),
        (
            "고민재 알아?",
            {
                "query": "고민재",
                "filter": 'or(eq("Teammate #1 name", "고민재"), eq("Teammate #2 name", "고민재"))',
            },
        ),
        (
            "화학과 관련된 팀 있어?",
            {
                "query": "화학",
                "filter": 'eq("Chemistry", True)',
            },
        ),
        (
            "작년에 김환은 뭐했어?",
            {
                "query": "작년, 김환",
                "filter": 'or(eq("Year", "2023"), or(eq("Teammate #1 name", "김환"), eq("Teammate #2 name", "김환"))',
            },
        ),
        (
            "환경에 관한 주제로 연구한 팀을 알려줄래?",
            {
                "query": "환경에 관한 주제로 연구한 팀을 알려줄래?",
                "filter": "NO_FILTER",
            }   
        ),
        (
            "팀 번호가 B로 시작하는 프로젝트의 주제는 어떤 것이 있어?",
            {
                "query": "팀 번호가 B로 시작하는 프로젝트의 주제는 어떤 것이 있어?",
                "filter": "NO_FILTER",
            }
        ),
        (
            "머신러닝을 사용하지 않은 팀이 있을까?",
            {
                "query": "머신러닝을 사용하지 않은 팀이 있을까?",
                "filter": "NO_FILTER",
            }
        )
        
    ]

    def __init__(self, _vectorstore):
        self.vectorstore = _vectorstore
        self.query_prompt = get_query_constructor_prompt(
            'Ocean ICT 대회에 참가한 팀의 작품 설명서.',
            self.metadata_field_info,
            examples=self.examples
        )
        self.output_parser = StructuredQueryOutputParser.from_components()

        self.new_query_constructor = self.query_prompt | llm | self.output_parser

        self.self_query_retriever = SelfQueryRetriever(
            query_constructor=self.new_query_constructor,
            vectorstore=self.vectorstore,
            structured_query_translator=ChromaTranslator(),
            search_kwargs={'k' : 5}
        )
        self.vectorstore_retriver = self.vectorstore.as_retriever(search_kwargs={'k' : 5})
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.self_query_retriever, self.vectorstore_retriver],
            weights=[0.5, 0.5],
            search_type="mmr",
            search_kwargs={'k' : 10}
        )
    
    def get_query_constructor(self): return self.new_query_constructor
    def get_selfquery_retriever(self): return self.self_query_retriever
    def get_vectorstore_retriever(self): return self.vectorstore_retriver
    def get_ensemble_retriever(self): return self.ensemble_retriever