from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel

class MyState(BaseModel):
    user_id: int = 1
    is_admin: bool = False 

class FirstFlow(Flow):

    @start()
    def first_step(self):
        print(self.state.user_id)
        print("Hello")

    @listen(first_step)
    def second_step(self):
        MyState.is_admin = True
        MyState.user_id = 2
        print("world")

    @listen(first_step)
    def third_step(self):
        self.state["my-msg"] =1
        print("!")

    @listen(and_(second_step, third_step))
    def final_step(self):
        print("CrewAI")
        print(f"last message: {self.state["my-msg"]}")


    @router(final_step)
    def route(self):
        if MyState.is_admin :
            return 'admin'
        elif MyState.is_admin == False:
            return 'normal-user'
        else:
            return 'None'
        
    @listen('admin')
    def handle_even(self):
        print('admin')

    @listen('normal-user')
    def handle_odd(self):
        print('normal-user')

flow = FirstFlow()

flow.plot()

# flow.kickoff()

