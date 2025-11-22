from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel

class ContentPipelineState(BaseModel):

    # inputs
    content_type: str =""
    topic: str = ""

    # internal state
    max_characters: int = 0


class ContentPipelineFlow(Flow[ContentPipelineState]):

    @start()
    def init_content_pipeline(self):
        if self.state.content_type not in ("tweet", "blog", "linkedin"):
            raise ValueError("유효하지 않은 컨텐츠 입니다.")
        
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
            raise ValueError("유효하지 않은 컨텐츠 입니다.")

    @listen("make_blog_post")
    def handle_make_blog_post(self):
        print(f"블로그 포스트 작성: {self.state.topic} 에 대해 블로그 포스트를 작성합니다.")
        return True
    
    @listen("make_tweet_post")
    def handle_make_tweet_post(self):
        print(f"트윗 포스트 작성: {self.state.topic} 에 대해 트윗 포스트를 작성합니다.")
        return True
    
    @listen("make_linkedin_post")
    def handle_make_linkedin_post(self):
        print(f"링크드인 포스트 작성: {self.state.topic} 에 대해 링크드인 포스트를 작성합니다.")
        return True

    @listen(handle_make_blog_post)
    def check_seo(self):
        print(f"블로그 포스트 SEO 체크: {self.state.topic} 에 대해 SEO 체크를 시작합니다.")
        return True
    
    @listen(or_(handle_make_tweet_post, handle_make_linkedin_post))
    def check_virality(self):
        print(f"트윗 또는 링크드인 포스트 화제성 체크: {self.state.topic} 에 대해 화제성 체크를 시작합니다.")
        return True


    @listen(or_(check_seo, check_virality))
    def finalize_content_pipeline(self):
        print(f"컨텐츠 파이프라인 완료: {self.state.topic} 에 대해 컨텐츠 파이프라인을 완료합니다.")
        return True
    

flow = ContentPipelineFlow()

flow.plot()