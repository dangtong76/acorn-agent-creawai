from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel

class ContentPipelineState(BaseModel):

    # INPUT
    content_type: str = ""
    topic: str = ""

    # INSTERNAL PARAMETER(STATE)
    max_characters: int = 0

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
    def router(self):
        content_type = self.state.content_type

        if content_type == "blog":
            return "make_blog_post"
        elif content_type == "tweet":
            return "make_tweet_post"
        elif content_type == "linkedin":
            return "make_linkedin_post"
        else:
            raise ValueError("작성을 지원하지 않는 컨텐츠 타입 입니다. [blog | tweet | linkedin]")
    
    @listen("make_blog_post")
    def handle_make_blog_post(self):
        print("handle_make_blog_post")
        return True
        
    
    @listen("make_tweet_post")
    def handle_make_tweet_post(self):
        print("handle_make_tweet_post")
        return True

    @listen("make_linkedin_post")
    def handle_make_linkedin_post(self):
        print("handle_make_linkedin_post")
        return True

    @listen(handle_make_blog_post)
    def check_seo(self):
        print("check_seo")
        return True

    @listen(or_(handle_make_tweet_post, handle_make_linkedin_post))
    def check_virality(self):
        print("check_virality")
        return True

    @listen(or_(check_seo, check_virality))
    def finalize_content_pipeline(self):
        print(f"컨텐츠 파이프라인 완료: {self.state.topic} 에 대한 컨텐츠 작성을 완료 하였습니다.")
        return True
        
    
flow = ContentPipelineFlow()


flow.plot()

# flow.kickoff(
#     inputs={
#         "content_type": "tweet",
#         "topic": "AI and Job Security"
#     }
# )