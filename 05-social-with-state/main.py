from crewai.flow.flow import Flow, listen, start, router, and_, or_

class FirstFlow(Flow):

    @start()
    def first_step(self):
        print("Hello")

    @listen(first_step)
    def second_step(self):
        self.state["my-msg"] =2
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
        if self.state["my-msg"] == 2:
            return 'even'
        elif self.state["my-msg"] ==1:
            return 'odd'
        else:
            return 'None'
        
    @listen('even')
    def handle_even(self):
        print('even')

    @listen('odd')
    def handle_odd(self):
        print('odd')

flow = FirstFlow()

flow.plot()

# flow.kickoff()

