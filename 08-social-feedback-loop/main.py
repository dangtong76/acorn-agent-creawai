from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel

class ContentPipelineState(BaseModel):

    # INPUT
    content_type: str = ""
    topic: str = ""

    # INSTERNAL PARAMETER(STATE)
    max_characters: int = 0
    score: int = 0

    # content
    blog_post: str = ""
    tweet_post: str = ""
    linkedin_post: str = ""

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
        return True

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
        
    
    @listen(or_("make_tweet_post","rewrite_tweet_post"))
    # Tweet 작성(make_tweet_post)을  AI에게 요청 하든지,
    # 이미 Tweet 작성된 상태(rewrite_tweet_post) 라면 AI에게 보여주고 수정을 요청 한다.
    def handle_make_tweet_post(self):
        print(f"Tweet 포스트 작성 : {self.state.topic}에 대한 Tweet 포스트를 작성 합니다.")
        

    @listen(or_("make_linkedin_post","rewrite_linkedin_post"))
    # Linkedin 작성(make_Linkedin_post)을  AI에게 요청 하든지,
    # 이미 Linkedin가 작성된 상태(rewrite_Linkedin_post) 라면 AI에게 보여주고 수정을 요청 한다.
    def handle_make_linkedin_post(self):
        print(f"Linkedin 포스트 작성 : {self.state.topic}에 대한 Linkedin 포스트를 작성 합니다.")
        

    @listen(handle_make_blog_post)
    def check_seo(self):
        print("check_seo")


    @listen(or_(handle_make_tweet_post, handle_make_linkedin_post))
    def check_virality(self):
        print("check_virality")


    @router(or_(check_seo, check_virality))
    def score_router(self):
        content_type = self.state.content_type
        score = self.state.score

        if score > 8:
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


flow.plot()

# flow.kickoff(
#     inputs={
#         "content_type": "tweet",
#         "topic": "AI and Job Security"
#     }
# )