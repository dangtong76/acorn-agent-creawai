from crewai.flow.flow import Flow, listen, start, router, and_, or_

class FirstFlow(Flow):

    @start()
    def first_step(self):
        print("Hello")

    @listen(first_step)
    def second_step(self):
        print("world")

    @listen(first_step)
    def third_step(self):
        print("!")

    @listen(and_(second_step, third_step))
    def final_step(self):
        print("CrewAI")

flow = FirstFlow()

# flow.plot()

flow.kickoff()

