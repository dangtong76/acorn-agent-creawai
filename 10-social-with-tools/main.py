from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel
from crewai import LLM # 
from crewai.agent import Agent
from dotenv import load_dotenv
from content_eval_crew import ContentEvalCrew
from tools import web_search_tool
import os
from datetime import datetime

load_dotenv()

class BlogPost(BaseModel):
    title: str
    subtitle: str 
    content: str

class TweetPost(BaseModel):
    content: str
    hashtags: str

class LinkedinPost(BaseModel):
    hook: str 
    content: str 
    call_to_action: str

class Score(BaseModel):
    score: int = 0 
    reason: str = ""

class ContentPipelineState(BaseModel):

    # INPUT
    content_type: str = ""
    topic: str = ""

    # INSTERNAL PARAMETER(STATE)
    max_characters: int = 0
    score: Score | None = None
    research: str = ""

    # content
    blog_post: BlogPost | None = None
    tweet_post: TweetPost | None = None
    linkedin_post: LinkedinPost | None = None

class ContentPipelineFlow(Flow[ContentPipelineState]):

    @start()
    def init_content_pipeline(self):
        if self.state.content_type not in ("tweet", "blog", "linkedin"):
            raise ValueError("작성을 지원하지 않는 컨텐츠 입니다.")
        if self.state.topic == "":
            raise ValueError("주제가 없습니다.")
        
        if self.state.content_type == "tweet":
            self.state.max_characters = 150
        elif self.state.content_type == "blog":
            self.state.max_characters = 800
        elif self.state.content_type == "linkedin":
            self.state.max_characters = 500
    
    @listen(init_content_pipeline)
    def conduct_research(self):
        print(f"조사시작: {self.state.topic} 에 대해 조사를 시작합니다.")
        researcher = Agent(
            role="조사 분석 전문가",
            backstory="당신은 컨테츠 작성을 위해서 사전 조사하는 전문가 입니다. 조사 결과를 제공 합니다.",
            goal=f"{self.state.topic} 에 대해 가능한 유용한 정보를 찾아서 조사를 시작합니다.",
            tools=[web_search_tool]
        )

        self.state.research = researcher.kickoff(
            f"{self.state.topic}에 대해 가능한 유용한 정보를 찾아서 조사를 시작하세요"
        )

    @router(conduct_research)
    def conduct_research_router(self):
        content_type = self.state.content_type

        if content_type == "blog":
            return "make_blog_post"
        elif content_type == "tweet":
            return "make_tweet_post"
        elif content_type == "linkedin":
            return "make_linkedin_post"
        else:
            raise ValueError("작성을 지원하지 않는 컨텐츠 타입 입니다. [blog | tweet | linkedin]")
    
    @listen(or_("make_blog_post","rewrite_blog_post"))
    # 블로그 작성(make_blog_post)을  AI에게 요청 하든지,
    # 이미 블로그가 작성된 상태(rewrite_blog_post) 라면 AI에게 보여주고 수정을 요청 한다.
    def handle_make_blog_post(self):
        print(f"블로그 포스트 작성 : {self.state.topic}에 대한 블로그 포스트를 작성 합니다.")

        blog_post = self.state.blog_post 
        llm = LLM(model="openai/gpt-4o-mini",response_format=BlogPost)

        if blog_post is None: # 최초 작성
            result = llm.call(f"""
            다음의 {self.state.research} 결과를 바탕으로 {self.state.topic} 에 대한 블로그 포스트를 한글로 작성하세요.
            작성할 경우, {self.state.research} 에 있는 인터넷 자료의 출처(Reference)를 반드시 명시하라.  
            출처는 실제로 존재하는 페이지 링크(URL)여야 하며, "출처 없음", "예시 링크" 등은 허용되지 않는다.
            
            <format>
                "title": "제목",
                "subtitle": "부제목",
                "content": "내용"
            </format>
            
            <research>
            {self.state.research}
            </research>
            """)
        else: # 다시 작성
            result = llm.call(f"""
            니가 작성한 포스트는 {self.state.score.reason} 때문에 SEO(검색엔진 최적화)점수가 좋지 않아, {self.state.topic} 에 대한 블로그 포스트를 개선해서 한글로 작성해줘.
            
            <format>
                "title": "제목",
                "subtitle": "부제목",
                "content": "내용"
            </format>
            
            <blog_post>
            {self.state.blog_post.model_dump_json()}
            </blog_post>

            다음의 research 결과를 하용해서 작성해.

            <research>
            {self.state.research}
            </research>
            """)
        print("블로그 작성 내용 ========================================")
        print(result)
        print("블로그 작성 내용 ========================================")

        self.state.blog_post = result

    
    @listen(or_("make_tweet_post","rewrite_tweet_post"))
    # Tweet 작성(make_tweet_post)을  AI에게 요청 하든지,
    # 이미 Tweet 작성된 상태(rewrite_tweet_post) 라면 AI에게 보여주고 수정을 요청 한다.
    def handle_make_tweet_post(self):
        print(f"Tweet 포스트 작성 : {self.state.topic}에 대한 Tweet 포스트를 작성 합니다.")
        tweet_post = self.state.tweet_post
        llm = LLM(model="openai/gpt-4o-mini",response_format=TweetPost)

        if tweet_post is None: # 최초 작성
            result = llm.call(f"""
            다음의 research 결과를 바탕으로 {self.state.topic} 에 대한 Tweet 포스트 내용과 해시태그를 한글로 작성하세요
            
            <format>
                "content": "내용",
                "hashtags": "해시태그"
            </format>
            
            <research>
            {self.state.research}
            </research>
            """)
        else: # 다시 작성
            result = llm.call(f"""
            니가 작성한 Tweet 포스트는 {self.state.score.reason} 때문에 화재성 점수가 좋지 않아,
            {self.state.topic} 에 대한 Tweet 포스트와 해시태그를 개선해서 한글로 작성해줘.
            
            <format>
                "content": "내용",
                "hashtags": "해시태그"
            </format>
            
            <tweet_post>
            {self.state.tweet_post.model_dump_json()}
            <tweet_post>

            다음의 research 결과를 하용해서 작성해.

            <research>
            {self.state.research}
            </research>
            """)
        print("Tweet 작성 내용 ========================================")
        print(result)
        print("Tweet로그 작성 내용 ========================================")

        self.state.tweet_post = result
        

    @listen(or_("make_linkedin_post","rewrite_linkedin_post"))
    # Linkedin 작성(make_Linkedin_post)을  AI에게 요청 하든지,
    # 이미 Linkedin가 작성된 상태(rewrite_Linkedin_post) 라면 AI에게 보여주고 수정을 요청 한다.
    def handle_make_linkedin_post(self):
        print(f"Linkedin 포스트 작성 : {self.state.topic}에 대한 Linkedin 포스트를 작성 합니다.")
        tweet_post = self.state.tweet_post
        llm = LLM(model="openai/gpt-4o-mini",response_format=TweetPost)

        if tweet_post is None: # 최초 작성
            result = llm.call(f"""
            다음의 research 결과를 바탕으로 {self.state.topic} 에 대한 Linkedin 포스트를 한글로 작성하세요. 
            작성할 경우, {self.state.research} 에 있는 인터넷 자료의 출처(Reference)를 반드시 명시하라.  
            출처는 실제로 존재하는 페이지 링크(URL)여야 하며, "출처 없음", "예시 링크" 등은 허용되지 않는다.
            
            <format>
                "hook": "훅",
                "content": "내용",
                "call_to_action": "호출 액션"
            <format>
            
            <research>
            {self.state.research}
            </research>
            """)
        else: # 다시 작성
            result = llm.call(f"""
            니가 작성한 Linkedin 포스트는 {self.state.score.reason} 때문에 화재성 점수가 좋지 않아,
            {self.state.topic} 에 대한 Linkedin 포스트를 개선해서 한글로 작성해줘.
            content 는 마크다운으로 작성하지 말고, 순수 텍스트로 작성하세요

            <format>
                "hook": "훅",
                "content": "내용",
                "call_to_action": "호출 액션"
            </format>

            <linkedin_post>
            {self.state.linkedin_post.model_dump_json()}
            <linkedin_post>

            다음의 research 결과를 이용해서 작성해.

            <research>
            {self.state.research}
            </research>
            """)
        print("Linkedin 작성 내용 ========================================")
        print(result)
        print("Linkedin 작성 내용 ========================================")

        self.state.linkedin_post = result
        

    @listen(handle_make_blog_post)
    def check_seo(self):
        print("check_seo")
        if isinstance(self.state.blog_post, BaseModel):
            blog_post_value = self.state.blog_post.model_dump_json()
        else:
            blog_post_value = str(self.state.blog_post)
        
        result = (
            ContentEvalCrew().seo_crew().kickoff(
                inputs={
                    "blog_post": blog_post_value, 
                    "topic": self.state.topic
                }
            )
        )

        self.state.score = result.pydantic


    @listen(or_(handle_make_tweet_post, handle_make_linkedin_post))
    def check_virality(self):
        print("check_virality")

        tweet_post_value = (
            self.state.tweet_post.model_dump_json()
            if isinstance(self.state.tweet_post, BaseModel )
            else str(self.state.tweet_post)
        )

        linkedin_post_value = (
            self.state.linkedin_post.model_dump_json()
            if isinstance(self.state.linkedin_post, BaseModel )
            else str(self.state.linkedin_post)
        )

        if self.state.content_type == "tweet":
            result = (
                ContentEvalCrew().virality_crew().kickoff(
                    inputs={
                        "content_type": self.state.content_type, 
                        "content": tweet_post_value,
                        "topic": self.state.topic
                    }
                )
            )
        elif self.state.content_type == "linkedin":
            result = (
                ContentEvalCrew().virality_crew().kickoff(
                    inputs={
                        "content_type": self.state.content_type, 
                        "content": linkedin_post_value,
                        "topic": self.state.topic
                    }
                )
            )

        self.state.score = result.pydantic


    @router(or_(check_seo, check_virality))
    def score_router(self):
        content_type = self.state.content_type
        score = self.state.score

        if score.score > 6:
            return "content_passed"
        else:
            if content_type == "blog":
                return "rewrite_blog_post"
            elif content_type == "tweet":
                return "rewrite_tweet_post"
            elif content_type == "linkedin":
                return "rewrite_linkedin_post"
            else:
                raise ValueError("유효하지 않은 컨텐츠 입니다.")

    
    @listen("content_passed")
    def complete_content_pipeline(self):
        print(f"컨텐츠 파이프라인 완료: {self.state.topic} 에 대해 작성을 완료 했습니다.")


flow = ContentPipelineFlow()


# flow.plot()

# flow.kickoff(
#     inputs={
#         "content_type": "tweet",
#         "topic": "AI and Job Security"
#     }
# )

for post_type in ("tweet", "blog", "linkedin"):
    flow = ContentPipelineFlow() ### --> missing 
    flow.kickoff(
        inputs={
            "content_type": post_type,
            "topic": "AI and Job Security",
        }
    )